"""Guardrails on agent output before the middle man accepts it."""

from __future__ import annotations

from typing import Dict, Iterable, List, Optional

from models.schemas import BundleDraft, Item

# Bundle price must land within this band of the sum of its item prices.
MIN_PRICE_RATIO = 0.6
MAX_PRICE_RATIO = 1.05


class ValidationFailed(Exception):
    def __init__(self, errors: List[str]):
        super().__init__("; ".join(errors))
        self.errors = errors


def validate_bundles(
    drafts: List[BundleDraft],
    inventory: Dict[str, Item],
    min_count: int,
    max_count: int,
    banned_item_ids: Optional[Iterable[str]] = None,
) -> None:
    """Raise ValidationFailed listing every problem with a seller's bundle set."""
    errors: List[str] = []
    banned = set(banned_item_ids or ())

    if not (min_count <= len(drafts) <= max_count):
        errors.append(f"expected {min_count}-{max_count} bundles, got {len(drafts)}")

    for i, d in enumerate(drafts):
        label = f"bundle {i + 1} ({d.name!r})"
        if not d.item_ids:
            errors.append(f"{label}: has no items")
            continue
        if len(set(d.item_ids)) != len(d.item_ids):
            errors.append(f"{label}: repeats an item")
        unknown = [x for x in d.item_ids if x not in inventory]
        if unknown:
            errors.append(f"{label}: unknown item ids {unknown}")
            continue
        out_of_stock = [x for x in d.item_ids if not inventory[x].in_stock]
        if out_of_stock:
            errors.append(f"{label}: out-of-stock item ids {out_of_stock}")
        used_banned = [x for x in d.item_ids if x in banned]
        if used_banned:
            errors.append(f"{label}: includes cold items the buyer rejected {used_banned}")
        total = sum(inventory[x].price_cents for x in d.item_ids)
        lo, hi = int(total * MIN_PRICE_RATIO), int(total * MAX_PRICE_RATIO)
        if not (lo <= d.price_cents <= hi):
            errors.append(
                f"{label}: price {d.price_cents} outside allowed range {lo}-{hi} "
                f"(item total {total})"
            )

    if errors:
        raise ValidationFailed(errors)


def clamp_probability(p: float) -> float:
    return max(0.0, min(1.0, float(p)))
