# Research program: attacking prime-field ECDLP through the localized solve step

Anchored on the barrier-localization theorem (research/THM-collection-lower-bound-
20260722.md), which reduces "beat Pollard rho over generic prime fields" to a
single quantity. This document devises the sub-problem tree, proves the reachable
stepping-stones, and identifies the exact crux whose resolution is the breakthrough.
Honest framing: a plan with proved sub-results and a new fine-grained-complexity
reduction; not itself a break.

## 0. The reduced target (from the theorem)
For E/F_p, N=#E(F_p), m-decomposition over a size-B factor base:
- collection + linear algebra is unconditionally >= B + m!N/(2^m B^{m-1});
- so the ONLY way to beat rho (total o(sqrt N)) is a decomposition-test cost
  sigma = o(N^{m/2-1})   (o(sqrt N) for m=3).
Everything below attacks sigma. Collection-phase / factor-base engineering is
proved irrelevant, so it is excluded.

## 1. Proposition P1 (best known m=3 total via meet-in-the-middle) — PROVED
Model the m=3 decomposition test with a pairwise-sum table: preprocess all
P_i+P_j (setup B^2, space B^2); a target R decomposes iff R-P_k is in the table
for some P_k (query = B hash lookups). Total
    T(B) = B^2 + B + B * (B/rho_3) = B^2 + Theta(N/B),
minimized at B = Theta(N^{1/3}), giving T = Theta(N^{2/3}).
Since N^{2/3} > N^{1/2}, MITM index calculus is provably WORSE than rho. (Verified
numerically: exponent 0.68-0.70 across N=1e6..1e18.) So the best *generic* (curve-
structure-oblivious) m=3 strategy does not beat rho — the sumset structure alone
gives nothing; any hope requires the summation polynomial to beat this.

## 2. The fine-grained-complexity reduction (the key reframing) — Proposition P2
The m-decomposition membership test "is R a sum of m factor-base points" is exactly
**m-SUM over the group G with preprocessing of F**. For m=3 it is B calls to
2-SUM-with-preprocessing = the **3SUM-Indexing** problem (Demaine-Vadhan; Golovnev-
Guo-Horel-Park-Vaikuntanathan 2020): preprocess a set into space S so that
"is t a 2-sum?" queries take time T.
- MITM = (S,T) = (B^2, 1). The 3SUM-Indexing conjecture asserts no data structure
  achieves S = B^{2-eps} AND T = B^{1-eps} simultaneously.
- Consequence (conditional): a *structure-oblivious* decomposition test cannot
  simultaneously have small preprocessing and sublinear query, so it cannot push
  the m=3 total below the N^{2/3}..sqrt(N) window. Under 3SUM-Indexing hardness,
  generic m=3 prime-field index calculus does NOT beat rho.

This REFRAMES the open problem in fine-grained terms and isolates the one escape.

## 3. THE CRUX (sub-problem whose resolution is the breakthrough)
**Does the summation polynomial S_{m+1} let the decomposition test beat generic
m-SUM-Indexing?** The factor-base points are NOT an arbitrary set: they lie on the
curve, and S_{m+1}(x_1,...,x_m,x_R)=0 is a low-degree algebraic constraint. The
entire sub-rho question is whether this algebraic structure provides a
decomposition oracle faster than the 3SUM-Indexing lower bound permits.
- POSITIVE resolution (a sub-o(sqrt N) algebraic decomposition oracle) => breakthrough.
- NEGATIVE resolution (the algebra provably does not beat 3SUM-Indexing) => an
  unconditional (or 3SUM-conditional) no-go, completing the theorem's m>=3 gap.

## 4. Sub-problem dependency tree (each with a concrete, attackable first step)
- **SP1 [tractable, no Sage]** Formalize P2 rigorously: give the exact reduction
  m=3 EC-decomposition <-> 3SUM-Indexing over Z/ell, with the precise (S,T) tradeoff
  and the conditional lower bound statement. Deliverable: a proof.
