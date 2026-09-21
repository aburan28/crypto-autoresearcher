---
id: KN-LIT-1676
type: literature
title: "Guess-and-Determine Rebound Revisited: Full Quantum Collision Attack on AES-256 in DM Hash Mode"
authors:
  - "Liyuan Tang"
  - "Lingyue Qin"
  - "Shiqi Hou(B)"
  - "Xiaoyang Dong"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/1050"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/1050"
tags: [cryptanalysis, hash, mpc, pairing, signature, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
At CRYPTO 2025, Qin et al. introduced the guess-anddetermine (GD) rebound attack, which integrates the guess-and-determine approach by Bouillaguet, Derbez, and Fouque and the rebound attack by Mendel et al. Taking the GD rebound as a building block, this paper introduces several classical and quantum models to convert the semifree-start (SFS) collision attack or free-start (FS) collision attack into collision attacks on DM hashing mode with AES.

## Key claims (as reported)
- As an application, the first full quantum collision attack on AES-256DM is proposed.
- Despite numerous round-reduced quantum or classical attacks proposed against the three popular hash modes MMO/MP/DM with AES over the past two decades, this is the first full attack that targets one of the three fundamental security requirements: collision, (2nd) preimage resistance.
- Our full attack on AES-256-DM improves the best previous attack by Taiyama et al. at ASIACRYPT 2024 by 5 rounds.
- Besides, some improved results on AES-128-DM and AES-192-DM are also given, which have been verified partially or fully by experiments.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-1050.pdf`
