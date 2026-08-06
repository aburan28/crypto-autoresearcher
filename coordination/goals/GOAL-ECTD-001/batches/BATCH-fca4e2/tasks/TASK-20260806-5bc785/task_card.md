# TASK-20260806-5bc785: Independent validation of the EXP-ECTD-001 run package

- **goal:** GOAL-ECTD-001
- **batch:** BATCH-fca4e2
- **role:** validator
- **state:** queued
- **priority:** 80
- **depends_on:** TASK-20260806-4455ac
- **review_required:** False (this task is itself the required independent review of TASK-20260806-983eed)
- **archived_by:** TASK-20260806-411ffd

## Objective

Independently verify run-set validity before any interpretation is trusted:

- Expected run count (2: impl + screen).
- Schema-complete manifests.
- Seed integrity (no duplicated/missing seeds among 201-205, or documented
  infrastructure substitutions only).
- Raw/summary agreement.
- Control comparability across all seven required controls.
- Planted-control recovery, recomputed from raw data, not trusted from a
  summary.
- Permutation-stability of any claimed outlier, recomputed from the raw
  permutation table.
- That the reported `decision_branch` is what `spec.decision_table` actually
  implies from the raw data.
- No trapdoor / crypto-scale / exponent-improvement language in any artifact.

## Constraints

- `independent_session: true` REQUIRED. Do not originate or edit the run
  artifacts under review.
- Verdict: `valid | invalid | incomplete`, plus the recomputed
  `decision_branch`.
- An invalid or incomplete run set is an evidence-integrity finding
  (AGENTS.md), not a negative result on H-ECTD-001. State concrete defects.
- Do not edit producer or snapshot artifacts; write findings only.

## Completion gate

- Verdict recorded with rationale tied to raw artifacts, not summaries.
- `independent_session: true` and model metadata recorded.
- Recomputed `decision_branch` stated explicitly.
