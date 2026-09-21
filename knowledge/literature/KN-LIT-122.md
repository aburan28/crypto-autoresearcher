---
id: KN-LIT-122
type: literature
title: Estimating quantum speedups for lattice sieves
authors: [Albrecht Martin R., Gheorghiu Vlad, Postlethwaite Eamonn W., Schanck John M.]
year: 2020
venue: ASIACRYPT 2020 (ePrint 2019/1161)
identifiers:
  eprint: iacr:2019/1161
  doi: null
  url: https://eprint.iacr.org/2019/1161
tags: [quantum, sieving, near-neighbour-search, circuits, cost-model, gate-count, grover, resource-estimate, post-quantum, lattice, calibration]
confidence: reported
citation_verified: read
added: 2026-07-24
superseded_by: null
---

## Contribution
Replaces the asymptotic `2^(0.265b)` quantum sieving figure with a heuristic but
*non-asymptotic* analysis: explicit quantum circuits for near-neighbour search
on high-dimensional spheres, plus software that numerically optimises algorithm
parameters under several cost metrics. The headline result is deflationary.

## Key claims (as reported)
- For the most performant near-neighbour search algorithm analysed, the quantum
  speedup in dimensions of cryptanalytic interest is **small**.
- Achieving even that speedup requires several optimistic physical and
  algorithmic assumptions, stated as such by the authors.
- The analysis is heuristic and non-asymptotic, aimed at concrete cost rather
  than exponents; costs are computed for classical and quantum near-neighbour
  search under various metrics.

## Relevance to this program
The corrective to reading `2^(0.265b)` as a quantum attack cost. That exponent
is an asymptotic convention (KN-LIT-107); this paper does the circuit-level work
and finds the realisable advantage over classical sieving is small and
assumption-laden. That is the same conclusion pattern the ECDLP quantum
resource estimates reach (KN-LIT-099, KN-TECH-037) -- asymptotic quantum
advantage is real, concrete resource requirements are the binding constraint --
and it means the program should not treat a quantum exponent as a cost without
a circuit-level source.

This paper is also load-bearing in the dual-attack dispute: MATZOV (KN-LIT-110)
obtains part of its claimed security reduction precisely by *revising these*
sieving gate-count estimates downward. Anyone comparing MATZOV's numbers with
earlier ones is comparing two versions of this cost model, not two attacks.

## Not verified here
The ePrint abstract was fetched and read. The circuits were not checked, the
optimisation software was not run, and the specific speedup factors, dimensions
and cost metrics were not extracted from the full text. The phrase "small
quantum speedup" is the authors' characterisation and is not quantified in this
entry.
