---
id: KN-LIT-3244
type: literature
title: "Cryptanalysis of LEDAcrypt"
authors:
  - "Daniel Apon"
  - "Ray Perlner"
  - "Angela Robinson"
  - "Paolo Santini"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, dlp, factoring, pairing, pqc, quantum, signature, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We report on the concrete cryptanalysis of LEDAcrypt, a 2nd Round candidate in NIST’s Post-Quantum Cryptography standardization process and one of 17 encryption schemes that remain as candidates for near-term standardization. LEDAcrypt consists of a publickey encryption scheme built from the McEliece paradigm and a keyencapsulation mechanism (KEM) built from the Niederreiter paradigm, both using a quasi-cyclic low-density parity-check (QC-LDPC) code.

## Key claims (as reported)
- In this work, we identify a large class of extremely weak keys and provide an algorithm to recover them.
- For example, we demonstrate how to recover 1 in 247.72 of LEDAcrypt’s keys using only 218.72 guesses at the 256-bit security level.
- This is a major, practical break of LEDAcrypt.
- Further, we demonstrate a continuum of progressively less weak keys (from extremely weak keys up to all keys) that can be recovered in substantially less work than previously known.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12171368 (1).pdf`
- `downloads/12171368.pdf`
