import re

from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.models import Conversation, Message
from app.memory.models import ConversationMemory, UserMemory
from app.memory.schemas import (
    MemoryContextResponse,
    UserMemoryCreate,
    UserMemoryUpdate,
)


class MemoryService:
    """Persistent memory primitives for EVU.

    Step 14 deliberately separates memory storage from the live model
    pipeline. This keeps the existing chat/agent/orchestration code stable
    while exposing reusable context builders for later pipeline integration.
    """

    _EXPLICIT_PATTERNS = (
        (
            re.compile(r"^\s*remember\s+that\s+(.+)$", re.I),
            "general",
            "statement",
        ),
        (
            re.compile(r"^\s*remember\s+i\s+(.+)$", re.I),
            "general",
            "user_statement",
        ),
        (
            re.compile(
                r"^\s*my\s+preferred\s+language\s+is\s+(.+)$",
                re.I,
            ),
            "preference",
            "language",
        ),
        (
            re.compile(r"^\s*i\s+prefer\s+(.+)$", re.I),
            "preference",
            "preference",
        ),
        (
            re.compile(r"^\s*i\s+like\s+(.+)$", re.I),
            "preference",
            "likes",
        ),
        (
            re.compile(r"^\s*i\s+don't\s+like\s+(.+)$", re.I),
            "preference",
            "dislikes",
        ),
        (
            re.compile(r"^\s*call\s+me\s+(.+)$", re.I),
            "identity",
            "preferred_name",
        ),
    )

    def list_user_memories(
        self,
        db: Session,
        user_id: int,
    ) -> list[UserMemory]:
        if not settings.USER_MEMORY_ENABLED:
            return []

        return (
            db.query(UserMemory)
            .filter(
                UserMemory.user_id == user_id,
                UserMemory.is_active.is_(True),
            )
            .order_by(UserMemory.updated_at.desc())
            .limit(settings.MEMORY_MAX_ITEMS)
            .all()
        )

    def create_user_memory(
        self,
        db: Session,
        user_id: int,
        payload: UserMemoryCreate,
    ) -> UserMemory:
        existing = (
            db.query(UserMemory)
            .filter(
                UserMemory.user_id == user_id,
                UserMemory.category == payload.category,
                UserMemory.key == payload.key,
            )
            .first()
        )

        if existing:
            existing.value = payload.value
            existing.source = payload.source
            existing.confidence = payload.confidence
            existing.is_active = True

            db.commit()
            db.refresh(existing)

            return existing

        row = UserMemory(
            user_id=user_id,
            category=payload.category,
            key=payload.key,
            value=payload.value,
            source=payload.source,
            confidence=payload.confidence,
            is_active=True,
        )

        db.add(row)
        db.commit()
        db.refresh(row)

        return row

    def update_user_memory(
        self,
        db: Session,
        user_id: int,
        memory_id: int,
        payload: UserMemoryUpdate,
    ) -> UserMemory | None:
        row = (
            db.query(UserMemory)
            .filter(
                UserMemory.id == memory_id,
                UserMemory.user_id == user_id,
            )
            .first()
        )

        if row is None:
            return None

        data = payload.model_dump(exclude_unset=True)

        for key, value in data.items():
            setattr(row, key, value)

        db.commit()
        db.refresh(row)

        return row

    def delete_user_memory(
        self,
        db: Session,
        user_id: int,
        memory_id: int,
    ) -> bool:
        row = (
            db.query(UserMemory)
            .filter(
                UserMemory.id == memory_id,
                UserMemory.user_id == user_id,
            )
            .first()
        )

        if row is None:
            return False

        # Soft delete so the memory record is not destroyed immediately.
        row.is_active = False

        db.commit()

        return True

    def extract_explicit_memory(
        self,
        text: str,
    ) -> UserMemoryCreate | None:
        if not settings.USER_MEMORY_ENABLED:
            return None

        for pattern, category, key in self._EXPLICIT_PATTERNS:
            match = pattern.match(text)

            if not match:
                continue

            value = match.group(1).strip()

            if not value:
                return None

            return UserMemoryCreate(
                category=category,
                key=key,
                value=value,
                source="explicit_user_statement",
                confidence=1.0,
            )

        return None

    def capture_explicit_memory(
        self,
        db: Session,
        user_id: int,
        text: str,
    ) -> UserMemory | None:
        payload = self.extract_explicit_memory(text)

        if payload is None:
            return None

        return self.create_user_memory(
            db,
            user_id,
            payload,
        )

    def build_user_memory_context(
        self,
        db: Session,
        user_id: int,
    ) -> str:
        rows = self.list_user_memories(
            db,
            user_id,
        )

        if not rows:
            return ""

        lines = [
            "PERSISTED USER MEMORY:",
            (
                "Use these facts/preferences when relevant. "
                "Do not mention this internal memory block unless asked."
            ),
        ]

        for row in rows:
            lines.append(
                f"- {row.category}.{row.key}: {row.value}"
            )

        return "\n".join(lines)[
            : settings.MEMORY_MAX_CONTEXT_CHARS
        ]

    def get_conversation_memory(
        self,
        db: Session,
        user_id: int,
        conversation_id: int,
    ) -> ConversationMemory | None:
        if not settings.CONVERSATION_MEMORY_ENABLED:
            return None

        conversation = (
            db.query(Conversation)
            .filter(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,
            )
            .first()
        )

        if conversation is None:
            return None

        return (
            db.query(ConversationMemory)
            .filter(
                ConversationMemory.conversation_id
                == conversation_id
            )
            .first()
        )

    def build_conversation_context(
        self,
        db: Session,
        user_id: int,
        conversation_id: int,
    ) -> str:
        memory = self.get_conversation_memory(
            db,
            user_id,
            conversation_id,
        )

        if memory is None or not memory.summary.strip():
            return ""

        return (
            "PERSISTED CONVERSATION SUMMARY:\n"
            "Use this summary as background context. "
            "Recent messages should take precedence.\n"
            + memory.summary[
                : settings.CONVERSATION_SUMMARY_MAX_CHARS
            ]
        )

    def build_context(
        self,
        db: Session,
        user_id: int,
        conversation_id: int | None = None,
    ) -> MemoryContextResponse:
        user_context = self.build_user_memory_context(
            db,
            user_id,
        )

        conversation_context = ""

        if conversation_id is not None:
            conversation_context = (
                self.build_conversation_context(
                    db,
                    user_id,
                    conversation_id,
                )
            )

        return MemoryContextResponse(
            user_memory=user_context,
            conversation_memory=conversation_context,
        )

    def recent_messages(
        self,
        db: Session,
        user_id: int,
        conversation_id: int,
    ) -> list[Message]:
        conversation = (
            db.query(Conversation)
            .filter(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,
            )
            .first()
        )

        if conversation is None:
            return []

        messages = (
            db.query(Message)
            .filter(
                Message.conversation_id == conversation_id
            )
            .order_by(Message.created_at.desc())
            .limit(settings.CONVERSATION_RECENT_MESSAGES)
            .all()
        )

        return list(reversed(messages))

    def save_conversation_summary(
        self,
        db: Session,
        user_id: int,
        conversation_id: int,
        summary: str,
    ) -> ConversationMemory:
        conversation = (
            db.query(Conversation)
            .filter(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,
            )
            .first()
        )

        if conversation is None:
            raise ValueError(
                "Conversation not found for current user."
            )

        message_count = (
            db.query(Message)
            .filter(
                Message.conversation_id == conversation_id
            )
            .count()
        )

        last_message = (
            db.query(Message)
            .filter(
                Message.conversation_id == conversation_id
            )
            .order_by(Message.id.desc())
            .first()
        )

        row = (
            db.query(ConversationMemory)
            .filter(
                ConversationMemory.conversation_id
                == conversation_id
            )
            .first()
        )

        bounded_summary = summary[
            : settings.CONVERSATION_SUMMARY_MAX_CHARS
        ]

        if row is None:
            row = ConversationMemory(
                conversation_id=conversation_id,
                summary=bounded_summary,
                message_count=message_count,
                last_summarized_message_id=(
                    last_message.id
                    if last_message
                    else None
                ),
            )

            db.add(row)

        else:
            row.summary = bounded_summary
            row.message_count = message_count

            if last_message:
                row.last_summarized_message_id = (
                    last_message.id
                )

        db.commit()
        db.refresh(row)

        return row


memory_service = MemoryService()