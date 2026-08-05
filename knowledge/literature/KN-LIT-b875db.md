---
id: KN-LIT-b875db
type: literature
title: "Solving the Shortest Vector Problem in 2^{0.7314n+o(n)} Time via Discrete Gaussian Sampling on Superlattices"
authors:
  - "Yiming Gao"
  - "Yansong Feng"
  - "Honggang Hu"
year: 2026
venue: "Preprint (unrefereed; no venue, ePrint number, or DOI stated in the supplied text)"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [svp, lattices, discrete-gaussian-sampling, superlattice, sparsification, smoothing-parameter, kabatiansky-levenshtein, sphere-packing, adrs, exponent-improvement, provable-algorithms, worst-case, pqc, cross-domain, target-result-profile]
confidence: reported
citation_verified: full_text_supplied
added: "2026-08-03"
superseded_by: null
---

> **Provenance caveat.** The full text was supplied directly by the user on
> 2026-08-03 and was read in full for this entry. The authors and affiliations
> are named (USTC School of Cyber Science and Technology; AMSS, Chinese Academy
> of Sciences; Hefei National Laboratory), but the supplied text states **no
> ePrint number, arXiv identifier, DOI, or venue**, so the citation cannot be
> independently resolved and `identifiers` is left empty rather than guessed
> (AGENTS.md rule 5; this entry therefore appears in the `SOURCES.md` gap
> table, which is the correct outcome). The result is **unrefereed**. The
> authors disclose use of a generative model for early drafting assistance and
> state they independently verified all mathematical claims.

## Contribution

A classical randomized algorithm for **exact** Euclidean SVP on arbitrary
full-rank lattices, claimed to run in `2^{E₀n+o(n)}` time and `2^{n/2+o(n)}`
space, with

```
β  = 2^0.401                       (Kabatiansky–Levenshtein)
E₀ = 1/2 + β²/(4e ln 2) = 0.73133754…
```

If correct, this is the first improvement on the `2^{n+o(n)}` worst-case
classical bound of Aggarwal–Dadush–Regev–Stephens-Davidowitz (ADRS, STOC 2015),
and it also undercuts the best known worst-case *quantum* bounds of
Aggarwal–Chen–Kumar–Shen (SICOMP 2025): `2^{0.9497n}` without QRAM,
`2^{0.8345n}` with QRAM.

## Mechanism

Exact SVP needs Gaussian mass on a shortest vector at a scale that can lie
*below* `η_{1/2}(L)`, where no fast sampler is available. The paper does not
try to sample `L` there. Instead it replaces `L` by a random **superlattice**
`Γ ⊃ L` that is smooth at that scale:

1. Set `Λ = L*`, pick a prime `p ≈ 2^{aₙ}·det(L)/sⁿ`, choose a uniformly
   random nonzero functional `φ: Λ/pΛ → 𝔽_p`, and set `M = ker φ`, `Γ = M*`.
   This is **dual-side lattice sparsification**: `M` is a random index-`p`
   sublattice of `L*`, so `Γ` is a random index-`p` superlattice of `L`.
2. Two structural facts do the work. Every vector of `L` — in particular every
   shortest vector — lies in **every** possible `Γ`, so the randomness can
   never destroy the target. And every nonzero dual vector outside `pΛ`
   survives with probability `≈ 1/p`, which suppresses the short-vector
   structure of `L*` that a fixed or structured superlattice would inherit.
3. The only vectors forced into every kernel are those of `pΛ`; these are
   controlled geometrically, via a codimension-one covolume identity
   (`det(L ∩ w^⊥) = det(L)·λ₁(L*)`) plus the KL sphere-packing bound.
4. `Γ` is then smooth at `s`, so `t = √2·s` clears the ADRS above-smoothing
   honest-DGS threshold and `2^{n/2}` samples per call are cheap. The
   algorithm simply scans raw `D_{Γ,t}` samples and keeps the shortest nonzero
   one passing an exact membership test for `L` — no rejection sampling down
   to a full `D_{L,t}` table.

`λ₁(L)` is unknown, so an LLL-based polynomial-size scale grid is searched;
wrong branches cannot produce false positives because every candidate is
explicitly verified to lie in `L \ {0}`.

## Key claims (as reported)

- Exact SVP, arbitrary full-rank lattices, success probability
  `1 − 2^{−Ω(n log n)}`.
- Time `2^{E₀n+O(n/√log n)}`, space `2^{n/2+O(n/log n + log⁵ n)}`, in a
  dimension-only arithmetic model (polynomial factors in input encoding length
  suppressed).
- Appendix A proves a **uniform** quantitative Gaussian-mass bound, introduced
  to close a quantifier gap the authors identify in the printed proof of ADRS
  Lemma 4.2 (the cited point-count estimate fixes the normalized radius,
  whereas the shell radii in the application vary with dimension).
- Remark 1.2: any strict improvement to the KL constant in *both* the packing
  bound and the point-counting bound lowers the exponent correspondingly.

## Verified here (arithmetic consistency only)

The following were re-derived independently while reading. **This is
consistency checking, not a proof check** — it establishes that the paper's
numbers cohere, not that its theorems are correct.

