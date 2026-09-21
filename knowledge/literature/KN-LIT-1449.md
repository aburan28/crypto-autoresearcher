---
id: KN-LIT-1449
type: literature
title: "PEGASIS: Practical Effective Class Group Action using 4-Dimensional Isogenies"
authors:
  - "Pierrick Dartois"
  - "Jonathan Komada Eriksen"
  - "Tako Boris Fouotsa"
year: 2025
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2025/401"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2025/401"
tags: [class-group, dlp, elliptic-curve, endomorphism, isogeny, lattice, mov-fr, number-theory, pqc, protocol, provable-security, quantum, sidh-csidh, signature, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we present the first practical algorithm to compute an effective group action of the class group of any imaginary quadratic order O on a set of supersingular elliptic curves primitively oriented by O. Effective means that we can act with any element of the class group directly, and are not restricted to acting by products of ideals of small norm, as for instance in CSIDH.

## Key claims (as reported)
- Such restricted effective group actions often hamper cryptographic constructions, e.g. in signature or MPC protocols.
- Our algorithm is a refinement of the Clapoti approach by Page and Robert, and uses 4-dimensional isogenies.
- As such, it runs in polynomial time, does not require the computation of the structure of the class group, nor expensive lattice reductions, and our techniques allow it to be instantiated with the orientation given by the Frobenius endomorphism.
- This makes the algorithm practical even at security levels as high as CSIDH-4096.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2025-401.pdf`
