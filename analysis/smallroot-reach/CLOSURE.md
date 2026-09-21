# The lattice-describable factor base is closed, by 0.048 in the exponent

**Status: analysis note, not an evidence record.** Nothing here transitions a
hypothesis, discharges a completion criterion, or claims a speedup.
`sota_delta`: zero. `dominated_by`: Pollard rho at exponent 1/2, unchanged.
Claim tier: **toy** — every number is a heuristic exponent, and the heuristic is
named and stated to be optimistic *toward the attack*.

Instrument: [`tools/smallroot_reach.py`](../../tools/smallroot_reach.py).
Tests: [`tests/test_smallroot_reach.py`](../../tests/test_smallroot_reach.py).
Proposal record: `ledger/proposals/IDEA-20260903-81a943.yaml`.
Closes (as a computation, subject to Coordinator review): the open family named
by `IDEA-20260808-486ae2`, with `IDEA-20260808-c31f1c`, `IDEA-20260808-2e14f7`
and `IDEA-20260808-e2315e` as siblings — all four `status: proposed`, none ever
executed, no `EXP-COPP-*` on disk, no evidence record citing them.

---

## 0. Why this is the question

Prime-field index calculus needs a factor base that is simultaneously **dense**
(random points decompose over it) and **structured** (the decomposition test is
cheap). Over `F_{q^n}` the subfield supplies both: `{x ∈ F_q}` is cut out by
*linear* conditions after Weil restriction, so the test is a fixed-degree
system. Over `F_p` there is no subfield, and the program has already closed the
algebraic substitute: a factor base cut out by a target-independent algebraic
locus of degree `d` yields `O(d)` usable points, so an algebraic factor base of
size `B` costs description degree `≥ B/3` and its membership polynomial is the
trivial `∏(x − v)` (`IDEA-20260801-021` / `IDEA-20260803-e2f5bd`).

That leaves exactly one family: **lattice-describable** sets — intervals,
arithmetic progressions, rank-`r` generalized APs — whose membership is an
*archimedean inequality*, not a polynomial identity. Its decomposition test is
therefore not a Gröbner computation at all but a multivariate **small-root**
problem, and its cost is governed by a quantity entirely independent of the
solving degree: the Coppersmith / Howgrave-Graham / Jochemsz–May **reach**.

This matters because the solving-degree obstruction does not apply here. The
companion result in `analysis/isogeny-dreg-search` measured the first-fall
degree pinned at `h + 2` by the factor-base size on all 551,304 members of a
certified `2^40` isogeny class. A lattice solver does not pay that cost. The
lattice-describable family is the one place where the prime-field wall was
never actually shown to hold.

`IDEA-20260808-486ae2` framed it correctly, stated the win condition, and
asserted the reach "is computable in closed form from the Newton polytope by
the Jochemsz–May extended strategy, **with zero compute**". The computation was
never run. This note runs it.

## 1. The two exponents

Fix a binary addition tree on `m` leaves. Window the leaves to `p^β`. Keep `w`
of the `m−2` non-root internal nodes as windowed unknowns (window `p^{γ_v}`) and
eliminate the rest by resultants; the root's value is the known `x_R`. Each
elimination fuses two equations into one, so the system has exactly `w + 1`
equations.

Reach convention (as in the proposal): the solver has reach `ε` when it returns
the roots whenever `∏(bounds) ≤ p^{ε·(#equations)}`. At `∏(bounds) =
p^{#equations}` the expected number of roots in the box reaches 1, so **`ε = 1`
is the information-theoretic ceiling** and `ε → 1` is the lattice-density-one
regime where lattice methods are known to fail.

**DEMAND.** From yield, relation count, linear algebra and the window cost:

```
(I)   relation collection : (m−1)β − Σ_v (1−γ_v) > 1/2
(II)  linear algebra      : 2β < 1/2
(III) solvability         : mβ + Σ_v γ_v ≤ ε·(w+1)
```

