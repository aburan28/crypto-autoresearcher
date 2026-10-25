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


@pytest.fixture(autouse=True)
def _no_git_auto_maintenance_in_sealed_repository_fixtures(request, monkeypatch):
    # These tests create and immediately seal temporary Git repositories. The
    # custody checker correctly rejects objects/maintenance.lock, so fixture
    # Git commands must not launch background maintenance between those steps.
    if request.node.path.name != "test_p192_wcm_role2_interface.py":
        return
    for key, value in {
        "GIT_CONFIG_COUNT": "2",
        "GIT_CONFIG_KEY_0": "maintenance.auto",
        "GIT_CONFIG_VALUE_0": "false",
        "GIT_CONFIG_KEY_1": "gc.auto",
        "GIT_CONFIG_VALUE_1": "0",
    }.items():
        monkeypatch.setenv(key, value)


def pytest_collection_modifyitems(items):
    # Execute reviewed, hash-bound successors without modifying frozen tests.
    from tools.ci_test_supersession import apply_supersession
    apply_supersession(items)
