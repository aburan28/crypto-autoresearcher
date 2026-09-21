# Experiment Contract: EXP-020 end-to-end solve-gate (m=3 Semaev IC vs rho)

Closes the campaign's most consequential gap (PAPER §6.2(iii)): every prior round metered *first-fall*,
a relation-generation **difficulty proxy**. This measures the **end-to-end index-calculus cost** —
relation generation × sparse linear algebra × target read-off — in counted operations, against the rho
baseline, and across sizes to extract the **scaling exponent** (the implementation-robust quantity).

## Hypothesis
End-to-end m=3 Semaev IC (factor base |FB| = L ≈ n^{1/3}, decomposition by Semaev S_4, linear algebra
over Z/n) has a total-cost scaling exponent **strictly greater than rho's 0.5**, so the IC/rho cost
ratio **grows** with n — no crossover at toy scale.

## Null hypothesis
IC total-cost exponent ≤ 0.5 (i.e. ≈ rho or better), or the IC/rho ratio shrinks toward a crossover.

## Baseline
Pollard rho with negation map, ≈ 0.886·√n group operations (implemented + verified end-to-end here).

## Parameters
- curve family: short Weierstrass y²=x³+ax+b / F_p, prime order n, P-256-like (a=−3 where possible).
- sizes: n ≈ 2^bits for bits ∈ {10, 12, 14, 16} (extend to 18 if feasible).
- factor base: L = max(4, round(n^{1/3})) smallest valid x-coordinates → base points F_0..F_{L-1}.
- decomposition: Semaev S_4(x1,x2,x3,x(R))=0, x_i ∈ FB, solved by enumerate-(x1,x2)+quartic-root-in-x3
  (an exact, fully-counted Semaev decomposition; upper-bounds the GB cost Yokoyama 2020 lower-bounds).
- relations collected: L + 8 (overdetermined), random (a,b), R = aP + bQ.

## Metrics (counted, not just wall-clock)
- IC: decomposition operations (quartic solves + S_4 evals), EC group ops (relation R-computation + sign
  lifting), #relations, #R-attempts, relation probability, linear-algebra dimension + GF(n) solve cost,
  wall-clock per phase, total.
- rho: EC group ops to collision, wall-clock.
- **Primary deliverable:** fitted exponent of total-IC-ops vs n and total-rho-ops vs n.

## Positive control
The IC must **recover the correct discrete log x** (Q = xP, x known) — proves it is a real solver, not a
proxy. rho recovers the same x.

## Negative control
A random non-curve linear system of the same dimension must NOT yield x (guards the linalg read-off);
and rho on the same instance independently recovers x (cross-check).

## Success criterion (for the resistance claim)
IC total-ops exponent > rho exponent (≈0.5) with the ratio monotonically growing over the 4 sizes; IC
verified to solve the DLP. ⇒ "no early fall" upgraded to "no end-to-end win" at toy scale.

## Falsification criterion
IC exponent ≤ 0.5, or IC total-ops < rho total-ops at the largest size, or the ratio trending to cross.

## Reproduction command
```bash
sage round020_solvegate_ic_vs_rho.sage
```

## Expected failure modes
- FB too small ⇒ relation probability ~0 ⇒ relation gen dominated by attempts (still counted; raises IC
  exponent, consistent with hypothesis). - GB/quartic cost undercount if a faster decomposition exists
  (we use enumerate, an upper bound; note it). - toy-size constant-factor noise ⇒ rely on the exponent,
  not absolute crossover, and sweep ≥4 sizes.
