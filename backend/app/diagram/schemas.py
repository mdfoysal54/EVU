from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class DiagramGenerateRequest(BaseModel):
    prompt: str = Field(min_length=1)
    diagram_type: str | None = None
    title: str | None = None
    options: dict[str, Any] = Field(default_factory=dict)


class DiagramNodeSchema(BaseModel):
    id: str
    label: str
    node_type: str
    description: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    group_id: str | None = None


class DiagramEdgeSchema(BaseModel):
    source: str
    target: str
    label: str | None = None
    edge_type: str
    style: str
    directed: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)


class DiagramGroupSchema(BaseModel):
    id: str
    label: str
    group_type: str
    parent_id: str | None = None
    node_ids: list[str] = Field(default_factory=list)


class DiagramResponse(BaseModel):
    id: str
    diagram_type: str
    title: str | None
    direction: str
    nodes: list[DiagramNodeSchema]
    edges: list[DiagramEdgeSchema]
    groups: list[DiagramGroupSchema]
    mermaid: str
    warnings: list[str] = Field(default_factory=list)


class DiagramTypeResponse(BaseModel):
    name: str
    description: str
    keywords: list[str]


class DiagramTypesResponse(BaseModel):
    types: list[DiagramTypeResponse]
# Backward-compatible names used by older EVU imports.
DiagramRequest = DiagramGenerateRequest
DiagramSchema = DiagramResponse
