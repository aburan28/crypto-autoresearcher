---
id: KN-LIT-1062
type: literature
title: "A note on “authenticated key agreement protocols for dew-assisted IoT systems”"
authors:
  - "Zhengjun Cao"
year: 2023
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2023/1497"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2023/1497"
tags: [elliptic-curve, finite-field, hash, protocol, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We show that the key agreement scheme [J. Supercomput., 78:12093-12113, 2022] is flawed.

## Key claims (as reported)
- (1) It neglects the representation of a point over an elliptic curve and the basic requirement for bit-wise XOR, which results in a trivial equality.
- By the equality, an adversary can recover a target device’s identity, which means the scheme fails to keep anonymity.
- (2) It falsely requires that the central server should share its master secret key with each dew server.
- (3) The specified certificate is almost nonsensical.

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2023-1497.pdf`
