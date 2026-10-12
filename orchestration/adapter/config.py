"""Load and validate the three-file inference configuration.

    model-policies.yaml   what a role needs        (vendor-free)
    providers.yaml        where requests go        (endpoints, wire, runtimes)
    model-bindings.yaml   which model serves what  (the only file with ids)

Validation is strict on purpose: a typo in a policy id must fail at load time,
not silently route a review task to whatever binding happened to match.
"""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from orchestration import fast_yaml

ADAPTER_VERSION = "1.2.0"

REPO_ROOT = Path(__file__).resolve().parents[2]
POLICIES_PATH = REPO_ROOT / "orchestration" / "model-policies.yaml"
PROVIDERS_PATH = REPO_ROOT / "orchestration" / "providers.yaml"
BINDINGS_PATH = REPO_ROOT / "orchestration" / "model-bindings.yaml"
# Operator-local bindings, merged over the committed file at load time. This
# is how a backend the repository ships unbound (openrouter) gets model ids on
# one machine without anyone committing an assertion nobody probed: the file
# is gitignored, its entries must say `provenance: operator-supplied`, and
# the merged digest changes so every manifest shows it was in effect.
BINDINGS_OVERLAY_PATH = REPO_ROOT / "orchestration" / "model-bindings.local.yaml"
BINDINGS_OVERLAY_ENV = "AUTORESEARCH_BINDINGS_OVERLAY"

DEFAULT_EFFORT_ORDER = ["none", "low", "medium", "high", "xhigh", "max", "ultra"]

# A binding's ``model`` is the sole authority for an outbound model selector.
# ``request`` is deliberately open for provider-specific tuning knobs, but it
# must not replace transport routing after resolution has already been checked.
REQUEST_TARGET_SELECTOR_FIELDS = frozenset({
    "model", "provider", "backend", "endpoint", "base_url", "url",
})

# Delivery routing between the synchronous Messages API and Message Batches,
# overridable under `defaults.batch` in providers.yaml.
DEFAULT_BATCH_DEFAULTS: dict[str, Any] = {
    "expected_latency_seconds": 3600,
    "max_latency_seconds": 86400,
    "urgent_priority": 90,
    "deadline_slack_seconds": 1800,
    "registry_dir": "coordination/inference-batches",
    "poll_interval_seconds": 60,
}


class ConfigError(ValueError):
    """The inference configuration is malformed or internally inconsistent."""


