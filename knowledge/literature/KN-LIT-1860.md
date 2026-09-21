---
id: KN-LIT-1860
type: literature
title: "Schnorr-like Proofs of Knowledge for Hidden Oil"
authors:
  - "Subspaces in UOV"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/1021"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/1021"
tags: [signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A UOV public key hides a distinguished linear subspace: the public-coordinate image of the central oil-coordinate subspace. In central coordinates, the homogeneous quadratic part of each UOV polynomial contains no oil-oil monomials.

## Key claims (as reported)
- Consequently, for every honestly generated UOV public key, each public homogeneous quadratic form vanishes when restricted to this hidden oil subspace.
- We formalize the hidden oil-subspace relation and construct a Schnorr-like Sigma protocol that proves knowledge of such a subspace without revealing it.
- The witness consists of matrices B, W satisfying W B = Io and Qk (Bz) ≡ 0 for all public quadratic forms Qk .
- The prover masks the witness linearly and responds to a challenge c with Z = A + cB, Y = E + cW , yielding a protocol with computational 3-special soundness and computational honest-verifier zero knowledge.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-1021.pdf`
