---
id: KN-LIT-813
type: literature
title: "Radical Isogenies"
authors:
  - "Wouter Castryck"
  - "Thomas Decru"
  - "Frederik Vercauteren"
year: 2020
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2020/1108"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2020/1108"
tags: [class-group, curve-arithmetic, elliptic-curve, endomorphism, hash, isogeny, lattice, number-theory, pairing, pqc, prime-field, sidh-csidh, supersingular, survey, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper introduces a new approach to computing isogenies called “radical isogenies” and a corresponding method to compute chains of N -isogenies that is very efficient for small N . The method is fully deterministic and completely avoids generating N -torsion points.

## Key claims (as reported)
- It is based on explicit formulae for the coordinates of an N -torsion point P 0 on the codomain of a cyclic N -isogeny φ : E → E 0 , such that composing φ with E 0 → E 0 /hP 0 i yields a cyclic N 2 -isogeny.
- These formulae are simple algebraic expressions in the coefficients of E, the coordinates of a √ generator P of ker φ, and an N th root N ρ , where the radicand ρ itself is given by an easily computable algebraic expression in the coefficients of E and the coordinates of P .
- The formulae can be iterated and are particularly useful when computing chains of N -isogenies over a finite field Fq with gcd(q − 1, N ) = 1, where taking an N th root is a simple exponentiation.
- Compared to the state-of-the-art, our method results in an order of magnitude speed-up for N ≤ 13; for larger N , the advantage disappears due to the increasing complexity of the formulae.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12491308 (1).pdf`
- `downloads/12491308.pdf`
- `downloads/2020-1108.pdf`
