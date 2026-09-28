from __future__ import annotations

from dataclasses import dataclass, field
from threading import RLock
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    Optional,
    Type,
)


class DiagramRegistryError(RuntimeError):
    """Base exception for diagram registry errors."""


class DiagramAlreadyRegisteredError(
    DiagramRegistryError
):
    """Raised when a duplicate registry entry is added."""


class DiagramNotFoundError(
    DiagramRegistryError
):
    """Raised when a requested registry entry does not exist."""


class DiagramRegistrationError(
    DiagramRegistryError
):
    """Raised when an invalid registry entry is registered."""


@dataclass
class DiagramTypeDefinition:
    """
    Metadata describing a diagram type.

    `builder` is optional. A diagram type can exist in the
    registry purely as metadata and be resolved later.
    """

    name: str

    display_name: str

    description: str = ""

    aliases: list[str] = field(
        default_factory=list
    )

    category: str = "general"

    builder: Optional[
        Callable[..., Any]
    ] = None

    planner: Optional[
        Callable[..., Any]
    ] = None

    renderer: Optional[
        Callable[..., Any]
    ] = None

    priority: int = 0

    enabled: bool = True

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def normalized_names(
        self,
    ) -> set[str]:
        names = {
            self.name,
            self.display_name,
            *self.aliases,
        }

        return {
            self._normalize(name)
            for name in names
            if name
        }

    @staticmethod
    def _normalize(
        value: str,
    ) -> str:
        return (
            value.strip()
            .lower()
            .replace(
                " ",
                "_",
            )
            .replace(
                "-",
                "_",
            )
        )


@dataclass
class DiagramRendererDefinition:
    """
    Registered diagram renderer.
    """

    name: str

    renderer: Callable[..., Any]

    formats: list[str] = field(
        default_factory=list
    )

    description: str = ""

    priority: int = 0

    enabled: bool = True

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class DiagramLayoutDefinition:
    """
    Registered diagram layout algorithm.
    """

    name: str

    layout: Callable[..., Any]

    diagram_types: list[str] = field(
        default_factory=list
    )

    description: str = ""

    priority: int = 0

    enabled: bool = True

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


