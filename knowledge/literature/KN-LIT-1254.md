---
id: KN-LIT-1254
type: literature
title: "Key Collisions on AES and Its Applications"
authors:
  - "Kodai Taiyama"
  - "Kosei Sakamoto"
  - "Ryoma Ito"
  - "Kazuma Taka"
year: 2024
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2024/1508"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2024/1508"
tags: [symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we explore a new type of key collisions called target-plaintext key collisions of AES, which emerge as an open problem in the key committing security and are directly converted into singleblock collision attacks on Davies-Meyer (DM) hashing mode. For this key collision, a ciphertext collision is uniquely observed when a specific plaintext is encrypted under two distinct keys.

## Key claims (as reported)
- We introduce an efficient automatic search tool designed to find target-plaintext key collisions.
- This tool exploits bit-wise behaviors of differential characteristics and dependencies among operations and internal variables of both data processing and key scheduling parts.
- This allows us to hierarchically perform rebound-type attacks to identify key collisions.
- As a result, we demonstrate single-block collision attacks on 2/5/6-round AES128/192/256-DM and semi-free-start collision attacks on 5/7/9-round AES-128/192/256-DM, respectively.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2024-1508.pdf`
