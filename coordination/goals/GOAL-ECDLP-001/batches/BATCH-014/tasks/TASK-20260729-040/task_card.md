# TASK-20260729-040 — Freeze the EXP-STR-004 two-arm B-sweep contract, its derivation note and its feasibility table

**MIRROR ONLY.** The authoritative card is the `tasks[]` entry with this id in
`coordination/goals/GOAL-ECDLP-001/batches/BATCH-014/dispatch_queue.json`.
Where this mirror and the queue disagree, **the queue governs and the
disagreement is a defect to report**, not to resolve by preference.

- **Role:** coordinator
- **Depends on:** none
- **Archived by:** TASK-20260729-041
- **Budget:** 3600 s, 2 GB, `maximum_runs: 1` (the schema rejects 0; this card executes nothing)
- **Inference policy:** `coordinator-orchestration-code`, no fallback, no degradation

## Objective

Convert `DEFER-BATCH009-001` into ONE frozen contract `EXP-STR-004` at status
`review_required` — the two-arm B-sweep of **arm A-prime** and **arm E-prime**
over the fourteen NAMED `(curve, B, m)` cells — plus the **derivation note**
that `DEC-20260727-009` requires archived BEFORE execution, plus the
**feasibility table**.

## Write scope

- `experiments/EXP-STR-004/specification.yaml`
- `experiments/EXP-STR-004/derivation_note.md`
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-014/tasks/TASK-20260729-040/`

## The load-bearing constraints

1. **Two arms and no third.** Arm A-prime = phi-invariant factor base with the
   line-303/304 dedup and zero-filter **disabled**; arm E-prime = phi-free
   closure emitting each sigma-orbit once and never suppressing.
   `harness.endomorphism_la.main()` is forbidden as an entry point.
2. **Fourteen named cells**, each named individually: ten ladder cells at
   CURVE-J12S1 with `m = 2` (B = 12, 13, 24, 25, 48, 49, 96, 97, 192, 193), two
   cross-curve cells at CURVE-J16S3 (B = 96, 97), two arity cells at
   CURVE-J12S1 with `m = 3` (B = 12, 13).
3. **PRED-ID-STR.** Every prediction is an identity of NAMED SETS at a NAMED
   cell. **No prediction is a cardinality.** A measured cardinality equal to a
   predicted cardinality with a different member set is
   `cardinality_only_agreement` and **counts as disagreement**.
4. **Matched base-row budget** `R_base(cell)`, a function of B alone, identical
   across arms; both closures unconditional; suppression count pre-registered
   as zero and reported beside alpha.
5. **The derivation note** derives the square-branch identity, why row `i`
   vanishes, why the first B rows are aligned exactly when `B mod 3 == 0`, and
   the **closed-form rule defining `T(cell)`**. Labelled `derivation`, never
   `proved`.
6. **Certificate discipline.** Base rows carry `decomposition` certificates;
   appended rows carry `none` with the reason. The Sage verifier is invoked
   **through the `sage` binary**, never as a Python import, and is independent
   of `harness/toycurve.py`.
7. **Budgets in the contract's own stopping rules:** 900 s per run, 7200 s
   total, 900 s Sage sub-cap, 2 MiB per run directory, 64 MiB tree, mandatory
   pre-flight disk check with a below-5-GiB stop. **Every breach is
   infrastructure signal, never a negative mathematical result.**
8. **The `mixed` branch must be reachable** — the verdict rule is defined over
   set equalities, not complementary predicates. This repairs the EXP-STR-003
   defect EV-STR-003 observation O-5 names.
9. RC-7 declared **inapplicable** with its reason and its cost. RC-8 and RC-D
   bind. RT21-1's false power sentence is not reproduced in any form.
10. **Make no commit.** TASK-20260729-041 commits these files.

## Completion gate

G1–G13 in the queue entry. In summary: contract complete at `review_required`
with `approved_by: null`; two arms and no third; fourteen cells named;
PRED-ID-STR in the contract's own text; derivation note defining `T(cell)`;
matched budget and unconditional closures; certificate discipline; solver fact
carried with provenance and limits; budgets and their meanings; `mixed`
reachable; feasibility table complete; ceiling and prohibitions present;
`tools/allocate_id.py --check` results recorded verbatim with a collision
reported as a STOP.
