from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional
import uuid


@dataclass
class AgentMessage:
    sender_id: str
    content: Any

    recipient_id: Optional[str] = None

    message_type: str = "message"

    conversation_id: Optional[str] = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    message_id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class MessageBus:
    """
    Lightweight in-process message bus.

    Redis/pub-sub can later replace this implementation.
    """

    def __init__(self) -> None:
        self._handlers: Dict[
            str,
            List[Callable[[AgentMessage], None]],
        ] = {}

        self._history: List[AgentMessage] = []

    def subscribe(
        self,
        agent_id: str,
        handler: Callable[[AgentMessage], None],
    ) -> None:
        self._handlers.setdefault(
            agent_id,
            [],
        ).append(handler)

    def unsubscribe(
        self,
        agent_id: str,
        handler: Callable[[AgentMessage], None],
    ) -> None:
        handlers = self._handlers.get(agent_id, [])

        if handler in handlers:
            handlers.remove(handler)

    def publish(
        self,
        message: AgentMessage,
    ) -> AgentMessage:
        self._history.append(message)

        if message.recipient_id is not None:
            handlers = self._handlers.get(
                message.recipient_id,
                [],
            )

            for handler in handlers:
                handler(message)

        else:
            for handlers in self._handlers.values():
                for handler in handlers:
                    handler(message)

        return message

    def history(
        self,
        conversation_id: Optional[str] = None,
    ) -> List[AgentMessage]:
        if conversation_id is None:
            return list(self._history)

        return [
            message
            for message in self._history
            if message.conversation_id == conversation_id
        ]

    def clear(self) -> None:
        self._history.clear()