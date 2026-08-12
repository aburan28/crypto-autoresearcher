---
id: KN-LIT-677
type: literature
title: "HASH FUNCTIONS FROM SUPERSPECIAL GENUS-2 CURVES USING RICHELOT ISOGENIES"
authors:
  - "WOUTER CASTRYCK"
  - "THOMAS DECRU"
  - "BENJAMIN SMITH"
year: 2019
venue: "arXiv preprint"
identifiers:
  eprint: null
  doi: null
  arxiv: "1903.06451"
  url: "https://arxiv.org/abs/1903.06451"
tags: [abelian-variety, elliptic-curve, finite-field, hash, isogeny, jacobian, pqc, protocol, sidh-csidh, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Last year Takashima proposed a version of Charles, Goren and Lauter’s hash function using Richelot isogenies, starting from a genus-2 curve that allows for all subsequent arithmetic to be performed over a quadratic finite field Fp2 . In a very recent paper Flynn and Ti point out that Takashima’s hash function is insecure due to the existence of small isogeny cycles.

## Key claims (as reported)
- We revisit the construction and show that it can be repaired by imposing a simple restriction, which moreover clarifies the security analysis.
- The runtime of the resulting hash function is dominated by the extraction of 3 square roots for every block of 3 bits of the message, as compared to one square root per bit in the elliptic curve case; however in our setting the extractions can be parallelized and are done in a finite field whose bit size is reduced by a factor 3.
- Along the way we argue that the full supersingular isogeny graph is the wrong context in which to study higher-dimensional analogues of Charles, Goren and Lauter’s hash function, and advocate the use of the superspecial subgraph, which is the natural framework in which to view Takashima’s Fp2 -friendly starting curve.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/1903.06451v1.pdf`
