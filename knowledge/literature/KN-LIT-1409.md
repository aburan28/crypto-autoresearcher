---
id: KN-LIT-1409
type: literature
title: "Insecurity of One Ring Signature Scheme with Batch Verification for Applications in VANETs"
authors:
  - "Zhengjun Cao"
year: 2025
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2025/999"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2025/999"
tags: [dlp, ecdlp, elliptic-curve, hash, quantum, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We show that the Negi-Kumar certificateless ring signature scheme [Wirel. 134(4): 1987-2011 (2024)] is insecure against forgery attack.

## Key claims (as reported)
- The signer’s public key P Kj and secret key P SKj are simply invoked to compute the hash value H2j = h5 (mj kP SKj kP Kj ktj ), which cannot be retrieved by the verifier for checking their dependency.
- The explicit dependency between the public key and secret key is not properly used to construct some intractable problems, such as Elliptic Curve Discrete Logarithm (ECDL), Computational Diffie-Hellman (CDH), and Decisional Diffie-Hellman (DDH).
- An adversary can find an efficient signing algorithm functionally equivalent to the valid signing algorithm.
- The findings in this note could be helpful for the newcomers who are not familiar with the designing techniques for certificateless ring signature.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2025-999.pdf`
