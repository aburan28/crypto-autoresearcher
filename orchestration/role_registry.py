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


def effort_support(roles_doc: dict[str, Any],
                   runtime: str) -> dict[str, Any] | None:
    """How `runtime` expresses per-agent reasoning effort, or None if it cannot.

    None is a real answer, like `expected_tools` returning None: the runtime
    takes its effort process-level from `orchestration.adapter env` instead, and
    a caller that checks agent files must not invent a field to compare.
    """
    table = roles_doc.get("runtime_reasoning_effort") or {}
    support = table.get(runtime)
    return dict(support) if isinstance(support, dict) else None


def policy_reasoning_effort(policies_doc: dict[str, Any],
                            policy_id: str) -> str:
    """The effort a policy actually REQUESTS per call.

    `model-policies.yaml` keeps two numbers apart on purpose:
    `requires.reasoning_effort` is the floor a backend must support, and
    `reasoning_effort` is what is requested. The floor is the default when the
    request is omitted -- the same rule `orchestration.adapter` applies -- so
    the agent definition and the adapter can never disagree about which of the
    two an agent file is quoting.
    """
    policy = policies_doc["policies"][policy_id]
    requested = policy.get("reasoning_effort")
    if requested is None:
        requested = (policy.get("requires") or {}).get("reasoning_effort")
    if requested is None:
        raise ValueError(
            f"policy {policy_id!r} states neither reasoning_effort nor "
            f"requires.reasoning_effort, so no effort can be bound to an agent")
    return str(requested)


def expected_effort(roles_doc: dict[str, Any], policies_doc: dict[str, Any],
                    role: str, runtime: str) -> str | None:
    """Effort a role's binding on `runtime` must declare, or None if it cannot.

    Derived, never stored twice: role -> default_policy -> requested effort.
    Changing how hard a role thinks is a one-line edit in `model-policies.yaml`,
    and the bindings are then wrong until they are updated, which is the point.
    """
    if effort_support(roles_doc, runtime) is None:
        return None
    return policy_reasoning_effort(
        policies_doc, role_spec(roles_doc, role)["default_policy"])


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


def _read_claude_effort(path: Path) -> Any:
    return parse_frontmatter(path).get("effort")


# Only runtimes listed in `runtime_reasoning_effort` with a field need one.
EFFORT_READERS = {
    "claude_code": _read_claude_effort,
}


def read_declared_effort(runtime: str, path: Path) -> Any:
    """The reasoning effort an agent file declares, or None if it declares none.

    Raises for a runtime the table says can express effort but that has no
    reader: an unread field is an unchecked field, and this checker exists
    precisely so nothing about a role is trusted rather than verified.
    """
    try:
        reader = EFFORT_READERS[runtime]
    except KeyError:
        raise ValueError(
            f"runtime {runtime!r} declares per-agent reasoning effort in "
            f"roles.yaml but has no effort reader; add one to EFFORT_READERS"
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
            problems.extend(_check_variant(roles_doc, role, spec))

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
            if policies_doc is not None:
                problems.extend(
                    _check_effort(roles_doc, policies_doc, role, runtime, path))
    return problems


def _check_effort(roles_doc: dict[str, Any], policies_doc: dict[str, Any],
                  role: str, runtime: str, path: Path) -> list[str]:
    """Compare a binding's declared reasoning effort against its policy."""
    support = effort_support(roles_doc, runtime)
    if support is None:
        return []
    field = support.get("field", "effort")
    levels = list(support.get("levels") or [])
    policy_id = role_spec(roles_doc, role)["default_policy"]
    try:
        wanted = expected_effort(roles_doc, policies_doc, role, runtime)
    except (KeyError, ValueError) as exc:
        # An unresolvable policy is already reported by `_check_policy`; adding
        # a second line for the same cause would only bury it.
        return [] if isinstance(exc, KeyError) else [f"{role}: {exc}"]

    if wanted not in levels:
        return [
            f"{role}/{runtime}: policy {policy_id} requests reasoning effort "
            f"{wanted!r}, which this runtime cannot express (accepts "
            f"{levels}); run the role under a runtime that can, or state an "
            f"expressible effort in model-policies.yaml"]

    try:
        declared = read_declared_effort(runtime, path)
    except ValueError as exc:
        return [f"{role}/{runtime}: {exc}"]

    if declared is None:
        return [
            f"{role}/{runtime}: binding declares no `{field}`, so this "
            f"subagent inherits the session's reasoning effort instead of the "
            f"{wanted!r} its policy {policy_id} asks for"]
    if declared != wanted:
        return [
            f"{role}/{runtime}: binding declares {field}: {declared!r} but "
            f"policy {policy_id} requests {wanted!r}"]
    return []


def _check_variant(roles_doc: dict[str, Any], role: str,
                   spec: dict[str, Any]) -> list[str]:
    """A policy-tier variant may change how hard a role thinks, and nothing else.

    One agent file carries one effort, so a role whose tasks are sometimes
    routed to a different policy needs a second binding to reach that tier at
    all. That second binding is the risk: `variant_of` is otherwise a way to
    mint a role with a familiar name and quietly different authority. The only
    difference a variant may carry is its policy -- and it must carry one, or it
    is a second name for a role that already exists.
    """
    base_role = spec.get("variant_of")
    if base_role is None:
        return []
    base = (roles_doc.get("roles") or {}).get(base_role)
    if base is None:
        return [f"{role}: variant_of names unknown role {base_role!r}"]

    problems: list[str] = []
    if base.get("variant_of"):
        problems.append(
            f"{role}: variant of {base_role}, which is itself a variant; tiers "
            f"hang off a base role, never off each other")
    if spec.get("contract") != base.get("contract"):
        problems.append(
            f"{role}: variant of {base_role} must share its contract "
            f"({base.get('contract')}), not {spec.get('contract')}")
    if spec.get("authority") != base.get("authority"):
        problems.append(
            f"{role}: variant of {base_role} declares different authority; a "
            f"variant may differ only in policy tier")
    if sorted(spec.get("capabilities") or []) != sorted(
            base.get("capabilities") or []):
        problems.append(
            f"{role}: variant of {base_role} declares different capabilities; "
            f"a variant may differ only in policy tier")
    if spec.get("default_policy") == base.get("default_policy"):
        problems.append(
            f"{role}: variant of {base_role} resolves to the same policy "
            f"({base.get('default_policy')}), so it is a duplicate rather than "
            f"a tier")
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
