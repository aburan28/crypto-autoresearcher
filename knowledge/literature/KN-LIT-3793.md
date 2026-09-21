---
id: KN-LIT-3793
type: literature
title: "Fast Correlation Attacks over Extension Fields, Large-unit Linear Approximation and Cryptanalysis of SNOW 2.0"
authors:
  - "Bin Zhang"
  - "Chao Xu"
  - "Willi Meier⋄"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, extension-field, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Several improvements of fast correlation attacks have been proposed during the past two decades, with a regrettable lack of a better generalization and adaptation to the concrete involved primitives, especially to those modern stream ciphers based on word-based LFSRs. In this paper, we develop some necessary cryptanalytic tools to bridge this gap.

## Key claims (as reported)
- First, a formal framework for fast correlation attacks over extension fields is constructed, under which the theoretical predictions of the computational complexities for both the offline and online/decoding phase can be reliably derived.
- Our decoding algorithm makes use of Fast Walsh Transform (FWT) to get a better performance.
- Second, an efficient algorithm to compute the large-unit distribution of a broad class of functions is proposed, which allows to find better linear approximations than the bitwise ones with low complexity in symmetric-key primitives.
- Last, we apply our methods to SNOW 2.0, an ISO/IEC 18033-4 standard stream cipher, which results in the significantly reduced complexities all below 2164.15 .

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/92160181 (1).pdf`
- `downloads/92160181 (2).pdf`
- `downloads/92160181.pdf`
