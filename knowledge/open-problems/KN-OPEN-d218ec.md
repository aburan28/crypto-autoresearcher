---
id: KN-OPEN-d218ec
type: open_problem
title: >-
  Where in (n, m, t, k) does Semaev's Assumption 1 fail -- and is the d_F4 it
  bounds even the same quantity GOAL-DREG-001 has been measuring on the same
  system for months?
tags: [semaev, first-fall-degree, degree-of-regularity, solving-degree, chained-system,
  characteristic-two, weil-descent, groebner, f4, assumption-1, definitional-gap,
  reproduction, open, ecdlp]
confidence: reported
status: open
source_refs: [KN-LIT-fa346d, KN-LIT-e77232, KN-LIT-7604, KN-LIT-7607, KN-TECH-b18366,
  KN-TECH-004, KN-FIND-006, KN-FIND-0618ab, RQ-DREG-001, H-DREG-001, EV-DREG-008,
  RQ-SEMBIN-fa2e3f]
added: 2026-09-13
superseded_by: null
---

## Statement

`KN-LIT-fa346d` (Semaev, ePrint 2015/310, frozen at `inputs/SEMAEV-2015-310/`)
rests its `2^{1.6986 sqrt(n ln n)}` bound and its "four FIPS binary curves are
theoretically broken" conclusion on

> **Assumption 1.** Let `q = 2^n`, `2 <= m < n`, `k = ceil(n/m)`, and let `V` be a
> subspace of dimension `k` in `F_{2^n}`. Then `d_F4 <= 4` for a Boolean equation
> system equivalent to (5) for any `2 <= t <= m`.

Two things about it are open, and the second is prior to the first.

**(A) The boundary.** The assumption is supported by 2300 MAGMA systems, all
reporting `d_F4 = 4`, but confined to `n <= 21, m <= 6` plus one cell at
`n = 40, m = t = 2, k = 20`. The FIPS conclusion needs `n = 409, 571` at
`m = 11, 12, k = 38, 48`. Unreproduced counter-data in the `KN-LIT-e77232`
comment thread reports step degree **5** at `n = 45, m = t = 2` (126 GB) and at
`n = 25, m = t = 3` (unfinished at 111 GB). Taken with Semaev's own `d_F4 = 4` at
`n = 40, m = t = 2`, the `m = 2` boundary would lie between `n = 40` and
`n = 45` — a gap of five in `n`, on the diagonal `k = ceil(n/m)` where the
assumption is actually asserted. **Nobody has reproduced either side.**

The question is not "is Assumption 1 true" but **what surface in `(n, m, t, k)`
separates `d_F4 = 4` from `d_F4 >= 5`**, and whether the growing quantity is
`n`, the chain length `t`, the ratio `n/k`, or the slack `k - ceil(n/m)`. The
paper already reports one face of that surface: at the end of Section 4.5.1,
"the maximal degree(regularity degree) generally exceeds 4 when `k > ceil(n/m)`
though the first fall degree is still 4" — so the paper itself exhibits a regime
where `d_reg > d_ff`, which is precisely what Assumption 1 assumes away.

**(B) The definitional gap, which comes first.** `GOAL-DREG-001` has been
measuring a degree quantity on **this same Weil-descended chained Semaev `m = 3`
Boolean system** since 2026-07, with a block-m4ri exact-rank instrument
(`experiments/EXP-DREG-001/`), and reports work at Macaulay degrees `D = 5` and
`D = 6` with an admitted genuine rank deficit at `n = 12, D = 6`
(`EV-DREG-008`). Semaev's Assumption 1 says the F4 step degree never exceeds 4 on
that system. These are either in direct tension or they are **not measuring the
same thing**, and nothing in this repository establishes which:

- Semaev's `d_F4` (Section 4.4) is the maximal total degree of polynomials
  occurring **before F4 terminates**, read off MAGMA's per-step verbosity. He
  explicitly notes that steps at degree 5, 6, 7 do occur, carrying the message
  "No pairs to reduce" — i.e. **after** the basis is complete — and excludes them.
  A naive "highest degree seen" reading of the same run reports 7, not 4.
- `GOAL-DREG-001`'s quantity is a Macaulay-matrix rank statistic at a chosen
  degree `D`, compared against a support-matched semi-regular null; its `D` is a
  parameter of the instrument, not an output of a solver.

