---
id: KN-LIT-034
type: literature
title: Fast counting with tensor networks
authors: [Kourtis Stefanos, Chamon Claudio, Mucciolo Eduardo R., Ruckenstein Andrei E.]
year: 2019
venue: SciPost Physics, 7(5):060
identifiers:
  eprint: null
  doi: 10.21468/SciPostPhys.7.5.060
  arxiv: "1805.00475"
  url: https://scipost.org/SciPostPhys.7.5.060
tags: [tensor-network, counting, csp, sharp-sat, treewidth, contraction, solution-counting]
confidence: reported
citation_verified: web
added: 2026-07-22
superseded_by: null
---

## Contribution
Recasts counting problems (#SAT / #CSP) as tensor networks whose full
contraction yields the number of satisfying assignments. Graph heuristics choose
favorable contraction orders, making the method efficient when the network has
low treewidth / bounded bond rank (KN-LIT-033).

## Key claims (as reported)
- On #P-hard instances (monotone #1-in-3SAT, #Cubic-Vertex-Cover) it beats
  state-of-the-art exact counters by a significant margin.
- Demonstrates exact combinatorial counting reduces to structured tensor-network
  contraction, with bond rank / treewidth as the operative resource.

## Relevance to this program
The closest precedent for the program's tensor-network candidate
(RQ-TTN-001, EXP-TTN-001, KN-OPEN-007): treat Semaev decomposition solution
COUNTING (and enumeration by conditional contraction) as tensor-network
contraction, verifying every emitted tuple exactly (truncation can only lose
recall, never precision). The transferable idea is bond rank as the complexity
invariant; whether the Semaev resultant tensor's bond ranks are low (like these
tractable #CSP instances) or generically full is exactly the open measurement.

## Not verified here
Full paper not read; the counting-as-contraction reduction and benchmarks
relayed from the abstract. Fields confirmed against the SciPost DOI and arXiv
records via search, not by fetching the primary pages.
