---
id: KN-TECH-043
type: technique
title: The lattice sieving family and modern sieve kernels
tags: [sieving, aks, gausssieve, listsieve, bdgl, lsh, g6k, dimensions-for-free, kissing-number, svp, records, lattice, baseline]
confidence: reported
complexity: heuristic 2^(0.292n+o(n)) time and comparable space for LSH sieving; provable variants are worse (List Sieve 2^(3.199n)); Gauss Sieve has no proven time bound
applicability: exact and approximate SVP in high dimension, and as the BKZ oracle above the enumeration crossover; requires exponential memory
source_refs: [KN-LIT-103, KN-LIT-104, KN-LIT-048, KN-LIT-105, KN-LIT-106, KN-LIT-081, KN-TECH-042]
added: 2026-07-24
superseded_by: null
---

## Method
Sieving keeps a large list of lattice vectors and repeatedly replaces pairs by
their differences, driving the list toward short vectors. The family's history is
a sequence of distinct algorithmic and engineering steps, and conflating them
causes cost-model errors:

1. **AKS** -- the original `2^O(n)` randomised algorithm, provable but believed
   impractical (hidden constant estimated at 30 or more).
2. **Nguyen-Vidick** (KN-LIT-103) -- first implementation, heuristic variant at
   `(4/3+eps)^n` operations, shortest vectors to dimension 50, and honestly
   slower than enumeration there.
3. **List Sieve / Gauss Sieve** (KN-LIT-104) -- List Sieve provable at
   `2^(3.199n)` time and `2^(1.325n)` space; Gauss Sieve practical, space
   provably `O~(tau_n)` in the kissing constant, and with **no known upper bound
   on its running time**.
4. **LSH sieving / BDGL** (KN-LIT-048) -- near-neighbour search brings the
   heuristic exponent to `2^(0.292n)`, the number quoted in every security
   estimate.
5. **Dimensions for free** (KN-LIT-105) -- solve dimension `n` with sieves in
   dimension `n - Theta(n/log n)`; sub-exponential saving, factor-10 practical
   speedup at dimension 70-80.
6. **G6K** (KN-LIT-106) -- a stateful machine rather than an oracle, with vector
   recycling, on-the-fly lifting and flexible insertion; the source of the
   current public records.

## What to carry into a cost claim
The deployed algorithm and the provable algorithm are different objects. Every
number used in practice -- `2^(0.292n)`, `2^(0.265n)` quantum, Gauss Sieve's
runtime -- is heuristic; the provable bounds are exponentially worse and nobody
quotes them. The kissing-number bound `tau_n > 2^(0.2075n)` is the closest thing
to a robust floor, because a sieve must store its near-neighbours whatever the
algorithm (KN-LIT-104, used as the "best plausible" bound in KN-LIT-107). The
reduction-probability modelling that turns these into estimates is itself an
active research question (KN-LIT-081).

## Applicability limits
Sieving's memory is exponential and is not an implementation detail; see
KN-TECH-044 before quoting a sieving cost as if memory were free. Below the
enumeration crossover (dimension 70, KN-TECH-042) sieving is simply the wrong
tool. Reported speedups are measurements on specific hardware with heavy
engineering, so a paper exponent understates the gap between an idea and a
running sieve -- which is precisely why the published records (KN-TECH-049)
rather than the exponents are the right calibration instrument.

## Verified vs reported
The staged history and its complexity figures are read from the abstracts of
KN-LIT-103, KN-LIT-104, KN-LIT-105 and KN-LIT-106, plus the existing KN-LIT-048
entry for BDGL. The `2^(3.199n)` and kissing-constant bounds are KN-LIT-104's
proven results; the `2^(0.292n)` exponent and Gauss Sieve's observed runtime are
heuristic and experimental respectively. Nothing here has been implemented or
measured by this program.
