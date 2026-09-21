# Repair report — v2 amendment to `EXP-HQC-982268`

**Task** `TASK-20260806-dbadc8` (executor) · **Batch** `BATCH-c5703d` ·
**Goal** `GOAL-HQC-001` · **Question** `RQ-HQC-001`
**Authorized by** `DEC-20260806-9d8aab` · **Repairs** the four defects recorded in
`EV-HQC-75c05b`, plus the oracle gate
**Produced** 2026-08-06

---

## 0. What this is, and the two boundaries I did not cross

This task designed and calibrated a **versioned amendment proposal**. It ran no
measurement arm and amended nothing.

**Claim tier is TOY and I do not move it.** Nothing below is a statement about
HQC, about assumption A17 or A5, about any decoding-failure rate, or about any
standardized HQC parameter set. Every number here is about an *instrument*. A
repaired instrument is not a result.

**Boundary 1 — the approved contract is untouched.**
`experiments/EXP-HQC-982268/specification.yaml` was read and not written. The
proposal lives entirely in `amendment_v2.yaml` in this task directory, and it is
inert until a Coordinator ledger archive commits it. Version 1 binds in full
until then, *including its unrepaired `INV-NULL`*.

**Boundary 2 — no `log2_A_k` on any (T) arm, and one place that cost something.**
Every joint-moment number in `calibration_results.json` is computed on a
synthetic law drawn under an explicit null or an explicitly declared
alternative. No HQC object was constructed: no ring, no fixed-weight sampler, no
truncation, no Reed–Muller decoder. The (T) arms contributed **first moments
only** — `q̂` and the per-block failure counts, both chartered Stage-A
diagnostics already published in `RUN-HQC-982268-STAGEA-a`.

The place it cost something is `R2`. The natural reference constant for the new
control is `E[Q] = (n_e−1)(1 − c/v)` with `c = Cov(F_j, F_j′)`, and on `{0..n_e}`

```
A_2  =  [ Var(S) + (n_e q)² − n_e q ] / ( 2·C(n_e,2)·q² )
```

so evaluating `c` on a (T) histogram **would be** the `k = 2` measurement. I did
not compute it. The control's demonstration below therefore runs against an
independent-blocks reference and is reported as a **can-fail sensitivity
demonstration, not a pass/fail verdict** on the Stage-A data. The exact
reference is a Stage-B trial bootstrap, which needs no knowledge of `c` at all.
This is `OPEN-8` in the amendment: the committed run record already contains the
sufficient statistic of a measurement Stage A was not authorized to take.

**Budget.** 816.3 core-seconds of 1200 authorized, across five executions
(12.7 + 16.1 + 88.3 + 315.1 + 384.1). Peak RSS 223 MB of 2 GB.
`calibration_results.json` is the output of the last run; phases 0–8 consume the
RNG before phase 9 was appended, so their values are bit-identical between the
last two runs and I verified that on the headline numbers. Nothing was truncated
and no result here is a budget artifact.

**The method that made this affordable, stated because it is load-bearing.**
Every statistic in the contract's null arms is a function of the histogram of `S`
over `n_e+1` bins (and, for the jackknife, of `B = 200` per-batch histograms).
For `T` i.i.d. trials with `S ~ Bin(n_e, q)`, that histogram is *exactly*
`Multinomial(T, pmf)`. So a null replicate at `T = 10⁸` costs one multinomial
draw over `n_e+1` categories rather than 10⁸ trials. **The calibration is exact
in distribution and O(1) in `T`.** That is why sizing a rule at the full Stage-B
allocation costs seconds, and it is why there was never a good reason for this
rule to go unsized.

**Self-test first.** The sizes below are sizes of `stage_a.py`'s *own* rule. My
vectorised re-implementation was checked against
`stage_a.log2_A_from_hist` / `stage_a.jackknife_log2_A` over 30 comparisons:
max difference **0.0** on the point estimate, **2.1e−16** on the SE.

---

## R1 — recalibrate `INV-NULL`. **DONE, with a measured size.**

### R1.1 The current rule, sized

20,000 replicates per cell of `S ~ Bin(n_e, q̂)` at the arm's own achieved `T`,
pushed through `stage_a.jackknife_log2_A`. Nominal size 0.27 %.

