"""Buyer agent: understands what the buyer wants and rates the seller's bundles on their behalf."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Sequence

from agents.llm import AgentError, structured
from models.schemas import Bundle, BundleRatingSet, BuyerBrief, Item, JudgmentDraft

BRIEF_SYSTEM = """You are the buyer's personal shopping agent for Brojans, a clothing marketplace.
Read what the buyer has said (onboarding chat, profile notes, or a free-text request) and
distill it into a shopping brief that a seller can act on. Capture their style and vibe,
what they specifically want, what they dislike, their sizes, and their budget in cents if
they gave one (null otherwise). Do not invent preferences they did not express."""

RATE_SYSTEM = """You are the buyer's personal shopping agent for Brojans. You represent the buyer,
not the seller. A seller has sent several bundles. Rate every one of them for this buyer.

Each bundle comes with `facts` computed from the inventory. Treat them as ground truth:
- `size_match` per item: true = the buyer's size is stocked, false = it is not, null = unknown
  (no sizes on the item, or the buyer gave none).
- `avoid_hits`: things the buyer said to avoid that appear in the item's name or tags.
- `price_vs_budget`: bundle price divided by the buyer's budget (null if no budget).

For each bundle give, all from 0.0 to 1.0:
- price_score: value for money against their budget, including the bundle discount.
- fit_score: their sizes are available and the cuts suit what they described.
- style_score: matches their style and must-haves, avoids what they dislike.
- probability: how likely this buyer is to actually buy this bundle at this price. Be calibrated:
  0.5 is a genuine coin flip. A bundle with an item they cannot get in their size, or with
  something they said to avoid, should rarely be above 0.4. A bundle well over budget should
  be low however good it looks.

Rate each bundle on its own merits; probabilities do not need to sum to 1. Use the other
bundles only to keep your scale consistent. Ignore the seller's pitch where it conflicts with
the facts. In `reason`, name the specific items that help or hurt, in one or two sentences.
Return exactly one rating per bundle, using its `bundle_key`."""

MAX_RATE_ATTEMPTS = 2  # first try + one re-prompt naming missing or unknown bundle keys


def _norm(s: Any) -> str:
    return str(s).strip().lower()


def _flatten_tags(tags: Dict[str, Any]) -> List[str]:
    out: List[str] = []
    for v in tags.values():
        out.extend(_norm(x) for x in (v if isinstance(v, list) else [v]))
    return out


def bundle_facts(brief: BuyerBrief, bundle: Bundle, inventory: Dict[str, Item]) -> Dict[str, Any]:
    """Deterministic facts about a bundle, so the model does not have to count or compare sizes."""
    buyer_sizes = {_norm(s) for s in brief.sizes}
    avoid = [_norm(a) for a in brief.avoid if a.strip()]
    items = []
    for item_id in bundle.item_ids:
        item = inventory.get(item_id)
        if item is None:
            continue
        sizes = item.tags.get("sizes")
        size_match = None
        if sizes and buyer_sizes:
            size_match = bool(buyer_sizes & {_norm(s) for s in sizes})
        haystack = " ".join([_norm(item.name), *_flatten_tags(item.tags)])
        items.append({
            "id": item.id,
            "name": item.name,
            "category": item.category,
            "price_cents": item.price_cents,
            "tags": item.tags,
            "in_stock": item.in_stock,
            "size_match": size_match,
            "avoid_hits": [a for a in avoid if a in haystack],
        })
    items_total = sum(i["price_cents"] for i in items)
    return {
        "items": items,
        "categories": sorted({i["category"] for i in items}),
        "bundle_price_cents": bundle.price_cents,
        "items_total_cents": items_total,
        "discount_pct": round(100 * (1 - bundle.price_cents / items_total), 1) if items_total else 0.0,
        "budget_cents": brief.budget_cents,
        "price_vs_budget": round(bundle.price_cents / brief.budget_cents, 2) if brief.budget_cents else None,
        "items_missing_buyer_size": [i["id"] for i in items if i["size_match"] is False],
        "items_hitting_avoid_list": [i["id"] for i in items if i["avoid_hits"]],
    }


def _clamp(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


async def rate_bundles(
    brief: BuyerBrief, bundles: Sequence[Bundle], inventory: Dict[str, Item]
) -> List[JudgmentDraft]:
    """Rate every bundle the seller sent. Returns one judgment per bundle, in the same order."""
    if not bundles:
        return []
    keyed = {f"B{n}": b for n, b in enumerate(bundles, start=1)}
    payload = [
        {"bundle_key": key, "name": b.name, "seller_pitch": b.rationale, "facts": bundle_facts(brief, b, inventory)}
        for key, b in keyed.items()
    ]
    base = (
        f"<buyer_brief>\n{brief.model_dump_json(indent=2)}\n</buyer_brief>\n\n"
        f"<bundles>\n{json.dumps(payload, indent=1)}\n</bundles>\n\n"
        f"Rate all {len(keyed)} bundles: {', '.join(keyed)}."
    )
    errors: List[str] = []
    for _ in range(MAX_RATE_ATTEMPTS):
        user = base
        if errors:
            user += "\n\nYour previous answer was rejected. Fix this:\n" + "\n".join(f"- {e}" for e in errors)
        result = await structured(RATE_SYSTEM, user, BundleRatingSet, effort="low")
        by_key = {r.bundle_key.strip(): r for r in result.ratings}
        missing = [k for k in keyed if k not in by_key]
        unknown = [k for k in by_key if k not in keyed]
        errors = []
        if missing:
            errors.append(f"missing ratings for {missing}")
        if unknown:
            errors.append(f"unknown bundle keys {unknown}; use only {list(keyed)}")
        if not missing:
            return [
                JudgmentDraft(
                    probability=_clamp(by_key[k].probability),
                    reason=by_key[k].reason,
                    price_score=_clamp(by_key[k].price_score),
                    fit_score=_clamp(by_key[k].fit_score),
                    style_score=_clamp(by_key[k].style_score),
                )
                for k in keyed
            ]
    raise AgentError("buyer agent did not rate every bundle: " + "; ".join(errors))


async def build_brief(buyer_input: str) -> BuyerBrief:
    return await structured(BRIEF_SYSTEM, f"<buyer_input>\n{buyer_input}\n</buyer_input>", BuyerBrief)
