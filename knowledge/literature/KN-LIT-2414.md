---
id: KN-LIT-2414
type: literature
title: "Algorithmic Number Theory Symposium XVII, Groningen, July 6-10, 2026 EFFICIENT QUATERNION ALGORITHMS FOR THE DEURING"
authors:
  - "APPLICATION TO THE"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [elliptic-curve, implementation, isogeny, lattice, pairing, pqc, provable-security, sidh-csidh, signature, supersingular, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: KN-LIT-7642
---

> **Superseded 2026-08-01 by [[KN-LIT-7642]].** This record's bibliographic header is
> corrupt: the `title` field concatenates an ANTS XVII conference banner with a
> truncated paper title, the `authors` field holds the text fragment
> `"APPLICATION TO THE"` instead of a person, and `year`, `venue`, and all three
> identifier fields are `null`. The paper is Antonin Leroux, *Efficient quaternion
> algorithms for the Deuring correspondence, and application to the evaluation of
> modular polynomials*, IACR ePrint 2026/185. The body below is left unedited per the
> immutability rule; cite KN-LIT-7642 instead.

## Contribution
This work presents several algorithms to perform operations in the quaternion ideals and orders stemming from the Deuring correspondence. While most of the desired operations can be done with generic linear algebra, we show that they can be performed much more efficiently while maintaining a strict control over the size of the integers involved.

## Key claims (as reported)
- This allows us to obtain a very efficient implementation with fixed sized integers of the effective Deuring correspondence.
- We apply our new algorithms to improve greatly the practical performances of a recent algorithm by Corte-Real Santos, Eriksen, Leroux, Meyer, and Panny to evaluate modular polynomials.
- Our new implementation, including several other improvements, runs 20 times faster than before for the level l = 11681.
- The Deuring correspondence also plays a central role in the most recent developments in isogeny-based cryptography, and in particular in the SQIsign signature scheme submitted to the NIST PQC competition.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/antsxvii-leroux-paper.pdf`
