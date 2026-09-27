import heapq


def memory_score(
    *,
    semantic: float = 0.0,
    lexical: float = 0.0,
    graph: float = 0.0,
    confidence: float = 0.0,
    importance: float = 0.0,
    recency: float = 0.0,
    project_relevance: float = 0.0,
    weights: dict[str, float] | None = None,
) -> float:
    w = weights or {
        "semantic": 0.25,
        "lexical": 0.20,
        "graph": 0.15,
        "confidence": 0.15,
        "importance": 0.10,
        "recency": 0.10,
        "project_relevance": 0.05,
    }

    return (
        w.get("semantic", 0.0) * semantic
        + w.get("lexical", 0.0) * lexical
        + w.get("graph", 0.0) * graph
        + w.get("confidence", 0.0) * confidence
        + w.get("importance", 0.0) * importance
        + w.get("recency", 0.0) * recency
        + w.get("project_relevance", 0.0) * project_relevance
    )


class HierarchicalRetriever:

    def __init__(self, repository):
        self.repository = repository

    async def retrieve(
        self,
        roots,
        query_embedding,
        limit=8,
        alpha=0.7,
        custom_weights: dict[str, float] | None = None,
    ):
        queue = []

        for root in roots:
            heapq.heappush(
                queue,
                (
                    -1.0,
                    root,
                ),
            )

        visited = set()
        results = []

        while queue and len(results) < limit:

            negative_score, uri = heapq.heappop(queue)

            parent_score = -negative_score

            if uri in visited:
                continue

            visited.add(uri)

            children = await self.repository.search_children(
                uri=uri,
                query_embedding=query_embedding,
            )

            for child in children:

                embedding_score = getattr(child, "embedding_score", 0.0)

                # Combine semantic embedding with metadata signals via memory_score
                semantic_rank = memory_score(
                    semantic=embedding_score,
                    lexical=getattr(child, "lexical_score", 0.0),
                    graph=getattr(child, "graph_score", 0.0),
                    confidence=getattr(child, "confidence", 1.0),
                    importance=getattr(child, "importance", 1.0),
                    recency=getattr(child, "recency_score", 1.0),
                    project_relevance=getattr(child, "project_relevance", 1.0),
                    weights=custom_weights,
                )

                final_score = (
                    alpha * semantic_rank
                    + (1 - alpha) * parent_score
                )

                if child.is_leaf:
                    results.append(
                        (
                            final_score,
                            child,
                        )
                    )
                else:
                    heapq.heappush(
                        queue,
                        (
                            -final_score,
                            child.uri,
                        ),
                    )

        results.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        return results[:limit]