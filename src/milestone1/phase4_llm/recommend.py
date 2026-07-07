"""Recommendation orchestrator — LLM call with hallucination guard + fallback.

Edge cases handled:
- GROQ_API_KEY missing → immediate fallback
- LLM returns invalid JSON → fallback
- LLM hallucinates restaurant IDs → discard unknowns
- LLM returns empty rankings → llm_no_picks
- LLM returns more items than candidates → truncate
- Any exception → graceful fallback
"""

from __future__ import annotations

import logging
import time
from milestone1.phase1_ingestion.models import Restaurant
from milestone1.phase2_preferences.models import UserPreferences
from milestone1.phase3_integration.filter import filter_restaurants
from milestone1.phase3_integration.prompt import build_prompt
from milestone1.phase4_llm.client import create_groq_client, call_groq
from milestone1.phase4_llm.models import RankedRestaurant, RecommendationResult
from milestone1.phase0.settings import load_settings

logger = logging.getLogger(__name__)


def _build_fallback(
    candidates: list[Restaurant],
    top_k: int = 5,
) -> RecommendationResult:
    """Rating-sorted top-k fallback with template explanations."""
    ranked = []
    for i, r in enumerate(candidates[:top_k]):
        ranked.append(RankedRestaurant(
            restaurant_id=r.restaurant_id,
            rank=i + 1,
            name=r.name,
            explanation=(
                f"Rated {r.rating}/5 with {r.votes} votes. "
                f"Serves {', '.join(r.cuisines)}."
            ),
        ))

    return RecommendationResult(
        rankings=ranked,
        source="fallback",
        has_results=bool(ranked),
        empty_reason="no_candidates" if not ranked else None,
    )


def _validate_rankings(
    raw_rankings: list[dict],
    candidate_map: dict[int, Restaurant],
) -> list[RankedRestaurant]:
    """Validate LLM-returned rankings against candidate map.

    - Discards unknown restaurant_ids (hallucination guard)
    - Enriches with restaurant name
    - Truncates to candidate count
    """
    valid = []
    seen_ids: set[int] = set()

    for item in raw_rankings:
        rid = item.get("restaurant_id")
        if rid is None or rid not in candidate_map or rid in seen_ids:
            logger.warning("Discarding invalid/hallucinated restaurant_id: %s", rid)
            continue

        seen_ids.add(rid)
        restaurant = candidate_map[rid]
        explanation = str(item.get("explanation", ""))[:500]

        valid.append(RankedRestaurant(
            restaurant_id=rid,
            rank=len(valid) + 1,
            name=restaurant.name,
            explanation=explanation,
        ))

    return valid


def recommend(
    restaurants: list[Restaurant],
    prefs: UserPreferences,
    candidate_cap: int = 20,
    top_k: int = 5,
) -> RecommendationResult:
    """Run the full recommendation pipeline.

    1. Filter candidates (Phase 3)
    2. Build prompt (Phase 3)
    3. Call LLM (Phase 4) or fall back
    4. Validate and return

    Args:
        restaurants: Full restaurant corpus.
        prefs: Validated user preferences.
        candidate_cap: Max candidates to send to LLM.
        top_k: Number of recommendations to return.

    Returns:
        RecommendationResult with ranked restaurants.
    """
    start_time = time.time()

    # Step 1: Filter
    candidates = filter_restaurants(restaurants, prefs, candidate_cap)

    # Zero-candidate guard
    if not candidates:
        return RecommendationResult(
            rankings=[],
            source="fallback",
            has_results=False,
            empty_reason="no_candidates",
            latency_ms=round((time.time() - start_time) * 1000, 1),
        )

    # Step 2: Build candidate map + prompt
    candidate_map = {r.restaurant_id: r for r in candidates}
    prompt_payload = build_prompt(prefs, candidates)

    # Step 3: Try LLM
    settings = load_settings()
    client = create_groq_client(settings.groq_api_key)

    if client is None:
        logger.warning("Groq not configured, using fallback")
        result = _build_fallback(candidates, top_k)
        result.latency_ms = round((time.time() - start_time) * 1000, 1)
        return result

    try:
        llm_response = call_groq(
            client=client,
            model=settings.groq_model,
            system_prompt=prompt_payload["system"],
            user_message=prompt_payload["user"],
        )
    except Exception as exc:
        logger.error("LLM call failed: %s", exc)
        llm_response = None

    # Step 4: Parse LLM response or fallback
    if llm_response is None:
        logger.warning("LLM returned nothing, using fallback")
        result = _build_fallback(candidates, top_k)
        result.latency_ms = round((time.time() - start_time) * 1000, 1)
        return result

    raw_rankings = llm_response.get("rankings", [])
    meta = llm_response.get("_meta", {})

    if not raw_rankings:
        # LLM explicitly returned empty rankings
        return RecommendationResult(
            rankings=[],
            source="llm",
            has_results=False,
            empty_reason="llm_no_picks",
            token_usage=meta.get("usage"),
            latency_ms=round((time.time() - start_time) * 1000, 1),
        )

    # Validate and filter hallucinated IDs
    validated = _validate_rankings(raw_rankings, candidate_map)

    if not validated:
        # All IDs were hallucinated — fallback
        logger.warning("All LLM IDs were hallucinated, using fallback")
        result = _build_fallback(candidates, top_k)
        result.latency_ms = round((time.time() - start_time) * 1000, 1)
        return result

    return RecommendationResult(
        rankings=validated[:top_k],
        source="llm",
        has_results=True,
        token_usage=meta.get("usage"),
        latency_ms=round((time.time() - start_time) * 1000, 1),
    )