| set / arm | `T` | `k` | measured size | 95 % CI | × nominal |
|---|---|---|---|---|---|
| PS-A NULL-M | 662 268 | 2 | 0.31 % | [0.24, 0.40] | 1.1 |
| PS-A NULL-M | 662 268 | 3 | 3.37 % | [2.47, 4.59] | 12.5 |
| PS-R1 NULL-M | 497 632 | 2 | 0.30 % | | 1.1 |
| PS-R1 NULL-M | 497 632 | 6 | 0.30 % | | 1.1 |
| PS-R1 NULL-M | 497 632 | 9 | 0.34 % | | 1.2 |
| PS-R1 NULL-M | 497 632 | 11 | 0.89 % | [0.76, 1.02] | 3.3 |
| PS-R1 NULL-M | 497 632 | 14 | 3.91 % | | 14.5 |
| **PS-R1 NULL-M** | 497 632 | **16 = m** | **8.69 %** | [8.30, 9.08] | **32.2** |
| PS-R1 NULL-M | 497 632 | 18 | 11.08 % | | 41.0 |
| PS-R3 NULL-M | 385 732 | 2 | 0.33 % | | 1.2 |
| PS-R3 NULL-M | 385 732 | 10 | 0.34 % | | 1.3 |
| **PS-R3 NULL-M** | 385 732 | **17 = m** | **1.71 %** | [1.54, 1.90] | **6.4** |
| PS-R3 NULL-M | 385 732 | 22 | 9.93 % | | 36.8 |
| PS-R3 NULL-M | 385 732 | 25 | 23.55 % | | 87.2 |
| PS-R5 NULL-M | 239 896 | 2 | 0.32 % | | 1.2 |
| PS-R5 NULL-M | 239 896 | 15 | 0.32 % | | 1.2 |
| **PS-R5 NULL-M** | 239 896 | **30 = m** | **7.76 %** | [7.40, 8.14] | **28.8** |
| PS-R5 NULL-M | 239 896 | 35 | 18.00 % | | 66.7 |

This **replicates the red team's `OBJ-2`** at 67× their sample size. Their point
estimates and mine agree at every cell except one: PS-R5 `k = 30`, where they
measured 12.7 % (38/300) and I measure 7.76 % [7.40, 8.14]. Their estimate falls
outside my interval, so the two are **not reconciled as Monte-Carlo noise**. It
changes no conclusion — both are 29–47× nominal — but it is an unexplained
discrepancy between two independent measurements and I have recorded it as
`OPEN-7` rather than averaging it away. `EV-HQC-75c05b` listed the red team's
300-draw estimate as an unreplicated confound; that confound is now retired at
every cell but this one.

### R1.2 The finding the reviews did not have: the mis-sizing survives to Stage B

The red team measured 0/20 firings at `T = 10⁸`, `k = 16` and correctly declined
to conclude anything from it. Sized properly at the **contracted allocations**:

| set | `T` | `k = m` | measured size | × nominal |
|---|---|---|---|---|
| PS-R1 | 1e8 | 16 | **1.44 %** [1.18, 1.76] | 5.3 |
| PS-R3 | 2e7 | 17 | 0.45 % [0.32, 0.64] | 1.7 |
| PS-R5 | 2e7 | 30 | **2.34 %** [2.00, 2.73] | 8.7 |

**The falsification criterion is still 5–9× over-sized at two of the three sets
at the allocation the contract actually funds.** The skew abates with `T`; it does
not abate enough. This is the forward-looking half of `OBJ-2` and nobody had
measured it.

### R1.3 Is a Wald ratio the right shape here? **No, for two measured reasons.**

**(1) Coupling.** The correlation between `|log2 Â_k − mean|` and its own
`SE_jack`, under the exact null:

| set | `k` = 6 / 9 / 11 / 14 / 16 |
|---|---|
| PS-R1 (Stage-A `T`) | +0.006 / +0.091 / +0.297 / +0.585 / **+0.610** |
| PS-R3 (`k` = 10 / 17 / 22 / 25) | +0.031 / +0.501 / +0.643 / +0.616 |
| PS-R5 (`k` = 15 / 30 / 35) | +0.043 / **+0.694** / +0.673 |

A Wald ratio assumes the denominator carries no information about the numerator.
Here they are driven by the same handful of large-`S` trials. The coupling
**persists at Stage-B `T`**: +0.608 at PS-R1 `k=16`, `T=1e8`; +0.618 at PS-R5
`k=30`, `T=2e7`. This is the mechanism the red team identified, now measured
directly rather than inferred.

**(2) Shape, which is the deeper problem.** The null distribution of
`log2 Â_k` is strongly right-skewed at high `k`, so **any symmetric rule is
mis-shaped regardless of scale**. At the contract allocations the calibrated
interval's right arm exceeds its left arm by a factor of **2.35** (PS-R1 `k=16`),
**2.66** (PS-R5 `k=30`) and 1.26 (PS-R3 `k=17`) — and at PS-A `k=3` the asymmetry
runs the *other* way (0.75). The shape is cell-specific and not predictable a
priori. That is the argument for measuring it rather than assuming it.

Worth stating for balance: at `k ≤ 10` the Wald rule is **well sized**
(0.18 %–0.34 %) and the calibrated interval is near-symmetric at `z = ±3.0`. The
defect is confined to high `k` — which is exactly where `k = m` sits at PS-R1
and PS-R5.

### R1.4 The replacement, and why it is still pre-registration