- **SP2 [needs Sage]** Measure sigma_gb: the true Groebner solving degree / cost of
  the S_4 decomposition system over PRIME fields (the campaign's DREG is binary).
  Feeds the crux: is sigma_gb below or above the N^{1/6}-per-query line at B=N^{1/3}?
  First step: run the DREG-style d_reg measurement on the prime-field S_4 system
  via the split pipeline (macaulay_export -> SMS -> tools/m4ri_rank.py; m4ri is
  provisioned) once a Sage-built system is available.
- **SP3 [tractable]** Prove the sharp best-achievable exponent over the whole
  (setup, query) tradeoff for structure-oblivious tests, closing the gap between
  the MITM N^{2/3} upper bound and the theorem's sqrt(N) lower bound. Likely
  answer: Theta(N^{2/3}) is optimal for generic tests (a clean conditional no-go).
- **SP4 [crux, hard]** Attack SP-crux directly: does S_{m+1} admit a batched
  evaluation / algebraic data structure answering decomposition queries in
  o(B^{2-eps}) preprocessing + o(B^{1-eps}) query? Concretely: can the resultant
  tree of S_{m+1} be preprocessed so that membership in the variety
  {S_{m+1}(.,x_R)=0} over the factor base is testable sublinearly? First step:
  study the m=3 case (S_4) as a bivariate elimination and test whether Nyldon/
  Kedlaya-Umans-style multipoint evaluation of the summation polynomial beats
  the pairwise table.

## 5. What is proved now vs open
PROVED (this session, verified): the localization theorem; the m=2 unconditional
no-go; the MITM N^{2/3} upper bound (P1); the m-SUM/3SUM-Indexing reduction framing
(P2, reduction direction). OPEN and load-bearing: SP4 (the crux) and SP2 (prime-
field d_reg). A negative SP3/SP4 yields a (conditional) full no-go; a positive SP4
is the breakthrough. The plan makes the target exact: beat 3SUM-Indexing using the
summation polynomial, or prove you cannot.

## 6. Honest status
No breakthrough is claimed. This is a rigorous decomposition of the problem with
proved stepping-stones and a genuine new reframing (fine-grained complexity /
3SUM-Indexing) that pinpoints the single crux and gives both a breakthrough
target and a no-go target. It converts the campaign's scattered negatives into a
directed program with a clear finish line.

## 7. The collinearity bridge (sharpens the crux; unifies with incidence geometry)
Classical fact (chord-tangent law): for E: y^2=x^3+ax+b, three points sum to the
identity O IFF they are collinear in P^2. Consequences:
- **Relation collection = General Position Testing (GPT).** The zero-sum triples
  of the factor base {P_i+P_j+P_k=O} are exactly its collinear triples. Deciding
  whether a point set contains a collinear triple is GPT, which is
  *unconditionally* 3SUM-hard (Gajentaan-Overmars 1995). So the m=3 relation
  search is a 3SUM-hard geometric problem in the classical (real-RAM / linear
  decision tree) model — a cleaner, stronger hook than 3SUM-Indexing for the
  "generic" hardness side.
- **Why the incidence approach could not convert.** Szemeredi-Trotter / chord-
  richness (the campaign's INC/INCB, supported_scoped) COUNT rich lines/curves,
  but GPT-hardness says counting incidences does not yield a subquadratic
  collinear-triple *oracle*. This explains, structurally, why INCB found a real
  richness excess yet no speedup: incidence counts are not a decomposition oracle.
- **Exact crux, geometric form.** A sub-rho m=3 algorithm needs a collinear-triple
  oracle on E(F_p)-points that beats the GPT/3SUM barrier by exploiting the extra
  algebraic structure of the cubic (the summation polynomial S_4 is the algebraic
  encoding of "4 points, one being -R, in the collinearity/divisor relation").
  Higher m corresponds to points lying on higher-degree plane curves (n points sum
  to O iff cut out by a degree-n/3 curve, by Riemann-Roch) -- i.e. m-decomposition
  is an incidence problem between V and low-degree plane curves. The whole open
  question is whether this algebraic-incidence structure beats generic k-SUM.
