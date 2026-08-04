from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "compressed_projective_shared_sign_locator.py"
spec = importlib.util.spec_from_file_location("compressed_locator_test_module", SOURCE)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_selector_is_source_only_and_reduces_prefixes():
    selected = module.selected_prefixes(14, 14)
    assert module.PREFIX_FRACTION == 0.5
    assert len(selected) == 1372
    assert len(selected) < 14**3


def test_selector_order_is_deterministic():
    assert module.selected_prefixes(4, 4) == module.selected_prefixes(4, 4)


def test_nested_runner_resolves_compressed_locator():
    assert module.ORBIT.BASE.locate is module.locate


def test_stratified_selectors_are_source_only_and_balanced():
    original = module.SELECTOR
    try:
        module.SELECTOR = "interleaved-diagonal-prefix"
        interleaved = module.selected_prefixes(4, 4)
        module.SELECTOR = "source-hash-ranked-prefix"
        hashed = module.selected_prefixes(4, 4)
        module.SELECTOR = "parity-balanced-prefix"
        balanced = module.selected_prefixes(4, 4)
        assert len(interleaved) == len(hashed) == len(balanced) == 32
        assert interleaved != hashed
        assert balanced != interleaved
    finally:
        module.SELECTOR = original
