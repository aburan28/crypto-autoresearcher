---
id: KN-LIT-5883
type: literature
title: "Preimage and Collision Attacks on MD2"
authors:
  - "Lars R. Knudsen"
  - "John E. Mathiassen"
year: null
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper contains several attacks on the hash function MD2 which has a hash code size of 128 bits. At Asiacrypt 2004 Muller presents the first known preimage attack on MD2.

## Key claims (as reported)
- The time complexity of the attack is about 2104 and the preimages consist always of 128 blocks.
- We present a preimage attack of complexity about 297 with the further advantage that the preimages are of variable lengths.
- Moreover we are always able to find many preimages for one given hash value.
- Also we introduce many new collisions for the MD2 compression function, which lead to the first known (pseudo) collisions for the full MD2 (including the checksum), but where the initial values differ.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/35570253 (1).pdf`
- `downloads/35570253 (2).pdf`
- `downloads/35570253 (3).pdf`
- `downloads/35570253.pdf`
