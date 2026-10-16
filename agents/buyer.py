"""Buyer agent: understands what the buyer wants and judges bundles on their behalf."""

from __future__ import annotations

import json
from typing import Dict

from agents.llm import structured
from models.schemas import Bundle, BuyerBrief, Item, JudgmentDraft

BRIEF_SYSTEM = """You are the buyer's personal shopping agent for Brojans, a clothing marketplace.
Read what the buyer has said (onboarding chat, profile notes, or a free-text request) and
distill it into a shopping brief that a seller can act on. Capture their style and vibe,
what they specifically want, what they dislike, their sizes, and their budget in cents if
they gave one (null otherwise). Do not invent preferences they did not express."""

JUDGE_SYSTEM = """You are the buyer's personal shopping agent for Brojans. You represent the buyer,
not the seller. You are shown the buyer's brief and one bundle a seller is offering, with
each item's tags and the bundle price.

Estimate the probability (0.0 to 1.0) that this buyer would actually purchase the bundle at
this price. Be calibrated: 0.5 means a genuine coin flip. Weigh style fit, whether it
covers what they asked for, anything they said to avoid, size availability, and value for
money against their budget. In `reason`, name the specific items that help or hurt."""


async def build_brief(buyer_input: str) -> BuyerBrief:
    return await structured(BRIEF_SYSTEM, f"<buyer_input>\n{buyer_input}\n</buyer_input>", BuyerBrief)


async def judge_bundle(brief: BuyerBrief, bundle: Bundle, inventory: Dict[str, Item]) -> JudgmentDraft:
    items = [inventory[i].model_dump(exclude={"in_stock"}) for i in bundle.item_ids if i in inventory]
    payload = {
        "bundle_name": bundle.name,
        "items": items,
        "bundle_price_cents": bundle.price_cents,
        "items_total_cents": sum(i["price_cents"] for i in items),
        "seller_pitch": bundle.rationale,
    }
    user = (
        f"<buyer_brief>\n{brief.model_dump_json(indent=2)}\n</buyer_brief>\n\n"
        f"<bundle>\n{json.dumps(payload, indent=2)}\n</bundle>"
    )
    return await structured(JUDGE_SYSTEM, user, JudgmentDraft, effort="low")
