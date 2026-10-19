# Degree-5 closure at C19: feasibility, not a result

Observations and derivations only. No claim about 1 in W_5 is made; **the question is not answered.**

## Measured (calib.json; engine #2410 lfdclose2.c, 1 thread, 4-core container, 15 GB RAM)
Saturating (satisfiable) m=3 systems, D=5, so the closure runs to its fixpoint:
| N | columns | wall s | peak RSS MB |
|--:|--:|--:|--:|
| 24 | 55,455 | 412 | 1,550 |
| 26 | 83,682 | 1,082 | 2,880 |
| 28 | 122,438 | 2,826 | 5,460 |

## Derived
- wall = 1.21e-9 * ncols^2.43 s; RSS = 4.5e-5 * ncols^1.59 MB (3-point log-log fit; no uncertainty estimable from 3 points).
- C19 (N=40, D=5): 760,099 columns, 72.2 GB per dense matrix, fit 98 GB RSS (a floor-ish figure: the engine holds two copies per chunk, so >= 145 GB), 2.7 d single-core by fit (up to ~7 d at 8 iterations).
- Host to request: >= 256 GB RAM (card: CARD-d5-c19.md). 768 GB is not required for this test.
- Fit sanity check, D=4 C19: fit 4.0 GB vs 3.7 GB recorded for crypto's engine; fit time ~1.8e3 s vs 3,964 s measured for lfdclose2 on C19a (the C19a run had 8 iterations, the calibration runs 3), so the fit understates iteration-heavy cases by ~2x.

## Not done (stated as missing)
- hky_par cross-check at D=4 and the m=4, l=5 cell: crypto build was denied in this session.
- Any run at N=40 or D=5 on a C19 instance.

## What the existing data does and does not say (descriptive)
- Degree 4 is refuted from N=36 at m=2 and N=40 at m=3, l=7 (#2410; crypto dreg_closure_scale).
- Both thresholds sit at similar N, so C19 (N=40) is just past the 4->5 transition. A "1 in W_5 at C19" outcome would therefore be expected and would NOT show the degree is bounded; only a failure (>=6) at m=3 would be informative, and that needs W_6 (millions of columns).
- #2214's "flat at 3-4 to N=40-54" holds only while m*l <= 18 (m=2: n <= 32). See correction-2214.md.
