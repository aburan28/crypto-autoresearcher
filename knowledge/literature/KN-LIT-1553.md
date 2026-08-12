---
id: KN-LIT-1553
type: literature
title: "Assessing Geometric Security of AES Neural Realizations: Linear-Time Key Recovery via Neural Leakage"
authors:
  - "Kwangjo Kim"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/734"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/734"
tags: [cryptanalysis, provable-security, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We investigate the security of AES-128/192/256 when implemented as ReLUbased neural networks via the natural sum-of-corners construction. Although these implementations are bit-exact on Boolean inputs, they extend AES into a continuous piecewise-linear function over R128 .

## Key claims (as reported)
- We show that under real-valued oracle access, such neural realizations admit deterministic linear-time master-key recovery.
- The attack exploits a geometric property of the natural XOR (AddRoundKey) layer: for corner parameter c < 1, ReLU activations partition the input space into key-dependent linear regions.
- Using symmetric perturbations, exactly one key hypothesis preserves linear-region membership, enabling bitwise recovery through simple output-equality tests.
- We formalize this phenomenon via a local separability lemma and obtain attack complexity O(128R) neural queries for R rounds.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-734.pdf`
