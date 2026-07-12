"""Dataset loader — prefers local JSON, falls back to HuggingFace.

Edge cases handled:
- HuggingFace unreachable → DatasetLoadError
- Rows with missing name/location → skipped
- Duplicate (name, location) → keep highest-rated
- Empty dataset after cleaning → EmptyDatasetError
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

from milestone1.phase1_ingestion.models import Restaurant
from milestone1.phase1_ingestion.normalizer import (
    parse_rating,
    parse_cost,
    map_budget,
    split_cuisines,
    strip_control_chars,
    parse_yes_no,
)

logger = logging.getLogger(__name__)

DATASET_ID = "ManikaSaini/zomato-restaurant-recommendation"
LOCAL_CORPUS_PATH = Path(__file__).resolve().parents[3] / "data" / "restaurants.json"


class DatasetLoadError(Exception):
    """Raised when dataset cannot be loaded from HuggingFace."""


class EmptyDatasetError(Exception):
    """Raised when dataset has zero valid rows after cleaning."""


def _row_to_restaurant(idx: int, row: dict) -> Optional[Restaurant]:
    """Convert a raw HuggingFace row dict to a Restaurant, or None if invalid."""
    name = row.get("name")
    location = row.get("location")

    # Edge case 1.9: skip rows without name or location
    if not name or not isinstance(name, str) or not name.strip():
        return None
    if not location or not isinstance(location, str) or not location.strip():
        return None

    name = strip_control_chars(name.strip())
    location = strip_control_chars(location.strip())

    rating = parse_rating(row.get("rate"))
    cost = parse_cost(row.get("approx_cost(for two people)"))
    budget = map_budget(cost)
    cuisines = split_cuisines(row.get("cuisines"))
    votes_raw = row.get("votes", 0)

    try:
        votes = int(votes_raw) if votes_raw else 0
    except (ValueError, TypeError):
        votes = 0

    rest_type = strip_control_chars(str(row.get("rest_type", "") or ""))

    return Restaurant(
        restaurant_id=idx,
        name=name,
        location=location,
        cuisines=cuisines,
        cost_raw=cost,
        budget=budget,
        rating=rating,
        votes=votes,
        online_order=parse_yes_no(row.get("online_order")),
        book_table=parse_yes_no(row.get("book_table")),
        rest_type=rest_type,
    )


def _deduplicate(restaurants: list[Restaurant]) -> list[Restaurant]:
    """Keep the highest-rated row per (name, location) pair."""
    best: dict[tuple[str, str], Restaurant] = {}
    for r in restaurants:
        key = (r.name.lower(), r.location.lower())
        if key not in best or r.rating > best[key].rating:
            best[key] = r
    return list(best.values())


def _local_corpus_paths() -> list[Path]:
    return [
        LOCAL_CORPUS_PATH,
        Path.cwd() / "data" / "restaurants.json",
    ]


def _load_from_local(limit: int | None = None) -> list[Restaurant] | None:
    """Load prebuilt corpus from disk if present (low-memory path for free hosts)."""
    path = next((p for p in _local_corpus_paths() if p.exists()), None)
    if path is None:
        return None

    logger.info("Loading restaurant corpus from %s", path)
    with path.open(encoding="utf-8") as f:
        rows = json.load(f)

    restaurants = [Restaurant.model_validate(row) for row in rows]
    if limit is not None:
        restaurants = restaurants[:limit]

    if not restaurants:
        raise EmptyDatasetError("Local corpus has zero restaurants.")

    logger.info("Loaded %d restaurants from local corpus", len(restaurants))
    return restaurants


def load_restaurants(limit: int | None = None) -> list[Restaurant]:
    """Load, normalise and deduplicate the Zomato dataset.

    Prefers ``data/restaurants.json`` when available to avoid HuggingFace/pyarrow
    memory spikes on small free-tier hosts.

    Args:
        limit: If set, only process this many rows (useful for dev/testing).

    Returns:
        List of deduplicated Restaurant objects.

    Raises:
        DatasetLoadError: If dataset cannot be fetched.
        EmptyDatasetError: If no valid rows remain after cleaning.
    """
    local = _load_from_local(limit=limit)
    if local is not None:
        return local

    try:
        from datasets import load_dataset
        ds = load_dataset(DATASET_ID, split="train")
    except Exception as exc:
        raise DatasetLoadError(
            f"Failed to load dataset '{DATASET_ID}': {exc}"
        ) from exc

    restaurants: list[Restaurant] = []
    for idx, row in enumerate(ds):
        if limit and idx >= limit:
            break

        r = _row_to_restaurant(idx, row)
        if r is not None:
            restaurants.append(r)

    logger.info("Parsed %d valid rows from %d total", len(restaurants), idx + 1)

    # Deduplicate
    restaurants = _deduplicate(restaurants)
    logger.info("After dedup: %d restaurants", len(restaurants))

    # Edge case 1.10: no valid rows
    if not restaurants:
        raise EmptyDatasetError("Dataset has zero valid rows after cleaning.")

    # Re-assign sequential IDs after dedup
    final: list[Restaurant] = []
    for new_id, r in enumerate(restaurants):
        final.append(r.model_copy(update={"restaurant_id": new_id}))

    return final
