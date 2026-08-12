---
id: KN-LIT-4098
type: literature
title: "Generic Related-key Attacks for HMAC"
authors:
  - "Thomas Peyrin"
  - "Yu Sasaki"
  - "Lei Wang"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, pairing, protocol, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this article we describe new generic distinguishing and forgery attacks in the related-key scenario (using only a single relatedkey) for the HMAC construction. When HMAC uses a k-bit key, outputs an n-bit MAC, and is instantiated with an l-bit inner iterative hash function processing m-bit message blocks where m = k, our distinguishing-R attack requires about 2n/2 queries which improves over the currently best known generic attack complexity 2l/2 as soon as l > n.

## Key claims (as reported)
- This means that contrary to the general belief, using wide-pipe hash functions as internal primitive will not increase the overall security of HMAC in the related-key model when the key size is equal to the message block size.
- We also present generic related-key distinguishing-H, internal state recovery and forgery attacks.
- Our method is new and elegant, and uses a simple cyclesize detection criterion.
- The issue in the HMAC construction (not present in the NMAC construction) comes from the non-independence of the two inner hash layers and we provide a simple patch in order to avoid this generic attack.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/76580573 (1).pdf`
- `downloads/76580573 (2).pdf`
- `downloads/76580573 (3).pdf`
- `downloads/76580573.pdf`
