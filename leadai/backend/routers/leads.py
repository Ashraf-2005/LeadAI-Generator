"""
Leads Router - CRUD operations and AI processing
"""

import os
import csv
import logging
from io import StringIO
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, status
from fastapi.responses import JSONResponse
import asyncio

from models.lead import Lead, LeadCreate, LeadUpdate, LeadScore, LeadEmail
from services.scoring import score_lead
from services.email_generator import generate_email
from routers.auth import get_current_user
import database

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/leads", tags=["leads"])

# Configuration
LEAD_SCORE_THRESHOLD = int(os.getenv("LEAD_SCORE_THRESHOLD", "70"))


@router.post("/", response_model=Lead, dependencies=[Depends(get_current_user)])
async def create_lead(lead_create: LeadCreate):
    """Create a new lead and auto-score it."""
    try:
        # Create lead in database
        lead = database.create_lead(lead_create)
        
        # Score the lead asynchronously
        try:
            score = await score_lead(
                company_name=lead.company_name,
                industry=lead.industry,
                website=lead.website or "",
                notes=lead.notes
            )
            
            # Update lead with score
            lead_updated = database.update_lead(
                lead.id,
                {
                    "score": score.dict(),
                    "email_generated": False
                }
            )
            
            # Generate email if score meets threshold
            if score.score_value >= LEAD_SCORE_THRESHOLD:
                try:
                    email = await generate_email(
                        company_name=lead.company_name,
                        industry=lead.industry,
                        notes=lead.notes,
                        suggested_contact_role=score.suggested_contact_role
                    )
                    
                    database.update_lead(
                        lead.id,
                        {
                            "email": email.dict(),
                            "email_generated": True
                        }
                    )
                    lead_updated = database.get_lead(lead.id)
                except Exception as e:
                    logger.error(f"Email generation failed for lead {lead.id}: {e}")
                    # Continue even if email fails
            
            return lead_updated
        
        except Exception as e:
            logger.error(f"Scoring failed for lead {lead.id}: {e}")
            return lead
    
    except Exception as e:
        logger.error(f"Error creating lead: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search/name", response_model=list[Lead], dependencies=[Depends(get_current_user)])
async def search_leads(name: str):
    """Search for leads by company name."""
    try:
        leads = database.search_leads_by_name(name)
        return leads
    except Exception as e:
        logger.error(f"Error searching leads by name {name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=list[Lead], dependencies=[Depends(get_current_user)])
async def list_leads():
    """List all leads."""
    try:
        leads = database.get_all_leads()
        return leads
    except Exception as e:
        logger.error(f"Error listing leads: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{lead_id}", response_model=Lead, dependencies=[Depends(get_current_user)])
async def get_lead(lead_id: str):
    """Get a specific lead by ID."""
    try:
        lead = database.get_lead(lead_id)
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        return lead
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting lead {lead_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{lead_id}", response_model=Lead, dependencies=[Depends(get_current_user)])
async def update_lead(lead_id: str, update: LeadUpdate):
    """Update a lead (e.g., mark as sent, add notes)."""
    try:
        lead = database.update_lead(lead_id, update.dict(exclude_unset=True))
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        return lead
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating lead {lead_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{lead_id}", dependencies=[Depends(get_current_user)])
async def delete_lead(lead_id: str):
    """Delete a lead."""
    try:
        success = database.delete_lead(lead_id)
        if not success:
            raise HTTPException(status_code=404, detail="Lead not found")
        return {"status": "deleted", "lead_id": lead_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting lead {lead_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk/upload", response_model=dict, dependencies=[Depends(get_current_user)])
async def upload_csv(file: UploadFile = File(...)):
    """
    Upload a CSV file with leads.
    Expected columns: company_name, industry, website (optional), notes
    """
    try:
        contents = await file.read()
        text = contents.decode('utf-8')
        csv_reader = csv.DictReader(StringIO(text))
        
        created_leads = []
        errors = []
        
        for row_num, row in enumerate(csv_reader, start=2):
            try:
                # Validate required fields
                company_name = row.get("company_name", "").strip()
                industry = row.get("industry", "").strip()
                notes = row.get("notes", "").strip()
                website = row.get("website", "").strip()
                
                if not company_name or not industry or not notes:
                    errors.append(f"Row {row_num}: Missing required fields (company_name, industry, notes)")
                    continue
                
                lead_create = LeadCreate(
                    company_name=company_name,
                    industry=industry,
                    website=website or None,
                    notes=notes
                )
                
                # Create and score lead
                lead = database.create_lead(lead_create)
                
                # Score asynchronously (fire and forget)
                try:
                    score = await score_lead(
                        company_name=lead.company_name,
                        industry=lead.industry,
                        website=lead.website or "",
                        notes=lead.notes
                    )
                    
                    database.update_lead(
                        lead.id,
                        {
                            "score": score.dict(),
                            "email_generated": False
                        }
                    )
                    
                    # Generate email if score meets threshold
                    if score.score_value >= LEAD_SCORE_THRESHOLD:
                        try:
                            email = await generate_email(
                                company_name=lead.company_name,
                                industry=lead.industry,
                                notes=lead.notes,
                                suggested_contact_role=score.suggested_contact_role
                            )
                            
                            database.update_lead(
                                lead.id,
                                {
                                    "email": email.dict(),
                                    "email_generated": True
                                }
                            )
                        except Exception as e:
                            logger.error(f"Email generation failed for lead {lead.id}: {e}")
                
                except Exception as e:
                    logger.error(f"Scoring failed for lead {lead.id}: {e}")
                
                created_leads.append(lead.id)
            
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
        
        return {
            "imported": len(created_leads),
            "failed": len(errors),
            "lead_ids": created_leads,
            "errors": errors
        }
    
    except Exception as e:
        logger.error(f"Error uploading CSV: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {str(e)}")


@router.post("/{lead_id}/score", response_model=LeadScore, dependencies=[Depends(get_current_user)])
async def rescore_lead(lead_id: str):
    """Re-score an existing lead (useful after manual edits)."""
    try:
        lead = database.get_lead(lead_id)
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        score = await score_lead(
            company_name=lead.company_name,
            industry=lead.industry,
            website=lead.website or "",
            notes=lead.notes
        )
        
        database.update_lead(lead_id, {"score": score.dict()})
        
        return score
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rescoring lead {lead_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{lead_id}/email", response_model=LeadEmail, dependencies=[Depends(get_current_user)])
async def regenerate_email(lead_id: str):
    """Regenerate email for a lead."""
    try:
        lead = database.get_lead(lead_id)
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        if not lead.score:
            raise HTTPException(status_code=400, detail="Lead has not been scored yet")
        
        email = await generate_email(
            company_name=lead.company_name,
            industry=lead.industry,
            notes=lead.notes,
            suggested_contact_role=lead.score.suggested_contact_role
        )
        
        database.update_lead(lead_id, {"email": email.dict(), "email_generated": True})
        
        return email
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating email for lead {lead_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

