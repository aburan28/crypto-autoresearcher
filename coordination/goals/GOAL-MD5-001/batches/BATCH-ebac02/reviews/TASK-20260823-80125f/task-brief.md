# Task brief — TASK-20260823-80125f (red-team resume)

You are the RED TEAM reviewer for GOAL-MD5-001, batch BATCH-ebac02, round 1 of
review-plan-87c429.yaml. This is a RESUME of TASK-20260822-87c429, which failed
on infrastructure (output-limit truncation) before producing any report. The
validator's joints (V1-V4) have final verdicts and are OUT of scope for you.

All paths below are relative to the repository root (your working directory).

## Your joints (from the frozen review plan)

- **R1** — The distribution actually separates seed-lottery from construction-
  defect from model-defect at the granularity the routing decision needs.
  Proves-too-much controls (run the criterion against objects whose verdict is
  KNOWN): (i) the ANOM-1 S=9 object from batch 4 (proven independent of one
  free word, KN-TECH-bb7e9f) MUST be flagged collapsed by the same criterion
  applied to its measured counts; (ii) the RC-5 null object (non-multiplexer
  mixer, same shape, by construction does NOT collapse) MUST PASS the
  criterion. If the criterion flags neither, or both, it is not measuring the
  construction and the routing answer is VOID — say so. Then: is the reported
  distribution's shape (and its confidence at n >= 100) actually distinguishable
  from a seed-lottery model at the declared tolerance?
- **R2** — The RC-4 static mask-survival argument is sound: a free word's
  varying bits that do not survive the (y XOR z) multiplexer mask at some F
  application on the path to the declared component cannot contribute to
  distinctness, and the check predicts the collapse. Proves-too-much: run the
  identical mask argument on the ANOM-1 S=9 construction, where the conclusion
  (no discriminating power over word9) is KNOWN TRUE from the blind proof — the
  argument must reproduce it from the mask ALONE; if it needs anything beyond
  the mask, it is not the general predictor its claim requires. Then check the
  argument against the batch-5 CTL-PO5(b) object (bits DO survive the mask, the
  observable still collapses for an unrelated reason): the check must be stated
  as necessary-not-sufficient, or the report overclaims.
- **R3** — The cost model is honest and the routing granularity adequate:
  compare the declared ceilings (120 s per sweep run) against the
  wrapper-measured wall-clock in the run manifests; a "seconds" claim resting
  on the 120 s ceiling with the actual time unreported is a misstatement. Check
  the deadline was armed (term f) and would have fired on a 10x slowdown. Then
  the granularity question: if the distribution is, say, a 60/40 split between
  two shapes, does the routing decision (seed vs criterion vs construction)
  actually change at that confidence? If not, the honest output is
  "inconclusive at n=100, recommend n=X", and the batch must say so.

**Failure signature (state it explicitly in the report):** if the criterion
flags neither the known-collapsed ANOM-1 object nor the known-good null mixer,
or attributes the CTL-PO5(b) collapse to the mask, the routing answer derived
from the distribution is void and the report must say so.

## Blind re-derivation (PHASE 1 — do this FIRST)

Quantity: the injectivity threshold count (1 - eps) * 2^k at BOTH 32-bit and
window/12-bit resolution, for the declared eps and the declared k of the
batch-5 construction.

Work ONLY from: the frozen criterion statement in
`ledger/decisions/DEC-20260822-40bf14.yaml` (next_actions item 3(a)), the
declared k, the declared eps, and the RFC 1320 (MD4) / RFC 1321 (MD5) standard
step schedules. Do NOT read, before this phase is complete and written down:
`harness/run_md4_seed_sweep.py`, any manifest under
`coordination/goals/GOAL-MD5-001/batches/BATCH-ebac02/tasks/TASK-20260822-767bb1/runs/`,
or the producer's execution report / derived analysis
(`.../TASK-20260822-767bb1/execution-report.yaml`, `derived-analysis-b6.json`).

Write `blind-rederivation.yaml` (same directory as this brief) with every
arithmetic step and the two resulting integer thresholds. THEN — and only then —
move to PHASE 2. In the report's blind_rederivation block, compare your
independently derived thresholds with the frozen quantity the records claim:
agreement is evidence about the quantity; disagreement localises to one of the
two implementations and is reported as such (it is a first-class finding, not
an error state).

## PHASE 2 inputs (read AFTER blind-rederivation.yaml is written)

