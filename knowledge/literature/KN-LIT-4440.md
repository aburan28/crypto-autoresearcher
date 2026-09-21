---
id: KN-LIT-4440
type: literature
title: "Improved Single-Key Attacks on 9-Round AES-192/256"
authors:
  - "Leibo Li"
  - "Keting Jia"
  - "Xiaoyun Wang"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper focuses on key-recovery attacks on 9-round AES192 and AES-256 under single-key model with the framework of the meet-in-the-middle attack. A new technique named key-dependent sieve is introduced to further reduce the size of lookup table of the attack, and the 9-round AES-192 is broken with 2121 chosen plaintexts, 2187.5 9-round encryptions and 2185 128-bit words of memory.

## Key claims (as reported)
- If the attack starts from the third round, the complexities would be further reduced by a factor of 16.
- Moreover, the whole attack is split up into a series of weak-key attacks.
- Then the memory complexity of the attack is saved significantly when we execute these weak attacks in streaming mode.
- This method is also applied to reduce the memory complexity of the attack on 9-round AES-256.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/85400131 (1).pdf`
- `downloads/85400131 (2).pdf`
- `downloads/85400131 (3).pdf`
- `downloads/85400131.pdf`
