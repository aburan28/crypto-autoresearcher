---
id: KN-LIT-903
type: literature
title: "On the Isogeny Problem with Torsion Point Information"
authors:
  - "Tako Boris Fouotsa"
  - "Péter Kutas"
  - "Simon-Philipp Merz"
  - "Yan Bo Ti"
year: 2021
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2021/153"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2021/153"
tags: [complexity-theory, elliptic-curve, endomorphism, finite-field, hash, isogeny, lattice, pqc, protocol, provable-security, sidh-csidh, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
It has recently been rigorously proven (and was previously known under certain heuristics) that the general supersingular isogeny problem reduces to the supersingular endomorphism ring computation problem. However, in order to attack SIDH-type schemes, one requires a particular isogeny which is usually not returned by the general reduction.

## Key claims (as reported)
- At Asiacrypt 2016, Galbraith, Petit, Shani and Ti presented a polynomial-time reduction of the problem of finding the secret isogeny in SIDH to the problem of computing the endomorphism ring of a supersingular elliptic curve.
- Their method exploits the fact that secret isogenies in SIDH are of degree approximately p1/2 .
- The method does not extend to other SIDH-type schemes, where secret isogenies of larger degree are used and this condition is not fulfilled.
- We present a more general reduction algorithm that generalises to all SIDH-type schemes.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/131770104 (1).pdf`
- `downloads/131770104.pdf`
- `downloads/2021-153.pdf`
