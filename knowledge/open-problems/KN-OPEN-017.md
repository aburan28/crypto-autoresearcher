---
id: KN-OPEN-017
type: open_problem
title: Where does the enumeration/sieving crossover move once sieving memory is fully charged?
tags: [full-cost, memory, sieving, enumeration, crossover, cost-model, kissing-number, wiener, concrete-security, open, lattice, cross-domain]
confidence: reported
status: open
source_refs: [KN-TECH-044, KN-LIT-094, KN-LIT-104, KN-LIT-106, KN-LIT-122, KN-TECH-035, KN-TECH-042]
added: 2026-07-24
superseded_by: null
---

## Statement
Sieving overtakes enumeration for exact SVP at dimension 70 in the measured
G6K-versus-FPLLL comparison. That crossover is a **step-count** comparison
between an algorithm using `>= 2^(0.2075n)` memory and one using polynomial
space. Under Wiener-style full-cost accounting -- hardware quantity multiplied by
time occupied, which charges memory and the cost of reaching it -- **where does
the crossover move, and does the ranking of primal, dual and enumeration-based
attacks change at cryptographic dimensions?**

## Current state (as reported)
- The memory is structural, not incidental: Gauss Sieve's space is provably
  proportional to the kissing constant, bounded below by `2^(0.2075n)`
  (KN-LIT-104). No sieve of this shape escapes storing its near-neighbour list.
- Wiener (KN-LIT-094) proves the analogous accounting changes exponents rather
  than constants in the ECDLP setting: baby-step giant-step's `n^(1/2)` step
  count becomes `n^(2/3+o(1))` full cost.
- The lattice community charges memory partially and inconsistently. "Min-space"
  sieve variants are costed at a worse time exponent to buy space back;
  KN-LIT-122 costs quantum sieving at circuit level and finds the realisable
  speedup small; but the `2^(0.292b)` figure inside core-SVP (KN-TECH-040)
  charges nothing for memory or its access pattern.
- **No source in this corpus computes the crossover under full cost.** The
  question is stated here because KN-TECH-044 needed the answer and did not have
  it.

## Why it matters here
It is the one question that sits squarely in both of the program's focus areas
and can be attacked with an instrument the program already trusts. The ECDLP
side has an established full-cost discipline (KN-TECH-035) derived from a proven
result; the lattice side has a memory-hungry algorithm whose cost is quoted as
if memory were free. Applying the former to the latter is a self-contained
analytical task requiring no new mathematics and no large computation -- it is a
cost-model derivation plus a comparison against published measurements. It is
also decision-relevant: if the crossover moves substantially, then some fraction
of the concrete-security literature ranks its own attacks wrongly, and any
program claim built on those rankings inherits the error.

## What would close it
A full-cost model for sieving that prices the near-neighbour list and its access
pattern, instantiated at the dimensions where G6K and FPLLL have published
measurements, yielding a revised crossover dimension with stated assumptions
about the memory technology and wiring model. Two honest failure modes should be
anticipated: the correction may be a constant factor rather than an exponent
change at reachable dimensions, and the o(1) terms in Wiener's model may be too
loose to settle the comparison. Either outcome is a usable result.