Eliminating `Σγ_v` between (I) and (III) gives `ε > (w + 1/2 + β)/(w+1)`, and
(I) forces `β > 1/(2(m−1))`. Hence

> **ε_required(m, w) = ( w + 1/2 + 1/(2(m−1)) ) / (w + 1)**

At `w = 0` this is exactly the proposal's `m/(2(m−1))` — reproduced, not
assumed (`test_eps_required_reduces_to_the_proposal_inequality_at_w_zero`). The
generalization to `w > 0` is new here, and it is **increasing in `w` toward 1**:
every kept window costs a factor `p^{γ−1}` of yield.

**SUPPLY.** The Jochemsz–May shift lattice, summed exactly over its monomials
and extrapolated `t → ∞` in `1/t`. The calculator is calibrated against a
theorem, not against itself: Coppersmith's univariate reach is exactly `1/d`,
and the machinery reproduces it to `10^{-4}` for every `d ∈ {1,2,3,4,5,8,16}`.
For a full box `[0,d]^n` it yields the closed form

> **ε_full-box = 2n / (d(n+1))**

which is also confirmed numerically. Note the shape: at fixed degree `d = 2`
this **rises toward 1 as `n` grows** — more variables with smaller bounds is
the configuration that helps lattices, which is why the family was worth
checking at all rather than dismissing.

## 2. The correction that decides it

A block spanning `l` inputs carries one summation polynomial `S_{l+1}` in
`n = l+1` unknowns of per-variable degree `2^{l−1}`.

The trap — and the error in this note's own first draft — is to index blocks by
*leaf* count. **A kept internal node's value is itself an input to its parent's
block.** The `w+1` blocks therefore consume `m` leaves *plus* `w` kept values,
`m + w` inputs in total, and the worst block takes

> **l = ⌈ (m + w) / (w + 1) ⌉**

Consequently `l = 2` — the all-`S_3`, degree-2, maximum-reach configuration —
requires `m + w ≤ 2(w+1)`, i.e. **`w ≥ m − 2`: only the full tree.** And the
full tree is precisely where the window cost is maximal. The two levers are
welded together.

## 3. The measured reaches

Computed on the *true* Newton polytopes, not on bounding boxes:

| block | polynomial | support | full box | measured ε (extended, `t→∞`) | sparsity gain |
| --- | --- | --- | --- | --- | --- |
| `l = 2` | `S_3` | **13** of 27 | 0.7500 | **0.8408** | ×1.12 |
| `l = 3` | `S_4` = `Res_Y(S_3,S_3)` | **439** of 625 | 0.4000 | **0.4137** | ×1.03 |

The `S_3` support of 13 is the same count measured on all 551,304 curves of the
`2^40` isogeny class. Sparsity is a **real** gain — it lifts `S_3` from 0.75 to
0.84, well past the basic-strategy value — but it decays fast: `S_4` is 70%
dense and buys almost nothing. Blocks with `l ≥ 4` are credited a **1.15×**
sparsity allowance, larger than anything measured and larger than the trend
allows, so the attack is over-credited by construction.

## 4. The decision

```
   m    w  blocks   l   n    deg   eps_req  eps_avail    margin  alive
   4    0       1   4   5      8    0.6667     0.2396   -0.4271  no
   4    1       2   3   4      4    0.8333     0.4137   -0.4196  no
   4    2       3   2   3      2    0.8889     0.8408   -0.0481  no   <-- best
   5    3       4   2   3      2    0.9062     0.8408   -0.0654  no
   6    4       5   2   3      2    0.9200     0.8408   -0.0792  no
   8    6       7   2   3      2    0.9388     0.8408   -0.0980  no
  16   14      15   2   3      2    0.9689     0.8408   -0.1281  no
```

**No configuration is alive.** The best margin over every `(m, w)` is
**−0.0481**, at `m = 4, w = 2` — the full binary tree on four leaves — and it
widens monotonically in every direction.

## 5. The obstruction, stated as a measurement

