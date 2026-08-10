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

    Names are de-duplicated with order preserved: a runtime may map two
    capabilities onto one tool (OpenCode gates writing and editing behind a
    single `edit` permission) without the caller receiving it twice.
    """
    vocabulary = roles_doc["capabilities"]
    tools: list[str] = []
    for capability in effective_capabilities(roles_doc, role, runtime):
        mapping = vocabulary.get(capability, {})
        if runtime not in mapping:
            return None
        for tool in mapping[runtime]:
            if tool not in tools:
                tools.append(tool)
    return tools


def granted_always(roles_doc: dict[str, Any], runtime: str) -> list[str]:
    """Capabilities `runtime` cannot withhold from any role it hosts."""
    return list((roles_doc.get("runtime_grants_always") or {}).get(runtime, []))


def capability_couplings(roles_doc: dict[str, Any],
                         runtime: str) -> list[list[str]]:
    """Capability groups `runtime` cannot separate."""
    couplings = (roles_doc.get("runtime_capability_coupling") or {})
    return [list(group) for group in couplings.get(runtime, [])]


def optional_capabilities(roles_doc: dict[str, Any], role: str) -> list[str]:
    """Capabilities the role uses where available and does without otherwise.

    Distinct from `capabilities`, which are REQUIRED: a runtime that cannot
    express one of those cannot host the role, and `expected_tools` returns
    None so the caller refuses rather than running a diminished agent. That is
    the right answer for the open web and the wrong one for live messaging,
    which every runtime can do durably through `tools/agent_bus.py` anyway.

    Declaring messaging required would have made all five roles unhostable on
    codex_cli and opencode in a single edit.
    """
    return list(role_spec(roles_doc, role).get("optional_capabilities") or [])


def effective_capabilities(roles_doc: dict[str, Any], role: str,
                           runtime: str) -> list[str]:
    """What the role actually holds on this runtime.

    The contract, widened by whatever the runtime cannot withhold: capabilities
    it grants unconditionally, plus the closure of any it cannot separate, plus
    the optional ones this runtime happens to support.
    """
    capabilities = list(role_spec(roles_doc, role)["capabilities"])

    # Optional capabilities join only where the vocabulary maps them for this
    # runtime. Filtering HERE rather than in expected_tools is what keeps an
    # unsupported optional from reading as "this runtime cannot host the role":
    # expected_tools returns None on any capability it cannot map, so an
    # unfiltered optional would refuse the runtime outright.
    vocabulary = roles_doc["capabilities"]
    for capability in optional_capabilities(roles_doc, role):
        if runtime in vocabulary.get(capability, {}):
            capabilities.append(capability)

    def add(capability: str) -> bool:
        if capability in capabilities:
            return False
        capabilities.append(capability)
        return True

    for capability in granted_always(roles_doc, runtime):
        add(capability)

    couplings = capability_couplings(roles_doc, runtime)
    widened = True
    while widened:  # to a fixpoint: one group may trigger another
        widened = False
        for group in couplings:
            if any(capability in capabilities for capability in group):
                widened = any([add(capability) for capability in group]) or widened
    return capabilities


def over_granted(roles_doc: dict[str, Any], role: str,
                 runtime: str) -> list[str]:
    """Capabilities the runtime forces on a role its contract does not ask for.

    Non-empty means the restriction is prompt-level on that runtime rather
    than enforced by the harness. That is a fact to weigh when choosing where
    to run a role, not an error -- so it is reported, never silently dropped.
    """
    # Optional capabilities are contracted too -- the role asked for them, just
    # conditionally. Omitting them here would report every Claude Code role as
    # over-granted on `send_messages`, which is the opposite of the truth.
    contracted = (set(role_spec(roles_doc, role)["capabilities"])
                  | set(optional_capabilities(roles_doc, role)))
    return [capability
            for capability in effective_capabilities(roles_doc, role, runtime)
            if capability not in contracted]


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


# --------------------------------------------------------------------------
# Binding readers
# --------------------------------------------------------------------------
# Each runtime states a role's identity and tool surface in its own format and
# its own vocabulary. Claude Code lists tool names; the Codex CLI has no tool
# list at all and implies the surface from `sandbox_mode` plus a web-search
# toggle; OpenCode states per-tool permissions. A reader turns any of them into
# the same pair -- (declared name, granted tool names) -- so `check` compares
# contract against reality once instead of once per format.

# Codex accepts no arbitrary keys in an agent role file (`deny_unknown_fields`
# upstream), so its surface cannot be declared and must be derived.
_CODEX_WRITE_SANDBOXES = {"workspace-write", "danger-full-access"}

# Permission keys OpenCode uses for the tools in the capability vocabulary.
# `task` is delegation rather than a capability, so it is not compared here.
_OPENCODE_TOOL_KEYS = ("read", "grep", "glob", "list", "edit", "bash",
                       "webfetch", "websearch")


def _read_claude_binding(path: Path) -> tuple[Any, set[str]]:
    frontmatter = parse_frontmatter(path)
    declared = {tool.strip()
                for tool in str(frontmatter.get("tools", "")).split(",")
                if tool.strip()}
    return frontmatter.get("name"), declared


def _read_codex_binding(path: Path) -> tuple[Any, set[str]]:
    import tomllib
    try:
        document = tomllib.loads(Path(path).read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        raise ValueError(f"{path} is not valid TOML: {exc}") from exc

    # Always present: the Codex sandbox restricts what a command may write,
    # never whether commands may run, so `shell` is granted unconditionally.
    granted = {"read", "search", "shell"}
    sandbox = document.get("sandbox_mode", "read-only")
    if sandbox in _CODEX_WRITE_SANDBOXES:
        granted |= {"write", "edit"}
    if (document.get("tools") or {}).get("web_search"):
        granted.add("web")
    return document.get("name"), granted


def _read_opencode_binding(path: Path) -> tuple[Any, set[str]]:
    frontmatter = parse_frontmatter(path)
    permission = frontmatter.get("permission") or {}
    # OpenCode defaults an unlisted tool to permitted, so absence is a grant.
    # A generated binding states every key explicitly; this default matters
    # only for a hand-edited one, where silence must not read as a denial.
    granted = {key for key in _OPENCODE_TOOL_KEYS
               if permission.get(key, "allow") != "deny"}
    # The agent name is the filename; OpenCode frontmatter has no name field.
    return Path(path).stem, granted


BINDING_READERS = {
    "claude_code": _read_claude_binding,
    "codex_cli": _read_codex_binding,
    "opencode": _read_opencode_binding,
}


def read_binding(runtime: str, path: Path) -> tuple[Any, set[str]]:
    try:
        reader = BINDING_READERS[runtime]
    except KeyError:
        raise ValueError(
            f"no binding reader for runtime {runtime!r}; add one to "
            f"BINDING_READERS so its files are checked rather than trusted"
        ) from None
    return reader(Path(path))


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
                declared_name, declared = read_binding(runtime, path)
            except ValueError as exc:
                problems.append(f"{role}/{runtime}: {exc}")
                continue
            if declared_name != role:
                problems.append(
                    f"{role}/{runtime}: binding declares name "
                    f"{declared_name!r}")
            # Set comparison: a runtime may map two capabilities onto one tool,
            # and `wanted` already accounts for whatever the runtime forces on
            # every role it hosts (`runtime_grants_always`).
            if declared != set(wanted):
                missing = sorted(set(wanted) - declared)
                extra = sorted(declared - set(wanted))
                detail = ", ".join(
                    part for part in (
                        f"missing {missing}" if missing else "",
                        f"unexpected {extra}" if extra else "",
                    ) if part)
                problems.append(
                    f"{role}/{runtime}: granted tools do not match the "
                    f"capabilities in roles.yaml, which imply "
                    f"{sorted(wanted)} ({detail})")
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
