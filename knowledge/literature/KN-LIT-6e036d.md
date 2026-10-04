---
id: KN-LIT-6e036d
type: literature
title: "WDSat (source release): a statically-allocated DPLL solver for Weil-descent PDP instances, with XORSET/XORGAUSS modules and static branching order"
authors:
  - "Monika Trimoska"
  - "Sorina Ionica"
  - "Gilles Dequen"
year: 2024
venue: "GitHub repository mtrimoska/WDSat (GPL-3.0 C source; solver of arXiv:2001.11229, CP 2020)"
identifiers:
  eprint: null
  doi: null
  arxiv: "arxiv:2001.11229"
  url: "https://github.com/mtrimoska/WDSat"
  git_commit: "61c6ff3f49445af2729274819edb27b85a89efc1"
tags: [sat-solver, wdsat, dpll, xor-reasoning, gaussian-elimination, anf, cnf-xor, point-decomposition, weil-descent, index-calculus, binary-curves, software, static-allocation, branching-order]
confidence: retrieved
citation_verified: read
provenance: retrieved
verified_by: coordinator (top-level session, 2026-09-13; cloned, README and main/wdsat.c read, built, run on six instances)
frozen_at: inputs/TRIMOSKA-WDSAT-2024/ (SRC-ICPERF-TRIMOSKA-WDSAT-2024)
added: "2026-09-13"
superseded_by: null
related:
  - KN-LIT-102cdb
  - KN-LIT-036049
  - SRC-SATIC-TRIMOSKA-2019
---

> **Provenance.** Cloned and built on 2026-09-13; source vendored with a hash manifest.
> This note records what the *code* does and how it is driven. The performance claims
> of the paper remain frozen as reported-not-reproduced in `SRC-SATIC-TRIMOSKA-2019`.

## What the code is

A single-threaded C solver (no dependencies beyond libc) implementing DPLL over three
constraint stores — CNF clauses, XOR clauses (XORSET), and an optional Gaussian
elimination module (XORGAUSS; `-x`, with an "XG-extended" variant enabled at compile
time by `__XG_ENHANCED__` that requires ANF input). Input is CNF, CNF-XOR, or ANF in
the repository's own dialect (`x .d l1 ... ld ... T 0`). A static branching order is
supplied with `-g v1,v2,...`; this is how the paper's *ml core variable* order
(Proposition 1 of `KN-LIT-102cdb`) is applied. `__FIND_ALL_SOLUTIONS__` switches from
first-solution to all-solutions mode.

**Everything is statically allocated.** `src/config.h` fixes `__MAX_ANF_ID__`,
`__MAX_DEGREE__`, `__MAX_ID__`, `__MAX_BUFFER_SIZE__`, `__MAX_EQ__`, `__MAX_EQ_SIZE__`,
`__MAX_XEQ__`, `__MAX_XEQ_SIZE__`; the shipped block is "IC-S4: l=6"
(`MAX_ANF_ID 52, MAX_ID 767, MAX_XEQ 52`). The README states performance depends on
`__MAX_ID__` being *exact*, and the binary prints the correct value when it is not
(observed here: "Set the `__MAX_ID__` constant to 502" on the n15l5 cell). Consequence
for any benchmark: **rebuild per cell** and record the constants; a mis-sized build is
a confound, and a cell above l = 6 needs new constants before it can run at all. This
is also the concrete mechanism behind the paper's "≈17 MB flat memory" claim (C5):
memory is fixed at compile time, so it cannot grow with the instance — which equally
means it cannot be compared to a dynamically-allocating engine's peak without saying so.

## Output format (read from `src/wdsat.c`, undocumented in the README)

- SAT: the assignment as a bit-string over the ANF variables, newline, then `conf[0]`.
- UNSAT: `UNSAT`, newline, then `conf[0]` (lines 535/539 at this commit).

`conf[0]` is the solver's conflict counter — the metric `RQ-SATIC-1ae57a` designates as
primary (hardware-independent) alongside wall time as secondary.

## How it bears on the program

- It is the *named competitor* to the Gröbner PDP step throughout the SATIC and
  ICPERF questions, and it is now runnable in-repo on the authors' own instances
  (`KN-LIT-036049`).
- The `-g` flag isolates the paper's central mechanistic claim — that the branching
  order on the ml core variables, not XOR reasoning per se, carries the speed-up (C2
  of `SRC-SATIC-TRIMOSKA-2019`) — so that claim is testable by running the same binary
  with and without the order, and by giving the same order to a generic solver.
- The paper's negative result on Gaussian elimination (C3) is testable with `-x`.

## Limits

- The bit-string ordering of the SAT output relative to the ANF variable ids is
  inferred from one instance (it began with the certificate `000010 001011 010010` of
  `INFOn19l6-1-S`); the experiment verifies every returned assignment against the curve
  rather than trusting this reading.
- No timing here is a reproduction of any published number; hardware, compiler and
  the `__MAX_ID__` sizing all differ from the authors' setup.
