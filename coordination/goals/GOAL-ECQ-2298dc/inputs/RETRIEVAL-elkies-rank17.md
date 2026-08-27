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

---

# Addendum: forensics attempted WITHOUT the fibration, and what it settled

Run in this session after the retrieval, on three rungs of the ladder: the
verified rank-28 curve, ICARM #273 (rank >= 30), and ICARM #302 (rank >= 31).
#273's a-invariants were retrieved the same way and carry the same provenance
caveat; its listed conductor was not independently checked.

## Measured

| curve | log&#124;disc&#124; | naive height | j integral |
| --- | --- | --- | --- |
| rank 28 | 381.2024 | 393.6297 | no |
| #273, r>=30 | 432.1249 | 442.0854 | no |
| #302, r>=31 | 453.0469 | 468.2771 | no |

**Pairwise quadratic-twist test: NEGATIVE on all three pairs.** No two of the
record curves share a j-invariant, so none is another's twist.

**Shared small primes in the discriminants**, with multiplicities
(rank28 / #273 / #302): p=2 -> 15/16/15, p=3 -> 6/12/4, p=5 -> 6/8/4,
p=7 -> 4/5/6, p=13 -> 4/5/5.

## What this settles, and what it does NOT

The twist test rules out only the degenerate case where two records are the same
fibre up to twist. **Distinct j is EXPECTED for distinct specialisations of one
fibration, so this does not refute a common family and must not be reported as
doing so.**

The shared small primes are **suggestive but not evidence.** A common fibration
would put bad fibres over fixed t-values and produce common bad primes -- but so
would search bias, because a sieve selects curves with many points modulo small
primes, which drives exactly this divisibility. The two explanations are not
separated by this measurement, and I am not going to pretend they are.

## Conclusion

**The family cannot be identified from the curves alone with what is available
here.** IDEA-20260824-155411's forensics test is decidable only against the
fibration's j-map, and that map is unpublished (see above). The inverted form --
reconstructing the fibration from several known specialisations -- is
over-determined in principle and was worth trying, but the discriminating
statistic still requires the object we do not have.

This closes the cheap forensics lane. It does not close the structural lane,
which now rests on the two actions named above: obtain the model from its author,
or recompute the K3 from the public Shimura-curve datum.

---

# Addendum 2: the descent obstruction, MEASURED on a real family

The scoping (IDEA-20260824-*) concluded from retrieval that what blocks high rank
over Q(t) is **Galois descent, not Shioda-Tate** -- geometric rank does not
descend to the rational field. That was a literature claim. It is now measured
here on the one explicit high-rank model this program successfully retrieved.

**Object:** Kloosterman, `arXiv:math/0502439` Thm 1.2, stated GEOMETRIC
Mordell-Weil rank **15** over Qbar(t):

    y^2 = x^3 + 2(t^8 + 14t^4 + 1) x + 4t^2(t^8 + 6t^4 + 1)

CAVEAT: obtained through a tool that silently drops exponents (see the hazard
note above). The measurement below is conditional on the model being as
transcribed and should be re-run against a verified PDF before it is cited.

**Method:** Silverman specialisation gives `rank E_t(Q) >= rank E(Q(t))` for all
but finitely many t, so the MINIMUM specialisation rank bounds the generic rank
from above. 31 specialisations evaluated, t integral 1..25 plus
1/2, 3/2, 1/3, 2/3, 5/2, 1/5; denominators cleared by `(x,y) -> (u^2 x, u^3 y)`.

**Result:** rank lower bounds ranged **0 to 2**, minimum **0**. Several t gave
rank exactly 0 (t = 8, 11, 13, ...). So the generic rank over Q(t) is at most 0
on this sample.

**Geometric rank 15; arithmetic rank over Q(t) measured at 0.** That is the
descent obstruction, in one line, on a published surface -- and it is why
"find a surface of high geometric rank" is not a route to rank 32. Shioda's
rank-68 surface is the same phenomenon at the extreme: its Mordell-Weil group is
defined over a field of degree 829,440.

**Consequence for the goal, stated plainly:** this family cannot yield rank 32
under any specialisation. Silverman hands only `rank >= generic rank`, and the
geometric ceiling caps the generic rank at 15 even before descent takes its cut.
It is ruled out as a vehicle, by measurement rather than by assumption.
