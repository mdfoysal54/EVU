"""Compatibility exports for authentication dependencies.

The project historically had two authentication dependency modules. The real
DB-backed implementation lives in app.api.dependencies; this module re-exports
it so model/local-model routes cannot silently bypass authentication.
"""

from app.api.dependencies import get_current_user

__all__ = ["get_current_user"]
