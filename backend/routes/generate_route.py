import logging

from fastapi import APIRouter, HTTPException

from models.schemas import ErrorResponse, GenerateRequest, GenerateSuccessResponse
from services.llm_service import generate_article
from services.prompt_service import build_prompts
from services.sanitizer_service import sanitize_html
from services.validation_service import validate_llm_output
from services.wordpress_service import publish_draft

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/generate",
    response_model=GenerateSuccessResponse,
    responses={500: {"model": ErrorResponse}},
)
def generate(request: GenerateRequest) -> GenerateSuccessResponse:
    try:
        logger.info("[INFO] Building prompt")
        system_prompt, user_prompt = build_prompts(
            topic=request.topic,
            keywords=request.keywords,
            target_audience=request.target_audience,
            call_to_action=request.call_to_action,
        )

        raw_output = generate_article(system_prompt, user_prompt)

        logger.info("[INFO] JSON validation passed")
        article = validate_llm_output(raw_output)

        logger.info("[INFO] HTML sanitized")
        safe_html = sanitize_html(article.content_html)

        wp_result = publish_draft(article.title, safe_html)

        return GenerateSuccessResponse(
            post_id=wp_result["post_id"],
            draft_url=wp_result["draft_url"],
            title=article.title,
            preview_html=safe_html,
        )
    except ValueError as exc:
        logger.error("[ERROR] Validation/config error: %s", exc)
        raise HTTPException(
            status_code=400,
            detail={"status": "error", "message": str(exc)},
        ) from exc
    except Exception as exc:
        logger.error("[ERROR] Generation pipeline failed: %s", exc)
        message = (
            "WordPress publishing failed."
            if "wordpress" in str(exc).lower() or "401" in str(exc)
            else "Generation failed. Please retry."
        )
        raise HTTPException(
            status_code=500,
            detail={"status": "error", "message": message},
        ) from exc
