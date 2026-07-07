"""Recommendation engine models."""

from __future__ import annotations

from pydantic import BaseModel, Field


class RankedRestaurant(BaseModel):
    """A single restaurant in the ranked recommendation list."""

    restaurant_id: int
    rank: int
    name: str = ""
    explanation: str = ""


class RecommendationResult(BaseModel):
    """Result of a recommendation request."""

    rankings: list[RankedRestaurant] = Field(default_factory=list)
    source: str = Field(
        default="llm",
        description="'llm' for AI-ranked, 'fallback' for rating-sorted top-k"
    )
    has_results: bool = True
    empty_reason: str | None = Field(
        default=None,
        description="'no_candidates' | 'llm_no_picks' | None"
    )
    token_usage: dict | None = None
    latency_ms: float | None = None
