---
id: KN-LIT-1759
type: literature
title: "New Quantum Circuits for ECDLP: Breaking Prime Elliptic Curve Cryptography"
authors:
  - "Hyunji Kim∗"
  - "Kyungbae Jang∗"
  - "Siyi Wang"
  - "Vikas Srivastava"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/106"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/106"
tags: [binary-field, cryptanalysis, dlp, ecdlp, elliptic-curve, factoring, finite-field, pqc, prime-field, protocol, quantum, rsa, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper improves quantum circuits for realizing Shor’s algorithm on elliptic curves. We present optimized quantum point addition circuits that focus on reducing circuit depth at the cost of using more qubits.

## Key claims (as reported)
- Our implementation includes in-place and out-of-place point additions, considering both affine and projective coordinates, respectively.
- This significantly reduces the circuit depth and achieves about 58%–82% improvement in the qubit count – T -depth product and 43%–87% improvement in the qubit count – full depth product over previous works, including those of M.
- (Asiacrypt 2017) and T.
- Based on these circuits, we construct Shor’s algorithm and evaluate the post-quantum security of elliptic curve cryptography.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-106 (1).pdf`
- `downloads/2026-106.pdf`
