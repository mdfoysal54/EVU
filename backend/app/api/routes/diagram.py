from fastapi import APIRouter

from app.diagram import diagram_service
from app.diagram.models import DiagramRequestModel
from app.diagram.schemas import (
    DiagramGenerateRequest,
    DiagramResponse,
)

router = APIRouter(
    prefix="/diagram",
    tags=["Diagram"],
)


@router.post("/generate", response_model=DiagramResponse)
def generate_diagram(
    request: DiagramGenerateRequest,
) -> DiagramResponse:
    result = diagram_service.generate(
        DiagramRequestModel(
            prompt=request.prompt,
            diagram_type=request.diagram_type,
            title=request.title,
            options=request.options,
        )
    )

    diagram = result.diagram

    return DiagramResponse(
        id=diagram.id,
        diagram_type=diagram.diagram_type,
        title=diagram.title,
        direction=diagram.direction,
        nodes=[
            {
                "id": node.id,
                "label": node.label,
                "node_type": node.node_type,
                "description": node.description,
                "metadata": node.metadata,
                "group_id": node.group_id,
            }
            for node in diagram.nodes
        ],
        edges=[
            {
                "source": edge.source,
                "target": edge.target,
                "label": edge.label,
                "edge_type": edge.edge_type.value,
                "style": edge.style.value,
                "directed": edge.directed,
                "metadata": edge.metadata,
            }
            for edge in diagram.edges
        ],
        groups=[
            {
                "id": group.id,
                "label": group.label,
                "group_type": group.group_type,
                "parent_id": group.parent_id,
                "node_ids": group.node_ids,
            }
            for group in diagram.groups
        ],
        mermaid=result.mermaid,
        warnings=result.warnings,
    )