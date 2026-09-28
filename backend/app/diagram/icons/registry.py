from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Icon:
    name: str
    value: str
    category: str = "general"


class IconRegistry:
    def __init__(self) -> None:
        self._icons: dict[str, Icon] = {}

    def register(
        self,
        name: str,
        value: str,
        category: str = "general",
    ) -> Icon:

        icon = Icon(
            name=name,
            value=value,
            category=category,
        )

        self._icons[name] = icon

        return icon

    def get(self, name: str) -> Icon | None:
        return self._icons.get(name)

    def all(self) -> list[Icon]:
        return list(self._icons.values())

    def by_category(
        self,
        category: str,
    ) -> list[Icon]:

        return [
            icon
            for icon in self._icons.values()
            if icon.category == category
        ]


DEFAULT_ICONS = IconRegistry()

DEFAULT_ICONS.register(
    "user",
    "user",
    "people",
)

DEFAULT_ICONS.register(
    "server",
    "server",
    "infrastructure",
)

DEFAULT_ICONS.register(
    "database",
    "database",
    "data",
)

DEFAULT_ICONS.register(
    "cloud",
    "cloud",
    "infrastructure",
)

DEFAULT_ICONS.register(
    "api",
    "api",
    "software",
)

DEFAULT_ICONS.register(
    "agent",
    "bot",
    "ai",
)

DEFAULT_ICONS.register(
    "queue",
    "queue",
    "infrastructure",
)

DEFAULT_ICONS.register(
    "storage",
    "hard-drive",
    "data",
)


def get_icon(name: str) -> Icon | None:
    return DEFAULT_ICONS.get(name)