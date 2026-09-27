from dataclasses import dataclass
from enum import Enum


class ContextType(str, Enum):
    MEMORY = "memory"
    RESOURCE = "resource"
    SKILL = "skill"


@dataclass
class TypedQuery:
    query: str
    context_type: ContextType
    intent: str
    priority: int = 1


class ContextQueryPlanner:
    def plan(self, query: str) -> list[TypedQuery]:
        query_lower = query.lower()
        queries: list[TypedQuery] = []

        memory_terms = [
            "my preference",
            "my preferences",
            "my style",
            "i prefer",
            "i like",
            "my previous",
            "remember",
            "what i told you",
        ]

        skill_terms = [
            "create",
            "build",
            "generate",
            "write",
            "analyze",
            "calculate",
            "search",
            "research",
            "debug",
        ]

        resource_terms = [
            "documentation",
            "docs",
            "project",
            "code",
            "architecture",
            "database",
            "api",
            "file",
        ]

        if any(term in query_lower for term in memory_terms):
            queries.append(
                TypedQuery(
                    query=query,
                    context_type=ContextType.MEMORY,
                    intent="retrieve_user_memory",
                    priority=5,
                )
            )

        if any(term in query_lower for term in resource_terms):
            queries.append(
                TypedQuery(
                    query=query,
                    context_type=ContextType.RESOURCE,
                    intent="retrieve_reference_resource",
                    priority=4,
                )
            )

        if any(term in query_lower for term in skill_terms):
            queries.append(
                TypedQuery(
                    query=query,
                    context_type=ContextType.SKILL,
                    intent="retrieve_capability",
                    priority=3,
                )
            )

        if not queries:
            queries.append(
                TypedQuery(
                    query=query,
                    context_type=ContextType.RESOURCE,
                    intent="general_context",
                    priority=1,
                )
            )

        return sorted(
            queries,
            key=lambda item: item.priority,
            reverse=True,
        )