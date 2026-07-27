---
id: KN-LIT-6104
type: literature
title: "Quantum Security of NMAC and Related Constructions — PRF domain extension against quantum attacks"
authors:
  - "Fang Song"
  - "Aaram Yun"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, dlp, elliptic-curve, factoring, pairing, pqc, provable-security, quantum, rsa, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We prove the security of NMAC, HMAC, AMAC, and the cascade construction with fixed input-length as quantum-secure pseudorandom functions (PRFs). Namely, they are indistinguishable from a random oracle against any polynomial-time quantum adversary that can make quantum superposition queries.

## Key claims (as reported)
- In contrast, many blockcipherbased PRFs including CBC-MAC were recently broken by quantum superposition attacks.
- Classical proof strategies for these constructions do not generalize to the quantum setting, and we observe that they sometimes even fail completely (e.g., the universal-hash then PRF paradigm for proving security of NMAC).
- Instead, we propose a direct hybrid argument as a new proof strategy (both classically and quantumly).
- We first show that a quantumsecure PRF is secure against key-recovery attacks, and remains secure under random leakage of the key.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10401307 (1).pdf`
- `downloads/10401307.pdf`
