# The quantity to be re-derived

You are performing a from-scratch blind re-derivation (Stage A''). **Read
`MANIFEST.yaml` first if you have not.** This file states the quantity and the
parameters. It states no result, no expectation, and no verdict at any open
cell.

Every definition below is quoted from the governing contract's `definitions`
and `inputs`. Where this file and that contract differ on any definitional
point, **the contract governs and this packet is defective** — report the
difference as a defect of the packet.

---

## 1. The instrument

A generic keyed random function on `N` points. There is no elliptic curve, no
finite field, and no group; the object is a functional graph.

```
step:  f(x) = mix64( x XOR K ) mod N,        for x in {0, ..., N-1}
```

`mix64` is a 64-bit avalanche mixer (any standard one; yours need not match
anyone else's — see §9). The walk key is derived from the integer seed:

```
K     = mix64( 0x9E3779B97F4A7C15 + seed )
K_dp  = mix64( K XOR 0xD1B54A32D192ED03 )
```

`K_dp` is the **distinguished-point key**, derived from `K` by a fixed
XOR-then-mix so that the DP marking is independent of the step function while
remaining a deterministic function of the seed.

## 2. Distinguished points

```
W             = sqrt( a * N / T )          (expected walk length between DPs)
theta         = 1 / W
dp_threshold  = floor( 2^64 / W )          (FLOOR, not round, not ceil)

x is a DP   iff   mix64( x XOR K_dp ) < dp_threshold
```

## 3. The walk cap — load-bearing, do not invent a convention

```
cap(N, a) = ceil( 8 * W(N, a) )
```

`cap` is a **count of walk steps** (group operations): a non-negative integer,
the **least integer >= 8*W**. Not `8*W` truncated, not `round(8*W)`, not a
distance in any other unit. The multiplier is exactly 8.

The cap binds in **two** places, and both are part of the quantity:

**(a) The exact basin partition.** A point is assigned to a basin only if its
distance to its first DP is `<= cap`.

**(b) Pool construction.** A pool-construction walk that reaches `cap` steps
without hitting a DP **terminates capped**: it is charged its `cap` steps to
the precomputation cost, and it credits **no `S_d` and no `h_d`** to any pool
entry. It is counted in `capped_walks`. Do not credit a capped walk to the DP
it would eventually have reached — that computes a different weight, hence a
different selection, hence a different coverage.

## 4. The exact basin partition and its residual mass

For each of the `N` points `x`, let `dist(x)` be the number of walk steps from
`x` to the first DP on its forward orbit, and `reach(x)` the predicate that
such a DP exists at all (some orbits enter a DP-free cycle and never reach
one). Compute `dist` exactly by full enumeration — pointer doubling with DPs
made absorbing is one way — and saturate `dist` for unreachable points.

Partition all `N` points into **exactly three disjoint, exhaustive** classes:

| class | condition | name |
|---|---|---|
| (1) | `reach(x)` and `dist(x) <= cap` | ASSIGNED |
| (2) | not `reach(x)` | CYCLE MASS |
| (3) | `reach(x)` and `dist(x) > cap` | CAPPED MASS |

`b(d)`, the **basin size** of DP `d`, counts points of **class (1) alone**
whose first DP is `d`.

The residual goes **nowhere**: it is not assigned to any basin, not
redistributed, and not discarded. It is **reported**, as two integers:

```
cycle_mass   = |class (2)|
capped_mass  = |class (3)|
```

**The accounting identity. It is NOT true that `sum_d b(d) = N`.** What holds,
exactly, in integer arithmetic with zero tolerance:

```
sum over all DPs d of b(d)  +  cycle_mass  +  capped_mass  =  N
```

Report `cycle_mass`, `capped_mass`, `capped_walks` and
`residual_fraction = (cycle_mass + capped_mass) / N` for **every** cell, and
check the identity at every cell. A cell where it does not hold exactly has an
implementation defect: stop and report it, do not fold it into a pass-count.

Corollary that catches a real defect class: **`b(d) >= 1` for every DP `d`**,
because `dist(d) = 0` at a DP and `0 <= cap`. A DP with `b(d) = 0` is a defect.

## 5. Pool construction

Generate a precomputation pool by **uniform random restarts**: pick a start
point uniformly at random from the `N` points, walk until a DP is reached or
the cap is hit, and repeat until the pool holds `r * T` **distinct** DPs.
Every walk is charged, whether it terminates or is capped (§3b).

For each pool entry `d` (a distinct DP that some walk terminated at), maintain:

- `h_d` — the **hit count**: the number of distinct pool-construction walks
  that terminated at `d`.
- `S_d` — the **sum of generating-walk lengths**: over every pool-construction
  walk that terminated at `d`, the number of steps from that walk's own start
  point to its termination at `d`. A DP hit by three walks of lengths
  `L1, L2, L3` has `S_d = L1 + L2 + L3`.

## 6. The selection weight and its tie-break

```
weight_d = S_d + 4 * W * h_d
```

The literal coefficient on `h_d` is `4 * W` — not `4*W^2`, not `W/4`. `W` is
the same `W` as in §2.

Select the **`T` pool entries with the largest `weight_d`**. This is the
realistic estimator, **never** the selected entries' own true exact basin
size: an oracle-by-true-size selection is a different and
better-for-the-selector quantity and is not what is being computed here.

**Ties at the `T`-th largest weight are real and they matter.** The
convention: ties are broken by an **ascending per-entry pseudorandom key**,
one key per pool entry, bound to the entry's **pool-insertion order** (the
order in which pool generation first discovered that DP), drawn as one bulk
array from a fresh pseudorandom generator seeded deterministically from the
integer seed. The key is **not** the DP value, **not** the pool index itself,
and **not** derived from the weight.