@dataclass(frozen=True)
class Config:
    policies: dict[str, Any]
    providers: dict[str, Any]
    bindings: dict[str, Any]
    digest: str
    paths: dict[str, str]

    # -- policies ----------------------------------------------------------
    @property
    def policy_table(self) -> dict[str, Any]:
        return self.policies["policies"]

    @property
    def effort_order(self) -> list[str]:
        return list(self.policies.get("adapter", {}).get(
            "reasoning_effort_order", DEFAULT_EFFORT_ORDER))

    def canonical_policy(self, name: str) -> str:
        """Map a policy id or a legacy alias to its canonical id.

        Committed handoffs reference pre-2.0 ids; they must keep resolving
        forever, so aliases are a permanent part of the contract.
        """
        table = self.policy_table
        if name in table:
            return name
        for pid, policy in table.items():
            if name in (policy.get("aliases") or []):
                return pid
        known = sorted(table) + sorted(
            a for p in table.values() for a in (p.get("aliases") or []))
        raise ConfigError(
            f"unknown inference policy {name!r}; known policies and aliases: "
            f"{', '.join(known)}")

    def policy(self, name: str) -> dict[str, Any]:
        return self.policy_table[self.canonical_policy(name)]

    def role_default_policy(self, role: str) -> str:
        defaults = self.policies.get("role_defaults", {})
        key = role.replace("-", "_")
        if key not in defaults:
            raise ConfigError(
                f"no default policy for role {role!r}; roles: "
                f"{', '.join(sorted(defaults))}")
        return defaults[key]

    # -- providers ---------------------------------------------------------
    @property
    def backend_table(self) -> dict[str, Any]:
        return self.providers["backends"]

    @property
    def runtime_table(self) -> dict[str, Any]:
        return self.providers.get("runtimes", {})

    @property
    def forbidden_provider_substrings(self) -> list[str]:
        governance = self.providers.get("governance", {})
        return [str(value).casefold() for value in
                governance.get("forbidden_provider_substrings", [])]

    def assert_inference_target_allowed(self, *values: object,
                                        context: str = "inference target") -> None:
        """Fail before resolution when a cost-prohibited provider is named."""
        for value in values:
            if value is None:
                continue
            normalized = str(value).casefold()
            for token in self.forbidden_provider_substrings:
                if token and token in normalized:
                    reason = (self.providers.get("governance", {}) or {}).get(
                        "reason", "provider is forbidden by repository policy")
                    raise ConfigError(
                        f"{context} {value!r} is forbidden by cost policy "
                        f"(matched {token!r}): {reason}")

    def backend(self, name: str) -> dict[str, Any]:
        self.assert_inference_target_allowed(name, context="backend")
        try:
            return self.backend_table[name]
        except KeyError:
            raise ConfigError(
                f"unknown backend {name!r}; configured backends: "
                f"{', '.join(sorted(self.backend_table))}") from None

    def runtime(self, name: str) -> dict[str, Any]:
        try:
            return self.runtime_table[name]
        except KeyError:
            raise ConfigError(
                f"unknown runtime {name!r}; configured runtimes: "
                f"{', '.join(sorted(self.runtime_table))}") from None

    def wire_protocol(self, name: str) -> dict[str, Any]:
        try:
            return self.providers["wire_protocols"][name]
        except KeyError:
            raise ConfigError(f"unknown wire protocol {name!r}") from None

    def base_url(self, backend_name: str, env: dict[str, str] | None = None) -> str:
        env = os.environ if env is None else env
        backend = self.backend(backend_name)
        override = backend.get("base_url_env")
        if override and env.get(override):
            base_url = env[override].rstrip("/")
        else:
            base_url = str(backend["base_url"]).rstrip("/")
        self.assert_inference_target_allowed(
            base_url, context=f"backend {backend_name} resolved endpoint")
        return base_url

    def default_backend(self, env: dict[str, str] | None = None) -> str:
        env = os.environ if env is None else env
        defaults = self.providers.get("defaults", {})
        var = defaults.get("backend_env")
        if var and env.get(var):
            return env[var]
        return defaults.get("backend", next(iter(self.backend_table)))

    def default_runtime(self, env: dict[str, str] | None = None) -> str:
        env = os.environ if env is None else env
        defaults = self.providers.get("defaults", {})
        var = defaults.get("runtime_env")
        if var and env.get(var):
            return env[var]
        return defaults.get("runtime", "api_direct")

    # -- bindings ----------------------------------------------------------
    @property
    def binding_table(self) -> dict[str, Any]:
        return self.bindings["bindings"]

    def binding(self, backend: str, policy: str) -> dict[str, Any] | None:
        return self.binding_table.get(backend, {}).get(self.canonical_policy(policy))

    def backend_fallback_order(self) -> list[str]:
        return list(self.bindings.get("defaults", {}).get(
            "backend_fallback_order", []))

    # -- message batches ---------------------------------------------------
    def batch_defaults(self) -> dict[str, Any]:
        """Delivery-routing figures from `providers.yaml` `defaults.batch`."""
        defaults = dict(DEFAULT_BATCH_DEFAULTS)
        defaults.update((self.providers.get("defaults") or {}).get("batch") or {})
        return defaults

    def supports_message_batches(self, backend_name: str) -> bool:
        """Whether a backend declares the Message Batches API.

        Speaking the Anthropic wire format does not imply it: the gateways
        that re-serve open-weight models over this protocol do not batch, so
        the capability is opt-in per backend rather than inferred from the
        protocol.
        """
        backend = self.backend(backend_name)
        if not backend.get("supports_message_batches"):
            return False
        return bool(self.wire_protocol(backend["wire"]).get("batches_path"))


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ConfigError(f"missing inference configuration file: {path}")
    with path.open(encoding="utf-8") as handle:
        data = fast_yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ConfigError(f"{path} must contain a YAML mapping")
    return data


