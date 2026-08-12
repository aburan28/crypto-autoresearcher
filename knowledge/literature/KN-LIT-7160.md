---
id: KN-LIT-7160
type: literature
title: "Time space tradeoffs for attacks against one-way functions and PRGs"
authors:
  - "Anindya De"
  - "Luca Trevisan"
  - "Madhur Tulsiani"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We study time space tradeoffs in the complexity of attacks against one-way functions and pseudorandom generators. Fiat and Naor [7] show that for every function f : [N ] → [N ], there is an algorithm that inverts f everywhere using (ignoring lower order factors) time, space and advice at most N 3/4 .

## Key claims (as reported)
- We show that an algorithm using time, space and advice at most √ 5 3 max{ 4 N 4 , N } exists that inverts f on at least an  fraction of inputs.
- A lower bound q of √ Ω̃( N ) also holds, making our result tight in the “low end” of  ≤ 3 N1 .
- (Both the results of Fiat and Naor and ours are formulated as more general trade-offs between the time and the space and advice length of the algorithm.
- The results quoted above correspond to the interesting special case in which time equals space and advice length.) We also show that for every length-increasing generator G : [N ] → [2N ] there is a algorithm that achieves distinguishing probability  between the output of G and the uniform distribution and that can be implemented in polynomial (in log N ) time and with advice and space O(2 · N log N ).

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/62230646 (1).pdf`
- `downloads/62230646 (2).pdf`
- `downloads/62230646 (3).pdf`
- `downloads/62230646.pdf`