`INV-NULL` v2 fires when `log2 Â_k` lies outside a frozen interval
`[c_lo, c_hi]`, the equal-tailed 0.135 %/99.865 % quantiles of the estimator's
**own** null sampling distribution at that `(n_e, q̂, T, batching)`. **No
jackknife. No Wald ratio. No division by a random quantity.**

The calibration null is `S ~ Bin(n_e, q̂)`, and **this is not a modelling
approximation**. On `{0..n_e}` the factorial moments `E[C(S,k)]`, `k = 0..n_e`,
determine the pmf by a triangular linear system, so "`A_k = 1` for every `k`"
pins every factorial moment to the binomial value and therefore pins the law.
Verified by inverting that system at `(n_e,q) = (10,0.3), (12,0.07), (8,0.55)`:
max `|pmf reconstructed − Bin|` = **7.5e−15**. A17's full content and the
binomial null are the same object. *Caveat, stated:* the contract measures
`k ≤ k_max < n_e`, so a rule calibrated this way tests a **sub-family** of A17.
The reference law is exact; the coverage is partial.

Pre-registration survives because the calibration consumes only
`(n_e, q̂, T, batching)`. `q̂` is a committed Stage-A diagnostic and `T` is fixed
before Stage B by `ST-7`, so `[c_lo, c_hi]` is **frozen in the amendment now**,
before any Stage-B (T) datum exists. The dependence on the data is through `q̂`
alone, and it is negligible: shifting `q̂` by ±3 SE moves the bounds by at most
~2 % of the interval width at every `k = m` cell.

### R1.5 The measured size of the replacement

Critical values from 1,000,000 calibration draws; size measured **out of sample**
on 1,000,000 independent draws.

**0.252 % – 0.290 % at every one of the 30 evaluable cells tested**, against
0.270 % nominal, with 95 % CIs about ±0.010 percentage points wide. Worst cell:
PS-R1 `k=14`, `T=1e8`, 0.290 % [0.280, 0.301]. Full table in
`calibration_results.json → phase3_proposed_rule`; the frozen constants are
transcribed into `amendment_v2.yaml`.

The v2 rule also carries a standing run-time obligation the v1 rule lacked: the
size **must** be re-measured out of sample at run time and recorded per cell, and
a cell whose measured size leaves `[0.002, 0.004]` is reported as CALIBRATION
FAILED with its (T) result withheld.

### R1.6 Two things that fell out and matter

**The advertised resolutions are wrong in shape, not only in scale.**

| set | `k` | contract advertised | measured calibrated interval |
|---|---|---|---|
| PS-R1 | 16 | ±0.096 | **−0.148 / +0.348** |
| PS-R3 | 17 | ±0.024 | **−0.040 / +0.051** |
| PS-R5 | 30 | ±0.078 | **−0.131 / +0.349** |
| PS-A | 2 | ±0.028 | −0.041 / +0.040 |
| PS-A | 3 | ±0.32 | **−0.696 / +0.520** |

**PS-A `k = 3` at Stage-A `T` is worse than "noisy" — it is degenerate.** Only
1 127 of 20 000 null replicates are even *defined*, and when defined the null
**mean** of `log2 Â_3` is **+2.4704 bits**. At the allocated `T = 1e8` it
recovers (all 10⁶ replicates defined, interval −0.696/+0.520), so the contract's
allocation rescues it — but the v1 rule would have read a +2.5-bit estimator
artifact as signal at any smaller `T`, and nothing in v1 would have caught it.
`PS-A k = 4` remains out of reach even at `T = 1e8` (81.7 % of null replicates
undefined) and is declared NOT REACHED.

---

## R2 — replace `CTRL-BS`. **DONE. New control designed, forced value declared, sensitivity measured.**

### R2.1 The demotion, and the structural fact stated in the contract

I confirmed the red team's structural claim against the source:
`stage_a.py` line ~1116 builds the pseudo-sample as
`Fb[:, j] = np.roll(F[:, j], -off[j])`. A cyclic roll is a **permutation of a
column**, so every per-block column sum is preserved *exactly*, hence
`q̂^BS ≡ q̂^T` identically (verified on the committed histograms: 8 122/8 122,
5 200 049/5 200 049, 9 159 668/9 159 668, 13 187 613/13 187 613).

The consequence the amendment now states plainly: **both the numerator and the
denominator of `Â_k^BS` are built from the same indicator matrix `F`**, so a
wrong `F` — from a broken sampler, ring product, truncation or decoder — enters
the control and the thing it controls identically, and cancels. It fired 0 of
108 cells with `|z|` never above 1.67.

v1 justified `PRIMARY` on the grounds that CTRL-BS matches "the EXACT true
marginal block-failure law — not a modelled marginal". The premise is true and
the conclusion is backwards: matching the (T) arm's own marginal *exactly* is
what makes the arm non-independent, not what makes it strong.

