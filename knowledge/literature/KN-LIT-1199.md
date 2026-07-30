---
id: KN-LIT-1199
type: literature
title: "An efficient collision attack on Castryck-Decru-Smith’s hash function"
authors:
  - "Ryo Ohashi"
  - "Hiroshi Onuki"
year: 2024
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2024/1776"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2024/1776"
tags: [cryptanalysis, elliptic-curve, endomorphism, hash, isogeny, pqc, quantum, sidh-csidh, signature, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In 2020, Castryck-Decru-Smith constructed a hash function using the (2, 2)-isogeny graph of superspecial principally polarized abelian surfaces. In their construction, the initial surface was chosen from vertices quite “close” to the square of a supersingular elliptic curve with a known endomorphism ring.

## Key claims (as reported)
- In this paper, we propose an algorithm for recovering a collision on their hash function.
- Under some heuristic assumptions, the time complexity and space complexity of our algorithm are estimated to e 3/10 ) which is smaller than the complexity O(p e 3/2 ) the authors had be O(p claimed necessary to recover such a collision, where p is the characteristic of the base field.
- In particular case where p has a special form, then both the time and space complexities of our algorithm are polynomial in log p.
- We implemented our algorithm in MAGMA, and succeeded in recovering a collision in 17 hours (using 64 parallel computations) under a parameter setting the authors had claimed to be 384-bit secure.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2024-1776.pdf`
