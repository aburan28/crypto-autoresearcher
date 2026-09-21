---
id: KN-LIT-1328
type: literature
title: "A Little LESS Secure Side-Channel Attacks Exploiting Randomness Leakage"
authors:
  - "Dina Hesse"
year: 2025
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2025/913"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2025/913"
tags: [cryptanalysis, pqc, side-channel, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Schnorr and (EC)DSA signatures famously become completely insecure once a few bits of the random nonce are revealed to an attacker. In this work, we explore whether the Fiat-Shamir based postquantum signature scheme LESS is vulnerable to analogous attacks.

## Key claims (as reported)
- In particular, we investigate the impact of partial leakage of the commitment randomness – a scenario that falls under the broader class of Hidden Number Problems – on the security of the secret key.
- We present an efficient attack on LESS that requires knowledge of a single bit of the randomness with less than 1200 signatures to fully recover the secret key.
- Our attack leverages the observation that knowledge of one bit is sufficient to distinguish secret key entries from random candidates.
- In addition, we describe a variant of this attack that requires one-bit leakage of multiple randomness values, but succeeds with only two signatures.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2025-913.pdf`
