# TASK-20260823-827765 — implementation notes and PROTOCOL DEVIATIONS

Producer notes for EXP-ECQ-0e0cbb. Everything here is recorded, not summarised
away. Deviations are listed first because they are the part a reviewer must not
have to hunt for.

## A. Protocol deviations, in full

1. **The intercept replication was executed out of the declared priority order,
   at position 6's own cost.** `step_5_priority_order_under_budget` ranks it (6),
   after RT-CONTROL-3 (5). It was in fact run after (5) as ordered — no deviation
   there — but its FIRST attempt (`RUN-ECQSTR-827765-008`) consumed ~470 s of the
   task's 3600 s before being killed, which shortened everything downstream. See
   deviation 4.
2. **SET B was not the 46-family / 2114-pair set the handoff names.** That exact
   partition could not be reproduced from the committed BATCH-541940 artifacts;
   the reproducible superset (96 census families of ceiling ≥ 12 × 73 t, minus
   1459 already-searched pairs = 5549) was used instead. Fully disclosed in
   `ranksearch.py`, in `rank_search_coverage.json`
   (`coverage.batch_541940_unfinished_SET_B.definition.reviewer_figure_disclosure`)
   and in report.md §3.
3. **`RUN-ECQSTR-827765-005` changed the instrument.** It re-attempted SET A's
   alarmed fibres at a 90 s PARI alarm rather than 20 s. Disclosed per row via
   `alarm_seconds`; the 20 s pass alone is what the pre-registered reference-rate
   comparison uses, and the 90 s pass is used only for coverage and for the
   rank-versus-height curve, where a longer point search can only add points.
4. **`RUN-ECQSTR-827765-008` failed as an `implementation_error` and was killed by
   the producer.** Its manifest was written BY HAND from the observed state, not
   by the run harness, because a signalled process cannot run its own exit hook.
   That is disclosed inside the manifest itself. It produced no deliverable and
   nothing from it is reported anywhere. Superseded by `RUN-ECQSTR-827765-010`.
5. **`RUN-ECQSTR-827765-007` reported the k = 0 proves-too-much object
   `NOT_RUN`.** Its candidate loop drew from six shuffled tuples and every one
   failed the |a − b| = 2 guard. The record stands unedited;
   `RUN-ECQSTR-827765-009` supplies the control, and both are reported.
6. **`RUN-ECQSTR-827765-002` produced a 6.46 MiB deliverable, above the declared
   `per_file_mib` of 5.** It was NOT truncated. The columnar rows were reduced at
   source — five repeated string columns replaced by integer codes plus a legend,
   with no row and no field dropped — and the enumeration was re-run identically
   as `RUN-ECQSTR-827765-003`, producing 4.00 MiB and reproducing every count to
   the digit. Both runs are recorded; RUN-002's own record states the size it
   wrote.
7. **`RUN-ECQSTR-827765-002S` is a smoke test** at spread ≤ 22, recorded as a run
   because every attempt is recorded. Its output went to scratch, not to a
   deliverable.
8. **The trace map P + P^σ was not constructed on either rung.** Stated in
   `null_controls.json` under `trace_map_disclosure` and in report.md §5.
9. **The Cremona check is a conductor bound, not a lookup.** PARI `elldata` is not
   installed and no network call is permitted. Decisive only in the ABSENT
   direction; a curve inside Cremona's range would have been marked
   `INCONCLUSIVE_LOOKUP_REQUIRED` and not reported as novel.

## B. What was reused, and what was written here

Reused unchanged from `BATCH-541940/tasks/TASK-20260823-416e78/scripts/`, whose
surface, admissibility and ceiling code two blind reviewers re-derived from
scratch and found correct: `mestre.py`, `surface.py`, `admissible.py`,
`measure.py`, `certify_candidates.py` (for `to_minimal` and `naive_height`), and
`exact_certify.py` unchanged from the BATCH-f2341e pipeline. Its **report prose**
was used for nothing.

Written for this task: `constants.py`, `prefilter.py`, `heights.py`, `runrec.py`,
`ranksearch.py`, `run001_fixtures.py`, `run002_enumerate.py`,
`run004_ranksearch.py`, `run005_retry.py`, `run007_controls.py`,
`run008_intercept.py`, `run009_k0.py`, `run011_deliverables.py`.

## C. Constants are read, never written

`constants.py` contains **no numeric literal** for the cell or the benchmark. It
reads each from its frozen file at run time and compares it against the audit
value **parsed out of `ledger/hypotheses/H-ECQ-0ed5c8.yaml`**, aborting on
mismatch. Because the audit value is parsed rather than typed, the rounding
defect validator F7 caught in BATCH-541940 cannot recur through this path. The
assertion was exercised at the head of every run: 3 checks, all matching, in
RUN-001, -002, -002S, -003, -004, -005, -006, -007, -009, -010 and -011.

## D. Budget and accounting

Task cap 3600 s wall clock, 4 GB, 80 runs, `per_file_mib` 5 /
`committed_total_mib` 25. Twelve runs. PARI was given 2 GB
(`allocatemem(2**31)`), inside the 4 GB cap; no memory breach occurred. Producer
compute totalled roughly 3.2 ks, inside the cap. No network call was made and
nothing was submitted to the ICARM endpoint.

## E. Inference

`requested_policy: executor-implementation`, recorded in every manifest's
`run.inference` block alongside the model that actually answered. This session
was launched without `AUTORESEARCH_POLICY`, `AUTORESEARCH_BACKEND` or
`AUTORESEARCH_MODEL` set, so the manifests record the session model
(`claude-opus-5`) and say explicitly that the adapter variables were unset rather
than inventing a resolution. `fallback_used: false`, `degraded: false`. No
downgrade was accepted.
