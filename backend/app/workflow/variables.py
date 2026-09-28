from __future__ import annotations

import re
from typing import Any, Dict, Mapping


_TEMPLATE = re.compile(
    r"\{\{\s*([^{}]+?)\s*\}\}"
)


class VariableStore:
    """
    Workflow variable storage.

    Supports:

        store.set("user.name", "Foysal")

        store.get("user.name")

        store.render("Hello {{ user.name }}")
    """

    def __init__(
        self,
        initial: Mapping[str, Any] | None = None,
    ) -> None:

        self._values: Dict[str, Any] = dict(
            initial or {}
        )

    def set(
        self,
        key: str,
        value: Any,
    ) -> None:

        parts = key.split(".")

        current = self._values

        for part in parts[:-1]:
            if part not in current:
                current[part] = {}

            if not isinstance(current[part], dict):
                current[part] = {}

            current = current[part]

        current[parts[-1]] = value

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:

        current: Any = self._values

        for part in key.split("."):
            if not isinstance(current, dict):
                return default

            if part not in current:
                return default

            current = current[part]

        return current

    def delete(self, key: str) -> None:
        parts = key.split(".")

        current = self._values

        for part in parts[:-1]:
            current = current.get(part, {})

            if not isinstance(current, dict):
                return

        current.pop(parts[-1], None)

    def all(self) -> Dict[str, Any]:
        return dict(self._values)

    def render(self, value: Any) -> Any:
        if not isinstance(value, str):
            return value

        def replace(match: re.Match[str]) -> str:
            key = match.group(1).strip()
            resolved = self.get(key)

            if resolved is None:
                return ""

            return str(resolved)

        return _TEMPLATE.sub(
            replace,
            value,
        )

    def resolve(self, value: Any) -> Any:
        if isinstance(value, str):
            matches = list(
                _TEMPLATE.finditer(value)
            )

            if (
                len(matches) == 1
                and matches[0].span() == (0, len(value))
            ):
                return self.get(
                    matches[0].group(1).strip()
                )

            return self.render(value)

        if isinstance(value, list):
            return [
                self.resolve(item)
                for item in value
            ]

        if isinstance(value, dict):
            return {
                key: self.resolve(item)
                for key, item in value.items()
            }

        return value