Your insertion order and your key stream will differ from any other
implementation's. **That is expected and is not a defect** — see §9. Report,
per cell, the **number of pool entries tied at the `T`-th largest weight**, so
the effect is measured rather than invisible.

## 7. The two readings and the margin

Let `Sel_static` be the `T` selected entries from §6.

```
cov_static(N, a, seed)  = exact coverage of Sel_static
                        = ( sum of b(d) over d in Sel_static ) / N

share_top(k)            = ( sum of the k largest b(d) over ALL DPs
                            of the exact partition ) / N

margin(N, a, seed)      = share_top(T_sel) - cov_static
```

Note the asymmetry, and preserve it: `cov_static` ranges over the **pool's**
selected entries; `share_top` ranges over **all DPs of the exact partition**.

`cov_static` is a function of the `T` selected entries and is **independent of
`T_sel`**.

## 8. The feasibility rule

At a given `(N, a)`, over the pre-registered seeds:

```
k  = number of seeds with margin >= 0            (an exact integer)

G3-FEASIBLE    iff  k >= 20 of 25
G3-INFEASIBLE  otherwise
```

Additionally score the **seeds 1..5 subgroup** by the original rule,
`>= 4 of 5`, and report it **separately**. Never composite the 25-seed reading
and the 5-seed subgroup reading into one number.

Also report, per `(N, a)`: the **mean margin over the 25 seeds and its sign**.
The pass-count `k` and the sign of the mean margin are the only two quantities
on which independent readings are compared; both are exact and
resampling-free.

## 9. What is *not* expected to match another implementation

Stated so you do not chase a false defect:

- Your `mix64`, and therefore your concrete functional graph at a given seed,
  will differ from any other implementation's. **Per-seed coincidence of
  margins is not expected and its absence is not a disagreement.**
- Your pool-insertion order and tie-break key stream will differ, so your
  `Sel_static` may differ at the `T`-th weight.
- What *is* compared across implementations is the pass-count `k` and the sign
  of the mean margin, over 25 seeds.

## 10. Parameters — the complete grid

```
N        in { 2^20, 2^24 }
T        = 64   at N = 2^20        (from a frozen table; NOT round(N^(1/3)),
           256  at N = 2^24         which would give 102 at N = 2^20)
T_sel    = T/2  = 32 at N = 2^20, = 128 at N = 2^24
r        = 2
a        in { 1/16, 1/8, 3/16, 1/4 }
seeds    = 1, 2, ..., 25   (the same 25 integers at every cell)
```

