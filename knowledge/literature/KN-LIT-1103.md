---
id: KN-LIT-1103
type: literature
title: "Effective Pairings in Isogeny-based Cryptography"
authors:
  - "Krijn Reijnders"
year: 2023
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2023/858"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2023/858"
tags: [curve-arithmetic, elliptic-curve, finite-field, implementation, isogeny, mov-fr, pairing, pqc, protocol, side-channel, sidh-csidh, supersingular, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Pairings are useful tools in isogeny-based cryptography and have been used in SIDH/SIKE and other protocols. As a general technique, pairings can be used to move problems about points on curves to elements in finite fields.

## Key claims (as reported)
- However, until now, their applicability was limited to curves over fields with primes of a specific shape and pairings seemed too costly for the type of primes that are nowadays often used in isogeny-based cryptography.
- We remove this roadblock by optimizing pairings for highly-composite degrees such as those encountered in CSIDH and SQISign.
- This makes the general technique viable again: We apply our low-cost pairing to problems of general interest, such as supersingularity verification and finding full-torsion points, and show that we can outperform current methods, in some cases up to four times faster than the state-of-the-art.
- Furthermore, we analyze how pairings can be used to improve deterministic and dummy-free CSIDH.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2023-858.pdf`
