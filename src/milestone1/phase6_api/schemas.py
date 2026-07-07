"""Request/Response DTOs for the API."""

from __future__ import annotations

from pydantic import BaseModel, Field
from milestone1.phase1_ingestion.models import BudgetBand


class RecommendationRequest(BaseModel):
    """POST /api/v1/recommendations request body."""

    location: str = Field(..., description="Location/neighbourhood")
    budget: BudgetBand | None = Field(default=None, description="Budget band")
    cuisines: list[str] = Field(default_factory=list, description="Cuisine filters")
    min_rating: float = Field(default=0.0, ge=0.0, le=5.0, description="Min rating")
    additional_preferences: str = Field(
        default="", max_length=500, description="Free-text preferences"
    )


class RankedItem(BaseModel):
    """A single ranked restaurant in the response."""

    restaurant_id: int
    rank: int
    name: str
    explanation: str


class RecommendationResponse(BaseModel):
    """POST /api/v1/recommendations response body."""

    rankings: list[RankedItem] = Field(default_factory=list)
    source: str = Field(description="'llm' or 'fallback'")
    has_results: bool
    empty_reason: str | None = None
    candidate_count: int = 0
    latency_ms: float | None = None


class HealthResponse(BaseModel):
    """GET /health response."""

    status: str = "ok"
    groq_configured: bool = False
    corpus_size: int = 0


class MetaResponse(BaseModel):
    """GET /api/v1/meta response."""

    locations: list[str] = Field(default_factory=list)
    cuisines: list[str] = Field(default_factory=list)
    total_restaurants: int = 0
