# Red-team objections — EXP-FB3-001 (TASK-20260724-233)

Independent red team for `GOAL-ICLIFT-001` `BATCH-001`. Target producer task
`TASK-20260724-228` (executor). Reviewed snapshot commit
`68e375f720123d4f46b1b5bc686920d77bf5ecf4` (parent
`e18c9bc0b90e3031cfa28483fe5571c0fb548dfb`), archive receipt
`coordination/goals/GOAL-ICLIFT-001/batches/BATCH-001/archives/TASK-20260724-230/snapshot-receipt.json`.
Working tree clean at `HEAD = ae5503dc288efe74f23a870c59d5870c5f779d72`, so the
artifacts attacked below are the committed ones.

I did not produce these artifacts. I did not re-check the executor's arithmetic
(that is the Validator's task). I attacked the interpretation, the counting
convention, the cost relevance, and the claim boundary, and I wrote and ran my
own throwaway probes in `/tmp` to try to break them.

**Overall position: `conclusion_requires_narrowing`.** The frozen success
criterion demonstrably fails and a scoped negative is supportable, but the
frozen falsification wording ("scoped KILL of the F3 factor-base family", "no
signal seen at reachable scale") is broader than what was measured in three
specific ways, and one pre-registered arm (`greedy_optimized`, H022) was
measured under a protocol that suppresses its own effect by about an order of
magnitude. Nothing I found is fatal to a scoped reject of H-FB3-001.

---

## 0. What I ran

Three throwaway probes, pure Python 3, no repository files touched. Full source
is reproduced in §9.

| probe | question |
|---|---|
| `/tmp/rt_probe.py` | Can the conservation identity fail in any convention? Does a Sidon/`B_3` base beat matched random? Is random coverage `1-e^-mu`? What is the universal coverage ceiling? Do restricted target sets break mean-invariance? |
| `/tmp/rt_probe2.py` | How much coverage headroom exists at the frozen operating point `B = ceil((6N)^(1/3))`? |
| `/tmp/rt_probe3.py` | Same question at the battery's **own** `2^18` curve orders, `B = 117`, pool `= 4B = 468` — apples to apples against the `greedy_optimized` cell. |

---

## 1. RT-1 (`scoping`) — "scoped KILL of the F3 family" is broader than what was closed

`specification.yaml` `falsification_criterion`: *"All geometries within CIs /
permutation bands at every N, or every nonzero effect constant across N: scoped
KILL of the F3 family — 'no signal seen at reachable scale'."*

The phrase "no signal seen at reachable scale" is true of the six tested
geometries on the two measured metrics. It is **not** true as a statement about
factor-base geometry in general, and the conservation identity does not make it
true. The identity pins the mean; coverage is free up to `min(1, mean)`, and
that headroom is large at the frozen operating point.

Measured headroom at the battery's own `2^18` parameters (probe 3, `N = 261643`,
`B = 117`, pool `= 4B = 468`, log-space construction, whole-group evaluation):

| base | exact coverage | ratio vs matched random |
|---|---|---|
| matched random (12 draws) | `0.649060` | `1.0000` (battery reports null `0.6480`) |
| `greedy_optimized` as run (held-out half) | — | `1.00299` (`+0.30%`) |
| whole-group low-collision greedy, same B, same pool | `0.666488` | **`1.0269` (`+2.69%`)** |
| ceiling `min(1, mu) = 1.0` | `1.000000` | **`1.5407` (`+54.1%`)** |

and a second geometry, entirely outside the six, that attains the ceiling
*exactly* (probe 1): a **Bose–Chowla `B_3` (Sidon-of-order-3) base**
`A = {a : theta^a - theta in F_q}` in `Z_{q^3-1}`. At `q = 13`, `N = 2196`,
`B = 13`: `max_count = 1`, so `coverage = mean = min(1, mean)` exactly,
mean-yield ratio `1.000000000` (the identity), and

```
coverage(B_3) / coverage(random) = 0.207195 / 0.187147 = 1.1071      (+10.7%)
```

asymptotically `1/6 / (1 - e^(-1/6)) = 1.0856` (`+8.6%`) for Bose–Chowla's
`|A| = q`, `N = q^3 - 1` schedule.

**Implication.** The recorded claim must be a **growth-clause** kill on the
**yield channel** for the **six named geometries**, not a statement that no
geometry beats random. A `+2.7%` (constructed with the same budget as the arm
that was run) and a `+10.7%` (a textbook additive-combinatorics object) are both
larger than everything the battery observed, by factors of 9 and 36.

## 2. RT-2 (`scoping`, fatal to one sentence) — the H022 arm cannot measure H022

Frozen definition (`amendment-001.yaml`, `frozen_definitions.geometries.greedy_optimized`):
*"Split the target space into a training half and a held-out half by a recorded
deterministic rule. Greedily add ... the pool point that maximizes the number of
newly covered TRAINING targets ... Report yield and coverage on the HELD-OUT
half only."* Implementation confirms it
(`implementation/fb3_core.py:677` `greedy_select(... train_bits ...)`,
`greedy_split` = seeded permutation, first half training, `greedy_pool_factor: 4`).

A train/held-out split is the correct guard when a statistic is estimated on a
**sample** of targets, which is what the pre-amendment protocol did (">=300
random targets"). Amendment `AMD-2` replaced sampling with **exact counting over
the whole group**. Once the whole group is counted, the group *is* the
population: a fresh uniform target decomposes with probability exactly equal to
the whole-group coverage. There is nothing left to overfit, so the split is not
a guard any more — it is a handicap, and by the conservation identity it is a
guaranteed one. Pushing count mass onto a random half necessarily starves the
complement (the executor measured exactly this: training mean ratio
`1.0446/1.0283/1.0194` versus held-out `0.9554/0.9717/0.9806`), and the greedy
objective is indifferent to collisions it creates on the held-out half.

I rebuilt the arm with the only change being the objective — same `N`, same
`B = 117`, same pool `4B = 468`, same log-space oracle, whole-group coverage
objective, whole-group evaluation:

| `N` (battery curve order) | frozen held-out coverage ratio | whole-group-objective coverage ratio |
|---|---|---|
| `261643` (`2^18` curve 1) | `1.0030` | `1.0269` |
| `261563` (`2^18` curve 4) | `1.0030` | `1.0275` |

a factor of **9.0–9.2**. Raising the pool at `2^18` gives diminishing returns
(`4B -> +2.62%`, `16B -> +3.15%`, `64B -> +3.43%`), so the level is a property of
the greedy heuristic, not of the pool rule.

**The offending sentence** (`analysis.md` §8, claim boundaries):

> "the `greedy_optimized` base is *selected* using the full discrete-log table,
> so that construction is not available to an attacker at all — it measures what
> an oracle-aided base could achieve, which makes its sub-1% decaying coverage
> excess an upper bound of an unrealisable kind, not an attack step."

"it measures what an oracle-aided base could achieve" is wrong by ~9x. What an
oracle-aided base achieves at these parameters is `+2.7%` (`+3.4%` at a 64B
pool), and the true ceiling for *any* base is `+54%`. The oracle-unavailability
point is correct and important; the number attached to it is not an upper bound.

**But the growth clause survives my correction, more decisively.** Running the
corrected objective at all three frozen sizes (1 curve per size, no replication,
no permutation null — a reduced version of the control I recommend):

| size | `N` | `B` | whole-group greedy coverage ratio |
|---|---|---|---|
| `2^14` | `16339` | `47` | `1.0565` (`+5.65%`) |
| `2^16` | `65579` | `74` | `1.0418` (`+4.18%`) |
| `2^18` | `261643` | `117` | `1.0272` (`+2.72%`) |

OLS slope vs `log2 N` = **`-0.00734` per bit**, versus the frozen arm's
`-0.00118`. The corrected arm has a larger effect at every size *and* decays
about six times faster, while the analytic ceiling drifts slightly **up**
(`+0.0167` per bit, because `mu -> 1` from above). Fraction of the available
headroom realised falls `0.119 -> 0.080 -> 0.050`.

**Implication.** The Coordinator may record that the greedy arm fails the growth
clause. The Coordinator may **not** record that greedy optimization finds no
exploitable additive structure, and must not quote the `<1%` figure as the
oracle-aided ceiling.

## 3. RT-3 (`scoping`) — the primary metric does not operationalize the hypothesis's own mechanism

`H-FB3-001.mechanism`: *"**Decomposition probability** depends on how the base's
x-coordinates interact with the chord structure of the summation condition."*
Decomposition probability is **coverage**. The frozen `success_criterion` is
stated on the **yield ratio** (the mean), which the pre-registered analytic arm
proves is exactly `1` for every matched-size untyped base at every `N`
(`conservation.md` §2(i)-(ii)).

So the pre-registered primary test could not have passed for 3 of 6 cells under
any data, and for 2 more (`mixed_two_base`, `asymmetric_sizing`) its value is a
closed-form typing constant fixed before any measurement. Only
`greedy_optimized` carried any contingency, and only because its evaluation
domain is a proper subset of the group. The executor states this plainly
(`analysis.md` §7: *"the primary metric is **mathematically incapable** of
showing a matched-size geometry effect"*), which is exactly right and must be
carried into the evidence record.

**Implication.** "0 of 6 geometries met the success criterion" is true but must
not be recorded as six null *findings*. It is one theorem applied to three
cells, one arithmetic identity applied to two, and one contingent measurement.
The evidential weight of the negative sits entirely on the **secondary exact
coverage metric** plus the ceiling argument of RT-5, and the decision record
should say so in those words.

## 4. RT-4 (`noted`) — the identity is unfalsifiable, so its "confirmation" is a counter control, and the one real escape route is a restricted target set

I tried ten conventions to break `sum_r c(r) = |M|` (probe 1, P4). All hold
exactly:

```
(a) plain multisets m=3      : 165 vs C(B+2,3)=165   True
(b) repeated base elements   : 165 vs C(B+2,3)=165   True     <- multiset base
(c) identity element in base : 165 vs C(B+2,3)=165   True
(d) m=2 / m=4 / m=5          : 45/495/1287 vs C(B+m-1,m)  True
(e) signed D u -D  (|D'|=18) : 1140 vs C(20,3)=1140  True
(f) NON-CYCLIC Z_2 x Z_8     : 84 vs C(9,3)=84       True
(g) ordered tuples           : 729 vs B^m=729        True
(h) typed Cartesian (4,3,2)  : 24 vs B1*B2*B3=24     True
```

The proof uses only that a target-independent counted family `M` maps into the
group, so it cannot fail for repeated elements, the identity element, any `m`,
signs, non-cyclic groups (relevant: `E(F_p)` need not be cyclic; this battery
restricted to prime order), ordered conventions, or typed patterns. In
particular the **cryptographically relevant** convention — factor base of
x-coordinates, `R = ±P1 ±P2 ±P3` over `D u (-D)`, targets `R = aP + bQ` uniform
in `<P>` — is covered verbatim, with constant `C(2|V| + 2, 3)`.

Two consequences the record should carry:

* The 67 784 closed-form-total checks are a **counter-verification control**,
  not empirical support for a research claim. Writing "the identity was
  confirmed by 67 784 checks" would invert what was tested.
* The only convention in which mean-invariance fails is a **non-uniform or
  restricted target set**. Probe 1, P5: `N = 1009`, `B = 19`, `S` = a
  `1/8`-of-group window in log space, base `= {1,...,B}` (small multiples):
  whole-group mean ratio `1.000000000` (identity) but **on `S` the mean ratio is
  `8.01`**. So mean-invariance is strictly a whole-group statement and fails by
  a factor of 8 on a restricted target set.

Is that route cryptographically live? For standard relation collection, no:
`R = aP + bQ` with random `a, b` is uniform, which is the tested convention. The
route becomes live only if the target restriction is decidable from the target's
**representation** rather than its logarithm — selecting `r` with `log(r) in S`
requires knowing `log(r)`. That is a real, untested, open channel (see RT-11),
and it sits squarely inside `KN-OPEN-001`.

## 5. RT-5 (`scoping`) — the cost model is missing, and supplying it both strengthens and bounds the claim

Neither `analysis.md` nor `conservation.md` nor `execution-report.yaml` states
relations per unit work. Supplying it changes what may be claimed:

**(a) Harvest-all-solutions model (the realistic one).** `EV-R6-001` records
`vdim 0..61` with per-cell medians `4.5-9`, i.e. a single Gröbner solve returns
all decompositions of the target at once. Expected relations per solve attempt
is then `E_r[c(r)] = mu = C(B+m-1, m)/N` — **exactly** geometry-invariant by the
identity. Under this cost model the yield channel is closed *exactly*, not
approximately, and coverage is irrelevant. This is a stronger closure than the
one the artifacts argue, and it is the right one to record.

**(b) One-relation-per-target model.** Throughput is `coverage`, and the gain
over matched random is `coverage / coverage_random <= min(1, mu) / (1 - e^-mu)`.
Probe 1, P2 maximises that expression over `mu`:

```
argmax mu = 1.0000   max ratio = 1.581977
mu = 0.001 -> 1.0005     mu = 1.0000 -> 1.5820     mu = 2.00 -> 1.1565
mu = 0.100 -> 1.0508     mu = 1.0436 -> 1.5436     mu = 8.24 -> 1.0003
```

So **the maximum coverage advantage of any base over a matched random base is a
universal constant `<= 1.582`, at any `N`, any `B`, any `m`, any convention** —
attained only at `mu = 1`, which is exactly where the frozen
`B = ceil((6N)^(1/3))` places the battery. The frozen operating point is the
*most favourable* one for the effect sought, and the bound cannot grow with `N`.
This closes the growth clause on the coverage channel by argument for **all**
geometries, not six. (Caveat, stated honestly: the bound `coverage <= min(1, mu)`
is a theorem; `coverage_random ~ 1 - e^-mu` is a heuristic. Probe 1, P3 measures
`0.740/0.679/0.678` versus `0.732/0.675/0.675` at `N = 1009/4001/16381`, and the
battery's own nulls are `0.6734/0.6594/0.6480` versus `0.6719/0.6588/0.6478` —
agreement to `0.2%-1%`. Label it heuristic-with-measured-support, not proved.)

**Baseline arithmetic.** `EV-R6-001` measured the `m=3` chained-Semaev solve at
`2.0e4..1.5e5x` Pollard rho on the same instances (`gb`-only
`5.1e3..2.7e4x`), with `d_reg` median flat at `2.0`. A *saturated* `1.582x`
coverage gain moves that to `1.3e4..9.5e4x` — still four to five orders of
magnitude behind rho. And at cryptographic parameters real prime-field IC would
run at `mu << 1`, where the ceiling is `1 + mu/2 -> 1`: the coverage channel is
*more* closed at crypto scale than at the tested `mu ~ 1`.

## 6. RT-6 (`scoping`) — "conservative" is backwards for a null conclusion

Two sentences:

> `analysis.md` §3: "family size 8 at every size (prior-cell slots retained even
> where censored, which is conservative)."

> `execution-report.yaml` D3: "`effect_on_criteria: conservative (family size
> stays 8)`."

Holm–Bonferroni controls the family-wise **false-positive** rate. The conclusion
being recorded is a **false-negative** claim ("no signal"). Inflating the family
from the number of real tests to 8 makes rejection harder, so it makes a null
*easier* to reach — that is anti-conservative for this conclusion, not
conservative. The label should read "conservative for any claimed effect;
permissive for the null, so the null is not sourced from failure to reject."

The family is thinner than "8 cells" suggests: on the primary metric 3 cells are
pinned at exactly `1` by theorem, 2 are pinned at a closed-form typing constant,
and 2 are censored recorded cells at `2^14` only. One cell
(`greedy_optimized`) carries contingency.

The kill must therefore be sourced from **effect sizes and sensitivity**, which
are good: the per-cell coverage null band at `2^18` is
`null_ratio_band_95 = [0.99516, 1.00476]`
(`runs/RUN-FB3-001-N18/raw-result.json`, `high_bit_interval` curve 1), i.e. a
per-cell resolution of about `±0.5%`, and the 16-replicate aggregate resolved
`+0.30%`. Against a ceiling of `+54%` (RT-5) that is ample power. Say it that
way, not "we failed to reject across an 8-cell Holm family."

## 7. RT-7 (`noted`) — two slope statements need the family-wise number, not CI95

* `analysis.md` §4 gives `coset_union` coverage slope CI95
  `[+0.000086, +0.00226]`, excluding 0. The family-wise interval in
  `runs/RUN-FB3-001-FAMILY/raw-result.json`
  (`growth.coset_union.coverage.ci99.375`) is
  `[-0.000453, +0.00253]`, which **includes 0**. The column is honestly labelled
  "slope CI95", but the frozen criterion is Holm-adjusted, so at the family-wise
  level `coset_union` has no slope effect at all. This *strengthens* the kill and
  should be recorded at the family-wise level.
* `greedy_optimized` coverage slope family-wise CI99.375 is
  `[-0.00228, -7.9e-7]` — it excludes 0 by `8e-7`. The "decays with `N`" claim is
  therefore fragile at the family-wise level. It does not matter for the verdict:
  a slope indistinguishable from 0 also fails the frozen growth clause (and
  matches H-FB3-001 falsification condition 2, "effect present but constant
  across N"). Record the verdict as robust to that fragility rather than leaning
  on the decay.

## 8. RT-8 (`noted`) — the greedy coverage excess is real, and honestly reported

I checked pseudo-replication directly. `greedy_optimized` **does** vary with the
replicate seed (the `4B` pool is seeded), so its 16 replicates are not
pseudo-replicated the way the three deterministic geometries are. At `2^18`,
14 of 16 replicates are above 1; the four curve means are
`1.00393 / 1.00235 / 1.00161 / 1.00407`, giving `t = 4.96` on 3 df
(`p ~ 0.016`). The curve-cluster `ci99.375 = [1.00161, 1.00407]` excludes 1 but
is exactly the min/max of four numbers, so it carries no real `99.375%`
guarantee — the defensible statement is "the excess appears in all four curves".
Anomaly `A3` describes this correctly. No change to the verdict.

Separately: the shared untyped permutation null (one set per
`(curve, N, seed, B)`) makes the three untyped coverage tests correlated. Holm
is valid under arbitrary dependence, so there is no validity problem, but the
record should not describe them as three independent nulls.

## 9. RT-9 (`scoping`) — the H004 arm cannot reach H004's design point

`H-FB3-001` prediction 2 and `specification.yaml` both name
*"`B_1 != B_2 != B_3` with `B_1*B_2*B_3 ~ l`"*. The amendment pins
`B1 + B2 + B3 = B = ceil((6N)^(1/3))`, so by AM-GM
`B1*B2*B3 <= (B/3)^3 = 6N/27 = 0.222 N < N`. The arm can never reach a product
`~ l`; reaching it needs total size `3 N^(1/3) ~ 1.65 B`, i.e. a base 65% larger
than the frozen matched size. So the `asymmetric_sizing` cell tests "unbalanced
splits at fixed total size", which AM-GM settles *a priori* (and the measured
ladder `0.2166 -> 0.1812 -> 0.1042 -> 0.0420` at `2^18` reproduces it), and its
Holm rejection is a size/typing artifact, not measured evidence about H004's
design point. The executor discloses this (D6(b), A5) and reports exactly
`1.000000` against same-typing controls.

**Implication.** Record H004's closure as "settled by AM-GM at matched total
size; the fixed-product (`B1*B2*B3 ~ l`) design point was not built, and at
matched typed total the ratio is forced to 1." Do not present the H004 Holm
rejection as measured evidence.

## 10. RT-10 (`noted`) — relation rank is unmeasured, and the omission is conservative for the kill

A relation is useful only if it is independent of the ones already collected.
The battery measures decomposition **counts** and never rank. Rank
`<= relation count`, and a random base is generically rank-optimal, so **no
geometry can gain on the rank channel** — the omission cannot rescue the F3
family. But it means the battery's metrics score cryptanalytically vacuous bases
as *exactly tied with random*:

* the `mixed_two_base` small-multiples sub-base and the exploratory
  `small_multiples_H017` base have logs `{1, ..., B}` — a rank-1 lattice, so the
  factor-base logs are all known multiples of `log G` and the relations are
  vacuous, yet the recorded mean-yield ratio is `1.000000`;
* the `qr_walk_H016` reconstruction is an r-adding walk with `r = 20`,
  `c_j in [1, 2^10)` (`analysis.md` §1), so its 47 logs lie in the `Z`-span of at
  most 21 values — the relation lattice is rank-deficient by construction and the
  deficiency is known to whoever knows the walk.

Any geometry that could realise the coverage ceiling of RT-5 must be constructed
in **log space** (additive structure in the group *is* log-space structure), so
it inherits exactly this defect — which is the deeper reason the ceiling is
unreachable by an attacker, and a better statement than the greedy-oracle remark
in `analysis.md` §8.

**Implication.** Add "relation rank and independence are not measured" to the
boundaries, and note that the omission bounds the F3 family further rather than
sparing it.

## 11. RT-11 (`scoping`) — channels the scoped kill must not appear to cover

The artifacts are careful here. `analysis.md` §8 says: *"A null result here
closes the **yield channel** of the F3 family on the tested scope; it says
nothing about the solving channel."* I searched for a sentence claiming closure
of index calculus, a cryptanalytic result, or closure of factor-base research
generally, and **found none** in `analysis.md`, `conservation.md`, or
`execution-report.yaml`. That boundary discipline should be preserved verbatim
in the evidence record. The channels a reader could wrongly think are covered:

1. **The solve.** Decisive point for the record: Gaudry–Diem's celebrated
   decomposition probability `1/n!` over `F_{q^n}` **is** the conservation mean —
   with `|F| ~ q`, `N ~ q^n`, `m = n`, `mu = C(q+n-1, n)/q^n ~ 1/n!`. So the
   extension-field advantage is *not* a yield-geometry advantage; it comes from
   the Weil restriction making the summation-polynomial solve tractable. The
   identity is fully consistent with index calculus working. Closing the yield
   channel therefore cannot be read as evidence against IC.
2. **Linear algebra.** `KN-OPEN-006` is open and proposes *arithmetic-progression
   relation supports* to force displacement-rank structure — cousins of
   `high_bit_interval` and the small-multiples sub-base. A reader who takes "the
   F3 family is killed" as covering AP-structured bases would wrongly close an
   open problem in a different stage.
3. **Sumset-recognizable bases.** A base whose `Sigma_m(D)` membership is cheaply
   decidable from the target's *representation* would let the attacker skip
   failing solves, cutting relation cost by `1/coverage` — unbounded as
   `mu -> 0`, not the bounded `1.582x`. Invisible to both measured metrics, not
   among the six, not closed. This is the sharpest surviving descendant of the
   F3 question.
4. **Sidon / `B_3` and other extremal additive geometries** (RT-1), **descent /
   individual logarithm**, **memory**, **other `m`** (`m = 4` is fully censored
   in `EV-R6-001`), **signed bases matched at x-coordinate count**, and
   **restricted target sets** (RT-4).

## 12. RT-12 (`noted`) — what the toy scale does and does not permit

*Permits, because they are size-free:* the mean-invariance identity (a theorem
in any finite abelian group for any target-independent counted family), and the
`coverage <= min(1, mu)` bound. Their transfer to crypto scale is mathematical,
not extrapolated.

*Does not permit:* any claim that x-coordinate structure remains additively
pseudorandom at large `B` — `B <= 117` here, and a weak additive bias in a
117-element set is not detectable at `±0.5%` per cell; any solve, linear-algebra,
memory, or `B/N`-tradeoff claim; any statement about the four generated curves per
size generalising to standardised curves.

*Perspective for the record:* exact counting at `2^18` costs about `5e5`
operations per cell (`O(B^3/6 + N)`), while Pollard rho solves the ECDLP on the
same curve in about `0.886 sqrt(N) ~ 453` group operations. Nothing measured
here is on an attack path, and the honesty note in `amendment-001.yaml`
("discrete logs ... known BY CONSTRUCTION ... no result here is a step of an
attack") is accurate.

## 13. RT-13 (`noted`) — one archive bookkeeping gap (Validator/Coordinator territory)

`archives/TASK-20260724-230/snapshot-receipt.json` records
`"commit_sha": null`, although the snapshot commit
`68e375f720123d4f46b1b5bc686920d77bf5ecf4` exists with the receipt's recorded
parent `e18c9bc`. The verification commit `ae5503d`'s message says it *"Fills the
TASK-20260724-230 and TASK-20260724-231 archive receipts with their commits
(68e375f, 9f9186c), parents, and per-path SHA-256 values"*, but its diffstat
touches only `current_dispatch.json`, `current_dispatch.md`, and
`dispatch_queue.json`. The sha is present at `dispatch_queue.json:397`. Also,
`declared_paths` has 40 entries and `path_sha256` has 39 (the receipt excludes
its own hash, `receipt_self_hash_excluded: true`, which is consistent).

This did not impair my review — the tree is clean and the artifacts I read are
the committed ones — but the receipt as written does not name its own commit.
Flagging it, not adjudicating it.

---

## 14. Narrowest defensible claim boundary

Exact sentences the Coordinator is entitled to record:

> For the six pre-registered factor-base geometries of H-FB3-001, at
> `N ~ 2^14/2^16/2^18` on 12 generated prime-order curves `E/F_p`, under the
> frozen counting convention (`m = 3`, unsigned multisets of factor-base points,
> targets uniform over the whole group, matched size `B = ceil((6N)^(1/3))`), no
> geometry met the frozen success criterion: 0 of 6 have a mean-yield ratio above
> 1 at any size, and no geometry has both a CI excluding 1 in the advantage
> direction and a growth slope excluding 0 in that direction, on either the
> primary mean-yield metric or the secondary exact-coverage metric
> (EXP-FB3-001; RUN-FB3-001-N14/N16/N18/CTRL/FAMILY; `analysis.md` §3-§5, §7).
>
> The mean-yield arm is vacuous by construction and carries no evidential
> weight: the pre-registered conservation identity forces the exact mean
> per-target yield of every base of size `B` to `C(B+2,3)/N`, so the primary
> metric equals 1 for every matched-size untyped base at every `N`, and the two
> typed cells' Holm rejections are the closed-form typing penalty rather than an
> element-geometry effect (`conservation.md` §1-§2, consequences (i), (ii), (iv)).
> The negative therefore rests on the secondary exact-coverage metric, where the
> largest advantage anywhere in the battery is `+0.30%` (greedy_optimized
> held-out coverage at `2^18`) against a per-cell null resolution of about `±0.5%`
> and a 16-replicate resolution of about `0.3%`.
>
> Scope of the negative: it closes the growth clause of the decomposition-YIELD
> channel for these six geometries, on this convention, at this scale. It does
> not establish that no factor-base geometry exceeds a matched random base on
> decomposition probability — coverage is free up to `min(1, mean)`, and bases
> outside the pre-registered six realise part of that headroom.
>
> Claim tier `toy` (field_bits 14-18). Untested and open: the cost of FINDING a
> decomposition, the linear-algebra stage, relation rank and independence,
> restricted or representation-selected target sets, other `m`, signed
> conventions matched at x-coordinate count, and every geometry outside the six.
> No cryptanalytic consequence follows, and `KN-OPEN-001` is untouched.

## 15. Over-reach to avoid

Exact sentences that would over-reach, each with what refutes it:

> "No structured factor base outperforms a matched random factor base."

Refuted: a Bose–Chowla `B_3` base attains `coverage = min(1, mean)` exactly
(measured ratio `1.1071` at `q = 13`, `N = 2196`); a whole-group low-collision
greedy at the battery's own `2^18` parameters reaches `1.0269`.

> "Even an oracle-aided base gains less than 1%."

Refuted: `+2.69%` at `2^18` with the same oracle and the same `4B` pool,
`+3.43%` at a `64B` pool; the ceiling is `+54%`.

> "The F3 factor-base family is dead." / "Factor-base geometry is closed as a
> research direction." / "Structured factor bases cannot help index calculus."

Over-reach: six named geometries, yield channel, growth clause only. And the
identity is *consistent with index calculus working* — Gaudry–Diem's `1/n!`
decomposition probability over `F_{q^n}` **is** the conservation mean, so the
extension-field advantage lives in the solve, which this experiment does not
touch.

> "Retaining the censored prior-cell Holm slots makes the null conclusion
> conservative."

Backwards: inflating the family size makes detection harder, which weakens a
null rather than strengthening it.

> "The conservation identity was empirically confirmed by 67 784 checks."

Category error: those checks verify the counter. The identity is a double count
that cannot fail for a target-independent counted family (10 conventions tested,
all hold).

> "The coverage channel is closed." (unqualified)

Over-reach as stated: closed *for these six geometries at this scale*, and
bounded for all geometries by a `<= 1.582` constant only under the heuristic
`coverage_random ~ 1 - e^-mu`.

Any sentence asserting a speedup, an attack step, a cryptanalytic result, or a
statement about medium or cryptographic curves.

## 16. Cheapest falsifying control

**One run, seconds of CPU, inside the existing harness.** Re-run the
`greedy_optimized` arm at the three frozen sizes with the **whole-group coverage
objective and no train/held-out split** (exact whole-group counting leaves
nothing to overfit), and add two arms at matched `B`: a Bose–Chowla `B_3`
(Sidon-of-order-3) base, and the same greedy at a `64B` pool. Report the
exact coverage ratio with its permutation band and the family-wise slope vs
`log2 N`, against the analytic ceiling `min(1, mu)/(1 - e^-mu)`.

*Overturns the conclusion if* any arm has a coverage-ratio family-wise CI
excluding 1 upward **and** a slope excluding 0 upward across `2^14..2^18`. Then a
factor-base geometry has an exponent-relevant coverage advantage and the F3
question is alive on the correct metric.

*Confirms and sharpens it if* the ratios exceed 1 but the slope is negative or
zero. My reduced version (1 curve per size, no null replication, no permutation
test) gives `+5.65% / +4.18% / +2.72%` with OLS slope `-0.00734` per bit, so I
expect confirmation. That is precisely why it is the right control: it builds the
strongest available version of the geometry the battery mis-specified, gets 9x
the effect, and still fails the growth clause 6x more steeply than the arm as
run. A kill that survives its strongest counterexample is worth recording; the
one currently on offer has not met it.

*Second-cheapest, if capacity allows:* instrument **relation rank** on one cell
per geometry (rank of the collected `(e_1..e_B | a, b)` rows mod `N`). It costs
one sparse rank computation per cell and would convert RT-10 from an argument
into a measurement, closing the F3 family on the channel that actually decides
whether relations are useful.

---

## 17. Probe source

`/tmp/rt_probe.py` (P1-P5), `/tmp/rt_probe2.py` (P6), `/tmp/rt_probe3.py` (P7).
Throwaway red-team code, not a research artifact and not committed; reproduced
here so the numbers above can be re-derived.

### `/tmp/rt_probe3.py` — the decisive apples-to-apples probe

```python
import math, random

def cyc_shift(bits, s, n, mask):
    s %= n
    if s == 0:
        return bits
    return ((bits << s) | (bits >> (n - s))) & mask

def sigma3_bits(D, n, mask):
    s_bits = s2 = s3 = 0
    for d in D:
        s3 |= (cyc_shift(s2, d, n, mask) | cyc_shift(s_bits, 2 * d, n, mask)
               | (1 << (3 * d % n)))
        s2 |= cyc_shift(s_bits, d, n, mask) | (1 << (2 * d % n))
        s_bits |= 1 << (d % n)
    return s3

def exact_counts_mean(D, n):            # coverage; mean is C(B+2,3)/n by conservation
    return sigma3_bits(D, n, (1 << n) - 1).bit_count() / n

def greedy_whole_group(n, pool, B):
    mask = (1 << n) - 1
    s_bits = s2 = s3 = 0
    chosen, remaining = [], list(pool)
    for _ in range(B):
        avail = mask & ~s3
        best_gain, best_d = -1, None
        for d in remaining:
            cand = (cyc_shift(s2, d, n, mask) | cyc_shift(s_bits, 2 * d, n, mask)
                    | (1 << (3 * d % n))) & avail
            g = cand.bit_count()
            if g > best_gain or (g == best_gain and (best_d is None or d < best_d)):
                best_gain, best_d = g, d
        d = best_d
        s3 |= (cyc_shift(s2, d, n, mask) | cyc_shift(s_bits, 2 * d, n, mask)
               | (1 << (3 * d % n)))
        s2 |= cyc_shift(s_bits, d, n, mask) | (1 << (2 * d % n))
        s_bits |= 1 << (d % n)
        chosen.append(d); remaining.remove(d)
    return chosen, s3.bit_count() / n

for N in (261643, 261563):              # actual RUN-FB3-001-N18 curve orders
    B = math.ceil((6 * N) ** (1 / 3))
    mu = math.comb(B + 2, 3) / N
    rng = random.Random(20260724)
    rc = sum(exact_counts_mean(rng.sample(range(1, N), B), N) for _ in range(12)) / 12
    pool = rng.sample(range(1, N), 4 * B)
    _, gcov = greedy_whole_group(N, pool, B)
    print(N, B, round(mu, 6), round(rc, 6), round(gcov, 6),
          round(gcov / rc, 4), round(min(1, mu) / rc, 4))
```

Output:

```
261643 117 1.046537 0.64906 0.666488 1.0269 1.5407
261563 117 1.046857 0.649306 0.667151 1.0275 1.5401
```

### `/tmp/rt_probe.py` — Bose–Chowla `B_3` base, ceiling, convention grid, restricted targets

```python
# P1  Bose-Chowla: A = {a : theta^a - theta in F_q} in Z_{q^3-1}, |A| = q, a B_3 set.
#     theta a primitive element of F_{q^3}, built from a primitive cubic found by search.
#     q = 13 -> N = 2196, B = 13, C(15,3) = 455 = measured total (identity holds),
#     max_count = 1 (perfect B_3), coverage = mean = 0.207195 = min(1, mean),
#     random coverage (40 draws) = 0.187147, 1 - exp(-mu) = 0.187139,
#     mean-yield ratio = 1.000000000, COVERAGE RATIO = 1.107123.
#
# P2  ceiling(mu) = min(1, mu) / (1 - exp(-mu));  argmax mu = 1.0000, max = 1.581977.
#
# P3  random-base coverage vs 1 - exp(-mu), B = ceil((6N)^(1/3)):
#       N=1009  mu=1.31814 cov=0.74034 vs 0.73237
#       N=4001  mu=1.12347 cov=0.67939 vs 0.67485
#       N=16381 mu=1.12472 cov=0.67804 vs 0.67526
#
# P4  sum_r c(r) = |M| under 10 conventions (see section 4) -- all True.
#
# P5  restricted target set S = first N/8 targets, base {1..B}, N=1009, B=19:
#       whole-group mean ratio 1.000000000 (identity)
#       on S: structured mean 10.5556 vs random 1.3175  ->  MEAN RATIO 8.0118
#       on S: structured cov  0.4365 vs random 0.7406  ->  COV RATIO  0.5894
```

### `/tmp/rt_probe2.py` — coverage headroom at the frozen operating point

```python
# whole-group low-collision greedy, pool = 4B, B = ceil((6N)^(1/3)),
# mean ratio exactly 1.000000000 in every case (identity), coverage ratio vs random:
#   N=401   B=14  ratio 1.1199   headroom realised 0.413
#   N=1009  B=19  ratio 1.1148   headroom realised 0.320
#   N=2003  B=23  ratio 1.0952   headroom realised 0.217
#   N=4001  B=29  ratio 1.0857   headroom realised 0.180
#   N=8009  B=37  ratio 1.0708   headroom realised 0.152
# (the small-N levels are inflated because a 4B pool is a large fraction of a tiny
#  group; at 2^18 a 4B pool is 0.179% of the group and the ratio is 1.0269)
#
# pool sensitivity at N = 261643, B = 117:
#   pool =  468 (= 4B)  ratio 1.0262
#   pool = 1872 (=16B)  ratio 1.0315
#   pool = 7488 (=64B)  ratio 1.0343
#
# three frozen sizes, pool = 4B, one curve each:
#   2^14 N= 16339 B= 47  ratio 1.0565
#   2^16 N= 65579 B= 74  ratio 1.0418
#   2^18 N=261643 B=117  ratio 1.0272
#   OLS slope of the ratio vs log2 N = -0.007342 per bit
#   OLS slope of the analytic ceiling vs log2 N = +0.016703 per bit
```
