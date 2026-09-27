import json
from app.context.service import context_service


def should_remember(
    *,
    importance: float,
    novelty: float,
    durability: float,
    threshold: float = 0.55,
) -> bool:
    """Intake write-gate to prevent transient noise from entering long-term memory."""
    score = (
        0.4 * importance
        + 0.3 * novelty
        + 0.3 * durability
    )

    return score >= threshold


def should_remember_event(event: dict) -> bool:
    """Filter out noisy or empty tool event executions."""
    # Don't remember failed executions or 0-result tool runs
    if event.get("result_count", 1) <= 0:
        return False

    # Skip excluded utilities
    ignored_tools = {"clock", "ping"}
    if event.get("tool") in ignored_tools:
        return False

    # Check write-gate signals if provided in the event payload
    importance = float(event.get("importance", 1.0))
    novelty = float(event.get("novelty", 1.0))
    durability = float(event.get("durability", 1.0))

    return should_remember(
        importance=importance,
        novelty=novelty,
        durability=durability,
    )


def build_observation(event: dict) -> str:
    """Format the payload into searchable, structured text."""
    tool = event.get("tool", "unknown_tool")
    query = event.get("query", "")
    count = event.get("result_count", 0)
    details = event.get("data") or ""

    lines = [
        f"Tool Used: {tool}",
        f"Query/Action: {query}",
        f"Results Returned: {count}",
    ]
    if details:
        lines.append(f"Result Snippet: {details[:1000]}")

    return "\n".join(lines)


async def on_tool_completed(event: dict, user_id: int | None = None):
    """Event subscriber callback."""
    if not should_remember_event(event):
        return

    await context_service.capture_observation(
        content=build_observation(event),
        source="tool_result",
        user_id=user_id,
        tool_name=event.get("tool"),
        metadata=event,
    )