# Research Loop v2 Implementation Plan

**Status:** Proposed  
**Date:** 2026-08-08  
**Architecture:** `docs/research-loop-v2.md`  
**Delivery strategy:** additive, shadow-first, and reversible

## 1. Desired outcome

Deliver a campaign-level control plane that can continuously advance a committed research goal while preserving all existing evidence and authority rules.

The implementation is complete when the repository can:

1. rehydrate an active `GOAL-*` campaign after a process restart;
2. maintain and rank a multi-branch research frontier;
3. build a provenance-preserving evidence bundle from `crypto-kb` before every model route;
4. select the least expensive eligible model policy without violating capability floors;
5. verify cheap-model output and escalate when required;
6. treat a worker’s final response as a task boundary, never a campaign boundary;
7. generate typed successor actions after every verified ledger checkpoint;
8. run periodic strong-model meta-reflection;
9. admit verified results and reusable negative lessons into durable memory;
10. pause only through an explicit, committed harness-level condition with a resume action; and
11. expose enough telemetry to measure cost, quality, continuation, and retrieval behavior.

## 2. Delivery principles

- **Do not rewrite the working components.** Extend the dispatcher, inference adapter, worker runner, and KB through narrow interfaces.
- **Keep the worker bounded.** Add a campaign controller above `orchestration/agent/graph.py` rather than making that graph infinite.
- **Shadow before authority.** New planning and routing decisions are recorded and evaluated before they control live work.
- **Preserve schema compatibility.** Existing dispatch queues and handoffs remain readable.
- **Make every phase independently testable.** Each pull request should have a useful vertical slice and a rollback switch.
- **Commit only durable facts.** High-volume telemetry and rebuildable caches stay outside the ledger; checkpoints and decisions are hash-bound to committed state.
- **No learned policy before a project dataset exists.** Rule-based routing and memory admission come first.

## 3. Proposed package layout

```text
orchestration/
├── campaign/
│   ├── __init__.py
│   ├── models.py               # closed Pydantic campaign contracts
│   ├── controller.py           # transition state machine
│   ├── checkpoint.py           # rehydrate, hash, idempotency
│   ├── lease.py                # canonical-controller lease
│   ├── frontier.py             # admission, DAG, scoring, deduplication
│   ├── proposer.py             # result -> typed successors
│   ├── reflection.py           # epoch meta-reflection
│   ├── terminal.py             # completion/pause policy
│   ├── store.py                # SQLite runtime projection
│   ├── telemetry.py
│   └── cli.py
├── knowledge/
│   ├── __init__.py
│   ├── models.py               # query plan and evidence bundle
│   ├── client.py               # KnowledgeClient protocol
│   ├── local.py                # in-process crypto-kb adapter
│   ├── mcp.py                  # MCP adapter
│   ├── planner.py              # task -> retrieval plan
│   ├── coverage.py             # coverage/freshness metrics
│   └── admission.py            # verified result -> draft memory records
├── routing/
│   ├── __init__.py
│   ├── models.py               # features, candidates, route decision
│   ├── classifier.py           # deterministic task feature extraction
│   ├── router.py               # hard gates + utility selection
│   ├── escalation.py           # verifier-driven cascade
│   ├── budget.py               # model/compute budget accounting
│   ├── pricing.py              # versioned binding price inputs
│   ├── telemetry.py
│   └── cli.py                  # route explain / compare
├── frontier-policy.yaml
├── router-policy.yaml
└── reflection-policy.yaml

schemas/
├── campaign-checkpoint.schema.json
├── evidence-bundle.schema.json
├── frontier-node.schema.json
├── route-decision.schema.json
├── task-envelope.schema.json
├── task-result.schema.json
└── verification-outcome.schema.json

coordination/goals/<GOAL-ID>/
├── campaign.yaml               # opt-in mode and pinned policy versions
├── checkpoints/                # immutable committed checkpoints
├── frontier/                   # immutable frontier snapshots
└── batches/                    # existing batch/dispatch artifacts
```

