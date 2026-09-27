from app.security.schemas import Permission


TOOL_PERMISSIONS: dict[str, Permission] = {

    "calculator": Permission.USE_CALCULATOR,

    "current_time": Permission.CHAT,

    "document_search": Permission.USE_DOCUMENTS,

    "web_research": Permission.USE_WEB,

    "browser": Permission.USE_BROWSER,

    "local_model": Permission.USE_LOCAL_MODELS,

    "external_model": Permission.USE_EXTERNAL_MODELS,
}


def required_permission(
    tool_name: str,
) -> Permission | None:

    return TOOL_PERMISSIONS.get(
        tool_name
    )