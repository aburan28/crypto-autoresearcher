---
id: KN-LIT-1797
type: literature
title: "Optimized Point Addition Circuits for Elliptic"
authors:
  - "Curve Discrete Logarithms"
year: 2026
venue: "arXiv preprint"
identifiers:
  eprint: "iacr:2026/1128"
  doi: null
  arxiv: "2606.02235"
  url: "https://arxiv.org/abs/2606.02235"
tags: [cryptanalysis, dlp, ecdlp, elliptic-curve, finite-field, pqc, prime-field, provable-security, quantum, rsa, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Shor’s algorithm represents the main threat of quantum computers to cryptography. In order to precisely understand its feasibility, many authors have worked towards reducing its costs, either at the logical level (assuming a fault-tolerant architecture), or at the physical level (taking into account the constraints of envisioned hardware).

## Key claims (as reported)
- In particular, recent works by Chevignard et al.
- (CRYPTO 2024) and Gidney (arXiv 2025) used improved arithmetic to significantly reduce the qubit cost of factoring RSA public keys.
- Even more recently, Babbush et al.
- (arXiv 2026) improved the cost of computing elliptic curve discrete logarithms, with a reduction of a factor 2 to 3 in gate count and qubit count compared to a previous work by Litinski (arXiv 2023).

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-1128.pdf`
- `downloads/2606.02235v1 (1).pdf`
- `downloads/2606.02235v1.pdf`
