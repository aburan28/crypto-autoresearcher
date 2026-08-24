# TASK-20260814-dfaa60 — DESIGN EXPERIMENT: convert IDEA-20260805-3d71ca to a frozen hypothesis + protocol

    goal / batch    GOAL-MLKEM-005 / BATCH-3b9962
    role            coordinator
    policy          coordinator-orchestration-code       effort high
    state           queued
    depends_on      (none)
    review_required false (this task drafts only; no measurement runs, no
                     claim is made or approved here)
    budget          7200 s, 2 GB, 1 run
    claim tier      N/A (specification only)

## What this task is for

Discharges `ledger/goals/GOAL-MLKEM-005.yaml`'s current `next_action`
(recorded in commit `25b7f4ead`): the next batch on this goal converts
`ledger/proposals/IDEA-20260805-3d71ca.yaml` — filed 2026-08-05, unconverted
for ~9 days across an estimated 13-20 batches by two disagreeing counts,
already stating this goal's own tracked object almost verbatim — to a frozen
`H-MLKEM-*` hypothesis via `/design-experiment`
(`.claude/skills/design-experiment/SKILL.md`), folding in
`ledger/proposals/IDEA-20260814-8f8f45.yaml` (the order-statistic floor test)
as a REQUIRED companion extension of the SAME protocol, and
`ledger/proposals/IDEA-20260814-137f68.yaml` (the GSA-profile-fidelity
covariate) as OPTIONAL/discretionary if it does not materially complicate the
protocol.

`IDEA-20260814-10e5e1` (the census-grounded C1 `GAIN(u)` evaluation) is
DELIBERATELY OUT OF SCOPE here — the goal's own `next_action` names it as its
own separate, cheaper, zero-lattice-compute task, not part of this protocol.
`IDEA-20260814-a609eb` (the C2 audit) is not commissioned at all (C2 already
met).

## What it asks for

1. **A frozen `H-MLKEM-<tok>.yaml` hypothesis record**
   (`templates/research-records.md` template), converting `3d71ca`'s own
   `claim`/`heuristic_assumptions`/`minimal_test`/`falsification_conditions`
   into the hypothesis schema's own fields: explicit test boundary,
   distinguishable outcomes, `goal_id: GOAL-MLKEM-005`,
   `question_id: RQ-MLKEM-001`, `source_idea: IDEA-20260805-3d71ca`. State
   plainly how `IDEA-20260814-8f8f45`'s own floor-test extension folds into
   the SAME hypothesis's test boundary (does it become a second conjunct of
   the same hypothesis, a companion hypothesis sharing the run, or a
   sub-claim within one hypothesis's own falsification structure? — your own
   reasoned call, not pre-decided by this card).
2. **A frozen `PREREG-8` protocol document** (this goal's own established
   split-producer notarization pattern — PREREG-4 through PREREG-7 all used
   it; read at least PREREG-7's own structure,
   `coordination/goals/GOAL-MLKEM-005/batches/BATCH-a5b13c/tasks/TASK-20260814-d13724/prereg.md`,
   for house style before drafting this one) covering: real ML-KEM-shaped
   instances (n in {64,128} per `3d71ca`'s own `minimal_test`), real CBD
   samplers, real FIPS 203 compression, one BKZ-beta-reduced basis per
   instance (THIS IS THE FIRST BATCH IN THIS GOAL'S `RQ-MLKEM-001` history to
   require actual lattice reduction rather than a closed-form estimator
   readout or a toy-scale hkz-lineage cell — size the budget accordingly and
   say so explicitly), >= 2^20 targets per instance, >= 8 independent
   (key, basis) draws, `3d71ca`'s own NULL-1/NULL-2/NULL-3/SENS/COMP controls
   plus `8f8f45`'s own NULL-2 reuse and brute-force-feasibility control (report
   exhaustive-search wall-clock at increasing toy `d` BEFORE committing to a
   specific `d` for the headline floor number).
3. **An `experiments/EXP-MLKEM-<tok>/specification.yaml`** experiment
   contract per `/design-experiment` step 2-3: inputs, controls, independent
   variables, primary/secondary metrics, seeds and replication plan, budget,
   stopping and invalidation rules, success and falsification criteria,
   required artifacts. This is a **cost-model / heuristic-validation hybrid**
   per `.claude/skills/design-experiment/SKILL.md`'s own "Experiment class
   patterns" section — read both subsections (heuristic-validation and
   cost-model measurement) and apply whichever fields are load-bearing for
   THIS protocol (it tests a heuristic distributional claim — the Beta order
   statistic — AND reports a measured floor value, so likely needs elements
   of both; your own reasoned call).
4. **A proof-architecture audit per `docs/inventor-protocol.md` section 8**
   (`knowledge/techniques/KN-TECH-080.md`) if this protocol is proof-oriented
   in that section's sense: exact bottleneck and baseline reproduction,
   observation-collision search, quantifier order, method ceiling, and
   nearby-object control — BEFORE approving any implementation or expensive
   experiment. `3d71ca`'s and `8f8f45`'s own `proof_search_map` fields (both
   already filed, both already populated) are a head start, not a
   substitute — verify them against the actual frozen protocol you draft,
   not merely copy them forward.

## What it does not do

Does not run any measurement. Does not mark the hypothesis `approved` or
spend compute — per `/design-experiment` step 4, the frozen contract is
presented for confirmation before approval; per this program's own
`AGENTS.md` rule 1, only a committed Coordinator decision (via the ledger
archive, later in this batch) can move a hypothesis past `specified`. Does
not mint the notarizing archive task's own identifier or any other
downstream task id — those are minted by the orchestrating session once this
task's own output (specifically: how many artifacts, what shape the split
notarization takes) is known, matching this goal's own established pattern
(PREREG-7's own authorship preceded and informed its own notarizing archive
task's specification).

## Next steps after this task completes

1. The returned hypothesis, PREREG document, and experiment specification are
   read and verified by the orchestrating session against this goal's own
   established rigor bar (PREREG-4 through PREREG-7 precedent) before
   anything is staged.
2. `H-MLKEM-*` and `EXP-MLKEM-*` identifiers are minted (two-scope verified)
   and the drafted records are saved under their real filenames.
3. A Coordinator-only NOTARIZING snapshot archive commits the frozen PREREG
   text ALONE (zero producer artifacts), per this goal's own split-producer
   discipline, verified via `git log --all` (0 prior commits) before staging.
4. Only then is the lead producer (executor role) dispatched to run the
   frozen protocol — real BKZ reduction, real CBD sampling, real FIPS 203
   compression — bounded by the budget this task's own PREREG names.

## Artifact

    coordination/goals/GOAL-MLKEM-005/batches/BATCH-3b9962/tasks/TASK-20260814-dfaa60/task_card.md
