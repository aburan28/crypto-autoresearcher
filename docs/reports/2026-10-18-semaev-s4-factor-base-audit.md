# Audit of KN-OPEN-5b3a08: `s4_expr` and `build_factor_base` in `harness/semaev.py`

**Date:** 2026-10-18. **Status:** code audit plus exact toy-prime test; no scientific trial, no speed claim, no archived record edited. **Requested by:** repository owner, 2026-10-18 (index-calculus review integrity findings). **Test:** [`tests/test_semaev_s4_exact.py`](../../tests/test_semaev_s4_exact.py). **Graph/PDF:** none owed. This is a code audit with no run and no canonical graph source affected; the checked-and-unchanged determination is recorded here as the visual-record rule asks.

## Verdicts

| Question | Verdict |
| --- | --- |
| Q1. Was the `s4_expr` defect real? | **Yes.** The pre-repair construction (sequential `.subs()` of `{x1: x3, x2: x4, x3: t}`) returns a polynomial in `x1, x2, x4` only: `x3` is gone. Reproduced on the current sympy (1.14.0). |
| Q1. Does the current `s4_expr` vanish exactly on `±P1±P2±P3±P4 = O`? | **Yes, on every tuple tested.** Curve `y^2 = x^3+2x+3` over `F_13` (18 points, 6561 x-tuples) and `y^2 = x^3+x+6` over `F_11` (13 points, 1296 x-tuples): 0 mismatches in both directions, degenerate tuples (repeated abscissae, 2-torsion) included. The legacy construction fails the same comparison on 2353 of 6561 and 648 of 1296 tuples (on the `F_13` curve 768 spurious zeros and 1585 missed relations). |
| Q1. Is the repair in the shared file? | **Yes.** `origin/main` (f279a4918c) `harness/semaev.py:52` uses `subs(..., simultaneous=True)`. The repair is recorded as accepted on 2026-08-13 by [CORR-20260813-d9f0fa](../../ledger/corrections/CORR-20260813-d9f0fa.yaml) (EXP-SEMAEV-a097b5). Before this audit the only regression test was one frozen witness and a degree check (`tests/test_harness.py::test_s4_has_exact_support_degree_and_frozen_witness`), which cannot distinguish a repair from a lucky witness. |
| Q2. Does `build_factor_base` draw from the target subgroup? | **Not by default, and that is a scope choice, not a defect.** `scope="full_curve"` (default, byte-identical to the legacy sampling) draws from `E(F_p)`. `scope="target_subgroup"` is opt-in, enumerates multiples of `P`, and checks each canonical lift has order dividing `n`. No archived caller opts in. The risk is the cofactor confound KN-OPEN-5b3a08 Q2 names, not wrong abscissae. |

## Method

1. Read `harness/semaev.py` (`s3_expr`, `s4_expr`, `build_factor_base`) and the KN-OPEN-5b3a08 text.
2. Decided the group relation by direct point arithmetic, independent of any summation polynomial: for every x-tuple `(x1,x2,x3,x4)` over the toy prime, the relation holds iff the sets `{P1±P2}` and `±{P3±P4}` meet (point at infinity included). That is the definition `±P1±P2±P3±P4 = O` with the overall sign factored out.
3. Evaluated `s4_expr(a,b)` mod `p` at every x-tuple of abscissae of finite curve points and compared vanishing with the relation, both directions.
4. Positive control: rebuilt the legacy construction in the test and required the same comparison to fail on it (`x3` absent from its free symbols and more than 0 mismatches). The test is therefore shown to see the defect, not merely to pass on the repaired code.
5. Checked the factor base on the `generate_instance(seed=1, field_bits=6)` instance (`n = 11`, cofactor 5): the default scope returns abscissae whose lifts are outside the order-`n` subgroup; the subgroup scope returns only subgroup abscissae.

Command and result: `python3 -m pytest -q tests/test_semaev_s4_exact.py` gives `5 passed`. (`tests/test_harness.py` has 5 failures in a sparse checkout that lacks `coordination/` and `experiments/` files; they are file-not-found failures unrelated to this change.)

## Archived runs that used the defective path

