---
id: KN-LIT-2725
type: literature
title: "Black-Box Construction of a Non-Malleable Encryption Scheme from Any Semantically Secure One"
authors:
  - "Seung Geol Choi"
  - "Dana Dachman-Soled"
  - "Tal Malkin"
  - "Hoeteck Wee"
year: null
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, provable-security, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We show how to transform any semantically secure encryption scheme into a non-malleable one, with a black-box construction that achieves a quasilinear blow-up in the size of the ciphertext. This improves upon the previous non-black-box construction of Pass, Shelat and Vaikuntanathan (Crypto ’06).

## Key claims (as reported)
- Our construction also extends readily to guarantee non-malleability under a boundedCCA2 attack, thereby simultaneously improving on both results in the work of Cramer et al.
- Our construction departs from the oft-used paradigm of re-encrypting the same message with different keys and then proving consistency of encryptions; instead, we encrypt an encoding of the message with certain locally testable and selfcorrecting properties.
- We exploit the fact that low-degree polynomials are simultaneously good error-correcting codes and a secret-sharing scheme.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/49480422 (1).pdf`
- `downloads/49480422 (2).pdf`
- `downloads/49480422 (3).pdf`
- `downloads/49480422.pdf`
