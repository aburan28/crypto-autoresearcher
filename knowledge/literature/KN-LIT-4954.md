---
id: KN-LIT-4954
type: literature
title: "More Efficient Algorithms for the NTRU Key Generation using the Field Norm"
authors:
  - "Thomas Pornin"
  - "Thomas Prest∗"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, quantum, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
NTRU lattices[13] are a class of polynomial rings which allow for compact and efficient representations of the lattice basis, thereby offering very good performance characteristics for the asymmetric algorithms that use them. Signature algorithms based on NTRU lattices have fast signature generation and verification, and relatively small signatures, public keys and private keys.

## Key claims (as reported)
- A few lattice-based cryptographic schemes entail, generally during the key generation, solving the NTRU equation: f G − gF = q mod xn + 1 Here f and g are fixed, the goal is to compute solutions F and G to the equation, and all the polynomials are in Z[x]/(xn + 1).
- The existing methods for solving this equation are quite cumbersome: their time and space complexities are at least cubic and quadratic in the dimension n, and for typical parameters they therefore require several megabytes of RAM and take more than a second on a typical laptop, precluding onboard key generation in embedded systems such as smart cards.
- In this work, we present two new algorithms for solving the NTRU equation.
- Both algorithms make a repeated use of the field norm in tower of fields; it allows them to be faster and more compact than existing algorithms by factors Õ(n).

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/114420276 (1).pdf`
- `downloads/114420276.pdf`
