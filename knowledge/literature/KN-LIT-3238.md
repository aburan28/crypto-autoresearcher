---
id: KN-LIT-3238
type: literature
title: "Cryptanalysis of GSM Encryption in 2G/3G Networks without Rainbow Tables"
authors:
  - "Bin Zhang"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, implementation, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The GSM standard developed by ETSI for 2G networks adopts the A5/1 stream cipher to protect the over-the-air privacy in cell phone and has become the de-facto global standard in mobile communications, though the emerging of subsequent 3G/4G standards. There are many cryptanalytic results available so far and the most notable ones share the need of a heavy pre-computation with large rainbow tables or distributed cracking network.

## Key claims (as reported)
- In this paper, we present a fast near collision attack on GSM encryption in 2G/3G networks, which is completely new and more threatening compared to the previous best results.
- We adapt the fast near collision attack proposed at Eurocrypt 2018 with the concrete irregular clocking manner in A5/1 to have a state recovery attack with a low complexity.
- It is shown that if the first 64 bits of one keystream frame are available, the secret key of A5/1 can be reliably found in 231.79 cipher ticks, given around 1 MB memory and after the pre-computation of 220.26 cipher ticks.
- Our current implementation clearly certified the validity of the suggested attack.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/119210208 (1).pdf`
- `downloads/119210208.pdf`
