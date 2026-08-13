"""Offline regression coverage for the OpenCode no-Bedrock policy checker."""
from __future__ import annotations

import pytest

from orchestration import adapter
from tools import check_inference_cost_policy as cost_policy


def _opencode_fixture() -> dict[str, object]:
    return {
        # This required denial-list sentinel is not a selectable target.
        "disabled_providers": ["amazon-bedrock"],
        "model": "openai/gpt-5.6-sol",
        "small_model": "openai/gpt-5.6-mini",
        "agent": {"executor": {"model": "openai/gpt-5.6-sol"}},
        "provider": {"safe-proxy": {"options": {"baseURL": "https://safe.invalid"}}},
    }


def test_checker_allows_required_bedrock_denylist_sentinel():
    cost_policy.check_opencode(adapter.load(), _opencode_fixture())


def test_checker_rejects_nested_provider_endpoint_case_insensitively():
    document = _opencode_fixture()
    providers = document["provider"]
    assert isinstance(providers, dict)
    providers["safe-proxy"] = {
        "options": {"baseURL": "https://Amazon-BeDrOcK.example.invalid/v1"},
    }

    with pytest.raises(SystemExit, match="provider.safe-proxy.options.baseURL"):
        cost_policy.check_opencode(adapter.load(), document)


def test_checker_rejects_nested_provider_model_case_insensitively():
    document = _opencode_fixture()
    providers = document["provider"]
    assert isinstance(providers, dict)
    providers["safe-proxy"] = {"models": ["Amazon-BeDrOcK/us.example-model"]}

    with pytest.raises(SystemExit, match=r"provider.safe-proxy.models\[0\]"):
        cost_policy.check_opencode(adapter.load(), document)
