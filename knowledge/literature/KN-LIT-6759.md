---
id: KN-LIT-6759
type: literature
title: "SPARKs: Succinct Parallelizable Arguments of Knowledge"
authors:
  - "Naomi Ephraim"
  - "Cody Freitag"
  - "Ilan Komargodski"
  - "Rafael Pass"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, quantum, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We introduce the notion of a Succinct Parallelizable Argument of Knowledge (SPARK). This is an argument system with the following three properties for computing and proving a time T (nondeterministic) computation: — The prover’s (parallel) running time is T + polylog T .

## Key claims (as reported)
- (In other words, the prover’s running time is essentially T for large computation times!) — The prover uses at most polylog T processors. — The communication complexity and verifier complexity are both polylog T .
- While the third property is standard in succinct arguments, the combination of all three is desirable as it gives a way to leverage moderate parallelism in favor of near-optimal running time.
- We emphasize that even a factor two overhead in the prover’s parallel running time is not allowed.
- Our main results are the following, all for non-deterministic polynomialtime RAM computation.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12105435 (1).pdf`
- `downloads/12105435.pdf`
