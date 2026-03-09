from fastapi import FastAPI

from app.routes import router
from app.routes.admin_routes import router as admin_router
from app.routes import interaction_settings_routes

from app.middleware.request_logging import request_logging_middleware
from app.core.app_logging import setup_logging
from app.core.config import settings


setup_logging()

app = FastAPI(
    title="Boboloo Backend API",
    version="1.0.0",
    docs_url=None if settings.ENVIRONMENT == "production" else "/docs",
    redoc_url=None if settings.ENVIRONMENT == "production" else "/redoc",
)

app.middleware("http")(request_logging_middleware)

app.include_router(router)
app.include_router(admin_router)

# Interaction Tuner
app.include_router(interaction_settings_routes.router)


@app.get("/")
async def root():
    return {"status": "Boboloo Backend Running"}


@app.get("/health")
async def health():
    return {"status": "ok"}