The exact package split can be compressed if the initial implementation remains small. The interfaces and ownership boundaries should remain.

## 4. Authoritative-state map

| State | Authoritative location | Runtime projection | Index/cache |
|---|---|---|---|
| Goal and research status | `ledger/` records and Coordinator decisions | campaign SQLite | KB/Qdrant |
| Experiment and review evidence | immutable run/review artifacts | campaign SQLite references | KB/Qdrant |
| Ready execution tasks | committed dispatch queue | dispatcher process | none |
| Research alternatives | checkpointed frontier snapshots | campaign SQLite | optional KB indexing |
| Route decisions | archived task artifacts | router telemetry store | analytics store |
| Retrieved evidence | immutable evidence bundle per attempt | task state | none |
| KB source documents | Git/object storage | local object cache | Qdrant |
| High-volume cost/latency telemetry | append-only telemetry store | local buffer | analytics store |

The runtime store may be deleted and reconstructed. Deleting the ledger or source corpus may not be required for any recovery path.

## 5. Phase 0 — Baselines, contracts, and evaluation fixtures

### Objective

Define what “better” means before changing scheduling or model selection.

### Add

- `orchestration/campaign/models.py`
- `orchestration/knowledge/models.py`
- `orchestration/routing/models.py`
- JSON schemas under `schemas/`
- `orchestration/frontier-policy.yaml`
- `orchestration/router-policy.yaml`
- `orchestration/reflection-policy.yaml`
- synthetic and replay fixtures under `tests/fixtures/research_loop/`
- baseline reports under `evals/baselines/` or the repository’s existing eval output location

### Baseline datasets

Create a small labeled corpus of real repository task patterns:

- deterministic extraction and record formatting;
- log normalization;
- routine implementation/debugging;
- experiment execution;
- experiment design;
- mathematical analysis;
- hypothesis generation;
- anomaly interpretation;
- contradiction resolution;
- ordinary independent review; and
- breakthrough/closure review.

Each fixture records:

- minimum acceptable policy;
- whether cheap-first is allowed;
- required evidence classes;
- expected verifier;
- expected escalation conditions; and
- whether a worker completion may create a campaign terminal event (normally false).

### Tests

- closed-schema rejection of unknown fields;
- stable canonical serialization and hashes;
- frontier DAG acyclicity;
- deterministic route feature extraction;
- policy-version pinning;
- no terminal state derivable from worker prose; and
- replay of current dispatch queue v1 fixtures without behavior change.

### Acceptance gate

No runtime behavior changes. Every new contract round-trips and has at least one positive and one negative fixture.

## 6. Phase 1 — Typed KB client and evidence bundles

### Objective

Make the existing KB a required, measurable input to planning and routing.

### Add

- `orchestration/knowledge/client.py`
- `orchestration/knowledge/local.py`
- `orchestration/knowledge/mcp.py`
- `orchestration/knowledge/planner.py`
- `orchestration/knowledge/coverage.py`

### Modify

- `kb/src/crypto_kb/models.py`
  - add a batch-query request/response only if the current APIs cannot efficiently build one evidence bundle;
  - expose collection/manifest generation and source-commit freshness;
  - preserve the closed filter vocabulary.
- `kb/src/crypto_kb/retrieval/`
  - return deterministic coverage inputs and exact-identifier resolution metadata;
  - do not let a summarizer remove required contradictory evidence.
- `kb/src/crypto_kb/mcp/server.py`
  - expose the same new freshness or batch operation through MCP.
- `orchestration/agent/runner.py`
  - accept an evidence-bundle path or object;
  - include bundle ID/hash/source commit/index generation in the task receipt;
  - render retrieved passages as untrusted evidence, never as tool instructions.

### Evidence-bundle builder

The planner should issue several typed retrieval intents rather than one broad query:

