"""Shared Claude client plus a helper that returns Pydantic-validated structured output."""

from __future__ import annotations

import os
from typing import Optional, Type, TypeVar

import anthropic
from pydantic import BaseModel

MODEL = os.environ.get("BROJANS_MODEL", "claude-opus-5-5")
EFFORT = os.environ.get("BROJANS_EFFORT", "medium")

T = TypeVar("T", bound=BaseModel)

_client: Optional[anthropic.AsyncAnthropic] = None


class AgentError(Exception):
    """The model refused, or returned nothing parseable."""


def client() -> anthropic.AsyncAnthropic:
    global _client
    if _client is None:
        _client = anthropic.AsyncAnthropic(max_retries=3)
    return _client


async def structured(system: str, user: str, output_model: Type[T], effort: str = EFFORT) -> T:
    response = await client().messages.parse(
        model=MODEL,
        max_tokens=16000,
        system=system,
        messages=[{"role": "user", "content": user}],
        output_format=output_model,
        output_config={"effort": effort},
        # Server-side refusal fallback: a declined request is re-run on Anthropic's
        # recommended fallback model inside the same call.
        extra_headers={"anthropic-beta": "server-side-fallback-2026-07-01"},
        extra_body={"fallbacks": "default"},
    )
    if response.stop_reason == "refusal":
        raise AgentError("model declined the request")
    if response.stop_reason == "max_tokens":
        raise AgentError("model output was truncated (max_tokens)")
    if response.parsed_output is None:
        raise AgentError("model returned no structured output")
    return response.parsed_output
