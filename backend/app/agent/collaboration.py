from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid

from .communication import AgentMessage, MessageBus


@dataclass
class CollaborationSession:
    goal: str

    session_id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )

    agent_ids: List[str] = field(
        default_factory=list
    )

    messages: List[AgentMessage] = field(
        default_factory=list
    )

    shared_state: Dict[str, Any] = field(
        default_factory=dict
    )

    status: str = "active"

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def add_agent(
        self,
        agent_id: str,
    ) -> None:
        if agent_id not in self.agent_ids:
            self.agent_ids.append(agent_id)

    def update_state(
        self,
        key: str,
        value: Any,
    ) -> None:
        self.shared_state[key] = value

    def close(self) -> None:
        self.status = "completed"


class CollaborationManager:
    def __init__(
        self,
        message_bus: Optional[MessageBus] = None,
    ) -> None:
        self.message_bus = message_bus or MessageBus()

        self._sessions: Dict[
            str,
            CollaborationSession,
        ] = {}

    def create(
        self,
        goal: str,
        agent_ids: Optional[List[str]] = None,
    ) -> CollaborationSession:
        session = CollaborationSession(
            goal=goal,
            agent_ids=list(agent_ids or []),
        )

        self._sessions[session.session_id] = session

        return session

    def get(
        self,
        session_id: str,
    ) -> Optional[CollaborationSession]:
        return self._sessions.get(session_id)

    def add_agent(
        self,
        session_id: str,
        agent_id: str,
    ) -> CollaborationSession:
        session = self._require(session_id)

        session.add_agent(agent_id)

        return session

    def send(
        self,
        session_id: str,
        sender_id: str,
        content: Any,
        recipient_id: Optional[str] = None,
        message_type: str = "collaboration",
    ) -> AgentMessage:
        session = self._require(session_id)

        message = AgentMessage(
            sender_id=sender_id,
            recipient_id=recipient_id,
            content=content,
            message_type=message_type,
            conversation_id=session.session_id,
        )

        session.messages.append(message)

        self.message_bus.publish(message)

        return message

    def update_state(
        self,
        session_id: str,
        key: str,
        value: Any,
    ) -> None:
        session = self._require(session_id)
        session.update_state(key, value)

    def close(
        self,
        session_id: str,
    ) -> None:
        session = self._require(session_id)
        session.close()

    def _require(
        self,
        session_id: str,
    ) -> CollaborationSession:
        session = self.get(session_id)

        if session is None:
            raise KeyError(
                f"Collaboration session not found: {session_id}"
            )

        return session