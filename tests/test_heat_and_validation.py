import pytest

from middleman.heat import compute_item_heat
from middleman.validation import ValidationFailed, validate_bundles
from models.schemas import Bundle, BundleDraft, HeatLabel, Judgment


def _b(id_, items):
    return Bundle(id=id_, negotiation_id="n", round=1, name=id_, item_ids=items, price_cents=100, rationale="")


def _j(bundle_id, p):
    return Judgment(bundle_id=bundle_id, negotiation_id="n", round=1, probability=p, reason="")


def test_heat_is_mean_probability_of_containing_bundles():
    bundles = [_b("a", ["x", "y"]), _b("b", ["y", "z"]), _b("c", ["w"])]
    judgments = [_j("a", 0.9), _j("b", 0.1), _j("c", 0.5)]
    heat = {h.item_id: h for h in compute_item_heat(bundles, judgments)}
    assert heat["x"].score == pytest.approx(0.9) and heat["x"].label == HeatLabel.HOT
    assert heat["y"].score == pytest.approx(0.5) and heat["y"].label == HeatLabel.NEUTRAL
    assert heat["y"].bundle_count == 2
    assert heat["z"].score == pytest.approx(0.1) and heat["z"].label == HeatLabel.COLD
    assert [h.item_id for h in compute_item_heat(bundles, judgments)][0] == "x"


def test_heat_ignores_unjudged_bundles():
    assert compute_item_heat([_b("a", ["x"])], []) == []


def _draft(ids, price):
    return BundleDraft(name="d", item_ids=ids, price_cents=price, rationale="")


def test_validation_accepts_good_bundle(items):
    inv = {i.id: i for i in items}
    validate_bundles([_draft(["itm_001", "itm_008"], 12000)], inv, 1, 1)  # total 13000


@pytest.mark.parametrize(
    "drafts, banned, fragment",
    [
        ([_draft(["itm_001", "nope"], 4500)], (), "unknown item ids"),
        ([_draft(["itm_001", "itm_001"], 9000)], (), "repeats an item"),
        ([_draft(["itm_001", "itm_008"], 100)], (), "outside allowed range"),
        ([_draft(["itm_001", "itm_008"], 20000)], (), "outside allowed range"),
        ([_draft(["itm_001", "itm_008"], 12000)], ("itm_008",), "cold items"),
        ([_draft([], 0)], (), "no items"),
        ([], (), "expected 1-1 bundles"),
    ],
)
def test_validation_rejects(items, drafts, banned, fragment):
    inv = {i.id: i for i in items}
    with pytest.raises(ValidationFailed) as exc:
        validate_bundles(drafts, inv, 1, 1, banned)
    assert fragment in str(exc.value)
