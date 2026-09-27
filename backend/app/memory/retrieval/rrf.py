from collections import defaultdict


def reciprocal_rank_fusion(
    ranked_lists: list[list[dict]],
    *,
    k: int = 60,
) -> list[dict]:
    """Combine multiple ranked lists using standard Reciprocal Rank Fusion (RRF)."""
    fused = defaultdict(
        lambda: {
            "score": 0.0,
            "item": None,
        }
    )

    for results in ranked_lists:
        for rank, result in enumerate(results, start=1):
            key = result["id"]
            fused[key]["score"] += 1.0 / (k + rank)
            fused[key]["item"] = result

    output = []
    for value in fused.values():
        item = dict(value["item"])
        item["rrf_score"] = value["score"]
        output.append(item)

    output.sort(
        key=lambda item: item["rrf_score"],
        reverse=True,
    )

    return output


def weighted_rrf(
    streams: dict[str, list[dict]],
    weights: dict[str, float],
    *,
    k: int = 60,
) -> list[dict]:
    """Combine multiple named retrieval streams with stream-specific weights."""
    fused: dict[str, dict] = {}

    for stream_name, results in streams.items():
        weight = weights.get(stream_name, 1.0)

        for rank, result in enumerate(results, start=1):
            item_id = result["id"]

            if item_id not in fused:
                fused[item_id] = {
                    "item": result,
                    "score": 0.0,
                }

            fused[item_id]["score"] += weight / (k + rank)

    output = []
    for value in fused.values():
        item = dict(value["item"])
        item["rrf_score"] = value["score"]
        output.append(item)

    return sorted(
        output,
        key=lambda item: item["rrf_score"],
        reverse=True,
    )