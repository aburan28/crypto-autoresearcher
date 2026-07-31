# EXP-FB3-001 analytic arm — the decomposition-conservation identity

Pre-registered in `experiments/EXP-FB3-001/amendment-001.yaml`, change
`AMD-3-analytic-arm`, approved before execution. This file states and proves the
identity, then reports each of the four pre-registered consequences as
**CONFIRMED / CONTRADICTED / UNTESTED** against the measured cells, with the
numbers and their run references.

Run references: `runs/RUN-FB3-001-N14`, `runs/RUN-FB3-001-N16`,
`runs/RUN-FB3-001-N18` (measurements), `runs/RUN-FB3-001-CTRL` (controls),
`runs/RUN-FB3-001-FAMILY` (`analytic_arm` block, machine-generated).

This is a `derivation`-level argument in the sense of
`docs/claims-and-verification.md`: a self-contained elementary argument that an
independent reader can check line by line. It is not machine-checked, and it is
a statement about the frozen counting convention, not about ECDLP hardness.

---

## 1. The identity

Let `G` be a cyclic group of prime order `N`, written additively and identified
with `Z_N`. Let `D` be a factor base: a set of `B` distinct nonzero elements of
`G`. Fix `m >= 1`. For a target `r` in `G` define

```
c_D(r) = # { multisets {d_1, ..., d_m} of elements of D (repetition allowed)
             with d_1 + ... + d_m = r }.
```

**Claim.** `sum over r in G of c_D(r) = binomial(B + m - 1, m)`, exactly.

**Proof.** Let `M` be the set of size-`m` multisets of elements of `D`. By
stars-and-bars, `|M| = binomial(B + m - 1, m)`. Because `G` is abelian the map

```
sigma : M -> G,    sigma({d_1, ..., d_m}) = d_1 + ... + d_m
```

is well defined: the value does not depend on the order in which the multiset's
elements are listed. A map from `M` to `G` partitions `M` into its fibres
`sigma^{-1}(r)`, one for each `r` in `G`, and by definition
`c_D(r) = |sigma^{-1}(r)|`. Summing the fibre sizes recovers the domain:

```
sum_{r in G} c_D(r) = sum_{r in G} |sigma^{-1}(r)| = |M| = binomial(B+m-1, m).
```

QED.

The proof uses only that every multiset sums to exactly one target. It therefore
generalises verbatim: **for any finite family `M` of counted decomposition
patterns, `sum_r c(r) = |M|`.** The identity is structural; only the constant
`|M|` depends on the convention. This is what makes it a control (section 3) as
well as a baseline.

For the frozen convention of this experiment (`m = 3`, untyped multisets,
targets over the whole group) the constant is

```
sum_r c_D(r) = binomial(B + 2, 3) = B(B+1)(B+2)/6.
```

## 2. The four pre-registered consequences

### (i) The exact mean per-target yield is geometry-independent

Dividing the identity by `|G| = N`:

```
mean_r c_D(r) = binomial(B + m - 1, m) / N,
```

which depends on `B` and `N` only. Hence for **any** two bases `D`, `D'` of the
same size `B` in the same group, the exact mean-yield ratio is exactly `1`. A
nonzero deviation can only come from

* a size mismatch `|D| != |D'|`;
* averaging over a proper subset of `G` (a held-out half) or over a sample of
  targets rather than over all of `G`;
* a different counted family `M` (a different typing convention);
* an implementation error.

**Status: CONFIRMED.**

* 144 untyped whole-group cells (`high_bit_interval`, `small_height`,
  `coset_union`; 3 geometries x 3 sizes x 4 curves x 4 seeds). Maximum absolute
  deviation of the measured exact mean from `binomial(B+2,3)/N`: **0.0**
  (the counters are integer-exact, so this is an exact zero, not a small
  residual).
* Measured mean-yield ratio against the matched-random null: `1.000000` at every
  size for all three untyped geometries, with a zero-width bootstrap CI
  `[1.0, 1.0]` and permutation p-value `1.000` (the null is a point mass).
* Floating-point footnote, stated for completeness: 108 of those 144 cells have
  a *float* ratio differing from `1.0` by at most `4.44e-16` (2 ULP), because the
  null mean is formed by averaging 200 identical `float64` values before the
  division. The underlying integer totals are identical in all 144 cells.
* The closed-form total control passed **67 784 / 67 784** times across the three
  size runs, covering every structured, null, and exploratory cell.

The observed exact mean does fall with `N` — `1.1276 -> 1.0755 -> 1.0436` at
`2^14 / 2^16 / 2^18` — but that is the ceiling in `B = ceil((6N)^(1/3))`, not a
geometry effect: the same value is taken by every base of that size, structured
or random.