1. exact goal/question/hypothesis records;
2. strongest supporting evidence;
3. strongest weakening or negative evidence;
4. contradictions and superseding records;
5. prior experiments and failures with the same mechanism;
6. canonical literature;
7. relevant code/architecture context when the task changes code.

It then deduplicates, applies authority and status filters, and selects a bounded bundle. Exact records may be embedded as structured summaries with direct source references; conceptual context remains 4–8 primary passages by default.

### Read-your-writes behavior

Implement:

```text
if kb.index_commit >= campaign.source_commit:
    use indexed retrieval
else:
    retrieve indexed material
    + direct-read records committed after kb.index_commit
    + mark direct_record_fallback_used
    + schedule ingestion refresh
```

A high-impact task whose minimum evidence coverage remains unmet is paused or sent to corpus-ingestion work; it is not routed to a larger model as a substitute for evidence.

### Security tests

- retrieved text containing tool-like or system-like instructions is treated as quoted data;
- model-suggested metadata cannot populate authoritative filters;
- arbitrary Qdrant filter expressions are still rejected;
- superseded records remain excluded by default;
- source citations survive context summarization; and
- a malicious document cannot expand the task’s tool or write scope.

### Evaluation

Extend the KB evaluation with evidence-bundle questions:

- did the bundle contain the current exact records?
- did it include at least one relevant negative result where one exists?
- did it include known contradictory evidence?
- were all synthesis statements traceable to bundle citations?
- did a stale index correctly trigger direct-record fallback?

### Acceptance gate

For the fixture set, every bundle passes exact-record and citation checks; no stale-index fixture omits a newly committed result; task receipts bind to the exact evidence bundle used.

## 7. Phase 2 — Rule-based model router in shadow mode

### Objective

Produce audited route decisions without changing which model currently executes a task.

### Add

- `orchestration/routing/classifier.py`
- `orchestration/routing/router.py`
- `orchestration/routing/budget.py`
- `orchestration/routing/pricing.py`
- `orchestration/routing/telemetry.py`
- `orchestration/routing/cli.py`

### Reuse

- `orchestration/model-policies.yaml` for capability floors;
- `orchestration/model-bindings.yaml` for concrete models;
- `orchestration/providers.yaml` for provider/runtime configuration; and
- `orchestration.adapter` for strict resolution and inference receipts.

### Router algorithm v1

```python
features = classify(task, evidence_bundle)
minimum_policy = derive_hard_policy(features, task.role, task.claim_impact)
eligible = adapter.resolve_all(minimum_policy, runtime_constraints)
eligible = reject_silent_downgrades(eligible)
selected = choose_by_rules_then_cost(eligible, features, budget)
return RouteDecision(...)
```

The classifier should be deterministic wherever possible. It may use a cheap model only to classify ambiguous natural-language tasks, and that classifier output is constrained by role and claim-impact hard gates.

### Initial hard rules

- deterministic commands and calculations -> T0;
- extraction, formatting, query generation, and log normalization -> `executor-mechanical`;
- routine implementation/debugging/experiment execution -> `executor-implementation`;
- experiment design, mathematical analysis, hypothesis generation, synthesis, and meta-reflection -> `research-deep` or the Coordinator policy appropriate to authority;
- independent claim interpretation -> `review-adversarial`;
- contradiction, closure, or claimed breakthrough -> `review-breakthrough`;
- state-changing work always retains Coordinator authority regardless of the worker model;
- low KB coverage triggers retrieval work before model escalation; and
- no route may reduce an independent-review effort floor.

### Shadow outputs

For every existing task, record:

- the static route actually used;
- the shadow route;
- candidate bindings rejected and why;
- predicted cost difference;
- whether both routes satisfy the same policy floor; and
- the eventual verifier result.

Store high-volume events outside the ledger, but archive the route decision associated with each task selected for evaluation.

### CLI

