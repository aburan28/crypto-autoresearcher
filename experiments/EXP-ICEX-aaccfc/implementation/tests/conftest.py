"""Shared fixtures.

PYTEST_DONT_REWRITE (v4b A-3): this module evaluates frozen fixtures, so assertion
rewriting is disabled and a failing assert reports no compared values."""

import os
import sys
from pathlib import Path

import pytest

IMPL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(IMPL))
sys.dont_write_bytecode = True


@pytest.fixture(scope="session")
def tmp_root():
    """Scratch space on the repository volume (the system volume is nearly full)."""
    base = Path(os.environ.get("TMPDIR", "/Volumes/SSD990/.tmp-agent")) / "icex-aaccfc-tests"
    base.mkdir(parents=True, exist_ok=True)
    return base


@pytest.fixture(scope="session")
def smoke_primary():
    import common
    import pipeline
    fx = common.fixture(16, 21)
    return pipeline.run_primary(fx, common.SMOKE_NS + "|tests", n_descents=2, n_heldout=8, log_fn=lambda *a: None)
