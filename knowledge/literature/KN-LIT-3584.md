---
id: KN-LIT-3584
type: literature
title: "Efficient Lattice-Based Blind Signatures via Gaussian One-Time Signatures"
authors:
  - "Vadim Lyubashevsky"
  - "Ngoc Khanh Nguyen"
  - "Maxime Plancon"
year: null
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, lattice, pairing, quantum, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Lattice-based blind signature schemes have been receiving some recent attention lately. Earlier efficient 3-round schemes (Asiacrypt 2010, Financial Cryptography 2020) were recently shown to have mistakes in their proofs, and fixing them turned out to be extremely inefficient and limited the number of signatures that a signer could send to less than a dozen (Crypto 2020).

## Key claims (as reported)
- In this work we propose a round-optimal, 2-round lattice-based blind signature scheme which produces signatures of length 150KB.
- The running time of the signing protocol is linear in the maximum number signatures that can be given out, and this limits the number of signatures that can be signed per public key.
- Nevertheless, the scheme is still quite efficient when the number of signatures is limited to a few dozen thousand, and appears to currently be the most efficient lattice-based candidate.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/131770133 (1).pdf`
- `downloads/131770133.pdf`
