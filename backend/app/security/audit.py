from datetime import datetime, timezone
from typing import Any

from app.security.schemas import SecurityAuditEvent


class SecurityAuditLogger:

    def __init__(self) -> None:

        self._events: list[
            SecurityAuditEvent
        ] = []

    def record(
        self,
        event_type: str,
        allowed: bool,
        user_id: int | None = None,
        username: str | None = None,
        permission: str | None = None,
        tool: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> SecurityAuditEvent:

        event = SecurityAuditEvent(
            event_type=event_type,
            user_id=user_id,
            username=username,
            permission=permission,
            tool=tool,
            allowed=allowed,
            details={
                **(details or {}),
                "timestamp": datetime.now(
                    timezone.utc
                ).isoformat(),
            },
        )

        self._events.append(event)

        # Prevent unlimited in-memory growth.
        if len(self._events) > 1000:
            self._events = self._events[-1000:]

        return event

    def list_events(
        self,
    ) -> list[SecurityAuditEvent]:

        return list(self._events)


security_audit_logger = SecurityAuditLogger()