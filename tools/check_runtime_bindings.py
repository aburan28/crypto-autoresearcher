#!/usr/bin/env python3
"""Check that every runtime's agent definitions still match orchestration/roles.yaml.

Role authority and tool surface are research-contract facts. When they live in
each runtime's own agent format, they drift: a subagent quietly gains `Bash`, a
review role quietly loses its independence requirement, and nothing fails. This
check makes that drift a build error.

    python3 tools/check_runtime_bindings.py            # verify
    python3 tools/check_runtime_bindings.py --list     # show the resolved table

The logic lives in `orchestration/role_registry.py`, which the `api_direct`
agent runner uses too -- so what CI verifies is what actually executes.

Exit status 0 = every binding matches, 1 = at least one mismatch.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from orchestration.role_registry import (  # noqa: E402
    ROLES_PATH, check, effort_support, expected_effort, expected_tools,
    load_policies, load_roles, parse_frontmatter, policy_reasoning_effort,
    role_spec)

__all__ = ["ROLES_PATH", "check", "effort_support", "expected_effort",
           "expected_tools", "load_policies", "load_roles",
           "parse_frontmatter", "policy_reasoning_effort", "role_spec"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true",
                        help="print the resolved role/runtime table")
    args = parser.parse_args()

    roles_doc = load_roles()
    policies_doc = load_policies()

    if args.list:
        runtimes = sorted({r for cap in roles_doc["capabilities"].values() for r in cap})
        for role, spec in roles_doc["roles"].items():
            effort = policy_reasoning_effort(policies_doc, spec["default_policy"])
            # A variant is the same role at another policy tier, and which tier
            # a task gets is decided by its `inference.policy`, not by the
            # dispatcher's taste. Print the link so the table answers "which
            # agent runs this task" without a second lookup.
            variant = spec.get("variant_of")
            variant_note = f"  variant_of={variant}" if variant else ""
            print(f"\n{role}  policy={spec['default_policy']}  "
                  f"effort={effort}{variant_note}")
            for runtime in runtimes:
                tools = expected_tools(roles_doc, role, runtime)
                binding = (spec.get("runtime_bindings") or {}).get(runtime, "-")
                # Where the effort above actually comes from at run time: the
                # agent file, or the session `adapter env` launched the runtime
                # with. An operator reading this table is usually deciding where
                # to run a role, and that is the difference that decides it.
                source = ("agent file"
                          if expected_effort(roles_doc, policies_doc, role, runtime)
                          else "session")
                print(f"  {runtime:<12} {binding:<36} "
                      f"effort:{source:<11} "
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