Derived, so you can check your own arithmetic — every row follows from
`W = sqrt(a*N/T)` and `cap = ceil(8*W)`:

| N | T | a | W | cap |
|---|---|---|---|---|
| 2^20 | 64 | 1/16 | 32 | 256 |
| 2^20 | 64 | 1/8 | 45.254833996… | 363 |
| 2^20 | 64 | 3/16 | 55.425625842… | 444 |
| 2^20 | 64 | 1/4 | 64 | 512 |
| 2^24 | 256 | 1/16 | 64 | 512 |
| 2^24 | 256 | 1/8 | 90.509667992… | 725 |
| 2^24 | 256 | 3/16 | 110.851251684… | 887 |
| 2^24 | 256 | 1/4 | 128 | 1024 |

The binding definition is the formula, never the printed decimal.

**Run `N = 2^20` first.** It is roughly 16x cheaper and shakes out a pipeline
defect before the expensive scale.

## 11. The interval estimator — it routes, it does not decide

No verdict and no comparison in §8 depends on a bootstrap. Compute an interval
anyway, to the following exact specification, because one downstream label
depends on whether it straddles zero:

```
method     percentile bootstrap  (NOT BCa, NOT basic, NOT studentised)
statistic  the mean over seeds of the per-seed margin at that (N, a) cell
resample   i.i.d. with replacement over the 25 per-seed margins;
           the SEED is the resampling unit
B          10000 resamples
rng        seeded as  20260907 + 1000*n_bits + round(10000*a),
           constructed FRESH per cell so a cell's interval does not depend
           on the order cells were processed in
endpoints  the 2.5th and 97.5th percentiles of the B resample means,
           by linear interpolation between order statistics
```

You may additionally report a BCa interval as context; nothing depends on it,
and you must record which variant you used if you do.

## 12. The control arms

Read all of these off the **same** exact basin partition. None is an online
algorithm.

**NULL-ORACLE-RAND (uniform).** Replace the `share_top(T_sel)` side by the
exact coverage of a **uniformly random `T_sel`-subset of the DPs of the same
enumerated partition**. Hold `cov_static` fixed and read the random subset's
coverage off the same basin-size array by the same arithmetic. Report
`margin_null = (random subset's coverage) - cov_static` per seed. One
substitution, same universe, same read-off.

**NULL-ORACLE-RAND (size-biased).** The same, but drawing the `T_sel`-subset
with probability proportional to basin size. Report it; nothing depends on it.

**NULL-RANDSEL.** Replace the `weight_d` selection by a uniformly random
`T`-subset of the `r*T` **pool**, and compare `share_top(T_sel)` against that
random selection's exact coverage.

**NULL-SHUF.** Permute the basin sizes across the pool's DPs, holding the size
multiset and the weights fixed, and report the resulting `cov_static`.

**DECAY readings.** Report the mean margin at each `a`, per scale, so
monotonicity in `a` can be checked. Report `share_top(T/4)` and
`share_top(T/8)` and `rho_ORACLE` (the smallest `T_sel/T` at which
`share_top(T_sel)` reaches `cov_static`) per cell.

## 13. The one thing you are told about an outcome, and why

**`T_sel = T/2` at `a = 1/4`, `r = 2`, `N = 2^24` records G3-INFEASIBILITY at
strength `preliminary`**, on one execution batch, with no independent
implementation (evidence record `EV-ECDLP-60e266`).

This is a **known-false object**, and it is the batch's replication control:
"controls before belief" requires the identical measurement be run against an
object whose answer is known, and you cannot run that control without being
told which object it is. **Compute and report the `a = 1/4` cell FIRST.** If
your `a = 1/4` reading comes out G3-FEASIBLE, the instrument — not the
hypothesis — is in question, and you should say so plainly rather than
continue.

This packet states **nothing** about `a = 1/16`, `a = 1/8` or `a = 3/16` at
either scale: no verdict, no expectation, no pass-count, no margin, no share,
no coverage, no interval, no crossing bracket. Those cells are what you are
measuring.