def overlay_path(env: dict[str, str] | None = None,
                 override: Path | None = None) -> Path | None:
    """The bindings overlay in effect, or None.

    `AUTORESEARCH_BINDINGS_OVERLAY` wins (an empty value disables the overlay
    outright, which is what a test or a CI job wants); otherwise the local
    file beside the committed bindings is used when it exists.
    """
    if override is not None:
        return override
    env = os.environ if env is None else env
    if BINDINGS_OVERLAY_ENV in env:
        value = env[BINDINGS_OVERLAY_ENV].strip()
        return Path(value).expanduser() if value else None
    return BINDINGS_OVERLAY_PATH if BINDINGS_OVERLAY_PATH.exists() else None


def merge_bindings(base: dict[str, Any], overlay: dict[str, Any],
                   source: str = "overlay") -> dict[str, Any]:
    """Merge an overlay's binding tables over the committed ones.

    One policy entry replaces the committed entry whole -- a half-merged
    binding (the overlay's model with the committed capabilities) would be a
    claim neither file made. An overlay may not relabel what it supplies as
    `runtime-verified`: that word means `doctor --probe` listed the id, and
    a local file cannot attest it. `defaults` are not overridable; the
    fallback order is the repository's contract.
    """
    tables = overlay.get("bindings")
    if not isinstance(tables, dict):
        raise ConfigError(f"{source}: overlay must contain a `bindings` mapping")
    for key in overlay:
        if key not in ("bindings", "schema_version", "notes"):
            raise ConfigError(f"{source}: overlay may set only `bindings` "
                              f"(and `notes`), not {key!r}")
    merged = json.loads(json.dumps(base))
    merged.setdefault("bindings", {})
    for backend_name, table in tables.items():
        if not isinstance(table, dict):
            raise ConfigError(f"{source}: bindings.{backend_name} must be a mapping")
        target = merged["bindings"].setdefault(backend_name, {})
        for policy_id, binding in table.items():
            if not isinstance(binding, dict):
                raise ConfigError(f"{source}: bindings.{backend_name}.{policy_id} "
                                  f"must be a mapping")
            if binding.get("provenance") == "runtime-verified":
                raise ConfigError(
                    f"{source}: bindings.{backend_name}.{policy_id} claims "
                    f"runtime-verified; an overlay can only be operator-supplied "
                    f"(run `adapter doctor --probe` and commit a verified binding "
                    f"instead)")
            target[policy_id] = dict(binding, overlay_source=source)
    return merged


def load(policies_path: Path | None = None,
         providers_path: Path | None = None,
         bindings_path: Path | None = None,
         bindings_overlay: Path | None = None,
         env: dict[str, str] | None = None) -> Config:
    """Load, cross-validate, and digest the configuration.

    `bindings_overlay` (or the file `overlay_path` finds) is merged over the
    committed bindings before validation, and recorded in `paths` so a
    manifest can say which local file shaped the resolution.
    """
    paths = {
        "policies": policies_path or POLICIES_PATH,
        "providers": providers_path or PROVIDERS_PATH,
        "bindings": bindings_path or BINDINGS_PATH,
    }
    docs = {name: _load_yaml(path) for name, path in paths.items()}
    overlay = overlay_path(env, bindings_overlay)
    if overlay is not None:
        docs["bindings"] = merge_bindings(docs["bindings"], _load_yaml(overlay),
                                          source=str(overlay))
        paths["bindings_overlay"] = overlay
    config = Config(
        policies=docs["policies"],
        providers=docs["providers"],
        bindings=docs["bindings"],
        digest=_digest(docs),
        paths={name: str(path) for name, path in paths.items()},
    )
    validate(config)
    return config


def _digest(docs: dict[str, Any]) -> str:
    blob = json.dumps(docs, sort_keys=True, default=str).encode("utf-8")
    return "sha256:" + hashlib.sha256(blob).hexdigest()[:32]


def _scalar_values(value: Any):
    """Yield scalar config values without treating mappings as string blobs."""
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from _scalar_values(child)
    elif isinstance(value, (list, tuple, set)):
        for child in value:
            yield from _scalar_values(child)
    else:
        yield value


