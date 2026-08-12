---
id: KN-LIT-125
type: literature
title: Improved Classical Cryptanalysis of SIKE in Practice
authors: [Costello Craig, Longa Patrick, Naehrig Michael, Renes Joost, Virdia Fernando]
year: 2020
venue: 'Public-Key Cryptography - PKC 2020, Springer'
identifiers:
  eprint: iacr:2019/298
  doi: 10.1007/978-3-030-45388-6_18
  url: https://eprint.iacr.org/2019/298
tags: [supersingular, isogeny, sike, sidh, cssi, golden-collision, van-oorschot-wiener, collision-search, memory, full-cost, cost-model, implementation, calibration, classical-baseline, post-quantum, adjacent]
confidence: reported
citation_verified: web
added: 2026-07-25
superseded_by: null
---

## Contribution
An optimised implementation of the van Oorschot-Wiener (vOW) parallel collision
finding algorithm, both generically and specialised to the supersingular isogeny
setting, yielding an improved classical cryptanalysis of the Computational
Supersingular Isogeny (CSSI) problem underlying SIKE. The paper's framing is
explicitly practical: challenges arise in implementation that the theory does
not capture, so the algorithm's real performance is a necessary input to security
estimation.

## Key claims (as reported)
- The main contribution is an **optimised implementation** of vOW parallel
  collision finding, not a new algorithm.
- Implementation behaviour is not captured by the theoretical cost expression,
  and "the performance of the algorithm in practice [is] a crucial element of
  estimating security."
- Improvements are reported at two levels: generic vOW collision finding in
  arbitrary functions, and the SIKE/CSSI-specific instantiation.

## Relevance to this program
The measured counterpart to `KN-LIT-124`. Together they give `GOAL-SSI-001`
BATCH-002 both the definition of the low-memory collision-search analogue and
evidence about how it behaves when actually run — which is exactly the
theory-versus-implementation distinction the program insists on elsewhere.

The stated thesis — that the gap between a cost expression and a measured
implementation is itself a security-relevant quantity — is the same one
`KN-LIT-123` reaches on the lattice side and that the program applies to its own
solver measurements. This entry is therefore a calibration anchor for isogeny
claims in the sense of `KN-TECH-036` and `KN-TECH-049`: a place where somebody
actually ran the attack rather than costing it.

## Not verified here
Verification was by web search surfacing primary-index listings (IACR ePrint
2019/298, Springer DOI 10.1007/978-3-030-45388-6_18, PKC 2020); direct fetches of
the ePrint page, the publisher page, and an author-hosted PDF all returned HTTP
403 under this session's egress policy. Title, author list, year and venue are
corroborated across independent results, and the two quoted phrases come from an
abstract returned by search rather than from a fetched page.

The LNCS volume number for PKC 2020 was **not** confirmed and is deliberately
omitted. Also NOT verified here: the specific optimisations, the speedups
claimed, the hardware used, any concrete security estimate for a named SIKE
parameter set, and the relationship of those estimates to the figures in
`KN-LIT-124`. An earlier ePrint version carries the different title "Improved
Classical Cryptanalysis of the Computational Supersingular Isogeny Problem";
this entry records the published title.
