"""Data normalisation utilities for raw Zomato dataset rows.

Handles all edge cases documented in the architecture:
- Rating strings: "4.1/5", "NEW", None, out-of-range
- Cost strings: commas, empty, non-numeric
- Cuisine strings: empty, None, comma-separated
- Control characters in text fields
"""

from __future__ import annotations

import re
from milestone1.phase1_ingestion.models import BudgetBand


# ---------------------------------------------------------------------------
# Rating
# ---------------------------------------------------------------------------

def parse_rating(raw: str | None) -> float:
    """Parse a rating string into a float in [0.0, 5.0].

    Handles:
        "4.1/5"  → 4.1
        "NEW"    → 0.0
        ""       → 0.0
        None     → 0.0
        "-"      → 0.0
        "6.2"    → 5.0  (clamped)
        "-1"     → 0.0  (clamped)
    """
    if not raw or not isinstance(raw, str):
        return 0.0

    raw = raw.strip()

    # Handle "X/5" format
    if "/" in raw:
        raw = raw.split("/")[0].strip()

    # Handle non-numeric markers
    if raw.upper() in ("NEW", "-", "--", ""):
        return 0.0

    try:
        val = float(raw)
    except (ValueError, TypeError):
        return 0.0

    # Clamp to [0.0, 5.0]
    return max(0.0, min(5.0, val))


# ---------------------------------------------------------------------------
# Cost
# ---------------------------------------------------------------------------

def parse_cost(raw: str | int | float | None) -> int:
    """Parse approximate cost for two into an integer.

    Handles:
        "800"    → 800
        "1,200"  → 1200
        ""       → 0
        None     → 0
        "varies" → 0
    """
    if raw is None:
        return 0

    if isinstance(raw, (int, float)):
        return max(0, int(raw))

    raw = str(raw).strip().replace(",", "")

    try:
        return max(0, int(float(raw)))
    except (ValueError, TypeError):
        return 0


def map_budget(cost: int) -> BudgetBand:
    """Map cost-for-two to a budget band.

    Thresholds (Bangalore context):
        Low    : cost <= 400
        Medium : 400 < cost <= 1000
        High   : cost > 1000
    """
    if cost <= 400:
        return BudgetBand.LOW
    elif cost <= 1000:
        return BudgetBand.MEDIUM
    else:
        return BudgetBand.HIGH


# ---------------------------------------------------------------------------
# Cuisines
# ---------------------------------------------------------------------------

def split_cuisines(raw: str | None) -> list[str]:
    """Split a comma-separated cuisine string.

    Handles:
        "North Indian, Chinese"  → ["North Indian", "Chinese"]
        ""                       → ["Unknown"]
        None                     → ["Unknown"]
    """
    if not raw or not isinstance(raw, str):
        return ["Unknown"]

    cuisines = [c.strip() for c in raw.split(",") if c.strip()]
    return cuisines if cuisines else ["Unknown"]


# ---------------------------------------------------------------------------
# Text sanitisation
# ---------------------------------------------------------------------------

_CONTROL_CHAR_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


def strip_control_chars(text: str | None) -> str:
    """Remove control characters (except newline/tab/space) from text."""
    if not text:
        return ""
    return _CONTROL_CHAR_RE.sub("", text)


# ---------------------------------------------------------------------------
# Boolean fields
# ---------------------------------------------------------------------------

def parse_yes_no(raw: str | None) -> bool:
    """Parse 'Yes'/'No' to bool. Defaults to False."""
    if not raw or not isinstance(raw, str):
        return False
    return raw.strip().lower() == "yes"
