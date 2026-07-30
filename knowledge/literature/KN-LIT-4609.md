---
id: KN-LIT-4609
type: literature
title: "Known-key Distinguisher on Full PRESENT"
authors: []
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this article, we analyse the known-key security of the standardized PRESENT lightweight block cipher. Namely, we propose a knownkey distinguisher on the full PRESENT, both 80- and 128-bit key versions.

## Key claims (as reported)
- We first leverage the very latest advances in differential cryptanalysis on PRESENT, which are as strong as the best linear cryptanalysis in terms of number of attacked rounds.
- Differential properties are much easier to handle for a known-key distinguisher than linear properties, and we use a bias on the number of collisions on some predetermined input/output bits as distinguishing property.
- In order to reach the full PRESENT, we eventually introduce a new meet-in-the-middle layer to propagate the differential properties as far as possible.
- Our techniques have been implemented and verified on the small scale variant of PRESENT.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/92160226 (1).pdf`
- `downloads/92160226 (2).pdf`
- `downloads/92160226.pdf`
