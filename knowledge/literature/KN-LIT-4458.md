---
id: KN-LIT-4458
type: literature
title: "Improving Support-Minors rank attacks:"
authors:
  - "John Baena"
  - "Pierre Briaud"
  - "Daniel Cabarcas"
  - "Ray Perlner"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, cryptanalysis, extension-field, pairing, pqc, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The Support-Minors (SM) method has opened new routes to attack multivariate schemes with rank properties that were previously impossible to exploit, as shown by the recent attacks of [40] and [9] on the Round 3 NIST candidates GeMSS and Rainbow respectively. In this paper, we study this SM approach more in depth and we propose a greatly improved attack on GeMSS based on this Support-Minors method.

## Key claims (as reported)
- Even though GeMSS was already affected by [40], our attack affects it even more and makes it completely unfeasible to repair the scheme by simply increasing the size of its parameters or even applying the recent projection technique from [36] whose purpose was to make GeMSS immune to [40].
- For instance, our attack on the GeMSS128 parameter set has estimated time complexity 272 , and repairing the scheme by applying [36] would result in a signature with slower signing time by an impractical factor of 214 .
- Another contribution is to suggest optimizations that can reduce memory access costs for an XL strategy on a large SM system using the Block-Wiedemann algorithm as subroutine when these costs are a concern.
- In a memory cost model based on [7], we show that the rectangular MinRank attack from [9] may indeed reduce the security for all Round 3 Rainbow parameter sets below their targeted security strengths, contradicting the lower bound claimed by [41] using the same memory cost model.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/135070031 (1).pdf`
- `downloads/135070031.pdf`
