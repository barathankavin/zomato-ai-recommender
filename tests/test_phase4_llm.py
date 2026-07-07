"""Tests for Phase 4 — LLM response validation (no actual API calls)."""

import pytest
from milestone1.phase1_ingestion.models import Restaurant, BudgetBand
from milestone1.phase4_llm.recommend import _validate_rankings, _build_fallback


def _make_restaurant(rid: int = 0, name: str = "Test", rating: float = 4.0) -> Restaurant:
    return Restaurant(
        restaurant_id=rid,
        name=name,
        location="Koramangala",
        cuisines=["Indian"],
        cost_raw=500,
        budget=BudgetBand.MEDIUM,
        rating=rating,
        votes=100,
    )


# ---------------------------------------------------------------------------
# _validate_rankings (hallucination guard)
# ---------------------------------------------------------------------------

class TestValidateRankings:
    def test_valid_ids(self):
        candidates = {0: _make_restaurant(0, "A"), 1: _make_restaurant(1, "B")}
        raw = [
            {"restaurant_id": 0, "rank": 1, "explanation": "Great"},
            {"restaurant_id": 1, "rank": 2, "explanation": "Good"},
        ]
        result = _validate_rankings(raw, candidates)
        assert len(result) == 2

    def test_hallucinated_id_discarded(self):
        candidates = {0: _make_restaurant(0, "A")}
        raw = [
            {"restaurant_id": 0, "rank": 1, "explanation": "Great"},
            {"restaurant_id": 999, "rank": 2, "explanation": "Fake"},
        ]
        result = _validate_rankings(raw, candidates)
        assert len(result) == 1
        assert result[0].restaurant_id == 0

    def test_all_hallucinated(self):
        candidates = {0: _make_restaurant(0, "A")}
        raw = [
            {"restaurant_id": 999, "rank": 1, "explanation": "Fake"},
        ]
        result = _validate_rankings(raw, candidates)
        assert len(result) == 0

    def test_duplicate_ids_deduped(self):
        candidates = {0: _make_restaurant(0, "A")}
        raw = [
            {"restaurant_id": 0, "rank": 1, "explanation": "First"},
            {"restaurant_id": 0, "rank": 2, "explanation": "Dup"},
        ]
        result = _validate_rankings(raw, candidates)
        assert len(result) == 1

    def test_missing_restaurant_id(self):
        candidates = {0: _make_restaurant(0)}
        raw = [{"rank": 1, "explanation": "No ID"}]
        result = _validate_rankings(raw, candidates)
        assert len(result) == 0

    def test_explanation_truncated(self):
        candidates = {0: _make_restaurant(0)}
        raw = [{"restaurant_id": 0, "rank": 1, "explanation": "x" * 1000}]
        result = _validate_rankings(raw, candidates)
        assert len(result[0].explanation) <= 500


# ---------------------------------------------------------------------------
# _build_fallback
# ---------------------------------------------------------------------------

class TestBuildFallback:
    def test_fallback_source(self):
        candidates = [_make_restaurant(0), _make_restaurant(1)]
        result = _build_fallback(candidates)
        assert result.source == "fallback"

    def test_fallback_top_k(self):
        candidates = [_make_restaurant(i) for i in range(10)]
        result = _build_fallback(candidates, top_k=3)
        assert len(result.rankings) == 3

    def test_fallback_empty(self):
        result = _build_fallback([])
        assert not result.has_results
        assert result.empty_reason == "no_candidates"
