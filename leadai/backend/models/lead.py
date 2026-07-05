from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class LeadScore(BaseModel):
    score_label: str  # "Hot", "Warm", "Cold"
    score_value: int  # 0-100
    reason: str
    suggested_contact_role: str


class LeadEmail(BaseModel):
    subject: str
    body: str


class Lead(BaseModel):
    id: Optional[str] = None
    company_name: str
    industry: str
    website: Optional[str] = None
    notes: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    score: Optional[LeadScore] = None
    email: Optional[LeadEmail] = None
    email_generated: bool = False
    email_sent: bool = False
    notes_from_user: Optional[str] = None  # User's notes after review

    class Config:
        json_schema_extra = {
            "example": {
                "company_name": "Acme Corp",
                "industry": "SaaS",
                "website": "https://acme.com",
                "notes": "Looking for lead scoring solution, mentioned budget concerns",
                "score": {
                    "score_label": "Warm",
                    "score_value": 75,
                    "reason": "Active interest in lead scoring, industry fit, but budget hesitant",
                    "suggested_contact_role": "VP of Sales"
                }
            }
        }


class LeadCreate(BaseModel):
    company_name: str
    industry: str
    website: Optional[str] = None
    notes: str


class LeadUpdate(BaseModel):
    notes_from_user: Optional[str] = None
    email_sent: Optional[bool] = None
