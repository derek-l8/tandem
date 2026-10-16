import os
import sys
from typing import Dict, List, Optional

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.repo import MemoryRepo, _MemoryStore, load_seed_items  # noqa: E402
from middleman.orchestrator import Agents  # noqa: E402
from models.schemas import Bundle, BundleDraft, BuyerBrief, HeatLabel, Item, JudgmentDraft  # noqa: E402

HOT_ITEM = "itm_001"   # buyer loves this
COLD_ITEM = "itm_002"  # buyer hates this

BRIEF = BuyerBrief(
    summary="Streetwear, minimal, hates preppy",
    style_keywords=["streetwear", "minimal"],
    must_haves=["tee"],
    avoid=["preppy"],
    sizes=["M", "32", "10"],
    budget_cents=40000,
)


def draft(name: str, ids: List[str], inventory: Dict[str, Item]) -> BundleDraft:
    total = sum(inventory[i].price_cents for i in ids)
    return BundleDraft(name=name, item_ids=ids, price_cents=int(total * 0.9), rationale=f"pitch for {name}")


class FakeAgents(Agents):
    """Deterministic agents. `fail_on` makes a method raise once; `bad_first` returns invalid output once."""

    def __init__(self, inventory: List[Item], fail_on: Optional[str] = None, bad_first: Optional[str] = None):
        self.inv = {i.id: i for i in inventory}
        self.fail_on, self.bad_first = fail_on, bad_first
        self.calls: Dict[str, int] = {}

    def _tick(self, name: str) -> int:
        self.calls[name] = self.calls.get(name, 0) + 1
        if self.fail_on == name:
            self.fail_on = None
            raise RuntimeError(f"boom in {name}")
        return self.calls[name]

    async def build_brief(self, buyer_input):
        self._tick("build_brief")
        return BRIEF

    async def judge_bundle(self, brief, bundle: Bundle, inventory):
        self._tick("judge_bundle")
        p = 0.5 + (0.4 if HOT_ITEM in bundle.item_ids else 0) - (0.4 if COLD_ITEM in bundle.item_ids else 0)
        return JudgmentDraft(probability=p, reason=f"judged {bundle.name}")

    async def propose_bundles(self, brief, inventory, count, errors=None):
        n = self._tick("propose_bundles")
        if self.bad_first == "propose_bundles" and n == 1:
            return [draft("bad", ["itm_999", "itm_001"], {**self.inv, "itm_999": self.inv["itm_001"]})]
        return [
            draft("street", [HOT_ITEM, "itm_008", "itm_013"], self.inv),
            draft("prep", [COLD_ITEM, "itm_009", "itm_014"], self.inv),
            draft("cozy", ["itm_003", "itm_006", "itm_016"], self.inv),
        ][:count]

    async def refine_bundles(self, brief, inventory, feedback, count, errors=None):
        n = self._tick("refine_bundles")
        cold = {h.item_id for fb in feedback for h in fb.heat if h.label == HeatLabel.COLD}
        if self.bad_first == "refine_bundles" and n == 1:
            # ignores the feedback and keeps a cold item
            return [draft(f"r{k}", [COLD_ITEM, "itm_013"], self.inv) for k in range(count)]
        assert COLD_ITEM in cold
        return [
            draft("street+", [HOT_ITEM, "itm_008", "itm_019"], self.inv),
            draft("street-lite", [HOT_ITEM, "itm_016"], self.inv),
            draft("cozy+", ["itm_004", "itm_006", "itm_013"], self.inv),
        ][:count]

    async def final_bundle(self, brief, inventory, feedback, errors=None):
        self._tick("final_bundle")
        return [draft("final", [HOT_ITEM, "itm_008", "itm_013", "itm_019"], self.inv)]


@pytest.fixture
def items() -> List[Item]:
    return load_seed_items()


@pytest.fixture
def repo(items) -> MemoryRepo:
    r = MemoryRepo(_MemoryStore())
    r.seed_items(items)
    return r
