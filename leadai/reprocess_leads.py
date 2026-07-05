import sys
import os
import asyncio
import logging

# Setup paths
sys.path.append('/app')
import database
from services.email_generator import generate_email

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("reprocess")

async def run():
    database.init_db()
    leads = database.get_all_leads()
    to_process = [l for l in leads if l.score and l.score.score_value >= 50 and not l.email_generated]
    
    print(f"Found {len(to_process)} leads to reprocess.")
    
    count = 0
    for l in to_process:
        try:
            print(f"Generating email for {l.company_name} (Score: {l.score.score_value})...")
            email = await generate_email(
                company_name=l.company_name,
                industry=l.industry,
                notes=l.notes,
                suggested_contact_role=l.score.suggested_contact_role
            )
            
            database.update_lead(
                l.id,
                {
                    "email": email.dict(),
                    "email_generated": True
                }
            )
            count += 1
            print(f"✓ Success for {l.company_name}")
        except Exception as e:
            print(f"✗ Failed for {l.company_name}: {e}")
            
    print(f"Reprocessing complete. Total updated: {count}")

if __name__ == "__main__":
    asyncio.run(run())
