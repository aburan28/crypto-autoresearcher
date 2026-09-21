---
id: KN-LIT-1220
type: literature
title: "Diving Deep into the Preimage Security of AES-like Hashing"
authors:
  - "Shiyao Chen"
  - "Jian Guo"
  - "Eik List"
  - "Danping Shi"
  - "Tianyu Zhang"
year: 2024
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2024/300"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2024/300"
tags: [cryptanalysis, hash, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Since the seminal works by Sasaki and Aoki, Meet-in-theMiddle (MITM) attacks are recognized as an effective technique for preimage and collision attacks on hash functions. At Eurocrypt 2021, Bao et al. automated MITM attacks on AES-like hashing and improved upon the best manual result.

## Key claims (as reported)
- The attack framework has been furnished by subsequent works, yet far from complete.
- This paper introduces three key contributions dedicated to further generalizing the idea of MITM and refining the automatic model on AES-like hashing.
- (1) We introduce S-box linearization to MITM pseudo-preimage attacks on AES-like hashing.
- The technique works well with superposition states to preserve information after S-boxes at affordable cost.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2024-300.pdf`
