"""Checks for the pinned Curve Smash secp256k1 worker challenge."""
import copy
import json
from pathlib import Path

from harness import sixclass_challenge
from harness.sixclass_challenge import make_job, profile
from harness.sixclass_native import verify_first_dp, verify_log


ROOT = Path(__file__).resolve().parents[1]


def test_profile_and_public_challenge_match_curve_smash():
    target = profile()
    job = json.loads((ROOT / "harness/fixtures/curvesmash_secp256k1_challenge.json").read_text())
    curve = job["curve"]
    assert target["id"] == "secp256k1-ecdlp"
    assert curve["p"] == target["field_modulus"]
    assert curve["order"] == target["subgroup_order"]
    assert curve["generator"] == target["generator_P"]
    assert len(curve["target"]["x"]) == len(curve["target"]["y"]) == 64
    assert not verify_log(job, "1")


def test_generator_and_independent_dp_check():
    planted = make_job(0x3039, seed=7, dp_bits=5, max_steps=512)
    assert verify_log(planted, "3039")
    assert not verify_log(planted, "303a")

    job = json.loads((ROOT / "harness/fixtures/curvesmash_secp256k1_challenge.json").read_text())
    result = json.loads((ROOT / "harness/evidence/sixclass-secp256k1-20261024.json").read_text())["result"]
    assert result["log"] is None
    assert verify_first_dp(job, result)
    changed = copy.deepcopy(result)
    changed["first_dp"]["a"] = "1"
    assert not verify_first_dp(job, changed)


def test_scalar_sampling_rejects_out_of_range(monkeypatch):
    order = int(profile()["subgroup_order"], 16)
    draws = iter([order.to_bytes(32, "big"), (1).to_bytes(32, "big")])
    monkeypatch.setattr(sixclass_challenge.secrets, "token_bytes", lambda size: next(draws))
    assert sixclass_challenge.draw_scalar(order) == 1
