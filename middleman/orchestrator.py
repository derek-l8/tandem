"""The middle man: drives buyer agent <-> seller agent through three rounds.

BRIEF -> R1_PROPOSE -> R1_JUDGE -> R2_REFINE -> R2_JUDGE -> FINAL -> DONE

Each step reads its inputs from the repo, calls the agents, validates the result, and
finishes with one atomic `repo.commit_step`. A run can therefore stop anywhere
(function timeout, crash, lost lease) and a later run resumes from the saved step.
"""

from __future__ import annotations

import logging
import uuid
from typing import Awaitable, Callable, Dict, List, Optional, Sequence, Set

from agents import buyer, seller
from db.repo import Repo
from middleman.heat import compute_item_heat
from middleman.validation import ValidationFailed, clamp_probability, validate_bundles
from models.schemas import (
    Bundle,
    BundleDraft,
    BuyerBrief,
    HeatLabel,
    Item,
    Judgment,
    JudgmentDraft,
    Negotiation,
    RoundFeedback,
    Status,
    Step,
)

log = logging.getLogger("brojans.middleman")

LEASE_SECONDS = 180
BUNDLES_PER_ROUND = 3
FINAL_ROUND = 3
MAX_ATTEMPTS = 2  # first try + one re-prompt carrying the validation errors


class Agents:
    """The buyer and seller agents the orchestrator calls. Tests swap in a fake."""

    async def build_brief(self, buyer_input: str) -> BuyerBrief:
        return await buyer.build_brief(buyer_input)

    async def rate_bundles(
        self, brief: BuyerBrief, bundles: Sequence[Bundle], inventory: Dict[str, Item]
    ) -> List[JudgmentDraft]:
        return await buyer.rate_bundles(brief, bundles, inventory)

    async def propose_bundles(self, brief, inventory, count, errors=None) -> List[BundleDraft]:
        return await seller.propose_bundles(brief, inventory, count, errors)

    async def refine_bundles(self, brief, inventory, feedback, count, errors=None) -> List[BundleDraft]:
        return await seller.refine_bundles(brief, inventory, feedback, count, errors)

    async def final_bundle(self, brief, inventory, feedback, errors=None) -> List[BundleDraft]:
        return await seller.final_bundle(brief, inventory, feedback, errors)


class LeaseLost(Exception):
    pass


