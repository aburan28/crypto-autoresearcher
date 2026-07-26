#!/usr/bin/env python3
"""Check that every runtime's agent definitions still match orchestration/roles.yaml.

Role authority and tool surface are research-contract facts. When they live in
each runtime's own agent format, they drift: a subagent quietly gains `Bash`, a
review role quietly loses its independence requirement, and nothing fails. This
check makes that drift a build error.

    python3 tools/check_runtime_bindings.py            # verify
    python3 tools/check_runtime_bindings.py --list     # show the resolved table

Exit status 0 = every binding matches, 1 = at least one mismatch.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
ROLES_PATH = REPO / "orchestration" / "roles.yaml"


def load_roles(path: Path = ROLES_PATH) -> dict:
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def expected_tools(roles_doc: dict, role: str, runtime: str) -> list[str] | None:
    """Runtime tool names for a role, or None if the runtime cannot host it."""
    vocabulary = roles_doc["capabilities"]
    tools: list[str] = []
    for capability in roles_doc["roles"][role]["capabilities"]:
        mapping = vocabulary.get(capability, {})
        if runtime not in mapping:
            return None
        tools.extend(mapping[runtime])
    return tools


def parse_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError(f"{path} has no YAML frontmatter")
    _, frontmatter, _ = text.split("---", 2)
    return yaml.safe_load(frontmatter) or {}


def check(roles_doc: dict, policies_doc: dict | None = None) -> list[str]:
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


def _check_policy(role: str, spec: dict, policies_doc: dict) -> list[str]:
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true",
                        help="print the resolved role/runtime table")
    args = parser.parse_args()

    roles_doc = load_roles()
    policies_doc = yaml.safe_load(
        (REPO / "orchestration" / "model-policies.yaml").read_text(encoding="utf-8"))

    if args.list:
        runtimes = sorted({r for cap in roles_doc["capabilities"].values() for r in cap})
        for role, spec in roles_doc["roles"].items():
            print(f"\n{role}  policy={spec['default_policy']}")
            for runtime in runtimes:
                tools = expected_tools(roles_doc, role, runtime)
                binding = (spec.get("runtime_bindings") or {}).get(runtime, "-")
                print(f"  {runtime:<12} {binding:<36} "
                      f"{', '.join(tools) if tools else 'UNSUPPORTED'}")
        return 0

    problems = check(roles_doc, policies_doc)
    if problems:
        print(f"{len(problems)} runtime-binding problem(s):")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    print(f"OK: {len(roles_doc['roles'])} roles consistent with every runtime binding")
    return 0


if __name__ == "__main__":
    sys.exit(main())
