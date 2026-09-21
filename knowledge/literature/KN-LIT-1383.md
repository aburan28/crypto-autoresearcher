---
id: KN-LIT-1383
type: literature
title: "Efficient Privacy-Preserving Blueprints for Threshold Comparison"
authors:
  - "Pratyush Ranjan Tiwari"
  - "Harry Eldridge"
  - "Matthew Green"
year: 2025
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2025/2253"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2025/2253"
tags: [zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Privacy-Preserving Blueprints (PPBs), introduced by Kohlweiss et al. in in EUROCRYPT 2023, offer a method for balancing user privacy and bad-actor detection in private cryptocurrencies. A PPB scheme allows a user to append a verifiable escrow to their transactions which reveals some identifying information to an authority in the case that the user misbehaved.

## Key claims (as reported)
- A natural PPB functionality is for escrows to reveal user information if the user sends an amount of currency over a certain threshold.
- However, prior works constructing PPBs for such a functionality have severe limitations when it comes to efficiency: escrows are either computationally infeasible to compute, or too large to be plausibly stored on a large-scale distributed ledger.
- We address these gaps by constructing a space and computation-efficient PPB for threshold comparison, producing escrows under 2kb that can be computed in seconds.
- The scheme can be instantiated using well-known cryptographic primitives, namely variants of the ElGamal encryption scheme and generic non-interactive zero-knowledge proofs.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2025-2253.pdf`
