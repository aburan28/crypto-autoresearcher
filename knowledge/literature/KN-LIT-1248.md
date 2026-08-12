---
id: KN-LIT-1248
type: literature
title: "Ideal-to-isogeny algorithm using 2-dimensional"
authors:
  - "Hiroshi Onuki"
  - "Kohei Nakagawa"
year: 2024
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2024/778"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2024/778"
tags: [elliptic-curve, endomorphism, extension-field, isogeny, pqc, protocol, quantum, sidh-csidh, signature, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The Deuring correspondence is a correspondence between supersingular elliptic curves and quaternion orders. Under this correspondence, an isogeny between elliptic curves corresponds to a quaternion ideal.

## Key claims (as reported)
- This correspondence plays an important role in isogeny-based cryptography and several algorithms to compute an isogeny corresponding to a quaternion ideal (ideal-to-isogeny algorithms) have been proposed.
- In particular, SQIsign is a signature scheme based on the Deuring correspondence and uses an ideal-to-isogeny algorithm.
- In this paper, we propose a novel ideal-to-isogeny algorithm using isogenies of dimension 2.
- Our algorithm is based on Kani’s reducibility theorem, which gives a connection between isogenies of dimension 1 and 2.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2024-778.pdf`
