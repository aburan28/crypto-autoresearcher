---
id: KN-LIT-b175dc
type: literature
title: "Acceleration of McEliece cryptosystem with instruction set extension for RISC-V"
authors:
  - "Samuel Kennedy"
  - "Basel Halak"
year: 2025
venue: "CSR"
identifiers:
  eprint: null
  doi: "10.1109/csr64739.2025.11130090"
  arxiv: null
  url: "https://ieeexplore.ieee.org/abstract/document/11130090"
tags: [classic-mceliece, code-based, implementation, risc-v, instruction-set-extension, acceleration]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
Acceleration of the McEliece cryptosystem with **instruction set extension for
RISC-V** — adding custom instructions rather than optimising within the existing
ISA.

## Key claims (as reported)
- Custom RISC-V instruction set extensions accelerate McEliece.

## Relevance to this program
The most aggressive point on the optimisation spectrum this section covers:
software tuning, then vectorisation, then custom instructions, then FPGA, then
ASIC. Held as part of that spectrum, which is a useful reference when this
program reasons about the **cost of an attack given a determined adversary** —
the honest upper end of that reasoning is custom silicon, not a fast CPU.

**Does not bear on the ECDLP.**

## Not verified here
citation verified against the Crossref record (DOI 10.1109/csr64739.2025.11130090).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

Which instructions were added and the speedup obtained are NOT recorded here.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