`CTRL-BS` → **tertiary re-indexing control**. `NULL-M` → **PRIMARY null object**
(only arm exercising the decoder; `A_k = 1` is a theorem; reached `|z| = 8.39`;
carries `D1`'s positive control at `γ̂ = 1.00034–1.00446`).

### R2.2 The new control: `CTRL-POSHOM`

**Forced value, declared analytically — this is a theorem, derived before any
number was computed, not a fit to data.**

`e'' = x·r₂ + r₁·y + e` in `R = F₂[X]/(Xⁿ−1)`. For every `s ∈ Z_n` the map
`v ↦ X^s v` is a bijection of each fixed-weight set, and
`(X^s x, X^s y, X^s e, r₁, r₂)` has the same joint law as `(x, y, e, r₁, r₂)`.
Hence **`X^s e''` has the same law as `e''`, exactly, for every `s`.** Block `j`
occupies coordinates `[jL, (j+1)L)` with `L = n₂·dup`, and `n_e·L = N < n`, so
the block-`j` window is the block-0 window shifted by the legal ring shift
`s = jL`. Two exact population consequences follow, and they are the forced
values:

- **Clause (a)** `E[F_j] = q` for every block `j`. *(first moment)*
- **Clause (b)** `P[F_j = F_{j+d} = 1]` depends only on `d`, never on `j`, for
  every pair with `0 ≤ j < j+d < n_e`. *(second moment — this clause touches the
  joint law)*

**Why it can fail where `CTRL-BS` cannot.** It is evaluated on the (T) indicator
matrix itself and its forced value is a property of the **upstream** path — ring
product, truncation window, block partition, `dup` folding, decoder indexing.
And `CTRL-BS`'s `np.roll` destroys the `(j, j+d)` pairing entirely, so a CTRL-BS
pseudo-sample satisfies clause (b) trivially: **clause (b) is a (T)-arm-only
check by construction.**

**Observations that would break it**, named as required:

- an off-by-one truncation window → block 0 or block `n_e−1` is special;
- a wrong ring modulus `n`, or a wrap-around error in the sparse shift-XOR near
  the `n − N` gap → blocks adjacent to the wrap are special;
- a `dup`-folding stride error → at PS-A (`dup = 3`, `n₂ = 384`) specific blocks
  are special;
- a decoder or WHT indexing bug that treats one block position differently.

Each appears as an offset-dependent `q` (clause a) or a position-dependent pair
moment (clause b), neither of which a correct instrument can produce.

**What it cannot detect, stated plainly.** A **position-equivariant** defect — a
wrong decoder or truncation applied identically at every block — passes
`CTRL-POSHOM`. That residual is covered, imperfectly, by `CTRL-DEC`,
`CTRL-REPLAY`, `D2`, and `BASE-TABLE10`. This control does **not** close the gap
the Stage-A report itself named — that no null arm tests the (T) joint law
against a known answer — and it is not claimed to. That gap is `OPEN-6`.

### R2.3 Measured sensitivity — the control demonstrably can fail

Power to detect a single block whose marginal is biased by the stated relative
amount, against an independent-blocks reference (see §0 for why that reference
and not the exact one):

| set | at Stage-A `T` | | | at Stage-B `T` | | |
|---|---|---|---|---|---|---|
| | 1 % | 2 % | 5 % | 0.2 % | 2 % | 5 % |
| PS-A | 0.002 | 0.003 | 0.004 | 0.002 | 0.075 | **0.998** |
| PS-R1 | 0.083 | **0.923** | 1.000 | **1.000** | 1.000 | 1.000 |
| PS-R3 | 0.223 | **0.999** | 1.000 | 0.560 | 1.000 | 1.000 |
| PS-R5 | 0.153 | **0.994** | 1.000 | 0.748 | 1.000 | 1.000 |

At the Stage-B allocations the control detects **sub-1 % single-block marginal
defects at PS-R1, PS-R3 and PS-R5**, and ~5 % at PS-A. At Stage-A `T` it is
**essentially blind at PS-A** (20 % bias → power 0.029), because PS-A has only
8 122 block failures in total; that is stated rather than smoothed.

Observed `Q/(n_e−1)` on the committed Stage-A first moments: 1.239 / 1.042 /
0.888 / 0.891, none exceeding the independent-blocks critical value. **Per §0
this is not a verdict** — the correctly scaled reference needs the (T) second
moment. Clause (b) could not be evaluated at all, because
`RUN-HQC-982268-STAGEA-a` did not record pairwise-by-position counts; the
amendment adds `pair_counts_by_position.csv` as a required artifact.

---

## R3 — restate `D3`. **DONE. And the honest answer on a real (T)-vs-(M) discriminator is: `D1` already is one, and no better hard invariant is available.**

### R3.1 `D3` cannot fire on (M)

On (M), `w(ẽ) ~ Bin(N, p̂)`. The cap in (M) standard deviations above the (M)
mean:

| set | `N` | cap | (M) mean | (M) sd | cap − mean, in (M)σ | max `w` seen on (T) |
|---|---|---|---|---|---|---|
| PS-A | 17 664 | 9 975 | 6 002.03 | 62.95 | **63.11** | 6 254 |
| PS-R1 | 5 888 | 3 476 | 2 048.52 | 36.55 | **39.06** | 2 202 |
| PS-R3 | 7 168 | 4 641 | 2 615.92 | 40.76 | **49.68** | 2 782 |
| PS-R5 | 11 520 | 7 973 | 4 333.69 | 51.99 | **69.99** | 4 549 |

An (M) sampler violates the cap with probability of order 10⁻³³¹ to 10⁻¹⁰⁶⁴.
**`D3` cannot fire on (M) at any reachable `T`.** v1's parenthetical "(a hard
support cap on (T), violated with probability ~1 on (M))" is struck, as is the
`why_this_matters` clause listing `D3` among the invariants "that cannot be
satisfied by an (M) sampler". `D3` becomes what it is: a **hard support
invariant**, `INV-INVARIANT` only, worth keeping because it catches a broken ring
product or truncation instantly at zero cost.

