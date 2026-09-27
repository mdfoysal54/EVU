from app.security.audit import (
    security_audit_logger,
)
from app.security.policy import (
    security_policy,
)
from app.security.schemas import (
    Permission,
    PermissionCheckResponse,
    Role,
)


class SecurityService:

    def resolve_role(
        self,
        user,
    ) -> Role:

        # Current EVU users are normal users unless
        # the application later adds explicit role storage.
        #
        # This keeps the security layer compatible with
        # the existing authentication system.

        raw_role = getattr(
            user,
            "role",
            None,
        )

        if raw_role:

            try:
                return Role(str(raw_role))

            except ValueError:
                pass

        return Role.USER

    def check_permission(
        self,
        user,
        permission: Permission,
    ) -> PermissionCheckResponse:

        role = self.resolve_role(user)

        allowed = security_policy.check_permission(
            role,
            permission,
        )

        reason = (
            "Permission granted."
            if allowed
            else (
                f"Role '{role.value}' does not "
                f"have this permission."
            )
        )

        security_audit_logger.record(
            event_type="permission_check",
            user_id=getattr(user, "id", None),
            username=getattr(user, "username", None),
            permission=permission.value,
            allowed=allowed,
        )

        return PermissionCheckResponse(
            allowed=allowed,
            role=role,
            permission=permission,
            reason=reason,
        )

    def check_tool(
        self,
        user,
        tool_name: str,
    ) -> tuple[bool, str]:

        role = self.resolve_role(user)

        allowed, reason = security_policy.check_tool(
            role,
            tool_name,
        )

        security_audit_logger.record(
            event_type="tool_authorization",
            user_id=getattr(user, "id", None),
            username=getattr(user, "username", None),
            tool=tool_name,
            allowed=allowed,
            details={
                "reason": reason,
                "role": role.value,
            },
        )

        return allowed, reason


security_service = SecurityService()