def _validate_wire_path(config: Config, wire_name: str, field: str,
                        value: Any) -> None:
    """Require a target-checked, slash-prefixed relative wire path.

    The transport concatenates this value to the guarded backend base URL.
    A relative path requirement prevents a configuration value such as
    ``@host`` or ``//host`` from changing the final request authority after
    that base URL check has completed.
    """
    if not isinstance(value, str) or not value:
        raise ConfigError(
            f"wire protocol {wire_name} is missing a non-empty `{field}` path")
    config.assert_inference_target_allowed(
        value, context=f"wire protocol {wire_name} {field}")
    parsed = urlsplit(value)
    if (not value.startswith("/") or value.startswith("//") or
            parsed.scheme or parsed.netloc or parsed.query or parsed.fragment):
        raise ConfigError(
            f"wire protocol {wire_name} {field} must be a slash-prefixed "
            "relative path without an authority, query, or fragment")


def validate(config: Config) -> None:
    """Fail loudly on anything that could mis-route a task."""
    for section, doc in (("policies", config.policies),
                         ("providers", config.providers),
                         ("bindings", config.bindings)):
        if "schema_version" not in doc:
            raise ConfigError(f"{section} file has no schema_version")

    policies = config.policies.get("policies")
    if not isinstance(policies, dict) or not policies:
        raise ConfigError("model-policies.yaml declares no policies")

    order = config.effort_order
    seen_aliases: dict[str, str] = {}
    for pid, policy in policies.items():
        requires = policy.get("requires")
        if not isinstance(requires, dict):
            raise ConfigError(f"policy {pid} has no `requires` block")
        effort = requires.get("reasoning_effort")
        if effort not in order:
            raise ConfigError(
                f"policy {pid} requires unknown reasoning effort {effort!r}; "
                f"lattice is {order}")
        fallback = policy.get("fallback_policy")
        if fallback and fallback not in policies:
            raise ConfigError(
                f"policy {pid} declares fallback_policy {fallback!r}, which is "
                f"not a policy id")
        if not isinstance(policy.get("degradable", True), bool):
            raise ConfigError(f"policy {pid}: degradable must be true or false")
        for alias in policy.get("aliases") or []:
            if alias in policies:
                raise ConfigError(
                    f"alias {alias!r} on {pid} collides with a policy id")
            if alias in seen_aliases:
                raise ConfigError(
                    f"alias {alias!r} is claimed by both {seen_aliases[alias]} "
                    f"and {pid}; aliases are permanent and single-owner")
            seen_aliases[alias] = pid

    for role, policy_id in (config.policies.get("role_defaults") or {}).items():
        config.canonical_policy(policy_id)  # raises on typo

    wire_protocols = config.providers.get("wire_protocols")
    if not isinstance(wire_protocols, dict) or not wire_protocols:
        raise ConfigError("providers.yaml declares no wire protocols")
    for wire_name, protocol in wire_protocols.items():
        if not isinstance(protocol, dict):
            raise ConfigError(f"wire protocol {wire_name!r} must be a mapping")
        config.assert_inference_target_allowed(
            wire_name, context="wire protocol name")
        for field in ("path", "models_path"):
            _validate_wire_path(config, wire_name, field, protocol.get(field))
        for field in ("batches_path", "count_tokens_path"):
            if protocol.get(field) is not None:
                _validate_wire_path(config, wire_name, field, protocol.get(field))

    backends = config.providers.get("backends")
    if not isinstance(backends, dict) or not backends:
        raise ConfigError("providers.yaml declares no backends")
    for name, backend in backends.items():
        config.assert_inference_target_allowed(
            name, backend.get("display_name"), backend.get("base_url"),
            backend.get("base_url_env"), backend.get("wire"),
            context=f"backend {name}")
        for field in ("wire", "base_url", "api_key_env"):
            if not backend.get(field):
                raise ConfigError(f"backend {name} is missing `{field}`")
        protocol = config.wire_protocol(backend["wire"])
        if backend.get("supports_message_batches") and not protocol.get("batches_path"):
            raise ConfigError(
                f"backend {name} declares supports_message_batches but its wire "
                f"protocol {backend['wire']!r} has no `batches_path`")

    batch_defaults = (config.providers.get("defaults") or {}).get("batch") or {}
    if not isinstance(batch_defaults, dict):
        raise ConfigError("providers.yaml defaults.batch must be a mapping")
    for field in ("expected_latency_seconds", "max_latency_seconds",
                  "deadline_slack_seconds", "poll_interval_seconds"):
        value = batch_defaults.get(field, DEFAULT_BATCH_DEFAULTS[field])
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
            raise ConfigError(f"providers.yaml defaults.batch.{field} must be a "
                              f"non-negative number, got {value!r}")
    urgent = batch_defaults.get("urgent_priority", DEFAULT_BATCH_DEFAULTS["urgent_priority"])
    if isinstance(urgent, bool) or not isinstance(urgent, int) or not 0 <= urgent <= 100:
        raise ConfigError("providers.yaml defaults.batch.urgent_priority must be an "
                          f"integer 0..100, got {urgent!r}")
    expected = batch_defaults.get("expected_latency_seconds",
                                  DEFAULT_BATCH_DEFAULTS["expected_latency_seconds"])
    maximum = batch_defaults.get("max_latency_seconds",
                                 DEFAULT_BATCH_DEFAULTS["max_latency_seconds"])
    if expected > maximum:
        raise ConfigError("providers.yaml defaults.batch.expected_latency_seconds "
                          "exceeds max_latency_seconds")

    for name, runtime in (config.providers.get("runtimes") or {}).items():
        for backend_name in runtime.get("compatible_backends") or []:
            if backend_name not in backends:
                raise ConfigError(
                    f"runtime {name} lists unknown backend {backend_name!r}")

    bindings = config.bindings.get("bindings")
    if not isinstance(bindings, dict):
        raise ConfigError("model-bindings.yaml declares no bindings")
    for backend_name, table in bindings.items():
        if backend_name not in backends:
            raise ConfigError(
                f"binding table for unknown backend {backend_name!r}")
        for policy_id, binding in (table or {}).items():
            if policy_id not in policies:
                raise ConfigError(
                    f"binding {backend_name}.{policy_id} does not name a "
                    f"canonical policy id (aliases are not allowed here)")
            if not isinstance(binding, dict):
                raise ConfigError(
                    f"binding {backend_name}.{policy_id} must be a mapping")
            provenance = binding.get("provenance")
            if provenance not in ("runtime-verified", "operator-supplied", "unbound"):
                raise ConfigError(
                    f"binding {backend_name}.{policy_id} has invalid provenance "
                    f"{provenance!r}")
            if binding.get("model") and provenance == "unbound":
                raise ConfigError(
                    f"binding {backend_name}.{policy_id} names a model but is "
                    f"marked unbound")
            if binding.get("model"):
                config.assert_inference_target_allowed(
                    binding["model"],
                    context=f"binding {backend_name}.{policy_id} model")
            request = binding.get("request")
            if request is not None:
                if not isinstance(request, dict):
                    raise ConfigError(
                        f"binding {backend_name}.{policy_id} request must be a mapping")
                config.assert_inference_target_allowed(
                    *_scalar_values(request),
                    context=f"binding {backend_name}.{policy_id} request")
                selectors = sorted(REQUEST_TARGET_SELECTOR_FIELDS.intersection(request))
                if selectors:
                    raise ConfigError(
                        f"binding {backend_name}.{policy_id} request may not override "
                        f"transport target selector(s): {', '.join(selectors)}")
            caps = binding.get("capabilities") or {}
            ceiling = caps.get("max_reasoning_effort")
            if binding.get("model") and ceiling not in order:
                raise ConfigError(
                    f"binding {backend_name}.{policy_id} declares unknown "
                    f"max_reasoning_effort {ceiling!r}")

    for backend_name in config.backend_fallback_order():
        if backend_name not in backends:
            raise ConfigError(
                f"backend_fallback_order names unknown backend {backend_name!r}")
