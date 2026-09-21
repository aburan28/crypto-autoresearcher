# Stage 0 derivation note — EXP-ECDLP-a26bde

## A. The splitting

For a prime `p >= 5`, a curve `E/F_p` with good reduction, and any lift
`E^/Q_p` (the naive lift: same Weierstrass coefficients, viewed over `Q_p`
instead of `F_p`), the reduction sequence

    0 -> E_1(Q_p) -> E^(Q_p) -> E(F_p) -> 0

splits on the prime-to-`p` part: for `n` with `gcd(n, p) = 1`, the torsion
lift `t: E(F_p)[n] -> E^(Q_p)[n]` is a homomorphic section, and it is the
*only* homomorphic section, because two sections differ by a homomorphism
from a group of order `n` into `E_1`, which is a pro-`p`, torsion-free
`Z_p`-module, and any homomorphism from an order-`n` group (`gcd(n,p)=1`)
into a torsion-free pro-`p` group is zero. So every point of `E^(Q_p)`
reducing into `<S>` (`S` of order `n`) is uniquely `t(R) + X` with `X` in
`E_1`, and the formal logarithm `psi: E_1 -> p Z_p` is a group isomorphism
onto its image (Silverman, *AEC*, Ch. IV; ledger citations:
`ledger/FINDING-PF-IC-001.md` ECFG-P1543-R0/R1, `KN-TECH-73630e`).

Consequently, for a global point `S^` of `E^(Q)` reducing to `S`, writing
`S^ = t(S) + X_S` with `X_S = [n]^{-1}([n] S^)` computed inside `E_1` (unique
`n`-division, since `n` is a unit in `Z_p`), the hard lift of `T = mS`
satisfies

    m S^ = t(m S) + m X_S,       psi(E_1-component of m S^) = m * psi(X_S).

Writing `v = v_p(psi(X_S)) >= 1` and `d(P) := (psi(E_1-component of P) / p^v)
mod p`, the identity `d(m S^) = m d(S^) mod p` follows exactly. This is
IDEA-20260905-848b77 part (B), which this experiment verifies numerically at
toy scale.

## B. The Teichmuller congruence

For `a` a nonzero residue mod `p`, `a^p ≡ a (1 + p q_p(a)) mod p^2`, where
`q_p(a) = (a^{p-1} - 1)/p mod p` is the Fermat quotient. `q_p(a) ≡ 0 mod p`
exactly when `a` is already (to first order) a fixed point of the `p`-th
power map mod `p^2` — the Teichmuller lift `omega(a)` (the unique `(p-1)`-th
root of unity in `Z_p` congruent to `a` mod `p`) is the honest such fixed
point to *every* precision, obtained here by Hensel-Newton iteration on
`f(x) = x^{p-1} - 1` (`instrument.teichmuller_lift_scalar`), not merely by
embedding `a`'s residue as a fixed integer (see BUG-EXP-a26bde-003 below,
where exactly that shortcut was tried first and found to give a spuriously
homomorphic-looking section).

## C. The first-order identity

For `P` on `E` and `X` in the formal group (image of `psi`), the addition
law gives, to first order in the formal parameter of `X`,

    x(P + X) - x(P) ≡ 2 y(P) * psi(X)   (mod p^2),

since the invariant differential `dx/2y` pulls back to `dt` on the formal
group and `psi` is its integral. This is checked numerically (self-check 4)
on random `(P, X)` pairs with `X` an explicit valuation-1 formal-group
point.

## D. The five frozen global curves and their reduction primes

