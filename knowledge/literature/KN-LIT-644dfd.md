---
id: KN-LIT-644dfd
type: literature
title: "Hybrid-grained GPU implementations for the Classic McEliece"
authors:
  - "Dingyan Xu"
  - "Yiwen Gao"
  - "Yongbin Zhou"
  - "Jian Weng"
year: 2025
venue: "ISPA"
identifiers:
  eprint: null
  doi: "10.1109/ispa67752.2025.00164"
  arxiv: null
  url: "https://ieeexplore.ieee.org/abstract/document/11245258"
tags: [classic-mceliece, code-based, implementation, gpu, parallel, throughput]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
**Hybrid-grained GPU implementations** of Classic McEliece — mixing
granularities of parallelism (coarse-grained across independent operations,
fine-grained within one) to fit the GPU execution model.

## Key claims (as reported)
- GPU implementations of Classic McEliece using mixed parallelism granularity.

## Relevance to this program
Part of a GPU cluster ([[KN-LIT-06af57]], [[KN-LIT-6938cf]]) that is
methodologically interesting to this program because **granularity choice, not
raw throughput, is where the wins come from.** The same is true of this
program's own solver work: a parallel run's efficiency is usually decided by how
work is decomposed, not by how many cores it is given.

**Does not bear on the ECDLP.**

## Not verified here
citation verified against the Crossref record (DOI 10.1109/ispa67752.2025.00164).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

Throughput figures, GPU model, and the baseline are NOT recorded here. The IEEE
page was not fetched.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
