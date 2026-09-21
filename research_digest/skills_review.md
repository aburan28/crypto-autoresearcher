# Skills / Role-Contract Review — crypto-autoresearcher

*Reviewed 2026-07-22. Sources: `AGENTS.md`, `agents/*.md`, `CLAUDE.md`, `README.md`, `docs/`, `templates/`, `orchestration/`, `tools/`, `.claude/agents/`, `.claude/skills/`.*

## 1. What this repo is

A multi-agent operating system for reproducible ECDLP (elliptic-curve discrete logarithm problem) experimentation. `AGENTS.md` is the binding inter-agent contract defining six roles (Coordinator, Idea Generator, Executor, Reviewer, Validator, Red Team), a mandatory handoff envelope, a dispatch mechanism (`tools/research_dispatch.py`), Git-backed snapshot/ledger archival commits, and formal hypothesis/experiment state machines. Supporting infrastructure: role contracts in `agents/`, operational Claude Code subagents in `.claude/agents/`, lifecycle skills in `.claude/skills/` (`/propose-ideas`, `/design-experiment`, `/run-experiment`, `/review-evidence`, `/research-status`, `/curate-knowledge`, `/coordinate-research-goal`), policy routing in `orchestration/model-policies.yaml`, record schemas in `templates/research-records.md`, five design docs in `docs/`, and tooling in `tools/` (dispatch planner, focus planner, ledger validator, model-policy resolver, immutability checker). Canonical state lives in `ledger/`, `experiments/`, `knowledge/`.

## 2. Role files

**Coordinator** (`agents/coordinator.md`) — keeps the research program coherent; sole authority to approve experiments, change hypothesis status, close/supersede directions, publish syntheses. Maintains five ledgers, requires controls/budgets/stopping rules before approval, owns knowledge promotion and both archival commits. May not invent results, move success criteria post-hoc, treat timeouts as negative math results, or make universal impossibility claims. Output: `coordinator_decision` YAML.

**Idea Generator** (`agents/idea-generator.md`) — produces falsifiable ECDLP ideas with claim, mechanism, novelty tier (`known`/`adaptation`/`speculative`/`unverified`), expected observables, minimal discriminating experiment, controls, falsification criteria. May not report imagined outcomes or propose experiments with no possible negative outcome. Output: `idea` YAML.

**Executor** (`agents/executor.md`) — implements and runs approved protocols exactly as specified. Refuses underspecified contracts, classifies every run valid/invalid, preserves failures. Failure taxonomy: only `negative_observation` is empirical evidence against a prediction; the other five classes require repair. Writes only inside its task `write_scope`; never declares a hypothesis supported/rejected. Output: `execution_report`.

**Red Team** (`agents/red-team.md`) — falsifies interpretation, cost model, and scope of proposed conclusions; checks against correct Pollard-rho/BSGS baselines and the end-to-end cost path; proposes the cheapest discriminating counterexample. Operates only on Coordinator-committed snapshots. Output: `red_team_report`.

**Validator** (`agents/validator.md`) — establishes whether a run is an admissible research receipt: artifact existence/binding, metric recomputation, command/revision/seed/environment coverage, frozen controls, replication independence. Verifies evidence but does not interpret it. Output: `validation_report` with verdict `passed | failed | incomplete | invalid`.

## 3. Cross-role workflow

Idea Generator proposes → Coordinator specifies/approves → Executor runs within a bounded task card → Coordinator snapshot-commits the producer's exact artifacts → independent Reviewer/Validator/Red Team examine only that snapshot → Coordinator ledger-commits reviews, evidence, decision, and any status change. Every inter-agent task carries the handoff envelope (id, objective, inference policy, budget, completion gate, `archived_by`). Dispatch is artifact-driven: non-overlapping `write_scope` paths, ≤3 concurrent tasks, dependencies need `completed` receipts. State machines: hypotheses `proposed → … → replicated → supported|weakened|rejected|inconclusive|superseded`; experiments `draft → review_required → approved → running → completed|failed_infrastructure|invalid → analyzed → archived`. Model policy is layered on top via `orchestration/model-policies.yaml` with mandatory resolution receipts and no silent downgrades.

## 4. Gaps and inconsistencies

1. **Missing `agents/reviewer.md` — confirmed.** `AGENTS.md` defines a Reviewer role and the handoff envelope lists `reviewer` as a valid target, but `agents/` has only coordinator, executor, idea-generator, red-team, validator. The Reviewer's distinct mandate (challenging claims and state transitions) is uncontracted; `.claude/agents/` mirrors the same gap. **Largest structural gap.**
2. **CLAUDE.md numeric inconsistency** — says "all three subagents" but lists five.
3. **`.claude/skills/review-evidence`** bundles validation + evidence-strength + official decision into one stage, blurring the AGENTS.md separation between Validator (verifies), Reviewer (challenges), Coordinator (decides).
4. **Model policy assumes a non-Claude runtime** — GPT-5.6 aliases are unresolvable inside Claude Code; "never silently downgrade" is a logging discipline, not a hard technical control.
5. **Concurrency ambiguity** — cap of 3 concurrent subagents vs. archival commit tasks that "run alone"; how commit tasks count against the cap is not pinned down.
6. **Minor** — `README.md`'s operating loop omits the Reviewer; repo currently has many dirty files, which sits uneasily with the commit-verification contract (operational state, not a contract flaw).

**Overall:** the contract system is unusually rigorous (failure taxonomy, immutable records, claim tiers, commit verification); its principal weakness is that the Reviewer — one of six named roles — exists only by reference.
