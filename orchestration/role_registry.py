"""Reader and consistency checker for `orchestration/roles.yaml`.

Shared by `tools/check_runtime_bindings.py` (which fails the build on drift)
and the `api_direct` agent runner (which derives a role's tool surface at run
time). One implementation, so the thing CI verifies is the thing that actually
executes.

No LangChain dependency: importing this must stay cheap.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

REPO = Path(__file__).resolve().parents[1]
ROLES_PATH = REPO / "orchestration" / "roles.yaml"
POLICIES_PATH = REPO / "orchestration" / "model-policies.yaml"


def load_roles(path: Path = ROLES_PATH) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_policies(path: Path = POLICIES_PATH) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def role_spec(roles_doc: dict[str, Any], role: str) -> dict[str, Any]:
    try:
        return roles_doc["roles"][role]
    except KeyError:
        raise KeyError(
            f"unknown role {role!r}; roles: "
            f"{', '.join(sorted(roles_doc['roles']))}") from None


def expected_tools(roles_doc: dict[str, Any], role: str,
                   runtime: str) -> list[str] | None:
    """Runtime tool names for a role, or None if the runtime cannot host it.

    None is a real answer, not an error: a runtime without a web capability
    genuinely cannot run a role whose contract depends on the open web, and
    the caller must refuse rather than run a quietly diminished version.
    """
    vocabulary = roles_doc["capabilities"]
    tools: list[str] = []
    for capability in role_spec(roles_doc, role)["capabilities"]:
        mapping = vocabulary.get(capability, {})
        if runtime not in mapping:
            return None
        tools.extend(mapping[runtime])
    return tools


def missing_capabilities(roles_doc: dict[str, Any], role: str,
                         runtime: str) -> list[str]:
    vocabulary = roles_doc["capabilities"]
    return [capability
            for capability in role_spec(roles_doc, role)["capabilities"]
            if runtime not in vocabulary.get(capability, {})]


def parse_frontmatter(path: Path) -> dict[str, Any]:
    text = Path(path).read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError(f"{path} has no YAML frontmatter")
    _, frontmatter, _ = text.split("---", 2)
    return yaml.safe_load(frontmatter) or {}


def check(roles_doc: dict[str, Any],
          policies_doc: dict[str, Any] | None = None) -> list[str]:
    """Every way a runtime binding can disagree with the role contract."""
    problems: list[str] = []
    for role, spec in roles_doc["roles"].items():
        contract = REPO / spec["contract"]
        if not contract.exists():
            problems.append(f"{role}: missing role contract {spec['contract']}")

        if policies_doc is not None:
            problems.extend(_check_policy(role, spec, policies_doc))

        for runtime, binding_path in (spec.get("runtime_bindings") or {}).items():
            path = REPO / binding_path
            if not path.exists():
                problems.append(f"{role}/{runtime}: missing binding file {binding_path}")
                continue
            wanted = expected_tools(roles_doc, role, runtime)
            if wanted is None:
                problems.append(
                    f"{role}/{runtime}: runtime cannot express every capability "
                    f"this role needs, yet a binding file exists")
                continue
            try:
                frontmatter = parse_frontmatter(path)
            except ValueError as exc:
                problems.append(f"{role}/{runtime}: {exc}")
                continue
            if frontmatter.get("name") != role:
                problems.append(
                    f"{role}/{runtime}: binding declares name "
                    f"{frontmatter.get('name')!r}")
            declared = [t.strip() for t in str(frontmatter.get("tools", "")).split(",")
                        if t.strip()]
            if sorted(declared) != sorted(wanted):
                problems.append(
                    f"{role}/{runtime}: tools {declared} do not match the "
                    f"capabilities in roles.yaml, which imply {wanted}")
    return problems


def _check_policy(role: str, spec: dict[str, Any],
                  policies_doc: dict[str, Any]) -> list[str]:
    policies = policies_doc["policies"]
    policy_id = spec.get("default_policy")
    if policy_id not in policies:
        return [f"{role}: default_policy {policy_id!r} is not a canonical policy id"]
    policy = policies[policy_id]
    problems = []
    if spec["authority"].get("independent_of_producer") and not policy.get(
            "independent_session_required"):
        problems.append(
            f"{role}: is an independent review role but its default policy "
            f"{policy_id} does not require an independent session")
    if spec["authority"].get("may_change_official_state") and not policy.get(
            "may_change_official_state"):
        problems.append(
            f"{role}: may change official state but its default policy "
            f"{policy_id} may not")
    if not spec["authority"].get("may_change_official_state") and policy.get(
            "may_change_official_state"):
        problems.append(
            f"{role}: may not change official state but is routed to "
            f"{policy_id}, which is permitted to")
    return problems
