"""Integration layer output model."""

from __future__ import annotations

from dataclasses import dataclass, field
from milestone1.phase1_ingestion.models import Restaurant


@dataclass(frozen=True)
class IntegrationResult:
    """Output of the integration layer (filter + prompt build).

    If has_candidates is False, the caller should skip the LLM call entirely
    and show the 'no_candidates' empty state.
    """

    has_candidates: bool
    candidates: list[Restaurant] = field(default_factory=list)
    prompt_payload: dict | None = None
    candidate_count: int = 0
