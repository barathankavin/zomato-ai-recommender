"""Preference parsing — validate and coerce raw input into UserPreferences."""

from __future__ import annotations

from pydantic import ValidationError
from milestone1.phase2_preferences.models import UserPreferences, PreferencesError


def parse_preferences(raw: dict) -> UserPreferences:
    """Parse a raw dict (from API/form/CLI) into validated UserPreferences.

    Raises:
        PreferencesError: With field-level detail on validation failure.
    """
    try:
        return UserPreferences(**raw)
    except ValidationError as exc:
        # Extract first field error for user-friendly message
        errors = exc.errors()
        if errors:
            first = errors[0]
            field = ".".join(str(loc) for loc in first.get("loc", []))
            msg = first.get("msg", "Invalid input")
            raise PreferencesError(msg, field=field) from exc
        raise PreferencesError("Invalid preferences input") from exc
