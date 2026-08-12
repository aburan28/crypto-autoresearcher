from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "run_rank_completion_harness.py"
spec = importlib.util.spec_from_file_location("rank_completion_test_runner", SOURCE)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_target_batch_is_expanded_beyond_original_b_plus_one():
    assert 2 * 14 + 1 == 29
    assert module.FRESH_SEEDS == [97531]
    assert module.FAMILIES == ["source_prf_x", "random_x"]


def test_registered_weights_are_explicit():
    assert module.INVERSION_WEIGHTS == [10, 50, 100, 200]
