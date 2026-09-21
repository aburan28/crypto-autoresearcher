---
id: KN-LIT-7569
type: literature
title: 'Beyond Binary: crosscorrelation of Cubic, Quartic and Quintic Character Sequences'
authors: [Dey Mriganka, Dey Sampa, Pal Sampurna, Samajder Subhabrata, Barua Rana]
year: 2026
venue: 'Cryptology ePrint Archive, Paper 2026/829'
identifiers:
  eprint: iacr:2026/829
  doi: null
  arxiv: null
  url: https://eprint.iacr.org/2026/829
tags: [character-sums, multiplicative-character, finite-field, pseudorandom-sequence, crosscorrelation, equidistribution, legendre-sequence, weil-bound, additive-combinatorics, adjacent]
confidence: reported
citation_verified: web
added: 2026-07-26
superseded_by: null
---

## Contribution
Initiates a systematic study of the **arithmetic crosscorrelation** of *non-binary*
pseudorandom sequences built from higher-order multiplicative characters over finite
fields. For two sequences of coprime periods `P` and `Q` defined via `r`-th order
characters of degree-`d` polynomials, the paper shows the joint local patterns are
asymptotically uniformly distributed and derives an explicit crosscorrelation bound.

## Key claims (as reported)
- The joint local patterns of two such sequences are **asymptotically uniformly
  distributed**.
- Explicit bound, for all shifts `tau`:
  `N(C^A_{S,T}(tau)) = O( ( phi(r) * d * P^{1/2} * Q * (log P)^2 )^{phi(r)} )`,
  where `phi` is Euler's totient and `N(.)` the norm function.
- Claimed as the **first nontrivial upper bounds** on arithmetic crosscorrelation of
  non-binary pseudorandom sequences.
- Extends results of Chen et al. (IEEE IT'22) and Yan-Ke (ePrint 2026/616), which were
  obtained exclusively for the binary Legendre sequence.

## Relevance to this program
`adjacent`, and the honest assessment is that the relevance is **methodological and
weak** rather than mechanistic.

The corpus keeps `KN-TECH-016` (sum-product and additive-combinatorics bounds over
`F_p`) and `KN-OPEN-010` asks whether character orthogonality forces `O(1)`
localization in a transfer-operator attack on the translation-by-`P` walk. Both live
on the same machinery this paper uses: multiplicative-character sums over finite
fields and the equidistribution / square-root-cancellation bounds that govern them.
The `P^{1/2}` factor in the displayed bound is the usual Weil-type square-root
cancellation, and this paper is a current instance of how far that machinery extends
when pushed from quadratic to `r`-th order characters — the joint distribution becomes
uniform, i.e. the extra structure of higher-order characters buys **no** exploitable
bias.

For this program that reads as **further negative evidence in the same direction as
`KN-OPEN-010`**: higher-order character structure over `F_p` equidistributes rather
than concentrating. It is not a proof about the ECDLP walk and must not be cited as
one — the objects are sequences, not group-walk observables — but a proposal
premising an ECDLP advantage on bias in higher-order character sequences over `F_p`
should expect to meet this bound.

Supplies no relation-harvesting mechanism and forecloses nothing formally.

## Not verified here
Full paper not read; all claims relayed from the official ePrint abstract retrieved
from eprint.iacr.org on 2026-07-26 (hence `confidence: reported`). ePrint history:
received 2026-04-28, last of 3 revisions 2026-07-22 — a **revision surfaced in the
2026-07-19..26 window**, not a first posting. No DOI; peer-review status not
established.

NOT verified here: the proof, the exact definitions of arithmetic crosscorrelation and
the norm function `N(.)` used (these differ between authors and change what the bound
means), whether the bound is nontrivial across the whole stated parameter range, the
priority claim, and the cited prior work (Chen et al. IEEE IT'22; Yan-Ke ePrint
2026/616 — the latter is **not** in this corpus and was not retrieved). The inference
drawn above under "Relevance" is this entry's own reading, not a claim of the paper.
