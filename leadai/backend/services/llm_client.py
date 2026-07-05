"""
LLM Client - Abstraction layer for LLM calls
Designed for easy swapping between Groq and other providers (e.g., Gemini)
"""

import os
import json
import logging
from typing import Optional
from groq import Groq

logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")
        self.client = Groq(api_key=self.api_key)
        # Using llama-3.3-70b-versatile - currently available on Groq
        self.model = "llama-3.3-70b-versatile"
    
    def call(self, system_prompt: str, user_message: str, temperature: float = 0.3) -> str:
        """
        Make a call to the LLM.
        
        Args:
            system_prompt: System-level instructions
            user_message: User prompt/message
            temperature: Controls randomness (0.0-1.0)
        
        Returns:
            Raw response text from the LLM
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=temperature,
                max_tokens=1024
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM API error: {e}")
            raise
    
    def parse_json_response(self, response: str, expected_keys: list) -> Optional[dict]:
        """
        Safely parse JSON response from LLM, with fallback handling.
        
        Args:
            response: Raw LLM response
            expected_keys: List of keys expected in the JSON
        
        Returns:
            Parsed dict or None if parsing fails
        """
        try:
            # Try to extract JSON from response (in case there's extra text)
            response = response.strip()
            if response.startswith('{'):
                end_idx = response.rfind('}')
                if end_idx != -1:
                    response = response[:end_idx + 1]
            
            data = json.loads(response)
            
            # Validate expected keys
            for key in expected_keys:
                if key not in data:
                    logger.warning(f"Missing expected key in LLM response: {key}")
                    return None
            
            return data
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error in LLM response: {e}")
            logger.error(f"Response was: {response[:200]}")
            return None


def get_llm_client() -> LLMClient:
    """Get or create LLM client instance."""
    return LLMClient()
