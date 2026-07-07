"""Tests for Phase 3 — Filter and prompt builder."""

import pytest
from milestone1.phase1_ingestion.models import Restaurant, BudgetBand
from milestone1.phase2_preferences.models import UserPreferences
from milestone1.phase3_integration.filter import filter_restaurants
from milestone1.phase3_integration.prompt import build_prompt


def _make_restaurant(
    rid: int = 0,
    name: str = "Test",
    location: str = "Koramangala",
    cuisines: list[str] | None = None,
    rating: float = 4.0,
    cost: int = 500,
    budget: BudgetBand = BudgetBand.MEDIUM,
) -> Restaurant:
    return Restaurant(
        restaurant_id=rid,
        name=name,
        location=location,
        cuisines=cuisines or ["Indian"],
        cost_raw=cost,
        budget=budget,
        rating=rating,
        votes=100,
    )


# ---------------------------------------------------------------------------
# Filter edge cases
# ---------------------------------------------------------------------------

class TestFilter:
    def test_location_filter(self):
        restaurants = [
            _make_restaurant(0, "A", "Koramangala"),
            _make_restaurant(1, "B", "Indiranagar"),
        ]
        prefs = UserPreferences(location="Koramangala")
        result = filter_restaurants(restaurants, prefs)
        assert len(result) == 1
        assert result[0].name == "A"

    def test_location_case_insensitive(self):
        restaurants = [_make_restaurant(0, "A", "Koramangala")]
        prefs = UserPreferences(location="koramangala")
        assert len(filter_restaurants(restaurants, prefs)) == 1

    def test_zero_candidates(self):
        restaurants = [_make_restaurant(0, "A", "Indiranagar")]
        prefs = UserPreferences(location="Koramangala")
        assert filter_restaurants(restaurants, prefs) == []

    def test_min_rating_filter(self):
        restaurants = [
            _make_restaurant(0, "A", rating=3.5),
            _make_restaurant(1, "B", rating=4.5),
        ]
        prefs = UserPreferences(location="Koramangala", min_rating=4.0)
        result = filter_restaurants(restaurants, prefs)
        assert len(result) == 1
        assert result[0].name == "B"

    def test_budget_filter(self):
        restaurants = [
            _make_restaurant(0, "A", budget=BudgetBand.LOW),
            _make_restaurant(1, "B", budget=BudgetBand.HIGH),
        ]
        prefs = UserPreferences(location="Koramangala", budget=BudgetBand.LOW)
        result = filter_restaurants(restaurants, prefs)
        assert len(result) == 1
        assert result[0].name == "A"

    def test_cuisine_filter(self):
        restaurants = [
            _make_restaurant(0, "A", cuisines=["Indian", "Chinese"]),
            _make_restaurant(1, "B", cuisines=["Italian"]),
        ]
        prefs = UserPreferences(location="Koramangala", cuisines=["Chinese"])
        result = filter_restaurants(restaurants, prefs)
        assert len(result) == 1
        assert result[0].name == "A"

    def test_no_cuisine_filter_matches_all(self):
        restaurants = [
            _make_restaurant(0, "A", cuisines=["Indian"]),
            _make_restaurant(1, "B", cuisines=["Italian"]),
        ]
        prefs = UserPreferences(location="Koramangala", cuisines=[])
        assert len(filter_restaurants(restaurants, prefs)) == 2

    def test_candidate_cap(self):
        restaurants = [_make_restaurant(i, f"R{i}") for i in range(30)]
        prefs = UserPreferences(location="Koramangala")
        result = filter_restaurants(restaurants, prefs, candidate_cap=5)
        assert len(result) == 5

    def test_rating_sort(self):
        restaurants = [
            _make_restaurant(0, "Low", rating=2.0),
            _make_restaurant(1, "High", rating=4.5),
            _make_restaurant(2, "Mid", rating=3.5),
        ]
        prefs = UserPreferences(location="Koramangala")
        result = filter_restaurants(restaurants, prefs)
        assert result[0].name == "High"
        assert result[1].name == "Mid"
        assert result[2].name == "Low"

    def test_single_candidate(self):
        restaurants = [_make_restaurant(0, "Only")]
        prefs = UserPreferences(location="Koramangala")
        result = filter_restaurants(restaurants, prefs)
        assert len(result) == 1


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------

class TestPromptBuilder:
    def test_builds_system_and_user(self):
        candidates = [_make_restaurant(0, "TestRestaurant")]
        prefs = UserPreferences(location="Koramangala")
        prompt = build_prompt(prefs, candidates)
        assert "system" in prompt
        assert "user" in prompt

    def test_candidates_in_prompt(self):
        candidates = [_make_restaurant(0, "MyRestaurant")]
        prefs = UserPreferences(location="Koramangala")
        prompt = build_prompt(prefs, candidates)
        assert "MyRestaurant" in prompt["user"]

    def test_grounding_rule_in_system(self):
        candidates = [_make_restaurant(0)]
        prefs = UserPreferences(location="Koramangala")
        prompt = build_prompt(prefs, candidates)
        assert "ONLY" in prompt["system"]
        assert "hallucinate" in prompt["system"].lower()
