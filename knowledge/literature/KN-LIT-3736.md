---
id: KN-LIT-3736
type: literature
title: "Exploring SAT for Cryptanalysis: (Quantum) Collision Attacks against 6-Round"
authors:
  - "Jian Guo "
  - "Guozhen Liu "
  - "Ling Song "
  - "Yi Tu "
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, glv-gls, hash, pqc, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this work, we focus on collision attacks against instances of SHA-3 hash family in both classical and quantum settings. Since the 5-round collision attacks on SHA3-256 and other variants proposed by Guo et al. at JoC 2020, no other essential progress has been published.

## Key claims (as reported)
- With a thorough investigation, we identify that the challenges of extending such collision attacks on SHA-3 to more rounds lie in the inefficiency of differential trail search.
- To overcome this obstacle, we develop a SATbased automatic search toolkit.
- The tool is used in multiple intermediate steps of the collision attacks and exhibits surprisingly high efficiency in differential trail search and other optimization problems encountered in the process.
- As a result, we present the first 6-round classical collision attack on SHAKE128 with time complexity 2123.5 , which also forms a quan√ tum collision attack with quantum time 267.25/ S , and the first 6-round quantum collision attack on SHA3-224 and SHA3-256 with quantum time √ √ 297.75/ S and 2104.25/ S , where S represents the hardware resources of the quantum computer.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/137910362 (1).pdf`
- `downloads/137910362.pdf`
