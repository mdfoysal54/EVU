from app.diagram.models import DiagramIR
from app.diagram.budget import complexity_budget

class ValidationError(Exception):
    pass

class DiagramValidator:
    def validate(self, diagram: DiagramIR) -> bool:
        self.validate_nodes(diagram)
        self.validate_edges(diagram)
        self.validate_complexity(diagram)
        return True

    def validate_nodes(self, diagram: DiagramIR):
        node_ids = set()
        for node in diagram.nodes:
            if not node.id or not node.id.strip():
                raise ValidationError("Node encountered with missing or empty ID.")
            if node.id in node_ids:
                raise ValidationError(f"Duplicate node ID detected: {node.id}")
            node_ids.add(node.id)

    def validate_edges(self, diagram: DiagramIR):
        valid_ids = {node.id for node in diagram.nodes}
        for edge in diagram.edges:
            if edge.source not in valid_ids:
                raise ValidationError(f"Dangling edge: Source ID '{edge.source}' does not exist.")
            if edge.target not in valid_ids:
                raise ValidationError(f"Dangling edge: Target ID '{edge.target}' does not exist.")

    def validate_complexity(self, diagram: DiagramIR):
        budget = complexity_budget(len(diagram.nodes), len(diagram.edges))
        if budget["level"] == "split":
            raise ValidationError(
                f"Complexity limit exceeded ({budget['nodes']} nodes). Diagram must be partitioned into modular zones."
            )