Proposed commands:

```bash
python -m orchestration routing explain path/to/task.yaml --evidence path/to/bundle.json
python -m orchestration routing compare path/to/task.yaml --all-backends
python -m orchestration routing evaluate evals/router/tasks.jsonl
```

### Tests

- mechanical tasks prefer T0/T1 when all hard requirements pass;
- novel reasoning skips cheap-first;
- high-impact review always selects the required review policy;
- an unbound or insufficient backend is rejected;
- fallback is recorded and requires explicit permission;
- pricing cannot override a capability floor;
- stale or incomplete evidence changes the route reason but does not falsely lower difficulty; and
- identical inputs and policy versions yield identical route decisions.

### Acceptance gate

Shadow mode shows zero hard-policy violations and zero silent downgrades. Disagreements with current static routing are reviewable by reason code.

## 8. Phase 3 — Verifier-driven cheap-first escalation

### Objective

Allow lower-cost execution for bounded, checkable tasks while preserving result quality.

### Add

- `orchestration/routing/escalation.py`
- task-type verifier registry
- escalation histories in the inference receipt

### Modify

- `orchestration/agent/runner.py`
  - emit a structured `TaskResult`;
  - distinguish completed, budget-exhausted, tool-denied, model-error, and invalid-output states;
  - record actual model/provider disagreement;
  - never label budget exhaustion as task success.
- `orchestration/agent/graph.py`
  - retain the bounded graph;
  - validate the final structured result before returning completed;
  - make “no tool calls” a worker event, not a campaign signal.

### Cascade behavior

```text
T0/T1 attempt
    -> deterministic verifier passes: accept
    -> missing evidence: retrieve/expand
    -> repairable schema issue: one bounded repair
    -> reasoning deficiency: escalate to T2/T3
    -> high-impact interpretation discovered: route to T3/T4
```

Do not run a cheap attempt merely to satisfy a cascade ritual. Tasks classified as strong-reasoning work route directly to the appropriate policy.

### Cost controls

- per-task maximum attempts;
- per-route retry budget;
- campaign inference budget;
- reserve budget for independent review and anomaly escalation;
- no repeated retries on identical evidence and prompt hashes; and
- cost receipt on every attempt.

### Evaluation

Compare against a premium-only baseline on the task fixture set:

- verifier pass rate;
- material omission rate;
- escalation precision and recall;
- final model required;
- total cost including failed cheap attempts; and
- latency including retries.

A provisional activation gate is meaningful measured cost reduction with no hard-gate violations and no material quality regression on bounded-task verifiers. The final tolerance should be selected from the project’s measured Pareto curve, not copied from a generic benchmark.

## 9. Phase 4 — Persistent frontier and mandatory successor proposer

### Objective

Replace the single-next-prompt pattern with a durable, diverse set of ranked research actions.

### Add

- `orchestration/campaign/frontier.py`
- `orchestration/campaign/proposer.py`
- frontier snapshot schema and policy
- `frontier list`, `frontier explain`, and `frontier replay` CLI commands

### Frontier operations

- `admit(proposal)` validates schema, dependencies, deduplication, and minimum decision value;
- `select_ready()` applies dependencies, score, portfolio diversity, and budgets;
- `apply_outcome()` closes or updates a node and creates typed branches;
- `rerank()` recomputes transparent score components;
- `archive()` records rejected, duplicate, exhausted, and completed nodes without deleting history; and
- `snapshot()` creates a canonical hash-bound frontier state for the campaign checkpoint.

### Deduplication

Use several signals rather than embedding similarity alone:

- exact hypothesis and mechanism identifiers;
- shared assumptions;
- experiment contract hash;
- target metric and parameter ranges;
- semantic similarity over claims/mechanisms; and
- cited predecessor graph.

A model may suggest duplication, but deterministic fields and explicit Coordinator review decide whether a node is merged or rejected.

### Successor proposer

