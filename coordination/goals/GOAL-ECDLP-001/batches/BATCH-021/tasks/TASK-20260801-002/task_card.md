# TASK-20260801-002 — Adversarial challenge to the RUN-DS-001-ctrl-unplanted control and its cost/claim framing

**MIRROR ONLY.** The authoritative card is the `tasks[]` entry with this id in
`coordination/goals/GOAL-ECDLP-001/batches/BATCH-021/dispatch_queue.json`. Where this mirror and the queue disagree, **the queue
governs and the disagreement is a defect to report**, not to resolve by preference.

- **Role:** red-team
- **Depends on:** none
- **Archived by:** TASK-20260801-003
- **Inference policy:** `review-adversarial`, fallback_allowed=True, independent_session_required=True

## Objective

Attack the RUN-DS-001-ctrl-unplanted package committed at 61cd52621e0a53669cee8f30af145f8193838362. Find the cheapest falsification, the hidden assumption, and the reading that would be wrong. Answer Q1-Q6 adversarially.

## Write scope

- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-021/reviews/TASK-20260801-002`

## Deliverables

- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-021/reviews/TASK-20260801-002/red_team_report.yaml`

## Constraints

1. READ THE RUN PACKAGE AT COMMIT 61cd52621e0a53669cee8f30af145f8193838362, NOT AT THE WORKING TREE. It is immutable and pushed. This batch exists because BATCH-020's TASK-20260731-045 archive is permanently unbindable (CORR-20260731-010); the snapshot-before-review guarantee is satisfied by that commit, not by an archive binding.
2. THE INSTRUMENT IS PRODUCER-AUTHORED AND UNREVIEWED. experiments/EXP-DS-001/implementation/ds001_driver.py gained --mode ctrl-unplanted (787 insertions, 2 deletions) written by the SAME session that ran it, in the same task. THIS IS THE PRIMARY REVIEW TARGET.
3. Interpret within scope only. Claim tier is toy (bits=20). No cryptographic-scale claim may be drawn.
4. Timeouts, crashes and infrastructure failures are never negative mathematical evidence.
5. Do not alter H-IC-001 or H-STR-002. Do not edit specification*.yaml, amendments/ or controls/.
6. MAKE NO COMMIT. TASK-20260801-003 is the ledger archive.
7. Do not change any hypothesis status or goal field; that is the Coordinator's in TASK-20260801-003.
8. Assume the producer-authored instrument is wrong until its code shows otherwise; name the specific line or function that would have to be correct for each headline number to stand.
9. Name the cheapest experiment that would falsify the unplantedness claim, and say whether this batch could run it.
10. Challenge whether an unplanted control that fails its own live-plant detection can support ANY reading of R, in either direction.
11. Charge end-to-end cost honestly: state what the 25s wall clock does and does not bound, and whether any cost claim is being smuggled in.
12. Q1 UNPLANTEDNESS: does harvest_real_unplanted draw targets with NO planted decomposition witness (claimed T = k*P, k uniform in [1,n-1])? Read the code, do not take the execution report's word.
13. Q2 NO SYNTHETIC SHORTCUT: is the live /4 plant companion free of the hardcoded synthetic known-answer path (synth_R/synth_Rn) that CTRL-RT025-UNPLANTED.yaml forbids?
14. Q3 BACKEND TRUTHFULNESS: are the charged-unit, search and null-arm paths behaviourally identical to the planted package, so BACKEND_ID ds001-v2-point-sum-membership+charged-units-v1 remains truthful?
15. Q4 THE CONTROL DID NOT PASS: live_plant_report.json reports planted_bug_detected false, which does NOT satisfy its own stated pass_condition. Adjudicate whether the control discharges, fails, or is inconclusive.
16. Q5 CI ANOMALY: R = 0.036552 lies BELOW its own 95% bootstrap CI [0.108, 0.415]. Confirmed pre-existing in 41 of 54 cells of the committed planted matrix. State what, if anything, R and R_null can support given a bootstrap that does not bracket its estimate.
17. Q6 R-1 LABEL: is r1_cell_label S1_eligible_on_null_axis correctly derived, and is it correctly scoped as an observation that a single cell cannot convert into S1 (spec requires >= 2 bit sizes)?

## Completion gate

- red_team_report.yaml written within write_scope; every one of Q1-Q6 answered explicitly with a verdict and its evidence; no fabricated metric; no commit made.
