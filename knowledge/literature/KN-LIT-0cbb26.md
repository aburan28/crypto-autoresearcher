---
id: KN-LIT-0cbb26
type: literature
title: "Montgomery Multiplication on the Cell"
authors:
  - "Joppe W. Bos"
  - "Marcelo E. Kaihara"
year: 2012
venue: "preprint (EPFL)"
identifiers:
  doi: null
  arxiv: null
  url: null
tags: [montgomery, multiplication, cell, simd, implementation]
confidence: reported
citation_verified: read
added: "2026-08-07"
superseded_by: null
---

Works in progress report: Montgomery multiplication split across the 4 SIMD
lanes of the Cell Broadband Engine's Synergistic Processor Elements (SPEs),
representing the operand as four consecutive parts placed in the vector
element positions (4-SIMD organisation). Arithmetic operates in 4‑way SIMD
with carry handling research, reporting speedups over scalar implementations.

## Key claims (as reported)
- A representation of a bignum as four equal parts permits shared-limb
  Montgomery multiplication in 4-SIMD fashion.
- Implementation is up to 2.47x faster than an unrolled plain implementation
  on the Cell SPE.
- The technique is presented as targeted at the Cell SPE but applicable to
  any parallel 32-bit SIMD architecture.

## Relevance
- Implementation-side hardware arithmetic; a data point on parallel bignum
  multiplication useful for the program's cost-modelling of the arithmetic
  baseline. No ECDLP theory content.

## Not verified here
- The benchmark environment (speeds / firmware) was not reproduced; timings
  taken from the paper.