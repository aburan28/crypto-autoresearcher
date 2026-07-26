---
id: KN-LIT-4188
type: literature
title: "Hidden Shift Quantum Cryptanalysis and Implications"
authors:
  - "Xavier Bonnetain"
  - "María Naya-Plasencia"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, pairing, pqc, quantum, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
At Eurocrypt 2017 a tweak to counter Simon’s quantum attack was proposed: replace the common bitwise addition with other operations, as a modular addition. The starting point of our paper is a follow up of these previous results: First, we have developed new algorithms that improves and generalizes Kuperberg’s algorithm for the hidden shift problem, which is the algorithm that applies instead of Simon when considering modular additions.

## Key claims (as reported)
- Thanks to our improved algorithm, we have been able to build a quantum attack in the superposition model on Poly1305, proposed at FSE 2005, widely used and claimed to be quantumly secure.
- We also answer an open problem by analyzing the effect of the tweak to the FX construction.
- We have also generalized the algorithm.
- We propose for the first time a quantum algorithm for solving the hidden problem with parallel modular additions, with a complexity that matches both Simon and Kuperberg in its extremes.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/11272155 (1).pdf`
- `downloads/11272155.pdf`
