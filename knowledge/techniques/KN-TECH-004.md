---
id: KN-TECH-004
type: technique
title: Groebner-basis solving and complexity indicators (F4/F5, degree of regularity, first-fall degree)
tags: [groebner, f4, f5, degree-of-regularity, first-fall-degree, solving-degree, complexity]
confidence: reported
complexity: worst-case doubly-exponential; practice governed by degree of regularity / first-fall degree
applicability: solving the polynomial systems from point decomposition
source_refs: [KN-LIT-005, KN-LIT-010]
added: 2026-07-19
superseded_by: null
---

## Method
Gröbner-basis algorithms (Buchberger; Faugere F4/F5) compute a canonical
generating set for a polynomial ideal, from which system solutions are read
off. For the dense/structured systems from summation-polynomial decomposition,
the practical cost is governed by the maximum degree reached during
computation.

## Complexity indicators (the metrics the program measures)
- **Solving degree / degree of regularity (d_reg):** the highest degree the
  algorithm works at; runtime is roughly polynomial in the number of monomials
  up to d_reg, so d_reg drives cost.
- **First-fall degree (d_ff):** the degree at which the first non-trivial
  degree fall (unexpected reduction) occurs; used as a heuristic proxy for
  d_reg in ECDLP systems (KN-LIT-005). Whether d_ff tracks d_reg is itself a
  research question over prime fields (KN-OPEN-002).

## Program usage
harness/semaev.py builds the decomposition system and records the achieved
solving degree and wall time; these are the primary metrics for EXP-SEMAEV
experiments. Note: sympy uses Buchberger/F5-style routines, not an optimized
F4 -- absolute timings are implementation-bound and must not be presented as
crypto-scale; only *trends vs. parameters* are interpreted.
