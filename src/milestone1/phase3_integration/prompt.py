"""Prompt assembly for LLM recommendation.

Builds a system prompt + user message containing:
- User preferences as JSON
- Candidate restaurants as a structured table
"""

from __future__ import annotations

import json
from milestone1.phase1_ingestion.models import Restaurant
from milestone1.phase2_preferences.models import UserPreferences


SYSTEM_PROMPT = """You are a restaurant recommendation expert for Bangalore, India.
You will be given a list of candidate restaurants and user preferences.
Your job is to rank the TOP 5 restaurants from the candidates that best match
the user's preferences and explain why each is a good fit.

RULES:
1. You must ONLY recommend restaurants from the provided candidate list.
2. Do NOT invent or hallucinate restaurants that are not in the list.
3. Every restaurant_id in your response MUST exist in the candidate list.
4. Return your response as valid JSON in this exact format:
{
  "rankings": [
    {
      "restaurant_id": <int>,
      "rank": <int 1-5>,
      "explanation": "<1-2 sentence reason>"
    }
  ]
}
5. If none of the candidates are a good fit, return: {"rankings": []}
6. Keep explanations concise and specific to the user's stated preferences.
"""


def _restaurant_to_row(r: Restaurant) -> dict:
    """Convert restaurant to a compact dict for the prompt."""
    return {
        "id": r.restaurant_id,
        "name": r.name,
        "cuisines": ", ".join(r.cuisines),
        "rating": r.rating,
        "cost_for_two": r.cost_raw,
        "budget": r.budget.value,
        "type": r.rest_type,
        "votes": r.votes,
    }


def build_prompt(
    prefs: UserPreferences,
    candidates: list[Restaurant],
) -> dict:
    """Build the prompt payload for the LLM.

    Returns:
        Dict with 'system' and 'user' message strings.
    """
    prefs_dict = {
        "location": prefs.location,
        "budget": prefs.budget.value if prefs.budget else "Any",
        "cuisines": prefs.cuisines if prefs.cuisines else "Any",
        "min_rating": prefs.min_rating,
        "additional_preferences": prefs.additional_preferences or "None",
    }

    candidate_rows = [_restaurant_to_row(r) for r in candidates]

    user_message = (
        f"## User Preferences\n"
        f"```json\n{json.dumps(prefs_dict, indent=2)}\n```\n\n"
        f"## Candidate Restaurants ({len(candidates)} total)\n"
        f"```json\n{json.dumps(candidate_rows, indent=2)}\n```\n\n"
        f"Please rank the top 5 restaurants from the candidates above."
    )

    return {
        "system": SYSTEM_PROMPT,
        "user": user_message,
    }
