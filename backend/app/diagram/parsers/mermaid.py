import re
from app.diagram.models import DiagramIR, DiagramNode, DiagramEdge
from app.diagram.parsers.security import sanitize_label

class SafeMermaidParser:
    """Parses basic Mermaid flowchart syntax deterministically without executing JS."""
    
    @staticmethod
    def parse(content: str) -> DiagramIR:
        nodes = {}
        edges = []
        lines = content.strip().splitlines()

        edge_pattern = re.compile(r"(\w+)\s*(?:-->|--\s*([^-]+)\s*-->)\s*(\w+)")
        node_label_pattern = re.compile(r"(\w+)\[([^\]]+)\]")

        for line in lines:
            line = line.strip()
            if not line or line.startswith(("graph", "flowchart")):
                continue

            # Check node definitions
            for match in node_label_pattern.finditer(line):
                node_id, label = match.groups()
                nodes[node_id] = DiagramNode(id=node_id, label=sanitize_label(label))

            # Check edges
            edge_match = edge_pattern.search(line)
            if edge_match:
                src, edge_lbl, tgt = edge_match.groups()
                if src not in nodes:
                    nodes[src] = DiagramNode(id=src, label=src)
                if tgt not in nodes:
                    nodes[tgt] = DiagramNode(id=tgt, label=tgt)
                
                label_val = sanitize_label(edge_lbl) if edge_lbl else None
                edges.append(DiagramEdge(source=src, target=tgt, label=label_val))

        return DiagramIR(
            title="Imported Mermaid Diagram",
            diagram_type="flowchart",
            nodes=list(nodes.values()),
            edges=edges
        )