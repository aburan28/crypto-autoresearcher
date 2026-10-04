---
id: KN-OPEN-9b4a2b
type: open_problem
title: >-
  Does an F_p-rational 2-torsion quotient of the n = m = 5 summation system on
  double-odd curves over F_{p^5} have ideal degree 2^16 = 2^{(m-1)^2}, and is it
  solvable within a stated memory envelope?
tags: [gfpn, ecgfp5, double-odd, summation-polynomial, semaev, 2-torsion,
  symmetrization, fhjrv, weil-descent, ideal-degree, groebner, msolve, pdp,
  index-calculus, extension-field, open, ecdlp]
confidence: reported
status: open
source_refs: [EV-GFPN-fc5950, DEC-20260923-d86ff2, EXP-GFPN-05ff43, H-GFPN-9a29be,
  RQ-GFPN-c01af8, CORR-20260923-064d0d, CORR-20260923-27ce4f, KN-LIT-8aff72,
  KN-LIT-673219, TASK-20260923-404bf9, TASK-20260923-aa277e]
added: 2026-09-23
superseded_by: null
---

## Statement

Let E be a double-odd curve y^2 = x(x^2 + a x + b) over F_q, q = p^5, with
b a non-square in F_q. EcGFp5 is such a curve: `b = 263z`, over
`F_p[z]/(z^5 - 3)`, `p = 2^64 - 2^32 + 1` (`KN-LIT-8aff72`). E has one
rational 2-torsion point T = (0, 0), and translation by T acts as
x -> b/x. The point-decomposition problem (PDP) asks to write a target R as a
sum of m = 5 points from a factor base. It reduces, by Weil descent, to a
square system of 5 equations over F_p derived from Semaev's S_6.

**The question.** For the `F_p`-rational `(Z/2)^{m-1} x| S_m` quotient of
that system, what is the ideal degree D at n = m = 5? Does it follow the
law `D = 2^{(m-1)^2}`, i.e. `2^16`? And is the quotient system solvable
within a stated memory envelope?

The quotient is built on a rescaled factor base. Because
`[F_{p^5} : F_p]` is odd, write `b = lam^2 * beta` with `beta` in `F_p*` a
non-square. The factor base is `{P : x(P)/lam in F_p}`. The unknowns are
`sigma_k(u_i + beta/u_i)` and `w = prod(u_i - beta/u_i)`, subject to
`w^2 = prod((u_i + beta/u_i)^2 - 4 beta)`.

For reference, the S_5-symmetrized system has `D = 2^20`, and the raw system
has mixed volume `5! * 2^20` (about 2^26.9).

## Why it is open, and what is known

- **The experiment that was meant to answer it did not.** `EXP-GFPN-05ff43`
  measured no m = 5 ideal degree for any arm. Arms (ii) and (iii) exhausted
  an 11 GiB RLIMIT_AS at `p' = 4111` in the degree-33 F4 round. That is an
  infrastructure boundary, not evidence about D (`CORR-20260923-3cbb89`).
- **Its arm (iii) was not the quotient.** It was the norm `S * S^(1)`, which
  is invariant under `(Z/2)^m x| S_m` and has arm (ii)'s support: 20349
  monomials at m = 5 (`CORR-20260923-064d0d`).
- **FHJRV's ring form does not apply.** The polynomial-ring form in FHJRV
  (Prop. 8(i) / Prop. 13, in-repo HAL text) needs b to be a square, or full
  2-torsion. Double-odd curves have neither. The rescaled construction above
  is the red team's derivation (`TASK-20260923-404bf9`, joint K5). It is not
  in FHJRV's text.
- **Evidence for the law, at toy size only.** The red team built square
  analogues and measured D with Singular, cross-checked by msolve. They are
  toy scale and reviewer scratch.

  | n = m | S_m arm | old norm arm (iii) | rescaled quotient |
  |---|---|---|---|
  | 3 | 64 | 64 | 16 |
  | 4 | 4096 | 4096 | 512 |

  - n = m = 3: primes 4111 and 16777291, two targets each. The dispatching
    session reproduced these values by re-running the red team's script.
    That is a reproduction, not an independent derivation.
  - n = m = 4: one prime, with b a square. Not reproduced.
- **The m = 5 system is smaller than the one that failed.** The rescaled
  quotient has A of sigma-degree at most 8 (at most C(13,5) = 1287 monomials)
  and B of sigma-degree at most 7 (at most 792). The system that exhausted
  the cap had 20349 monomials. Whether it completes, under what cap, and at
  which primes, is unknown.

## Why it matters

The design note's 2^142 figure is the D^2 floor of the S_5 system
(`CORR-20260923-27ce4f`). Re-anchored under that note's own model, a genuine
torsion quotient with D = 2^16 would sit at about 2^134.4 (D^2 edge) to
2^152.7 (nominal 5 D^3). With the inverse success probability charged
(FHJRV: 2^4 x 5! decomposition tests per relation), it would sit at 2^144.3
to 2^162.6.

These are model arithmetic, not measurements. Which side of 142 the measured
figure lands on is the content of goal criterion C1 of `GOAL-GFPN-380702`.
The same quotient question bears on any torsion-quotient PDP lane over odd
extension degrees.

## Resolution criterion

All of the following are needed:

1. The rescaled quotient arm is built and validated against the n = m = 3
   square analogue (D = 16, against 64 for S_3), with an identity control
   that reproduces the rescaled raw system's solutions orbit by orbit.
2. D is measured at n = m = 5 on EcGFp5-shaped curves at three or more
   primes spanning 12 or more bits, under a recorded memory envelope. This
   is the measurement protocol the versioned amendment designed by
   `TASK-20260923-aa277e` is to state.
3. D is reported against the S_5 arm measured on the same targets, with the
   orbit non-freeness gap reported. It is never reported against the
   constant 2^20.
4. A memory exhaustion or timeout at m = 5 is recorded as not_measured.
   It does not resolve the question.

## What must NOT be said in the meantime

- **Not** "the 2-torsion symmetrization does not help at m = 5".
  `EXP-GFPN-05ff43` never tested it.
- **Not** "the quotient gives 2^16 at m = 5". The law is observed only at
  n = m = 3 and 4, at toy scale.
- **Not** "EcGFp5 is below 142 bits (or below 128)". Nor that it is safe.
  The re-anchored figures are the design note's model, not a measurement.
  Any such reading is a closure or break claim that routes to
  review-breakthrough.
