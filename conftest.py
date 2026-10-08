"""Session-wide test fixtures.

The inference configuration can be shaped by an operator-local bindings
overlay (`orchestration/model-bindings.local.yaml`, see
`orchestration.adapter.config.overlay_path`). A developer who has one would
otherwise see tests that pin "openrouter ships unbound" fail on their machine
and pass in CI, which is the kind of disagreement nobody debugs quickly. The
suite therefore runs with the overlay disabled; a test that wants one passes
`bindings_overlay=` to `config.load` explicitly.
"""
from __future__ import annotations

import os

import pytest

from orchestration.adapter import config as config_module


@pytest.fixture(autouse=True, scope="session")
def _no_bindings_overlay():
    previous = os.environ.get(config_module.BINDINGS_OVERLAY_ENV)
    os.environ[config_module.BINDINGS_OVERLAY_ENV] = ""
    try:
        yield
    finally:
        if previous is None:
            os.environ.pop(config_module.BINDINGS_OVERLAY_ENV, None)
        else:
            os.environ[config_module.BINDINGS_OVERLAY_ENV] = previous
