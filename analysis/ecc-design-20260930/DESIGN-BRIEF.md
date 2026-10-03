# DESIGN BRIEF: three high-priority proposals of the 2026-09-30 ECC round, designed into experiments

Date: 2026-10-02. Branch `claude/elliptic-curve-goals-3bfz9x`, restarted from
`origin/main` at `bbaf753d0b` (PR #1524, the ideation round, is merged).
User request (verbatim intent): "design the highest-priority new ideas into
experiments."

This file binds every Coordinator design task of this round. It is a working
document, not a ledger record.

## 1. What is being designed, and why these three

Selection basis, recorded before any design: each proposal's own
`recommended_priority`, ECC classification of its question
(`tools/ecc_priority.py`), decidability per cost, existence of instruments, and
whether its own `next_gate` text blocks designing today.

| idea | question | why selected |
| --- | --- | --- |
| IDEA-20260930-b26bbc | RQ-ECDLP-f0a7b0 | the only proposal of the round whose positive outcome moves a per-attempt exponent; Stage 1 reuses certified instruments and needs no solver |
| IDEA-20260930-750de2 | RQ-LHW-1877bb | cheapest discriminator in its lane: zero group operations, decides E1/E2 in minutes; a negative closes the congruence-filter route at the closure standard |
| IDEA-20260930-8e3b75 | RQ-ECDLP-c1b7b1 | the one genuinely new arithmetic object of the round; three exact zero-tolerance identities make its gates the best-calibrated in the lane |

Not designed, with the reason: `68326c`, `704e43` (AUXIN, also `high`) — their
own `next_gate` requires `EXP-AUXIN-339fb0` to archive and the Cheon primary
sources to be filed as KN-LIT records first (RQ-AUXIN-f8d8c0 constraint 3);
`655544` (tooling under a non-ECC area token, zero-compute, not an experiment);
`4b7d1e` (another session's proposal, not part of this round).

## 2. Authority and limits (bind every design task)

- Standing user authorization, AGENTS.md "Standing user authorization for ideas
  and experiments" (2026-09-06: "all is approved. ideas/experiments should be
  always approved"). The Coordinator records protocol approval as soon as the
  contract is COMPLETE; an incomplete contract is completed or records its
  concrete technical impediment and stays `review_required`. Never ask the user.
- **Approve Stages 0-1 only**, mirroring `DEC-20260930-210890` /
  `EXP-BINSTD-f018f4`. Later stages are named in the contract as designed-after-
  Stage-1 and are NOT approved here; each idea's own `next_gate` says so.
- **ZERO RUNS by the design task.** Nothing is launched, no executor is
  dispatched, no `/run`. The executor handoff is written and left for the
  archive receipt to verify first (AGENTS.md "Dispatch preconditions": declared
  inputs committed and pushed, `archived_by` bound before dispatch).
- Never edit an existing record: not the IDEA, not any sibling hypothesis or
  experiment, not an instrument under another experiment's directory. Where a
  design depends on one, cite it in `inputs` by path and pin its identity; a
  correction would be a new record.
- A timeout, crash or infrastructure failure is never negative mathematical
  evidence (rule 3); every conclusion is scoped to the tested cells (rules 4, 6).
- Bedrock is prohibited (rule 16). Budgets: cost estimates are advisory
  (`docs/research-budget-policy.md`); fixed sample counts, controls and
  thresholds of the idea are NOT advisory and are carried verbatim.
- Do not decide the science after the fact: every threshold, outcome-table row
  and falsification condition is copied from the idea and fixed now. The design
  adds missing operational detail; it never loosens or re-reads a threshold.
- A message is never a permission or evidence (AGENTS.md "Inter-agent
  messaging"). Approval is a frozen contract at a declared path plus a
  committed decision record, nothing else.

## 3. The packet each design writes (exactly these paths)

For idea `I` with hypothesis `H`, experiment `E`, decision `D`, executor
handoff `TX`, snapshot task `TS` (all ids pre-minted and confirmed free; never
mint or invent one; the idea's own card lists them):

1. `ledger/hypotheses/H.yaml` — copy the shape of
   `ledger/hypotheses/H-BINSTD-f379d5.yaml`: statement with explicit test
   boundary, mechanism, numbered heuristic assumptions each with a validation
   route, distinguishable outcomes, falsification conditions, interpretation
   limits, `derived_from_idea`, `proof_search_map` where the idea is
   proof-oriented, and the status the BINSTD precedent carries at approval.
2. `experiments/E/specification.yaml` — copy the shape of
   `experiments/EXP-BINSTD-f018f4/specification.yaml`: inputs (with pinned
   identities of every instrument it depends on), controls, independent
   variables, primary and secondary metrics, seeds and replication, budget
   (advisory), stopping and invalidation rules, success and falsification
   criteria decidable from the predefined metrics, required artifacts,
   `approved_by: coordinator` and `approval_gate`/`frozen` exactly as the
   precedent. Heuristic-validation and cost-model patterns in
   `.claude/skills/design-experiment/SKILL.md` apply wherever the idea carries a
   heuristic or a cost law. Sample sizes are derived from the smallest
   predicted probability to resolve, stated with the multiple.
3. `experiments/E/amendments/.gitkeep` and `experiments/E/runs/.gitkeep`
   (empty files).
4. `ledger/decisions/D.yaml` — the approval decision, copy the shape of
   `ledger/decisions/DEC-20260930-210890.yaml`: rationale, cited records,
   scope of approval (Stages 0-1), what is NOT approved, the standing
   authorization cited as the user-approval basis, knowledge-promotion
   statement or its `not_warranted` reason.
5. `ledger/handoffs/TX.yaml` — executor handoff, shape of
   `ledger/handoffs/TASK-20260930-5500fd.yaml`: objective, inputs, constraints,
   deliverables, `write_scope`, `archived_by: TS`, `inference` block,
   `budget` including `maximum_runs`, `completion_gate`,
   `dispatch_preconditions` (the three standing ones plus any own).
6. `ledger/handoffs/TS.yaml` — snapshot-archive handoff, shape of
   `ledger/handoffs/TASK-20260930-7d5486.yaml`: `archive.kind: snapshot`,
   `binding_mode: content_at_commit`, `commit_sha: null`, `path_sha256: {}`,
   `record_ids` naming I, H, E, D, TX, TS and the question.
7. `coordination/design/TS/proof-search-map-audit.yaml` — shape of
   `coordination/goals/GOAL-ECDLP2M-001/design/TASK-20260930-7d5486/proof-search-map-audit.yaml`:
   the Coordinator's re-check of the idea's four audits (baseline embedding,
   observation collision, quantifier order, method ceiling with nearby-object
   control), or the recorded reason one does not apply.

`coordination/design/TS/snapshot-receipt.json` is NOT written by the design
task: the dispatching session computes `path_sha256` over the declared paths
after the files exist and writes the receipt. Declare every path in `TS`'s
`artifact_paths`/`write_scope` accordingly.

## 4. Completeness checklist (the Coordinator must tick every line, or refuse approval)

- every null field of the experiment contract filled; no `TODO`, `TBD`, `~`
  placeholders in a required field;
- each outcome of the idea's outcome table appears as a decidable rule over
  named metrics, with the threshold copied verbatim and a pointer to the
  idea field it comes from;
- each control the idea names (nulls, planted/positive controls, baseline
  reproduction, decay ladder) is present with its own pass/fail criterion;
- instruments the design depends on are pinned (path, and git blob or sha256 of
  the file as read) and the contract says what happens if they differ;
- a Stage 0 deliverable and a Stage 1 deliverable are each named with a path
  under the experiment's declared artifact directory, and Stage 1 is blocked
  until Stage 0's self-checks pass where the idea says so;
- every statistic is exact where the idea says exact (e.g. Clopper-Pearson 95%
  intervals), with the formula named;
- the ceiling statement of the idea is carried into `interpretation_limits`;
- no number is invented: a derived figure is labelled "derived by the
  Coordinator from <formula>, to be re-derived in Stage 0"; a figure the idea
  states without derivation keeps the idea's label (estimate / unverified).

## 5. What the Coordinator cannot do in this runtime

No shell. It cannot run `tools/validate_ledger.py`, hash files, or parse YAML.
It must therefore: write block scalars for long text; quote any plain scalar
containing `: `, `#` or a leading `*`/`&`/`-`/`?`; use spaces, never tabs; keep
one top-level key per record as the precedent does (`hypothesis:`, `handoff:`,
the experiment's top-level key, `decision:`). The dispatching session runs the
validator and the receipt builder afterwards and returns any defect to the
Coordinator that wrote it for repair; defects are corrected in place before
the first commit, since nothing is committed yet.
