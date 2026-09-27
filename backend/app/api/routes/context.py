from fastapi import APIRouter, Depends

from app.context.schemas import (
    ContextNodeCreate,
    ContextSearchRequest,
)
from app.context.service import context_service

router = APIRouter(
    prefix="/api/v1/context",
    tags=["context"],
)


@router.post("/nodes")
async def create_context_node(
    payload: ContextNodeCreate,
):
    node = await context_service.upsert(
        user_id=payload.user_id,
        uri=payload.uri,
        context_type=payload.context_type,
        name=payload.name,
        content=payload.content,
        parent_uri=payload.parent_uri,
        abstract=payload.abstract,
        overview=payload.overview,
        metadata=payload.metadata,
        source=payload.source,
    )

    return {
        "id": node.id,
        "uri": node.uri,
        "context_type": node.context_type,
    }


@router.post("/search")
async def search_context(
    payload: ContextSearchRequest,
):
    results = await context_service.search(
        query=payload.query,
        user_id=payload.user_id,
        context_type=payload.context_type,
        target_uri=payload.target_uri,
        limit=payload.limit,
        max_chars=(
            payload.max_chars
            or 12000
        ),
    )

    return {
        "query": payload.query,
        "context_type": payload.context_type,
        "results": results,
    }