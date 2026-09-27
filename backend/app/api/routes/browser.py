from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_current_user
from app.browser.schemas import (
    BrowserActionResponse,
    BrowserClickRequest,
    BrowserCloseRequest,
    BrowserCloseResponse,
    BrowserFillRequest,
    BrowserInspectRequest,
    BrowserInspectResponse,
    BrowserNavigationRequest,
    BrowserOpenRequest,
    BrowserOpenResponse,
    BrowserPressRequest,
    BrowserScreenshotRequest,
    BrowserScreenshotResponse,
)
from app.browser.service import browser_service
from app.database.models import User


router = APIRouter(
    prefix="/api/v1/browser",
    tags=["EVU Browser Intelligence"],
)


@router.post(
    "/open",
    response_model=BrowserOpenResponse,
)
async def open_browser(
    request: BrowserOpenRequest,
    current_user: User = Depends(
        get_current_user
    ),
):
    del current_user

    result = await browser_service.open(
        url=request.url,
        wait_until=request.wait_until,
    )

    if not result.success:
        raise HTTPException(
            status_code=502,
            detail=result.error,
        )

    return result


@router.post(
    "/inspect",
    response_model=BrowserInspectResponse,
)
async def inspect_browser(
    request: BrowserInspectRequest,
    current_user: User = Depends(
        get_current_user
    ),
):
    del current_user

    result = await browser_service.inspect(
        request.session_id
    )

    if not result.success:
        raise HTTPException(
            status_code=400,
            detail=result.error,
        )

    return result


@router.post(
    "/click",
    response_model=BrowserActionResponse,
)
async def click_browser(
    request: BrowserClickRequest,
    current_user: User = Depends(
        get_current_user
    ),
):
    del current_user

    result = await browser_service.click(
        session_id=request.session_id,
        selector=request.selector,
        wait_after=request.wait_after,
    )

    if not result.success:
        raise HTTPException(
            status_code=400,
            detail=result.error,
        )

    return result


@router.post(
    "/fill",
    response_model=BrowserActionResponse,
)
async def fill_browser(
    request: BrowserFillRequest,
    current_user: User = Depends(
        get_current_user
    ),
):
    del current_user

    result = await browser_service.fill(
        session_id=request.session_id,
        selector=request.selector,
        value=request.value,
        wait_after=request.wait_after,
    )

    if not result.success:
        raise HTTPException(
            status_code=400,
            detail=result.error,
        )

    return result


@router.post(
    "/press",
    response_model=BrowserActionResponse,
)
async def press_browser(
    request: BrowserPressRequest,
    current_user: User = Depends(
        get_current_user
    ),
):
    del current_user

    result = await browser_service.press(
        session_id=request.session_id,
        selector=request.selector,
        key=request.key,
        wait_after=request.wait_after,
    )

    if not result.success:
        raise HTTPException(
            status_code=400,
            detail=result.error,
        )

    return result


@router.post(
    "/back",
    response_model=BrowserActionResponse,
)
async def browser_back(
    request: BrowserNavigationRequest,
    current_user: User = Depends(
        get_current_user
    ),
):
    del current_user

    result = await browser_service.back(
        request.session_id
    )

    if not result.success:
        raise HTTPException(
            status_code=400,
            detail=result.error,
        )

    return result


@router.post(
    "/forward",
    response_model=BrowserActionResponse,
)
async def browser_forward(
    request: BrowserNavigationRequest,
    current_user: User = Depends(
        get_current_user
    ),
):
    del current_user

    result = await browser_service.forward(
        request.session_id
    )

    if not result.success:
        raise HTTPException(
            status_code=400,
            detail=result.error,
        )

    return result


@router.post(
    "/screenshot",
    response_model=BrowserScreenshotResponse,
)
async def browser_screenshot(
    request: BrowserScreenshotRequest,
    current_user: User = Depends(
        get_current_user
    ),
):
    del current_user

    result = await browser_service.screenshot(
        session_id=request.session_id,
        full_page=request.full_page,
    )

    if not result.success:
        raise HTTPException(
            status_code=400,
            detail=result.error,
        )

    return result


@router.post(
    "/close",
    response_model=BrowserCloseResponse,
)
async def close_browser(
    request: BrowserCloseRequest,
    current_user: User = Depends(
        get_current_user
    ),
):
    del current_user

    closed = await browser_service.close(
        request.session_id
    )

    return BrowserCloseResponse(
        session_id=request.session_id,
        closed=closed,
        success=True,
    )