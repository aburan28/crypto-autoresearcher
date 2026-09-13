---
id: KN-OPEN-94f456
type: open_problem
title: >-
  Is the chain length t a free cost parameter? Semaev declines the t < m trade-off
  as asymptotically irrelevant, but that argument uses Assumption 1 -- and becomes
  exponent-relevant exactly where the assumption fails
tags: [semaev, chained-system, chain-length, relation-collection, yield, trade-off,
  characteristic-two, first-fall-degree, degree-of-regularity, asymptotic-complexity,
  author-declined-lead, open, ecdlp]
confidence: reported
status: closed_scoped
closed_scoped_at: '2026-09-13'
closed_scoped_by: DEC-20260913-74e208
closed_scoped_as: >-
  CLOSED AS AN OPTIMIZATION QUESTION UNDER eq. (11) ONLY. There is no interior
  optimum in t at any integer n in [250,600] under any of the three solving-cost
  readings drawn from the frozen text: shortening the chain costs k - log2(t) bits
  of yield per link (measured 27.68 to 44.00 bits at the FIPS labels at the
  cost-optimal m) while every available solving-cost saving has DECREASING
  per-link increments and so grows only like log(m-t). Semaev's t = m is optimal
  under his own cost model at concrete cryptographic n, not merely asymptotically
  indifferent, so the trade-off he declined would not have paid. Obstruction,
  measurement and scope: KN-FIND-9643e7 and EV-SEMBIN-1d36a3. The hypothesis that
  proposed the interior optimum, H-SEMBIN-b1708c, is rejected in scope.
still_open_in:
  - >-
    UNDER ANY YIELD LAW OTHER THAN eq. (11). The whole closure consumes eq. (11)
    as published and unmeasured, so it is conditional on it throughout.
  - >-
    THE INVERTING CONFOUND IS UNMEASURED. If realized yield falls short of
    eq. (11) MORE at t = m than at t < m, the comparison flips and this closure
    with it. EXP-SEMBIN-354a75 exists to measure exactly that by exhaustive
    enumeration, and until it returns this closure is conditional on an unmeasured
    premise.
  - >-
    THE ASSUMPTION-1 COUPLING THAT THIS RECORD WAS OPENED FOR IS UNTOUCHED. The
    original question was two-sided: the trade-off becomes exponent-relevant
    exactly where Assumption 1 fails, and no degree was measured by anyone in the
    round that closed the optimization side. KN-OPEN-d218ec remains the
    prerequisite and remains open; IMP-SEMBIN-ENGINE records why it could not be
    addressed.
source_refs: [KN-LIT-fa346d, KN-LIT-e77232, KN-TECH-b18366, KN-OPEN-d218ec, KN-FIND-007,
  RQ-SEMBIN-ade131, KN-FIND-9643e7, EV-SEMBIN-1d36a3, DEC-20260913-74e208]
added: 2026-09-13
superseded_by: null
---

## Statement

`KN-LIT-fa346d` (Semaev, ePrint 2015/310) Section 3, step 3, identifies a
trade-off and declines it, in the author's own words:

> "The experiments in characteristic 2 presented below demonstrate that for
> `t < m` the solving running time with a Gröbner basis algorithm drops
> dramatically and the probability of solving is relatively lower. So it may be
> more efficient to solve a lot of the systems with `t < m` for different `R`
> instead of one system for `t = m` with one `R`. One can probably win in
> efficiency and lose in probability. Though the trade off may be positive, we
> won't pursue this approach in the present work as this does not affect the
> asymptotical running time estimates."

His Table 2 quantifies it. Reading expected time per relation as
`avg_seconds / exp_prob`:

| cell | `t = m` | shorter `t` | ratio favouring short chain |
|---|---|---|---|
| `n=21, m=3, k=7` | `133.54 / 0.12` | `t=2`: `0.0095 / 0.01` | ~`10^3` |
| `n=19, m=3, k=7` | `137.32 / 0.47` | `t=2`: `0.0092 / 0.01` | ~`10^2`-`10^3` |
| `n=16, m=4, k=4` | `160.87 / 0.04` | `t=3`: `0.4984 / 0.01` | ~`10^2` |
| `n=15, m=4, k=4` | `102.85 / 0.06` | `t=3`: `0.4765 / 0.02` | ~`10^1`-`10^2` |

**Caveat that must be carried with those numbers**: the `0.01` and `0.00`
probability cells are 1 and 0 successes out of 100 draws, so their relative error
is of order 100% and a `0.00` cell is consistent with any true rate below about
`0.03`. The table shows a direction, not a factor.

## The two-sided question

**The asymptotic side, where Semaev is very likely right.** Hold the factor base
at `dim V = k`. The Section 4.3 yield is `P ~ 2^{tk-n}/t!`, so shortening the
chain by one costs a factor `2^k = 2^{n/m}` in yield, which is *exponential*.
Under Assumption 1 (`d_F4 <= 4`) the solve cost is `poly(n)` for every `t`, so the
saving is at most polynomial. Exponential loss against polynomial gain: `t = m` is
optimal and the trade-off cannot move the exponent. His dismissal is sound **on
its own premise**.

**The coupled side, which is open.** That argument *uses Assumption 1*. If `d_F4`
grows with the chain length `t` — and the chained system's size grows linearly in
`t`, and the unreproduced Kosters data in `KN-LIT-e77232` reports step degree 5 at
`n = 25, m = t = 3` while Semaev reports 4 at `n = 40, m = t = 2` — then solve
cost is `n^{omega d_F4(t)}`, superpolynomial in the relevant regime, and the two
exponentials compete. The optimum over `t` then becomes a real optimization whose
solution can move the constant `c ~ 1.6986`, and possibly the shape of the bound.

