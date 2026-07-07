"""Tests for Phase 2 — User preferences validation."""

import pytest
from pydantic import ValidationError
from milestone1.phase2_preferences.models import UserPreferences, PreferencesError
from milestone1.phase2_preferences.parser import parse_preferences
from milestone1.phase2_preferences.cities import fuzzy_match_city


# ---------------------------------------------------------------------------
# UserPreferences validation
# ---------------------------------------------------------------------------

class TestUserPreferences:
    def test_valid_minimal(self):
        p = UserPreferences(location="Koramangala")
        assert p.location == "Koramangala"
        assert p.budget is None
        assert p.cuisines == []
        assert p.min_rating == 0.0

    def test_empty_location_rejected(self):
        with pytest.raises(ValidationError):
            UserPreferences(location="")

    def test_whitespace_location_rejected(self):
        with pytest.raises(ValidationError):
            UserPreferences(location="   ")

    def test_rating_clamped_high(self):
        p = UserPreferences(location="Test", min_rating=10.0)
        assert p.min_rating == 5.0

    def test_rating_clamped_low(self):
        p = UserPreferences(location="Test", min_rating=-1.0)
        assert p.min_rating == 0.0

    def test_additional_truncated(self):
        long_text = "x" * 600
        p = UserPreferences(location="Test", additional_preferences=long_text)
        assert len(p.additional_preferences) == 500

    def test_html_stripped(self):
        p = UserPreferences(
            location="Test",
            additional_preferences="<script>alert('xss')</script>Hello"
        )
        assert "<script>" not in p.additional_preferences
        assert "Hello" in p.additional_preferences

    def test_control_chars_stripped(self):
        p = UserPreferences(
            location="Test",
            additional_preferences="Hello\x00World"
        )
        assert "\x00" not in p.additional_preferences


# ---------------------------------------------------------------------------
# parse_preferences
# ---------------------------------------------------------------------------

class TestParsePreferences:
    def test_valid(self):
        prefs = parse_preferences({"location": "Koramangala"})
        assert prefs.location == "Koramangala"

    def test_missing_location(self):
        with pytest.raises(PreferencesError) as exc_info:
            parse_preferences({"location": ""})
        assert exc_info.value.field is not None


# ---------------------------------------------------------------------------
# fuzzy_match_city
# ---------------------------------------------------------------------------

class TestFuzzyMatchCity:
    def test_exact_match(self):
        allowed = {"Koramangala", "Indiranagar", "Whitefield"}
        matches = fuzzy_match_city("Koramangala", allowed)
        assert "Koramangala" in matches

    def test_close_match(self):
        allowed = {"Koramangala", "Indiranagar", "Whitefield"}
        matches = fuzzy_match_city("Koramangla", allowed)  # Typo
        assert "Koramangala" in matches

    def test_no_match(self):
        allowed = {"Koramangala", "Indiranagar"}
        matches = fuzzy_match_city("xyzzyxyzzy", allowed)
        assert matches == []