class DiagramRegistry:
    """
    Central registry for the EVU Diagram Engine.

    The registry manages:

    - diagram types
    - renderers
    - layout algorithms

    It is intentionally independent of FastAPI, databases,
    and plugin frameworks.
    """

    def __init__(self) -> None:
        self._types: Dict[
            str,
            DiagramTypeDefinition,
        ] = {}

        self._aliases: Dict[
            str,
            str,
        ] = {}

        self._renderers: Dict[
            str,
            DiagramRendererDefinition,
        ] = {}

        self._layouts: Dict[
            str,
            DiagramLayoutDefinition,
        ] = {}

        self._lock = RLock()

    # =========================================================
    # Diagram types
    # =========================================================

    def register_type(
        self,
        definition: DiagramTypeDefinition,
        *,
        replace: bool = False,
    ) -> DiagramTypeDefinition:
        self._validate_type(
            definition
        )

        name = self._normalize(
            definition.name
        )

        with self._lock:
            if (
                name in self._types
                and not replace
            ):
                raise DiagramAlreadyRegisteredError(
                    f"Diagram type '{name}' "
                    "is already registered."
                )

            if replace:
                self._remove_aliases_for(
                    name
                )

            definition.name = name

            self._types[name] = (
                definition
            )

            for alias in (
                definition.aliases
            ):
                normalized = self._normalize(
                    alias
                )

                existing = self._aliases.get(
                    normalized
                )

                if (
                    existing
                    and existing != name
                    and not replace
                ):
                    raise DiagramAlreadyRegisteredError(
                        f"Alias '{alias}' is already "
                        "registered for '{existing}'."
                    )

                self._aliases[
                    normalized
                ] = name

            return definition

    def register(
        self,
        name: str,
        *,
        display_name: Optional[str] = None,
        description: str = "",
        aliases: Optional[
            Iterable[str]
        ] = None,
        category: str = "general",
        builder: Optional[
            Callable[..., Any]
        ] = None,
        planner: Optional[
            Callable[..., Any]
        ] = None,
        renderer: Optional[
            Callable[..., Any]
        ] = None,
        priority: int = 0,
        enabled: bool = True,
        metadata: Optional[
            Dict[str, Any]
        ] = None,
        replace: bool = False,
    ) -> DiagramTypeDefinition:
        definition = DiagramTypeDefinition(
            name=name,
            display_name=(
                display_name
                or name.replace(
                    "_",
                    " ",
                ).title()
            ),
            description=description,
            aliases=list(
                aliases or []
            ),
            category=category,
            builder=builder,
            planner=planner,
            renderer=renderer,
            priority=priority,
            enabled=enabled,
            metadata=dict(
                metadata or {}
            ),
        )

        return self.register_type(
            definition,
            replace=replace,
        )

    def unregister_type(
        self,
        name: str,
    ) -> bool:
        normalized = self._normalize(
            name
        )

        with self._lock:
            canonical = self._aliases.get(
                normalized,
                normalized,
            )

            if canonical not in self._types:
                return False

            del self._types[
                canonical
            ]

            self._remove_aliases_for(
                canonical
            )

            return True

    def get_type(
        self,
        name: str,
        *,
        enabled_only: bool = True,
    ) -> DiagramTypeDefinition:
        normalized = self._normalize(
            name
        )

        with self._lock:
            canonical = self._aliases.get(
                normalized,
                normalized,
            )

            definition = self._types.get(
                canonical
            )

            if definition is None:
                raise DiagramNotFoundError(
                    f"Diagram type '{name}' "
                    "is not registered."
                )

            if (
                enabled_only
                and not definition.enabled
            ):
                raise DiagramNotFoundError(
                    f"Diagram type '{name}' "
                    "is disabled."
                )

            return definition

    def find_type(
        self,
        name: str,
    ) -> Optional[
        DiagramTypeDefinition
    ]:
        try:
            return self.get_type(
                name,
                enabled_only=False,
            )
        except DiagramNotFoundError:
            return None

    def list_types(
        self,
        *,
        enabled_only: bool = True,
        category: Optional[str] = None,
    ) -> list[
        DiagramTypeDefinition
    ]:
        with self._lock:
            values = list(
                self._types.values()
            )

        if enabled_only:
            values = [
                item
                for item in values
                if item.enabled
            ]

        if category is not None:
            values = [
                item
                for item in values
                if item.category
                == category
            ]

        return sorted(
            values,
            key=lambda item: (
                -item.priority,
                item.name,
            ),
        )

    def enable_type(
        self,
        name: str,
    ) -> None:
        definition = self.get_type(
            name,
            enabled_only=False,
        )

        definition.enabled = True

    def disable_type(
        self,
        name: str,
    ) -> None:
        definition = self.get_type(
            name,
            enabled_only=False,
        )

        definition.enabled = False

    # =========================================================
    # Renderers
    # =========================================================

    def register_renderer(
        self,
        definition: DiagramRendererDefinition,
        *,
        replace: bool = False,
    ) -> DiagramRendererDefinition:
        self._validate_renderer(
            definition
        )

        name = self._normalize(
            definition.name
        )

        with self._lock:
            if (
                name in self._renderers
                and not replace
            ):
                raise DiagramAlreadyRegisteredError(
                    f"Renderer '{name}' "
                    "is already registered."
                )

            definition.name = name

            self._renderers[
                name
            ] = definition

            return definition

    def get_renderer(
        self,
        name: str,
        *,
        enabled_only: bool = True,
    ) -> DiagramRendererDefinition:
        normalized = self._normalize(
            name
        )

        with self._lock:
            definition = self._renderers.get(
                normalized
            )

            if definition is None:
                raise DiagramNotFoundError(
                    f"Renderer '{name}' "
                    "is not registered."
                )

            if (
                enabled_only
                and not definition.enabled
            ):
                raise DiagramNotFoundError(
                    f"Renderer '{name}' "
                    "is disabled."
                )

            return definition

    def list_renderers(
        self,
        *,
        enabled_only: bool = True,
        format_name: Optional[str] = None,
    ) -> list[
        DiagramRendererDefinition
    ]:
        with self._lock:
            values = list(
                self._renderers.values()
            )

        if enabled_only:
            values = [
                item
                for item in values
                if item.enabled
            ]

        if format_name:
            normalized_format = (
                self._normalize(
                    format_name
                )
            )

            values = [
                item
                for item in values
                if any(
                    self._normalize(fmt)
                    == normalized_format
                    for fmt in item.formats
                )
            ]

        return sorted(
            values,
            key=lambda item: (
                -item.priority,
                item.name,
            ),
        )

    def unregister_renderer(
        self,
        name: str,
    ) -> bool:
        normalized = self._normalize(
            name
        )

        with self._lock:
            if (
                normalized
                not in self._renderers
            ):
                return False

            del self._renderers[
                normalized
            ]

            return True

    # =========================================================
    # Layouts
    # =========================================================

    def register_layout(
        self,
        definition: DiagramLayoutDefinition,
        *,
        replace: bool = False,
    ) -> DiagramLayoutDefinition:
        self._validate_layout(
            definition
        )

        name = self._normalize(
            definition.name
        )

        with self._lock:
            if (
                name in self._layouts
                and not replace
            ):
                raise DiagramAlreadyRegisteredError(
                    f"Layout '{name}' "
                    "is already registered."
                )

            definition.name = name

            self._layouts[
                name
            ] = definition

            return definition

    def get_layout(
        self,
        name: str,
        *,
        enabled_only: bool = True,
    ) -> DiagramLayoutDefinition:
        normalized = self._normalize(
            name
        )

        with self._lock:
            definition = self._layouts.get(
                normalized
            )

            if definition is None:
                raise DiagramNotFoundError(
                    f"Layout '{name}' "
                    "is not registered."
                )

            if (
                enabled_only
                and not definition.enabled
            ):
                raise DiagramNotFoundError(
                    f"Layout '{name}' "
                    "is disabled."
                )

            return definition

    def list_layouts(
        self,
        *,
        enabled_only: bool = True,
        diagram_type: Optional[str] = None,
    ) -> list[
        DiagramLayoutDefinition
    ]:
        with self._lock:
            values = list(
                self._layouts.values()
            )

        if enabled_only:
            values = [
                item
                for item in values
                if item.enabled
            ]

        if diagram_type:
            normalized_type = (
                self._normalize(
                    diagram_type
                )
            )

            values = [
                item
                for item in values
                if not item.diagram_types
                or normalized_type
                in {
                    self._normalize(
                        value
                    )
                    for value in item.diagram_types
                }
            ]

        return sorted(
            values,
            key=lambda item: (
                -item.priority,
                item.name,
            ),
        )

    def unregister_layout(
        self,
        name: str,
    ) -> bool:
        normalized = self._normalize(
            name
        )

        with self._lock:
            if (
                normalized
                not in self._layouts
            ):
                return False

            del self._layouts[
                normalized
            ]

            return True

    # =========================================================
    # Bulk operations
    # =========================================================

    def clear(
        self,
        *,
        diagram_types: bool = True,
        renderers: bool = True,
        layouts: bool = True,
    ) -> None:
        with self._lock:
            if diagram_types:
                self._types.clear()
                self._aliases.clear()

            if renderers:
                self._renderers.clear()

            if layouts:
                self._layouts.clear()

    def stats(
        self,
    ) -> Dict[str, int]:
        with self._lock:
            return {
                "diagram_types": len(
                    self._types
                ),
                "aliases": len(
                    self._aliases
                ),
                "renderers": len(
                    self._renderers
                ),
                "layouts": len(
                    self._layouts
                ),
            }

    # =========================================================
    # Validation
    # =========================================================

    def _validate_type(
        self,
        definition: DiagramTypeDefinition,
    ) -> None:
        if not definition.name:
            raise DiagramRegistrationError(
                "Diagram type name cannot be empty."
            )

        if not definition.display_name:
            raise DiagramRegistrationError(
                "Diagram display name cannot be empty."
            )

        if definition.priority < 0:
            raise DiagramRegistrationError(
                "Diagram priority cannot be negative."
            )

    def _validate_renderer(
        self,
        definition: DiagramRendererDefinition,
    ) -> None:
        if not definition.name:
            raise DiagramRegistrationError(
                "Renderer name cannot be empty."
            )

        if not callable(
            definition.renderer
        ):
            raise DiagramRegistrationError(
                "Renderer must be callable."
            )

    def _validate_layout(
        self,
        definition: DiagramLayoutDefinition,
    ) -> None:
        if not definition.name:
            raise DiagramRegistrationError(
                "Layout name cannot be empty."
            )

        if not callable(
            definition.layout
        ):
            raise DiagramRegistrationError(
                "Layout must be callable."
            )

    # =========================================================
    # Internal helpers
    # =========================================================

    def _normalize(
        self,
        value: str,
    ) -> str:
        return (
            value.strip()
            .lower()
            .replace(
                " ",
                "_",
            )
            .replace(
                "-",
                "_",
            )
        )

    def _remove_aliases_for(
        self,
        canonical: str,
    ) -> None:
        aliases = [
            alias
            for alias, target
            in self._aliases.items()
            if target == canonical
        ]

        for alias in aliases:
            del self._aliases[
                alias
            ]