So the object of interest is not the trade-off and not the assumption but **their
coupling**: `KN-OPEN-d218ec` asks where `d_F4` leaves 4, and the answer's
dependence *on `t` specifically* is what decides whether this trade-off is a
practical constant or an exponent question. Neither has been measured.

## Two further accounting questions in the same neighbourhood

1. **`t = m` versus the union over `t`.** The algorithm as specified in Section 3
   step 3 tries `t = 2, 3, ..., m` and stops at the first satisfiable system, and
   Lemma 2's equivalence *requires* the lower-`t` systems to be unsatisfiable. But
   the cost model in eqs. (15)-(17) charges one solve at `t = m` and one yield
   `P(n,m,m,k)`. What the algorithm as literally written costs, and whether its
   yield is the union over `t` or the single-`t` probability, are different
   questions from the trade-off above and are not answered in the paper.
2. **The direction of the Section 4.3 approximation.** The paper argues
   `P(solve one of the first t-1 systems) >= P(n,m,t,k) >= P(solve eq. 5)` and
   then assumes `P(solve eq. 5) ~ P(n,m,t,k)`. An **upper** bound on success
   probability placed in the **denominator** of relation-collection cost yields a
   *lower* bound on cost, not an estimate of it. The size of that gap propagates
   directly into Table 3 and the `n > 310` threshold.

## Resolution criterion

- Measure `d_F4(t)` at fixed `(n, k)` with `t` as the only varying parameter --
  the paper's Table 2 has the cells to anchor against (`n=15, m=5, t=2..5, k=3`
  and `n=15,16, m=4, t=2..4, k=4`) and they are cheap. A `d_F4` that is flat in
  `t` settles this in Semaev's favour; one that grows in `t` makes the trade-off
  an exponent question and reopens the optimal-`m` balance.
- Derive the joint optimum over `(t, k)` symbolically under a *parameterized*
  `d_F4(t, k)` rather than under a constant, and report which regions of that
  parameter space change the exponent as against the constant.
- Cost the algorithm as literally specified (union over `t`, with Lemma 2's
  unsatisfiability condition) against the single-`t` cost model, and report the
  ratio at the paper's own Table 3 parameters.

Assigned to `RQ-SEMBIN-ade131` and `GOAL-SEMBIN-cbf422`.

## What must NOT be said in the meantime

- **Not** "the short-chain trade-off improves the exponent." Under Assumption 1
  it demonstrably does not, and Assumption 1 has not been refuted.
- **Not** "Table 2 shows a `10^3` speedup." It shows a ratio computed from a
  one-success-in-100 cell. The direction is real; the factor is not measured.
- **Not** "Semaev overlooked this." He states it explicitly and gives a correct
  reason under his own assumption. The open content is the coupling, not an
  oversight.
- **Supportable instead**: the trade-off's asymptotic irrelevance is conditional
  on the same assumption as the paper's headline bound, so the two cannot be
  evaluated independently; and its practical size at `n <= 21` is unmeasured
  beyond one table's worth of low-count cells.

## Related open surface

- `KN-FIND-007` (decomposition-yield conservation: mean decomposition count is
  exactly `binom(B+m-1,m)/N`) bounds what any *factor-base* change can buy at
  fixed `|FB|`. It does not bound what a *chain-length* change buys, because
  varying `t` changes the number of summands rather than the factor base — but any
  proposal in this area must state which of the two it is varying, or it will be
  claiming against a settled conservation law without noticing.
- `KN-OPEN-d218ec` is the prerequisite; this problem is not independently
  resolvable.

## Scoped closure, 2026-09-13

Recorded by `DEC-20260913-74e208`, composing `REVIEW-SEMBIN-20260913-9d649f`.
The body above is unchanged; this section is appended.

**What closed.** The optimization side, and only under eq. (11). `EXP-SEMBIN-81dc96`
re-solved Semaev's two-stage balance jointly over `(m, t)` instead of over `m` at
`t = m`. There is no interior optimum: `t* = m*` at every integer `n` in
[250, 600] under all three solving-cost readings, reproduced by two implementations
sharing no code. The measured obstruction is in `KN-FIND-9643e7`; the composed
evidence is `EV-SEMBIN-1d36a3`.

**The question above was two-sided, and only one side is answered.** The record
asked whether `t` is a free cost parameter *and* whether the trade-off becomes
exponent-relevant where Assumption 1 fails. The first is answered no. The second
is untouched: no degree was measured in the round that closed the first, because no
Gröbner engine exists on the host (`IMP-SEMBIN-ENGINE`). `KN-OPEN-d218ec` stays the
prerequisite and stays open, so the "not independently resolvable" note in *Related
open surface* above still stands for the assumption-coupling half.

**What must NOT be said, added to the list above.**

- **Not** "the short-chain lane is dead." It is closed as an optimization under one
  yield law, with the inverting measurement outstanding.
- **Not** "coset-typed factor bases will reopen it." They close it *harder*:
  removing the `t!` symmetry factor raises the per-link charge from `k - log2(t)`
  to `k`, from 33.72 to 37.18 bits at `n = 409, m = 11`. See the resource reading in
  `KN-FIND-9643e7`.
- **Not** "Semaev was right for the reason he gave." He declined the trade-off
  because it does not affect the asymptotics, which is correct and is a different
  statement from what is now measured — that it does not pay at concrete `n`
  either. The concrete claim is the new content.
