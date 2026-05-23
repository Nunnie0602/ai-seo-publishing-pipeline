import html
from typing import Any

import google.generativeai as genai
import httpx

from config.settings import settings
from services.wordpress_service import _auth_header


def _check_wordpress() -> dict[str, str]:
    if not all(
        [
            settings.wordpress_url,
            settings.wordpress_username,
            settings.wordpress_app_password,
        ]
    ):
        return {
            "status": "ERROR",
            "message": "WordPress credentials are not configured",
        }

    base_url = settings.wordpress_url.rstrip("/")
    endpoint = f"{base_url}/wp-json/wp/v2/users/me"

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(endpoint, headers=_auth_header())
            response.raise_for_status()
        return {"status": "OK"}
    except httpx.HTTPStatusError as exc:
        detail = exc.response.text.strip()[:200] or exc.response.reason_phrase
        return {
            "status": "ERROR",
            "message": f"WordPress API returned {exc.response.status_code}: {detail}",
        }
    except httpx.RequestError as exc:
        return {"status": "ERROR", "message": f"WordPress connection failed: {exc}"}
    except Exception as exc:
        return {"status": "ERROR", "message": str(exc)}


def _check_llm() -> dict[str, str]:
    if not settings.gemini_api_key:
        return {"status": "ERROR", "message": "GEMINI_API_KEY is not configured"}

    try:
        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel(settings.gemini_model)
        model.count_tokens("health")
        return {"status": "OK"}
    except Exception as exc:
        return {"status": "ERROR", "message": str(exc)}


def build_health_report() -> dict[str, dict[str, str]]:
    return {
        "app": {"status": "OK"},
        "wordpress": _check_wordpress(),
        "llm": _check_llm(),
    }


def health_http_status(report: dict[str, dict[str, str]]) -> int:
    for key in ("wordpress", "llm"):
        if report[key].get("status") != "OK":
            return 503
    return 200


def _render_component_row(name: str, component: dict[str, str]) -> str:
    status = component.get("status", "ERROR")
    status_class = "ok" if status == "OK" else "error"
    rows = [
        f'<tr class="{status_class}">',
        f"<td>{html.escape(name)}</td>",
        f"<td>{html.escape(status)}</td>",
        "<td>",
    ]
    if status != "OK":
        message = component.get("message", "Unknown error")
        rows.append(f'<span class="error-msg">{html.escape(message)}</span>')
    else:
        rows.append("—")
    rows.extend(["</td>", "</tr>"])
    return "\n".join(rows)


def render_health_html(report: dict[str, Any]) -> str:
    rows = "\n".join(
        [
            _render_component_row("App", report["app"]),
            _render_component_row("WordPress", report["wordpress"]),
            _render_component_row("LLM", report["llm"]),
        ]
    )
    return f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Health Check</title>
  <style>
    body {{
      font-family: system-ui, -apple-system, sans-serif;
      margin: 2rem auto;
      max-width: 720px;
      padding: 0 1rem;
      color: #1a1a1a;
    }}
    h1 {{ font-size: 1.5rem; margin-bottom: 1rem; }}
    table {{
      width: 100%;
      border-collapse: collapse;
      border: 1px solid #ddd;
    }}
    th, td {{
      padding: 0.75rem 1rem;
      text-align: left;
      border-bottom: 1px solid #eee;
    }}
    th {{ background: #f5f5f5; }}
    tr.ok td:nth-child(2) {{ color: #0a7a2f; font-weight: 600; }}
    tr.error td:nth-child(2) {{ color: #b00020; font-weight: 600; }}
    .error-msg {{ color: #b00020; font-size: 0.9rem; }}
  </style>
</head>
<body>
  <h1>AI SEO Publishing Pipeline — Health</h1>
  <table>
    <thead>
      <tr>
        <th>Component</th>
        <th>Status</th>
        <th>Message</th>
      </tr>
    </thead>
    <tbody>
{rows}
    </tbody>
  </table>
</body>
</html>"""
