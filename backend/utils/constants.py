SYSTEM_PROMPT = """You are an SEO content writer.

Requirements:
- Return valid JSON only
- Generate semantic HTML
- Use <h1>, <h2>, <p>, <ul>
- Naturally include ALL provided keywords
- Avoid markdown
- No script tags
- Write coherent SEO-friendly content"""

USER_PROMPT_TEMPLATE = """Topic:
{topic}

Keywords:
{keywords}

Target Audience:
{target_audience}

Call To Action:
{call_to_action}"""

ALLOWED_HTML_TAGS = [
    "h1",
    "h2",
    "h3",
    "p",
    "ul",
    "ol",
    "li",
    "strong",
    "em",
    "a",
    "br",
]

ALLOWED_HTML_ATTRIBUTES = {
    "a": ["href", "title", "rel"],
}
