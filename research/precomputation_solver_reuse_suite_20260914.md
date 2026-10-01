# Prime-field ECDLP solver-precomputation experiment suite

Date: 2026-09-14

## Goal

Determine how much of the point-decomposition solver workload for fixed-curve
prime-field ECDLP index calculus is reusable across target points, and whether
the reusable fraction grows with field size.

This is deliberately distinct from the earlier fixed-curve preprocessing line.
EXP-FCP-002/003 measured factor-base construction reuse with B=14 and m=2.
DEC-20260726-003 weakened H-FCP-001 after that construction cost plateaued at
~1.6% of Groebner cost. The experiments below instead target the dominant
solver work itself: F4 symbolic preprocessing, Macaulay layouts, pivot
schedules, partial Groebner state, SAT clauses, and parameterized
specialization.

## Non-negotiable accounting

Every experiment reports both cold and warm cost. Cache construction,
serialization, lookup, deserialization, specialization, validation, and any
fallback work are charged.

For N target DLP point-decomposition queries, report

- `T_cold`: median target solve without reusable solver state.
- `T_pre`: one-time reusable-state construction cost.
- `T_warm`: median target solve using reusable state, including lookup and
  specialization.
- `S = T_cold / T_warm`.
- `T_amortized(N) = (T_pre + N*T_warm)/N`.
- `e_amortized(N) = log2(T_amortized(N))` using a fixed operation/time unit.
- cache bytes and peak resident bytes.
- exact-success/fallback rate.

No result may be called an ECDLP complexity improvement merely because online
cost falls. A complexity claim requires evidence that the warm/cold advantage
scales with n after total offline cost is reported.

## Shared fixture policy

Use generated ordinary prime-field toy curves only until the mechanism is
understood. No production-key targets are required. Fix curve, factor-base
rule, decomposition arity, solver, monomial order, and implementation version
inside a comparison cell. Change only the target unless the experiment
explicitly sweeps another variable.

Initial bit-size ladder: 11, 13, 16, 20, 24, 28, 32, stopping on budget.
Use at least three deterministic curve seeds and enough target points per cell
to estimate both SAT/decomposable and UNSAT/nondecomposable behavior where the
factor-base density permits it. Positive planted decompositions must be used
when random targets are too sparse.

Every warm result must be independently verified against the original
polynomial system. Trace/cache failure must fall back to the cold solver and be
reported, never silently dropped.

## Experiment ladder

1. `EXP-PRECOMP-001` — structural overlap across targets.
2. `EXP-PRECOMP-002` — F4 trace replay.
3. `EXP-PRECOMP-003` — parameterized target Groebner specialization.
4. `EXP-PRECOMP-004` — partial Groebner/F4 prefix reuse.
5. `EXP-PRECOMP-005` — Macaulay matrix template cache.
6. `EXP-PRECOMP-006` — pivot/elimination-schedule stability.
7. `EXP-PRECOMP-007` — incremental SAT and target-independent clause reuse.
8. `EXP-PRECOMP-008` — cache/Redis transport overhead accounting.
9. `EXP-PRECOMP-009` — cross-target generalization matrix.
10. `EXP-PRECOMP-010` — factor-base selection under warm-solver cost.
11. `EXP-PRECOMP-011` — decomposition-arity sweep under precomputation.
12. `EXP-PRECOMP-012` — relation precompute vs solver precompute under equal
    offline budget.
13. `EXP-PRECOMP-013` — scaling law for warm/cold speedup versus field size.

## Priority order

Execute 002 -> 005 -> 006 -> 004 -> 003 -> 007 -> 013 first. 001 is the
instrumentation/calibration prerequisite and may be run concurrently with 002.
008 is required before any remote-cache result is promoted. 009-012 are
follow-ups once a reusable mechanism survives the first ladder.

## Interpretation gates

- `S < 2`: engineering noise unless exceptionally cheap to deploy.
- `2 <= S < 5`: useful implementation optimization.
- `5 <= S < 10`: strong reusable solver state.
- `10 <= S < 50`: significant fixed-curve amortization.
- `S >= 100`: investigate for a genuinely parameterized/offline-online
  mechanism; do not infer an asymptotic gain without EXP-PRECOMP-013.

For EXP-PRECOMP-013 fit both a constant-speedup model and
`log2(S(n)) = alpha*n + beta`. Treat `alpha > 0` as a research signal only if
confidence intervals exclude zero across multiple curve seeds and the result
survives total-cost accounting.

## Relationship to existing evidence

The suite does not reopen the exact mechanism weakened by DEC-20260726-003.
That decision found factor-base construction negligible relative to Groebner
solving for the tested S3 setup. The new suite asks whether the Groebner/SAT
solver work itself contains a reusable target-independent component.
