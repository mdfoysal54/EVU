from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BACKEND_DIR / ".env"


class Settings(BaseSettings):

    # ---------------------------------------------------------
    # APPLICATION
    # ---------------------------------------------------------
    APP_NAME: str = "EVU"
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./app.db"

    # ---------------------------------------------------------
    # DATABASE POOLING & PERFORMANCE
    # ---------------------------------------------------------
    DATABASE_POOL_PRE_PING: bool = True
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10

    # ---------------------------------------------------------
    # OPENAI
    # ---------------------------------------------------------
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-5-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    # ---------------------------------------------------------
    # ANTHROPIC
    # ---------------------------------------------------------
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-sonnet-4-6"

    # ---------------------------------------------------------
    # GEMINI
    # ---------------------------------------------------------
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # ---------------------------------------------------------
    # XAI
    # ---------------------------------------------------------
    XAI_API_KEY: str = ""
    XAI_MODEL: str = "grok-4.5"

    # ---------------------------------------------------------
    # ZAI
    # ---------------------------------------------------------
    ZAI_API_KEY: str = ""
    ZAI_MODEL: str = "glm-5.1"
    ZAI_BASE_URL: str = "https://api.z.ai/api/paas/v4/"

    # ---------------------------------------------------------
    # AUTHENTICATION
    # ---------------------------------------------------------
    JWT_SECRET_KEY: str = "evu-development-secret-change-before-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # ---------------------------------------------------------
    # REDIS
    # ---------------------------------------------------------
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_ENABLED: bool = False

    # ---------------------------------------------------------
    # FRONTEND
    # ---------------------------------------------------------
    FRONTEND_URL: str = "http://localhost:3000"

    # ---------------------------------------------------------
    # RAG
    # ---------------------------------------------------------
    RAG_ENABLED: bool = True
    RAG_MAX_FILE_SIZE_MB: int = 20
    RAG_CHUNK_SIZE: int = 1200
    RAG_CHUNK_OVERLAP: int = 200
    RAG_TOP_K: int = 5
    RAG_MAX_CONTEXT_CHARS: int = 12000

    # ---------------------------------------------------------
    # AGENT & EXECUTION
    # ---------------------------------------------------------
    AGENT_ENABLED: bool = True
    AGENT_MAX_STEPS: int = 4
    AGENT_MAX_TOOL_OUTPUT_CHARS: int = 6000
    AGENT_EXECUTION_ENABLED: bool = True
    AGENT_TOOL_TIMEOUT_SECONDS: int = 30
    AGENT_MAX_TOOL_CALLS: int = 20
    AGENT_ALLOW_REPLANNING: bool = True
    AGENT_MAX_REPLANS: int = 2

    # ---------------------------------------------------------
    # PLANNING
    # ---------------------------------------------------------
    PLANNING_ENABLED: bool = True
    PLANNING_MAX_STEPS: int = 8
    PLANNING_MAX_EXECUTION_TIME_SECONDS: int = 120
    PLANNING_ALLOW_REPLAN: bool = True
    PLANNING_MAX_REPLANS: int = 2

    # ---------------------------------------------------------
    # TASKS
    # ---------------------------------------------------------
    TASKS_ENABLED: bool = True
    TASK_MAX_CONCURRENT: int = 5
    TASK_DEFAULT_TIMEOUT_SECONDS: int = 300
    TASK_RETENTION_SECONDS: int = 86400

    # ---------------------------------------------------------
    # ENSEMBLE
    # ---------------------------------------------------------
    ENSEMBLE_ENABLED: bool = True
    ENSEMBLE_MAX_MODELS: int = 3
    ENSEMBLE_TIMEOUT_SECONDS: int = 60
    ENSEMBLE_SYNTHESIS_PROVIDER: str = "openai"

    # ---------------------------------------------------------
    # SYNTHESIS
    # ---------------------------------------------------------
    SYNTHESIS_ENABLED: bool = True
    SYNTHESIS_MAX_CANDIDATES: int = 5
    SYNTHESIS_DEFAULT_TEMPERATURE: float = 0.2
    SYNTHESIS_REQUIRE_CONSENSUS: bool = False
    SYNTHESIS_FALLBACK_ENABLED: bool = True

    # ---------------------------------------------------------
    # EVALUATION
    # ---------------------------------------------------------
    EVALUATION_ENABLED: bool = True
    EVALUATION_JUDGE_TIMEOUT_SECONDS: int = 60

    # ---------------------------------------------------------
    # TELEMETRY
    # ---------------------------------------------------------
    TELEMETRY_ENABLED: bool = True
    FEEDBACK_ENABLED: bool = True
    TELEMETRY_RETENTION_DAYS: int = 90

    # ---------------------------------------------------------
    # MEMORY & CONVERSATION
    # ---------------------------------------------------------
    MEMORY_ENABLED: bool = True
    USER_MEMORY_ENABLED: bool = True
    CONVERSATION_MEMORY_ENABLED: bool = True
    MEMORY_MAX_ITEMS: int = 50
    MEMORY_MAX_CONTEXT_CHARS: int = 6000
    CONVERSATION_SUMMARY_TRIGGER_MESSAGES: int = 12
    CONVERSATION_SUMMARY_MAX_CHARS: int = 8000
    CONVERSATION_RECENT_MESSAGES: int = 12

    # ---------------------------------------------------------
    # MEMORY RETRIEVAL & FUSION
    # ---------------------------------------------------------
    MEMORY_HYBRID_SEARCH_ENABLED: bool = True
    MEMORY_BM25_ENABLED: bool = True
    MEMORY_VECTOR_ENABLED: bool = True
    MEMORY_GRAPH_ENABLED: bool = True
    MEMORY_BM25_WEIGHT: float = 0.40
    MEMORY_VECTOR_WEIGHT: float = 0.40
    MEMORY_GRAPH_WEIGHT: float = 0.20
    MEMORY_RRF_K: int = 60
    MEMORY_MAX_RESULTS: int = 12
    MEMORY_MAX_RESULTS_PER_SESSION: int = 3
    MEMORY_CONTEXT_TOKEN_BUDGET: int = 2000
    MEMORY_MAX_OBSERVATIONS_PER_SESSION: int = 500

    # ---------------------------------------------------------
    # MEMORY MANAGEMENT & GOVERNANCE
    # ---------------------------------------------------------
    MEMORY_AUTO_COMPRESS: bool = True
    MEMORY_CONSOLIDATION_ENABLED: bool = True
    MEMORY_GRAPH_EXTRACTION_ENABLED: bool = True
    MEMORY_DEDUP_ENABLED: bool = True
    MEMORY_PROVENANCE_ENABLED: bool = True
    MEMORY_VERSIONING_ENABLED: bool = True
    MEMORY_PROJECT_SCOPING_ENABLED: bool = True
    MEMORY_AGENT_SCOPING_ENABLED: bool = True
    MEMORY_RECENCY_ENABLED: bool = True
    MEMORY_CONFIDENCE_ENABLED: bool = True
    MEMORY_LESSONS_ENABLED: bool = True
    MEMORY_PROCEDURAL_ENABLED: bool = True
    MEMORY_CRYSTALS_ENABLED: bool = True

    # ---------------------------------------------------------
    # WEB INTELLIGENCE
    # ---------------------------------------------------------
    WEB_SEARCH_ENABLED: bool = True
    WEB_SEARCH_API_KEY: str = ""
    WEB_SEARCH_API_URL: str = "https://api.tavily.com/search"
    WEB_SEARCH_TIMEOUT_SECONDS: int = 15
    WEB_SEARCH_DEPTH: str = "basic"
    WEB_SEARCH_FALLBACK_ENABLED: bool = True

    # ---------------------------------------------------------
    # BROWSER
    # ---------------------------------------------------------
    BROWSER_ENABLED: bool = True
    BROWSER_HEADLESS: bool = True
    BROWSER_NAVIGATION_TIMEOUT_MS: int = 30000
    BROWSER_ACTION_TIMEOUT_MS: int = 10000
    BROWSER_MAX_PAGE_TEXT_CHARS: int = 20000
    BROWSER_MAX_SESSIONS: int = 5

    # ---------------------------------------------------------
    # MULTIMODAL STORAGE
    # ---------------------------------------------------------
    MULTIMODAL_ENABLED: bool = True
    MULTIMODAL_STORAGE_DIR: str = "./multimodal_storage"
    MULTIMODAL_MAX_FILE_SIZE_MB: int = 20
    MULTIMODAL_MAX_IMAGE_SIZE_MB: int = 10
    MULTIMODAL_MAX_AUDIO_SIZE_MB: int = 25
    MULTIMODAL_MAX_VIDEO_SIZE_MB: int = 100
    MULTIMODAL_MAX_DOCUMENT_SIZE_MB: int = 20
    MULTIMODAL_CHUNK_SIZE_BYTES: int = 1024 * 1024

    # ---------------------------------------------------------
    # VISION
    # ---------------------------------------------------------
    VISION_ENABLED: bool = True
    VISION_PROVIDER: str = "openai"
    VISION_MODEL: str = "gpt-5.6-luna"
    VISION_MAX_IMAGE_SIZE_MB: int = 10
    VISION_MAX_PROMPT_CHARS: int = 12000

    # ---------------------------------------------------------
    # AUDIO
    # ---------------------------------------------------------
    AUDIO_ENABLED: bool = True
    AUDIO_PROVIDER: str = "openai"
    AUDIO_TRANSCRIPTION_MODEL: str = "gpt-4o-transcribe"
    AUDIO_MAX_FILE_SIZE_MB: int = 25
    AUDIO_MAX_PROMPT_CHARS: int = 4000

    # ---------------------------------------------------------
    # LOCAL MODELS
    # ---------------------------------------------------------
    LOCAL_MODELS_ENABLED: bool = True
    LOCAL_MODEL_RUNTIME: str = "ollama"
    OLLAMA_ENABLED: bool = True
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_TIMEOUT_SECONDS: int = 120
    OLLAMA_DEFAULT_MODEL: str = "gemma3"
    OLLAMA_ALLOW_AUTO_DISCOVERY: bool = True

    # ---------------------------------------------------------
    # ADVANCED ROUTING
    # ---------------------------------------------------------
    ADVANCED_ROUTING_ENABLED: bool = True
    ROUTING_PREFER_LOCAL: bool = False
    ROUTING_PRIVACY_MODE: bool = False
    ROUTING_LATENCY_MODE: bool = False
    ROUTING_MINIMUM_SCORE: float = 0.0
    ROUTING_MAX_CANDIDATES: int = 5
    ROUTING_ENABLE_FALLBACK: bool = True
    ROUTING_LEARN_FROM_TELEMETRY: bool = True

    # ---------------------------------------------------------
    # SECURITY
    # ---------------------------------------------------------
    SECURITY_ENABLED: bool = True
    SECURITY_DENY_UNKNOWN_TOOLS: bool = True
    SECURITY_AUDIT_ENABLED: bool = True

    # ---------------------------------------------------------
    # OBSERVABILITY
    # ---------------------------------------------------------
    OBSERVABILITY_ENABLED: bool = True
    OBSERVABILITY_LOG_LEVEL: str = "INFO"
    OBSERVABILITY_METRICS_ENABLED: bool = True
    OBSERVABILITY_ADMIN_ONLY: bool = True

    # ---------------------------------------------------------
    # RESEARCH & FABRIC
    # ---------------------------------------------------------
    RESEARCH_ENABLED: bool = True
    DATASET_BUILDER_ENABLED: bool = True
    TRAINING_ENABLED: bool = True
    CONTEXT_FABRIC_ENABLED: bool = True
    CONTEXT_EMBEDDINGS_ENABLED: bool = True
    CONTEXT_L0_MAX_CHARS: int = 256
    CONTEXT_L1_MAX_CHARS: int = 4000
    CONTEXT_MAX_ASSEMBLED_CHARS: int = 12000
    CONTEXT_DEFAULT_RETRIEVAL_LIMIT: int = 8
    CONTEXT_ENABLE_TYPED_QUERY_ROUTING: bool = True
    CONTEXT_ENABLE_HIERARCHICAL_RETRIEVAL: bool = True
    CONTEXT_ENABLE_TIER_DEGRADATION: bool = True
    CONTEXT_ENABLE_SKILLS: bool = True
    CONTEXT_ENABLE_RETRIEVAL_TRACE: bool = True
    CONTEXT_SCORE_SEMANTIC_WEIGHT: float = 0.85
    CONTEXT_SCORE_LEXICAL_WEIGHT: float = 0.15
    CONTEXT_HIERARCHICAL_SCORE_ALPHA: float = 0.70

    # ---------------------------------------------------------
    # EVU OWN MODEL
    # ---------------------------------------------------------
    EVU_ENABLED: bool = True
    EVU_MODEL_BUNDLE_DIR: str = "./models/evu"
    EVU_MODEL_DEVICE: str = "cpu"
    EVU_MODEL_MAX_NEW_TOKENS: int = 128
    EVU_MODEL_TEMPERATURE: float = 0.7
    EVU_MODEL_TOP_K: int = 50
    EVU_MODEL_TOP_P: float = 0.95
    EVU_DEFAULT_PROVIDER: str = "evu"
    EVU_FALLBACK_PROVIDER: str = ""

    # ---------------------------------------------------------
    # PYDANTIC SETTINGS
    # ---------------------------------------------------------
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()