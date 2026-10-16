"""Seller agent: assembles bundles from inventory and refines them using buyer feedback."""

from __future__ import annotations

import json
from typing import List, Optional, Sequence

from agents.llm import structured
from models.schemas import BundleDraft, BundleSet, BuyerBrief, HeatLabel, Item, RoundFeedback

SYSTEM = """You are the seller's merchandising agent for Brojans, a clothing marketplace.
You build outfit bundles from the seller's inventory for one specific buyer and price them.

Rules:
- Only use item ids that appear in the inventory, and only in-stock items.
- Never repeat an item within a bundle.
- Price each bundle in cents, between 60% and 105% of the sum of its item prices. A modest
  bundle discount helps conversion. Do not give away margin unnecessarily.
- Make bundles meaningfully different from one another so the buyer's reactions are informative.
- `rationale` is your short pitch to the buyer for that bundle."""


def _inventory_block(inventory: Sequence[Item]) -> str:
    rows = [i.model_dump() for i in inventory if i.in_stock]
    return f"<inventory>\n{json.dumps(rows, indent=1)}\n</inventory>"


def _feedback_block(feedback: Sequence[RoundFeedback]) -> str:
    rounds = []
    for fb in feedback:
        prob = {j.bundle_id: j for j in fb.judgments}
        rounds.append({
            "round": fb.round,
            "bundles": [
                {
                    "name": b.name,
                    "item_ids": b.item_ids,
                    "price_cents": b.price_cents,
                    "buy_probability": prob[b.id].probability if b.id in prob else None,
                    "buyer_reason": prob[b.id].reason if b.id in prob else None,
                }
                for b in fb.bundles
            ],
            "hot_items": [h.model_dump() for h in fb.heat if h.label == HeatLabel.HOT],
            "cold_items": [h.model_dump() for h in fb.heat if h.label == HeatLabel.COLD],
        })
    return f"<buyer_feedback>\n{json.dumps(rounds, indent=1)}\n</buyer_feedback>"


def _retry_block(errors: Optional[List[str]]) -> str:
    if not errors:
        return ""
    joined = "\n".join(f"- {e}" for e in errors)
    return f"\n\nYour previous answer was rejected for these reasons. Fix all of them:\n{joined}"


def _brief_block(brief: BuyerBrief) -> str:
    return f"<buyer_brief>\n{brief.model_dump_json(indent=2)}\n</buyer_brief>"


async def propose_bundles(
    brief: BuyerBrief, inventory: Sequence[Item], count: int, errors: Optional[List[str]] = None
) -> List[BundleDraft]:
    user = (
        f"{_brief_block(brief)}\n\n{_inventory_block(inventory)}\n\n"
        f"Propose exactly {count} distinct bundles for this buyer, each 2-5 items."
        f"{_retry_block(errors)}"
    )
    return (await structured(SYSTEM, user, BundleSet)).bundles


async def refine_bundles(
    brief: BuyerBrief,
    inventory: Sequence[Item],
    feedback: Sequence[RoundFeedback],
    count: int,
    errors: Optional[List[str]] = None,
) -> List[BundleDraft]:
    user = (
        f"{_brief_block(brief)}\n\n{_inventory_block(inventory)}\n\n{_feedback_block(feedback)}\n\n"
        f"The buyer's agent scored your last bundles. Propose exactly {count} new bundles, each 2-5 items. "
        "Build around the hot items, do NOT include any cold items, and use the buyer's reasons to "
        "choose replacements from inventory. Adjust price if the feedback suggests price was the issue."
        f"{_retry_block(errors)}"
    )
    return (await structured(SYSTEM, user, BundleSet)).bundles


async def final_bundle(
    brief: BuyerBrief,
    inventory: Sequence[Item],
    feedback: Sequence[RoundFeedback],
    errors: Optional[List[str]] = None,
) -> List[BundleDraft]:
    """Returns a list so the middle man's validation can enforce that it is exactly one bundle."""
    user = (
        f"{_brief_block(brief)}\n\n{_inventory_block(inventory)}\n\n{_feedback_block(feedback)}\n\n"
        "This is the final offer. Using every round of feedback, propose exactly 1 bundle (2-6 items) "
        "and the price most likely to close the sale. Do NOT include any item marked cold in any round."
        f"{_retry_block(errors)}"
    )
    return (await structured(SYSTEM, user, BundleSet)).bundles
