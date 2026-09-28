from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SemanticPattern:
    name: str
    diagram_type: str
    keywords: tuple[str, ...]
    priority: int = 0
    description: str = ""


PATTERNS: tuple[SemanticPattern, ...] = (
    SemanticPattern(
        "architecture",
        "architecture",
        (
            "architecture",
            "system architecture",
            "software architecture",
            "microservice",
            "microservices",
            "backend",
            "frontend",
        ),
        10,
        "System and software architecture relationships.",
    ),
    SemanticPattern(
        "flow",
        "flowchart",
        (
            "flowchart",
            "flow chart",
            "process",
            "workflow",
            "steps",
            "process flow",
        ),
        9,
        "Sequential process or decision flow.",
    ),
    SemanticPattern(
        "sequence",
        "sequence",
        (
            "sequence diagram",
            "request",
            "response",
            "interaction",
            "message",
            "communicate",
        ),
        8,
        "Interactions between actors or services over time.",
    ),
    SemanticPattern(
        "state",
        "state",
        (
            "state diagram",
            "state machine",
            "status",
            "transition",
            "states",
        ),
        8,
        "State transitions.",
    ),
    SemanticPattern(
        "database",
        "er",
        (
            "entity relationship",
            "erd",
            "database schema",
            "tables",
            "entities",
            "relationships",
        ),
        10,
        "Database entities and relationships.",
    ),
    SemanticPattern(
        "timeline",
        "timeline",
        (
            "timeline",
            "chronology",
            "history",
            "events over time",
        ),
        8,
        "Events ordered by time.",
    ),
    SemanticPattern(
        "swimlane",
        "swimlane",
        (
            "swimlane",
            "departments",
            "roles",
            "responsibility",
            "who does what",
        ),
        8,
        "Process responsibilities separated by actor.",
    ),
    SemanticPattern(
        "quadrant",
        "quadrant",
        (
            "quadrant",
            "2x2",
            "matrix",
            "four quadrants",
        ),
        8,
        "Two-dimensional four-quadrant classification.",
    ),
    SemanticPattern(
        "tree",
        "tree",
        (
            "tree",
            "parent child",
            "decision tree",
            "branching tree",
        ),
        7,
        "Tree-shaped hierarchy.",
    ),
    SemanticPattern(
        "hierarchy",
        "hierarchy",
        (
            "hierarchy",
            "organizational chart",
            "org chart",
            "organization",
        ),
        7,
        "Hierarchical organization.",
    ),
    SemanticPattern(
        "layers",
        "layers",
        (
            "layers",
            "layered architecture",
            "presentation layer",
            "business layer",
            "data layer",
        ),
        8,
        "Layered system organization.",
    ),
    SemanticPattern(
        "data_flow",
        "data_flow",
        (
            "data flow",
            "data pipeline",
            "data movement",
            "etl",
            "pipeline",
        ),
        9,
        "Movement of data through components.",
    ),
    SemanticPattern(
        "deployment",
        "deployment",
        (
            "deployment",
            "infrastructure",
            "cloud",
            "kubernetes",
            "docker",
            "production",
        ),
        9,
        "Runtime infrastructure and deployment.",
    ),
    SemanticPattern(
        "dependency",
        "dependency",
        (
            "dependency",
            "dependencies",
            "depends on",
            "package graph",
            "module graph",
        ),
        8,
        "Dependency relationships.",
    ),
)