class _Run:
    def __init__(self, repo: Repo, negotiation_id: str, owner: str, agents: Agents):
        self.repo, self.id, self.owner, self.agents = repo, negotiation_id, owner, agents
        self._inventory: Optional[List[Item]] = None

    async def inventory(self) -> List[Item]:
        if self._inventory is None:
            self._inventory = await self.repo.list_items()
        return self._inventory

    async def inventory_by_id(self) -> Dict[str, Item]:
        return {i.id: i for i in await self.inventory()}

    async def commit(self, from_step: Step, to_step: Step, **kwargs) -> None:
        ok = await self.repo.commit_step(self.id, self.owner, from_step, to_step,
                                         lease_seconds=LEASE_SECONDS, **kwargs)
        if not ok:
            raise LeaseLost(f"lost lease or step moved while committing {from_step.value}")

    async def feedback(self, rounds: Sequence[int]) -> List[RoundFeedback]:
        out = []
        for r in rounds:
            out.append(RoundFeedback(
                round=r,
                bundles=await self.repo.list_bundles(self.id, r),
                judgments=await self.repo.list_judgments(self.id, r),
                heat=await self.repo.list_item_heat(self.id, r),
            ))
        return out

    async def validated(
        self,
        produce: Callable[[Optional[List[str]]], Awaitable[List[BundleDraft]]],
        count: int,
        banned: Set[str],
    ) -> List[BundleDraft]:
        inventory = await self.inventory_by_id()
        errors: Optional[List[str]] = None
        for attempt in range(MAX_ATTEMPTS):
            drafts = await produce(errors)
            try:
                validate_bundles(drafts, inventory, count, count, banned)
                return drafts
            except ValidationFailed as e:
                log.warning("negotiation %s: seller output rejected (attempt %d): %s", self.id, attempt + 1, e)
                errors = e.errors
        raise ValidationFailed(errors or ["seller output invalid"])

    def to_bundles(self, drafts: Sequence[BundleDraft], round_: int) -> List[Bundle]:
        return [Bundle(id=str(uuid.uuid4()), negotiation_id=self.id, round=round_, **d.model_dump())
                for d in drafts]

    # ---------------------------------------------------------------- steps

    async def step_brief(self, neg: Negotiation) -> None:
        brief = await self.agents.build_brief(neg.buyer_input)
        await self.commit(Step.BRIEF, Step.R1_PROPOSE, brief=brief, events=[("brief", brief.model_dump())])

    async def step_propose(self, neg: Negotiation) -> None:
        inv = await self.inventory()
        drafts = await self.validated(
            lambda errs: self.agents.propose_bundles(neg.brief, inv, BUNDLES_PER_ROUND, errs),
            BUNDLES_PER_ROUND, banned=set(),
        )
        bundles = self.to_bundles(drafts, 1)
        await self.commit(Step.R1_PROPOSE, Step.R1_JUDGE, bundles=bundles,
                          events=[("bundles_proposed", _round_payload(1, bundles))])

    async def step_judge(self, neg: Negotiation, round_: int, from_step: Step, to_step: Step) -> None:
        bundles = await self.repo.list_bundles(self.id, round_)
        inventory = await self.inventory_by_id()
        drafts = await self.agents.rate_bundles(neg.brief, bundles, inventory)
        if len(drafts) != len(bundles):
            raise ValueError(f"buyer agent returned {len(drafts)} ratings for {len(bundles)} bundles")
        judgments = [
            Judgment(bundle_id=b.id, negotiation_id=self.id, round=round_,
                     **{**d.model_dump(), "probability": clamp_probability(d.probability)})
            for b, d in zip(bundles, drafts)
        ]
        heat = compute_item_heat(bundles, judgments)
        events = [("bundle_judged", j.model_dump()) for j in judgments]
        events.append(("heat", {"round": round_, "items": [h.model_dump(mode="json") for h in heat]}))
        await self.commit(from_step, to_step, judgments=judgments, heat_round=round_, heat=heat, events=events)

    async def step_refine(self, neg: Negotiation) -> None:
        inv = await self.inventory()
        feedback = await self.feedback([1])
        drafts = await self.validated(
            lambda errs: self.agents.refine_bundles(neg.brief, inv, feedback, BUNDLES_PER_ROUND, errs),
            BUNDLES_PER_ROUND, banned=_cold_items(feedback),
        )
        bundles = self.to_bundles(drafts, 2)
        await self.commit(Step.R2_REFINE, Step.R2_JUDGE, bundles=bundles,
                          events=[("bundles_proposed", _round_payload(2, bundles))])

    async def step_final(self, neg: Negotiation) -> None:
        inv = await self.inventory()
        feedback = await self.feedback([1, 2])
        drafts = await self.validated(
            lambda errs: self.agents.final_bundle(neg.brief, inv, feedback, errs),
            1, banned=_cold_items(feedback),
        )
        [bundle] = self.to_bundles(drafts, FINAL_ROUND)
        inventory = await self.inventory_by_id()
        items = [inventory[i] for i in bundle.item_ids]
        items_total = sum(i.price_cents for i in items)
        offer = {
            "bundle": bundle.model_dump(),
            "items": [i.model_dump() for i in items],
            "items_total_cents": items_total,
            "savings_cents": items_total - bundle.price_cents,
        }
        await self.commit(Step.FINAL, Step.DONE, status=Status.DONE, bundles=[bundle],
                          events=[("final_offer", offer), ("done", {})])


def _round_payload(round_: int, bundles: Sequence[Bundle]) -> dict:
    return {"round": round_, "bundles": [b.model_dump() for b in bundles]}


def _cold_items(feedback: Sequence[RoundFeedback]) -> Set[str]:
    return {h.item_id for fb in feedback for h in fb.heat if h.label == HeatLabel.COLD}


async def run_negotiation(repo: Repo, negotiation_id: str, owner: str, agents: Optional[Agents] = None) -> None:
    """Run from the saved step to DONE. The caller must already hold the lease."""
    run = _Run(repo, negotiation_id, owner, agents or Agents())
    try:
        while True:
            neg = await repo.get_negotiation(negotiation_id)
            if neg is None or neg.status in (Status.DONE, Status.FAILED) or neg.step == Step.DONE:
                return
            log.info("negotiation %s: running %s", negotiation_id, neg.step.value)
            if neg.step == Step.BRIEF:
                await run.step_brief(neg)
            elif neg.step == Step.R1_PROPOSE:
                await run.step_propose(neg)
            elif neg.step == Step.R1_JUDGE:
                await run.step_judge(neg, 1, Step.R1_JUDGE, Step.R2_REFINE)
            elif neg.step == Step.R2_REFINE:
                await run.step_refine(neg)
            elif neg.step == Step.R2_JUDGE:
                await run.step_judge(neg, 2, Step.R2_JUDGE, Step.FINAL)
            elif neg.step == Step.FINAL:
                await run.step_final(neg)
    except LeaseLost as e:
        log.warning("negotiation %s: %s", negotiation_id, e)
    except Exception as e:  # noqa: BLE001 - any agent/validation failure ends the run as failed
        log.exception("negotiation %s failed", negotiation_id)
        await repo.mark_failed(negotiation_id, owner, f"{type(e).__name__}: {e}")
    finally:
        await repo.release_lease(negotiation_id, owner)
