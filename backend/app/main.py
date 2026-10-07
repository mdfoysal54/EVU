import asyncio
from contextlib import asynccontextmanager
import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

# Execution & Tool Registration
from app.agent.execution.bootstrap import register_default_tools

# Core & Configuration
from app.core.config import settings

# Database & Cache
from app.database import models  # Ensures model metadata is loaded
from app.database.database import Base, engine
from app.database.health import check_database_connection
from app.context import models as context_models  # Ensures context model metadata is loaded
from app.observability.service import observability_service
from app.services.redis_service import redis_service

# API Route Routers
from app.api.routes.agent import router as agent_router
from app.api.routes.audio import router as audio_router
from app.api.routes.auth import router as auth_router
from app.api.routes.browser import router as browser_router
from app.api.routes.chat import router as chat_router
from app.api.routes.context import router as context_router
from app.api.routes.conversations import router as conversations_router
from app.api.routes.diagram import router as diagram_router
from app.api.routes.documents import router as documents_router
from app.api.routes.ensemble import router as ensemble_router
from app.api.routes.evaluation import router as evaluation_router
from app.api.routes.execution import router as execution_router
from app.api.routes.feedback import router as feedback_router
from app.api.routes.memory import router as memory_router
from app.api.routes.models import router as models_router
from app.api.routes.multimodal import router as multimodal_router
from app.api.routes.observability import router as observability_router
from app.api.routes.planning import router as planning_router
from app.api.routes.providers import router as providers_router
from app.api.routes.security import router as security_router
from app.api.routes.synthesis import router as synthesis_router
from app.api.routes.tasks import router as tasks_router
from app.api.routes.telemetry import router as telemetry_router
from app.api.routes.vision import router as vision_router
from app.api.routes.web import router as web_router
from app.research.api.routes import router as research_router

logger = logging.getLogger("uvicorn")


def _init_db_and_tools():
    logger.info("--> Initializing database schemas...")
    # If using async engine, use engine.sync_engine; otherwise plain engine
    target_engine = getattr(engine, "sync_engine", engine)
    Base.metadata.create_all(bind=target_engine)
    logger.info("--> Schemas created. Registering default tools...")
    register_default_tools()
    logger.info("--> Tools registered successfully.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting lifespan initialization...")
    try:
        # Offload synchronous setup off the main event loop
        await asyncio.to_thread(_init_db_and_tools)
        logger.info("Lifespan initialization complete.")
    except Exception as exc:
        logger.error(f"Error during lifespan startup: {exc}", exc_info=True)
        raise exc
    yield
    logger.info("Shutting down application...")


app = FastAPI(
    title=settings.APP_NAME,
    version="1.1.0",
    description="EVU AI",
    lifespan=lifespan,
)

# Allow both hostname formats to avoid browser CORS / Fetch rejections
allowed_origins = list(
    {
        settings.FRONTEND_URL,
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    }
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def observe_requests(request: Request, call_next):
    started = time.perf_counter()
    success = False
    try:
        response = await call_next(request)
        success = response.status_code < 500
        return response
    finally:
        if settings.OBSERVABILITY_ENABLED:
            observability_service.record(
                metric_name="http_request",
                duration_ms=(time.perf_counter() - started) * 1000,
                success=success,
                metadata={"method": request.method, "path": request.url.path},
            )


ROUTERS = [
    agent_router,
    audio_router,
    auth_router,
    browser_router,
    chat_router,
    context_router,
    conversations_router,
    diagram_router,
    documents_router,
    ensemble_router,
    evaluation_router,
    execution_router,
    feedback_router,
    memory_router,
    models_router,
    multimodal_router,
    observability_router,
    planning_router,
    providers_router,
    research_router,
    security_router,
    synthesis_router,
    tasks_router,
    telemetry_router,
    vision_router,
    web_router,
]

for router in ROUTERS:
    app.include_router(router)


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "status": "online",
        "version": "1.1.0",
    }


@app.get("/health")
async def health():
    database_healthy = check_database_connection()
    redis_healthy = await redis_service.ping() if settings.REDIS_ENABLED else False
    return {
        "status": "healthy" if database_healthy else "degraded",
        "database": database_healthy,
        "redis": redis_healthy,
        "redis_enabled": settings.REDIS_ENABLED,
        "rag_enabled": settings.RAG_ENABLED,
        "memory_enabled": settings.MEMORY_ENABLED,
        "security_enabled": settings.SECURITY_ENABLED,
        "observability_enabled": settings.OBSERVABILITY_ENABLED,
        "research_enabled": settings.RESEARCH_ENABLED,
    }