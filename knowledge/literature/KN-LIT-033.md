---
id: KN-LIT-033
type: literature
title: Simulating Quantum Computation by Contracting Tensor Networks
authors: [Markov Igor L., Shi Yaoyun]
year: 2008
venue: SIAM Journal on Computing, 38(3):963-981
identifiers:
  eprint: null
  doi: 10.1137/050644756
  arxiv: "quant-ph/0511069"
  url: https://epubs.siam.org/doi/10.1137/050644756
tags: [tensor-network, contraction, treewidth, complexity, counting, semaev]
confidence: reported
citation_verified: web
added: 2026-07-22
superseded_by: null
---

## Contribution
Proves that contracting a tensor network can be done in time exponential only in
the *treewidth* of the network's underlying (line) graph. Bounded-treewidth
networks therefore contract efficiently, tying contraction cost to a
graph-structural parameter.

## Key claims (as reported)
- Simulation cost T^{O(1)} * exp[O(w)] for a network of treewidth w.
- Consequence: log-depth / bounded-treewidth structures are tractable; the cost
  driver is the contraction schedule's width, not the raw tensor sizes.
- Counting connection: Kourtis-Chamon-Mucciolo-Ruckenstein, "Fast counting with
  tensor networks," SciPost Phys. 7(5):060, 2019 (doi:10.21468/SciPostPhys.7.5.060,
  arXiv:1805.00475) -- recasts #SAT/#CSP counting as tensor-network contraction,
  efficient at low treewidth / bounded bond rank.

## Relevance to this program
Supplies the complexity theorem for the program's tensor-network candidate
(RQ-TTN-001, KN-OPEN-007): the Semaev recursion tree's treewidth / bond rank,
not dense-resultant degree, is the true cost driver of contraction-based solution
counting. Kourtis et al. is the direct precedent for treating an algebraic
counting problem as contractible tensor network. Whether the Semaev tensor's
bond ranks stay bounded (tractable) or are generically full (intractable, method
== dense resultant) is the measured question.

## Not verified here
Full paper not read; the treewidth contraction bound and the counting connection
relayed from abstracts and standard references. Fields confirmed against the SIAM
DOI and arXiv records via search, not by fetching the primary pages.
