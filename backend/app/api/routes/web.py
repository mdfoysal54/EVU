from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_current_user
from app.database.models import User
from app.web.schemas import WebSearchRequest, WebSearchResponse
from app.web.service import web_search_service


router = APIRouter(
    prefix="/api/v1/web",
    tags=["EVU Web Intelligence"],
)


@router.post("/search", response_model=WebSearchResponse)
async def search_web(
    request: WebSearchRequest,
    current_user: User = Depends(get_current_user),
):
    del current_user

    try:
        provider, results = await web_search_service.search(
            request.query,
            request.max_results,
        )

        return WebSearchResponse(
            query=request.query,
            provider=provider,
            results=results,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc