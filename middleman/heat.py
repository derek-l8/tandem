"""Per-item hot/cold scoring: turns bundle-level buy probabilities into item-level signal."""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Sequence

from models.schemas import Bundle, HeatLabel, ItemHeat, Judgment

HOT_THRESHOLD = 0.6
COLD_THRESHOLD = 0.3


def compute_item_heat(
    bundles: Sequence[Bundle],
    judgments: Sequence[Judgment],
    hot: float = HOT_THRESHOLD,
    cold: float = COLD_THRESHOLD,
) -> List[ItemHeat]:
    """Score each item as the mean buy probability of the bundles that contain it.

    Items are sorted hottest first. Bundles without a judgment are ignored.
    """
    prob_by_bundle: Dict[str, float] = {j.bundle_id: j.probability for j in judgments}
    probs_by_item: Dict[str, List[float]] = defaultdict(list)
    for bundle in bundles:
        p = prob_by_bundle.get(bundle.id)
        if p is None:
            continue
        for item_id in set(bundle.item_ids):
            probs_by_item[item_id].append(p)

    heat = []
    for item_id, probs in probs_by_item.items():
        score = sum(probs) / len(probs)
        if score >= hot:
            label = HeatLabel.HOT
        elif score <= cold:
            label = HeatLabel.COLD
        else:
            label = HeatLabel.NEUTRAL
        heat.append(ItemHeat(item_id=item_id, score=round(score, 4), label=label, bundle_count=len(probs)))
    heat.sort(key=lambda h: (-h.score, h.item_id))
    return heat
