---
id: KN-LIT-1465
type: literature
title: "Scrutinizing the Security of AES-based Hashing and One-way Functions"
authors:
  - "Shiyao Chen"
  - "Jian Guo"
  - "Eik List"
  - "Danping Shi"
  - "Tianyu Zhang(B)"
year: 2025
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2025/792"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2025/792"
tags: [cryptanalysis, hash, mpc, pairing, survey, symmetric, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
AES has cemented its position as the primary symmetric-key primitive for a wide range of cryptographic applications, which motivates the analysis on the concrete security of AES in practical instantiations, for instance, the collision resistance of AES-based hashing, the key commitment security of AES-based authenticated encryption schemes, and the one-wayness of AES-based one-way functions in MPC/ZK protocols. In this work, we further advance the meet-in-the-middle (MITM) attack framework on AES-like constructions.

## Key claims (as reported)
- We introduce single-color initial structure (SCIS), which leverages new structural insights to reduce the complexity of neutral word generation, a critical bottleneck in MITM attacks.
- As a result, we yield a series of improved results on AES over the state-of-the-art, including the first classical one-block collision attack on 7-round AES-MMO/MP, marking the first round advancement in over a decade and matching the best attack round in the quantum setting, as well as the first one-block collision attack on 4-round AES-128-DM, bridging the gap highlighted by Taiyama et al. at Asiacrypt 2024 from a non-differential-based approach.
- Additionally, we provide a comprehensive list of new results on the security margins of AES-192, AES-256, Rijndael-192, and Rijndael-256 in multiple attack settings.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2025-792.pdf`
