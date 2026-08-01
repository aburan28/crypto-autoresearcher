# EXP-SEMAEV-001 — factor-base scaling: restoring a measurable cost trend

Analysis-side follow-up to the run records in `../runs/`. **Not** an instrument run
(no run receipts): these probes call `harness.semaev.measure_s3_decomposition`
directly, because the run id `RUN-SEMAEV-{rho,gb}-b{bits}-s{seed}` does not encode
the factor-base size, so a factor-base sweep cannot be recorded under the existing
id scheme without ambiguity.

## The problem this addresses

The canonical runs hold `factor_base = 14` fixed while `p` grows. Decomposition
probability for the S_3 (length-2) test is ~ `F^2 / 2p`, so with F fixed it decays
as 1/p and the S_3 target stops decomposing:

| bits | trivial ideal | decompositions found |
|---|---|---|
| 8 | 0/4 | 4/4 |
| 10 | 3/4 | 1/4 |
| 12 | 4/4 | **0/4** |
| 14 | 4/4 | **0/4** |

Where `is_trivial_ideal` is true the Groebner basis is `{1}`: `basis_size = 1` and
`max_degree_proxy = 0` are **degenerate values, not cheap solves**. The apparently
flat Groebner cost at bits >= 12 is an empty measurement, not evidence about cost
scaling (KN-OPEN-002).

## Calibration — cost is a function of F alone

`fb_calibrate.py` sweeps F at fixed field size. Groebner seconds, by (bits, F):

| F | bits 8 | bits 10 | bits 12 |
|---|---|---|---|
| 14 | 0.047 | 0.047 | 0.048 |
| 24 | 0.160 | 0.164 | 0.163 |
| 32 | 0.362 | 0.354 | 0.365 |
| 48 | 1.031 | 1.084 | 1.061 |
| 64 | 2.034 | 2.285 | 2.391 |

Cost is **independent of p at fixed F** (identical to ~3 significant figures across
three field sizes) and grows in F with empirical exponent ≈ 2.3–2.8. This is the
direct explanation for the flat timings in the canonical runs: F never moved, so the
cost could not move either. The ideal is
`<S3(x1,x2,x_R), fV(x1), fV(x2)>` with `deg fV = F`, so F — not p — sets the cost.

## Scaled sweep — F = ceil(sqrt(p)), holding decomposition probability ~0.5

`fb_scaled_sweep.py`, seeds 1 and 2:

| bits | seed | p | F | F²/2p | gb_secs | size | maxdeg | decomposed |
|---|---|---|---|---|---|---|---|---|
| 8 | 1 | 241 | 16 | 0.53 | 0.064 | 3 | 4 | yes |
| 8 | 2 | 137 | 12 | 0.53 | 0.033 | 3 | 3 | yes |
| 10 | 1 | 1009 | 32 | 0.51 | 0.352 | 1 | 0 | no (trivial) |
| 10 | 2 | 787 | 29 | 0.53 | 0.278 | 3 | 4 | yes |
| 12 | 1 | 3571 | 60 | 0.50 | 1.958 | 4 | 5 | yes |
| 12 | 2 | 3343 | 58 | 0.50 | 1.796 | 3 | 4 | yes |
| 14 | 1 | 11777 | 109 | 0.50 | 10.917 | 2 | 2 | yes |
| 14 | 2 | 9479 | 98 | 0.51 | 8.031 | 3 | 4 | yes |
| 16 | 1 | 52721 | 230 | 0.50 | 111.023 | 3 | 3 | yes |
| 16 | 2 | 50441 | 225 | 0.50 | 111.894 | 4 | 4 | yes |

**The measurement is restored: 9/10 cells decompose** (versus 0/4 at bits >= 12 with
fixed F). Mean Groebner seconds per size: 0.049 / 0.315 / 1.877 / 9.474 / 111.459.

Fitting cost against p across consecutive sizes gives exponents **1.20, 1.32, 1.44,
1.54** — i.e. per-test cost ≈ p^1.2…1.5, and rising over the measured range
(equivalently ≈ F^2.4…3.1). For matched context the rho baseline on the same
instances used 6–123 group operations.

## Interpretation, and what this does NOT show

- With the factor base scaled to keep the S_3 test non-degenerate, the cost of a
  **single decomposition test** grows faster in p than the generic baseline's
  *total* ~sqrt(p) work — and a full index calculus needs ~F ≈ sqrt(p) such
  relations on top of that. In this toy regime there is no advantage; this is
  consistent with the corpus verdict elsewhere in the workspace.
- Absolute timings are **not** crypto-scale claims: sympy uses Buchberger, not an
  optimised F4/F5, and p <= 2^16 here. Per the harness README's metrics-honesty
  note, only trends versus parameters are interpreted.
- `max_degree_proxy` stays small (2–5) and does not grow with p; it is confounded by
  the number of solutions in the ideal (at bits 8 with a factor base saturating the
  curve it reached 21 in calibration). It is an implementation-bound proxy and must
  not be read as a degree of regularity.
- bits 10 seed 1 did not decompose despite F²/2p ≈ 0.51 — decomposition is
  probabilistic and these are single samples per cell, not a distribution claim.
- Two seeds per size is a small design; the exponent trend (1.20 → 1.54) is a
  measured direction, not a fitted asymptotic law.

## Reproduce

```
cd <workspace root>
TMPDIR=/Volumes/Volume/tmp python3 experiments/EXP-SEMAEV-001/factor-base-scaling/fb_calibrate.py
TMPDIR=/Volumes/Volume/tmp python3 experiments/EXP-SEMAEV-001/factor-base-scaling/fb_scaled_sweep.py
```

The scaled sweep takes ~4 minutes, dominated by the two bits=16 cells (~112 s each).
Do not pipe it through `tail` — that buffers until exit and hides incremental rows.
