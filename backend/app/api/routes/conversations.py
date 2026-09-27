import json

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.gateway import ai_gateway
from app.api.dependencies import get_current_user
from app.core.config import settings
from app.database.database import get_db
from app.database.models import Conversation, Message, User
from app.memory.service import memory_service
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.conversation import (
    ConversationCreate,
    ConversationDetailResponse,
    ConversationResponse,
)
from app.schemas.document import RAGSource
from app.services.rag_service import rag_service
from app.services.redis_service import redis_service


router = APIRouter(
    prefix="/api/v1/conversations",
    tags=["Conversations"],
)


SYSTEM_PROMPT = (
    "You are EVU, an intelligent AI assistant. "
    "Be helpful, accurate, clear, and honest."
)


def get_user_conversation(
    conversation_id: int,
    user: User,
    db: Session,
) -> Conversation:
    conversation = db.scalar(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user.id,
        )
    )

    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    return conversation


def build_messages(
    conversation: Conversation,
    db: Session,
    user_id: int,
    user_text: str,
    rag_context: str = "",
) -> list[dict]:
    """
    Build a bounded context window.

    Order:

    system prompt
    user memory
    conversation memory
    recent messages
    current user message
    """

    system = SYSTEM_PROMPT

    memory_context = memory_service.build_memory_context(
        db,
        user_id,
        conversation.id,
    )

    if memory_context:
        system += (
            "\n\n"
            + memory_context
        )

    if rag_context:
        system += (
            "\n\n"
            + rag_context
        )

    messages: list[dict] = [
        {
            "role": "system",
            "content": system,
        }
    ]

    # ---------------------------------------------------------
    # CONVERSATION MEMORY
    # ---------------------------------------------------------

    conversation_memory = (
        memory_service.get_conversation_memory(
            db,
            user_id,
            conversation.id,
        )
    )

    if (
        conversation_memory is not None
        and conversation_memory.summary.strip()
    ):
        messages.append(
            {
                "role": "system",
                "content": (
                    "Earlier conversation summary:\n"
                    f"{conversation_memory.summary}"
                ),
            }
        )

    # ---------------------------------------------------------
    # RECENT MESSAGES ONLY
    # ---------------------------------------------------------

    recent_messages = list(
        db.scalars(
            select(Message)
            .where(
                Message.conversation_id
                == conversation.id
            )
            .order_by(
                Message.created_at.desc(),
                Message.id.desc(),
            )
            .limit(
                settings.CONVERSATION_RECENT_MESSAGES
            )
        )
    )

    recent_messages.reverse()

    messages.extend(
        {
            "role": message.role,
            "content": message.content,
        }
        for message in recent_messages
    )

    messages.append(
        {
            "role": "user",
            "content": user_text,
        }
    )

    return messages


async def get_rag_context(
    user_id: int,
    request: ChatRequest,
    db: Session,
):
    if not request.use_rag:
        return "", []

    retrieved = await rag_service.retrieve(
        user_id,
        request.message,
        db,
    )

    return (
        rag_service.build_context(retrieved),
        retrieved,
    )


