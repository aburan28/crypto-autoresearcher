#!/usr/bin/env python3
"""Validate and resolve auditable model-policy runtime metadata."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml


REPO = Path(__file__).resolve().parents[1]
DEFAULT_POLICY_PATH = REPO / "orchestration" / "model-policies.yaml"
CAPABILITY_SCHEMA = "crypto.autoresearch.runtime_capabilities.v1"
RESOLUTION_SCHEMA = "crypto.autoresearch.model_resolution.v2"
RESOLUTION_REQUIRED_FIELDS = (
    "requested_policy",
    "requested_model_id",
    "requested_model_family",
    "requested_reasoning_effort",
    "resolved_model_id",
    "resolved_model_family",
    "resolved_reasoning_effort",
    "available_reasoning_efforts",
    "fallback_used",
    "authorization",
    "adapter_version",
    "independent_session_required",
)


class ModelPolicyError(ValueError):
    """Raised when policy metadata or runtime capabilities are unsafe."""


def _text(value: Any, location: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ModelPolicyError(f"{location} must be nonempty text")
    return value


def _text_list(value: Any, location: str, *, nonempty: bool = True) -> list[str]:
    if (
        not isinstance(value, list)
        or (nonempty and not value)
        or not all(isinstance(item, str) and item.strip() for item in value)
    ):
        qualifier = "nonempty " if nonempty else ""
        raise ModelPolicyError(f"{location} must be a {qualifier}text list")
    if len(value) != len(set(value)):
        raise ModelPolicyError(f"{location} contains duplicates")
    return value


def load_document(path: Path) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        raise ModelPolicyError(f"cannot load {path}: {error}") from error
    if not isinstance(value, dict):
        raise ModelPolicyError(f"{path} must contain an object")
    return value


def validate_catalog(catalog: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(catalog, dict):
        raise ModelPolicyError("model policy catalog must be an object")
    if catalog.get("schema_version") != "2.0":
        raise ModelPolicyError("model policy schema_version must be 2.0")
    reasoning_efforts = catalog.get("reasoning_efforts")
    if not isinstance(reasoning_efforts, dict):
        raise ModelPolicyError("reasoning_efforts must be an object")
    efforts = _text_list(
        reasoning_efforts.get("supported"),
        "reasoning_efforts.supported",
    )
    models = catalog.get("models")
    if not isinstance(models, dict) or not models:
        raise ModelPolicyError("models must be a nonempty object")
    for model_id, model in models.items():
        _text(model_id, "models key")
        if not isinstance(model, dict):
            raise ModelPolicyError(f"models.{model_id} must be an object")
        _text(model.get("family"), f"models.{model_id}.family")
        supported = _text_list(
            model.get("supported_reasoning_efforts"),
            f"models.{model_id}.supported_reasoning_efforts",
        )
        unknown = set(supported) - set(efforts)
        if unknown:
            raise ModelPolicyError(
                f"models.{model_id} has unknown reasoning efforts {sorted(unknown)}"
            )

    policies = catalog.get("policies")
    if not isinstance(policies, dict) or not policies:
        raise ModelPolicyError("policies must be a nonempty object")
    for name, policy in policies.items():
        location = f"policies.{name}"
        if not isinstance(policy, dict):
            raise ModelPolicyError(f"{location} must be an object")
        model_id = _text(policy.get("model_id"), f"{location}.model_id")
        effort = _text(
            policy.get("requested_reasoning_effort"),
            f"{location}.requested_reasoning_effort",
        )
        if model_id not in models:
            raise ModelPolicyError(f"{location}.model_id is unknown")
        family = _text(policy.get("family"), f"{location}.family")
        if family != models[model_id]["family"]:
            raise ModelPolicyError(f"{location}.family does not match {model_id}")
        legacy_effort = _text(
            policy.get("reasoning_effort"), f"{location}.reasoning_effort"
        )
        if legacy_effort != effort:
            raise ModelPolicyError(
                f"{location}.reasoning_effort does not match requested_reasoning_effort"
            )
        if effort not in models[model_id]["supported_reasoning_efforts"]:
            raise ModelPolicyError(
                f"{location} requests unsupported effort {effort!r} for {model_id}"
            )
        alternatives = policy.get("allowed_alternatives", [])
        if not isinstance(alternatives, list):
            raise ModelPolicyError(f"{location}.allowed_alternatives must be a list")
        alternative_ids: list[str] = []
        for index, alternative in enumerate(alternatives):
            alt_location = f"{location}.allowed_alternatives[{index}]"
            if not isinstance(alternative, dict):
                raise ModelPolicyError(f"{alt_location} must be an object")
            alternative_ids.append(_text(alternative.get("id"), f"{alt_location}.id"))
            alt_model = _text(alternative.get("model_id"), f"{alt_location}.model_id")
            alt_effort = _text(
                alternative.get("reasoning_effort"),
                f"{alt_location}.reasoning_effort",
            )
            _text(alternative.get("authorization"), f"{alt_location}.authorization")
            if alt_model not in models:
                raise ModelPolicyError(f"{alt_location}.model_id is unknown")
            if alt_effort not in models[alt_model]["supported_reasoning_efforts"]:
                raise ModelPolicyError(
                    f"{alt_location} uses unsupported effort {alt_effort!r}"
                )
        if len(alternative_ids) != len(set(alternative_ids)):
            raise ModelPolicyError(f"{location}.allowed_alternatives has duplicate IDs")

    resolution = catalog.get("runtime_resolution")
    if not isinstance(resolution, dict) or resolution.get("strict") is not True:
        raise ModelPolicyError("runtime_resolution.strict must be true")
    if not isinstance(
        resolution.get("policy_declared_alternatives_allowed_without_handoff_fallback"),
        bool,
    ):
        raise ModelPolicyError(
            "runtime_resolution policy alternative setting must be boolean"
        )
    return catalog


def load_catalog(path: Path = DEFAULT_POLICY_PATH) -> dict[str, Any]:
    return validate_catalog(load_document(path))


def validate_capabilities(
    capabilities: dict[str, Any], catalog: dict[str, Any]
) -> dict[str, Any]:
    if not isinstance(capabilities, dict):
        raise ModelPolicyError("runtime capabilities must be an object")
    if capabilities.get("schema") != CAPABILITY_SCHEMA:
        raise ModelPolicyError(f"runtime capabilities schema must be {CAPABILITY_SCHEMA}")
    _text(capabilities.get("adapter_version"), "capabilities.adapter_version")
    entries = capabilities.get("models")
    if not isinstance(entries, list) or not entries:
        raise ModelPolicyError("capabilities.models must be a nonempty list")
    seen_bindings: set[tuple[str, str]] = set()
    seen_runtime_ids: set[str] = set()
    for index, entry in enumerate(entries):
        location = f"capabilities.models[{index}]"
        if not isinstance(entry, dict):
            raise ModelPolicyError(f"{location} must be an object")
        model_id = _text(entry.get("model_id"), f"{location}.model_id")
        resolved_model_id = _text(
            entry.get("resolved_model_id"), f"{location}.resolved_model_id"
        )
        available = _text_list(
            entry.get("available_reasoning_efforts"),
            f"{location}.available_reasoning_efforts",
        )
        binding = (model_id, resolved_model_id)
        if binding in seen_bindings:
            raise ModelPolicyError(f"capabilities.models repeats binding {binding}")
        if resolved_model_id in seen_runtime_ids:
            raise ModelPolicyError(
                f"capabilities.models repeats resolved_model_id {resolved_model_id}"
            )
        seen_bindings.add(binding)
        seen_runtime_ids.add(resolved_model_id)
        model = catalog["models"].get(model_id)
        if model is None:
            raise ModelPolicyError(f"{location}.model_id is not in the policy catalog")
        unsupported = set(available) - set(model["supported_reasoning_efforts"])
        if unsupported:
            raise ModelPolicyError(
                f"{location} advertises unsupported efforts {sorted(unsupported)}"
            )
    return capabilities


def validate_handoff_inference(
    inference: Any, catalog: dict[str, Any]
) -> dict[str, Any]:
    if not isinstance(inference, dict):
        raise ModelPolicyError("handoff.inference must be an object")
    policy_name = _text(inference.get("policy"), "handoff.inference.policy")
    if policy_name not in catalog["policies"]:
        raise ModelPolicyError(f"handoff.inference.policy {policy_name!r} is unknown")
    policy = catalog["policies"][policy_name]
    for field in ("fallback_allowed", "independent_session_required"):
        if not isinstance(inference.get(field), bool):
            raise ModelPolicyError(f"handoff.inference.{field} must be boolean")
    requested_model = inference.get("requested_model_id")
    if requested_model is not None:
        _text(requested_model, "handoff.inference.requested_model_id")
        if requested_model not in catalog["models"]:
            raise ModelPolicyError("handoff.inference.requested_model_id is unknown")
        if requested_model != policy["model_id"]:
            raise ModelPolicyError(
                "handoff.inference.requested_model_id cannot override the policy model"
            )
    requested_effort = inference.get("requested_reasoning_effort")
    if requested_effort is not None:
        _text(requested_effort, "handoff.inference.requested_reasoning_effort")
        if requested_effort != policy["requested_reasoning_effort"]:
            raise ModelPolicyError(
                "handoff.inference.requested_reasoning_effort cannot override "
                "the policy effort"
            )
        model_id = requested_model or policy["model_id"]
        if requested_effort not in catalog["models"][model_id]["supported_reasoning_efforts"]:
            raise ModelPolicyError(
                "handoff.inference.requested_reasoning_effort is unsupported "
                f"for {model_id}"
            )
    if inference["fallback_allowed"]:
        _handoff_fallback_contract(inference, catalog)
    return inference


def _handoff_fallback_contract(
    inference: dict[str, Any], catalog: dict[str, Any]
) -> tuple[str, str, str]:
    fallback_model = _text(
        inference.get("fallback_model"), "handoff.inference.fallback_model"
    )
    authorization_ref = _text(
        inference.get("authorization_ref"), "handoff.inference.authorization_ref"
    )
    required = inference.get("required_resolution")
    if not isinstance(required, dict):
        raise ModelPolicyError(
            "handoff.inference.required_resolution must be an object "
            "for task-specific fallback"
        )
    policy_name = inference["policy"]
    if required.get("requested_policy") != policy_name:
        raise ModelPolicyError(
            "handoff.inference.required_resolution.requested_policy "
            "must match handoff.inference.policy"
        )
    if required.get("resolved_model_id") != fallback_model:
        raise ModelPolicyError(
            "handoff.inference.required_resolution.resolved_model_id "
            "must match fallback_model"
        )
    policy = catalog["policies"][policy_name]
    required_requested_effort = required.get("requested_reasoning_effort")
    if (
        required_requested_effort is not None
        and required_requested_effort != policy["requested_reasoning_effort"]
    ):
        raise ModelPolicyError(
            "handoff.inference.required_resolution.requested_reasoning_effort "
            "must match the policy effort"
        )
    effort_values = [
        required[field]
        for field in (
            "resolved_reasoning_effort",
            "available_reasoning_effort",
            "reasoning_effort",
        )
        if required.get(field) is not None
    ]
    if not effort_values:
        raise ModelPolicyError(
            "handoff.inference.required_resolution must name a resolved reasoning effort"
        )
    if any(not isinstance(value, str) or not value.strip() for value in effort_values):
        raise ModelPolicyError(
            "handoff.inference.required_resolution reasoning effort must be nonempty text"
        )
    if len(set(effort_values)) != 1:
        raise ModelPolicyError(
            "handoff.inference.required_resolution reasoning effort fields disagree"
        )
    fallback_effort = effort_values[0]
    if fallback_effort not in catalog["reasoning_efforts"]["supported"]:
        raise ModelPolicyError(
            "handoff.inference.required_resolution reasoning effort is unknown"
        )
    if required.get("fallback_used") is not True:
        raise ModelPolicyError(
            "handoff.inference.required_resolution.fallback_used must be true"
        )
    return fallback_model, fallback_effort, authorization_ref


def _capability_by_model(
    capabilities: dict[str, Any],
) -> dict[str, list[dict[str, Any]]]:
    output: dict[str, list[dict[str, Any]]] = {}
    for entry in capabilities["models"]:
        output.setdefault(entry["model_id"], []).append(entry)
    return output


def _capability_for_effort(
    by_model: dict[str, list[dict[str, Any]]], model_id: str, effort: str
) -> dict[str, Any] | None:
    return next(
        (
            entry
            for entry in by_model.get(model_id, [])
            if effort in entry["available_reasoning_efforts"]
        ),
        None,
    )


def resolve(
    policy_name: str,
    capabilities: dict[str, Any],
    *,
    catalog: dict[str, Any] | None = None,
    handoff_inference: dict[str, Any] | None = None,
) -> dict[str, Any]:
    catalog = load_catalog() if catalog is None else validate_catalog(catalog)
    capabilities = validate_capabilities(capabilities, catalog)
    policy = catalog["policies"].get(policy_name)
    if policy is None:
        raise ModelPolicyError(f"unknown requested policy {policy_name!r}")

    inference = handoff_inference or {
        "policy": policy_name,
        "fallback_allowed": False,
        "independent_session_required": bool(
            policy.get("independent_session_required", False)
        ),
    }
    validate_handoff_inference(inference, catalog)
    if inference["policy"] != policy_name:
        raise ModelPolicyError("handoff policy does not match requested policy")

    requested_model = inference.get("requested_model_id") or policy["model_id"]
    requested_effort = (
        inference.get("requested_reasoning_effort")
        or policy["requested_reasoning_effort"]
    )
    by_model = _capability_by_model(capabilities)
    candidate = None
    chosen_model = requested_model
    chosen_effort = requested_effort
    authorization = {
        "type": "policy_exact",
        "ref": f"orchestration/model-policies.yaml#policies.{policy_name}",
    }
    fallback_used = False

    if inference["fallback_allowed"]:
        fallback_model, fallback_effort, authorization_ref = (
            _handoff_fallback_contract(inference, catalog)
        )
        for model_id, available_entries in by_model.items():
            available = next(
                (
                    entry
                    for entry in available_entries
                    if entry["resolved_model_id"] == fallback_model
                ),
                None,
            )
            if available is not None:
                if fallback_effort not in available["available_reasoning_efforts"]:
                    raise ModelPolicyError(
                        f"required handoff fallback effort {fallback_effort!r} is unavailable"
                    )
                candidate = available
                chosen_model = model_id
                chosen_effort = fallback_effort
                authorization = {
                    "type": "handoff",
                    "ref": authorization_ref,
                }
                fallback_used = True
                break
        if candidate is None:
            raise ModelPolicyError(
                f"required handoff fallback {fallback_model} at {fallback_effort} "
                "is not advertised"
            )
    else:
        candidate = _capability_for_effort(
            by_model, requested_model, requested_effort
        )

    if candidate is None:
        policy_alternatives_allowed = catalog["runtime_resolution"][
            "policy_declared_alternatives_allowed_without_handoff_fallback"
        ]
        if candidate is None and policy_alternatives_allowed:
            for alternative in policy.get("allowed_alternatives", []):
                available = _capability_for_effort(
                    by_model,
                    alternative["model_id"],
                    alternative["reasoning_effort"],
                )
                if available is not None:
                    candidate = available
                    chosen_model = alternative["model_id"]
                    chosen_effort = alternative["reasoning_effort"]
                    authorization = {
                        "type": "policy_declared_alternative",
                        "ref": alternative["authorization"],
                    }
                    fallback_used = True
                    break

        if candidate is None:
            raise ModelPolicyError(
                f"{policy_name} requires {requested_model} at {requested_effort}; "
                "no authorized available resolution exists"
            )

    independent_required = bool(
        policy.get("independent_session_required", False)
        or inference["independent_session_required"]
    )
    return {
        "metadata_schema": RESOLUTION_SCHEMA,
        "requested_policy": policy_name,
        "requested_model_id": requested_model,
        "requested_model_family": catalog["models"][requested_model]["family"],
        "requested_reasoning_effort": requested_effort,
        "resolved_model_id": candidate["resolved_model_id"],
        "resolved_model_family": catalog["models"][chosen_model]["family"],
        "resolved_reasoning_effort": chosen_effort,
        "available_reasoning_efforts": candidate["available_reasoning_efforts"],
        "fallback_used": fallback_used,
        "authorization": authorization,
        "adapter_version": capabilities["adapter_version"],
        "independent_session_required": independent_required,
    }


def validate_resolution_receipt(
    receipt: Any, catalog: dict[str, Any]
) -> dict[str, Any]:
    """Validate the semantic relationships in one v2 resolution receipt."""

    catalog = validate_catalog(catalog)
    if not isinstance(receipt, dict):
        raise ModelPolicyError("run.inference must be an object")
    if receipt.get("metadata_schema") != RESOLUTION_SCHEMA:
        raise ModelPolicyError(
            f"run.inference.metadata_schema must be {RESOLUTION_SCHEMA}"
        )
    for field in RESOLUTION_REQUIRED_FIELDS:
        if field not in receipt:
            raise ModelPolicyError(f"run.inference missing v2 field {field!r}")

    policy_name = _text(receipt.get("requested_policy"), "run.inference.requested_policy")
    policy = catalog["policies"].get(policy_name)
    if policy is None:
        raise ModelPolicyError("run.inference.requested_policy is unknown")
    requested_model = _text(
        receipt.get("requested_model_id"), "run.inference.requested_model_id"
    )
    if requested_model != policy["model_id"]:
        raise ModelPolicyError(
            "run.inference.requested_model_id does not match requested_policy"
        )
    requested_effort = _text(
        receipt.get("requested_reasoning_effort"),
        "run.inference.requested_reasoning_effort",
    )
    if requested_effort != policy["requested_reasoning_effort"]:
        raise ModelPolicyError(
            "run.inference.requested_reasoning_effort does not match requested_policy"
        )
    requested_family = _text(
        receipt.get("requested_model_family"), "run.inference.requested_model_family"
    )
    if requested_family != catalog["models"][requested_model]["family"]:
        raise ModelPolicyError(
            "run.inference.requested_model_family does not match requested_model_id"
        )

    _text(receipt.get("resolved_model_id"), "run.inference.resolved_model_id")
    resolved_family = _text(
        receipt.get("resolved_model_family"), "run.inference.resolved_model_family"
    )
    available = _text_list(
        receipt.get("available_reasoning_efforts"),
        "run.inference.available_reasoning_efforts",
        nonempty=False,
    )
    unknown_efforts = set(available) - set(catalog["reasoning_efforts"]["supported"])
    if unknown_efforts:
        raise ModelPolicyError(
            f"run.inference advertises unknown efforts {sorted(unknown_efforts)}"
        )
    if not isinstance(receipt.get("fallback_used"), bool):
        raise ModelPolicyError("run.inference.fallback_used must be boolean")
    if not isinstance(receipt.get("independent_session_required"), bool):
        raise ModelPolicyError(
            "run.inference.independent_session_required must be boolean"
        )
    if (
        policy.get("independent_session_required", False)
        and receipt["independent_session_required"] is not True
    ):
        raise ModelPolicyError(
            "run.inference cannot disable the policy independent-session requirement"
        )
    _text(receipt.get("adapter_version"), "run.inference.adapter_version")
    authorization = receipt.get("authorization")
    if not isinstance(authorization, dict):
        raise ModelPolicyError("run.inference.authorization must be an object")
    authorization_type = _text(
        authorization.get("type"), "run.inference.authorization.type"
    )
    authorization_ref = _text(
        authorization.get("ref"), "run.inference.authorization.ref"
    )
    if authorization_type not in {
        "policy_exact",
        "policy_declared_alternative",
        "handoff",
        "deterministic_harness",
    }:
        raise ModelPolicyError("run.inference.authorization.type is unknown")

    resolved_effort = receipt.get("resolved_reasoning_effort")
    if authorization_type == "deterministic_harness":
        if (
            receipt["fallback_used"]
            or resolved_family != "none"
            or resolved_effort is not None
            or available
        ):
            raise ModelPolicyError(
                "run.inference deterministic harness receipt has runtime capabilities"
            )
        return receipt

    if not available:
        raise ModelPolicyError(
            "run.inference.available_reasoning_efforts must be nonempty"
        )
    resolved_effort = _text(
        resolved_effort, "run.inference.resolved_reasoning_effort"
    )
    if resolved_effort not in available:
        raise ModelPolicyError(
            "run.inference.resolved_reasoning_effort is not advertised as available"
        )

    if authorization_type == "policy_exact":
        expected_ref = f"orchestration/model-policies.yaml#policies.{policy_name}"
        if receipt["fallback_used"] or authorization_ref != expected_ref:
            raise ModelPolicyError(
                "run.inference exact policy authorization is inconsistent"
            )
        if resolved_family != requested_family or resolved_effort != requested_effort:
            raise ModelPolicyError(
                "run.inference exact policy resolution changes model family or effort"
            )
    elif authorization_type == "policy_declared_alternative":
        if receipt["fallback_used"] is not True:
            raise ModelPolicyError(
                "run.inference policy alternative must set fallback_used true"
            )
        alternatives = [
            alternative
            for alternative in policy.get("allowed_alternatives", [])
            if alternative["authorization"] == authorization_ref
        ]
        if len(alternatives) != 1:
            raise ModelPolicyError(
                "run.inference policy alternative authorization is not declared"
            )
        alternative = alternatives[0]
        expected_family = catalog["models"][alternative["model_id"]]["family"]
        if (
            resolved_family != expected_family
            or resolved_effort != alternative["reasoning_effort"]
        ):
            raise ModelPolicyError(
                "run.inference policy alternative does not match its declaration"
            )
    else:
        if receipt["fallback_used"] is not True:
            raise ModelPolicyError(
                "run.inference handoff fallback must set fallback_used true"
            )
        known_families = {model["family"] for model in catalog["models"].values()}
        if resolved_family not in known_families:
            raise ModelPolicyError(
                "run.inference handoff fallback has an unknown model family"
            )
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("policy", help="requested policy alias")
    parser.add_argument("capabilities", type=Path, help="runtime capability YAML/JSON")
    parser.add_argument(
        "--model-policies", type=Path, default=DEFAULT_POLICY_PATH
    )
    args = parser.parse_args()
    try:
        receipt = resolve(
            args.policy,
            load_document(args.capabilities),
            catalog=load_catalog(args.model_policies),
        )
    except ModelPolicyError as error:
        print(json.dumps({"valid": False, "error": str(error)}, indent=2))
        return 2
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
