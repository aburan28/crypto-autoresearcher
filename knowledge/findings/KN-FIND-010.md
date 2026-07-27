---
id: KN-FIND-010
type: finding
title: >-
  A fixed factor base makes the prime-field S_3 decomposition measurement
  degenerate; with F scaled as sqrt(p) the Groebner cost is a function of F alone
  and grows as p^1.2-1.5 per decomposition test
tags: [semaev, point-decomposition, index-calculus, groebner, factor-base, prime-field, cost-model, measurement-artifact, ecdlp, negative-result]
confidence: reported
status: established
source_refs: [EXP-SEMAEV-001, KN-OPEN-002, KN-OPEN-001, KN-TECH-002, KN-TECH-003, KN-TECH-004, KN-TECH-011]
added: 2026-07-26
superseded_by: null
---

## Finding

Two coupled results about measuring S_3 (length-2) point-decomposition cost over
prime fields.

**1. Fixed factor base degenerates the measurement.** The S_3 decomposition
probability is ~ `F^2 / 2p`. Holding `factor_base = F = 14` fixed while p grows
makes the target stop decomposing entirely:

| field bits | trivial ideal | decompositions found |
|---|---|---|
| 8 | 0/4 | 4/4 |
| 10 | 3/4 | 1/4 |
| 12 | 4/4 | 0/4 |
| 14 | 4/4 | 0/4 |

Where `is_trivial_ideal` is true the Gröbner basis is `{1}`, so `basis_size = 1`
and `max_degree_proxy = 0` are **degenerate values, not cheap solves**. A flat
Gröbner cost at bits >= 12 is an *empty measurement*, and must not be read as
evidence that cost fails to grow with field size.

**2. Cost is a function of F alone; scaling F restores the trend.** Sweeping F at
fixed field size shows the cost is independent of p to three significant figures
(F=14: 0.047/0.047/0.048 s at bits 8/10/12; F=64: 2.03/2.29/2.39 s), growing in F
with exponent ~2.3-2.8. This is expected from the ideal
`<S3(x1,x2,x_R), fV(x1), fV(x2)>` where `deg fV = F`: **F, not p, sets the cost.**
That is the direct explanation of the flat canonical timings — F never moved.

Setting `F = ceil(sqrt(p))` holds `F^2/2p ~ 0.5` and restores a live measurement
(9/10 cells decompose). Mean Gröbner seconds then run
0.049 / 0.315 / 1.877 / 9.474 / 111.459 at bits 8/10/12/14/16, i.e. an exponent in
p of **1.20, 1.32, 1.44, 1.54** — rising over the measured range (~F^2.4-3.1).

**Reading:** with the factor base scaled to keep the test non-degenerate, a
*single* decomposition test already grows faster in p than the generic baseline's
*total* ~sqrt(p) work — and index calculus needs ~F ~ sqrt(p) such relations on
top of that. No advantage in this regime.

## Scope and limitations

- Toy scale (p <= 2^16) with sympy's Buchberger, **not** an optimized F4/F5.
  Absolute timings are not crypto-scale claims; only trends versus parameters are
  interpreted, per the harness metrics-honesty rule.
- `max_degree_proxy` stays 2-5 and does not grow with p. It is confounded by the
  number of solutions in the ideal (it reached 21 at bits 8 when the factor base
  saturated the curve), so it is an implementation-bound proxy and **must not** be
  read as a degree of regularity.
- bits 10 seed 1 did not decompose despite `F^2/2p ~ 0.51` — decomposition is
  probabilistic and these are single samples per cell.
- Two seeds per size: the rising exponent is a measured direction, not a fitted
  asymptotic law.
- The measured quantity is one decomposition test, not an end-to-end index-calculus
  cost (no relation collection, linear algebra, or descent accounting).

## Evidence

- EXP-SEMAEV-001 run records (rho + gb matched pairs), including the bits=14 tier
  completed to four seeds: RUN-SEMAEV-{rho,gb}-b14-s1, -b14-s2.
- `experiments/EXP-SEMAEV-001/factor-base-scaling/` — `README.md` with the
  recorded tables and caveats, `fb_calibrate.py` (cost is F-only),
  `fb_scaled_sweep.py` (F = ceil(sqrt(p)) sweep, bits 8-16).