Generated deterministically by `driver/curves.py` from `seed = 20260905`
(the contract's `replication.seeds`), by a seeded search over small-integer
`(x0, y0, A)` with `B = y0^2 - x0^3 - A x0` (so the point is exact by
construction), filtered for nonsingularity and infinite order of `S^` up to
the full m-ladder, then four reduction primes per curve in `[2^10, 2^14)`
with good ordinary reduction, `#E(F_p) != p`, and `gcd(n, p) = 1` for `n` the
order of `S = S^ mod p`. The full machine-readable list (including trace and
`n` per prime) is `frozen_curves_and_primes.json` alongside this note;
summarised here:

| curve | A | B | (x0, y0) | primes (p, n) |
|---|---|---|---|---|
| 0 | 3 | -315 | (7, 7) | (12853, 12958), (12889, 12790), (12893, 3270), (12899, 6433) |
| 1 | 9 | -801 | (9, 3) | (1129, 1086), (1151, 1164), (1153, 1137), (1163, 303) |
| 2 | 9 | 26 | (1, 6) | (7477, 930), (7481, 7428), (7487, 413), (7489, 3694) |
| 3 | 2 | -54 | (5, 9) | (14821, 415), (14827, 14785), (14831, 14852), (14843, 14744) |
| 4 | 9 | -134 | (5, 6) | (11927, 3909), (11933, 6021), (11939, 5962), (11941, 11824) |

One anomalous toy curve with a rational point (`#E(F_p) == p` exactly, found
by the same seeded search continuing past the five curves above so it is
never accidentally reused): `A=9, B=-397, (x0,y0)=(7,3), p=3673, order=3673`.

All twenty (curve, prime) pairs above have `v = v_p(psi(X_S)) = 1` (measured,
not assumed); no instance in this run has `v > 1`, so the tail check
"instances with v > 1 are listed" is vacuously satisfied (an empty list) and
the precision-`v+1`/`v+2` check reduces to the standard `Kreq = v+2 = 3`
used throughout.

## E. Protocol deviations and defects found and fixed during Stage 1

A previous, unreviewed attempt at this driver left five files on disk
(`exactcurve.py`, `formalgroup.py`, `padic.py`, `instrument.py`,
`derive_formulas.py`, `validate_projective.py`) with no self-check
transcript. `exactcurve.py`, `formalgroup.py`, `padic.py`,
`derive_formulas.py` and `validate_projective.py` were independently
re-verified (symbolic re-derivation of the projective addition/doubling
formulas and the `(t,w)`-chart identity via a fresh sympy session;
1700-comparison numeric validation against `harness/toycurve.py` over five
real primes; independent sympy re-derivation of the log series to degree 13,
matching `formalgroup.py` term for term) and kept as-is. `instrument.py` had
defects, found by direct testing before any self-check was trusted:

- **BUG-EXP-a26bde-001**: `curve_lift_projective` treated a point known only
  mod `p` as if `(x % N, y % N, 1)` were valid mod a much larger `N`; a
  point's mod-`p` residue does **not** satisfy the curve equation mod `p^2`
  in general (only the curve's own integer coefficients naively lift; the
  point does not). Fixed by adding `hensel_lift_point` (fix `x`, Hensel-lift
  `y`) for points only known mod `p`, and keeping the exact global reduction
  (`reduce_point_mod`) for points derived from a real rational point.
- **BUG-EXP-a26bde-002**: even after fixing 001, the `P - X_S` subtraction
  that produces `t(P)` silently returned a wrong, off-curve point at
  precision `K >= 2` under the original `WORKING_DEGREE=15` /
  `PRECISION_MARGIN=24`. Root cause: each near-identity chart conversion can
  produce a projective representative carrying a redundant common `p`-power
  factor, and the margin/degree were not generously sized against this
  compounding across the full `[n]P -> log -> /n -> exp -> subtract` chain.
  Fixed by raising `WORKING_DEGREE` to 80 and `PRECISION_MARGIN` to 40, and
  — more importantly — adding an **internal round-trip check**
  (`t(P) + X_S == P`, checked projectively at full working precision) inside
  `split_point` that raises `PrecisionInsufficient` rather than returning a
  silently wrong digit. This is what caught the defect in the first place
  and is what would catch a recurrence.
- **BUG-EXP-a26bde-003**: a minority of instances still needed more than
  margin 40 (measured: up to ~60) to pass the round-trip check. Fixed with
  automatic margin escalation (`split_point` retries at margins
  `40, 60, 75`, re-lifting the point at each precision via a caller-supplied
  `lift_fn`), capped at 75 to stay clear of `WORKING_DEGREE=80`'s log/exp
  truncation floor.
- **BUG-EXP-a26bde-004**: the first version of self-check (2)'s defect
  digit (`s(R) - t(R)`) computed the subtraction at bare `p^K` precision
  with no margin, which — for exactly the same reason as 002 — collapsed to
  an exact-zero `Z`-coordinate every time, reporting a false "always
  additive" defect. Fixed by computing at `K + 30` and truncating the digit
  down afterward.
- **Naming defect**: the inherited `non_canonical_section` (fixed `x`,
  Hensel-lifted `y`) was initially used as "the Teichmuller section" for the
  Stage 3 contrast, and measured as *fully homomorphic* (100% agreement,
  contradicting the pre-registered expectation): it is not actually the
  Teichmuller lift (which must satisfy `x^{p-1} = 1` exactly, via the
  multiplicative structure of `F_p^*`, not merely reduce to the right
  residue mod `p`). Added `teichmuller_lift_scalar` /
  `teichmuller_section` (Hensel-Newton on `x^{p-1} - 1`), verified
  `omega(a)^{p-1} = 1` and `omega(a) ≡ a mod p` directly, and used this for
  the Stage 3 contrast; `non_canonical_section` is kept only for self-check
  (2), where any non-homomorphic section suffices by the check's own design.
- **Leak-arm feasibility cap**: `T' = (m + jn) S^` can require a scalar of
  several times `n` (`n` itself up to `2^14`), and the exact rational height
  of `x(T')` grows with the *square* of that scalar (the size law being
  tested) with `fractions.Fraction`'s own gcd-normalisation cost growing
  faster still — measured directly: a scalar of ~39000 on this contract's
  own curve 0 did not finish an exact multiplication in 120 CPU-seconds.
  The leak arm therefore uses a size-law-informed pre-check (estimate
  `bits(m+jn)` from the same instance's already-measured size-law fit before
  attempting the exact computation) and skips, with a recorded reason
  (`infeasible_estimated_bits_exceeds_cap`, cap = 300,000 bits), any
  `(m, j)` pair whose estimated cost is too large; it also uses a smaller
  representative sample of the m-ladder (`LEAK_M_SAMPLE`, 12 values spanning
  1 to 256) crossed with the full `j in {-3,...,3}` rather than the full
  68-value ladder, to keep total compute bounded. This is a budget-driven
  scope decision, not a tuned-after-the-fact result: it was decided once,
  from a direct timing measurement, before the 20-instance run, and applied
  identically to every instance. See the execution report for exactly how
  many `(m, j)` pairs were computed vs. skipped per instance.

All five self-checks pass after these fixes; the transcript is
`selfcheck_transcripts/selfcheck_transcript.json` (also embedded as
`RUN-ECDLP-a26bde-000-selfchecks/raw-result.json`).
