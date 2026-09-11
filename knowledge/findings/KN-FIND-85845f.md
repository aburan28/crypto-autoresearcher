---
id: KN-FIND-85845f
type: internal_finding
title: Formal-group digit identity for explicit hard lifts holds exactly at toy scale; canonical-height leak certified; anomalous break confirmed at the predicted step
tags:
- ecdlp
- toy-scale
- formal-group
- p-adic
- digit-identity
- canonical-height
- leak-demonstration
- non-homomorphic-section
- instrument-artifact
confidence: established
internal_refs:
- EV-ECDLP-95ec68
- DEC-20260911-74c9dc
- EXP-ECDLP-a26bde
- H-ECDLP-6a9479
proof_status: derivation
proof_refs:
- experiments/EXP-ECDLP-a26bde/derivation_note.md
- experiments/EXP-ECDLP-a26bde/analysis.md
added: '2026-09-11'
superseded_by: null
---

## Finding

On five frozen global elliptic curves `E/Q` with small-integer rational
points, reduced at twenty toy primes (10-14 bits, good ordinary reduction,
`gcd(n,p)=1`, `#E(F_p) != p`), `H-ECDLP-6a9479`'s claims (1), (2) and (4)
hold exactly as stated, each independently re-verified by a method distinct
from the producing driver's own aggregation/certificate code
(`EV-ECDLP-95ec68`, `DEC-20260911-74c9dc: support`, strength `strong`):

- **The digit identity** (claim 1): with `t` the unique prime-to-`p`
  torsion section and `d(P) = (psi(E_1-component of P) / p^v) mod p`,
  `d(mS^) = m*d(S^) mod p` holds exactly on **1360/1360** instances
  (5 curves × 4 primes × 68 m-values), independently re-derived from raw
  per-datum records by code that does not import the driver's own
  aggregation logic. Zero mismatches.
- **The size law** (claim 2): the log-log slope of the numerator bit-size
  of `x(mS^)` against `m` (for `m >= 16`) is 2.00 within the pre-registered
  `+-0.05` band on every instance (measured range `[1.9983, 1.9999]`,
  independently refit to ~1e-14 agreement with the reported values).
- **The leak and the break** (claim 4): from an explicit lift
  `T' = (m+jn)S^`, the scalar `m` is recovered and certified by `[m]S=T` on
  **277/277** attempted (m,j) pairs, independently re-verified via
  `harness.toycurve.EllipticCurve.mul` (a method distinct from the p-adic
  solver path); 683 companion pairs were skipped under a pre-declared,
  budget-driven infeasibility cap (`infeasible_estimated_bits_exceeds_cap`,
  fixed before the run), 0 certificate failures. On the anomalous toy curve
  (`#E(F_p) = p` exactly), the torsion-section construction refuses at
  exactly the predicted step (division by `n=p` inside `E_1`), matched by
  self-check 5's 24/24-certified positive control on a non-anomalous
  synthetic instance.

**Claim (3) (the Teichmuller non-homomorphic contrast) is explicitly NOT
promoted as supported or rejected here** — see "What is NOT established"
below; it is scoped `refine` in `DEC-20260911-74c9dc`, pending a protocol
amendment named in that decision's `next_actions`.

Claim tier: **toy** throughout (5 curves, 20 primes, `m` to 256, one
anomalous object). No attack and no exponent claim: the leak arm consumes
the scalar `m` to build the lift it reads from, and is a demonstration of
the digit-identity mechanism, never a recovery result. Nothing here bears
on cryptographic-scale hardness.

## Methodological finding: an instrument pitfall for Teichmuller-contrast tests

A secondary, reusable result for anyone building a "canonical Teichmuller
section" as a non-homomorphic contrast against a torsion/formal-group
splitting: a section realized as **fixed-x Teichmuller lift + Hensel-lifted
y** (`omega(x0 mod p)`, the unique `(p-1)`-th root of unity congruent to
`x0` mod `p`, paired with a Hensel square-root for `y`) will coincide
**exactly** with the true reduction of the global lift, at *every* prime and
*every* precision, whenever a tested point's x-coordinate is a rational
integer equal to `+-1` — the only rational integers that are universal
`(p-1)`-th roots of unity for every odd prime. This produces a spurious
"linear/homomorphic-looking" digit agreement at exactly those multiples,
unrelated to any real homomorphism in the section.

Concretely (`EXP-ECDLP-a26bde`, curve 2, `S^=(1,6)` on `y^2=x^3+9x+26`):
the doubling slope `lambda=(3*1+9)/(2*6)=1` exactly, so `2S^=(-1,-4)`
exactly over `Q`. The Teichmuller/Hensel section therefore reproduces
`2S^`'s reduction with zero p-adic correction at every one of curve 2's four
primes, producing an agreement at `m=2` that is a **global rational
coincidence**, not four independent per-prime accidents, and not evidence
about homomorphism one way or the other. Anyone reusing this instrument
pattern should exclude, or specially flag, any tested multiple whose
x-coordinate reduces to `+-1`.

A second, independent design defect compounds this in `EXP-ECDLP-a26bde`
specifically: the `m=1` entry in the same pooled statistic is a
mathematical tautology (the driver computes the baseline digit `u_S` and
the `m=1` loop entry `u_{1S}` via the byte-identical function call on
byte-identical arguments — the same computation invoked twice, confirmed by
direct reading of `driver/stage23.py`), and the pre-registered `3/p`
falsification threshold is uncalibrated to the tested ladder's 68-sample
resolution (the coarsest measurable nonzero rate, `1/68 ~ 0.0147`, already
exceeds `3/p` at every tested prime). Both defects are in the experiment's
design and are independent of the curve-2 coincidence above.

## What is NOT established

- Claim (3) itself: whether the canonical Teichmuller section is or is not
  systematically non-homomorphic is **neither confirmed nor contradicted**
  by `EXP-ECDLP-a26bde` as run. Every non-trivial agreement observed (4 of
  1340 non-tautological trials, all four in curve 2 at `m=2`) is fully
  explained by the instrument artifact above; zero *unexplained* deviations
  from the "agrees only by chance" prediction were found. This is a
  measurement-instrument blind spot in this specific test, not a result
  about the underlying uniqueness-of-homomorphic-section mechanism
  (`KN-TECH-73630e`).
- The curve-2/`m=2` explanation is a derivation cross-checked three ways
  against committed raw data (numerator-bit-length, exact digit coincidence
  restricted to `m=1,2`, identical recurrence across all four of curve 2's
  primes), not a re-executed numerical confirmation — the reviewing
  dispatch had no Bash/Python tool. It is elementary and independently
  checkable by any reader from the doubling formula and
  `instrument.py`'s `teichmuller_lift_scalar`/`hensel_lift_sqrt`
  definitions; a follow-up numerical confirmation is named in
  `DEC-20260911-74c9dc`'s `next_actions`.
- No transfer beyond the tested toy scale (5 curves, 20 primes, `m` to 256)
  is claimed or implied.
