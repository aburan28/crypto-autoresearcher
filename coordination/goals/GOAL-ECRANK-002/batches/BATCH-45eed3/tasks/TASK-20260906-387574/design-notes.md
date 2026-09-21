# Design notes — TASK-20260906-387574 (BATCH-45eed3)

Design producer for the successor contract. Records where each of the eleven
successor_contract_requirements of DEC-20260906-7448cf lands in
experiments/EXP-ECRANK-73275e/specification.yaml (tag [SR-n] in the contract)
and in ledger/hypotheses/H-ECRANK-36d8d7.yaml.

| SR | Requirement (DEC-20260906-7448cf) | Landing in EXP-ECRANK-73275e |
|----|-----------------------------------|------------------------------|
| 1 | per-draw logging (solved y-tuple + per-coordinate squareness verdicts) | required_artifacts[1]; metrics.secondary per-draw log; P2 tail check reports the full per-draw log |
| 2 | draw-stage ENCOUNTER control (full support on the sub-box; a plant-shaped subspace with a known point at height <= H met with nonzero probability) | inputs.audit_source + inputs.audited_b_tuples; metrics.primary audit_verdict (in-box fraction, |S|, N_a, expected vs observed meets); F1_audit; controls IV-5 (self-test) |
| 3 | name the ledger run schema in required_artifacts (nested run: record + RUN_REQUIRED_TOP + command.txt/environment.json) | required_artifacts[0] (explicit, names the predecessor omission) |
| 4 | declared per-run attempt ceiling, every attempt preserved | budget.maximum_attempts_per_run 12 [SR-4]; control IV-6; stopping rule 5; required_artifacts (attempt directories) |
| 5 | named seed for the planted control in replication.seeds | replication.seeds 760808 with seeds_note (named planted-control seed); the predecessor's derived-seed practice explicitly forbidden |
| 6 | planted-control exponent gate under the FROZEN window [0.699, 1.301], per-decade [5, 20] | control IV-3 (frozen window and per-decade ratios stated) |
| 7 | multi-class certificate coverage (>= 1 instance with 4 distinct twist classes, or explicit untested statement) | control IV-8; metrics.secondary certificate coverage; success criterion G2 |
| 8 | planted-instance distinctness/independence clause (O-08/C6 spirit) | control IV-9 (forbids the predecessor's shared-A-tuple / shared-h0 shape); replication.independent_instances |
| 9 | exact ops_cap_respected flag, no 1% tolerance, stop exact at >= 1.0e8 | budget.counted_ops_note [SR-9]; stopping rule 2 |
| 10 | wall_seconds both semantics (internal monotonic + timestamp span) | metrics.secondary [SR-10]; required_artifacts (op ledger line) |
| 11 | IC-1 counting-convention exclusions counted or explicitly bounded | confounder in the hypothesis; metrics.secondary op ledger with IC-1 exclusions itemized [SR-11]; required_artifacts |

## Design decisions recorded

1. Two-part hypothesis (M-A attribution, M-B construction) so the negative
   outcomes are first-class: F1_audit (support defect) and F2_n6 (infeasibility
   pattern) RESOLVE the artifact-vs-mathematics ambiguity either way. The
   success criterion says so explicitly (G1/G2 with negatives).
2. The audit reads only committed bytes bound at a20a49b6a (the snapshot of the
   predecessor's run package); audited b-tuples are the first three of the
   R3-armB record stream (AT-0/1/2), frozen in inputs.audited_b_tuples.
3. N_a (planted-meet draw count) is derived at run start from the exactly
   computed |S| with expected meets >= 5, recorded before any meet is counted —
   the expected-meet arithmetic is part of P2 so a zero is decidable.
4. The n = 8 arm (R5) is secondary and descriptive at this scale; only n = 6 is
   load-bearing for the construction claim (one quadratic, no measured local
   obstruction, HEUR-1 exponent +2).
5. The null family (R6) is frozen in the run source before any R6 step, with
   its infeasibility proof in the run record — the control-before-belief object
   for the construction solver.
6. No recalled external numbers anywhere in the pre-registered prediction:
   anchors are EV-ECRANK-8b35bb (0/80000, < 3e-4, 4.5e-5), the predecessor
   contract (q = 10^-3 floor, 10^4 sample), and the d = 1 closed form (control
   anchors 5 and 7 at n = 6/8).
7. Budget mirrors the predecessor (8 enumerated runs, 1.0e8 counted-ops cap per
   run binding, 7200 s per run, 8 GB, zero descent, no network) with the new
   12-attempt ceiling; the audit runs are read-only exact arithmetic and far
   cheaper than the caps.

## Status

- hypothesis: H-ECRANK-36d8d7 filed `specified`.
- contract: EXP-ECRANK-73275e frozen at version 1, `review_required`,
  approved_by null. NO self-approval; the approval gate (user confirmation +
  committed Coordinator decision) is a later step per the opening decision
  DEC-20260906-8ab17b.
