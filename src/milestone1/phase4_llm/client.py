"""Groq LLM client via OpenAI-compatible API.

Edge cases handled:
- GROQ_API_KEY missing → returns None (caller falls back)
- 429 rate limit → retry up to 2× with exponential backoff
- Timeout after 30s → returns None
- Non-JSON response → returns None
"""

from __future__ import annotations

import json
import logging
import time
from typing import Optional

from openai import OpenAI, APIError, RateLimitError, APITimeoutError

logger = logging.getLogger(__name__)

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
MAX_RETRIES = 2
TIMEOUT_SECONDS = 30


def create_groq_client(api_key: str) -> OpenAI | None:
    """Create an OpenAI-compatible client for Groq.

    Returns None if api_key is empty.
    """
    if not api_key or api_key == "your_groq_api_key_here":
        return None

    return OpenAI(
        api_key=api_key,
        base_url=GROQ_BASE_URL,
        timeout=TIMEOUT_SECONDS,
    )


def call_groq(
    client: OpenAI,
    model: str,
    system_prompt: str,
    user_message: str,
) -> Optional[dict]:
    """Call Groq LLM and return parsed JSON response.

    Returns:
        Parsed JSON dict on success, None on failure.
    """
    for attempt in range(MAX_RETRIES + 1):
        try:
            start = time.time()
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.3,
                max_tokens=2000,
                response_format={"type": "json_object"},
            )
            elapsed_ms = (time.time() - start) * 1000

            content = response.choices[0].message.content
            if not content:
                logger.warning("Empty response from Groq")
                return None

            # Parse JSON
            try:
                parsed = json.loads(content)
            except json.JSONDecodeError:
                logger.warning("Non-JSON response from Groq: %s", content[:200])
                return None

            # Attach usage metadata
            usage = {}
            if response.usage:
                usage = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                }

            parsed["_meta"] = {
                "latency_ms": round(elapsed_ms, 1),
                "usage": usage,
            }

            return parsed

        except RateLimitError:
            if attempt < MAX_RETRIES:
                wait = 2 ** (attempt + 1)
                logger.warning("Rate limited (429), retrying in %ds...", wait)
                time.sleep(wait)
            else:
                logger.error("Rate limited after %d retries", MAX_RETRIES)
                return None

        except APITimeoutError:
            logger.error("Groq API timeout after %ds", TIMEOUT_SECONDS)
            return None

        except APIError as exc:
            logger.error("Groq API error: %s", exc)
            return None

        except Exception as exc:
            logger.error("Unexpected error calling Groq: %s", exc)
            return None

    return None
