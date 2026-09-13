---
id: KN-OPEN-86e7e1
type: open_problem
title: >-
  Semaev 2015's asymptotic claim reports time only, and it is compared against an
  algorithm with negligible memory -- what is the memory-charged crossover
  against parallel rho with distinguished points?
tags: [semaev, characteristic-two, index-calculus, asymptotic-complexity, memory,
  time-memory-tradeoff, van-oorschot-wiener, pollard-rho, cost-honesty, fips-186-4,
  concrete-cost, open, ecdlp]
confidence: reported
status: open
source_refs: [KN-LIT-fa346d, KN-LIT-e77232, KN-TECH-b18366, KN-OPEN-001, RQ-SEMBIN-fa2e3f]
added: 2026-09-13
superseded_by: null
---

## Statement

`KN-LIT-fa346d` (Semaev, ePrint 2015/310) concludes that its method "starts
performing better than Pollard's for `n > 310`", and hence that four FIPS PUB
186-4 binary curves at `n = 409, 571` are theoretically broken. The comparison in
Table 3 has three columns of cost — `2^{n/2}` for rho, `m! 2^{n/m} n^{12}` for
relation collection, `2^{2n/m}` for linear algebra — and **all three are time**.
No memory figure appears in eqs. (15)-(17), in Table 3, or anywhere in the
asymptotic analysis. Per-experiment memory is reported in Tables 1-2 and then
does not propagate into the claim.

That omission is load-bearing rather than cosmetic, because the two algorithms
being compared sit at opposite ends of the memory axis:

- **Pollard rho** at `2^{n/2}` group operations needs negligible memory, and its
  parallel form (van Oorschot-Wiener, distinguished points) achieves linear
  speedup in the number of processors with small per-processor storage.
- **This method** must collect and store `Theta(2^k)` relations, `k = ceil(n/m)`,
  and the optimal `m` makes `k` grow with `n`: `2^{31}` relations at `n = 310`,
  `2^{38}` at `n = 409`, `2^{48}` at `n = 571`. Separately, each decomposition
  solves a Boolean system in `N = (m-2)n + km` variables at degree `<= 4`, whose
  Macaulay width is `2^{41.2}`, `2^{43.4}`, `2^{45.9}` monomials at those three
  parameter sets.

So the claim as stated compares a constant-memory algorithm against one whose
memory also grows exponentially in `sqrt(n ln n)`, and reports only the axis on
which the new method wins.

**Open: where is the crossover once memory is charged, and under what cost
metric does the `n = 409` / `n = 571` conclusion survive?**

## What is already known, and its status

`KN-LIT-e77232` records, from the ellipticnews comment thread of April-May 2015
and never reproduced since, that Galbraith put dense storage at `2^{91}` bits for
`n = 571, m = 12` against Semaev's sparse estimate of `2^{70}` bits, with the
scale markers "Avogadro ~ `2^{79}`" and "2013 web ~ 4 zettabytes". Semaev's reply
in the same thread is that the method still beats Pollard at `n = 571, m = 12`
even with regularity degree up to 6 and linear-algebra constant 3.

The freezing session independently re-derived `2^{91.8}` bits from the paper's own
parameters (squaring the degree-`<=4` Macaulay width at `n = 571, m = 12`), which
recovers Galbraith's figure from the source rather than from the blog. That is a
derivation, not a measurement, and it settles nothing by itself: `2^{70}` sparse
and `2^{91}` dense are estimates of two different storage strategies, and neither
side of that exchange did the comparison against *parallel* rho.

## Why a memory figure is not by itself a refutation

Stating a large memory requirement does not refute a time claim, and this open
problem must not be read as though it did. Charging memory honestly means:

1. Choosing an explicit cost metric and saying so — plain time, time x memory,
   or a memory-bounded model where the machine has `M` words and the algorithm
   must fit.
2. Comparing against the right rho. The relevant baseline for a large-memory
   attack is not textbook rho but **van Oorschot-Wiener parallel rho with
   distinguished points**, including its own storage for distinguished points and
   its linear-speedup regime.
3. Reporting the **time-memory tradeoff curve**, not one point: the method has a
   free parameter `m` (hence `k`), so it interpolates between a
   high-memory/low-time and a low-memory/high-time endpoint, and the honest
   output is that curve against rho's.
4. Flagging every optimistic assumption on both sides, per the
   `concrete_cost` schema in `templates/research-records.md` — a cost table
   without `optimistic_assumptions` is invalid in this program.

It is entirely possible that the conclusion survives. The point is that it has
never been checked, in the paper or since, and that this program's own
`GOAL-ICEX-001` exists precisely to compare a charged index-calculus exponent
against a matched rho baseline — so the instrument and the standard already exist
here.

## Resolution criterion

A `concrete_cost` record (`COST-*`) at the standardized parameter sets
`n = 233, 283, 409, 571` (the FIPS 186-4 binary curves) carrying, for each:

- time and memory exponents for the chained-`S_3` index calculus at the paper's
  own optimal `m`, and at the `m` that minimises a stated combined metric;
- time and memory for van Oorschot-Wiener parallel rho at the same `n`,
  including per-processor storage and the processor count assumed;
- the tradeoff curve in `m`, with the memory-bounded crossover at several
  machine sizes `M`;
- `optimistic_assumptions` on both sides, explicitly including whatever the
  sparse-storage estimate assumes about the relation matrix, and the
  `o(1)`/polylog cofactors hidden in `n^{4 omega}`;
- `affected_scope` and `safe_scope` statements.

Assigned to `EXP-SEMBIN-f4a17b`. This is pure computation from published
formulas: it needs no curve arithmetic, no Gröbner basis, and no new
mathematics, which is why it should not wait behind the Assumption 1 work.

## What must NOT be said in the meantime

- **Not** "the FIPS curves are safe because the attack needs too much memory."
  No memory-charged comparison has been done, and a large memory requirement is
  a cost, not an impossibility.
- **Not** "Semaev's claim is wrong." The time analysis is internally consistent
  (verified in `inputs/SEMAEV-2015-310/tables.yaml`); what is missing is a
  second axis, and adding it is a strengthening of the accounting, not a
  refutation of the arithmetic.
- **Not** any conflation of this with `KN-OPEN-d218ec`. Assumption 1 could hold
  perfectly and this question would be unchanged; the memory cost of stage 2 does
  not depend on the Gröbner step's degree at all.
- **Supportable instead**: the published claim is a time-only comparison against a
  negligible-memory baseline; stage 2 stores `Theta(2^{ceil(n/m)})` relations,
  which is `2^{38}` at `n = 409` and `2^{48}` at `n = 571` at the paper's own
  optimal `m`; and no memory-charged crossover has been computed by anyone.

## Related open surface

- `KN-OPEN-001` ("does index calculus beat Pollard rho for prime-field ECDLP?")
  is the prime-field sibling and has the same missing axis.
- `GOAL-ICEX-001`'s completion criterion is a charged exponent decision against a
  matched rho/BSGS control; this problem is the same question asked of a
  published characteristic-2 claim instead of of this program's own toy pipeline,
  and the two should share a cost convention rather than inventing two.