If those are different quantities, then this program's DREG measurements neither
support nor contradict Assumption 1, months of work are pointed at a different
question than the one the literature is arguing about, and the `d_ff ~ d_reg`
debate in `KN-LIT-7604` / `KN-LIT-7607` is partly definitional. Settling it is
cheap — it requires running both definitions against one instance family, not new
mathematics.

## Why it matters here

Assumption 1 is the single load-bearing input to a published claim that deployed
curves are broken. Every downstream number in this program that prices a
summation-polynomial decomposition inherits its status: `GOAL-SDEG-001`'s
`C_decomp(p,m)` cost model, `GOAL-ICEX-001`'s charged exponent, and any
comparison of index calculus against rho. `KN-FIND-0618ab` already voided one
constant-degree cost model in this program by measuring
`D_0(s) = 4 + floor(s/2)`; Assumption 1 is the same shape of claim at a scale
nobody has probed.

## Resolution criterion

1. **Reconcile the definitions** on one instance family: instrument both
   Semaev's `d_F4` (last step degree strictly before termination, excluding
   "no pairs to reduce" tail steps) and the DREG `d_reg`/`D` statistic on
   identical systems, and report the map between them, including whether the
   tail-step exclusion is what accounts for any gap. Assigned to
   `EXP-SEMBIN-c2c312`.
2. **Reproduce the published cells** before extending them: Tables 1-2 of
   `KN-LIT-fa346d` are fully specified (`n`, `m`, `t`, `k`, `B = 1` or random,
   `V` = polynomials of degree `< k`, 100 random `z`), transcribed row-wise in
   `inputs/SEMAEV-2015-310/tables.yaml`, and the cheapest cells cost
   milliseconds. A reproduction that recovers `d_F4 = 4` where the paper reports
   it is the control that makes any later disagreement mean something.
3. **Locate the boundary**, with the `m = 2` window `n in [40, 45]` first
   because it is the narrowest and the cheapest. Assigned to `EXP-SEMBIN-7e1371`.
4. **Prefer certificates to completion.** Kosters' cells are unaffordable here
   (111-126 GB against roughly 8-16 GB usable) *if* the criterion is completing a
   Gröbner basis. Whether entering a degree-5 step can instead be *certified* --
   e.g. by showing the degree-4 Macaulay system does not determine the solution
   set -- is itself part of the open problem, and this program already owns the
   exact-rank instrument that would do it.

## What must NOT be said in the meantime

- **Not** "Assumption 1 is false." Two blog-comment data points, unreproduced,
  are a pointer. Their status is `recalled`-equivalent until an agent in this
  program measures them.
- **Not** "Assumption 1 holds up to n = 40." That is one cell of one table
  produced by an unpublished implementation on a machine nobody else has run.
- **Not** "GOAL-DREG-001 contradicts Semaev." That presumes (B) is settled in the
  direction of the two quantities being the same, which is exactly what is open.
- **Not** "the FIPS curves are safe" or "at risk" on the basis of any of this. A
  failure of Assumption 1 leaves Assumption 2 (`d_F4 = o(sqrt(n/ln n))`)
  untouched, and under Assumption 2 the asymptotic bound survives while the
  Table 3 concrete estimates — and only they — do not. The two must not be
  refuted as one.
- **Supportable instead**: the assumption's measured support is confined to
  `n <= 21, m <= 6` plus `n = 40, m = 2`, on the diagonal `k = ceil(n/m)`, from a
  single unpublished implementation; and the paper reports `d_reg > 4 = d_ff`
  off that diagonal.

## Related open surface

- `KN-OPEN-002` (growth of solving degree for **prime-field** summation systems)
  is the odd-characteristic sibling and is not touched by anything here.
- `KN-OPEN-94f456` is coupled to this one: whether the chain-length trade-off is
  exponent-relevant depends on whether `d_F4` grows with `t`, which is one axis
  of the surface in (A).
- `KN-FIND-006`'s `8*dim(V)` deficit law is stated over this same system at
  `t = 3` and is a candidate *explanation* of a `d_reg > d_ff` gap rather than a
  competitor to it; the two have never been compared.
