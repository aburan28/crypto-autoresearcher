# CLAUDE.md

Claude Code harness for autonomous, reproducible ECDLP research. The
binding inter-agent contract is `AGENTS.md` — read it before doing any
research work. This file wires that contract into Claude Code.

## Harness layout

- **Subagents** (`.claude/agents/`): `coordinator`, `idea-generator`,
  `executor`, `validator`, and `red-team`. These are the operational versions
  of the role contracts in `agents/*.md`. Research work is done BY these
  subagents; the top-level session orchestrates and talks to the user.
- **Skills** (`.claude/skills/`), one per lifecycle stage:
  - `/propose-ideas` — ideation for a research question
  - `/design-experiment` — hypothesis + frozen approved protocol
  - `/run-experiment` — bounded execution, immutable run records
  - `/review-evidence` — validation, evidence strength, official decision
  - `/research-status` — read-only ledger overview
  - `/curate-knowledge` — maintain the knowledge corpus
  - `/coordinate-research-goal` — launch and continuously coordinate a committed
    research goal across dispatch batches
- **State**:
  - `ledger/` — canonical YAML records (questions, proposals, hypotheses,
    evidence, decisions, handoffs)
  - `experiments/` — frozen contracts and immutable run artifacts
  - `knowledge/` — curated long-term corpus (literature, techniques,
    internal findings, open problems)

## Non-negotiable rules (summary of AGENTS.md)

1. Only the coordinator changes hypothesis status or approves experiments.
2. Run records, ledger records, and knowledge entries are immutable —
   corrections supersede, never overwrite.
3. Timeouts/crashes/infra failures are never negative mathematical
   evidence.
4. Every conclusion is scoped to the tested curves, parameters, solver,
   and budget; toy-scale evidence is never presented as crypto-scale. Claim
   tiers and solution certificates are defined in
   `docs/claims-and-verification.md`: any claimed solve/relation carries a
   certificate the run wrapper re-verifies independently, and no evidence
   record asserts above its claim tier.
5. Never fabricate commands, outputs, timings, statistics, citations, or
   runs. Missing data stays missing and is reported as such.
6. Every conclusion cites the experiment/run/evidence IDs supporting it.
7. The Coordinator makes isolated snapshot and ledger commits for declared
   research artifacts. A theory, run package, review report, or ledger record
   is not official until the dispatcher's post-commit verifier accepts it.
8. A `GOAL-*` record reaches `status: completed` only on a three-model closure
   quorum: three `CONCUR` attestations in `completion_quorum.attestations`
   whose `resolved_model_id` values are pairwise distinct, with any single
   `DISSENT` blocking closure. Distinctness is on the resolved model, not the
   requested policy alias — three aliases falling back to one model is not a
   quorum. Under this harness that fallback is the common case (see the model
   policy note below), so closing a goal here usually requires deliberately
   routing three different backends. If you cannot, leave the goal `paused` and
   say so; never record an attestation you did not obtain. Enforced by
   `check_goals` in `tools/validate_ledger.py`.
9. Pursue promising paths in good faith. Do not deliberately abandon,
   suppress, mischaracterize, or steer away from a plausible high-value lead
   to derail research. Any deprioritization or closure must record its
   evidence, budget, test boundary, remaining uncertainty, and a concrete
   successor or revisit condition. The harness retains auditable decision
   summaries, rankings, provenance, and ordinary research artifacts for
   independent review; it does not store, infer, or expose private
   chain-of-thought.

## Research direction

Procedure for ideation and closure is anchored by `docs/inventor-protocol.md`
(technique abstract: `knowledge/techniques/KN-TECH-056.md`): object-first
generation, the lossy-projection test, null-object controls before belief, a
real closure standard, and Pareto `dominated_by`/`sota_delta` honesty in every
deliverable. It binds the idea-generator, validator, and red-team subagents.
Premature closure — declining to search because a target looks saturated — is
treated as a failure mode symmetric with overclaiming.

Section 8 of that protocol (`knowledge/techniques/KN-TECH-080.md`) adds the
proof-architecture portfolio and binds the coordinator too: a proof-oriented
proposal carries a `proof_search_map` — exact bottleneck and baseline
reproduction, observation-collision search, quantifier order, method ceiling
and nearby-object control — before the coordinator approves implementation or
expensive experiments. These are cheap pre-compute falsification checks; a
failed audit is often the useful result, and passing them all still claims
nothing beyond rules 4 and 6.

Direction and taste are anchored by `docs/target-result-profile.md`, whose
canonical exemplar is Wesolowski's p^{1/3+o(1)} supersingular-isogeny result
(full text: `inputs/P13-WESOLOWSKI-2026/paper_fulltext.md`): exponent-moving
results on central hard problems, stated conditionally on explicit numbered
heuristics, validated at cryptographic scale, and costed honestly. Idea
Generator proposals and Coordinator prioritization decisions are evaluated
against that profile; the profile is not a license to overclaim, so the
evidence rules above apply unchanged.

## Conventions

- IDs: `RQ-<AREA>-NNN`, `IDEA-YYYYMMDD-NNN`, `H-<AREA>-NNN`,
  `EXP-<AREA>-NNN`, `RUN-*`, `EV-<AREA>-NNN`, `DEC-YYYYMMDD-NNN`,
  `TASK-YYYYMMDD-NNN`, `KN-{LIT,TECH,FIND,OPEN}-NNN`. Immutable, never
  reused. Find the next free number by grepping the relevant directory.
- Record schemas live in `templates/research-records.md`; copy, don't
  invent fields.
- The Coordinator alone stages declared research paths in the shared worktree:
  snapshot before review, then ledger commit before a state transition. Commit
  messages reference the task and record IDs; never rewrite history over
  pushed run records.

## Model policy note

`orchestration/model-policies.yaml` defines role→model routing (GPT-5.6
family policy aliases) for the future runtime adapter described in
AGENTS.md and the roadmap. Claude Code cannot resolve those identifiers:
subagent frontmatter in `.claude/agents/` supports only Claude models, so
all three subagents use `model: inherit` here. When running under this
harness, record `requested_policy` from the handoff and the actual
resolved model in each run manifest's `inference` block, with
`fallback_used: true` if they differ — never silently substitute.

## Typical loop

```text
/research-status
  → /propose-ideas RQ-...
  → /design-experiment IDEA-...
  → /run-experiment EXP-...
  → (Coordinator snapshot commit + independent validation/red team)
  → /review-evidence EXP-...
  → (knowledge-promotion gate: proven results → /curate-knowledge KN-FIND;
     every decision fills knowledge_promotion or says why not)
  → (Coordinator ledger commit + verified decision)
  → (decision drives next iteration)
```
