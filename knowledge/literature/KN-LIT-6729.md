---
id: KN-LIT-6729
type: literature
title: "Soft Analytical Side-Channel Attacks"
authors:
  - "Nicolas Veyrat-Charvillon"
  - "Benoı̂t Gérard"
  - "François-Xavier Standaert"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, pairing, side-channel, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we introduce a new approach to side-channel key recovery, that combines the low time/memory complexity and noise tolerance of standard (divide and conquer) differential power analysis with the optimal data complexity of algebraic side-channel attacks. Our fundamental contribution for this purpose is to change the way of expressing the problem, from the system of equations used in algebraic attacks to a code, essentially inspired by low density parity check codes.

## Key claims (as reported)
- We then show that such codes can be efficiently decoded, taking advantage of the sparsity of the information corresponding to intermediate variables in actual leakage traces.
- The resulting soft analytical side-channel attacks work under the same profiling assumptions as template attacks, and directly exploit the vectors of probabilities produced by these attacks.
- As a result, we bridge the gap between popular side-channel distinguishers based on simple statistical tests and previous approaches to analytical side-channel attacks that could only exploit hard information so far.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/88730239 (1).pdf`
- `downloads/88730239 (2).pdf`
- `downloads/88730239 (3).pdf`
- `downloads/88730239.pdf`
