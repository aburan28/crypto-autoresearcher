---
id: KN-LIT-520
type: literature
title: "PREDICTING THE ELLIPTIC CURVE CONGRUENTIAL GENERATOR LÁSZLÓ MÉRAI"
authors: []
year: 2016
venue: "arXiv preprint"
identifiers:
  eprint: null
  doi: "10.1007/s00200-016-0303-x"
  arxiv: "1609.03305"
  url: "https://arxiv.org/abs/1609.03305"
tags: [elliptic-curve, finite-field, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Let p be a prime and let E be an elliptic curve defined over the finite field Fp of p elements. For a point G ∈ E(Fp ) the elliptic curve congruential generator (with respect to the first coordinate) is a sequence (xn ) defined by the relation xn = x(Wn ) = x(Wn−1 ⊕ G) = x(nG ⊕ W0 ), n = 1, 2, . . . , where ⊕ denotes the group operation in E and W0 is an initial point.

## Key claims (as reported)
- In this paper, we show that if some consecutive elements of the sequence (xn ) are given as integers, then one can compute in polynomial time an elliptic curve congruential generator (where the curve possibly defined over the rationals or over a residue ring) such that the generated sequence is identical to (xn ) in the revealed segment.
- It turns out that in practice, all the secret parameters, and thus the whole sequence (xn ), can be computed from eight consecutive elements, even if the prime and the elliptic curve are private.

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/1609.03305v1.pdf`