The proposer is a strong-reasoning task with a structured output contract. It receives:

- the just-verified outcome;
- the current frontier;
- negative results and contradictions;
- coverage by mechanism and assumption;
- campaign budget; and
- the target-result profile.

It returns distinct proposals plus shared-assumption annotations. The controller validates them and may send incomplete proposals back for one bounded repair; it does not silently repair scientific content itself.

### Empty-frontier refill ladder

Implement the existing documented order in code:

1. execute the goal’s committed `next_action` when still valid;
2. select the highest-ranked open hypothesis;
3. propose a replication or control for the weakest-supported live claim;
4. invoke the successor/idea generator on the bound `RQ-*`;
5. invoke epoch meta-reflection if the frontier appears locally exhausted;
6. pause with `NoWorkReason` and an exact resume action only when no candidate ranks above doing nothing.

### Tests

- every verified outcome maps to appropriate successor classes;
- infrastructure failure does not weaken a mathematical hypothesis;
- invalid receipt produces repair work only;
- negative results remain retrievable and influence future proposals;
- proposals sharing one assumption are not counted as mechanism diversity;
- cyclic dependencies and duplicate nodes are rejected;
- empty-frontier refill is deterministic and exhausts the ladder in order; and
- a worker’s “done” text cannot clear the frontier or close the goal.

### Acceptance gate

On replay fixtures, every nonterminal checkpoint leaves at least one ranked successor or a valid committed pause reason. No synthetic campaign stops because a worker emitted a final answer.

## 10. Phase 5 — Campaign controller, checkpointing, and canonical lease

### Objective

Run the complete multi-task loop continuously and recoverably.

### Add

- `orchestration/campaign/controller.py`
- `orchestration/campaign/checkpoint.py`
- `orchestration/campaign/store.py`
- `orchestration/campaign/lease.py`
- `orchestration/campaign/terminal.py`
- `orchestration/campaign/cli.py`

### Modify

- `tools/research_dispatch.py`
  - add optional dispatch queue v2 fields for `frontier_node_id`, evidence bundle, route decision, successor contract, and attempt history;
  - retain v1 parsing and rendering;
  - validate that archived artifacts include the route/evidence IDs declared by the task.
- `.claude/skills/coordinate-research-goal/SKILL.md`
  - make the new controller the executable implementation of the documented loop;
  - retain the prose as the human-readable contract.
- `docs/dynamic-subagent-dispatch.md`
  - document the boundary between frontier admission and ready-task dispatch.
- `Makefile`
  - add campaign schema, replay, and recovery checks.

### Controller transitions

Each transition writes an idempotency receipt before moving to the next state. State-changing transitions require the Coordinator lease and existing archive validation.

The controller should support two execution modes:

```bash
# One transition for debugging and supervised operation
python -m orchestration campaign step --goal GOAL-ECDLP-001

# Continue until a committed terminal/pause condition
python -m orchestration campaign run --goal GOAL-ECDLP-001
```

A process supervisor may restart `campaign run`; correctness comes from checkpoint recovery, not from assuming the process never crashes.

### Campaign opt-in

`coordination/goals/<GOAL-ID>/campaign.yaml`:

```yaml
schema: crypto.autoresearch.campaign_config.v1
goal_id: GOAL-ECDLP-001
mode: shadow
controller_policy: coordinator-orchestration-code
router_policy_version: rules-v1
frontier_policy_version: v1
reflection_policy_version: v1
knowledge:
  required: true
  minimum_index_freshness: source_commit
budgets:
  inference_usd: "..."
  compute_hours: "..."
  reserve_fraction_for_review: 0.20
terminal_policy:
  completion_requires_committed_goal_criterion: true
  user_stop_allowed: true
  pause_on_budget_exhaustion: true
```

### Canonical lease

The lease must include:

- goal ID;
- owner runtime/session ID;
- source commit;
- monotonically increasing epoch;
- acquired/renewed timestamps; and
- expiration.

