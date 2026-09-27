from __future__ import annotations

from pydantic import BaseModel, Field


class WebSearchRequest(BaseModel):
    query: str = Field(
        min_length=2,
        max_length=1000,
    )

    max_results: int = Field(
        default=5,
        ge=1,
        le=10,
    )


class WebSearchResult(BaseModel):
    title: str = ""

    url: str

    snippet: str = ""

    source: str = ""

    score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )


class WebSearchResponse(BaseModel):
    query: str

    provider: str

    results: list[WebSearchResult] = Field(
        default_factory=list
    )


class WebFetchRequest(BaseModel):
    url: str = Field(
        min_length=8,
        max_length=2048,
    )


class WebPageResponse(BaseModel):
    url: str

    final_url: str

    title: str = ""

    status_code: int = 0

    content_type: str = ""

    text: str = ""

    success: bool = True

    error: str = ""

    score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )


class WebResearchRequest(BaseModel):
    query: str = Field(
        min_length=2,
        max_length=1000,
    )

    max_results: int = Field(
        default=5,
        ge=1,
        le=10,
    )

    fetch_pages: int = Field(
        default=3,
        ge=0,
        le=5,
    )


class WebResearchResponse(BaseModel):
    query: str

    provider: str

    search_results: list[WebSearchResult] = Field(
        default_factory=list
    )

    pages: list[WebPageResponse] = Field(
        default_factory=list
    )

    context: str = ""