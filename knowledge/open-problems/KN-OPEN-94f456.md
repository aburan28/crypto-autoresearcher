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
status: open
source_refs: [KN-LIT-fa346d, KN-LIT-e77232, KN-TECH-b18366, KN-OPEN-d218ec, KN-FIND-007,
  RQ-SEMBIN-ade131]
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
