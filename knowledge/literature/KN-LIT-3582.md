---
id: KN-LIT-3582
type: literature
title: "Efficient KZG-based Univariate Sum-check and Lookup Argument"
authors:
  - "Yuncong Zhang"
  - "Shi-Feng Sun⋆"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [curve-arithmetic, pairing, survey, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We propose a novel KZG-based sum-check scheme, dubbed Losum, with optimal efficiency. Particularly, its proving cost is one multiscalar-multiplication of size k—the number of non-zero entries in the vector, its verification cost is one pairing plus one group scalar multiplication, and the proof consists of only one group element.

## Key claims (as reported)
- Using Losum as a component, we then construct a new lookup argument, named Locq, which enjoys a smaller proof size and a lower verification cost compared to the state of the arts cq, cq+ and cq++.
- Specifically, the proving cost of Locq is comparable to cq, keeping the advantage that the proving cost is independent of the table size after preprocessing.
- For verification, Locq costs four pairings, while cq, cq+ and cq++ require five, five and six pairings, respectively.
- For proof size, a Locq proof consists of four G1 elements and one G2 element; when instantiated with the BLS12-381 curve, the proof size of Locq is 2304 bits, while cq, cq+ and cq++ have 3840, 3328 and 2944 bits, respectively.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14602099 (1).pdf`
- `downloads/14602099.pdf`
