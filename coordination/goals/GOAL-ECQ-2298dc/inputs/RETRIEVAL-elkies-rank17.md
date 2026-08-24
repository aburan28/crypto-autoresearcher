# Retrieval finding: the vehicle of every rank record since 2006 is UNPUBLISHED

Author: orchestrating session, from a retrieval task run 2026-08-24.
Status: input to GOAL-ECQ-2298dc. Not an evidence record; no run records back it.

## The finding

**Elkies never published a Weierstrass model for the rank-17 elliptic K3 fibration
over Q(t)** that produced the rank-28 record (2006) and was reused for rank-29
(2024). This is a statement about the literature, verified against five named
sources, NOT a claim that the mathematical lane is closed.

- `arXiv:0709.2908` (Elkies, *Three lectures on elliptic surfaces and curves of
  high rank*) treats the surface in a single paragraph and prints no model. What
  it does print is the genus-2 **Shimura curve** `u^2 = 16t^6 - 19t^4 + 88t^2 - 48`
  for N = 6*79, corroborated across four fetches. That is the moduli
  parametrisation, not the elliptic surface, and it will not specialise.
- NMBRTHRY, May 2006, Elkies, *"Z^28 in E(Q), etc."*, verbatim:
  > "I'll post formulas for E, its 18 independent points, and a 19th point on
  > infinitely many specializations, after I have streamlined the formulas, which
  > as I have them look needlessly complicated."
  He deferred them. Two independent signs he never followed through: his own 2007
  lecture notes still print no model, and Dujella -- the field's record-keeper --
  cites `G(0) >= 18, Elkies (2006)` only to the listserv post plus
  "Personal communication, 2006, 2009".
- Not on Elkies' Harvard pages (`/~elkies/`, `math.html`, `compnt.html` enumerated;
  `rk28_1.html` returns HTTP 404). Not in Elkies-Klagsbrun ANTS-XIV
  (`arXiv:2003.00077`), which is about torsion records and contains no K3 surface.
  LMFDB cannot hold it -- it carries curves over Q, not surfaces over Q(t).

This is why the structural route is blocked here, and it is plausibly why no group
outside Elkies-Klagsbrun-Alpoge-Howell has matched the ladder.

## Two contradictions in this program's own reading, now RESOLVED

1. `(Z/2Z) x Z^18` in the arXiv:0709.2908 abstract is **over Q**, not over Q(t).
   The rank-17 statement is over **Q(t)**. Two different objects; an earlier agent
   here got conflicting readings because an HTML summariser was confabulating.
   Rank 18 over Q(T) comes from the rank-17 surface **"again via quadratic base
   change"** -- verbatim, with no quadratic and no model given.
2. The sentence *"But I did not compute explicit equations for this K3 surface..."*
   is real but its antecedent is the **N = 311 / Galbraith rank-15 surface**, NOT
   the rank-17 surface. It must not be cited as saying the rank-17 model was never
   computed; it says something else.

## VERIFIED HERE: the rank-28 curve

Retrieved with three-source digit agreement (Dujella rk28.html, the NMBRTHRY
posting, the lecture-notes extraction) and then checked in this session:

    y^2 + xy + y = x^3 - x^2
      - 20067762415575526585033208209338542750930230312178956502 x
      + 34481611795030556467032985690390720374855944359319180361266008296291939448732243429

The listed point
`P1 = (-2124150091254381073292137463, 259854492051899599030515511070780628911531)`
**satisfies the equation exactly** in rational arithmetic; the discriminant is
nonzero; `log|disc| = 381.2024` and `log max(|c4|^3, c6^2) = 393.6297`.
That verifies transcription and membership only -- NO rank is certified here.

## A LIVE HAZARD, carried forward

The retrieval tool **silently drops exponents**. Two reads of the same Nagao paper
gave `(9T + 211950)X^4` versus `(9T^6 + 211950)X^4`, and `396150T` versus
`396150T^2`. **Every coefficient string obtained this way is a pointer to verify,
never something to paste into PARI.** The rank-28 curve above survived only because
three sources agreed digit-for-digit AND a listed point checked out. Apply that
same bar to anything else retrieved.

## Correction to the statistic this program has been using

The published Elkies-Klagsbrun scoring function (`arXiv:2003.00077`) is
`S(t,B) = sum_{p<B, E_t good} log(N_p(E_t)/p)`, with `exp(-S)` a partial Euler
product for `L_{E_t}(s)` at `s = 1`. That is NOT the `sum a_p log p / p` used in
EXP-ECQ-f5af06, and it runs the opposite way. Anything built on the published
method should use the published statistic.

## Usable substitutes, ranked

1. **Nagao rank >= 13 over Q(T)** (Proc. Japan Acad. 70 (1994) 152) -- quartic model
   plus **12 explicit Q(T)-rational generators**, which is what defines the
   specialised generic subgroup. Coefficients extracted inconsistently; obtain a
   real PDF first.
2. **Kloosterman geometric rank 15** (`arXiv:math/0502439` Thm 1.2):
   `y^2 = x^3 + 2(t^8 + 14t^4 + 1)x + 4t^2(t^8 + 6t^4 + 1)`. Rank is **geometric**,
   over Qbar(t); rank over Q(t) is smaller and unstated. No explicit generators.
   Exercises the machinery; cannot reach 32.
3. **Elkies-Klagsbrun torsion fibrations** (`arXiv:2003.00077`, open access) --
   generic rank only 9, but the object and the method are both published and
   mutually consistent. Highest fidelity to the real pipeline.

## The action most likely to unblock the goal is not a retrieval

Email Elkies. The formulas existed in 2006, he offered to post them, and Dujella's
"Personal communication" citations show he shares them on request. That is a
human action this program cannot take on its own.

## Untried route nobody here has scoped

Recompute the K3 from the public datum: the non-CM orbit at `|t| = 14/13` on
`u^2 = 16t^6 - 19t^4 + 88t^2 - 48`, via Elkies-Kumar 2-neighbour methods. **The
input is public even though the output model is not.** Costed as a substantial
project, not a session task.
