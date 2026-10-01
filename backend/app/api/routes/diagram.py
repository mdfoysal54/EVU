from fastapi import APIRouter
from app.diagram import diagram_service
from app.diagram.models import DiagramRequestModel
from app.diagram.schemas import DiagramGenerateRequest, DiagramResponse

router = APIRouter(prefix="/api/v1/diagram", tags=["Diagram"])


@router.post("/generate", response_model=DiagramResponse)
def generate_diagram(request: DiagramGenerateRequest) -> DiagramResponse:
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
            {"id": n.id, "label": n.label, "node_type": n.node_type,
             "description": n.description, "metadata": n.metadata, "group_id": n.group_id}
            for n in diagram.nodes
        ],
        edges=[
            {"source": e.source, "target": e.target, "label": e.label,
             "edge_type": e.edge_type.value, "style": e.style.value,
             "directed": e.directed, "metadata": e.metadata}
            for e in diagram.edges
        ],
        groups=[
            {"id": g.id, "label": g.label, "group_type": g.group_type,
             "parent_id": g.parent_id, "node_ids": g.node_ids}
            for g in diagram.groups
        ],
        mermaid=result.mermaid,
        warnings=result.warnings,
    )
