from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class DiagramSemanticPattern(str, Enum):
    ARCHITECTURE = "architecture"
    DATA_FLOW = "data_flow"
    PROCESS = "process"
    SEQUENCE = "sequence"
    DECISION = "decision"
    HIERARCHY = "hierarchy"
    RELATIONSHIP = "relationship"
    TIMELINE = "timeline"
    SECURITY = "security"
    DEPENDENCY = "dependency"
    COMPARISON = "comparison"


class DiagramFormat(str, Enum):
    HTML = "html"
    SVG = "svg"
    PNG = "png"
    HTML_PNG = "html+png"


class DiagramSize(str, Enum):
    DOC_INLINE = "doc-inline"
    DOC_WIDE = "doc-wide"
    SLIDE_16X9 = "slide-16x9"
    SLIDE_4X3 = "slide-4x3"
    SOCIAL_OG = "social-og"
    SOCIAL_SQUARE = "social-square"
    PRINT_A4 = "print-a4"
    PRINT_LETTER = "print-letter"
    FIT = "fit"


class DiagramDetail(str, Enum):
    FAITHFUL = "faithful"
    BALANCED = "balanced"
    SIMPLIFIED = "simplified"


class DiagramAudience(str, Enum):
    ENGINEER = "engineer"
    MIXED = "mixed"
    EXECUTIVE = "executive"


@dataclass
class DiagramOutputSpec:
    format: DiagramFormat = DiagramFormat.SVG
    size: DiagramSize = DiagramSize.FIT
    detail: DiagramDetail = DiagramDetail.BALANCED
    audience: DiagramAudience = DiagramAudience.MIXED
    theme: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    metadata: dict = field(default_factory=dict)


@dataclass
class DiagramNode:
    id: str
    label: str
    kind: str = "component"
    group: Optional[str] = None
    metadata: dict = field(default_factory=dict)


@dataclass
class DiagramEdge:
    source: str
    target: str
    label: Optional[str] = None
    kind: str = "directed"
    metadata: dict = field(default_factory=dict)


@dataclass
class DiagramIR:
    title: str
    diagram_type: str
    nodes: list[DiagramNode]
    edges: list[DiagramEdge]
    groups: list[dict] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)