Method: for every run manifest of an experiment whose code imports `harness.semaev.s4_expr`, read the recorded `commit` and test whether `harness/semaev.py` at that commit contains `simultaneous`. "Defective" means the recorded commit lacks the repair. The recorded commit is the repository HEAD at run start in a shared worktree and several manifests note a dirty tree, so this is strong but not conclusive evidence of the code that ran; the 2026-08-13 CORR record reaches the same conclusion for MTIC and FIB.

| Experiment | Runs (commit lacks repair) | Reaches `s4_expr` on the result path | In CORR-20260813-d9f0fa |
| --- | --- | --- | --- |
| EXP-MTIC-001 | 11: RUN-MTIC-001 to 010, 010b (a2947025e2, 2026-07-29) | Yes: `run_mtic.py::s4_setup` first line | yes |
| EXP-FIB-001 | 10: RUN-FIB-001 to 008 including 006B and 006C (1ba846482a and 53d3fed02f, 2026-08-07) | Yes: `decompcost.py` | yes |
| EXP-ICINV-e0cd8f | RUN-ICINV-e0cd8f-m3class (76a48ff3d8, 2026-08-11); RUN-ICINV-e0cd8f-s0 and -s1 (91eff12458, failed_infrastructure, no results) | **Yes for m3class**: `harness/exp_icinv_e0cd8f_m3class.py::s4_generators/s4_support` feed the m4 columns of `control-set-invariants.json` | **no, new finding** |

**New finding (not in the CORR record).** RUN-ICINV-e0cd8f-m3class archived `s4_support` of 227 in 274 of its 276 m4 records (225 in the other two; 138 curves, each with an m4 and a gauge m4 record) in its control-set invariants. Recomputed with the repaired `s4_expr` at `p = 4001`, curves `(a,b) = (3603,2402)` and `(2646,1291)`, the support is 439. The archived m4 invariants (`s4_support`, `singular_locus_*`) of that run were produced from a polynomial missing `x3`. The m3 columns use `s3_expr` and are unaffected. No numeric correction is made here; a CORR record is a Coordinator act (see the decision request).

Checked and not affected by the defect: RUN-ICINV-geom-* (their m4 stage uses `harness/exp_icinv_geometry.py`, which imports only `s3_expr`; their `s4_support: 2` is a separate computation); EXP-DTREE-001 (local `semaev_fix.py`); EXP-MONO-7c653b, -7f39bf, -805a02 and EXP-SEMAEV-002 (recorded commits 9c0f463dd1, 147b5cd1fc, 53aac6d887 contain the repair); EXP-PFDR-5726af (imports `s3_eval` only).

Review-time scripts that import `s4_expr` (EXP-MONO-805a02 red-team `rt*.py`, `coordination/reviews/pfdr-battery-20260904/.../rt_semaev_control.py`) are not archived run results and were not classified.

Local history limit: the clone's history is truncated at PR #2309 (2026-10-16), so `git log -S` cannot date the repair on `main`; the dates above come from run-manifest commits and the CORR record.

### Q2 exposure (confound check, not an error list)

Experiment code that calls `build_factor_base` with the default `full_curve` scope and could carry the cofactor confound: EXP-BINSTD-375338, -38e4ad; EXP-DS-001; EXP-DTREE-001 (instances, slope); EXP-ECDLP-1ed445; EXP-FIB-001 (has its own subgroup constructor); EXP-MONO-005b49, -64aaa4, -7f39bf, -805a02, -cb905d; EXP-MTBK-306bdb; EXP-MTIC-001; EXP-RT1476-001; EXP-SEMAEV-f48dd1; EXP-SEMBIN-d830d5; EXP-SGCP-EMBED-001; EXP-XOR-62b256, -7267e4. This was found by a path-level grep only. None was re-examined for whether it compares decomposition rates across cofactors.

## Classification

Correctness repair and regression test: engineering, not an improvement over the index-calculus baseline. No cost, `S`, or rho gap changes. Nothing here is a relabelling claim.

## What stays open

- The numerical effect of the defect on the 21 MTIC/FIB runs and the ICINV m4 columns is **not measured**. Matched reruns under the repaired code are required by CORR-20260813-d9f0fa before any comparison; this audit ran none.
- Whether Q2 changes any cross-cofactor comparison.
- KN-OPEN-5b3a08's `status` is unchanged; a decision request is filed in [`coordination/remediation/DECISION-REQUEST-20261018-ic-integrity.md`](../../coordination/remediation/DECISION-REQUEST-20261018-ic-integrity.md).
