from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.config import settings
from app.database.database import get_db
from app.database.models import User
from app.memory.schemas import (
    ConversationMemoryResponse,
    MemoryContextResponse,
    UserMemoryCreate,
    UserMemoryResponse,
    UserMemoryUpdate,
)
from app.memory.service import memory_service


router = APIRouter(
    prefix="/api/v1/memory",
    tags=["EVU Memory"],
)


def _ensure_enabled() -> None:
    if not settings.MEMORY_ENABLED:
        raise HTTPException(
            status_code=503,
            detail="EVU memory is disabled.",
        )


@router.get(
    "",
    response_model=list[UserMemoryResponse],
)
def list_memories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _ensure_enabled()

    return memory_service.list_user_memories(
        db,
        current_user.id,
    )


@router.post(
    "",
    response_model=UserMemoryResponse,
)
def create_memory(
    payload: UserMemoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _ensure_enabled()

    return memory_service.create_user_memory(
        db,
        current_user.id,
        payload,
    )


@router.patch(
    "/{memory_id}",
    response_model=UserMemoryResponse,
)
def update_memory(
    memory_id: int,
    payload: UserMemoryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _ensure_enabled()

    row = memory_service.update_user_memory(
        db,
        current_user.id,
        memory_id,
        payload,
    )

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Memory not found.",
        )

    return row


@router.delete("/{memory_id}")
def delete_memory(
    memory_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _ensure_enabled()

    deleted = memory_service.delete_user_memory(
        db,
        current_user.id,
        memory_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Memory not found.",
        )

    return {
        "deleted": True,
        "memory_id": memory_id,
    }


@router.get(
    "/context/{conversation_id}",
    response_model=MemoryContextResponse,
)
def memory_context(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _ensure_enabled()

    return memory_service.build_context(
        db,
        current_user.id,
        conversation_id,
    )


@router.get(
    "/conversations/{conversation_id}",
    response_model=ConversationMemoryResponse | None,
)
def get_conversation_memory(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _ensure_enabled()

    return memory_service.get_conversation_memory(
        db,
        current_user.id,
        conversation_id,
    )


@router.post(
    "/conversations/{conversation_id}/summary",
    response_model=ConversationMemoryResponse,
)
def save_conversation_summary(
    conversation_id: int,
    payload: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _ensure_enabled()

    summary = str(
        payload.get("summary", "")
    ).strip()

    if not summary:
        raise HTTPException(
            status_code=422,
            detail="summary is required.",
        )

    try:
        return memory_service.save_conversation_summary(
            db,
            current_user.id,
            conversation_id,
            summary,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@router.post(
    "/capture",
    response_model=UserMemoryResponse | None,
)
def capture_explicit_memory(
    payload: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _ensure_enabled()

    text = str(
        payload.get("text", "")
    ).strip()

    if not text:
        raise HTTPException(
            status_code=422,
            detail="text is required.",
        )

    return memory_service.capture_explicit_memory(
        db,
        current_user.id,
        text,
    )