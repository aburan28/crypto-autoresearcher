---
id: KN-LIT-ace115
type: literature
title: "Acceleration of Classic McEliece post-quantum cryptosystem with cache processing"
authors:
  - "Cyrius Nugier"
  - "Vincent Migliore"
year: 2023
venue: "IEEE Micro"
identifiers:
  eprint: null
  doi: "10.1109/mm.2023.3304425"
  arxiv: null
  url: "https://hal.science/hal-04232870/"
tags: [classic-mceliece, code-based, implementation, cache, memory-hierarchy, acceleration]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
Acceleration of Classic McEliece using **cache processing** — exploiting the
memory hierarchy rather than the arithmetic units, which is the right target
given that the scheme's bottleneck is data movement over a very large key.

## Key claims (as reported)
- Cache-oriented processing accelerates Classic McEliece.

## Relevance to this program
The clearest instance in this cluster of optimising **the actual bottleneck**
rather than the conspicuous one. Classic McEliece is memory-bound; work on
arithmetic throughput addresses the wrong resource.

This is `KN-TECH-080`'s exact-bottleneck requirement stated in hardware terms,
and it is a mistake this program can make just as easily — optimising the step
that is easy to measure rather than the step that dominates.

**Does not bear on the ECDLP.**

## Not verified here
citation verified against the Crossref record (DOI 10.1109/mm.2023.3304425).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

Speedup figures and the platform are NOT recorded here.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
