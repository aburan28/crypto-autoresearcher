---
id: KN-LIT-3339
type: literature
title: "CSI-FiSh: Efficient Isogeny based Signatures through Class Group Computations"
authors:
  - "Ward Beullens"
  - "Thorsten Kleinjung"
  - "Frederik Vercauteren"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [class-group, elliptic-curve, endomorphism, hash, isogeny, lattice, number-theory, pqc, protocol, sidh-csidh, signature, supersingular, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper we report on a new record class group computation of an imaginary quadratic field having 154-digit discriminant, surpassing the previous record of 130 digits. This class group is central to the CSIDH-512 isogeny based cryptosystem, and knowing the class group structure and relation lattice implies efficient uniform sampling and a canonical representation of its elements.

## Key claims (as reported)
- Both operations were impossible before and allow us to instantiate an isogeny based signature scheme first sketched by Stolbunov.
- We further optimize the scheme using multiple public keys and Merkle trees, following an idea by De Feo and Galbraith.
- We also show that including quadratic twists allows to cut the public key size in half for free.
- Optimizing for signature size, our implementation takes 390ms to sign/verify and results in signatures of 263 bytes, at the expense of a large public key.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/119210274 (1).pdf`
- `downloads/119210274.pdf`
