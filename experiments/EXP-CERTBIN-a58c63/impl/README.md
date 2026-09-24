# EXP-CERTBIN-a58c63 implementation

Written from `experiments/EXP-CERTBIN-a58c63/specification.yaml` (version 1)
under TASK-20260924-6ab0d8. Pure Python 3.11 + numpy 2.4.6 + mpmath (exact
tails); no compiled helper, no Sage, no GPU. The regime-A arm is COPIED from
`experiments/EXP-CERTBIN-4e92d7/impl/` (reviewed) and generalized; every change
is listed in `impl-provenance.json` (source sha256, unified diff, reason).
Nothing in `EXP-CERTBIN-4e92d7/` is imported or edited.

## Modules

| file | origin | responsibility |
|---|---|---|
| `gf2n.py` | copied, generalized | F_2[t]/(f) for n in {17, 19}; the n = 19 pentanomial by exhaustive lexicographic search; table and schoolbook multiplication, trace, half-trace, sqrt |
| `curve.py` | copied, unchanged | Y^2 + XY = X^3 + AX^2 + B; group law, counting, schoolbook S_3 |
| `macaulay.py` | copied, generalized | regime A: Weil descent `Descent(F, l)` and the fixed-shape GF(2) Macaulay matrix (Stage-1 conventions) |
| `elim.py` | copied, unchanged | regime-A solver, row pass, traces, replays, forms |
| `oracles.py` | copied, generalized + new oracle C | oracle A (root finding over V), oracle B (exhaustive 2^{2l}), oracle C (direct evaluation of g_0 on V x V), witnesses, PS0 (regime A) |
| `families.py` | copied, rewritten for Stage 2 | phase 1 per cell: curve/points, references, targets of all eight families, C-TR, x(2E) classes |
| `engineA.py` | copied from `engine.py`, restructured | regime-A per-(family, D) processing; per-target work is a pure function (shardable) |
| `hull.py` | new | hull H = h_0 + W, K_rank_hull, Sigma / Sigma_H, C-FORMS (matmul path), C-SURV, C-HZERO, TS1R evaluation set with exact bands |
| `regimeB.py` | new | regime-B shape (rows/columns/L_V), THE F_{2^n} SOLVER with in-pass divergence classification, row pass (Z), traces, fixed-schedule replay |
| `engineB.py` | new | regime-B per-family processing, delta / C-DELTA / C-RANKB / PS0 per instance, sizes and savings, K_B probes, C-BREAK |
| `delta.py` | new | Phi = Vand^{-1}, Coef = Phi F Phi^T, delta, top identity |
| `detmod.py` | new | INDEPENDENT determinant (own tables, Markowitz pivoting) for C-BREAK |
| `certs.py` | new | PS0' certificate extraction (tracked eliminations) |
| `statsx.py` | new | exact Clopper-Pearson, Poisson intervals, conditional-binomial ratio interval, exact binomial bands and tails (Fractions / mpmath 60 digits) |
| `analysis.py`, `report.py`, `runreport.py` | new (structure after Stage 1) | phase 8 metrics, controls, DB-1..DB-12, artifacts, raw-result recomputation, manifest, run report |
| `common.py`, `make_trial_plan.py` | new | constants transcribed from the spec; trial-plan writer |
| `driver.py` | copied, restructured | pilot phase, phases 1-5 and 7a, determinism phase, phase 8; checkpoints, memory caps, workers |
| `selftest.py`, `selftest_gf2.py` | copied, extended | C-SELF and C-FIX for both fields and both regimes |

`verifier/verify_cert.py` imports nothing from `impl/`.

## Commands

See the specification's `execution` block; `command.txt` in the run directory
records the exact commands used.

## Regime-B speed invariant

As in the Stage-1 README: after the columns before c are processed, every
unused row is zero at every column before c, so a row update at column c only
touches the pivot row's nonzero columns >= c. The self-test compares the op
log (p, c, X) with a literal dictionary-based transcription of the rule on 20
random matrices per field, the row-pass Z with a naive prefix-rank Z, and the
rank with an independent elimination.

## Workers

The per-target work of every unit is a pure function of (target, references).
With two workers the targets are split by `multiprocessing` (fork) and joined in
order; the driver enables the second worker only after the serial and sharded
outputs for the 20 lowest-idx F-S3 targets of cell (17, 6), both regimes, are
byte-identical (checkpoint `workers-identity`, recorded in the manifest).

## Protocol version 2 (AMD-20260924-3a9f06)

The run executes the frozen specification (version 1) plus the committed
amendment AMD-20260924-3a9f06 (DEC-20260924-c41e7a): first-match divergence
classification R0-R6 and C-CLASS (`regimeB.column_pass`), E3 success at the
target's first non-pivot column (`engineB.target_record_B`), the
T_strict-guided computation and C-REPLAYB v2 (`regimeB.guided`,
`engineB.replayb_v2`), one S_probe stream across cells (`driver.probe_stream`),
the retired-seed table (`common.cell_seeds`), exhaustion stops with the two
E_SAT enumerations (`families.sat_population`, `families.sat_population_vv`),
the stream-01 log (`families.SharedCurveSeq`), C-TR v2 (`families.curve_classes`)
and the per-family modal rule. Development runs use seeds below 10^6
(`common.dev_cell_seeds`, `common.DEV_FIXED_SEEDS`) and write outside the
repository only.