Only lease ownership plus Coordinator authority permits checkpoint advancement. A stale secondary worktree cannot acquire a lease without reconciling against current committed state.

### Recovery tests

Inject a crash after every state transition and verify that restart:

- never executes a completed model/tool side effect twice;
- never creates two archive commits for one attempt;
- never loses a verified result;
- never advances from an unverified snapshot;
- resumes the correct frontier node; and
- retains budget accounting.

### Acceptance gate

A fixture campaign runs through multiple positive, negative, invalid, and budget-exhausted tasks, survives injected restarts, and ends only through a valid committed completion or pause policy.

## 11. Phase 6 — Memory admission and epoch meta-reflection

### Objective

Convert verified experience into reusable research and strategic memory without polluting authoritative state.

### Add

- `orchestration/knowledge/admission.py`
- `orchestration/campaign/reflection.py`
- draft templates for strategic lessons and frontier-coverage reports

### Memory admission pipeline

```text
TaskResult + VerificationOutcome + DEC-*
    -> deterministic eligibility checks
    -> proposed memory classification
    -> Coordinator/reviewer gate where required
    -> immutable KN-*/ledger or project record
    -> snapshot/ledger archive
    -> crypto-kb stage-repo + ingest
    -> freshness watermark update
```

### Admission classes

- verified fact or scoped finding;
- negative result;
- anomaly requiring future work;
- reusable implementation lesson;
- experimental-design lesson;
- contradiction/assumption dependency; and
- strategic reflection.

Raw transcripts, speculative model explanations, duplicate summaries, and unsupported novelty claims are not admitted.

### Reflection triggers

Run meta-reflection when any condition fires:

- every configured number of ledger decisions;
- frontier score stagnation;
- repeated route escalation;
- multiple failures sharing an assumption;
- unresolved contradiction;
- mechanism diversity below threshold;
- repeated duplicate proposals; or
- no candidate survives frontier admission.

### Tests

- model-suggested authoritative metadata is rejected;
- admission cites the exact verified records;
- negative results are stored and retrieved by future task bundles;
- strategic reflections cannot change claim status;
- a newly admitted record is visible through read-your-writes before indexing catches up; and
- a reflection cannot schedule work outside the goal or budget contract.

## 12. Phase 7 — Shadow rollout, canary, and activation

### Feature switches

```text
AUTORESEARCH_CAMPAIGN_MODE=off|shadow|active
AUTORESEARCH_ROUTER_MODE=static|shadow|active
AUTORESEARCH_FRONTIER_MODE=manual|suggest|active
AUTORESEARCH_MEMORY_ADMISSION=off|draft|active
AUTORESEARCH_META_REFLECTION=off|shadow|active
```

Configuration files should be preferred for committed campaigns. Environment switches provide emergency rollback and local testing; every effective mode is recorded in receipts.

### Rollout order

1. **Replay only:** run historical tasks and campaigns without model calls.
2. **Live shadow routing:** predict routes while current static policies execute.
3. **Live shadow frontier:** generate and score successors without admitting them.
4. **Cheap-route canary:** activate routing only for mechanical, deterministic-verifier tasks.
5. **Frontier suggestion mode:** Coordinator reviews generated successors before admission.
6. **Single-goal active campaign:** enable automatic continuation on one non-closure, non-breakthrough goal.
7. **Meta-reflection activation:** allow strong-model strategic guidance but not official transitions.
8. **Broader activation:** expand task classes only after evaluation gates pass.

### Rollback

- switch campaign to `shadow` or `off`;
- retain all checkpoints and route decisions;
- resume from the last committed goal `next_action` using the current manual skill flow;
- never delete a frontier or failed attempt during rollback; and
- do not rebase or rewrite archived campaign commits.

### Operational health

Expose:

