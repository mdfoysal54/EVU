def complexity_budget(node_count: int, edge_count: int) -> dict:
    if node_count <= 7:
        level = "simple"
    elif node_count <= 12:
        level = "balanced"
    elif node_count <= 24:
        level = "detailed"
    else:
        level = "split"

    return {
        "level": level,
        "nodes": node_count,
        "edges": edge_count,
        "recommended_action": "split_into_zones" if level == "split" else "single_canvas"
    }