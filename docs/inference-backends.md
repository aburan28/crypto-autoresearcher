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

## Cost guardrail: Amazon Bedrock is prohibited

Amazon Bedrock is disabled for all new inference. The adapter rejects any
backend name, provider label, configured or overridden endpoint, or model ID
containing `bedrock` (case-insensitive) before transport can build a request.
OpenCode independently disables the `amazon-bedrock` provider in the project
`opencode.json` and selects OpenAI models by default.

Use an allowed configured API backend such as `openai` or `local`, or an
authenticated direct Codex or Claude Code session whose resolved provider is
not Bedrock. If no allowed API or direct runtime satisfies the requested
policy, the task stops as an infrastructure failure; fallback or downgrade
permission never permits Bedrock. Historical run receipts that mention prior
Bedrock use remain immutable evidence and are not rewritten by this prospective
rule.

## Credentials and endpoints

Every backend needs two things: an **API key** in a named environment variable,
and a **base URL** (which has a working default you only override for a gateway
or a regional deployment). Nothing else.

| backend | wire | base URL (override var) | API key var |
|---|---|---|---|
| `anthropic` | Anthropic Messages | `https://api.anthropic.com` (`ANTHROPIC_BASE_URL`) | `ANTHROPIC_API_KEY` |
| `zai` | OpenAI Chat | `https://api.z.ai/api/paas/v4` (`ZAI_BASE_URL`) | `ZAI_API_KEY` |
| `zai-anthropic` | Anthropic Messages | `https://api.z.ai/api/anthropic` (`ZAI_ANTHROPIC_BASE_URL`) | `ZAI_API_KEY` |
| `fireworks` | OpenAI Chat | `https://api.fireworks.ai/inference/v1` (`FIREWORKS_BASE_URL`) | `FIREWORKS_API_KEY` |
| `fireworks-anthropic` | Anthropic Messages | `https://api.fireworks.ai/inference` (`FIREWORKS_ANTHROPIC_BASE_URL`) | `FIREWORKS_API_KEY` |
| `openai` | OpenAI Chat | `https://api.openai.com/v1` (`OPENAI_BASE_URL`) | `OPENAI_API_KEY` |
| `openrouter` | OpenAI Chat | `https://openrouter.ai/api/v1` (`OPENROUTER_BASE_URL`) | `OPENROUTER_API_KEY` |
| `local` | OpenAI Chat | `http://localhost:8000/v1` (`LOCAL_LLM_BASE_URL`) | `LOCAL_LLM_API_KEY` (optional) |

`zai` and `zai-anthropic` are the same GLM models behind two protocols and share
one key. Pick by what is calling: `zai-anthropic` to point an Anthropic-protocol
CLI at GLM, `zai` for everything else.

**Protocol compatibility is not model access.** Fireworks speaks both wire
formats but serves *open-weight* models — GLM, Kimi, DeepSeek, Qwen, Llama.
`fireworks-anthropic` lets an Anthropic-protocol CLI talk to those models; it
does not provide Claude. The same distinction applies to `zai-anthropic`.

Its Anthropic endpoint also authenticates with `X-Fireworks-Api-Key` rather
than `x-api-key`, declared as a per-backend `auth:` override in
`providers.yaml`. That is deliberate on their side and useful on ours: a real
`ANTHROPIC_API_KEY` sitting in your environment cannot be sent to a
non-Anthropic endpoint by accident.

`fireworks`, `fireworks-anthropic`, `openai`, `openrouter`, and `local` ship
**unbound** — a key alone is not enough,
because `model: null` is set for every policy until you fill in identifiers.

Set them up:

```sh
cp .env.example .env      # then fill in the one or two you use
autoresearch backends     # endpoints, key vars, and what each can serve
autoresearch doctor       # what is missing, and the exact next command
```

`.env` is gitignored and loaded automatically by `autoresearch`, never
overriding a variable already exported in your shell. Plain environment
variables work identically if you would rather not use a file.

Never edit a base URL in `providers.yaml` for a deployment difference — set the
override variable. The file is the shared contract; the variable is your machine.

## Reasoning effort is calibrated per role

Thinking is the dominant cost and latency term here, and it is not uniformly
useful. Two separate fields keep that tunable:

* `requires.reasoning_effort` — the **floor** a backend must support. Below it
  is a downgrade, refused unless the handoff permits one.
* `reasoning_effort` — what is actually **requested** per call. Defaults to the
  floor.

Conflating those makes calibration impossible, because asking for less than a
model can do is not the same as the model not being able to do it.

| policy | floor | requested | why |
|---|---|---|---|
| `review-breakthrough` | max | **max** | a claimed break, closure, or contradiction |
| `review-adversarial` | xhigh | **xhigh** | the gate protecting every ledger claim |
| `coordinator-orchestration-code` | high | **high** | state transitions, contradiction resolution |
| `coordinator-orchestration` | high | **high** | prioritisation and synthesis |
| `research-deep` | high | **high** | mechanism search; depth is the product |
| `executor-implementation` | medium | **medium** | runs an already-frozen protocol |
| `executor-mechanical` | low | **low** | re-run a command, collect artifacts |

