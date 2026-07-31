---
id: KN-LIT-1380
type: literature
title: "ECDSA Cracking Methods"
authors:
  - "William J. Buchanan"
  - "Jamie Gilchrist"
  - "Keir Finlow-Bates"
year: 2025
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2025/654"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2025/654"
tags: [ecdsa, elliptic-curve, rsa, side-channel, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The ECDSA (Elliptic Curve Digital Signature Algorithm) is used in many blockchain networks for digital signatures. This includes the Bitcoin and the Ethereum blockchains.

## Key claims (as reported)
- While it has good performance levels and as strong current security, it should be handled with care.
- This care typically relates to the usage of the nonce value which is used to create the signature.
- This paper outlines the methods that can be used to break ECDSA signatures, including revealed nonces, weak nonce choice, nonce reuse, two keys and shared nonces, and fault attack.

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2025-654.pdf`
