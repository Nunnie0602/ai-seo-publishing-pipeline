import base64
import logging

import httpx

from config.settings import settings
from utils.retry import with_retry
from utils.retry_policy import is_wp_retryable

logger = logging.getLogger(__name__)


def _auth_header() -> dict[str, str]:
    credentials = f"{settings.wordpress_username}:{settings.wordpress_app_password}"
    token = base64.b64encode(credentials.encode()).decode()
    return {"Authorization": f"Basic {token}"}


def _publish_once(title: str, content_html: str) -> dict:
    base_url = settings.wordpress_url.rstrip("/")
    endpoint = f"{base_url}/wp-json/wp/v2/posts"
    payload = {
        "title": title,
        "content": content_html,
        "status": "draft",
    }

    with httpx.Client(timeout=30.0) as client:
        response = client.post(
            endpoint,
            json=payload,
            headers={**_auth_header(), "Content-Type": "application/json"},
        )
        response.raise_for_status()
        data = response.json()

    post_id = data.get("id")
    draft_url = data.get("link", "")
    if post_id and not draft_url:
        draft_url = f"{base_url}/wp-admin/post.php?post={post_id}&action=edit"

    return {
        "post_id": post_id,
        "draft_url": draft_url,
        "status": data.get("status", "draft"),
    }


def publish_draft(title: str, content_html: str) -> dict:
    if not all(
        [
            settings.wordpress_url,
            settings.wordpress_username,
            settings.wordpress_app_password,
        ]
    ):
        raise ValueError("WordPress credentials are not configured")

    logger.info("[INFO] Publishing to WordPress")

    def _call() -> dict:
        return _publish_once(title, content_html)

    result = with_retry(
        _call,
        max_attempts=settings.wp_max_retries,
        label="WordPress publish",
        retry_on=is_wp_retryable,
    )
    logger.info("[INFO] Draft created successfully (post_id=%s)", result.get("post_id"))
    return result
