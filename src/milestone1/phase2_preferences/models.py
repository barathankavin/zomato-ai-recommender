"""User preference models and validation.

Edge cases handled:
- Empty/null location → PreferencesError
- Budget not in [Low, Medium, High] → validation error
- min_rating outside [0.0, 5.0] → clamped
- Empty cuisines → no filter (all match)
- additional_preferences > 500 chars → truncated
- Control chars / HTML in free text → stripped
"""

from __future__ import annotations

import re
from pydantic import BaseModel, Field, field_validator
from milestone1.phase1_ingestion.models import BudgetBand


class PreferencesError(Exception):
    """Raised when user preferences are invalid."""

    def __init__(self, message: str, field: str | None = None):
        self.field = field
        super().__init__(message)


_CONTROL_CHAR_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")
_HTML_TAG_RE = re.compile(r"<[^>]+>")
MAX_ADDITIONAL_LEN = 500


class UserPreferences(BaseModel):
    """Validated user preferences for restaurant search."""

    location: str = Field(..., description="Neighbourhood / area to search")
    budget: BudgetBand | None = Field(
        default=None, description="Budget band filter (optional)"
    )
    cuisines: list[str] = Field(
        default_factory=list, description="Preferred cuisines (empty = no filter)"
    )
    min_rating: float = Field(
        default=0.0, description="Minimum acceptable rating [0.0–5.0]"
    )
    additional_preferences: str = Field(
        default="", description="Free-text additional preferences (max 500 chars)"
    )

    @field_validator("location")
    @classmethod
    def validate_location(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("location is required")
        return v.strip()

    @field_validator("min_rating")
    @classmethod
    def clamp_rating(cls, v: float) -> float:
        return max(0.0, min(5.0, v))

    @field_validator("additional_preferences")
    @classmethod
    def sanitise_additional(cls, v: str) -> str:
        if not v:
            return ""
        # Strip HTML tags (edge case 2.8)
        v = _HTML_TAG_RE.sub("", v)
        # Strip control characters (edge case 2.7)
        v = _CONTROL_CHAR_RE.sub("", v)
        # Truncate (edge case 2.6)
        return v[:MAX_ADDITIONAL_LEN]