The Executor drop is the one that matters most in volume. It runs a protocol the
Coordinator already specified and approved; extra thinking there re-derives a
frozen design, which is both wasted budget and the route by which an Executor
drifts into reinterpreting a specification it is supposed to follow exactly.

This reaches the wire, not just the manifest. On the Anthropic protocol a
binding maps effort to a thinking budget (`budget_by_effort`), and `low` maps to
`0`, which disables extended thinking and lets `temperature: 0.0` through. On
the OpenAI protocol the effort maps to `reasoning_effort`.

### Per subagent, where the runtime can express it

Calibrating effort per role only pays off if a role's effort follows the role.
When effort can be set only per process, a session runs every subagent at
whatever depth it was launched with: an Executor replaying a frozen protocol
thinks as hard as a Validator, and a Validator dispatched from an Executor
session reviews at Executor depth — the exact two errors this table exists to
prevent, reintroduced by the harness.

`runtime_reasoning_effort` in `orchestration/roles.yaml` records which runtimes
can carry effort in the agent definition itself:

| runtime | how | effect |
|---|---|---|
| `claude_code` | `effort:` in `.claude/agents/<role>.md` frontmatter | per subagent; one session dispatches all five roles at their own depths |
| `codex_cli` | `-c model_reasoning_effort=…` from `adapter env` | per session |
| `opencode` | `adapter env` at launch | per session |
| `api_direct` | the resolved policy, per call | per task |

The frontmatter value is **derived, never chosen there**: role →
`default_policy` → `reasoning_effort`, the same requested column as the table
above. `tools/check_runtime_bindings.py` fails the build while an agent file
and its policy disagree, and `--list` prints, per role and runtime, whether
effort comes from the agent file or from the session. Retune by editing the
policy; a hand-tuned agent file is exactly the drift the check exists to catch.