@router.post(
    "",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_conversation(
    request: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conversation = Conversation(
        user_id=current_user.id,
        title=request.title,
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation


@router.get(
    "",
    response_model=list[ConversationResponse],
)
def list_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return list(
        db.scalars(
            select(Conversation)
            .where(
                Conversation.user_id
                == current_user.id
            )
            .order_by(
                Conversation.created_at.desc()
            )
        )
    )


@router.get(
    "/{conversation_id}",
    response_model=ConversationDetailResponse,
)
def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_user_conversation(
        conversation_id,
        current_user,
        db,
    )


@router.post(
    "/{conversation_id}/chat",
    response_model=ChatResponse,
)
async def conversation_chat(
    conversation_id: int,
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conversation = get_user_conversation(
        conversation_id,
        current_user,
        db,
    )

    # ---------------------------------------------------------
    # USER MEMORY
    # ---------------------------------------------------------

    memory_service.capture_explicit_memories(
        db,
        current_user.id,
        request.message,
    )

    # ---------------------------------------------------------
    # RAG
    # ---------------------------------------------------------

    rag_context, retrieved = await get_rag_context(
        current_user.id,
        request,
        db,
    )

    # ---------------------------------------------------------
    # BUILD MEMORY-AWARE CONTEXT
    # ---------------------------------------------------------

    messages = build_messages(
        conversation,
        db,
        current_user.id,
        request.message,
        rag_context,
    )

    try:
        response = await ai_gateway.generate(
            messages,
            request.provider,
            request.model,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"AI provider error: {exc}",
        ) from exc

    # ---------------------------------------------------------
    # SAVE MESSAGE
    # ---------------------------------------------------------

    db.add(
        Message(
            conversation_id=conversation.id,
            role="user",
            content=request.message,
        )
    )

    db.add(
        Message(
            conversation_id=conversation.id,
            role="assistant",
            content=response,
        )
    )

    db.commit()

    await redis_service.set_conversation_activity(
        conversation.id,
        current_user.id,
    )

    # ---------------------------------------------------------
    # UPDATE LONG-TERM MEMORY
    # ---------------------------------------------------------

    await memory_service.maybe_summarize_conversation(
        db,
        current_user.id,
        conversation.id,
    )

    sources = [
        RAGSource(
            document_id=item.document_id,
            filename=item.filename,
            chunk_index=item.chunk_index,
            score=item.score,
        )
        for item in retrieved
    ]

    return ChatResponse(
        response=response,
        provider=request.provider,
        model=request.model,
        rag_used=bool(rag_context),
        sources=sources,
    )


@router.post(
    "/{conversation_id}/stream",
)
async def conversation_stream(
    conversation_id: int,
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conversation = get_user_conversation(
        conversation_id,
        current_user,
        db,
    )

    # ---------------------------------------------------------
    # USER MEMORY
    # ---------------------------------------------------------

    memory_service.capture_explicit_memories(
        db,
        current_user.id,
        request.message,
    )

    # ---------------------------------------------------------
    # RAG
    # ---------------------------------------------------------

    rag_context, retrieved = await get_rag_context(
        current_user.id,
        request,
        db,
    )

    # ---------------------------------------------------------
    # MEMORY-AWARE CONTEXT
    # ---------------------------------------------------------

    messages = build_messages(
        conversation,
        db,
        current_user.id,
        request.message,
        rag_context,
    )

    async def event_generator():
        chunks: list[str] = []

        try:
            async for delta in ai_gateway.stream(
                messages,
                request.provider,
                request.model,
            ):
                chunks.append(delta)

                yield (
                    "data: "
                    + json.dumps(
                        {"delta": delta}
                    )
                    + "\n\n"
                )

            full_response = "".join(chunks)

            if not full_response:
                raise RuntimeError(
                    "AI provider returned an empty response."
                )

            # -------------------------------------------------
            # SAVE MESSAGES
            # -------------------------------------------------

            db.add(
                Message(
                    conversation_id=conversation.id,
                    role="user",
                    content=request.message,
                )
            )

            db.add(
                Message(
                    conversation_id=conversation.id,
                    role="assistant",
                    content=full_response,
                )
            )

            db.commit()

            await redis_service.set_conversation_activity(
                conversation.id,
                current_user.id,
            )

            # -------------------------------------------------
            # LONG-TERM SUMMARY
            # -------------------------------------------------

            await memory_service.maybe_summarize_conversation(
                db,
                current_user.id,
                conversation.id,
            )

            sources = [
                {
                    "document_id": item.document_id,
                    "filename": item.filename,
                    "chunk_index": item.chunk_index,
                    "score": item.score,
                }
                for item in retrieved
            ]

            yield (
                "data: "
                + json.dumps(
                    {
                        "done": True,
                        "provider": request.provider,
                        "model": request.model,
                        "sources": sources,
                    }
                )
                + "\n\n"
            )

            yield "data: [DONE]\n\n"

        except Exception as exc:
            db.rollback()

            yield (
                "data: "
                + json.dumps(
                    {"error": str(exc)}
                )
                + "\n\n"
            )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )