from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


LOCATOR = load("orbit_quotient_receipt_locator", ROOT / "src" / "orbit_quotient_locator.py")


def test_orbit_class_key_is_negation_invariant():
    assert LOCATOR.class_key((7, 3)) == LOCATOR.class_key((7, -3))
    assert LOCATOR.class_key(None) is None


def test_budget_is_class_bounded():
    assert LOCATOR.parse_budget("full", 5) == 5
    assert LOCATOR.parse_budget("8", 5) == 5
    assert LOCATOR.parse_budget("4", 5) == 4


def test_predicate_zero_requires_exact_target_over_nonsquare():
    ops = LOCATOR.zero_ops()
    assert LOCATOR.predicate((3, 4), (3, 4), 101, LOCATOR.ORACLE.nonsquare(101), ops) == 0
    assert LOCATOR.predicate((3, 5), (3, 4), 101, LOCATOR.ORACLE.nonsquare(101), ops) != 0
