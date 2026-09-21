from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "run_projective_16bit_harness.py"
spec = importlib.util.spec_from_file_location("projective_16bit_test_runner", SOURCE)
assert spec and spec.loader
MODULE = importlib.util.module_from_spec(spec)
spec.loader.exec_module(MODULE)


def test_registered_inversion_weights_are_monotone():
    vector = {"field_multiplications": 100, "field_inversions": 3}
    values = [MODULE.weighted_cost(vector, weight) for weight in MODULE.INVERSION_WEIGHTS]
    assert values == sorted(values)


def test_16bit_scope_is_fresh_and_has_a_negative_control():
    assert MODULE.FIELD_BITS == 16
    assert len(MODULE.FRESH_SEEDS) == 2
    assert MODULE.FAMILIES == ["source_prf_x", "random_x"]
