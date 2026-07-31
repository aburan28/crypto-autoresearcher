---
id: KN-LIT-1686
type: literature
title: "IACR Transactions on Symmetric Cryptology"
authors:
  - "ISSN XXXX-XXXX"
  - "pp. –"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/176"
  doi: "10.46586/tosc.v2025.i3.475-515"
  arxiv: null
  url: "https://eprint.iacr.org/2026/176"
tags: [complexity-theory, cryptanalysis, finite-field, hash, mpc, pairing, pqc, provable-security, quantum, rsa, signature, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper introduces a new cryptographic notion for diffusion matrices, termed the Differential Pattern Transition (DPT). Building on this notion, we develop a systematic framework for describing the differential behavior of diffusion layers over multiple rounds in AES-like block ciphers.

## Key claims (as reported)
- Specifically, the DPT framework enables a finer-grained evaluation of diffusion strength against differential attacks, allowing distinctions even among matrices sharing the same branch number.
- Furthermore, the DPT framework facilitates the classification of shuffle layers and assists in identifying permutation layers that maximize differential resistance.
- As a case study, we apply the DPT framework to the diffusion matrices used in MIDORI, PRINCE, QARMA, and AES, as well as a lightweight MDS matrix proposed in [SS16].
- The results show that DPT provides both theoretical insights and practical guidance for the selection and design of diffusion and shuffle layers in secure and efficient block cipher constructions.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2022-025.pdf`
- `downloads/2022-487.pdf`
- `downloads/2023-1095.pdf`
- `downloads/2024-1962.pdf`
- `downloads/2024-352.pdf`
- `downloads/2025-396.pdf`
- (+1 more duplicate copies)
