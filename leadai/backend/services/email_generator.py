"""
Email Generation Service - Drafts personalized cold outreach emails
"""

import logging
from models.lead import LeadEmail
from services.llm_client import get_llm_client

logger = logging.getLogger(__name__)

# ============================================================================
# EMAIL GENERATION PROMPT TEMPLATE
# This is the core prompt for email drafting.
# Must return strict JSON only, no preamble.
# ============================================================================
EMAIL_SYSTEM_PROMPT = """You are a skilled B2B sales copywriter specializing in personalized cold outreach.

Your task is to write a short, professional cold outreach email that will be reviewed and edited by a sales representative before sending.
This is a DRAFT for human review — make it compelling but honest.

CRITICAL GUIDELINES:
- Reference specific details from the company's industry and notes naturally (not generic)
- Keep the email under 120 words
- Use a friendly but professional tone
- Do not invent product names, pricing, or claims not provided to you
- Use placeholders like [Your Product] or [Your Company] where you need flexibility
- Include a clear call-to-action
- Always mark this as a draft for review (e.g., "Feel free to personalize this further")
- Never imply the email has been sent or is final
- Make it feel personal, not templated

Return ONLY valid JSON in this exact format:
{
  "subject": "<email subject line, under 50 chars>",
  "body": "<email body, under 120 words>"
}
"""

EMAIL_USER_PROMPT_TEMPLATE = """Company: {company_name}
Industry: {industry}
Notes: {notes}
Suggested contact role: {suggested_contact_role}

Draft a personalized cold outreach email for this lead. Reference their industry and context naturally."""


async def generate_email(
    company_name: str, 
    industry: str, 
    notes: str, 
    suggested_contact_role: str,
    retry_count: int = 0
) -> LeadEmail:
    """
    Generate a personalized cold email for a lead.
    
    Args:
        company_name: Company name
        industry: Industry vertical
        notes: Sales notes about the lead
        suggested_contact_role: Target contact role (e.g., CTO, Founder)
        retry_count: Internal retry counter
    
    Returns:
        LeadEmail object with subject and body
    
    Raises:
        ValueError: If email generation fails after retries
    """
    try:
        llm = get_llm_client()
        
        # Build the user message
        user_message = EMAIL_USER_PROMPT_TEMPLATE.format(
            company_name=company_name,
            industry=industry,
            notes=notes,
            suggested_contact_role=suggested_contact_role
        )
        
        # Call LLM
        response = llm.call(
            system_prompt=EMAIL_SYSTEM_PROMPT,
            user_message=user_message,
            temperature=0.5  # Slightly higher for more creative emails
        )
        
        # Parse JSON response
        expected_keys = ["subject", "body"]
        parsed = llm.parse_json_response(response, expected_keys)
        
        if parsed is None:
            if retry_count < 1:
                logger.warning("First JSON parse attempt failed, retrying...")
                return await generate_email(company_name, industry, notes, suggested_contact_role, retry_count + 1)
            else:
                # Fallback safe default
                logger.error("Email generation failed after retries, using safe default")
                return LeadEmail(
                    subject="Let's explore how we can help [Company]",
                    body="Hi [Name],\n\nWe work with companies in the {industry} space to [your value prop]. I'd love to see if there's a fit.\n\n[Your Company]\n\n---\nThis is a draft. Please personalize before sending."
                )
        
        subject = parsed.get("subject", "Let's connect")[:50]  # Cap at 50 chars
        body = parsed.get("body", "").strip()
        
        # Ensure draft marker is present
        if "draft" not in body.lower():
            body += "\n\n---\nThis is a draft. Please review and personalize before sending."
        
        return LeadEmail(
            subject=subject,
            body=body
        )
    
    except Exception as e:
        logger.error(f"Error in generate_email: {e}")
        raise ValueError(f"Failed to generate email: {str(e)}")
