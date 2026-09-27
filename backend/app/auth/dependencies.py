from typing import Any
from fastapi import Header, HTTPException, status


async def get_current_user(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    """Temporary dependency stub until full authentication is configured."""
    return {"user_id": "test-user", "username": "developer"}