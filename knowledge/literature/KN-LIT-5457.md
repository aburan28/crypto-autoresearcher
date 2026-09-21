---
id: KN-LIT-5457
type: literature
title: "On the Depth of Oblivious Parallel RAM?"
authors:
  - "T-H. Hubert Chan"
  - "Kai-Min Chung"
  - "Elaine Shi"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, mpc, pairing]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Oblivious Parallel RAM (OPRAM), first proposed by Boyle, Chung, and Pass, is the natural parallel extension of Oblivious RAM (ORAM). OPRAM provides a powerful cryptographic building block for hiding the access patterns of programs to sensitive data, while preserving the paralellism inherent in the original program.

## Key claims (as reported)
- All prior OPRAM schemes adopt a single metric of “simulation overhead” that characterizes the blowup in parallel runtime, assuming that oblivious simulation is constrained to using the same number of CPUs as the original PRAM.
- In this paper, we ask whether oblivious simulation of PRAM programs can be further sped up if the OPRAM is allowed to have more CPUs than the original PRAM.
- We thus initiate a study to understand the true depth of OPRAM schemes (i.e., when the OPRAM may have access to unbounded number of CPUs).
- On the upper bound front, we construct a new OPRAM scheme that gains a logarithmic factor in depth and without incurring extra blowup in total work in comparison with the stateof-the-art OPRAM scheme.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/106240301 (1).pdf`
- `downloads/106240301.pdf`
