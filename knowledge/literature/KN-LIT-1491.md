---
id: KN-LIT-1491
type: literature
title: "The Rényi Smoothing Parameter and Its Applications in Lattice-Based Cryptography"
authors:
  - "Cong Ling"
  - "Laura Luzzi"
  - "Hao Yan"
year: 2025
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2025/986"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2025/986"
tags: [lattice, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The smoothing parameter is a cornerstone concept in latticebased cryptography. Traditionally defined using the L∞ distance, this standard formulation can be overly stringent compared to the L1 (or statistical) distance more commonly employed in cryptographic contexts.

## Key claims (as reported)
- Recent work has proposed relaxed definitions based on Kullback-Leibler (KL) divergence and L1 distance, thereby loosening the constraints required for the distance to vanish.
- However, the additive nature of the L1 distance can be limiting for cryptographic applications where probability preservation is essential.
- In this paper, we introduce the Rényi smoothing parameter of a lattice, based on Rényi divergence, to address this limitation.
- The advantages of Rényi divergence in cryptographic settings are well known thanks to its multiplicative nature.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2025-986.pdf`
