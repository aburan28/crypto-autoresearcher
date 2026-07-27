---
id: KN-LIT-737
type: literature
title: "COMPUTING ENDOMORPHISM RINGS OF SUPERSINGULAR"
authors:
  - "ELLIPTIC CURVES"
  - "CONNECTIONS TO PATHFINDING IN"
year: 2020
venue: "arXiv preprint"
identifiers:
  eprint: null
  doi: null
  arxiv: "2004.11495"
  url: "https://arxiv.org/abs/2004.11495"
tags: [complexity-theory, elliptic-curve, endomorphism, finite-field, hash, isogeny, provable-security, sidh-csidh, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Computing endomorphism rings of supersingular elliptic curves is an important problem in computational number theory, and it is also closely connected to the security of some of the recently proposed isogeny-based cryptosystems. In this paper we give a new algorithm for computing the endomorphism ring of a supersingular elliptic curve E defined over Fp2 that runs, under certain heuristics, in time O((log p)2 p1/2 ).

## Key claims (as reported)
- The algorithm works by first finding two cycles of a certain form in the supersingular l-isogeny graph G(p, l), generating an order Λ ⊆ End(E).
- Then all maximal orders containing Λ are computed, extending work of Voight [28].
- The final step is to determine which of these maximal orders is the endomorphism ring.
- As part of the cycle finding algorithm, we give a lower bound on the set of all j-invariants j that are adjacent to j p in G(p, l), answering a question in [1].

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2004.11495v2 (1).pdf`
- `downloads/2004.11495v2.pdf`
