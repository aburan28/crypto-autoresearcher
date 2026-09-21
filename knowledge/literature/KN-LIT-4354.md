---
id: KN-LIT-4354
type: literature
title: "Implementing BP-Obfuscation Using Graph-Induced Encoding"
authors:
  - "Shai Halevi"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, pairing]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We implemented (a simplified version of) the branching-program obfuscator due to Gentry et al. (GGH15), which is itself a variation of the first obfuscation candidate by Garg et al.

## Key claims (as reported)
- To keep within the realm of feasibility, we had to give up on some aspects of the construction, specifically the “multiplicative bundling” factors that protect against mixedinput attacks.
- Hence our implementation can only support read-once branching programs.
- To be able to handle anything more than just toy problems, we developed a host of algorithmic and code-level optimizations.
- These include new variants of discrete Gaussian sampler and lattice trapdoor sampler, efficient matrix-manipulation routines, and many tradeoffs.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/obfus.pdf`