# =============================================================
# Global EVU registry
# =============================================================

diagram_registry = DiagramRegistry()


def register_diagram_type(
    name: str,
    **kwargs: Any,
) -> DiagramTypeDefinition:
    """
    Convenience decorator/function.

    Example:

        @register_diagram_type(
            "flowchart",
            aliases=["flow", "process"],
        )
        class FlowchartBuilder:
            ...
    """

    builder = kwargs.pop(
        "builder",
        None,
    )

    def decorator(
        target: Any,
    ) -> Any:
        actual_builder = (
            builder
            or target
        )

        diagram_registry.register(
            name,
            builder=actual_builder,
            **kwargs,
        )

        return target

    return decorator


def register_renderer(
    name: str,
    renderer: Callable[..., Any],
    *,
    formats: Optional[
        Iterable[str]
    ] = None,
    description: str = "",
    priority: int = 0,
    enabled: bool = True,
    replace: bool = False,
) -> DiagramRendererDefinition:
    definition = DiagramRendererDefinition(
        name=name,
        renderer=renderer,
        formats=list(
            formats or []
        ),
        description=description,
        priority=priority,
        enabled=enabled,
    )

    return diagram_registry.register_renderer(
        definition,
        replace=replace,
    )


def register_layout(
    name: str,
    layout: Callable[..., Any],
    *,
    diagram_types: Optional[
        Iterable[str]
    ] = None,
    description: str = "",
    priority: int = 0,
    enabled: bool = True,
    replace: bool = False,
) -> DiagramLayoutDefinition:
    definition = DiagramLayoutDefinition(
        name=name,
        layout=layout,
        diagram_types=list(
            diagram_types or []
        ),
        description=description,
        priority=priority,
        enabled=enabled,
    )

    return diagram_registry.register_layout(
        definition,
        replace=replace,
    )


def get_diagram_type(
    name: str,
) -> DiagramTypeDefinition:
    return diagram_registry.get_type(
        name
    )


def get_renderer(
    name: str,
) -> DiagramRendererDefinition:
    return diagram_registry.get_renderer(
        name
    )


def get_layout(
    name: str,
) -> DiagramLayoutDefinition:
    return diagram_registry.get_layout(
        name
    )


__all__ = [
    "DiagramRegistry",
    "DiagramTypeDefinition",
    "DiagramRendererDefinition",
    "DiagramLayoutDefinition",
    "DiagramRegistryError",
    "DiagramAlreadyRegisteredError",
    "DiagramNotFoundError",
    "DiagramRegistrationError",
    "diagram_registry",
    "register_diagram_type",
    "register_renderer",
    "register_layout",
    "get_diagram_type",
    "get_renderer",
    "get_layout",
]