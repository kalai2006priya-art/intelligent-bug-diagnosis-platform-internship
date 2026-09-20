import json
import logging
from typing import Dict, Any, Optional
import httpx
from app.config import settings

logger = logging.getLogger(__name__)

class LLMService:
    """
    Unified LLM Service supporting Google Gemini, OpenAI, or Local Heuristic Engine.
    """

    @classmethod
    def is_external_llm_available(cls) -> bool:
        if settings.LLM_PROVIDER == "gemini" and settings.GEMINI_API_KEY:
            return True
        if settings.LLM_PROVIDER == "openai" and settings.OPENAI_API_KEY:
            return True
        return False

    @classmethod
    async def call_gemini(cls, system_prompt: str, user_prompt: str) -> Optional[str]:
        if not settings.GEMINI_API_KEY:
            return None
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": f"{system_prompt}\n\nUser Query:\n{user_prompt}"}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json"
            }
        }
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(url, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            return parts[0].get("text", "")
                else:
                    logger.warning(f"Gemini API returned status {resp.status_code}: {resp.text}")
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")
        return None

    @classmethod
    async def call_openai(cls, system_prompt: str, user_prompt: str) -> Optional[str]:
        if not settings.OPENAI_API_KEY:
            return None
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"}
        }
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(url, headers=headers, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    choices = data.get("choices", [])
                    if choices:
                        return choices[0].get("message", {}).get("content", "")
                else:
                    logger.warning(f"OpenAI API returned status {resp.status_code}: {resp.text}")
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
        return None

    @classmethod
    async def generate_json(cls, system_prompt: str, user_prompt: str) -> Optional[Dict[str, Any]]:
        """
        Attempts to call configured LLM and parse response as JSON.
        Returns None if no LLM configured or call fails.
        """
        raw_text = None
        if settings.LLM_PROVIDER == "gemini" and settings.GEMINI_API_KEY:
            raw_text = await cls.call_gemini(system_prompt, user_prompt)
        elif settings.LLM_PROVIDER == "openai" and settings.OPENAI_API_KEY:
            raw_text = await cls.call_openai(system_prompt, user_prompt)

        if raw_text:
            try:
                # Strip markdown json code block fences if present
                cleaned = raw_text.strip()
                if cleaned.startswith("```json"):
                    cleaned = cleaned[7:]
                if cleaned.startswith("```"):
                    cleaned = cleaned[3:]
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3]
                return json.loads(cleaned.strip())
            except Exception as e:
                logger.error(f"Failed to parse LLM JSON output: {e}. Output was: {raw_text[:200]}")
        return None
