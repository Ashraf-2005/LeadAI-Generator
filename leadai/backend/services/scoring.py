"""
Lead Scoring Service - Evaluates lead quality using LLM
"""

import logging
from models.lead import LeadScore
from services.llm_client import get_llm_client

logger = logging.getLogger(__name__)

# ============================================================================
# SCORING PROMPT TEMPLATE
# This is the core prompt for lead evaluation.
# Must return strict JSON only, no preamble.
# ============================================================================
SCORING_SYSTEM_PROMPT = """You are a senior B2B sales analyst with 10+ years of experience qualifying enterprise leads.

Your task is to score a lead's potential ONLY using the information provided in the fields below.
CRITICAL: Do not assume, invent, or infer any facts not explicitly stated:
- Do not fabricate budget information
- Do not assume company size or stage
- Do not invent buying signals, timelines, or intent that are not mentioned
- Do not reference external knowledge about the company
- Ground your analysis ONLY in the provided fields

You will assign:
1. score_label: "Hot" (80+), "Warm" (50-79), or "Cold" (<50)
2. score_value: 0-100 integer
3. reason: 1-2 sentences justifying the score, referencing specific fields
4. suggested_contact_role: The person most likely to be the decision-maker (e.g., CTO, Founder, CFO)

Return ONLY valid JSON in this exact format, with no additional text:
{
  "score_label": "Hot" | "Warm" | "Cold",
  "score_value": <integer 0-100>,
  "reason": "<1-2 sentence justification>",
  "suggested_contact_role": "<role name>"
}
"""

SCORING_USER_PROMPT_TEMPLATE = """Company: {company_name}
Industry: {industry}
Website: {website}
Notes: {notes}

Score this lead based ONLY on the information above."""


async def score_lead(company_name: str, industry: str, website: str, notes: str, retry_count: int = 0) -> LeadScore:
    """
    Score a lead using the LLM.
    
    Args:
        company_name: Company name
        industry: Industry vertical
        website: Company website (optional)
        notes: Sales notes about the lead
        retry_count: Internal retry counter
    
    Returns:
        LeadScore object with score, label, reason, and suggested role
    
    Raises:
        ValueError: If scoring fails after retries
    """
    try:
        llm = get_llm_client()
        
        # Build the user message
        user_message = SCORING_USER_PROMPT_TEMPLATE.format(
            company_name=company_name,
            industry=industry,
            website=website or "Not provided",
            notes=notes
        )
        
        # Call LLM
        response = llm.call(
            system_prompt=SCORING_SYSTEM_PROMPT,
            user_message=user_message,
            temperature=0.3  # Lower temperature for consistent scoring
        )
        
        # Parse JSON response
        expected_keys = ["score_label", "score_value", "reason", "suggested_contact_role"]
        parsed = llm.parse_json_response(response, expected_keys)
        
        if parsed is None:
            if retry_count < 1:
                logger.warning("First JSON parse attempt failed, retrying...")
                return await score_lead(company_name, industry, website, notes, retry_count + 1)
            else:
                # Fallback safe default
                logger.error("Scoring failed after retries, using safe default")
                return LeadScore(
                    score_label="Cold",
                    score_value=0,
                    reason="AI parsing failed; please review manually.",
                    suggested_contact_role="Founder"
                )
        
        # Validate score_value is in range
        score_value = int(parsed.get("score_value", 0))
        score_value = max(0, min(100, score_value))
        
        # Determine label based on score
        score_label = parsed.get("score_label", "Cold").capitalize()
        if score_value >= 80:
            score_label = "Hot"
        elif score_value >= 50:
            score_label = "Warm"
        else:
            score_label = "Cold"
        
        return LeadScore(
            score_label=score_label,
            score_value=score_value,
            reason=parsed.get("reason", "No reason provided"),
            suggested_contact_role=parsed.get("suggested_contact_role", "Founder")
        )
    
    except Exception as e:
        logger.error(f"Error in score_lead: {e}")
        raise ValueError(f"Failed to score lead: {str(e)}")
