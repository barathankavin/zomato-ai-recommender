"""Deterministic restaurant filtering.

Filter chain (in order): location → min_rating → budget → cuisine overlap.

Edge cases handled:
- Zero candidates after all filters → returns empty list
- Exactly 1 candidate → returns it
- Candidates exceed candidate_cap → truncated after rating sort
- All restaurants share same rating → stable sort preserves order
"""

from __future__ import annotations

from milestone1.phase1_ingestion.models import Restaurant
from milestone1.phase2_preferences.models import UserPreferences

DEFAULT_CANDIDATE_CAP = 20


def filter_restaurants(
    restaurants: list[Restaurant],
    prefs: UserPreferences,
    candidate_cap: int = DEFAULT_CANDIDATE_CAP,
) -> list[Restaurant]:
    """Apply hard filters and return capped, rating-sorted candidates.

    Filter order:
        1. Location (case-insensitive exact match)
        2. Minimum rating
        3. Budget band (if specified)
        4. Cuisine overlap (if any cuisines specified)

    Args:
        restaurants: Full corpus.
        prefs: Validated user preferences.
        candidate_cap: Max candidates to return (default 20).

    Returns:
        Rating-sorted list of candidates, truncated to candidate_cap.
    """
    candidates = restaurants

    # 1. Location filter (case-insensitive)
    candidates = [
        r for r in candidates
        if r.location.lower() == prefs.location.lower()
    ]

    # 2. Min rating filter
    if prefs.min_rating > 0.0:
        candidates = [
            r for r in candidates
            if r.rating >= prefs.min_rating
        ]

    # 3. Budget filter (optional)
    if prefs.budget is not None:
        candidates = [
            r for r in candidates
            if r.budget == prefs.budget
        ]

    # 4. Cuisine filter (optional — empty means "all cuisines")
    if prefs.cuisines:
        pref_cuisines_lower = {c.lower() for c in prefs.cuisines}
        candidates = [
            r for r in candidates
            if any(c.lower() in pref_cuisines_lower for c in r.cuisines)
        ]

    # Ranking hint: sort by rating descending (stable sort)
    candidates.sort(key=lambda r: r.rating, reverse=True)

    # Truncate to candidate cap
    return candidates[:candidate_cap]
