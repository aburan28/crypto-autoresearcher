"""Controls for the independent variable that confounded the first timing run."""
import itertools
import json

import pytest

from tools.ic_target_balanced_benchmark import CONFIG, ROOT, base, check_balance, order_for


def schedule():
    config = json.loads(CONFIG.read_text())
    lock = json.loads((ROOT / config["environment_lock"]).read_text())
    rows = []
    for bits, curve, seed, repetition in itertools.product(
            config["bits"], config["curve_seeds"], config["solver_seeds"], range(3)):
        for position, arm in enumerate(order_for(config, seed, repetition)):
            rows.append(dict(bits=bits, curve_seed=curve, solver_seed=seed, repetition=repetition,
                             arm=arm, order=position, worker_affinity=[min(lock["allowed_affinity"])],
                             environment_sha256=base.digest(lock), load_before=[0, 0, 0], load_after=[0, 0, 0]))
    return dict(config=config, rows=rows, environment_lock=lock, environment_sha256=base.digest(lock))


def test_every_treatment_crosses_every_slot_within_each_exact_target_cell():
    raw = schedule()
    assert check_balance(raw)["arm_cell_groups"] == 54
    assert len({tuple(order_for(raw["config"], seed, r)) for seed, r in
                itertools.product(raw["config"]["solver_seeds"], range(3))}) == 6


def test_original_middle_only_schedule_is_known_false_control():
    raw = schedule()
    for row in raw["rows"]:
        row["order"] = {"reference_a": 0, "fixed_window": 1, "reference_b": 2}[row["arm"]]
    with pytest.raises(ValueError, match="slot"):
        check_balance(raw)


def test_missing_repetition_cannot_claim_crossing():
    raw = schedule()
    raw["rows"].pop()
    with pytest.raises(ValueError, match="crossed"):
        check_balance(raw)
