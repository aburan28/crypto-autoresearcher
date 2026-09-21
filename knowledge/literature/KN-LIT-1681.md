---
id: KN-LIT-1681
type: literature
title: Highlights Image Encryption via DataIdentified Discrete Chaotic Maps
authors:
- Wenyuan Li
- Xiao-Yun Wang
- Zhigang Zhu
- Xiaofeng Zhang
- Li Zhang
year: 2026
venue: arXiv preprint
identifiers:
  eprint: null
  doi: null
  arxiv: '2605.21118'
  url: https://arxiv.org/abs/2605.21118
tags:
- symmetric
- image-encryption
- chaotic-map
- implementation
confidence: reported
citation_verified: read
added: '2026-07-24'
superseded_by: null
---

## Contribution
Keywords: Image encryption SINDy-PI Discrete chaotic map In this work, we propose a data-driven image encryption framework that identifies chaotic maps directly from data via the SINDy-PI algorithm. Unlike conventional encryption schemes relying on predefined maps, our method learns the full explicit dynamicsincluding cross-terms and higher-order nonlinearitiesfrom observational data.

## Key claims (as reported)
- The validity of this approach is verified on three distinct chaotic systems: the Hénon map, the threedimensional logistic map, and the piecewiselinear Lozi map, demonstrating its generality.
- The encryption key consists solely of initial conditions; the map structure itself becomes datadependent, introducing an extra layer of security.
- Moreover, even when the initial conditions are fixed, different training data (e.g., with a tiny noise seed) lead to slightly different maps, which produce completely different ciphertexts (NPCR ≈ 99.6%, UACI ≈ 33.5%).
- Numerical experiments on the Hénon system show nearideal information entropy (≈ 8 bits), negligible inter-pixel correlation, and extreme sensitivity to initial conditions: a perturbation of 10−16 causes total decryption failure.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2605.21118v2.pdf`
