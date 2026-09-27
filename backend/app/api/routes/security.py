from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user
from app.security.audit import (
    security_audit_logger,
)
from app.security.schemas import (
    PermissionCheckRequest,
)
from app.security.service import (
    security_service,
)

router = APIRouter(
    prefix="/api/v1/security",
    tags=["EVU Security"],
)


@router.get("/me")
async def security_me(
    current_user=Depends(get_current_user),
):
    role = security_service.resolve_role(
        current_user
    )

    return {
        "user_id": getattr(
            current_user,
            "id",
            None,
        ),
        "username": getattr(
            current_user,
            "username",
            None,
        ),
        "role": role.value,
    }


@router.post("/check")
async def check_permission(
    request: PermissionCheckRequest,
    current_user=Depends(get_current_user),
):
    result = security_service.check_permission(
        current_user,
        request.permission,
    )

    return result


@router.get("/audit")
async def audit_events(
    current_user=Depends(get_current_user),
):
    role = security_service.resolve_role(
        current_user
    )

    if role.value != "admin":
        return {
            "error": "Admin permission required."
        }

    return {
        "events": [
            event.model_dump()
            for event
            in security_audit_logger.list_events()
        ]
    }