from datetime import datetime, timedelta, timezone
import json
import math
import re
import uuid

from sqlalchemy import select

from app.context.models import ContextNode
from app.context.processing import (
    content_hash,
    create_abstract,
    create_overview,
)
from app.database.database import get_db_session
from app.services.rag_service import rag_service


def normalize_weights(
    available: set[str],
    configured: dict[str, float],
) -> dict[str, float]:
    active = {
        key: value
        for key, value in configured.items()
        if key in available and value > 0
    }

    total = sum(active.values())

    if total <= 0:
        return {}

    return {
        key: value / total
        for key, value in active.items()
    }


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


class ContextService:

    def _lexical_score(
        self,
        query: str,
        text: str,
    ) -> float:
        query_tokens = set(
            re.findall(
                r"\w+",
                query.lower(),
            )
        )

        text_tokens = set(
            re.findall(
                r"\w+",
                text.lower(),
            )
        )

        if not query_tokens:
            return 0.0

        overlap = query_tokens & text_tokens

        return len(overlap) / len(query_tokens)

    def _cosine_similarity(
        self,
        a: list[float],
        b: list[float],
    ) -> float:
        if not a or not b:
            return 0.0

        size = min(len(a), len(b))

        a = a[:size]
        b = b[:size]

        dot = sum(
            x * y
            for x, y in zip(a, b)
        )

        norm_a = math.sqrt(
            sum(x * x for x in a)
        )

        norm_b = math.sqrt(
            sum(y * y for y in b)
        )

        if norm_a == 0 or norm_b == 0:
            return 0.0

        cosine = dot / (norm_a * norm_b)

        return max(
            0.0,
            min(1.0, (cosine + 1.0) / 2.0),
        )

    async def upsert(
        self,
        *,
        user_id: int | None,
        uri: str,
        context_type: str,
        name: str,
        content: str,
        parent_uri: str | None = None,
        abstract: str | None = None,
        overview: str | None = None,
        metadata: dict | None = None,
        source: str | None = None,
        dedup_window_minutes: int = 10,
    ) -> ContextNode:
        current_hash = content_hash(content)
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(minutes=dedup_window_minutes)

        async with get_db_session() as db:
            result = await db.execute(
                select(ContextNode).where(
                    ContextNode.user_id == user_id,
                    ContextNode.uri == uri,
                )
            )

            node = result.scalar_one_or_none()

            # Deduplication: same content + same scope + recent write window
            if node is not None and getattr(node, "updated_at", None):
                node_time = (
                    node.updated_at.replace(tzinfo=timezone.utc)
                    if node.updated_at.tzinfo is None
                    else node.updated_at
                )
                existing_meta = json.loads(node.metadata_json or "{}")
                if (
                    existing_meta.get("content_hash") == current_hash
                    and node_time >= cutoff
                ):
                    return node

            abstract = abstract or create_abstract(
                content
            )

            overview = overview or create_overview(
                content
            )

            embedding = None

            try:
                embedding_result = await rag_service.embed_many(
                    [abstract]
                )

                if embedding_result:
                    embedding = embedding_result[0]

            except Exception:
                embedding = None

            if node is None:
                node = ContextNode(
                    user_id=user_id,
                    uri=uri,
                )
                db.add(node)

            payload_meta = metadata or {}
            payload_meta["content_hash"] = current_hash

            node.parent_uri = parent_uri
            node.context_type = context_type
            node.name = name
            node.level = 2
            node.is_leaf = True

            node.abstract = abstract
            node.overview = overview
            node.content = content

            node.metadata_json = json.dumps(
                payload_meta,
                ensure_ascii=False,
            )

            node.embedding_json = (
                json.dumps(embedding)
                if embedding
                else None
            )

            node.source = source
            node.is_active = True

            await db.commit()
            await db.refresh(node)

            return node

    async def capture_observation(
        self,
        *,
        content: str,
        source: str = "tool_result",
        user_id: int | None = None,
        tool_name: str | None = None,
        metadata: dict | None = None,
    ) -> ContextNode:
        generated_uri = f"memory://observations/{tool_name or 'tool'}/{uuid.uuid4().hex[:8]}"
        meta = metadata or {}
        meta.update({"source": source, "tool_name": tool_name})

        return await self.upsert(
            user_id=user_id,
            uri=generated_uri,
            context_type="observation",
            name=f"Observation: {tool_name or 'generic'}",
            content=content,
            metadata=meta,
            source=source,
        )

    async def search(
        self,
        *,
        query: str,
        user_id: int | None = None,
        context_type: str | None = None,
        target_uri: str | None = None,
        limit: int = 8,
        max_chars: int = 12000,
    ) -> list[dict]:

        async with get_db_session() as db:

            stmt = select(ContextNode).where(
                ContextNode.is_active.is_(True)
            )

            if user_id is not None:
                stmt = stmt.where(
                    (
                        ContextNode.user_id == user_id
                    )
                    | (
                        ContextNode.user_id.is_(None)
                    )
                )

            if context_type:
                stmt = stmt.where(
                    ContextNode.context_type
                    == context_type
                )

            if target_uri:
                stmt = stmt.where(
                    ContextNode.uri.startswith(
                        target_uri.rstrip("/") + "/"
                    )
                )

            result = await db.execute(stmt)

            nodes = result.scalars().all()

        if not nodes:
            return []

        query_embedding = None

        try:
            embeddings = await rag_service.embed_many(
                [query]
            )

            if embeddings:
                query_embedding = embeddings[0]

        except Exception:
            query_embedding = None

        configured_weights = {
            "semantic": 0.85,
            "lexical": 0.15,
        }

        scored = []

        for node in nodes:

            searchable_text = " ".join(
                [
                    node.name or "",
                    node.abstract or "",
                    node.overview or "",
                    node.content or "",
                ]
            )

            available_streams: set[str] = set()

            lexical = self._lexical_score(
                query,
                searchable_text,
            )
            if searchable_text.strip():
                available_streams.add("lexical")

            semantic = 0.0

            if query_embedding and node.embedding_json:
                try:
                    node_embedding = json.loads(
                        node.embedding_json
                    )

                    semantic = self._cosine_similarity(
                        query_embedding,
                        node_embedding,
                    )
                    available_streams.add("semantic")
                except Exception:
                    semantic = 0.0

            effective_weights = normalize_weights(
                available_streams,
                configured_weights,
            )

            score = (
                semantic * effective_weights.get("semantic", 0.0)
                + lexical * effective_weights.get("lexical", 0.0)
            )

            scored.append(
                (
                    score,
                    node,
                )
            )

        scored.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        results = []

        current_chars = 0

        for score, node in scored[:limit]:

            content = node.content or ""

            if current_chars + len(content) <= max_chars:
                selected_content = content
                level = 2

            elif current_chars + len(node.overview or "") <= max_chars:
                selected_content = node.overview
                level = 1

            else:
                selected_content = node.abstract
                level = 0

            results.append(
                {
                    "uri": node.uri,
                    "context_type": node.context_type,
                    "name": node.name,
                    "level": level,
                    "score": round(score, 6),
                    "abstract": node.abstract,
                    "overview": node.overview,
                    "content": selected_content,
                }
            )

            current_chars += len(
                selected_content or ""
            )

            if current_chars >= max_chars:
                break

        return results


context_service = ContextService()