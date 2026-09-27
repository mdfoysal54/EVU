from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

# Core Routes
from app.api.routes.auth import router as auth_router
from app.api.routes.chat import router as chat_router
from app.api.routes.conversations import router as conversations_router
from app.api.routes.documents import router as documents_router
from app.api.routes.providers import router as providers_router

# AI Routes
from app.api.routes.agent import router as agent_router
from app.api.routes.ensemble import router as ensemble_router
from app.api.routes.evaluation import router as evaluation_router
from app.api.routes.models import router as models_router
from app.api.routes.synthesis import router as synthesis_router

# Agent / Execution Routes
from app.api.routes.planning import router as planning_router
from app.api.routes.execution import router as execution_router
from app.api.routes.tasks import router as tasks_router

# RAG / Memory / Web / Browser
from app.api.routes.memory import router as memory_router
from app.api.routes.web import router as web_router
from app.api.routes.browser import router as browser_router

# Multimodal Routes
from app.api.routes.audio import router as audio_router
from app.api.routes.vision import router as vision_router
from app.api.routes.multimodal import router as multimodal_router

# Platform Routes
from app.api.routes.telemetry import router as telemetry_router
from app.api.routes.feedback import router as feedback_router
from app.api.routes.security import router as security_router
from app.api.routes.observability import router as observability_router

# Research / Future Model Training
from app.research.api.routes import router as research_router

# Context Layer
from app.api.routes.context import router as context_router
from app.context import models as context_models

# Database & Cache
from app.database import models
from app.database.database import Base, engine
from app.database.health import check_database_connection
from app.services.redis_service import redis_service

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="EVU AI Meta-Orchestrator",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database tables
Base.metadata.create_all(bind=engine)

# Route Registrations
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(conversations_router)
app.include_router(documents_router)
app.include_router(providers_router)
app.include_router(models_router)
app.include_router(agent_router)
app.include_router(ensemble_router)
app.include_router(evaluation_router)
app.include_router(synthesis_router)
app.include_router(planning_router)
app.include_router(execution_router)
app.include_router(tasks_router)
app.include_router(memory_router)
app.include_router(web_router)
app.include_router(browser_router)
app.include_router(audio_router)
app.include_router(vision_router)
app.include_router(multimodal_router)
app.include_router(telemetry_router)
app.include_router(feedback_router)
app.include_router(security_router)
app.include_router(observability_router)
app.include_router(research_router)
app.include_router(context_router)


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "status": "online",
        "version": "1.0.0",
    }


@app.get("/health")
async def health():
    database_healthy = check_database_connection()
    redis_healthy = False

    if settings.REDIS_ENABLED:
        redis_healthy = await redis_service.ping()

    status = "healthy"
    if not database_healthy:
        status = "degraded"

    return {
        "status": status,
        "database": database_healthy,
        "redis": redis_healthy,
        "redis_enabled": settings.REDIS_ENABLED,
        "rag_enabled": settings.RAG_ENABLED,
        "memory_enabled": settings.MEMORY_ENABLED,
        "security_enabled": settings.SECURITY_ENABLED,
        "observability_enabled": settings.OBSERVABILITY_ENABLED,
        "research_enabled": settings.RESEARCH_ENABLED,
    }