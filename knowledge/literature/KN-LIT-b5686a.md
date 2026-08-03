---
id: KN-LIT-b5686a
type: literature
title: "McBits revisited"
authors:
  - "Tung Chou"
year: 2017
venue: "CHES"
identifiers:
  eprint: null
  doi: "10.1007/978-3-319-66787-4_11"
  arxiv: null
  url: "https://tungchou.github.io/papers/mcbits_revisited.pdf"
tags: [classic-mceliece, code-based, implementation, constant-time, bitslicing, software, mcbits]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
**McBits revisited** — a rework of the McBits constant-time code-based software
([[KN-LIT-4873]]), improving performance while keeping constant-time behaviour.

## Key claims (as reported)
- Improved constant-time software implementation of code-based cryptography.

## Relevance to this program
The constant-time software line matters because it demonstrates the point the
side-channel section keeps proving in the negative: **timing leakage is an
implementation choice, not an inherent property of the algorithm.**

Note the division of labour this pair illustrates — the mathematics is
unchanged, the security-relevant property is entirely in the implementation. A
result about one says nothing about the other, which is the separation rule 4
requires this program's conclusions to respect.

**Does not bear on the ECDLP.**

## Not verified here
citation verified against the Crossref record (DOI 10.1007/978-3-319-66787-4_11).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

Performance figures and the improvements over the original McBits are NOT
recorded here.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