### (ii) The growth slope of the mean-yield ratio is identically zero

If matched-size bases have ratio exactly `1` at every `N`, then the slope of
that ratio against `log N` is exactly `0`, with no residual variance to
bootstrap.

**Status: CONFIRMED.**

| geometry | slope of mean-yield ratio vs log2 N | bootstrap CI95 |
|---|---|---|
| `high_bit_interval` | `0.0` | `[-3.8e-17, +3.8e-17]` |
| `small_height` | `0.0` | `[-3.8e-17, +3.8e-17]` |
| `coset_union` | `0.0` | `[-3.8e-17, +3.8e-17]` |

The CI half-width is the float noise of the ULP effect noted above, not a
measured spread. The exploratory exact recomputations of the two prior-cell
geometries behave identically: `qr_walk_H016` slope `-0.0`,
`small_multiples_H017` slope `0.0`, both with mean-yield ratio `1.000000` at
every size.

The three cells whose measured mean-yield ratio is *not* 1 are exactly the three
predicted escape routes, and each is accounted for:

* `mixed_two_base` (`0.3726 / 0.3700 / 0.3749`) and `asymmetric_sizing`
  (`0.0342 / 0.0418 / 0.0420`) count a different family `M` (typed patterns)
  than their untyped same-total-size control — route 3 of consequence (i), and
  the subject of consequence (iv). Against a **same-typing** matched-random
  control both have a mean ratio of exactly `1.000000` at every rung and size.
* `greedy_optimized` (`0.9554 / 0.9717 / 0.9806`) is evaluated on a held-out
  half rather than the whole group — route 2. Its whole-group total obeys the
  identity exactly; the greedy selection moves count mass onto the training half
  (training mean ratio `1.0446 / 1.0283 / 1.0194`), and the held-out deficit is
  the exact complement of that shift.

### (iii) Coverage is bounded by the mean, and concentration destroys coverage

Let `cov_D = #{r : c_D(r) >= 1} / N`. Splitting the identity over the support of
`c_D`:

```
N * mean = sum_r c_D(r) = #{r : c_D(r) >= 1} + sum_r (c_D(r) - 1)^+
```

so

```
cov_D = mean - (1/N) * sum_r (c_D(r) - 1)^+        (exact accounting identity)
```

and therefore `cov_D <= min(1, mean)`, with `cov_D = mean` (when `mean <= 1`)
if and only if `c_D(r) <= 1` for every `r`, i.e. no target has two
decompositions. Every repeated multiset sum — every additive coincidence inside
`D` — is subtracted from coverage one for one. Additive structure in `D` can
therefore only **lower** coverage at matched size; it cannot raise it above the
`mean` ceiling. With the concentration statistic `conc = (1/N) sum_r c(c-1)` and
the elementary inequality `(c-1)^+ <= c(c-1)/2` for integers `c >= 0`, the
identity also gives the reportable lower bound `cov >= mean - conc/2`.

**Status: CONFIRMED.**

* 336 measured cells checked (all geometries, all evaluation domains, all
  sizes): **0** violations of `cov <= min(1, mean)`, and the equality condition
  `cov = mean iff max_count <= 1` held in every cell
  (`runs/RUN-FB3-001-FAMILY/raw-result.json`,
  `analytic_arm.consequence_iii_coverage_bound`).
* The bound is not vacuous. The log-space-structured bases lose almost all of
  their coverage to concentration: the exact recomputation of the H017
  small-multiples geometry has mean ratio exactly `1` and coverage ratio
  `0.0126 / 0.0051 / 0.0021` at `2^14 / 2^16 / 2^18` with concentration ratio
  `188 / 480 / 1224`. The mixed geometry's secondary typing (two from the
  small-multiples sub-base) shows the same trade: coverage ratio
  `0.0920 / 0.0616 / 0.0395` against concentration ratio `2.48 / 4.05 / 6.67`.
* Two geometries end up marginally **above** `1` in coverage ratio at `2^18`:
  `coset_union` (`1.00121`) and `greedy_optimized` (`1.00299`). This does not
  contradict the consequence, which bounds coverage by the mean (`1.0436`), not
  by the coverage of a random base. The consequence's directional clause
  ("additive structure can only lower coverage") is a statement about additive
  coincidences; a base with *fewer* coincidences than a random base of the same
  size legitimately has slightly higher coverage, still under the `mean`
  ceiling. Both cases are analysed in `analysis.md`; neither is significant
  against its own per-size permutation band, and the greedy excess decays with
  `N`.

