"""Output rendering for recommendation results.

Provides markdown and plain-text rendering for ranked restaurants,
with special handling for fallback source and edge cases.
"""

from __future__ import annotations

from milestone1.phase4_llm.models import RecommendationResult
from milestone1.phase5_output.empty_states import get_empty_state_message


def render_markdown(result: RecommendationResult) -> str:
    """Render recommendation results as Markdown.

    Handles:
    - Fallback banner when source="fallback"
    - Empty states (no_candidates, llm_no_picks)
    - Normal ranked results with AI explanations
    """
    lines: list[str] = []

    # Empty states
    if not result.has_results:
        lines.append(get_empty_state_message(result.empty_reason, fmt="markdown"))
        return "\n".join(lines)

    # Fallback notice
    if result.source == "fallback":
        lines.append(
            "> ⚠️ **AI ranking unavailable** — showing top matches by rating.\n"
        )

    lines.append("## 🍽️ Restaurant Recommendations\n")

    for item in result.rankings:
        lines.append(f"### #{item.rank} {item.name}")
        if item.explanation:
            explanation = item.explanation[:500]
            lines.append(f"💡 *{explanation}*")
        lines.append("")

    # Telemetry summary
    if result.latency_ms is not None:
        lines.append(f"---\n*Response time: {result.latency_ms:.0f}ms*")

    return "\n".join(lines)


def render_plain(result: RecommendationResult) -> str:
    """Render recommendation results as plain text for CLI."""
    lines: list[str] = []

    if not result.has_results:
        lines.append(get_empty_state_message(result.empty_reason, fmt="plain"))
        return "\n".join(lines)

    if result.source == "fallback":
        lines.append("[!] AI ranking unavailable — showing top matches by rating.\n")

    lines.append("=== Restaurant Recommendations ===\n")

    for item in result.rankings:
        lines.append(f"  #{item.rank} {item.name}")
        if item.explanation:
            explanation = item.explanation[:500]
            lines.append(f"      → {explanation}")
        lines.append("")

    if result.latency_ms is not None:
        lines.append(f"--- Response time: {result.latency_ms:.0f}ms ---")

    return "\n".join(lines)