- `E₀ = 1/2 + β²/(4e ln 2) = 0.73134…` for `β = 2^0.401`. Matches.
- The exponent decomposition is honest and non-mysterious: the `1/2` is
  literally `(t/s)ⁿ = 2^{n/2}`, i.e. the `√2` in the ADRS sampling threshold
  raised to the `n`; the `D/4` is the Gaussian weight `exp(−πλ₁²/t²)` of a
  shortest vector at width `t`.
- The choice of scale `s₀` is exactly the point where the KL kissing-number
  bound and the Gaussian weight balance:
  `2^{0.401n}·exp(−β²n/(2e)) = 2^{−0.0617n}`. The shell sum converges, so
  `ρ_{s₀}(L) ≤ 2^{O(log n)}` is plausible — but **the margin is thin** (0.0617
  in the exponent), and it is what Lemma 4.1 rests on.
- The Poisson-summation bookkeeping is dimensionally consistent throughout:
  `ρ_t(Γ) ≈ tⁿp/det(L) = 2^{n/2+aₙ}`; nonforced mass `≈ ρ_s(L)/2^{aₙ}`; forced
  mass superexponentially small given `p·s·λ₁(L*) ≥ 2^{aₙ−O(log n)}`.
- **Limit behaviour, a useful internal check the paper does not state
  explicitly:** as the KL constant improves (`β → 1`), `E₀ → 1/2 + 1/(4e ln 2)
  = 0.63269…`, which is *exactly* the Pouly–Shen average-case exponent for
  Haar–Siegel-random lattices (EUROCRYPT 2026). So Remark 1.2 is internally
  coherent, and `0.63269` is the floor of this method: `β²` is precisely the
  worst-case geometric loss relative to the random-lattice case.

## Not verified here

- **Appendix A is the load-bearing weak point and was not checked.** Lemma 4.1,
  the nonforced-mass bound, the forced-mass bound, and the prime choice all
  depend on its uniformity claim. It is also the part the authors wrote
  themselves to patch a gap in the literature, so it has had the least external
  scrutiny of anything in the paper. A referee should start here.
- The restatement of the ADRS honest-DGS guarantee (their Theorem 5.11) and its
  quantitative specialization at `κ = n²` were not checked against ADRS.
- The quoted ACKS quantum bounds, the Pouly–Shen `0.63269` figure, and the KL
  constants `0.599`/`0.401` were not checked against their sources.
- No claim in this entry has been reproduced computationally by this program.

## Relevance to this program

**Not an ECDLP result.** Relevance is (a) as an exemplar for
`docs/target-result-profile.md` and (b) methodological.

*As a target-profile exemplar.* This is an exponent-moving result on a central
hard problem, in the worst case, and — unlike the profile's canonical
Wesolowski exemplar — stated **unconditionally**, with no numbered heuristics.
The improvement is also honestly small and honestly costed: the authors decline
to claim the numerical improvement available from a recent unrefereed
manuscript, keeping the classical KL bound in the stated result. That
combination (real exponent movement + refusal to bank an unrefereed dependency)
is close to the taste this program is trying to encode.

*As a method.* The core move is object-first in the sense of
`docs/inventor-protocol.md`: when the input object lacks a property the
algorithm needs (`L` is not smooth at the useful scale), do not weaken the
algorithm — construct a **random object of controlled shape that contains the
target**, so the property becomes available while the answer is provably
preserved. The two-line justification (`v ∈ L ⊂ Γ` always; non-target
structure survives with probability `1/p`) is the transferable schema, and the
null-object control is built in: a fixed or structured superlattice would
retain too much of `L*`'s short-vector structure, and the paper says so
explicitly.

*Cost model discipline worth copying.* The exponent is decomposed into two
named, separately attributable terms (`sampler threshold` + `Gaussian weight of
the target`), which makes it immediately visible which half a future
improvement would have to attack.

## Limits of applicability

- **This does not bear on the security of deployed lattice cryptography, and
  must not be cited as if it did.** Practical cryptanalysis uses heuristic
  sieving at `≈2^{0.292n}` (Becker–Ducas–Gama–Laarhoven), already far below
  `2^{0.7314n}`, and concrete parameter estimates for ML-KEM, ML-DSA, and
  Falcon are built on those heuristic costs. This is a result about the
  *provable worst-case* frontier only.
- `2^{n/2+o(n)}` space makes it non-practical independently of the time bound.
- Asymptotic and non-constructive in the small-dimension regime: correctness is
  claimed only for `n ≥ n₀` for an unspecified absolute `n₀`, with fixed-dimension
  exact SVP invoked below it.
- Unrefereed; see the provenance caveat.

## Related entries found while curating

None. Grepping `knowledge/` for `svp`, `shortest vector`, `lattice`,
`Kabatiansky`, and `ADRS` returns lattice material only in code-based and
LIP/HAWK contexts (e.g. `KN-LIT-7965a1` on reduction theory for binary codes,
`KN-LIT-7603` on module-LIP). This is the corpus's first entry on the
provable-SVP-algorithms line specifically.
