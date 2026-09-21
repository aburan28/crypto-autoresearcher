---
id: KN-LIT-979
type: literature
title: "Failing to hash into supersingular isogeny graphs"
authors:
  - "Sabrina Kunzweiler"
  - "Simon-Philipp Merz"
  - "Christophe Petit"
  - "Benjamin Smith"
  - "Katherine E"
year: 2022
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2022/518"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2022/518"
tags: [class-group, cryptanalysis, elliptic-curve, endomorphism, finite-field, hash, isogeny, number-theory, protocol, sidh-csidh, signature, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
An important open problem in supersingular isogeny-based cryptography is to produce, without a trusted authority, concrete examples of “hard supersingular curves” that is, equations for supersingular curves for which computing the endomorphism ring is as difficult as it is for random supersingular curves. A related open problem is to produce a hash function to the vertices of the supersingular `-isogeny graph which does not reveal the endomorphism ring, or a path to a curve of known endomorphism ring.

## Key claims (as reported)
- Such a hash function would open up interesting cryptographic applications.
- In this paper, we document a number of (thus far) failed attempts to solve this problem, in the hope that we may spur further research, and shed light on the challenges and obstacles to this endeavour.
- The mathematical approaches contained in this article include: (i) iterative root-finding for the supersingular polynomial; (ii) gcd’s of specialized modular polynomials; (iii) using division polynomials to create small systems of equations; (iv) taking random walks in the isogeny graph of abelian surfaces; and (v) using quantum random walks. ∗ Jeremy Booher was supported by a grant from the Marsden Fund Council administered by the Royal Society of New Zealand.
- Ross Bowden was supported by EPSRC grant EP/T517872/1.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2022-518.pdf`
