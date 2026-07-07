"""Tests for Phase 1 — Data normalisation."""

import pytest
from milestone1.phase1_ingestion.normalizer import (
    parse_rating,
    parse_cost,
    map_budget,
    split_cuisines,
    strip_control_chars,
    parse_yes_no,
)
from milestone1.phase1_ingestion.models import BudgetBand


# ---------------------------------------------------------------------------
# parse_rating edge cases
# ---------------------------------------------------------------------------

class TestParseRating:
    def test_normal(self):
        assert parse_rating("4.1") == 4.1

    def test_slash_format(self):
        assert parse_rating("4.1/5") == 4.1

    def test_new(self):
        assert parse_rating("NEW") == 0.0

    def test_none(self):
        assert parse_rating(None) == 0.0

    def test_empty_string(self):
        assert parse_rating("") == 0.0

    def test_dash(self):
        assert parse_rating("-") == 0.0

    def test_clamp_high(self):
        assert parse_rating("6.2") == 5.0

    def test_clamp_low(self):
        assert parse_rating("-1") == 0.0

    def test_garbage(self):
        assert parse_rating("not_a_number") == 0.0

    def test_whitespace(self):
        assert parse_rating("  3.5/5  ") == 3.5


# ---------------------------------------------------------------------------
# parse_cost edge cases
# ---------------------------------------------------------------------------

class TestParseCost:
    def test_normal(self):
        assert parse_cost("800") == 800

    def test_commas(self):
        assert parse_cost("1,200") == 1200

    def test_none(self):
        assert parse_cost(None) == 0

    def test_empty(self):
        assert parse_cost("") == 0

    def test_non_numeric(self):
        assert parse_cost("varies") == 0

    def test_int_input(self):
        assert parse_cost(500) == 500

    def test_float_input(self):
        assert parse_cost(499.9) == 499

    def test_negative(self):
        assert parse_cost("-100") == 0


# ---------------------------------------------------------------------------
# map_budget edge cases
# ---------------------------------------------------------------------------

class TestMapBudget:
    def test_low(self):
        assert map_budget(200) == BudgetBand.LOW

    def test_low_boundary(self):
        assert map_budget(400) == BudgetBand.LOW

    def test_medium(self):
        assert map_budget(700) == BudgetBand.MEDIUM

    def test_medium_boundary(self):
        assert map_budget(1000) == BudgetBand.MEDIUM

    def test_high(self):
        assert map_budget(1500) == BudgetBand.HIGH

    def test_zero(self):
        assert map_budget(0) == BudgetBand.LOW


# ---------------------------------------------------------------------------
# split_cuisines edge cases
# ---------------------------------------------------------------------------

class TestSplitCuisines:
    def test_normal(self):
        assert split_cuisines("North Indian, Chinese") == ["North Indian", "Chinese"]

    def test_none(self):
        assert split_cuisines(None) == ["Unknown"]

    def test_empty(self):
        assert split_cuisines("") == ["Unknown"]

    def test_single(self):
        assert split_cuisines("Italian") == ["Italian"]

    def test_whitespace(self):
        assert split_cuisines(" Thai , Japanese ") == ["Thai", "Japanese"]

    def test_trailing_comma(self):
        assert split_cuisines("Indian,") == ["Indian"]


# ---------------------------------------------------------------------------
# strip_control_chars
# ---------------------------------------------------------------------------

class TestStripControlChars:
    def test_normal(self):
        assert strip_control_chars("Hello World") == "Hello World"

    def test_null_bytes(self):
        assert strip_control_chars("Hello\x00World") == "HelloWorld"

    def test_none(self):
        assert strip_control_chars(None) == ""

    def test_preserves_newlines(self):
        # Newlines (\n = 0x0a) and tabs (\t = 0x09) are NOT in the regex
        assert strip_control_chars("Hello\nWorld") == "Hello\nWorld"


# ---------------------------------------------------------------------------
# parse_yes_no
# ---------------------------------------------------------------------------

class TestParseYesNo:
    def test_yes(self):
        assert parse_yes_no("Yes") is True

    def test_no(self):
        assert parse_yes_no("No") is False

    def test_none(self):
        assert parse_yes_no(None) is False

    def test_empty(self):
        assert parse_yes_no("") is False

    def test_case_insensitive(self):
        assert parse_yes_no("yes") is True
        assert parse_yes_no("YES") is True
