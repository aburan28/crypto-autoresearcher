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
restated_at: '2026-09-13'
restated_by: DEC-20260913-74e208
restatement: >-
  THE QUESTION AS ORIGINALLY POSED IS MALFORMED AND STAYS OPEN IN A SHARPER FORM.
  "What is the memory-charged crossover" presumes a number. It is a SURFACE over
  (cost metric x distinguished-point store size x processor count x
  operation-unit conversion kappa), and REVIEW-SEMBIN-20260913-9d649f showed the
  first published answer (COST-SEMBIN-8d123b: 375 sparse, 435 dense) was one
  undeclared slice of it at store_log2 = 30 and one processor. The crossover moves
  180 in n across the store parameter against 132 across the whole metric set, so
  a crossover quoted without its store is underdetermined in exactly the way that
  record says a crossover quoted without its metric would be. THE SHARPENED
  QUESTION: at which (metric, memory budget, baseline operating point) does the
  verdict at each FIPS label change, and which of those points is physically
  occupiable? EXP-SEMBIN-2c40bb computes that surface; H-SEMBIN-97ea23 is the
  hypothesis it tests.
what_the_first_attempt_established: >-
  Retained because it is progress even though the framing was wrong. (i) The paper
  states NO memory model anywhere, so both storage readings in circulation come
  from the recorded ellipticnews dispute rather than from Semaev's text
  (KN-LIT-e77232): width^2 is Galbraith's count, (nm)^4/24 x n^3/m is Semaev's own
  answer. (ii) The variable count N = n(t-2) + kt is exact and confirmed from two
  separate sections, giving 2790 / 4099 / 6286 at (310,10) / (409,11) / (571,12).
  (iii) The relation store is textually grounded at 2^ceil(n/m) rows of
  (mk + 2n) bits. (iv) Charging memory moves the crossover UP, and by MORE than
  the first attempt reported. (v) Semaev's cheapest memory at n = 409 is 2^65.33
  bits sparse at m = 8 -- four exabytes, above every storage system that exists --
  which is the fact that makes a fixed-budget metric decisive.
sharpened_by_findings:
  - >-
    THE BASELINE WAS CHARGED AT A DOMINATED OPERATING POINT: vOW's memory for a
    2^30-point store together with one processor's time, which are different points
    on one curve and sit 29.0 bits above the minimum of vOW's own T x Mem product
    (constant across n = 283 to 571). Charged at any single coherent point the
    crossover moves +85 in n, to 460 sparse and 520 dense, and n = 409 becomes a
    loss under BOTH storage readings.
  - >-
    UNDER ANY FIXED PHYSICAL MEMORY BUDGET THE TWO STORAGE READINGS AGREE. They
    differ only inside the band 2^65 to 2^89 bits; below 2^65 both say n = 409
    favours parallel rho. The band is what the first attempt mistook for a property
    of the algorithm.
  - >-
    THE SPARSE WORKING SET IS COMPUTED IN EXACTLY ONE IMPLEMENTATION IN THIS
    REPOSITORY, is corroborated at exactly one parameter point (n = 571) by the
    knowledge record it came from, and it is the term that moves the n = 409 verdict
    by about 20 bits. The blind re-derivation commissioned to check it could not,
    because the review plan misstated the formula (DEC-20260913-74e208 PD-1).
  - >-
    THE FROZEN SOURCE CARRIES 34 MAGMA MEMORY MEASUREMENTS of this exact object that
    no cost model in this program had been compared against. Under the peak reading
    of that column, measured peak lies between the two storage readings in 21 of 27
    non-trivial rows. Whether the column is a peak or a total over 100 systems is
    itself contradicted between two sources here and is NOT settled.
  - >-
    THE DENSE/SPARSE GAP WIDENS WITH THE PARAMETER: about 7 bits at N ~ 50 where the
    measurements are, 19 to 21 bits at N = 2790 to 6286 where the claims are. Any
    bracket quoted at cryptographic n is largely an extrapolation of a gap last
    observed at a seventieth of the scale.
  - >-
    CROSSOVERS HERE ARE CONVENTION-DEPENDENT UNDER A RULE THIS PROGRAM ALREADY WROTE
    DOWN. EXP-ICEX-c32447 requires field-to-group operation conversion at
    kappa in {1,10,100} and forbids quoting a kappa-sensitive conclusion without it.
    The crossover moves about 20 in n across that grid.
