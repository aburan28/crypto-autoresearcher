---
id: KN-LIT-1360
type: literature
title: "Computing Isomorphisms between Products of Supersingular Elliptic Curves"
authors:
  - "Pierrick Gaudrya"
  - "Julien Soumiera"
  - "Pierre-Jean Spaenlehauera"
year: 2025
venue: "arXiv preprint"
identifiers:
  eprint: null
  doi: null
  arxiv: "2503.21535"
  url: "https://arxiv.org/abs/2503.21535"
tags: [abelian-variety, elliptic-curve, endomorphism, finite-field, isogeny, pairing, protocol, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The Deligne-Ogus-Shioda theorem guarantees the existence of isomorphisms between products of supersingular elliptic curves over finite fields. In this paper, we present methods for explicitly computing these isomorphisms in polynomial time, given the endomorphism rings of the curves involved.

## Key claims (as reported)
- Our approach leverages the Deuring correspondence, enabling us to reformulate computational isogeny problems into algebraic problems in quaternions.
- Specifically, we reduce the computation of isomorphisms to solving systems of quadratic and linear equations over the integers derived from norm equations.
- We develop l-adic techniques for solving these equations when we have access to a low discriminant subring.
- Combining these results leads to the description of an efficient probabilistic Las Vegas algorithm for computing the desired isomorphisms.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2503.21535v1 (1).pdf`
- `downloads/2503.21535v1.pdf`
