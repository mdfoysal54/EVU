from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class Role(str, Enum):
    USER = "user"
    POWER_USER = "power_user"
    ADMIN = "admin"


class Permission(str, Enum):
    CHAT = "chat"

    USE_CALCULATOR = "use_calculator"
    USE_DOCUMENTS = "use_documents"

    USE_WEB = "use_web"
    USE_BROWSER = "use_browser"

    USE_LOCAL_MODELS = "use_local_models"
    USE_EXTERNAL_MODELS = "use_external_models"

    RUN_AGENT = "run_agent"
    RUN_BACKGROUND_TASK = "run_background_task"

    VIEW_TELEMETRY = "view_telemetry"
    VIEW_AUDIT_LOGS = "view_audit_logs"

    MANAGE_SYSTEM = "manage_system"


class PermissionCheckRequest(BaseModel):
    permission: Permission


class PermissionCheckResponse(BaseModel):
    allowed: bool

    role: Role

    permission: Permission

    reason: str | None = None


class SecurityAuditEvent(BaseModel):
    event_type: str

    user_id: int | None = None

    username: str | None = None

    permission: str | None = None

    tool: str | None = None

    allowed: bool

    details: dict[str, Any] = Field(
        default_factory=dict
    )