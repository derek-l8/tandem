"""Shared data shapes for the middle man, the buyer agent and the seller agent."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Step(str, Enum):
    """Negotiation state machine. Each step is resumable from the DB."""

    BRIEF = "BRIEF"
    R1_PROPOSE = "R1_PROPOSE"
    R1_JUDGE = "R1_JUDGE"
    R2_REFINE = "R2_REFINE"
    R2_JUDGE = "R2_JUDGE"
    FINAL = "FINAL"
    DONE = "DONE"


class Status(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


class HeatLabel(str, Enum):
    HOT = "hot"
    NEUTRAL = "neutral"
    COLD = "cold"


class Item(BaseModel):
    """One piece of seller inventory, with the AI-generated tags."""

    id: str
    name: str
    category: str
    price_cents: int
    tags: Dict[str, Any] = Field(default_factory=dict)
    in_stock: bool = True


# ---- LLM output shapes (kept constraint-free so they work as structured-output schemas;
# ---- range checks live in middleman/validation.py) ----


class BuyerBrief(BaseModel):
    summary: str
    style_keywords: List[str]
    must_haves: List[str]
    avoid: List[str]
    sizes: List[str]
    budget_cents: Optional[int] = None


class BundleDraft(BaseModel):
    name: str
    item_ids: List[str]
    price_cents: int
    rationale: str


class BundleSet(BaseModel):
    bundles: List[BundleDraft]


class JudgmentDraft(BaseModel):
    probability: float
    reason: str
    # Sub-scores (0-1) behind the probability. Optional so older rows still load.
    price_score: Optional[float] = None
    fit_score: Optional[float] = None
    style_score: Optional[float] = None


class BundleRating(BaseModel):
    """The buyer agent's rating of one bundle, keyed by the label it was shown (B1, B2, ...)."""

    bundle_key: str
    price_score: float
    fit_score: float
    style_score: float
    probability: float
    reason: str


class BundleRatingSet(BaseModel):
    ratings: List[BundleRating]


# ---- Persisted records ----


class Bundle(BundleDraft):
    id: str
    negotiation_id: str
    round: int


class Judgment(JudgmentDraft):
    bundle_id: str
    negotiation_id: str
    round: int


class ItemHeat(BaseModel):
    item_id: str
    score: float
    label: HeatLabel
    bundle_count: int


class Negotiation(BaseModel):
    id: str
    buyer_input: str
    brief: Optional[BuyerBrief] = None
    status: Status = Status.PENDING
    step: Step = Step.BRIEF
    error: Optional[str] = None


class Event(BaseModel):
    id: int
    negotiation_id: str
    type: str
    payload: Dict[str, Any]
    ts: datetime


class RoundFeedback(BaseModel):
    """What the middle man hands the seller after a judging round."""

    round: int
    bundles: List[Bundle]
    judgments: List[Judgment]
    heat: List[ItemHeat]
