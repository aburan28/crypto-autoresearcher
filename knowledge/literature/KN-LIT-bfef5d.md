---
id: KN-LIT-bfef5d
type: literature
title: "Leveraging HLS to design a versatile & high-performance Classic McEliece accelerator"
authors:
  - "Ioannis-Vatistas Kostalabros"
  - "Jordi Ribes"
  - "Xavier Carril"
  - "Oriol Farras"
  - "Carles Hernandez"
  - "Miquel Moreto"
year: 2024
venue: "ACM Transactions on Embedded Computing Systems"
identifiers:
  eprint: null
  doi: "10.1145/3698395"
  arxiv: null
  url: "https://dl.acm.org/doi/abs/10.1145/3698395"
tags: [classic-mceliece, code-based, implementation, hardware, hls, accelerator, versatile]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
Uses **high-level synthesis** to design a versatile, high-performance Classic
McEliece accelerator — versatility (supporting multiple parameter sets) being
traded against the peak performance a fixed-parameter design could reach.

## Key claims (as reported)
- An HLS-designed accelerator that is both versatile across parameter sets and high-performance.

## Relevance to this program
The **versatility/performance trade** is the interesting axis. A design serving
all parameter sets is more useful and slower than one specialised to a single
set; which to build depends on the deployment question, not on the benchmark.

This program faces the same choice in its tooling: a general instrument that
serves many experiments versus a specialised one that serves the current
experiment better. `/curate-knowledge` promotes a method to `KN-TECH` only when
it has been validated across two or more experiments — a rule that encodes a
preference for the general instrument once it has earned it.

**Does not bear on the ECDLP.**

## Not verified here
citation verified against the Crossref record (DOI 10.1145/3698395).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

Performance figures and the parameter sets supported are NOT recorded here.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
