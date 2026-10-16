import asyncio

import pytest

from agents import buyer
from agents.llm import AgentError
from models.schemas import Bundle, BundleRating, BundleRatingSet
from tests.conftest import BRIEF


def _bundle(id_, item_ids, price_cents):
    return Bundle(id=id_, negotiation_id="n", round=1, name=id_, item_ids=item_ids,
                  price_cents=price_cents, rationale="trust me")


def _rating(key, p):
    return BundleRating(bundle_key=key, price_score=0.5, fit_score=0.5, style_score=0.5, probability=p, reason=key)


def test_bundle_facts_flags_sizes_avoid_hits_and_price(items):
    inv = {i.id: i for i in items}
    # itm_002 is the preppy oxford (avoid list), itm_012 only comes in 38/40/42, itm_016 has no sizes
    facts = buyer.bundle_facts(BRIEF, _bundle("b", ["itm_001", "itm_002", "itm_012", "itm_016"], 20000), inv)
    by_id = {i["id"]: i for i in facts["items"]}
    assert by_id["itm_001"]["size_match"] is True
    assert by_id["itm_012"]["size_match"] is False
    assert by_id["itm_016"]["size_match"] is None
    assert by_id["itm_002"]["avoid_hits"] == ["preppy"]
    assert facts["items_missing_buyer_size"] == ["itm_012"]
    assert facts["items_hitting_avoid_list"] == ["itm_002"]
    total = sum(inv[i].price_cents for i in ["itm_001", "itm_002", "itm_012", "itm_016"])
    assert facts["items_total_cents"] == total
    assert facts["price_vs_budget"] == round(20000 / BRIEF.budget_cents, 2)


def test_rate_bundles_maps_keys_back_in_order_and_clamps(items, monkeypatch):
    inv = {i.id: i for i in items}
    bundles = [_bundle("x", ["itm_001"], 4000), _bundle("y", ["itm_002"], 6000)]

    async def fake_structured(system, user, model, effort=None):
        assert '"bundle_key": "B1"' in user and '"bundle_key": "B2"' in user
        # out of order, and one probability out of range
        return BundleRatingSet(ratings=[_rating("B2", 1.7), _rating("B1", 0.8)])

    monkeypatch.setattr(buyer, "structured", fake_structured)
    out = asyncio.run(buyer.rate_bundles(BRIEF, bundles, inv))
    assert [j.reason for j in out] == ["B1", "B2"]
    assert [j.probability for j in out] == [0.8, 1.0]
    assert out[0].style_score == 0.5


def test_rate_bundles_reprompts_on_missing_ratings_then_gives_up(items, monkeypatch):
    inv = {i.id: i for i in items}
    bundles = [_bundle("x", ["itm_001"], 4000), _bundle("y", ["itm_002"], 6000)]
    prompts = []

    async def fake_structured(system, user, model, effort=None):
        prompts.append(user)
        return BundleRatingSet(ratings=[_rating("B1", 0.5), _rating("B9", 0.5)])

    monkeypatch.setattr(buyer, "structured", fake_structured)
    with pytest.raises(AgentError, match="did not rate every bundle"):
        asyncio.run(buyer.rate_bundles(BRIEF, bundles, inv))
    assert len(prompts) == buyer.MAX_RATE_ATTEMPTS
    assert "missing ratings for ['B2']" in prompts[1] and "B9" in prompts[1]
