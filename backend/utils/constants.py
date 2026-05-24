SYSTEM_PROMPT = """You are an SEO content writer.

Output contract:
- Return valid JSON only with "title" and "content_html"
- "title": post title for WordPress metadata; do not repeat it in content_html
- "content_html": article body blocks only
  - Do NOT include <h1> or the post title
  - Start with an intro <p> paragraph
  - Use <h2> for section headings (and <h3> if needed)

HTML requirements:
- Generate semantic HTML using <h2>, <h3>, <p>, <ul>, <ol>
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
