import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse

from config.settings import settings
from routes.generate_route import router as generate_router
from services.health_service import (
    build_health_report,
    health_http_status,
    render_health_html,
)

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "app.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

app = FastAPI(
    title="AI SEO Publishing Pipeline",
    description="AI-driven SEO content generation and WordPress publishing",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generate_router)


@app.get("/health")
def health(request: Request):
    report = build_health_report()
    status_code = health_http_status(report)

    if "application/json" in request.headers.get("accept", ""):
        return JSONResponse(content=report, status_code=status_code)

    return HTMLResponse(
        content=render_health_html(report),
        status_code=status_code,
    )
