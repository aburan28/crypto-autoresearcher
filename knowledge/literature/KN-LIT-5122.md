---
id: KN-LIT-5122
type: literature
title: "New Key-Recovery Attacks on HMAC/NMAC-MD4 and"
authors:
  - "Lei Wang"
  - "Kazuo Ohta"
  - "Noboru Kunihiro"
year: null
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, protocol]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
At Crypto ’07, Fouque, Leurent and Nguyen presented full key-recovery attacks on HMAC/NMAC-MD4 and NMAC-MD5, by extending the partial key-recovery attacks of Contini and Yin from Asiacrypt ’06. Such attacks are based on collision attacks on the underlying hash function, and the most expensive stage is the recovery of the so-called outer key.

## Key claims (as reported)
- In this paper, we show that the outer key can be recovered with near-collisions instead of collisions: near-collisions can be easier to find and can disclose more information.
- This improves the complexity of the FLN attack on HMAC/NMAC-MD4: the number of MAC queries decreases from 288 to 272 , and the number of MD4 computations decreases from 295 to 277 .
- We also improved the total complexity of the related-key attack on NMAC-MD5.
- Moreover, our attack on NMACMD5 can partially recover the outer key without the knowledge of the inner key, which might be of independent interest.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/49650235 (1).pdf`
- `downloads/49650235 (2).pdf`
- `downloads/49650235 (3).pdf`
- `downloads/49650235.pdf`
