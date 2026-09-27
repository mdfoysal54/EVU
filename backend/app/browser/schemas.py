from __future__ import annotations

from pydantic import BaseModel, Field


class BrowserOpenRequest(BaseModel):
    url: str = Field(
        min_length=8,
        max_length=2048,
    )

    wait_until: str = Field(
        default="domcontentloaded",
        pattern="^(commit|domcontentloaded|load|networkidle)$",
    )


class BrowserOpenResponse(BaseModel):
    session_id: str
    url: str
    title: str
    text: str
    success: bool = True
    error: str = ""


class BrowserInspectRequest(BaseModel):
    session_id: str


class BrowserInspectResponse(BaseModel):
    session_id: str
    url: str
    title: str
    text: str
    links: list[dict[str, str]] = Field(
        default_factory=list
    )
    success: bool = True
    error: str = ""


class BrowserClickRequest(BaseModel):
    session_id: str

    selector: str = Field(
        min_length=1,
        max_length=500,
    )

    wait_after: int = Field(
        default=500,
        ge=0,
        le=5000,
    )


class BrowserActionResponse(BaseModel):
    session_id: str
    url: str
    title: str
    text: str
    success: bool = True
    error: str = ""


class BrowserFillRequest(BaseModel):
    session_id: str

    selector: str = Field(
        min_length=1,
        max_length=500,
    )

    value: str = Field(
        max_length=5000,
    )

    wait_after: int = Field(
        default=200,
        ge=0,
        le=5000,
    )


class BrowserPressRequest(BaseModel):
    session_id: str

    selector: str = Field(
        min_length=1,
        max_length=500,
    )

    key: str = Field(
        min_length=1,
        max_length=100,
    )

    wait_after: int = Field(
        default=500,
        ge=0,
        le=5000,
    )


class BrowserScreenshotRequest(BaseModel):
    session_id: str

    full_page: bool = False


class BrowserScreenshotResponse(BaseModel):
    session_id: str
    url: str
    title: str
    image_base64: str = ""
    success: bool = True
    error: str = ""


class BrowserNavigationRequest(BaseModel):
    session_id: str


class BrowserCloseRequest(BaseModel):
    session_id: str


class BrowserCloseResponse(BaseModel):
    session_id: str
    closed: bool
    success: bool = True
    error: str = ""