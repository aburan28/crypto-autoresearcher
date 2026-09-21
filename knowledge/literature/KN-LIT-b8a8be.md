---
id: KN-LIT-b8a8be
type: literature
title: "Memory-efficient quantum information set decoding algorithm"
authors:
  - "Naoto Kimura"
  - "Atsushi Takayasu"
  - "Tsuyoshi Takagi"
year: 2023
venue: "ACISP"
identifiers:
  eprint: null
  doi: "10.1007/978-3-031-35486-1_20"
  arxiv: null
  url: "https://link.springer.com/chapter/10.1007/978-3-031-35486-1_20"
tags: [isd, syndrome-decoding, code-based, mceliece, concrete-security, quantum, memory-constrained, resource-estimation]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
A **memory-efficient** quantum ISD algorithm. Advanced ISD variants (MMT, BJMM)
buy their time exponent with large lists; carrying those lists in quantum memory
is the step where the advantage is most easily lost, so constraining memory is
the sharp version of the question.

## Key claims (as reported)
- A quantum ISD algorithm with reduced memory requirements.
- Framed as memory-efficiency, i.e. an improvement on the axis where quantum ISD is weakest.

## Relevance to this program
Together with [[KN-LIT-072f64]] and [[KN-LIT-5677ae]], this makes the corpus's
low-memory ISD picture reasonably complete. The recurring finding across those
entries — that **the fancy variants lose most of their advantage once memory is
charged for** — is a result this program should expect to encounter in its own
work whenever a proposed speedup depends on a large precomputed table.

**Does not bear on the ECDLP.**

## Not verified here
citation verified against the Crossref record (DOI 10.1007/978-3-031-35486-1_20).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

The memory bound achieved and the time cost paid for it are NOT recorded here.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