- active goal and transition;
- lease owner/epoch;
- last committed checkpoint;
- current frontier node and dispatch tasks;
- KB source/index freshness;
- selected route and spend;
- verifier/escalation state;
- last successful heartbeat; and
- exact pause or terminal reason.

A watchdog may restart a dead process. It may not infer scientific success or alter official state.

## 13. Phase 8 — Project-specific learned routing (future)

This phase begins only after enough verified routes exist.

### Dataset

Each row should include:

- task features;
- evidence coverage/freshness/contradiction features;
- policy/backend/model selected;
- reasoning effort;
- cost and latency;
- verifier result;
- escalation path;
- final model required;
- human/Coordinator override; and
- downstream research-value signals.

### Training targets

Prefer predicting task-specific verifier success and expected total cascade cost over predicting a vague scalar “quality.” Calibrate uncertainty by task type and backend.

### Deployment boundary

The learned router may rank only candidates that pass hard deterministic gates. It cannot:

- lower a policy floor;
- waive independent review;
- route breakthrough review to a weaker policy;
- override a tool/write-scope constraint;
- declare a goal complete; or
- admit authoritative memory.

Run it in shadow, compare against rules, then permit it only on task classes where calibration and cost benefit are demonstrated.

## 14. Pull-request sequence

The implementation should be split so each change is reviewable and reversible.

| PR | Proposed title | Core deliverable | Depends on |
|---|---|---|---|
| 1 | `loop: define campaign, frontier, routing, and evidence contracts` | schemas, models, fixtures, baseline eval | none |
| 2 | `kb: build typed evidence bundles with freshness guarantees` | KnowledgeClient, bundle builder, stale-index fallback | PR 1 |
| 3 | `routing: add auditable rule-based model routing in shadow mode` | classifier, hard gates, route decisions, telemetry | PRs 1–2 |
| 4 | `routing: add verifier-driven cheap-first escalation` | verifiers, cascades, structured task results | PR 3 |
| 5 | `loop: add persistent research frontier and successor generation` | frontier DAG, scoring, dedup, refill ladder | PRs 1–2 |
| 6 | `loop: add recoverable campaign controller and checkpoints` | state machine, lease, idempotency, dispatch v2 | PRs 3–5 |
| 7 | `memory: admit verified results and add epoch reflection` | memory writer, KB refresh, strategic reflection | PR 6 |
| 8 | `loop: canary active routing and automatic continuation` | feature modes, operational health, replay/canary evidence | PRs 1–7 |
| 9 | `routing: calibrate project-specific learned router` | optional learned ranking within hard gates | sufficient telemetry |

PRs 3 and 5 can proceed in parallel after the common contracts and KB bundle are stable. PR 6 is the integration point.

## 15. File-level change checklist

### Existing orchestration

- [ ] `orchestration/model-policies.yaml`: keep IDs immutable; add only new purpose tags or policy aliases when required by concrete task classes.
- [ ] `orchestration/model-bindings.yaml`: add verified low-cost bindings where available; do not overstate capabilities to make routing pass.
- [ ] `orchestration/adapter/resolver.py`: expose eligible-candidate enumeration in addition to single resolution.
- [ ] `orchestration/adapter/manifest.py`: record route/evidence/escalation IDs.
- [ ] `orchestration/agent/runner.py`: accept evidence and route decisions; emit structured task results.
- [ ] `orchestration/agent/graph.py`: preserve bounded execution and validate task termination semantics.
- [ ] `tools/research_dispatch.py`: add compatible queue v2 fields and archive binding checks.

### Existing KB

- [ ] `kb/src/crypto_kb/models.py`: freshness and optional batch evidence contracts.
- [ ] `kb/src/crypto_kb/retrieval/`: coverage inputs and required-evidence selection.
- [ ] `kb/src/crypto_kb/mcp/server.py`: parity with local client.
- [ ] `kb/src/crypto_kb/observability.py`: evidence-bundle/freshness metrics.
- [ ] `kb/tests/`: stale-index, contradiction, prompt-injection, and read-your-writes tests.