### R3.2 A real discriminator — yes, and it is already in the contract

**`D1` is the discriminator. No new detector is needed and none I could design
beats it.** `γ̂ = Var(w(ẽ))/(N p̂ (1−p̂))` is exactly 1 on (M) — a theorem — and
the measured (T) values sit **79–135 SE** away, with a genuine positive control:

| set | `γ̂` on (T) | SE | separation from 1 | `γ̂` on NULL-M |
|---|---|---|---|---|
| PS-A | 0.73642 | 0.00195 | **135.4 SE** | 1.000341 |
| PS-R1 | 0.75316 | 0.00187 | **132.1 SE** | 1.004460 |
| PS-R3 | 0.79031 | 0.00198 | **106.0 SE** | 0.998680 |
| PS-R5 | 0.81273 | 0.00238 | **78.8 SE** | 1.000812 |

**The generalizable lesson, which is the part worth keeping.** A discriminator
must **force the side it is trying to rule out**, and the alternative must
actually violate that forced value. `D1` forces the (M) side (`γ = 1` exactly on
(M)) and the (T) value sits 79–135 SE away, so it fires. `D3` forces the (T)
side (the cap holds with probability 1 on (T)) and the (M) alternative sits
39–70 (M)σ *inside* it, so it cannot. Both are correct statements; only one is a
detector.

Related, and it explains why the cap was always the wrong shape: the (T) and (M)
laws of `w(ẽ)` have nearly the **same mean by construction** — `p̂` matches the
analytic `p*` to 5.2e−7–1.5e−5, and `p*` is a deterministic function of
`(n, ω, ω_r, ω_e, N)` that the sampler realizes by construction. The largest
`w(ẽ)` observed on (T) sits only **4.0–4.2 (M)σ** above the (M) mean at all four
sets. **The two laws differ in dispersion, not in location.** Any location-based
detector is the wrong shape, and a support cap is the most extreme
location-based detector there is.

### R3.3 What I could not design, said plainly

**There is no cheap deterministic (probability-1) (T)-vs-(M) discriminator
available here, and I am reporting that as the answer rather than padding it.**
The support cap is the only easy deterministic (T) invariant and it is far too
slack. A sharp one would have to test membership in the sumset
`{Σ of ω shifts of r₂} + {Σ of ω_r shifts of y} + {weight-ω_e vectors}`, which is
a hard combinatorial problem, not a detector. So the discriminating power in this
contract is carried by a **soft** statistic with a measured positive control and
a 79–135 SE separation, and the amendment says that instead of dressing it up as
a hard invariant.

One optional strengthening is proposed and explicitly not required: `D6`, the
lag-resolved coordinate autocorrelation `A(ℓ)`, which by ring-shift invariance is
a genuine function of `ℓ` alone and is forced to exactly `p²` on (M). `D1` is
already the aggregate of exactly this
(`Var(w) ≈ N p(1−p) + N Σ_{ℓ≠0}(A(ℓ)−p²)`), so `D6` buys **diagnostic detail,
not extra separation**. The Coordinator should feel free to decline it.

---

## R4 — re-derive the allocations. **DONE, with the arithmetic and a cost/resolution table.**

### R4.1 The arithmetic, at the measured `q̂`

