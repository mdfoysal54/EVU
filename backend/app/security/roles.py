from app.security.schemas import Permission, Role


ROLE_PERMISSIONS: dict[Role, set[Permission]] = {

    Role.USER: {
        Permission.CHAT,
        Permission.USE_CALCULATOR,
        Permission.USE_DOCUMENTS,
        Permission.USE_WEB,
        Permission.USE_EXTERNAL_MODELS,
        Permission.RUN_AGENT,
    },

    Role.POWER_USER: {
        Permission.CHAT,
        Permission.USE_CALCULATOR,
        Permission.USE_DOCUMENTS,
        Permission.USE_WEB,
        Permission.USE_BROWSER,
        Permission.USE_LOCAL_MODELS,
        Permission.USE_EXTERNAL_MODELS,
        Permission.RUN_AGENT,
        Permission.RUN_BACKGROUND_TASK,
    },

    Role.ADMIN: {
        permission
        for permission in Permission
    },
}


def permissions_for_role(
    role: Role,
) -> set[Permission]:

    return ROLE_PERMISSIONS.get(
        role,
        set(),
    )