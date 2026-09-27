from dataclasses import dataclass

from app.security.permissions import required_permission
from app.security.roles import permissions_for_role
from app.security.schemas import (
    Permission,
    Role,
)


@dataclass
class SecurityPolicy:

    enabled: bool = True

    deny_unknown_tools: bool = True

    allow_admin_all: bool = True

    def check_permission(
        self,
        role: Role,
        permission: Permission,
    ) -> bool:

        if not self.enabled:
            return True

        if (
            role == Role.ADMIN
            and self.allow_admin_all
        ):
            return True

        return permission in permissions_for_role(
            role
        )

    def check_tool(
        self,
        role: Role,
        tool_name: str,
    ) -> tuple[bool, str]:

        permission = required_permission(
            tool_name
        )

        if permission is None:

            if self.deny_unknown_tools:
                return (
                    False,
                    "Tool has no registered permission policy.",
                )

            return True, "Unknown tool allowed by policy."

        allowed = self.check_permission(
            role,
            permission,
        )

        if allowed:
            return (
                True,
                "Permission granted.",
            )

        return (
            False,
            (
                f"Role '{role.value}' does not have "
                f"permission '{permission.value}'."
            ),
        )


security_policy = SecurityPolicy()