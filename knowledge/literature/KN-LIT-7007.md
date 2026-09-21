---
id: KN-LIT-7007
type: literature
title: "The Knowledge Tightness of Parallel Zero-Knowledge"
authors:
  - "Kai-Min Chung"
  - "Rafael Pass"
  - "Wei-Lung Dustin Tseng"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, mpc, pairing, provable-security, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We investigate the concrete security of black-box zeroknowledge protocols when composed in parallel. As our main result, we give essentially tight upper and lower bounds (up to logarithmic factors in the security parameter) on the following measure of security (closely related to knowledge tightness): the number of queries made by black-box simulators when zero-knowledge protocols are composed in parallel.

## Key claims (as reported)
- As a function of the number of parallel sessions, k, and the round complexity of the protocol, m, the bound is roughly k1/m .
- We also construct a modular procedure to amplify simulator-query lower bounds (as above), to generic lower bounds in the black-box concurrent zero-knowledge setting.
- As a demonstration of our techniques, we give a self-contained proof of the o(log n/ log log n) lower bound for the round complexity of black-box concurrent zero-knowledge protocols, first shown by Canetti, Kilian, Petrank and Rosen (STOC 2002).
- Additionally, we give a new lower bound regarding constant-round black-box concurrent zero-knowledge protocols: the running time of the black-box simulator must be at least nΩ(log n) .

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/71940179 (1).pdf`
- `downloads/71940179 (2).pdf`
- `downloads/71940179 (3).pdf`
- `downloads/71940179.pdf`
