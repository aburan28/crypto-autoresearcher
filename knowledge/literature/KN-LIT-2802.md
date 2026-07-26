---
id: KN-LIT-2802
type: literature
title: "Breaking The FF3 Format-Preserving Encryption Standard Over Small Domains"
authors:
  - "F. Betül Durak"
  - "Serge Vaudenay"
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
The National Institute of Standards and Technology (NIST) recently published a Format-Preserving Encryption standard accepting two Feistel structure based schemes called FF1 and FF3. Particularly, FF3 is a tweakable block cipher based on an 8-round Feistel network.

## Key claims (as reported)
- In CCS 2016, Bellare et. al. gave an attack to break FF3 (and FF1) with time and data complexity O(N5 log(N)), which is much larger than the code book (but using many tweaks), where N2 is domain size to the Feistel network.
- In this work, we give a new practical total break attack to the FF3 scheme (also known as BPS scheme).
- Our FF3 attack 11 requires O(N 6 ) chosen plaintexts with time complexity O(N5 ).
- Our attack was successfully tested with N ⩽ 29 .

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10401209 (1).pdf`
- `downloads/10401209.pdf`
