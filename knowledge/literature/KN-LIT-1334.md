---
id: KN-LIT-1334
type: literature
title: "A Note on “CABC: A Cross-Domain Authentication Method Combining Blockchain with Certificateless Signature for IIoT”"
authors:
  - "Zhengjun Cao"
year: 2025
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2025/834"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2025/834"
tags: [dlp, ecdlp, elliptic-curve, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We show that the authentication method [Future Gener. 158: 516-529 (2024)] cannot be practically implemented, because the signature scheme is insecure against certificateless public key replacement forgery attack.

## Key claims (as reported)
- The explicit dependency between the certificateless public key and secret key is not properly used to construct some intractable problems, such as Elliptic Curve Discrete Logarithm (ECDL).
- An adversary can find an efficient signing algorithm functionally equivalent to the valid signing algorithm.
- We also correct some typos in the original presentation.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2025-834.pdf`
