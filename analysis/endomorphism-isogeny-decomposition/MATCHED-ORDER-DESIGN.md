# Endomorphism-order variation × Semaev geometry: a matched-order redesign

**Status** design proposal, not an approved contract. No ledger IDs minted, no
hypothesis status changed. Lane: `RQ-ICINV-475b5e` (gating), `RQ-VOLC-f6253b`,
`RQ-JINV-8fc13a`, under `GOAL-ENDO-001`.

**Provenance of every number below.** Values marked *[committed]* are read from
records on `origin/main`. Values marked *[derived here]* were computed in this
session by a script calibrated against committed data (it reproduces the
campaign's own 138-curve enumeration for `p = 4001, t = 30` exactly). Nothing
here is an experimental result; no run has been executed against this design.

---

## 1. Why the obvious design cannot work

The proposed experiment is: take one ordinary prime-field isogeny class,
generate several thousand vertices, and regress solver-side quantities
(`d_reg`, `d_ff`, Macaulay rank, Betti tables, relation density) against
curve-side quantities (`f_E`, `disc End(E)`, `N(alpha_min)`, `|Aut(E)|`,
volcano depth).

Inside a single class those five regressors are not five variables. They are
one. `T4` *[committed, DECOMPOSITION.md §3]* fixes `t`, hence `D = t^2 - 4p`,
hence the fundamental discriminant `D_0` in `D = D_0 f^2`. Everything the design
regresses against is then a function of the single integer `f_E | f`:

| quantity | dependence on `f_E` |
|---|---|
| `disc End(E)` | `= D_0 * f_E^2` — determined |
| volcano depth at `ell` | `= v_ell(f_E)` — a digit of `f_E` |
| `N(alpha_min)` | `~ \|D_0\| f_E^2 / 4` — determined |
| `\|Aut(E)\|` | `= 2` unless `D_0 in {-3,-4}`, which `T4` fixes for the whole class |

At the campaign's own committed instance `p = 4001, t = 30`,
`D = -15104 = -59 * 16^2` *[committed]*, so `f_E` ranges over the five divisors
of 16 and the design matrix is *[derived here]*:

```
   f   disc End   v_2(f)   N(a_min)   |Aut|      curves at this level
   1        -59        0         15       2         3      <- crater
   2       -236        1         59       2         9
   4       -944        2        236       2        18
   8      -3776        3        944       2        36
  16     -15104        4       3776       2        72      <- floor
                                                  138  [committed: class size]
```

Four columns are strictly monotone in `f`; the fifth is constant. **The
effective sample size of the regression is 5, not 138**, and the only level
carrying the maximal order has `n = 3`. This is not a property of `p = 4001` —
`T4` makes it a property of every ordinary class.

The campaign's red team already measured the resulting per-level table on the
correct (rebuilt) volcano *[committed, `red_team_notes.md` §10]*:

```
 level    n   mean rate_m3      sd
     0    3        0.4800   0.0173
     1    9        0.4456   0.0430
     2   18        0.4489   0.0311
     3   36        0.4411   0.0382
     4   72        0.4519   0.0366
```

No monotone trend, and the design cannot detect below a ~9.8% excess at the
crater. That is the identifiability ceiling, not a result about curves.

## 2. Why `d_reg` in particular cannot move here

The harness builds, for the `m = 3` test
*[committed, `harness/semaev.py:92-121`]*:

```
ideal < S_3(x1, x2, x_R),  fV(x1),  fV(x2) >     where fV(x) = prod_{v in V} (x - v)
```

The two factor-base-membership polynomials are univariate of degree `|V|` and
already generate a zero-dimensional radical ideal of degree `|V|^2` in shape
position. The curve enters only through `S_3`, which is bidegree `(2,2)`. So the
solving degree is pinned by `|V|`, and curve-to-curve variation in `d_reg` is
structurally near-zero in this formulation — before any statistics.

This predicts, and explains, the campaign's own most puzzling committed pair
*[committed, `red_team_notes.md` §11]*: the `S_3` monomial support really does
drop `13 -> 9` for `j = 0` and `13 -> 10` for `j = 1728` (exact, hand-verified),
a 23–31% reduction in the algebraic object — and the Gröbner time moves by
`-0.44%` and `-0.67%`, with `gb_size` for `j = 1728` moving the *wrong way*
(`+3.41%`).

In inventor-protocol terms this is a **lossy projection**: the observation
collision is real and exact, and it does not survive projection onto the cost
functional, because the cost functional is dominated by `fV`, not by `S_3`.
Note also that `groebner_basis_max_degree` is annotated in the source as
`"proxy, NOT degree of regularity"` *[committed, `harness/semaev.py:85`]* — the
campaign has never measured `d_reg`, `d_ff`, a Macaulay rank, or a Betti table.

**Consequence for the proposal.** Of the two hoped-for signals,
`N(alpha_min) down => relation density up` is measurable with today's harness;
`v_ell(f_E) up => d_reg down` is not, and would not be even with unlimited
samples, until the system formulation changes (§4, E1).

## 3. The redesign: hold the group order fixed, sweep the discriminant

The confound that voided the earlier between-class results is `#E`
*[committed: `NULL-C` is a between-class mean detector with power 1.00 at a 0.9%
shift, `red_team_notes.md` §5]*. The fix makes it vanish identically rather than
being modelled.

Write `N = #E(F_p) = p + 1 - t`. Then

```
D = t^2 - 4p = (t-2)^2 - 4N
```

**Fix `N` and vary `t`** (keeping `p = N + t - 1` prime). Every class in the
resulting family has *exactly* the same group order `N`, while `D` — and hence
`D_0` and `f` — sweeps freely. The identity was verified on every admissible
trace of the families computed here *[derived here]*.

This is the crossed design the single-class experiment cannot be:

- **conductor axis** — within any one class, `f_E | f`, `D_0` fixed;
- **discriminant axis** — across the `f = 1` classes, `D_0` varies, conductor
  pinned at 1, `N` identical;
- **`|Aut|` axis** — see below;
- **nuisance** — `N` is identical by construction, so no `#E` covariate, no
  matching, and `NULL-C`'s known failure mode is out of scope by design.

### Recommended instance: `N = 19507` (prime) *[derived here]*

59 isogeny classes, ~2000 curves total — the requested "several thousand
vertices" — **all with `#E = 19507` exactly**:

- **51 classes at `f = 1`**, carrying **46 distinct** fundamental discriminants
  (five values are hit twice, by trace pairs `t` and `-t'` — a free internal
  replication check) spanning `|D_0| = 1299` to `78027`, i.e. nearly two orders
  of magnitude with the conductor pinned. This is the clean `N(alpha_min)` axis,
  since at `f = 1`, `N(alpha_min) ~ |D_0|/4`.
- **conductor arm** `f in {1, 3, 107}` for the volcano-depth axis.
- **a `j = 0` class**: `t = 211`, `p = 19717`, `D = -34347 = -3 * 107^2`.

That last class is the most valuable object in the design. It is a depth-1
`107`-volcano: **1 curve at the crater with `j = 0`** (`End = Z[zeta_3]`,
`|Aut| = 6`) **and 36 curves at the floor** with generic `j` and `|Aut| = 2`
*[derived here; class size 37, cross-checked against the analytic class-number
formula `h(-3*107^2) = 107*(1+1/107)/3 = 36`]*.

Because they lie in one isogeny class, `|Aut|` varies while `D_0`, `N`, `p` and
`t` are all identical. Across classes `|Aut| = 6` and `|D_0| = 3` are perfectly
confounded and can never be separated; **inside this class they separate
exactly.** `gcd(107, 19507) = 1` with `N` prime, so `T1` transport applies and
the ECDLP is carried between the two arms with the same `k`.

### Caveat carried forward

Isogeny-class sizes above are class numbers of orders. For `D_0 in {-3, -4}` the
Deuring correspondence weights `j = 0` and `j = 1728` by `1/3` and `1/2`; the
campaign already enumerates against the Hurwitz–Kronecker mass formula
*[committed, `what_survived_review`]* and that enumeration, not this note, is
the authority on the exact vertex count of the `t = 211` class.

## 4. Four experiments

Ordered so that each one's failure kills the next cheaply.

### E1 — exact symbolic Semaev geometry across a class *(no statistics at all)*

The deterministic core of the proposal, and the cheapest decisive test.
For every curve in a class, compute **exactly**: the `S_3` and `S_4` monomial
support; the singular locus and its dimension for the Semaev variety
`S_m = 0`; the Betti table and Castelnuovo–Mumford regularity of the ideal
generated by `S_m` **and its partials, without the `fV` membership polynomials**
(removing them is what makes `d_reg` a curve functional rather than a function
of `|V|`, per §2); and the degree/factorisation of the elimination polynomial.

These are functions of `(a, b)` alone — no sampling, no target draw, no null
object, no `p`-value. Either the invariant varies across the class or it does
not. Per `T3` *[committed]* both outcomes are decisive: constancy closes the
`d_reg` axis with a named obstruction; variation hands the campaign
`min_{E' ~ E} C(E')` as a target and promotes E2.

Run it first on the `p = 4001, t = 30` class (138 curves, already enumerated and
Hurwitz-certified) before spending anything on `N = 19507`.

### E2 — relation density on the matched-order family

Dependent variables: `decomposition_rate_m2/m3`, `liftable_density`,
`decomposition_efficiency`. Design: the `N = 19507` family, all 59 classes.
Two independent contrasts, reported separately and never pooled:

1. **between-class, `f = 1`**: rate vs `|D_0|` across 51 classes at identical `N`;
2. **within-class**: rate vs level, on the true volcano.

Mandatory, from committed failures:
- **Sample targets with `targets_B`** (`harness/exp_icinv_fullgroup.py:485`), not
  `targets_uniform`. `H-ICINV-6c7920` *[committed, status `specified`]* holds
  that the whole reported over-dispersion is an artifact of `targets_uniform`
  sampling a cyclic subgroup, split by `r = #{x : x^3+ax+b = 0}`. Any design
  reusing that sampler measures two different estimands on the two halves of
  every class.
- **Stratify on `r` anyway**, and report the strata.
- **Build the volcano by Vélu**, not by `two_torsion_x_count` — the committed
  "volcano level" resolved 2 of 5 levels *[committed, §10]*.
- **Sweep factor-base density**, do not run the saturated row. The
  over-dispersion decays from 2.04 to 0.93 as density falls *[committed, §4]*;
  the operating density for `m = 3` is `1/m! ~ 0.167`.

### E3 — the reachability gate

`T5` *[committed]* is binding: variance is worthless unless the minimiser is
reachable. If E1 or E2 finds a cost-minimising vertex, test whether "good" is
(i) common enough to hit by random walk, or (ii) decided by a **local** test
evaluable at each step. On the `j = 0` class this is sharp and cheap: the good
vertex, if it is the crater, is 1 of 37, and craters are locally detectable by
counting rational `107`-isogenies. Report the walk length distribution over
seeds, not a point estimate *[committed failure mode: N5]*.

### E4 — instrument control (blocking, per `C4`)

Every statistic in E2 needs both directions on this design: planted-signal
detection and matched-null rejection. `NULL-C` is disqualified for the
within-class contrast by its own committed characterisation. E1 needs no null,
which is the main reason to run it first.

## 5. What would count, and what would not

- A monotone `|D_0|` → relation-density trend across the 51 matched-`N`,
  `f = 1` classes, surviving the density sweep and reproducing at a second `N`,
  is the real form of `N(alpha_min) down => relation density up`. Note it is a
  **between-class** statement; within a single class it is not distinguishable
  from the conductor axis (§1).
- A Betti-table or singular-locus difference in E1 that tracks volcano level is
  the real form of `v_ell(f_E) up => d_reg down`, and is exact rather than
  statistical.
- A `j = 0` vs floor difference **inside** the `t = 211` class is the only clean
  `|Aut|` measurement available anywhere in this program.
- None of these is an attack. `H-ENDO-001` *[committed]* — every endomorphism
  acts as a scalar on the prime-order subgroup — is used as the admissibility
  filter, not retested, and any claimed advantage is stated against the
  automorphism-discounted rho baseline (`KN-TECH-018`), where a factor at or
  below `sqrt(6)` is baseline calibration. Claim tier: `toy`.

## 6. The decision this design does not make

`RQ-ICINV-475b5e` is **paused**, not failed. `EXP-ICINV-4d33aa` terminated
`INVALID` twice on its `SR3` baseline-reproduction gate — both times an
admissibility failure that, per the Coordinator's own independent check, bears
on neither `H-ICINV-6c7920` nor `EV-ENDO-10109d` *[committed,
`DEC-20260809-de11f9`]*. The committed head records the gate redesign as **a
user decision, not dispatched automatically**, with three named candidates.

This design does not resolve that. It sidesteps it for E1 (which has no
statistical gate) and inherits it for E2.
