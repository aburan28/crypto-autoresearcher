# EXP-CERTBIN-4e92d7 implementation

Written from `experiments/EXP-CERTBIN-4e92d7/specification.yaml` (version 1)
under TASK-20260923-6f1ad4. Pure Python 3.11 + numpy (bit-packed GF(2)); no
compiled helper, no Sage, no GPU. `src/macaulay_export.py` is not used.

## Modules

| file | responsibility |
|---|---|
| `gf2n.py` | F_2[t]/(t^17 + t^3 + 1): schoolbook and exp/log-table multiplication, inverse, trace, half-trace, square root, and the irreducibility test (gcd(t^{2^i} - t, f) = 1 for i = 1..8 and t^{2^17} = t). |
| `curve.py` | Y^2 + XY = X^3 + AX^2 + B: affine group law, scalar multiplication, the deterministic x-lift, trace-based point count, naive point count (small fields, for the self-test), S_3 evaluated with schoolbook arithmetic only (used by C-WIT). |
| `macaulay.py` | Weil descent: generic multilinear expansion of S_3(x_1, x_2, x_R) to the 17 x 172 matrix E(r), the affine basis E^0, E^j, and the scalar evaluation of the 17 Boolean equations. Fixed-shape Macaulay matrix M_D: row order (mu by degree, then lexicographic index tuple; row = mu_index * 17 + k), column order (descending degrevlex, v_0 > ... > v_17, constant last), bit packing. |
| `elim.py` | THE SOLVER (column-major forward elimination, smallest original unused row index as pivot), the separate row-sequential pass for Z_D, canonical-JSON sha256 trace encodings, fixed-schedule replays (18 affine planes at once, and direct), and small rank helpers. |
| `oracles.py` | Oracle A (O(2^l) quadratic root finding over V, half-trace), oracle B (bit-sliced exhaustive evaluation over 2^18 assignments), witness re-verification (C-WIT), the rational flag, and PS0. |
| `families.py` | Phase 1: curve and points, the reference rule, test targets, and the instances of F-S3, F-PLANT, F-RANDX, F-AFF-1..3 and F-NULLF2 (F-S3-REV reuses F-S3), with both oracles, witnesses and the C-AFF identity. |
| `engine.py` | Phases 2-6: per (family, D) eliminations, the four traces, target-vs-reference comparisons (match per granularity, f_div, divergence column), modal reference, affine forms, direct-replay C-AFF check, hazard tables, PS0/PS1/PS3 per instance, sizes and saving ratios per reference. |
| `analysis.py` | Phase 8 statistics: M1-M5, secondary metrics, tail checks, instrument checks and invalidation rules, and DR-1..DR-8. |
| `report.py` | Phase 8 writer: every declared artifact, the independent raw-result recomputation and its agreement check, the manifest, the environment file and run-report.md. |
| `stats.py` | Clopper-Pearson, Wilson, exact binomial tails and intervals, entropy, Mann-Whitney U. |
| `driver.py` | CLI entry point: plan/spec verification, memory cap, checkpoints (one per phase, family and D), phases 1-6, phase 7 (`--phase determinism`, separate process), phase 8 (after phase 7, via `--resume`). |
| `selftest.py` | Phase 0: C-SELF items and C-FIX, seed S_selftest; writes selftest.json. |
| `make_trial_plan.py` | Writes trial-plan-v1.json from the specification (seeds, counts, phases, outputs, draw procedures and interpretations; no drawn value). `--dev` writes a development plan with other seeds, which the driver accepts only with `--dev` and only for an output directory outside the repository. |

## Commands

```sh
python3 experiments/EXP-CERTBIN-4e92d7/impl/make_trial_plan.py --spec experiments/EXP-CERTBIN-4e92d7/specification.yaml --run-id RUN-CERTBIN-3b7e05 --out experiments/EXP-CERTBIN-4e92d7/trial-plan-v1.json
python3 experiments/EXP-CERTBIN-4e92d7/impl/selftest.py --out experiments/EXP-CERTBIN-4e92d7/runs/RUN-CERTBIN-3b7e05/selftest.json
python3 experiments/EXP-CERTBIN-4e92d7/impl/driver.py --spec experiments/EXP-CERTBIN-4e92d7/specification.yaml --plan experiments/EXP-CERTBIN-4e92d7/trial-plan-v1.json --run-id RUN-CERTBIN-3b7e05 --out experiments/EXP-CERTBIN-4e92d7/runs/RUN-CERTBIN-3b7e05
python3 experiments/EXP-CERTBIN-4e92d7/impl/driver.py ... --phase determinism     # separate process (C-DET)
python3 experiments/EXP-CERTBIN-4e92d7/impl/driver.py ... --resume                # phase 8
```

## Speed invariant (column pass)

After the columns before c are processed, every unused row is zero in all
columns before c. At a pivot column, every unused row with a 1 is XORed with
the pivot row. At a non-pivot column, no unused row has a 1. XORs only add
unused rows into unused rows. The XOR at column c can therefore start at word
c >> 6. The replays use the same offset, because the entries they read at
later steps lie in columns greater than c_k. The self-test checks the op log
(p, c, X) against a literal set-based transcription of the rule on random
matrices.

## Z_D and the nesting

Every XOR adds a row p into a row with a larger original index. So a row that
the column pass zeroes lies in the span of earlier rows, and the zeroed rows
are exactly Z_D (|Z_D| = R_D - rank_D). The separate row pass computes Z_D
independently, and C-PASS compares the two.
