---
id: KN-TECH-b18366
type: technique
title: Chained S_3 presentation of point decomposition (auxiliary-variable degree reduction)
tags: [semaev, summation-polynomial, chained-system, auxiliary-variables, weil-descent,
  characteristic-two, first-fall-degree, degree-of-regularity, point-decomposition,
  index-calculus, groebner]
confidence: established
complexity: >-
  Boolean system of n(t-1) equations in n(t-2)+kt variables of algebraic degree 3,
  first fall degree proved 4; replaces one equation of degree 2^{t-1} in kt
  variables. Solving cost is NOT established -- it depends on the degree of
  regularity, which is the contested quantity (KN-OPEN-d218ec)
applicability: >-
  any E/F_{q} where S_3 is available and a factor base is defined by a subspace or
  subset condition on x; stated and measured in the literature for q = 2^n with V
  an F_2-subspace of dimension k, and asserted extendable to F_{p^n} for fixed
  odd p
source_refs: [KN-LIT-fa346d, KN-LIT-327949, KN-LIT-001, KN-LIT-005, KN-TECH-002, KN-TECH-004]
added: 2026-09-13
superseded_by: null
---

## The presentation

Point decomposition asks, for a target `R` and factor base `{(x,y) in E : x in V}`,
for `x_1,...,x_t in V` with `R = sum (x_i, y_i)`. The classical test is one
summation-polynomial equation

    S_{t+1}(x_1, ..., x_t, R_X) = 0,

whose degree in each variable is `2^{t-1}`. The chained presentation instead
introduces `t-2` **auxiliary variables** `u_1,...,u_{t-2}` ranging over the whole
field and writes the same condition as a path of `S_3` constraints:

    S_3(u_1, x_1, x_2)         = 0
    S_3(u_i, u_{i+1}, x_{i+2}) = 0     for 1 <= i <= t-3
    S_3(u_{t-2}, x_t, R_X)     = 0

Each `u_i` is the `x`-coordinate of the running partial sum, so the chain is the
addition chain `((x_1 + x_2) + x_3) + ... ` made explicit in the equations
instead of being eliminated by resultants. The elimination is exactly what the
recurrence `S_m = Res_X(S_{m-r}, S_{r+2})` of `KN-TECH-002` performs, and it is
what drives the degree to `2^{t-1}`; keeping the intermediate nodes as variables
keeps every equation at the degree of `S_3`.

**The trade is degree for variables.** In characteristic 2 with
`Y^2 + XY = X^3 + AX^2 + B`, `S_3 = (x_1x_2 + x_1x_3 + x_2x_3)^2 + x_1x_2x_3 + B`,
so after Weil descent over `F_2` with `dim V = k` the chain at `t = m` becomes
`n(t-1)` Boolean equations of algebraic degree **3** in `n(t-2) + kt ~ (t-1)n`
variables, against one equation of degree `2^{t-1}` in `kt` variables.

## Why the degree drop is not automatically a cost drop

The first fall degree of the chained system is **4** and this is proved, not
assumed (`KN-LIT-fa346d` Section 4.5: `deg_{F_2} S_3 = 3` while
`deg_{F_2} x_1 S_3 = 3` as well, exhibiting a degree fall at 4). The step from
there to a cost bound requires `d_reg <= d_ff`, which is a separate assumption
(Semaev's Assumption 1, `d_F4 <= 4`) and is the contested part:

- `KN-LIT-7604` and `KN-LIT-7607` argue against `d_ff ~ d_reg` for summation
  systems in general.
- `KN-LIT-fa346d` itself reports that `d_reg > 4` once `k > ceil(n/m)`, while
  `d_ff` stays 4 — the paper exhibits the gap it assumes away.
- Unreproduced counter-data in the `KN-LIT-e77232` comment thread puts step
  degree 5 at `n = 45, m = t = 2` and at `n = 25, m = t = 3`.

So this technique's value is the *presentation*: it is a genuine, reproducible
reduction in algebraic degree and in measured solve time and memory (up to 50x
faster and 10x less memory than the unchained solve at the same parameters,
`KN-LIT-fa346d` Section 4.2, comparing against `KN-LIT-010`). Its asymptotic
consequence is conditional on a quantity nobody has measured outside a small
window.

## Correctness conditions, which are easy to lose

`KN-LIT-fa346d` Lemma 2 gives the equivalence with `S_{t+1}(...) = 0`, and it is
conditional:

1. **Lower chains must be unsatisfiable.** The equivalence holds *assuming*
   `S_{i+1}(x_1,...,x_i,R_X) = 0` has no solution in `V` for `2 <= i < t`. The
   algorithm as specified therefore tries `t = 2, 3, ..., m` and stops at the
   first satisfiable system; a cost model that charges one solve at `t = m` is
   not costing the algorithm as written.
2. **The order-2 channel.** If some `y_i` lie in `F_{q^2} \ F_q`, their partial
   sum is a point of order exactly 2, so the count of such indices is `0` or
   `>= 2`. `KN-LIT-fa346d` calls the result "a useful relation anyway", but such
   a relation carries the 2-torsion point as an extra unknown into the linear
   algebra, and the paper never accounts for what fraction of relations arrive
   this way.
3. **Auxiliary variables are unconstrained.** The `u_i` range over `F_q`, not
   `V`. Constraining them is a different system with a different solution set,
   not an optimisation.

## Independent variants

`KN-LIT-327949` (Karabina, ePrint 2015/319, frozen at
`inputs/KARABINA-PDP-2015/`) introduces auxiliary variables into the same problem
with a **different chain topology**, independently and contemporaneously; the
`KN-LIT-fa346d` acknowledgement records that Kosters, Karabina and
Petit-Takagi-Huang all had the splitting idea in unpublished form. Comparing the
two topologies at fixed `(n, m, t, k)` is a legitimate open measurement; the
`d_reg` question above is the same for both.

## In this repository

The Weil-descended Boolean form of this presentation at `m = 3` is the object
`GOAL-DREG-001` measures (`experiments/EXP-DREG-001/`, block-m4ri exact-rank
instrument, Macaulay degrees up to 6) and the object `KN-FIND-006`'s closed-form
`8*dim(V)` rank deficit is stated over. Implementation support is in
`harness/semaev.py` and `src/semaev_tree.py`. Whether the degree quantity those
records report is Semaev's `d_F4` is open: `KN-OPEN-d218ec`.
