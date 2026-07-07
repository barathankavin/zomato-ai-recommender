"""City corpus and fuzzy matching.

Edge cases handled:
- Location not in dataset → fuzzy match top-3 suggestions
- Case-insensitive matching
"""

from __future__ import annotations

import difflib
from milestone1.phase1_ingestion.models import Restaurant


def allowed_cities_from_restaurants(restaurants: list[Restaurant]) -> set[str]:
    """Build the set of allowed cities/locations from the loaded corpus."""
    return {r.location for r in restaurants}


def fuzzy_match_city(
    query: str,
    allowed: set[str],
    max_suggestions: int = 3,
    cutoff: float = 0.5,
) -> list[str]:
    """Return fuzzy-matched city suggestions using SequenceMatcher.

    Args:
        query: The user-typed location.
        allowed: Set of valid location strings.
        max_suggestions: Maximum number of suggestions.
        cutoff: Minimum similarity ratio (0.0–1.0).

    Returns:
        List of closest matches, sorted by similarity (best first).
    """
    matches = difflib.get_close_matches(
        query,
        list(allowed),
        n=max_suggestions,
        cutoff=cutoff,
    )
    return matches
