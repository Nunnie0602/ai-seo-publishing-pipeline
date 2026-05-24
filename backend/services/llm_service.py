import logging

import google.generativeai as genai

from config.settings import settings
from utils.constants import SYSTEM_PROMPT
from utils.parser import extract_json_from_response
from utils.retry import with_retry

logger = logging.getLogger(__name__)


def generate_article(system_prompt: str, user_prompt: str) -> dict:
    if not settings.gemini_api_key:
        raise ValueError("GEMINI_API_KEY is not configured")

    genai.configure(api_key=settings.gemini_api_key)
    model = genai.GenerativeModel(
        model_name=settings.gemini_model,
        system_instruction=system_prompt or SYSTEM_PROMPT,
        generation_config=genai.GenerationConfig(
            temperature=settings.llm_temperature,
            response_mime_type="application/json",
            response_schema={
                "type": "OBJECT",
                "properties": {
                    "title": {
                        "type": "STRING",
                        "description": (
                            "Post title for WordPress metadata. "
                            "Must not appear in content_html."
                        ),
                    },
                    "content_html": {
                        "type": "STRING",
                        "description": (
                            "Article body HTML only. No <h1> and no post title. "
                            "Start with <p>; use <h2> for section headings."
                        ),
                    },
                },
                "required": ["title", "content_html"],
            },
        ),
    )

    def _call() -> dict:
        logger.info("[INFO] Calling Gemini API")
        response = model.generate_content(user_prompt)
        text = response.text or ""
        return extract_json_from_response(text)

    return with_retry(
        _call,
        max_attempts=settings.llm_max_retries,
        label="LLM generation",
    )
