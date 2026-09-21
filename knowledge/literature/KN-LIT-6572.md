---
id: KN-LIT-6572
type: literature
title: "Séta: Supersingular Encryption from Torsion Attacks"
authors:
  - "Luca De Feo"
  - "Cyprien Delpech de Saint Guilhem"
  - "Tako Boris Fouotsa"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [elliptic-curve, endomorphism, hash, isogeny, pqc, quantum, sidh-csidh, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present Séta,11 a new family of public-key encryption schemes with post-quantum security based on isogenies of supersingular elliptic curves. It is constructed from a new family of trapdoor one-way functions, where the inversion algorithm uses Petit’s so called torsion attacks on SIDH to compute an isogeny between supersingular elliptic curves given an endomorphism of the starting curve and images of torsion points.

## Key claims (as reported)
- We prove the OW-CPA security of Séta and present an IND-CCA variant using the post-quantum OAEP transformation.
- Several variants for key generation are explored together with their impact on the selection of parameters, such as the base prime of the scheme.
- We furthermore formalise an “uber” isogeny assumption framework which aims to generalize computational isogeny problems encountered in schemes including SIDH, CSDIH, OSIDH and ours.
- Finally, we carefully select parameters to achieve a balance between security and run-times and present experimental results from our implementation.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/130900345 (1).pdf`
- `downloads/130900345.pdf`
