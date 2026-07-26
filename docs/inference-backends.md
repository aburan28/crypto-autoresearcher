# Inference backends, runtimes, and policy resolution

This program is not a Claude harness or a Codex harness. It is a set of role
contracts plus an evidence discipline, and those are indifferent to which model
answers. This document defines how a role gets bound to an actual inference API
and what has to be recorded when it does.

## The four layers

| Layer | File | Answers | Contains vendor names? |
|---|---|---|---|
| Role | `agents/<role>.md`, `orchestration/roles.yaml` | who may do what | no |
| Policy | `orchestration/model-policies.yaml` | what the role needs from a model | no |
| Backend | `orchestration/providers.yaml` | where requests go, in which wire format | endpoints only |
| Binding | `orchestration/model-bindings.yaml` | which model serves which policy | **yes — only here** |

Switching the whole program from one vendor to another is an edit to the
binding table plus one environment variable. No skill, subagent, dispatch
record, ledger record, or committed handoff changes — which matters because
those records are immutable.

`orchestration/adapter/` is the resolver and transport that AGENTS.md has
always described. It is standard library only: no vendor SDK is a dependency of
this research program.

## Policy ids and the alias contract

Policy ids are permanent. The pre-2.0 ids (`coordinator-ultra-code`,
`research-sol-max`, `executor-terra`, `review-xhigh`, `coordinator-sol-max`)
appear in handoffs that are already committed, so they are carried forever as
`aliases:` and resolve to the neutral canonical ids. An alias is never
reassigned to a different capability contract, and
`tests/test_inference_adapter.py` walks every committed handoff to prove they
all still resolve.

Write new handoffs with the canonical ids:

| canonical | legacy alias |
|---|---|
| `coordinator-orchestration-code` | `coordinator-ultra-code` |
| `coordinator-orchestration` | `coordinator-sol-max` |
| `research-deep` | `research-sol-max` |
| `review-adversarial` | `review-xhigh` |
| `executor-implementation` | `executor-terra` |

## Resolution is strict

A policy states requirements (`reasoning_effort`, `tool_use`,
`structured_output`, `min_context_tokens`, `min_output_tokens`). A binding
states capabilities. The resolver compares them and takes exactly one of four
outcomes:

1. **Resolved** — the binding meets every requirement.
2. **Fallback** — the first choice was unusable and the handoff set
   `fallback_allowed: true`. The resolver tries the policy's declared
   `fallback_policy`, then other backends, and accepts only a binding that
   *fully* meets the requirements. `fallback_used: true` and the reason are
   recorded.
3. **Degraded** — the handoff also set `degraded_allowed: true`. A binding that
   misses a requirement is accepted, and every gap is recorded in
   `degraded_requirements`. This needs a coordinator-approved
   `inference_amendment`; it is the machine-checked version of the amendment
   records already in `coordination/goals/*/batches/*/`.
4. **Refused** — anything else stops the task with the exact reason.

`model: null` is a hard stop under every permission: there is no model to call,
and the resolver will not pick a nearby one.

Two governance gates run before any backend is consulted. A policy with
`independent_session_required: true` resolves only when the caller asserts an
independent session, and it refuses when the assigned agent is the agent that
originated the claim.

## Model identifiers are assertions until probed

A model id written into `model-bindings.yaml` is an operator assertion, not a
fact. `provenance` records which:

* `runtime-verified` — reported by the executing runtime itself;
* `operator-supplied` — asserted by the operator, unverified;
* `unbound` — no id chosen; the resolver refuses.

```sh
python3 -m orchestration.adapter doctor --backend zai --probe
```

asks the backend which models it actually serves and fails if a configured id
is missing, printing the closest served names. Every resolution and manifest
block carries `model_verified`, so an unverified id can never be presented as
a verified one. Do this before any run whose manifest will be cited as
evidence — the same discipline as re-verifying a solution certificate.

Declared capabilities are assertions too. The resolver can catch a binding that
*admits* it is too weak; it cannot catch one that overstates itself. Inflating
`max_reasoning_effort` to make a review gate pass is an evidence-integrity
failure, in the same class as overstating a claim tier.

## Running the program on GLM

`glm-5.2` is configured on two backends: `zai` (OpenAI wire) and
`zai-anthropic` (Anthropic wire, same models). Which one you want depends on
the runtime.