Contract's own rule: `s_90 = min{s : Σ_{s'≤s} P[S=s']·C(s',k) ≥ 0.90·E[C(S,k)]}`,
`T_stab = 30 / P[S ≥ s_90]`, `S ~ Bin(n_e, q̂)`. This reproduces the committed
`k_max_sizing` block and the red team's `OBJ-1` table exactly.

| set | `q̂` measured | (contract `q_for_sizing`) | `m` | `s_90` | `T_stab(m)` | allocated `T` | verdict | `k_max` @ alloc |
|---|---|---|---|---|---|---|---|---|
| PS-A | 0.00033445 | 0.0004993 | 16 | 16 | 1.246e45 | 1e8 | infeasible (already declared) | **3** |
| **PS-R1** | 0.19742737 | 0.2306 | 16 | 25 | **1.452e8** | 1e8 | **short by 1.452×** | **15** |
| PS-R3 | 0.31994629 | 0.3704 | 17 | 33 | **1.000e6** | 2e7 | **20× margin** | 20 |
| **PS-R5** | 0.41412035 | 0.473 | 30 | 60 | **2.554e7** | 2e7 | **short by 1.277×** | **29** |

The contract's frozen `T_req(PS-R1, 16) = 2.91e7` "against `T = 1e8`, margin
3.4×" was computed at the modelled `q = 0.2306`. The measured `q̂` is 14.4 %
lower and `T_stab` is violently non-linear in `q`, so the margin does not shrink
to 2.9× — **it inverts to 0.69×**. `ST-4` is triggered. PS-A `k = 3` also rises
3.3× (1.61e7 → 5.34e7) and survives only because PS-A's allocation is 1e8.

### R4.2 A correction to `OBJ-3` that changes the repair

`OBJ-3` concluded the contract's variance formula `V(n_e,q,k)` understates the
null variance by 5.4×. **Measured here, the formula is fine; the tabulated
numbers used the wrong `q`.** Measured null SD against `SE = √(V/T)/ln2`
evaluated at the **measured** `q̂`, 20 000 replicates per cell:

| set | `k` | `T` | measured SD | formula at measured `q̂` | ratio | contract tabulated | tabulated understates by |
|---|---|---|---|---|---|---|---|
| PS-R1 | 16 | 1e8 | 0.06457 | 0.06616 | 0.976 | 0.0321 | 2.01× |
| PS-R3 | 17 | 2e7 | 0.01427 | 0.01442 | 0.990 | 0.008 | 1.78× |
| PS-R5 | 30 | 2e7 | 0.06036 | 0.06461 | 0.934 | 0.0259 | 2.33× |
| PS-A | 3 | 1e8 | 0.19822 | 0.19556 | 1.014 | 0.108 | 1.84× |

The formula's functional form is validated to 1–7 %. `OBJ-3`'s diagnosis says
*replace the variance formula*; this one says *recompute the same formula at the
measured `q̂`*. The magnitude of the `T_prec` correction is similar (3.2×–5.4×,
since `T_prec ∝ V`) but **the repair is different, and repairing the wrong thing
would leave the real defect in place.** The red team's own SD estimate (0.0744,
`R = 20`, stated at ±16 % relative) is consistent with 0.06457 at 20 000
replicates, which supersedes it.

Residual caveat: a symmetric SE is the wrong object at these cells *whatever* `q`
it is computed at, because the null distribution is skewed. The binding width is
the calibrated interval from R1.

### R4.3 Success criterion (iv), restated

v1's (iv) requires `log2 Â_m` at **PS-R1, PS-R3 and PS-R5**. Two of the three
cannot deliver it at their allocations. It is unsatisfiable by arithmetic, not by
outcome.

**v2 (iv):** report `log2 Â_m` with its frozen calibrated interval at **PS-R3**
(`m = 17`), and `log2 Â_2`, `log2 Â_3` at PS-A. At PS-R1 and PS-R5, report the
reachable `k_max` and report `k = m` as **NOT REACHED** under `ST-4` — a budget
outcome, never a null result — *unless* the Coordinator funds
`T ≥ T_stab(m)` at the measured `q̂`.

### R4.4 Cost, resolution and power — the table the Coordinator needs

Core-seconds at the **measured** throughput (1 502–2 555 trials/core-second,
1.9×–3.1× below the modelled 4 728). `MDE80` is the 80 %-power effect size
against **one declared alternative family** (the two-point common-mode mixture at
`ε = 0.05`, the `M+` mechanism the contract already names). *A different
mechanism at the same `|log2 A_m|` can give different power; this is not a
general sensitivity claim.*

| set | `k` | `T` | core-s | calibrated interval | measured size | `MDE80` |
|---|---|---|---|---|---|---|
| **PS-R3** | 17 | 1e6 | **485** | −0.158 / +0.294 | 0.274 % | 0.355 |
| **PS-R3** | 17 | 5e6 | **2 426** | −0.077 / +0.114 | 0.254 % | 0.165 |
| **PS-R3** | 17 | **1e7** | **4 852** | **−0.055 / +0.075** | 0.269 % | **0.092** |
| **PS-R3** | 17 | 2e7 | 9 705 | −0.040 / +0.051 | 0.257 % | **0.077** |
| PS-R1 | 16 | 1e8 | 39 135 | −0.148 / +0.348 | 0.247 % | 0.427 |
| PS-R1 | 16 | 1.452e8 | 56 823 | −0.127 / +0.273 | 0.260 % | 0.345 |
| PS-R1 | 16 | 1e9 | 391 346 | −0.054 / +0.088 | 0.267 % | 0.127 |
| PS-R5 | 30 | 2e7 | 13 318 | −0.132 / +0.373 | 0.231 % | 0.557 |
| PS-R5 | 30 | 2.554e7 | 17 007 | −0.119 / +0.323 | 0.276 % | 0.362 |
| PS-R5 | 30 | 1e8 | 66 590 | −0.067 / +0.152 | 0.286 % | 0.176 |
| PS-A | 3 | 1e8 | 60 005 | −0.693 / +0.515 | 0.307 % | 0.688 |

**What this settles.** PS-R3 at `k = m` **dominates every other arm on both axes
at once**, and this needs no interpolation to state:

- PS-R3 at `T = 1e7` costs **4 852** core-seconds and reaches `MDE80 = 0.092`;
- PS-R1 at `T = 1e9` costs **391 346** core-seconds and reaches only `0.127`;
- PS-R5 at `T = 1e8` costs **66 590** core-seconds and reaches only `0.176`.

So PS-R3 buys a **strictly better** detectable effect at **1/81** of PS-R1's
cost and **1/14** of PS-R5's. On the scale-invariant figure of merit
`core-seconds × MDE80²` (invariant because `MDE ∝ T^−½` and cost `∝ T`) the arms
sit at **41** (PS-R3 `T=1e7`), 2 058 (PS-R5 `T=1e8`), 6 284 (PS-R1 `T=1e9`) and
28 380 (PS-A `k=3`, `T=1e8`) — nearly three orders of magnitude.

`T = 1e7` at PS-R3 is **half** the contract allocation, about 1 213 wall-seconds
on this host's 4 cores, with a calibrated interval of −0.055/+0.075.
`DEC-20260806-5289fb` ranked B3 next on cost alone; it is now correct on
measurement as well.

**What is lost, and is not hidden.** PS-R1 is the **only** order-matched arm at
HQC-1's shape (same `n_e = 46`, same `m = 16`). Anchoring (iv) on PS-R3 anchors
it on HQC-3's shape. That is a real narrowing of scope and must appear in every
downstream record, not only here. `ST-3`'s rule that PS-R1 is never cut is
retained: PS-R1 is not cut, it is reported at its reachable `k_max = 15`.

**Cost of the contract as written.** At measured throughput the four Stage-B
allocations cost **122 163 core-seconds** against the contract's modelled 53 080
— a factor **2.30**, at or past the declared 2× contingency. That number, not
the modelled one, is what the campaign budget has to absorb.

---

## R5 — promote the real oracle gate. **DONE as a specification change. Verified as machinery, NOT re-verified against the oracle.**

The v1 `ORACLE AGREEMENT` gate hashes three sibling files, re-runs `oracle.py`
and deep-diffs it against the JSON `oracle.py` itself produced, and runs
`oracle.py`'s own tests. **No value produced by `stage_a.py` enters the
comparison.** It is a chain-of-custody and reproducibility check carrying the
name of a cross-validation it does not perform.

`CTRL-ORACLE` v2 is now **mandatory and blocking**: take each oracle
configuration's exact rational `law_of_S`, multiply by the lcm of the
denominators to get exact integer pseudo-counts, feed the histogram to
`stage_a.log2_A_from_hist` — the same function the (T) analysis uses — and
compare against the exact rational `log2 A_k`. Required coverage: **≥ 40 cells,
of which ≥ 5 have `|log2 A_k| > 1` bit and ≥ 5 are negative.** Tolerance 1e−12
bits. That coverage clause is the whole point: the v1 instrument was calibrated
**only at the null point of a two-sided test whose entire purpose is detecting
departures from it.** The old phase is retained and renamed `ORACLE-PROVENANCE`;
it is a real check and it keeps its own gate row, but it may not be reported
under the name of an agreement check.

**Status, stated exactly.** The oracle package lives in
`BATCH-003/tasks/TASK-20260803-6f50df`, which is **outside this task's read
scope**. I neither read nor re-ran it. The passing measurement is the red team's
(`TASK-20260806-dd901b` §5: 40 cells, 13 configurations, max diff 1.2e−14,
including `+9.965784` and `−2.851453`), not mine. **R5 is a specification change
I wrote and could not independently confirm.**

What I *did* verify is the **gate machinery**, on exact rational laws constructed
inside `calibration.py`: 27 cells over 7 configurations, `log2 A_k` spanning
**−2.651 to +32.370 bits**, max difference **5.3e−15**. This establishes that the
lcm-scaling construction is exact and that the 1e−12 tolerance is achievable with
three orders of magnitude to spare. It establishes nothing about the oracle
package.

---

## Per-repair status

| | repair | status | what was measured | what remains unverified |
|---|---|---|---|---|
| **R1** | recalibrate `INV-NULL` | **DONE** | v1 size at 20 000 reps/cell across 18 Stage-A cells (0.30 %–23.55 %) and 8 Stage-B cells (0.18 %–2.34 %); v2 size out-of-sample at 10⁶ reps/cell across 30 cells (**0.252 %–0.290 %** vs 0.270 % nominal); Wald coupling +0.50…+0.69; interval asymmetry 0.75×–2.66× | the size of v2 **on the (T) arm's real S-law** if A17 fails — a calibrated interval is exact under the null and says nothing about behaviour under an alternative it was not sized against. Power is measured against **one** declared family only. |
| **R2** | replace `CTRL-BS` | **DONE (design + clause-a sensitivity)** | `np.roll` permutation confirmed in source; `Σ_t S_t` identical at all four sets; `CTRL-POSHOM` forced value derived as a theorem; detection power 0.92–1.00 at a 2 % single-block bias (Stage-A `T`), 0.56–1.00 at 0.2 % (Stage-B `T`) | **clause (b) is entirely unevaluated** — the pairwise-by-position counts do not exist in any committed run. The clause-(a) reference constant is **independent-blocks**, not exact; the exact one needs the (T) second moment, which determines `log2 A_2` and which this task refused to compute. Observed `Q` values are therefore **not a verdict**. |
| **R3** | restate `D3` | **DONE** | cap sits **39.1–70.0 (M)σ** above the (M) mean → cannot fire on (M); max `w` on (T) only 4.0–4.2 (M)σ above it → the laws differ in dispersion, not location; `D1` separates at **78.8–135.4 SE** with a working positive control | nothing new is claimed. `D6` is **proposed and unrun**. The negative answer — no cheap probability-1 (T)-vs-(M) discriminator exists here — is an argument, not a proof, and I did not attempt an exhaustive search of candidate invariants. |
| **R4** | re-derive allocations | **DONE** | `T_stab(m)` at measured `q̂`: **1.452e8 / 1.000e6 / 2.554e7** vs **1e8 / 2e7 / 2e7**; `k_max@alloc` = 3/15/20/29; contract SE tabulations understate by 1.78×–2.33× **because of `q`, not the formula** (formula validated to 1–7 %); full cost/resolution/power curve at 15 `(set, T)` points | `MDE80` is against **one** alternative family. The `T_stab` threshold constant 30 is inherited from v1 and is still "a judgement, not a theorem". Throughput is from **one** host and one Stage-A run; every core-second figure moves with it. |
| **R5** | promote the oracle gate | **DONE as specification; NOT re-verified** | gate machinery exact to **5.3e−15** over 27 cells spanning −2.651…+32.370 bits | **the gate was not run against the actual oracle package** — `BATCH-003` is outside this task's read scope. The passing 40-cell result is the red team's, cited not reproduced. The **end-to-end** `CTRL-ORACLE` (whole pipeline vs an exact instance) remains unbuilt: `stage_a.decode_blocks` is hard-wired to a size-128 WHT while the oracle's block models are `threshold(n2=4,t=1)` and RM(1,2). `OPEN-6`. |

### Two additional unresolved items, recorded not buried

- **`OPEN-7`** — v1's size at PS-R5 `k=30` measures **7.76 %** [7.40, 8.14] here
  against the red team's **12.7 %** (38/300). Their point estimate lies outside
  my interval, so the two are not reconciled as Monte-Carlo noise. No conclusion
  changes (both are 29×–47× nominal), but it is an unexplained disagreement
  between independent measurements.
- **`OPEN-8`** — `RUN-HQC-982268-STAGEA-a` archives the (T) arms' full `S`
  histograms as a chartered diagnostic, and `log2 A_2` is a two-line function of
  `Var(S)` computed from them. The `k = 2` measurement is therefore **recoverable
  from the committed record** even though Stage A was authorized to compute no
  (T) joint moment and correctly did not. This is a disclosure surface, not a
  violation — nothing was computed and nothing is claimed — and it is why this
  task declined to form `Var(S)` on any (T) histogram. It needs a Coordinator
  ruling, not a change to the immutable archive.

---

## What I did not do

- No measurement arm. No `log2_A_k` or `log2_A_m` on any (T) arm. No HQC object
  constructed at all — no ring, no fixed-weight sampler, no truncation, no
  decoder.
- No edit to `experiments/EXP-HQC-982268/specification.yaml`, to any ledger
  record, to any run artifact, to `BATCH-6fddee`, or to anything outside
  `.../BATCH-c5703d/tasks/TASK-20260806-dbadc8/`.
- No status transition, no hypothesis moved, no evidence or decision record
  written. `H-HQC-18d1b4` remains `proposed`.
- No reading of `BATCH-003` (outside read scope), which is why R5 is cited rather
  than reproduced.
- No claim that a repaired instrument tells anyone anything about HQC. It does
  not, and this batch was never going to.

*Executor record. Files written: `amendment_v2.yaml`, `calibration.py`,
`calibration_results.json`, `repair_report.md`, all under this task directory.
`PYTHONDONTWRITEBYTECODE` set so no `__pycache__` was left in the read-only
sibling directory.*
