---
id: KN-LIT-4383
type: literature
title: "Improved Attacks on Full GOST"
authors:
  - "Itai Dinur"
  - "Orr Dunkelman"
  - "Adi Shamir"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, pairing, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
GOST is a well known block cipher which was developed in the Soviet Union during the 1970’s as an alternative to the US-developed DES. In spite of considerable cryptanalytic effort, until very recently there were no published single key attacks against its full 32-round version which were faster than the 2256 time complexity of exhaustive search.

## Key claims (as reported)
- In February 2011, Isobe used the previously discovered reflection property in order to develop the first such attack, which requires 232 data, 264 memory and 2224 time.
- In this paper we introduce a new fixed point property and a better way to attack 8-round GOST in order to find improved attacks on full GOST: Given 232 data we can reduce the memory complexity from an impractical 264 to a practical 236 without changing the 2224 time complexity, and given 264 data we can simultaneously reduce the time complexity to 2192 and the memory complexity to 236 .

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/75490009 (1).pdf`
- `downloads/75490009 (2).pdf`
- `downloads/75490009 (3).pdf`
- `downloads/75490009.pdf`