```sh
# An Anthropic-protocol agent CLI, driven entirely by GLM:
eval "$(python3 -m orchestration.adapter env \
          --runtime claude_code --backend zai-anthropic --role coordinator)"

# An OpenAI-protocol agent CLI (Codex and friends):
eval "$(python3 -m orchestration.adapter env \
          --runtime codex_cli --backend zai --role executor)"

# Everything, by default, for this shell:
export AUTORESEARCH_BACKEND=zai
```

`env` refuses a runtime/backend pair whose wire protocols disagree, exports the
resolved model rather than a guess, and also exports `AUTORESEARCH_POLICY` and
`AUTORESEARCH_BACKEND` so runs launched in that shell record what they ran on.
Four variables drive that recording: `AUTORESEARCH_POLICY`,
`AUTORESEARCH_BACKEND`, `AUTORESEARCH_FALLBACK_ALLOWED`, and
`AUTORESEARCH_DEGRADED_ALLOWED`. A fifth,
`AUTORESEARCH_INDEPENDENT_SESSION`, must be set explicitly by whoever launches
a review session — the adapter never asserts independence on a run's behalf,
because independence is a fact about how the session was launched, not
something a manifest may claim for itself.

The one gap worth knowing about: `review-adversarial` requires `xhigh`
reasoning and the GLM bindings declare a `high` ceiling, so review tasks refuse
to resolve on GLM unless a coordinator grants a recorded downgrade
(`--allow-degraded`) or the ceiling is raised because the provider documents a
deeper tier. This is deliberate. Independent adversarial review is the gate
that protects every ECDLP claim in the ledger, so weakening it is a decision
someone has to make and sign, not a side effect of changing a vendor.

Check coverage at any time:

```sh
python3 -m orchestration.adapter matrix
```

## Adding a backend

1. Add a `backends:` entry in `providers.yaml` — `wire`, `base_url`,
   `base_url_env`, `api_key_env`. Only a genuinely new wire shape needs code.
2. Add a binding table in `model-bindings.yaml` covering every policy.
3. `python3 -m orchestration.adapter doctor --backend <name> --probe`.
4. `python3 -m orchestration.adapter matrix --backend <name>` to see what it
   can serve as written.

`local` is preconfigured for any OpenAI-compatible server (vLLM, SGLang,
Ollama). A pinned local weight set is the only configuration in which
`resolved_model_id` is stable over time — worth considering for review runs
whose reproducibility must outlive a vendor's deprecation schedule.

## Adding a runtime

A runtime owns the tool loop, the filesystem, and the session.
`orchestration/roles.yaml` holds each role's authority and capabilities in
runtime-neutral terms, plus the tool names each runtime uses for each
capability. To add one: extend the `capabilities:` table with its tool names,
add a `runtimes:` entry in `providers.yaml`, add the role binding files, and
run

```sh
python3 tools/check_runtime_bindings.py
```

which fails if any runtime's agent definition has drifted from the role
contract — a subagent that quietly gained shell access, or a review role routed
to a policy that does not require an independent session. CI runs it on every
push.

`api_direct` is this repository's own transport: single-turn completions with a
resolution receipt, no tool loop. Use it for resolution checks, prompt-level
experiments, and reviews that need no filesystem access. A role that must read
or write repository artifacts runs under a runtime that has a tool loop.

## What every run must record

`orchestration/adapter/manifest.py` is the only writer of the `inference` block,
so a manifest cannot disagree with what the resolver did:

```yaml
inference:
  requested_policy: research-sol-max     # exactly as the handoff wrote it
  canonical_policy: research-deep
  backend: zai
  provider: Z.ai open platform (GLM), OpenAI-compatible
  resolved_model_id: glm-5.2
  model_provenance: operator-supplied
  model_verified: false
  requested_reasoning_effort: high
  reasoning_effort: high
  fallback_used: false
  fallback_reason: null
  degraded_requirements: []
  independent_session: false
  adapter_version: 1.0.0
  config_digest: sha256:...              # binds the run to exact configuration
```

Deterministic harness runs record the same block with `resolved_model_id: null`
and a note saying no model was in the loop. That is a reproducibility fact
worth stating: it is what makes those numbers independent of any inference
vendor. If a policy was requested but could not be resolved, the failure is
recorded in the manifest as `resolution_error` rather than being replaced by a
plausible-looking block.