Two limits are deliberate. A policy requesting effort outside a runtime's
vocabulary (`none`, in Claude Code's case) is a build error rather than a
silent nearest match — the role runs on a runtime that can express it, or the
policy states something expressible. And per-task escalation to
`review-breakthrough` at `max` stays out of frontmatter: it is a Coordinator
decision recorded in the handoff, and it requires an independent session, so
binding it to an agent file would let a session promote its own review.

### Choosing between the two coordinator policies

Both run at `high`; the difference is scope, not depth.

* **`coordinator-orchestration-code`** (was `coordinator-ultra-code`) — the
  Coordinator's decision depends on repository state: writing a dispatch plan,
  designing an experiment pipeline, specifying a protocol against real code,
  resolving a contradiction that spans experiments and ledger records. Larger
  context floor (180k) because it has to hold the code path and the records at
  once. The `coordinator-code-path` routing rule selects it automatically when
  a task touches code, repository orchestration, or pipeline design.
* **`coordinator-orchestration`** (was `coordinator-sol-max`) — prioritisation,
  synthesis, and decision records read from the ledger alone. 120k floor.

If you are unsure, use the code policy: it is the declared fallback for the
other, and the cost difference is context, not reasoning depth. The reverse
substitution is not available, which is the right asymmetry — a task that
turned out to need the code path should not quietly proceed without it.

### When `max` applies

`max` is reserved for one policy, `review-breakthrough`, and one situation:
**a wrong answer is unrecoverable**. Concretely, the three triggers in the
`unrecoverable-result-review` routing rule:

* a **claimed breakthrough** — an assertion that something is broken;
* a **closure** result — declaring a direction dead;
* a **contradiction** between two independently validated evidence records.

Everything else about a review — is this receipt valid, do the controls hold,
does this evidence justify `supported` — stays on `review-adversarial` at
`xhigh`. Those are recoverable: a wrong call gets caught by replication or the
next review, and paying `max` for every validator pass would price review out
of the loop entirely, which is the failure mode that actually ends with
unreviewed claims.

The distinction was previously absent: `critical-result-review` routed a
claimed break of a real curve to the same policy as a routine receipt check.

Two properties make this tier different from every other:

* **It cannot be degraded.** `degradable: false` means no amendment, no
  permission, and no `degraded_allowed` flag will run it on a binding that
  misses the `max` floor. Every other policy bends when a coordinator signs for
  it; here there is nothing to sign for. GLM's binding declares a `high`
  ceiling, so a breakthrough review simply refuses to run there.
* **Cross-backend fallback still works**, and is not a weakening — moving to a
  backend that fully meets `max` is how you get the review you asked for. Only
  substitution *downward* is blocked.

If that feels heavy: it fires on a few decisions per campaign at most. If it
fires often, the routing is wrong, not the tier — "breakthrough" that happens
weekly is a miscalibrated claim threshold.

A handoff can calibrate one task without changing the policy:

```yaml
inference:
  policy: executor-implementation
  reasoning_effort: low          # this task is mechanical
```

Two guards apply. Asking for more than the backend supports is **capped and
recorded** (`reasoning_effort_capped`, visible in the summary as `CAPPED`), never
silently granted. And a review policy may not be calibrated below its floor —
`tools/research_dispatch.py` rejects the handoff. Review is where discipline
lives, and buying budget by thinking less there is exactly the trade
`evals/suites/discipline.yaml` exists to catch.

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

### Verifying one Codex CLI session

Backend catalog verification and session runtime verification answer different
questions. `doctor --probe` asks a configured API backend which model IDs it
serves. The session probe instead proves which exact model, reasoning effort,
provider, CLI version, working directory, source, and sandbox were persisted
for one newly created Codex CLI thread:

```sh
python3 -m orchestration.adapter probe-codex-session \
  --codex-bin /absolute/path/to/codex \
  --state-db /absolute/path/to/.codex/state.sqlite \
  --workdir /absolute/path/to/repository \
  --model gpt-5.6-sol \
  --effort xhigh \
  --policy review-adversarial \
  --role validator \
  --task-id TASK-YYYYMMDD-NNN \
  --receipt /new/path/runtime-session-receipt.json \
  --independent-session
```

The command launches exactly one non-ephemeral `codex exec --json` process
with the fixed public `PROBE_OK` prompt and a read-only sandbox. It obtains the
new thread ID from exactly one `thread.started` event, queries only that ID in
the supplied SQLite database (URI `mode=ro` plus `PRAGMA query_only=ON`), and
streams only that row's rollout file. The requested values must agree exactly
with the single state row, `session_meta`, and probe-turn `turn_context`.
Unknown metadata and every missing, ambiguous, or mismatched value fail closed.

The receipt is created exclusively and is never overwritten, including after a
failed attempt. It stores allowlisted facts, canonical-path hashes, event-line
hashes, output byte counts and hashes, and safe argument vectors. It does not
store raw stdout/stderr, raw rollout events, prompts other than the fixed public
probe, environment variables, credentials, base instructions, or unrelated
thread IDs. `tools/check_runtime_bindings.py` must also pass before the receipt
can set `runtime_resolution_verified: true`.

A verified receipt always states:

```yaml
verification_scope: exact_codex_session_only
global_backend_verified: false
model_bindings_mutated: false
```

It is valid only for its `independent_session_id`. It neither upgrades
`model-bindings.yaml` nor proves that a provider serves the model generally.
Each independent Validator or Red Team session therefore needs its own new
receipt and must conduct or resume its review in that exact receipt-bound
thread.

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

## The `api_direct` runtime

`api_direct` is this repository's own runtime: a LangGraph tool loop over the
adapter, so a role can execute against any configured backend without Claude
Code or an OpenAI-protocol CLI.

```sh
# what the task is permitted to do — full resolution, no network
python3 -m orchestration.agent plan --task ledger/handoffs/TASK-20260724-221.yaml

# run it, on GLM, with a resumable checkpoint and an immutable record
python3 -m orchestration.agent run \
  --task ledger/handoffs/TASK-20260724-221.yaml \
  --backend zai \
  --checkpoint .agent-state/TASK-20260724-221.sqlite \
  --out coordination/tasks/TASK-20260724-221/agent
```

It depends on `langgraph` and `langchain-core` from `requirements-agent.txt`.
The adapter core does not: resolution, transport, and manifests stay
standard-library, and importing `orchestration.agent` is the only thing that
pulls LangGraph in. No vendor provider package is needed either — the chat
model in `orchestration/adapter/langchain_model.py` wraps our own transport, so
every backend in `providers.yaml` works through `langchain-core` alone and
every request keeps going through one recorded HTTP path.

**Scope is enforced, not requested.** Under a CLI runtime, "write only inside
your `write_scope`" is an instruction an agent is asked to follow. Here the
tools refuse: writes outside the declared scope, path traversal, absolute
paths, and symlinks leaving the repository are denied, and each refusal is
recorded in the tool journal rather than silently retried elsewhere. Existing
files are never overwritten — artifacts are immutable, so a correction is a new
path. `run_command` takes an argument list (never a shell string), accepts only
allow-listed programs from `orchestration/roles.yaml`, and permits only
read-only git subcommands: committing is a Coordinator archival task with a
verified post-commit receipt, never a worker action.

**A role this runtime cannot host is refused.** `api_direct` has no web
capability, so `idea-generator` and `red-team` — whose contracts depend on the
open literature — will not start here. Running them with a quietly reduced tool
surface would produce a novelty screen that silently never searched anything.
`tools/check_runtime_bindings.py --list` shows the full matrix.

**A budget stop is not a result.** The loop checks the step and wall-clock
budget before each model call and exits with `step_budget_exhausted` or
`wall_clock_budget_exhausted` recorded in the receipt. Rule 5 of `AGENTS.md`
applies to this runtime like any other: an exhausted budget is infrastructure
signal, and a report that cannot distinguish it from a finished task is worse
than no report.

**Long runs resume.** With `--checkpoint`, state is persisted after every node,
keyed by task id, so an interrupted run continues from the last completed tool
call instead of restarting and repeating side effects.

Each run writes `transcript.jsonl`, `tool-journal.json`, and
`inference-receipt.json` into `--out`. The receipt carries the resolution, the
stop reason, token usage, files written, every denied tool call, and any
disagreement between the model that was resolved and the model the backend
answered as.

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