- Review plan: `coordination/goals/GOAL-MD5-001/batches/BATCH-ebac02/review-plan/review-plan-87c429.yaml`
- Object under review (snapshot-frozen): receipt
  `coordination/goals/GOAL-MD5-001/batches/BATCH-ebac02/archives/TASK-20260822-b325fe/snapshot-receipt.json`;
  driver `harness/run_md4_seed_sweep.py` (sha256 4aa7b6f0c5d5c7883a463aebc9f49edf8581e64ad1bf4eeee4fa78b34a2b0fe9);
  run dirs `coordination/goals/GOAL-MD5-001/batches/BATCH-ebac02/tasks/TASK-20260822-767bb1/runs/RUN-MDFIVE-b6-{primary,null}-{md4,md5}-prod` (manifest.yaml + raw-result.json each);
  execution report `.../TASK-20260822-767bb1/execution-report.yaml`.
- ANOM-1 S=9 (batch 4): `coordination/goals/GOAL-MD5-001/batches/BATCH-af29f6/tasks/TASK-20260821-de817d/execution-report.yaml` + its `runs/` raw results; blind proof `knowledge/techniques/KN-TECH-bb7e9f.md`.
- CTL-PO5(b) (batch 5): `coordination/goals/GOAL-MD5-001/batches/BATCH-7215fa/tasks/TASK-20260821-372d67/` (execution-report.yaml, runs/RUN-MDFIVE-b5-gate_and_controls/) and the gate decision `.../BATCH-7215fa/tasks/TASK-20260821-fad775/gate-decision.yaml`.
- Frozen contract / ceilings (R3): `experiments/EXP-MDFIVE-8f0fe3/specification.yaml`.
- The Coordinator's prior and its falsifiable prediction: as recorded in the review plan (do not seek it anywhere else).

## Prohibitions

- DO NOT read `coordination/goals/GOAL-MD5-001/batches/BATCH-ebac02/reviews/TASK-20260822-40389d/` or `.../reviews/TASK-20260822-7f5ed3/` (sibling validator reports).
- DO NOT read `ledger/decisions/DEC-20260822-d7c2d0.yaml` or `ledger/evidence/EV-MDFIVE-b0def7.yaml` (post-review Coordinator compositions — your reading must be independent).
- DO NOT read `coordination/goals/GOAL-MD5-001/quarantine/` under any circumstances.
- Write ONLY inside `coordination/goals/GOAL-MD5-001/batches/BATCH-ebac02/reviews/TASK-20260823-80125f/`. Never modify any other file in the repository.

## Deliverables (both in your task directory)

1. `blind-rederivation.yaml` — PHASE 1 output (see above).
2. `red-team-report.yaml` — top-level key `red_team_report` with:
   - `id`, `task_id: TASK-20260823-80125f`, `batch_id: BATCH-ebac02`, `goal_id: GOAL-MD5-001`, `review_plan: review-plan-87c429.yaml`, `snapshot_reviewed: TASK-20260822-b325fe`, `role: red-team`
   - `verdict`, `verdict_one_line`, `claim_under_review`
   - `blind_rederivation`: quantity, derived_from (the allowed inputs), `ordering_attestation` (state that this file was completed before any blind_from read), the two derived integer thresholds, `agreement_with_the_records_claim`
   - `per_joint_verdicts`: one entry each for R1, R2, R3 — verdict (SOUND / OVERTURNED / INCONCLUSIVE) with the worked reasoning and the numbers behind it
   - `proves_too_much`: method, per-object results (ANOM-1 S=9, RC-5 null, CTL-PO5(b)), and the explicit failure_signature test result
   - `coordinator_prior_comparison`: the plan's falsifiable prediction (>= 50% of seeds at the 12-bit threshold on either primitive flips the routing to SEED and overturns the prior) assessed against the raw results — including the MD5 limb, which you must evaluate on its own numbers
   - `review_attestation`: `task_id: TASK-20260823-80125f`, the complete list of paths you read, explicit statements that you did NOT read the two validator report directories or the quarantine, and the PHASE 1/PHASE 2 ordering attestation
   - `inference`: requested policy `review-adversarial`, declared model `gpt-5.6-sol`, declared effort `xhigh`, and the statement that the authoritative session-level provenance is `run-receipt.json` in this directory (written by the Coordinator after the run) — do not self-describe the runtime beyond what the Coordinator's brief states
   - `stop_reason`
3. Any working scripts / intermediate computations you need, also in your task directory.

## Conduct

- A timeout, crash, or tool failure is NOT evidence against any mathematical
  hypothesis. If a tool fails, record the exact error verbatim, work around it
  if you can, and say so in the report; never fabricate a command output,
  timing, statistic, or citation (AGENTS.md rule 5).
- Claim ceiling: analyzed. You challenge and adjudicate; you do not promote any
  hypothesis status.
- The run is externally time-boxed at 40 minutes from start. Check elapsed
  time with `date -u` when you start and as you go; if you are within ~5
  minutes of the box with work remaining, stop starting new computations,
  write the report with the findings you have, and set `stop_reason` to
  "wall-clock budget" naming exactly which joint work is incomplete.
- Verdicts must be earned: cite the specific file and the specific number for
  every claim. Prose alone does not carry a finding.