### Documentation and skills

- [ ] `docs/dynamic-subagent-dispatch.md`: distinguish frontier from dispatch queue.
- [ ] `docs/focused-autoresearch-loop.md`: reconcile focus limits with a broad frontier and bounded active set.
- [ ] `docs/control-plane-primacy.md`: document lease as enforcement of existing authority, not new authority.
- [ ] `.claude/skills/coordinate-research-goal/SKILL.md`: call the executable campaign controller.
- [ ] `.claude/skills/propose-ideas/SKILL.md`: use typed KB evidence bundles and frontier admission.
- [ ] runtime bindings generated for any new role only if a genuinely new role is required.

## 16. End-to-end test scenarios

At minimum, automate these scenarios:

1. **Normal negative experiment:** valid negative result -> ledger archive -> negative memory -> alternative-mechanism and control successors -> campaign continues.
2. **Worker says done:** final text contains “research complete” -> task completes -> verifier and successor stages still execute -> goal remains active.
3. **Mechanical cheap route:** T1 extraction passes deterministic verifier -> accepted without premium escalation.
4. **Cheap route misses contradiction:** verifier detects omitted contradictory evidence -> retrieval expands -> route escalates -> failure retained.
5. **Novel hypothesis request:** classifier routes directly to `research-deep`; no cheap attempt.
6. **Breakthrough-like result:** route becomes `review-breakthrough`; independent-session and no-degradation gates hold.
7. **Stale KB:** new negative result exists after index watermark -> direct record fallback includes it -> ingestion refresh scheduled.
8. **KB outage:** exact direct records permit a low-impact task; high-impact synthesis pauses for evidence rather than guessing.
9. **Implementation timeout:** result is infrastructure failure -> repair/decomposition node; hypothesis status unchanged.
10. **Invalid receipt:** no mathematical conclusion; archival repair path only.
11. **Frontier collapse:** refill ladder runs in order; meta-reflection proposes a valid branch or controller commits a scoped pause with resume action.
12. **Concurrent controllers:** only lease owner advances; secondary plane cannot commit checkpoint.
13. **Crash matrix:** crash after each transition; restart resumes without duplicate side effects.
14. **Budget exhaustion:** campaign pauses with remaining frontier and exact resume action; no scientific conclusion inferred.
15. **Malicious retrieved document:** embedded instructions cannot change tools, role, route floor, or write scope.

## 17. Definition of done

Research Loop v2 is ready for broad use when:

- all contracts and configurations are versioned and hash-bound;
- queue v1 and existing handoffs replay unchanged;
- the campaign controller passes crash/recovery and lease-contention tests;
- every nonterminal checkpoint has a ranked successor or valid pause reason;
- route shadow evaluation reports zero hard-gate violations and zero silent downgrades;
- activated cheap routes preserve task-specific verifier quality while reducing measured total inference cost;
- every task receipt identifies its evidence bundle, route decision, actual resolved model, and escalation history;
- the KB passes freshness, contradiction, citation, and read-your-writes tests;
- verified negative results demonstrably affect later retrieval and frontier generation;
- meta-reflection cannot change official state;
- feature switches can return the system to current manual/static behavior without rewriting history; and
- one real, non-critical research goal completes several autonomous batches under active mode with all artifacts reviewable in its standing PR.

## 18. Recommended first implementation slice

Start with PRs 1–3 as one vertical planning/routing slice:

1. define the contracts and fixtures;
2. build the evidence bundle from the existing KB; and
3. run the new router in shadow mode against current tasks.

This slice produces immediate value without granting new scheduling authority: it reveals how often current premium routes are unnecessary, how often KB coverage changes the appropriate route, and which task classes cause escalation. That evidence should determine the exact activation thresholds before the campaign controller begins automatic continuation.
