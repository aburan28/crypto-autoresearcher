---
id: KN-LIT-998
type: literature
title: "Key Structures: Improved Related-Key Boomerang Attack against the Full AES-256"
authors:
  - "Jian Guo"
  - "Ling Song"
  - "Haoyang Wang(B)"
year: 2022
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2022/845"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2022/845"
tags: [cryptanalysis, hash, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper introduces structure to key, in the related-key attack settings. While the idea of structure has been long used in keyrecovery attacks against block ciphers to enjoy the birthday effect, the same had not been applied to key materials due to the fact that key structure results in uncontrolled differences in key and hence affects the validity or probabilities of the differential trails.

## Key claims (as reported)
- We apply this simple idea to improve the related-key boomerang attack against AES-256 by Biryukov and Khovratovich in 2009.
- Surprisingly, it turns out to be effective, i.e., both data and time complexities are reduced by a factor of about 28 , to 292 and 291 respectively, at the cost of the amount of required keys increased from 4 to 219 .
- There exist some tradeoffs between the data/time complexity and the number of keys.
- To the best of our knowledge, this is the first essential improvement of the attack against the full AES-256 since 2009.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2022-845.pdf`