> **Statement.** For windowed (lattice-describable) prime-field factor bases,
> the small-root reach available to the decomposition test and the reach
> demanded by the index-calculus balance are *monotone in the same parameter*
> and never cross. Keeping an internal node cheap enough to solve (degree 2,
> reach 0.8408) forces the full tree, where the accumulated window cost demands
> reach ≥ 0.8889; releasing a window to recover yield forces a block of ≥ 3
> inputs, whose degree doubles and whose reach collapses to 0.4137 while the
> demand stays above 1/2.

| field | value |
| --- | --- |
| quantity | `ε_available − ε_required`, exponents base `p` |
| value | **−0.0481** at the optimum `(m,w) = (4,2)`; `≤ −0.0481` everywhere |
| supply ceiling | `ε(S_3, extended) = 0.8408` (`t→∞`, extrapolations 0.8407–0.8412) |
| demand floor at that ceiling | `ε_required(4, 2) = 8/9 = 0.8889` (exact rational) |
| scope | binary addition trees, `m ≤ 32`, any `w`, any window sizes, any rank-1 GAP factor base, `#eq = w+1`; heuristic JM reach assuming algebraic independence |
| claimed nowhere else | not a statement about non-tree decomposition strategies, rank-`r ≥ 2` GAPs, or non-Coppersmith lattice solvers |

**The direction of the error is toward the attack.** Every modelling choice
over-credits it: the JM bound assumes the recovered short vectors are
algebraically independent (real LLL frequently fails this, which *lowers* true
reach); blocks are split as evenly as possible; `l ≥ 4` gets an unearned 1.15×;
and the information ceiling `ε ≤ 1` is never invoked as a binding constraint.
A margin of −0.048 under those assumptions is a real gap, not a rounding error.

**`resource_check` — turning it over.** `examined: true`. The obstruction says
this family lives at lattice density → 1, the same regime where low-density
subset-sum attacks die. That is a *reusable* connection, not just a verdict:
it means the windowed-decomposition problem is a natural hard instance
generator in the density-1 regime, and it predicts that any future improvement
in density-1 lattice solving transfers directly here with a computable
threshold (`ε > ε_required(m,w)` from §1). It also says where NOT to look:
improving Gröbner solving degree cannot help this family at all, because the
family never pays that cost.

## 6. What stays open — this is not a closure of prime-field ECDLP

1. **Rank-`r ≥ 2` GAPs.** `IDEA-20260808-c31f1c`'s invariance lemma makes all
   rank-1 APs equivalent to intervals (affine substitution is polytope-neutral),
   so §4 covers them. Rank `r ≥ 2` splits one bounded variable into `r` smaller
   ones and **changes the polytope** — the one lever inside this family that
   this note does not compute. The `n/(n+1) → 1` shape of the full-box formula
   is exactly the direction that helps, so this is the live successor and it is
   cheap: it is the same calculator on a substituted support.
2. **Non-tree strategies.** The block model assumes decomposition follows a
   binary addition tree. A decomposition test that is not an elimination on a
   tree is outside scope.
3. **`ε(δ)` at superpolynomial lattice dimension** (`IDEA-20260808-e2315e`).
   This note computes the conventional `t → ∞` reach at polynomial dimension.
   Whether charging dimension as an exponent buys more than it costs is
   untouched here, and the margin to beat is now a number: 0.048.
4. **The heuristic itself.** `--probe` calibrates planted-root recovery against
   the univariate theorem; a full multivariate probe measuring whether real LLL
   attains the JM reach on `S_3` would tighten the supply side. It can only
   move it *down*, strengthening the closure.

## 7. Reproduction

```bash
python3 -m pytest -q tests/test_smallroot_reach.py
python3 tools/smallroot_reach.py --validate            # calibration vs Coppersmith 1/d
python3 tools/smallroot_reach.py --m 4,5,6,8,12,16,24,32
python3 tools/smallroot_reach.py --probe --probe-degree 3   # planted-root LLL
```