### (iv) Typing is a fixed penalty, not a lever

For typed decompositions with sub-bases of sizes `B1 + B2 + B3 = B`, one element
from each, the counted family is a Cartesian product, so
`sum_r c(r) = B1*B2*B3`. By AM-GM, `B1*B2*B3 <= (B/3)^3 = B^3/27`, with equality
iff `B1 = B2 = B3`, whereas untyped counting gives
`binomial(B+2,3) = B(B+1)(B+2)/6 > B^3/6`. Hence

```
typed_total / untyped_total <= 6 B^2 / (27 (B+1)(B+2))  ->  2/9 = 0.2222 as B -> inf,
```

a penalty of at least `27/6 = 4.5x` asymptotically, attained by the balanced
split and strictly worse for any unbalanced one. For the (1,2) pattern of
`mixed_two_base` with `B1 = ceil(B/2)`, `B2 = floor(B/2)` the total is
`B1 * binomial(B2+1, 2) ~ B^3/16`, i.e. a ratio approaching `6/16 = 0.375`.

**Status: CONFIRMED, with the asymptotic constants recovered.**

| quantity | 2^14 | 2^16 | 2^18 | predicted limit |
|---|---|---|---|---|
| balanced typed / untyped total | `0.20761` | `0.21303` | `0.21664` | `0.22222` |
| balanced typing penalty (reciprocal) | `4.817x` | `4.694x` | `4.616x` | `4.5x` |
| `mixed_two_base` (1,2) typed / untyped | `0.37264` | `0.37000` | `0.37492` | `0.375` |
| most unbalanced rung `(8,1,1)` typed / untyped | `0.03387` | `0.04182` | `0.04198` | (split-dependent) |

* 144 typed cells: every typed total is strictly below the untyped total at the
  same `B`, and every typed mean-yield ratio against the untyped same-size
  control is below `1`.
* The `asymmetric_sizing` ladder is monotone in the wrong direction for H004:
  at `2^18` the typed/untyped total falls `0.2166 -> 0.1812 -> 0.1042 -> 0.0420`
  as the split goes `(1,1,1) -> (2,1,1) -> (4,1,1) -> (8,1,1)`. No rung
  dominates the balanced rung; unbalancing strictly reduces the number of typed
  decompositions available, exactly as AM-GM requires.

## 3. Is the identity convention-bound?

Pre-registered secondary exploratory arm (amendment `honesty_notes`): recount
with the symmetric convention `D u (-D)`.

The proof of section 1 never used how `D` was built, so it applies verbatim to
the set `D' = D u (-D)`: `sum_r c_{D'}(r) = binomial(|D'| + 2, 3)`. Measured, at
every size and every arm:

| arm at `2^18` | effective size `B'` | exact mean | total equals `C(B'+2,3)` |
|---|---|---|---|
| `symmetric/high_bit_interval` | 234 | `8.2434` | yes |
| `symmetric/small_height` | 234 | `8.2434` | yes |
| `symmetric/coset_union` | 234 | `8.2434` | yes |
| `symmetric/matched_random` | 234 | `8.2434` | yes |

So the identity is **convention-robust in form and convention-bound in its
constant**. Allowing signs raises the mean by a factor of about
`C(2B+2,3)/C(B+2,3) ~ 8` because it doubles the effective base size, and
coverage saturates (`0.9997` at `2^18`), but no arm gains any advantage over
matched random: whenever the effective sizes agree the exact means agree
exactly. The small cross-arm mean differences visible at `2^14`
(e.g. `8.7447` versus `8.2139`) are entirely a `B'` difference: `B' = 2B` unless
two base elements are mutual negatives, which happened for one matched-random
base at `2^14` (`B' = 92` instead of `94`) and for none of the structured bases
at that size. Since the exact total equals `C(B'+2,3)` in every one of those
cells, the mean is a function of `(B', N)` alone — consequence (i)'s "size
mismatch" escape route, observed in the wild.

## 4. What the identity does not say

* It says nothing about the **cost of finding** a decomposition. It counts how
  many decompositions exist; the index-calculus cost sits in the search, which
  this experiment does not measure.
* It says nothing about the **distribution** of the counts. Coverage,
  concentration, and every geometry-sensitive quantity live in the distribution,
  which the identity leaves completely free subject to its total.
* It is bound to the counted family `M`. Signs, other `m`, restricted target
  sets, or weighted counting all change the constant, and the symmetric arm
  above shows one such change explicitly.
* It is not a statement about ECDLP hardness, and it supports no cost, speedup,
  or attack claim. The measurements behind it are toy scale (`N <= 2^18`) with
  discrete logs known by construction for measurement only.
