---
id: KN-LIT-2349
type: literature
title: "Adaptively Secure Garbling with Applications to"
authors:
  - "One-Time Programs"
  - "Secure Outsourcing"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, mpc, pairing, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Standard constructions of garbled circuits provide only static security, meaning the input x is not allowed to depend on the garbled circuit F . But some applications—notably one-time programs (Goldwasser, Kalai, and Rothblum 2008) and secure outsourcing (Gennaro, Gentry, Parno 2010)—need adaptive security, where x may depend on F .

## Key claims (as reported)
- We identify gaps in proofs from these papers with regard to adaptive security and suggest the need of a better abstraction boundary.
- To this end we investigate the adaptive security of garbling schemes, an abstraction of Yao’s garbled-circuit technique that we recently introduced (Bellare, Hoang, Rogaway 2012).
- Building on that framework, we give definitions encompassing privacy, authenticity, and obliviousness, with either coarsegrained or fine-grained adaptivity.
- We show how adaptively secure garbling schemes support simple solutions for one-time programs and secure outsourcing, with privacy being the goal in the first case and obliviousness and authenticity the goal in the second.We give transforms that promote static-secure garbling schemes to adaptive-secure ones.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/76580129 (1).pdf`
- `downloads/76580129 (2).pdf`
- `downloads/76580129 (3).pdf`
- `downloads/76580129.pdf`
