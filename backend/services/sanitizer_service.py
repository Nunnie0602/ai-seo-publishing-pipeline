import bleach

from utils.constants import ALLOWED_HTML_ATTRIBUTES, ALLOWED_HTML_TAGS


def sanitize_html(html: str) -> str:
    return bleach.clean(
        html,
        tags=ALLOWED_HTML_TAGS,
        attributes=ALLOWED_HTML_ATTRIBUTES,
        strip=True,
    )
