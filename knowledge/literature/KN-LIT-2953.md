---
id: KN-LIT-2953
type: literature
title: "Collisions and Semi-Free-Start Collisions for Round-Reduced RIPEMD-160"
authors:
  - "Fukang Liu"
  - "Florian Mendel"
  - "Gaoli Wang"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we propose an improved cryptanalysis of the double-branch hash function RIPEMD-160 standardized by ISO/IEC. Firstly, we show how to theoretically calculate the step differential probability of RIPEMD-160, which was stated as an open problem by Mendel et al. at ASIACRYPT 2013.

## Key claims (as reported)
- Secondly, based on the method proposed by Mendel et al. to automatically find a differential path of RIPEMD160, we construct a 30-step differential path where the left branch is sparse and the right branch is controlled as sparse as possible.
- To ensure the message modification techniques can be applied to RIPEMD-160, some extra bit conditions should be pre-deduced and well controlled.
- These extra bit conditions are used to ensure that the modular difference can be correctly propagated.
- This way, we can find a collision of 30-step RIPEMD-160 with complexity 267 .

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/106240194 (1).pdf`
- `downloads/106240194.pdf`
