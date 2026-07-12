"""Thread-safe corpus singleton.

Loads restaurant data once; subsequent calls return the cached list.
Thread-safe via threading.Lock.
"""

from __future__ import annotations

import logging
import threading
from milestone1.phase1_ingestion.models import Restaurant
from milestone1.phase1_ingestion.loader import load_restaurants

logger = logging.getLogger(__name__)

_lock = threading.Lock()
_corpus: list[Restaurant] | None = None


def get_corpus_size() -> int | None:
    """Return cached corpus size without triggering a load."""
    return len(_corpus) if _corpus is not None else None


def get_corpus() -> list[Restaurant]:
    """Get the restaurant corpus, loading it if necessary.

    Thread-safe: only the first caller triggers loading.
    """
    global _corpus

    if _corpus is not None:
        return _corpus

    with _lock:
        # Double-check after acquiring lock
        if _corpus is not None:
            return _corpus

        logger.info("Loading restaurant corpus...")
        _corpus = load_restaurants()
        logger.info("Corpus loaded: %d restaurants", len(_corpus))
        return _corpus


def reset_corpus() -> None:
    """Reset the corpus cache (for testing)."""
    global _corpus
    with _lock:
        _corpus = None
