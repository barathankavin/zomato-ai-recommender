"""Telemetry — single-line JSON to stderr for observability.

No PII: only counts, latency, token usage, and source labels.
"""

from __future__ import annotations

import json
import sys
import time
from milestone1.phase4_llm.models import RecommendationResult


def emit_telemetry(
    result: RecommendationResult,
    candidate_count: int = 0,
    corpus_size: int = 0,
) -> None:
    """Emit a single-line JSON telemetry event to stderr.

    Fields:
    - timestamp (ISO 8601)
    - source: "llm" | "fallback"
    - result_count: number of ranked results
    - candidate_count: candidates sent to LLM
    - corpus_size: total restaurants in corpus
    - empty_reason: "no_candidates" | "llm_no_picks" | null
    - latency_ms: end-to-end latency
    - token_usage: {prompt_tokens, completion_tokens, total_tokens} | null
    """
    event = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "event": "recommendation",
        "source": result.source,
        "result_count": len(result.rankings),
        "candidate_count": candidate_count,
        "corpus_size": corpus_size,
        "has_results": result.has_results,
        "empty_reason": result.empty_reason,
        "latency_ms": result.latency_ms,
        "token_usage": result.token_usage,
    }

    print(json.dumps(event, separators=(",", ":")), file=sys.stderr)
