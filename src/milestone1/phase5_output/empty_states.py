"""Empty state messages — distinct copy for different empty scenarios.

Three distinct empty states:
1. no_candidates  — No restaurants matched the filters
2. llm_no_picks   — AI model returned empty rankings
3. fallback       — AI unavailable, showing rating-sorted results
"""

from __future__ import annotations

_MESSAGES = {
    "no_candidates": {
        "markdown": (
            "## 😕 No restaurants found\n\n"
            "No restaurants match your current filters. "
            "Try broadening your search:\n"
            "- Choose a different location\n"
            "- Lower your minimum rating\n"
            "- Select a different budget range\n"
            "- Remove cuisine filters"
        ),
        "plain": (
            "No restaurants found.\n"
            "No restaurants match your current filters.\n"
            "Try: different location, lower rating, different budget, or fewer cuisine filters."
        ),
    },
    "llm_no_picks": {
        "markdown": (
            "## 🤔 AI couldn't decide\n\n"
            "The AI model reviewed the candidates but couldn't pick the best matches. "
            "This can happen with very specific preferences.\n\n"
            "**Try:** Broaden your filters or adjust your additional preferences."
        ),
        "plain": (
            "AI couldn't decide.\n"
            "The AI reviewed candidates but couldn't pick best matches.\n"
            "Try: Broaden filters or adjust additional preferences."
        ),
    },
}


def get_empty_state_message(reason: str | None, fmt: str = "markdown") -> str:
    """Get the appropriate empty state message.

    Args:
        reason: 'no_candidates' | 'llm_no_picks' | None
        fmt: 'markdown' or 'plain'

    Returns:
        Human-readable empty state message.
    """
    if reason and reason in _MESSAGES:
        return _MESSAGES[reason].get(fmt, _MESSAGES[reason]["plain"])

    # Default fallback
    return _MESSAGES["no_candidates"].get(fmt, _MESSAGES["no_candidates"]["plain"])
