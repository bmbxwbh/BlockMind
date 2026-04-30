"""Token usage tracking for AI providers."""

import logging
import time
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger("blockmind.ai.token_tracker")


@dataclass
class UsageInfo:
    """Per-call token usage info."""
    tokens_in: int = 0
    tokens_out: int = 0
    model: str = ""
    provider: str = ""
    timestamp: float = field(default_factory=time.time)


class ChatResult(str):
    """String subclass that also carries usage info.

    Backward-compatible: existing code using the result as a plain str
    works unchanged, but new code can access .usage for stats.
    """

    def __new__(cls, text: str, usage: Optional[UsageInfo] = None):
        instance = super().__new__(cls, text)
        instance.usage = usage or UsageInfo()
        return instance


# ── Per-model cost estimates (USD per 1M tokens) ──

_COST_TABLE = {
    # OpenAI models
    "gpt-4o":           {"in": 2.50,  "out": 10.00},
    "gpt-4o-mini":      {"in": 0.15,  "out": 0.60},
    "gpt-4-turbo":      {"in": 10.00, "out": 30.00},
    "gpt-4":            {"in": 30.00, "out": 60.00},
    "gpt-3.5-turbo":    {"in": 0.50,  "out": 1.50},
    "o1":               {"in": 15.00, "out": 60.00},
    "o1-mini":          {"in": 3.00,  "out": 12.00},
    "o3-mini":          {"in": 1.10,  "out": 4.40},
    # Anthropic models
    "claude-3-5-sonnet-20241022": {"in": 3.00,  "out": 15.00},
    "claude-3-5-sonnet-latest":   {"in": 3.00,  "out": 15.00},
    "claude-3-opus-20240229":     {"in": 15.00, "out": 75.00},
    "claude-3-haiku-20240307":    {"in": 0.25,  "out": 1.25},
    "claude-sonnet-4-20250514":   {"in": 3.00,  "out": 15.00},
    "claude-opus-4-20250514":     {"in": 15.00, "out": 75.00},
}


def _estimate_cost(model: str, tokens_in: int, tokens_out: int) -> float:
    """Estimate cost in USD for a single call."""
    # Try exact match, then prefix match
    rates = _COST_TABLE.get(model)
    if not rates:
        # Try prefix match (e.g. "gpt-4o-2024-08-06" → "gpt-4o")
        for prefix, r in _COST_TABLE.items():
            if model.startswith(prefix):
                rates = r
                break
    if not rates:
        return 0.0
    return (tokens_in * rates["in"] + tokens_out * rates["out"]) / 1_000_000


class TokenTracker:
    """Aggregates token usage statistics across all providers.

    Thread-safe for the async use-case (single event loop).
    """

    def __init__(self) -> None:
        self.total_tokens_in: int = 0
        self.total_tokens_out: int = 0
        self.calls_count: int = 0
        self.cost_estimate: float = 0.0
        # Per-provider breakdown
        self._per_provider: dict[str, dict] = {}
        # Per-model breakdown
        self._per_model: dict[str, dict] = {}

    def record(self, usage: UsageInfo) -> None:
        """Record a single API call's usage."""
        self.total_tokens_in += usage.tokens_in
        self.total_tokens_out += usage.tokens_out
        self.calls_count += 1
        cost = _estimate_cost(usage.model, usage.tokens_in, usage.tokens_out)
        self.cost_estimate += cost

        # Per-provider
        pp = self._per_provider.setdefault(
            usage.provider,
            {"tokens_in": 0, "tokens_out": 0, "calls": 0, "cost": 0.0},
        )
        pp["tokens_in"] += usage.tokens_in
        pp["tokens_out"] += usage.tokens_out
        pp["calls"] += 1
        pp["cost"] += cost

        # Per-model
        pm = self._per_model.setdefault(
            usage.model,
            {"tokens_in": 0, "tokens_out": 0, "calls": 0, "cost": 0.0},
        )
        pm["tokens_in"] += usage.tokens_in
        pm["tokens_out"] += usage.tokens_out
        pm["calls"] += 1
        pm["cost"] += cost

        logger.debug(
            "Token usage: %s/%s — in=%d out=%d cost=$%.4f (total: in=%d out=%d calls=%d cost=$%.4f)",
            usage.provider, usage.model,
            usage.tokens_in, usage.tokens_out, cost,
            self.total_tokens_in, self.total_tokens_out,
            self.calls_count, self.cost_estimate,
        )

    def get_stats(self) -> dict:
        """Return a snapshot of all stats."""
        return {
            "total_tokens_in": self.total_tokens_in,
            "total_tokens_out": self.total_tokens_out,
            "calls_count": self.calls_count,
            "cost_estimate": round(self.cost_estimate, 6),
            "per_provider": {
                k: {**v, "cost": round(v["cost"], 6)}
                for k, v in self._per_provider.items()
            },
            "per_model": {
                k: {**v, "cost": round(v["cost"], 6)}
                for k, v in self._per_model.items()
            },
        }

    def reset(self) -> None:
        """Reset all counters."""
        self.total_tokens_in = 0
        self.total_tokens_out = 0
        self.calls_count = 0
        self.cost_estimate = 0.0
        self._per_provider.clear()
        self._per_model.clear()
