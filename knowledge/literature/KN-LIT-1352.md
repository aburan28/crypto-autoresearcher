---
id: KN-LIT-1352
type: literature
title: "Breaking ECDSA with Two Affinely Related Nonces"
authors:
  - "Jamie Gilchrist"
  - "William J. Buchanan"
  - "Keir Finlow-Bates"
year: 2025
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2025/705"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2025/705"
tags: [cryptanalysis, curve-arithmetic, ecdsa, elliptic-curve, finite-field, lattice, protocol, provable-security, rsa, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The security of the Elliptic Curve Digital Signature Algorithm (ECDSA) depends on the uniqueness and secrecy of the nonce, which is used in each signature. While it is well understood that nonce k reuse across two distinct messages can leak the private key, we show that even if a distinct value is used for k2 , where an affine relationship exists in the form of: km = a · kn + b, we can also recover the private key.

## Key claims (as reported)
- Our method requires only two signatures (even over the same message) and relies purely on algebra, with no need for lattice reduction or brute-force search(if the relationship, or offset, is known).
- To our knowledge, this is the first closed-form derivation of the ECDSA private key from only two signatures over the same message, under a known affine relationship between nonces.

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2025-705.pdf`
