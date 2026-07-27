---
id: KN-FIND-006
type: internal_finding
title: >-
  The Semaev/Weil-descent Macaulay rank deficit is bounded structural syzygy
  content equal to 8*dim(V); the generic degree-4 baseline is exactly the
  classical trivial syzygies and the excess is a vanishing fraction
tags: [semaev, weil-descent, groebner, degree-of-regularity, syzygy, betti, rank-deficit, semi-regular, binary-field, ecdlp, bounded, negative-result]
confidence: reported
internal_refs: [EV-DREG-001]
proof_status: empirical_only
proof_refs:
  - experiments/EXP-DREG-001/analysis.md
  - experiments/EXP-DREG-001/DREG_DEFICIT_CLOSED_FORM.md
  - experiments/EXP-DREG-001/characterization/README.md
  - experiments/EXP-DREG-001/characterization/deficit_by_degree.py
  - experiments/EXP-DREG-001/characterization/syzygy_degree3.py
  - experiments/EXP-DREG-001/characterization/syzygy_degree4.py
  - experiments/EXP-DREG-001/characterization/alpha_action_test.py
claim_tier: toy
added: 2026-07-27
superseded_by: null
---

## Finding

For Weil-descended Semaev systems over GF(2) (t=3, chained S_3, k = dim V), the
degree-D Macaulay rank falls short of the Bardet–Faugère–Salvy semi-regular
prediction by an amount that is **exactly closed-form at low degree and bounded**,
not growing with system size.

Writing `deficit(D) = pred[D] - rank(D)` (the excess quotient dimension, i.e. the
extra non-Koszul syzygies):

- **Support-matched null arm is exact**: deficit = 0 at n = 12, 15, 17, 18, every
  replicate. Any sem-arm deficit is therefore real structure, not predictor bias.
- **deficit(D=3) = 1** for every full system (n >= 12).
- **deficit(D=4) = 8k - 1**, exact for k = 3,4,5,6,7 (n = 9,12,15,18,21).
- **Cumulative deficit at D=4 = 8k = 8*dim(V)** for full systems.
- The **generic degree-4 syzygies are exactly the classical trivial ones** —
  n_q Frobenius (q_i^2 = q_i) plus C(n_q,2) Koszul pairs — verified by
  rank(G) = nrows - pred[4] to the integer (78/120/171 at k=4/5/6). Everything
  beyond that baseline is the deficit.
- **Mechanism** (degree 3, exhibited): a subset-sum of descended quadrics
  degenerates to an **affine** form P (the quadratic parts cancel), and the
  multiplier is its exact complement, so the relation is the Boolean identity
  `P*(1+P) = P + P^2 = 0`. The Semaev-specific content is the degeneration; the
  support-matched null admits none (degree-3 kernel 0).

While the system grows ~5x (pred 29,418 -> 145,881), the deficit stays in a narrow
band and its *relative* size decays 4.49% -> 1.37%. The extra syzygies are a
vanishing fraction of the system, so they supply **no asymptotic leverage** against
ECDLP.

## Scope and limitations

- Measured at D <= 5 and n <= 21 over **binary** fields (Weil descent of a
  chained S_3 system), not prime fields. It bears on KN-OPEN-002 by analogy and
  by shared machinery, but is not a prime-field measurement.
- A **fixed-degree cross-section is the wrong instrument**: the cumulative D=5
  series (1322/1862/1823/1999 at n=12/15/17/18) looks "bounded but non-monotonic"
  only because D=5 sits at different depths relative to each system's regularity,
  and because n=17 is a structurally deficient system (nb = 2n+1, 34 equations).
  Degree-resolved measurement removes both artifacts. Do not extrapolate a
  fixed-D deficit series.
- The generic/extra isolation is valid only for **full** systems (exactly n
  quadrics + n cubics in nb = 2n variables); n=9 and n=17 are deficient cells.
- `8*dim(V)` is measured-exact over k = 3..7, **not derived**. Two mechanism
  hypotheses were refuted: generator-level Frobenius as the source (those hold in
  the null too), and alpha-orbit invariance under the naive companion-matrix
  action (it fails even on the universal generic space, so the operator is
  incomplete). A derivation needs the correct Weil-restriction/Frobenius symmetry,
  or a direct count of the degeneracy subspace
  `{c : deg(sum c_i f_i) < max deg}` — the favoured open route.

## Evidence

- EXP-DREG-001 run records, including the matched null control
  RUN-DREG-001-VALIDATE-N18-NULL (completed_valid, deficit 0) that closed the
  validation ladder at n = 12/15/17/18.
- `experiments/EXP-DREG-001/analysis.md` (sections 9-13) and
  `experiments/EXP-DREG-001/DREG_DEFICIT_CLOSED_FORM.md`.
- Reproducible probes: `experiments/EXP-DREG-001/characterization/`
  (`deficit_by_degree.py`, `syzygy_degree3.py`, `syzygy_degree4.py`,
  `alpha_action_test.py` — the last recording the refuted alpha-orbit action).
  Exact GF(2) rank via the archived `peel_and_rank` engine.
