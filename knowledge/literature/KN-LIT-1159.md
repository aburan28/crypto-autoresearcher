---
id: KN-LIT-1159
type: literature
title: "Ready to SQI? Safety first! Towards a constant-time implementation of isogeny-based signature SQIsign"
authors:
  - "David Jacquemin"
  - "Anisha Mukherjee"
  - "Péter Kutas"
  - "Sujoy Sinha Roy"
year: 2023
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2023/807"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2023/807"
tags: [class-group, cryptanalysis, dlp, endomorphism, factoring, implementation, isogeny, lattice, mov-fr, number-theory, pairing, pqc, provable-security, quantum, side-channel, sidh-csidh, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
NIST has already published the first round of submissions for additional post-quantum signature schemes and the only isogeny-based candidate is SQIsign. It boasts the most compact key and signature sizes among all post-quantum signature schemes.

## Key claims (as reported)
- However, its current implementation does not address side-channel resistance.
- This work is the first to identify a potential side-channel vulnerability in SQIsign.
- At certain steps within the signing procedure, it relies on Cornacchia’s algorithm to represent an integer as a sum of squares of two integers.
- This algorithm in turn uses a ‘half-GCD’ (half-greatest common divisor) sub-routine based on Euclid’s division algorithm which has often been exploited for side-channel attacks.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2023-807.pdf`
