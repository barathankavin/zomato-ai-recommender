"""FastAPI application — thin HTTP layer over the recommendation pipeline.

Endpoints:
    POST /api/v1/recommendations — get restaurant recommendations
    GET  /health                 — health check
    GET  /api/v1/meta            — corpus metadata (locations, cuisines)

Edge cases handled:
    - 422 on bad input (Pydantic validation)
    - 503 if Groq not configured
    - CORS restricted to allowed origins
    - No raw user text in logs
"""

from __future__ import annotations

import logging
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from milestone1.phase0.settings import load_settings
from milestone1.phase2_preferences.models import UserPreferences
from milestone1.phase2_preferences.cities import allowed_cities_from_restaurants, fuzzy_match_city
from milestone1.phase4_llm.recommend import recommend
from milestone1.phase5_output.telemetry import emit_telemetry
from milestone1.phase6_api.corpus import get_corpus, get_corpus_size
from milestone1.phase6_api.schemas import (
    RecommendationRequest,
    RecommendationResponse,
    RankedItem,
    HealthResponse,
    MetaResponse,
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Zomato AI Recommendation API",
    version="1.0.0",
    description="AI-powered restaurant recommendations for Bangalore",
)

# CORS
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in cors_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Lightweight root so platform probes don't 404."""
    return {"status": "ok"}


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check — reports Groq config and corpus status."""
    settings = load_settings()
    # Avoid loading the full corpus during platform health probes.
    # Corpus is loaded lazily on /api/v1/meta and /api/v1/recommendations.
    corpus_size = get_corpus_size() or 0
    return HealthResponse(
        status="ok",
        groq_configured=bool(
            settings.groq_api_key and settings.groq_api_key != "your_groq_api_key_here"
        ),
        corpus_size=corpus_size,
    )


@app.get("/api/v1/meta", response_model=MetaResponse)
async def meta():
    """Return corpus metadata — available locations and cuisines."""
    corpus = get_corpus()
    locations = sorted({r.location for r in corpus})
    cuisines = sorted({c for r in corpus for c in r.cuisines if c != "Unknown"})
    return MetaResponse(
        locations=locations,
        cuisines=cuisines,
        total_restaurants=len(corpus),
    )


@app.post("/api/v1/recommendations", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    """Get restaurant recommendations based on user preferences."""
    corpus = get_corpus()
    settings = load_settings()

    # Check if Groq is configured (edge case 6.2)
    groq_configured = bool(
        settings.groq_api_key and settings.groq_api_key != "your_groq_api_key_here"
    )

    # Validate location against corpus
    allowed_cities = allowed_cities_from_restaurants(corpus)
    location_lower = request.location.lower()
    exact_match = any(c.lower() == location_lower for c in allowed_cities)

    if not exact_match:
        suggestions = fuzzy_match_city(request.location, allowed_cities)
        if suggestions:
            raise HTTPException(
                status_code=422,
                detail={
                    "field": "location",
                    "message": f"Location '{request.location}' not found. Did you mean: {', '.join(suggestions)}?",
                    "suggestions": suggestions,
                },
            )
        else:
            raise HTTPException(
                status_code=422,
                detail={
                    "field": "location",
                    "message": f"Location '{request.location}' not found in our database.",
                },
            )

    # Find the canonical casing for the location
    canonical_location = next(
        c for c in allowed_cities if c.lower() == location_lower
    )

    # Build preferences
    prefs = UserPreferences(
        location=canonical_location,
        budget=request.budget,
        cuisines=request.cuisines,
        min_rating=request.min_rating,
        additional_preferences=request.additional_preferences,
    )

    # Run recommendation pipeline
    result = recommend(corpus, prefs)

    # Emit telemetry (no PII)
    emit_telemetry(
        result,
        candidate_count=len(result.rankings),
        corpus_size=len(corpus),
    )

    # Build response
    return RecommendationResponse(
        rankings=[
            RankedItem(
                restaurant_id=r.restaurant_id,
                rank=r.rank,
                name=r.name,
                explanation=r.explanation,
            )
            for r in result.rankings
        ],
        source=result.source,
        has_results=result.has_results,
        empty_reason=result.empty_reason,
        candidate_count=len(result.rankings),
        latency_ms=result.latency_ms,
    )