source_refs: [KN-LIT-fa346d, KN-LIT-e77232, KN-TECH-b18366, KN-OPEN-001, RQ-SEMBIN-fa2e3f,
  EV-SEMBIN-71e5cd, DEC-20260913-74e208, H-SEMBIN-97ea23, KN-TECH-006, KN-TECH-035,
  KN-TECH-036]
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

## Restated, 2026-09-13 — the question wanted a number and the answer is a surface

Recorded by `DEC-20260913-74e208`, composing `REVIEW-SEMBIN-20260913-9d649f`.
The body above is unchanged; this section is appended. **This problem stays open.**

`EXP-SEMBIN-f4a17b` / `COST-SEMBIN-8d123b` was the first attempt at the
*Resolution criterion* above, and its arithmetic is sound — three independent
implementations reproduce it to `4.8e-5` bits. What the review round broke is the
shape of the answer. The record reported a crossover per metric; the crossover is
a function of at least four parameters, and three of them appeared only as Python
keyword defaults.

**The sensitivity, side by side.** Sparse reading, product metric:

| varied parameter | range of the crossover, in `n` |
|---|---|
| cost metric (the parameter the record reported) | 72 |
| distinguished-point store, `store_log2 ∈ {30,40,48,60}` (declared by the contract, never swept) | 96 |
| distinguished-point store, `store_log2 ∈ {0,20,40,60}` | 183 |
| baseline charging mode (dominated point → own-curve minimum) | 85 |
| operation-unit conversion `kappa ∈ {1,10,100}` | 20 |

The parent contract had already named this failure mode in its own
`falsification_criterion` — "if the crossover depends more strongly on the vOW
store parameter than on the metric choice, the deliverable is a two-parameter
surface and the hypothesis's framing is wrong even where its direction is right"
— and the condition fired.

### The sharpened question

Not *what is the memory-charged crossover*, but:

> At which `(metric, memory budget, baseline operating point, kappa)` does the
> verdict at each FIPS label change, and **which of those points is physically
> occupiable**?

The second clause is what makes it answerable rather than a matter of taste. Two
anchors now exist for it: vOW's product is invariant along its own tradeoff curve
with a unique minimum anywhere `w ≈ M`, which fixes what "charged coherently"
means; and Semaev's cheapest memory at `n = 409` is `2^65.33` bits, which is above
every storage system that exists and so decides most budgets by feasibility rather
than by cost.

### What must NOT be said, added to the list above

- **Not** "the memory-charged crossover is 375" or "435". Both are cells of a
  surface at `store_log2 = 30`, one processor, `kappa = 1`, and neither may be
  quoted without all four labels.
- **Not** "the verdict at `n = 409` is decided by the storage reading." It is
  decided by the memory budget and by where the baseline is charged. At any fixed
  budget the two storage readings agree except inside one band above four
  exabytes.
- **Not** "the swing straddles zero between two defensible readings." Of eight
  charging configurations examined, only two straddle zero and one of them is the
  first attempt's own.
- **Not** "Semaev's memory model is wrong." He states none; both readings in
  circulation come from a blog exchange, and the accounting is right wherever it is
  checkable — `N` exact, the store textually grounded, max-versus-sum immaterial to
  0.0005 bits.
- **Still not** any statement about the security of B-409, K-409, B-571 or K-571,
  in either direction. Every figure is a heuristic estimate under Assumption 1,
  whose failure mode (+19.4 bits at degree 5 at `n = 409`) is **larger than every
  effect discussed on this page**.

### What would now resolve it

1. `EXP-SEMBIN-2c40bb` — the surface, with the baseline on its own curve, a second
   independent implementation of the sparse working set, the 34 frozen measurements
   used as a control, and the prime-field nearby-object control the first attempt
   substituted away from.
2. **Read van Oorschot–Wiener 1999.** `HEUR-VOW-CURVE` is load-bearing for the
   largest correction here (+85 in `n`) and rests on two internal records;
   `KN-LIT-012` records that its own full text was not re-read, and no agent in this
   program has opened the primary source.
3. **Settle whether the Tables 1–2 MB column is a peak or a total over 100
   systems.** It decides whether the only 34 measurements of this object
   discriminate between the storage readings or over-predict under all of them.
4. **Clear `IMP-SEMBIN-ENGINE`.** Until a degree can be measured, the largest term
   in every figure on this page is an unvalidated premise.
