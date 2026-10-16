import asyncio

from middleman.orchestrator import run_negotiation
from models.schemas import Status, Step
from tests.conftest import COLD_ITEM, HOT_ITEM, FakeAgents


def run(coro):
    return asyncio.run(coro)


async def _create_and_run(repo, agents, owner="o1"):
    neg = await repo.create_negotiation("I like streetwear, size M")
    assert await repo.acquire_lease(neg.id, owner, 60)
    await run_negotiation(repo, neg.id, owner, agents)
    return neg.id


def test_full_run_produces_three_rounds_and_final_offer(repo, items):
    agents = FakeAgents(items)

    async def go():
        nid = await _create_and_run(repo, agents)
        neg = await repo.get_negotiation(nid)
        assert neg.status == Status.DONE and neg.step == Step.DONE
        assert len(await repo.list_bundles(nid, 1)) == 3
        assert len(await repo.list_bundles(nid, 2)) == 3
        [final] = await repo.list_bundles(nid, 3)
        assert HOT_ITEM in final.item_ids and COLD_ITEM not in final.item_ids
        assert len(await repo.list_judgments(nid, 1)) == 3
        assert len(await repo.list_judgments(nid, 2)) == 3
        heat1 = {h.item_id: h.label.value for h in await repo.list_item_heat(nid, 1)}
        assert heat1[HOT_ITEM] == "hot" and heat1[COLD_ITEM] == "cold"
        types = [e.type for e in await repo.list_events(nid)]
        assert types == (
            ["brief", "bundles_proposed"] + ["bundle_judged"] * 3 + ["heat", "bundles_proposed"]
            + ["bundle_judged"] * 3 + ["heat", "final_offer", "done"]
        )
        final_offer = (await repo.list_events(nid))[-2].payload
        assert final_offer["savings_cents"] == final_offer["items_total_cents"] - final.price_cents

    run(go())
    assert agents.calls["judge_bundle"] == 6


def test_invalid_seller_output_is_reprompted_with_errors(repo, items):
    agents = FakeAgents(items, bad_first="refine_bundles")
    seen_errors = []
    original = agents.refine_bundles

    async def spy(brief, inventory, feedback, count, errors=None):
        seen_errors.append(errors)
        return await original(brief, inventory, feedback, count, errors)

    agents.refine_bundles = spy

    async def go():
        nid = await _create_and_run(repo, agents)
        assert (await repo.get_negotiation(nid)).status == Status.DONE

    run(go())
    assert seen_errors[0] is None
    assert any("cold items" in e for e in seen_errors[1])


def test_failure_marks_failed_then_retry_resumes_without_redoing_steps(repo, items):
    agents = FakeAgents(items, fail_on="refine_bundles")

    async def go():
        nid = await _create_and_run(repo, agents)
        neg = await repo.get_negotiation(nid)
        assert neg.status == Status.FAILED and neg.step == Step.R2_REFINE
        assert "boom in refine_bundles" in neg.error
        assert (await repo.list_events(nid))[-1].type == "error"

        assert await repo.reset_failed(nid)
        assert await repo.acquire_lease(nid, "o2", 60)
        await run_negotiation(repo, nid, "o2", agents)
        neg = await repo.get_negotiation(nid)
        assert neg.status == Status.DONE
        assert len(await repo.list_bundles(nid, 1)) == 3  # round 1 was not redone

    run(go())
    assert agents.calls["build_brief"] == 1
    assert agents.calls["propose_bundles"] == 1


def test_lease_is_exclusive_and_stale_owner_cannot_commit(repo, items):
    async def go():
        neg = await repo.create_negotiation("hi")
        assert await repo.acquire_lease(neg.id, "a", 60)
        assert not await repo.acquire_lease(neg.id, "b", 60)
        # "b" never got the lease, so its run must not write anything
        await run_negotiation(repo, neg.id, "b", FakeAgents(items))
        assert (await repo.get_negotiation(neg.id)).step == Step.BRIEF
        assert await repo.list_events(neg.id) == []

    run(go())


def test_prebuilt_brief_skips_brief_step(repo, items):
    from tests.conftest import BRIEF

    agents = FakeAgents(items)

    async def go():
        neg = await repo.create_negotiation("from buyer side", BRIEF)
        assert neg.step == Step.R1_PROPOSE
        assert await repo.acquire_lease(neg.id, "o", 60)
        await run_negotiation(repo, neg.id, "o", agents)
        assert (await repo.get_negotiation(neg.id)).status == Status.DONE

    run(go())
    assert "build_brief" not in agents.calls
