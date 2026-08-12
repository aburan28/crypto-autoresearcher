---
id: KN-LIT-7472
type: literature
title: "Very High Order Masking: Efficient"
authors:
  - "Security Evaluation"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [implementation, pairing, side-channel, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we study the performances and security of recent masking algorithms specialized to parallel implementations in a 32-bit embedded software platform, for the standard AES Rijndael and the bitslice cipher Fantomas. By exploiting the excellent features of these algorithms for bitslice implementations, we first extend the recent speed records of Goudarzi and Rivain (presented at Eurocrypt 2017) and report realistic timings for masked implementations with 32 shares.

## Key claims (as reported)
- We then observe that the security level provided by such implementations is uneasy to quantify with current evaluation tools.
- We therefore propose a new “multi-model” evaluation methodology which takes advantage of different (more or less abstract) security models introduced in the literature.
- This methodology allows us to both bound the security level of our implementations in a principled manner and to assess the risks of overstated security based on well understood parameters.
- Concretely, it leads us to conclude that these implementations withstand worst-case adversaries with > 264 measurements under falsifiable assumptions.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10529149 (1).pdf`
- `downloads/10529149.pdf`
