from fastapi import FastAPI
from app.routes import router
from app.middleware.request_logging import request_logging_middleware
from app.routes.admin_routes import router as admin_router
from app.core.app_logging import setup_logging
from app.core.config import settings

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

setup_logging()

app = FastAPI(
    title="Boboloo Backend API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

app.middleware("http")(request_logging_middleware)

app.include_router(router)
app.include_router(admin_router)

# ─────────────────────────────────────────────
# BOBOTV — feature flag guard
# Existing app is unaffected when ENABLE_BOBOTV=false
# ─────────────────────────────────────────────
if settings.ENABLE_BOBOTV:
    try:
        from app.routes.bobotv_routes import router as bobotv_router
        app.include_router(bobotv_router)
        logging.getLogger(__name__).info("BoboTV feature is ENABLED")
    except Exception as exc:  # noqa: BLE001
        logging.getLogger(__name__).error(
            "BoboTV router failed to load — feature disabled: %s", exc
        )


@app.get("/")
async def root():
    return {"status": "Boboloo Backend Running"}


@app.get("/health")
async def health():
    return {"status": "ok"}