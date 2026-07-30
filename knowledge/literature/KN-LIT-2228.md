---
id: KN-LIT-2228
type: literature
title: "A simple and compact algorithm for SIDH with arbitrary degree isogenies"
authors:
  - "Craig Costello"
  - "Huseyin Hisil"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [curve-arithmetic, elliptic-curve, finite-field, isogeny, lattice, pairing, pqc, protocol, quantum, sidh-csidh, signature, supersingular, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We derive a new formula for computing arbitrary odd-degree isogenies between elliptic curves in Montgomery form. The formula lends itself to a simple and compact algorithm that can efficiently compute any low odd-degree isogenies inside the supersingular isogeny Diffie-Hellman (SIDH) key exchange protocol.

## Key claims (as reported)
- Our implementation of this algorithm shows that, beyond the commonly used 3-isogenies, there is a moderate degradation in relative performance of (2d + 1)-isogenies as d grows, but that larger values of d can now be used in practical SIDH implementations.
- We further show that the proposed algorithm can be used to both compute isogenies of curves and evaluate isogenies at points, unifying the two main types of functions needed for isogeny-based public-key cryptography.
- Together, these results open the door for practical SIDH on a much wider class of curves, and allow for simplified SIDH implementations that only need to call one general-purpose function inside the fundamental computation of the large degree secret isogenies.
- As an additional contribution, we also give new explicit formulas for 3- and 4-isogenies, and show that these give immediate speedups when substituted into pre-existing SIDH libraries.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/106240339 (1).pdf`
- `downloads/106240339.pdf`
