---
id: KN-LIT-1238
type: literature
title: "Finding Practical Parameters for Isogeny-based Cryptography"
authors:
  - "Maria Corte-Real Santos"
  - "Jonathan Komada Eriksen"
year: 2024
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2024/1150"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2024/1150"
tags: [dlp, elliptic-curve, factoring, finite-field, isogeny, lattice, pairing, pqc, provable-security, rsa, sidh-csidh, signature, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Isogeny-based schemes often come with special requirements on the field of definition of the involved elliptic curves. For instance, the efficiency of SQIsign, a promising candidate in the NIST signature standardisation process, requires a large power of two and a large smooth integer T to divide p2 − 1 for its prime parameter p.

## Key claims (as reported)
- We present two new methods that combine previous techniques for finding suitable primes: sieve-and-boost and XGCD-and-boost.
- We use these methods to find primes for the NIST submission of SQIsign.
- Furthermore, we show that our methods are flexible and can be adapted to find suitable parameters for other isogeny-based schemes such as AprèsSQI or POKE.
- For all three schemes, the parameters we present offer the best performance among all parameters proposed in the literature.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2024-1150.pdf`
