---
id: KN-LIT-6565a8
type: literature
title: "Complete and improved FPGA implementation of Classic McEliece"
authors:
  - "Po-Jen Chen"
  - "Tung Chou"
  - "Sanjay Deshpande"
  - "Norman Lahr"
  - "Ruben Niederhagen"
  - "Jakub Szefer"
  - "Wen Wang"
year: 2022
venue: "CHES"
identifiers:
  eprint: "iacr:2022/412"
  doi: "10.46586/tches.v2022.i3.71-113"
  arxiv: null
  url: "https://doi.org/10.46586/tches.v2022.i3.71-113"
tags: [classic-mceliece, code-based, implementation, hardware, fpga, complete-implementation, reference]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
A **complete and improved FPGA implementation** of Classic McEliece — complete
in covering the whole scheme (key generation, encapsulation, decapsulation)
rather than one operation, by a team including the specification's own authors.

## Key claims (as reported)
- A full FPGA implementation of all Classic McEliece operations.
- Improves on prior partial FPGA work.

## Relevance to this program
The reference FPGA implementation, and the natural target for the hardware
side-channel attacks in section 4 — which is exactly why completeness matters:
**a partial implementation cannot be attacked or evaluated as a system.**

The parallel obligation here is that this program's experiment contracts are
frozen and complete before execution, so that what was run is unambiguous and
independently checkable.

**Does not bear on the ECDLP.**

## Not verified here
Citation verified against the IACR ePrint record for report 2022/412 (title and author list checked) on 2026-08-03; citation verified against the Crossref record (DOI 10.46586/tches.v2022.i3.71-113).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

Resource usage and performance figures are NOT recorded here.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
