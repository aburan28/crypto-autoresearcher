---
id: KN-LIT-1257
type: literature
title: "KLaPoTi: An asymptotically efficient isogeny group action from 2-dimensional isogenies"
authors:
  - "Lorenz Panny"
  - "Christophe Petit"
year: 2024
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2024/1844"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2024/1844"
tags: [abelian-variety, class-group, elliptic-curve, isogeny, lattice, pairing, pqc, protocol, provable-security, sidh-csidh, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We construct and implement an efficient post-quantum commutative cryptographic group action based on combining the SCALLOP framework for group actions from isogenies of oriented elliptic curves on one hand with the recent Clapoti method for polynomial-time evaluation of the CM group action on elliptic curves on the other. We take advantage of the very attractive performance of (2e , 2e )isogenies between products of elliptic curves in the theta coordinate system.

## Key claims (as reported)
- To successfully apply Clapoti in dimension 2, it is required to resolve a particular quadratic diophantine norm equation, for which we employ a slight variant of the KLPT algorithm.
- Our work marks the first practical instantiation of the CM group action for which both the setup and the online phase can be computed in (heuristic) polynomial time.
- We also point out that the order of the acting group — equivalently, the size of the set being acted on — is known, and can be chosen (within constraints) during parameter generation, in our construction.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2024-1844.pdf`
