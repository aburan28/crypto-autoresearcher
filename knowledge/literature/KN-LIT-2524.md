---
id: KN-LIT-2524
type: literature
title: "Analysis of RIPEMD-160: New Collision"
authors:
  - "Yingxin Li"
  - "Takanori Isobe"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, pairing]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The hash function RIPEMD-160 is an ISO/IEC standard and is being used to generate the bitcoin address together with SHA-256. Despite the fact that many hash functions in the MD-SHA hash family have been broken, RIPEMD-160 remains secure and the best collision attack could only reach up to 34 out of 80 rounds, which was published at CRYPTO 2019.

## Key claims (as reported)
- In this paper, we propose a new collision attack on RIPEMD-160 that can reach up to 36 rounds with time complexity 264.5 .
- This new attack is facilitated by a new strategy to choose the message differences and new techniques to simultaneously handle the differential conditions on both branches.
- Moreover, different from all the previous work on RIPEMD-160, we utilize a MILP-based method to search for differential characteristics, where we construct a model to accurately describe the signed difference transitions through its round function.
- As far as we know, this is the first model targeting the signed difference transitions for the MD-SHA hash family.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14004040 (1).pdf`
- `downloads/14004040.pdf`
