# TASK-20260808-3a5f18 — Section C / AM-7: the matched-`V` comparison rebuilt with an SE that contains the variance it omitted

BATCH-cbe023 / GOAL-MLKEM-005. Executor artifact. **Observations only.**
No status change, no hypothesis movement, no evidence record, and no
interpretation beyond the declared outcomes of the frozen contract.

**Claim tier TOY, unconditionally.** Nothing in this report bears on ML-KEM
security, on any FIPS 203 parameter set, on any attack cost, or on any cost
model. `V`, `m3` and `D` are properties of a basis PRESENTATION, not of a
lattice, and no verdict here is offered as an AM-4 adjudicator.
`certificate.kind: none` — no discrete-log solve and no factor-base relation is
claimed or produced, so `docs/claims-and-verification.md` requires no solution
certificate. The independent re-verifications carried below are INSTRUMENT
CHECKS and are labelled as such, never as certificates.

---

## 0. Notarization — verified before anything ran

```
governing contract : coordination/goals/GOAL-MLKEM-005/batches/BATCH-cbe023/
                     tasks/TASK-20260808-35efa3/prereg.md   (section 4)
sha256 (quoted)    : 2da554914e5d78146c1e6cafcdbd109aacbc1a1624ed1f8e94ae769f757fc4f8
```

The digest was recomputed and compared against **six** sources, all of which
agree:

| source | sha256 |
|---|---|
| recomputed from the worktree file | `2da5549…fc8` |
| `prereg_sha256.txt` producer sidecar | `2da5549…fc8` |
| snapshot receipt `archive.path_sha256[prereg.md]` | `2da5549…fc8` |
| snapshot receipt `prereg_sha256` field | `2da5549…fc8` |
| the blob **inside** notarizing commit `4f7c63703` | `2da5549…fc8` |
| the value quoted in the dispatch task card | `2da5549…fc8` |

**Ancestry (correction V-7 — the notarizing commit ITSELF, never its parent):**

```
git merge-base --is-ancestor 4f7c63703d50445c758fc6216ca8d4436e04ae2a HEAD
```

asserted TRUE in this worktree at `HEAD = 100df18ae7b940b4e2881b95563725ec51665d84`
**before** the run and again at
`HEAD = c32b4b5dc22b8d81e8beef1d17996729c38ef01e` **after** it. The notarizing
commit `4f7c63703` PREDATES this task and this task did not modify `prereg.md`.

**One recorded defect in the run's own git bookkeeping, which changes no
measurement.** `measure_am7.py` computes `REPO_ROOT` five levels above the
`batches/` directory, which in this worktree resolves to
`/Volumes/SSD990/crypto-autoresearcher/.claude/worktrees` — the *enclosing*
checkout, not this worktree. So `results_am7.json.git.head_commit`
(`111d04124…`) is that checkout's HEAD at run time, not this worktree's, and
the in-script ancestry assertion (which returned TRUE) was made against it.
The assertion that the contract requires is the one quoted above, made
directly in this worktree, TRUE at both the pre-run and post-run HEAD. The
prereg blob comparison is unaffected because worktrees share one object
store, and it agrees. Recorded rather than corrected in place: the run record
is immutable.

---

## 1. What was rebuilt, against AM-7's three clauses

| AM-7 clause | what the superseded instrument did | what this run does |
|---|---|---|
| (1) the SE must contain the variance that dominates it | the TL frame was deterministic on ONE fixed coordinate support, so all 8 TL draws shared it and the SE was a between-frame dispersion over a single shared error pool | **both the support and the pairing are drawn afresh at every index** from `default_rng([5, d, beta, s])`; **E = 4 independent error pools per cell**; the SE comes from a **two-way random-effects decomposition** over `S = 8` supports × `E = 4` pools with Satterthwaite `nu_eff` |
| (2) a replicated null calibration that ESTIMATES a rate | none existed | **three nulls** (N-A, N-B, N-C), `R = 300` per cell for N-A and N-B in two cells, `R = 60` per cell for N-C, in **5 disjoint pool-quadruple clusters**, reported with a Wilson interval **and** a cluster bootstrap |
| (3) a relative-effect floor above the null's own median | `5%` | **`tau_rel = 0.15`**, frozen in the contract |

`V_TL` and `m3_TL` depend on `u` alone and not on the support or the pairing,
so independent supports do not break the `V`-matching. The achieved match is
reported per target below.

**BINDING CARRY, restated: BATCH-a44d08's Section C verdict is VOID IN BOTH
DIRECTIONS.** It is not cited, not reproduced as a baseline and not used as a
prior anywhere in this run, this script or this report. Neither "falsified"
nor "consistent" nor its non-firing pairs' floors exist for this run. This
run rebuilt the instrument; it did not re-score that output.

**BOUNDARY CARRY:** `Var(e^T P e) = 2 beta + (mu_4 - 3)(V + beta^2/d)` IS a
function of `V` alone, so L2's derivation is correct AT SECOND ORDER and
nothing here touches it. Only whether the `2^-10` tail quantile inherits that
was in question.

---

## 2. THE SE DECOMPOSITION — mandatory reporting (contract 4.3)

`SE^2(Delta_bar) = (MS_S + MS_P - MS_res)/(S·E)`, `S = 8`, `E = 4`,
`df = 7 / 3 / 21`, Satterthwaite `nu_eff`.

| cell | target | `MS_S` | `MS_P` | `MS_res` | `SE(Delta_bar)` | `nu_eff` | S% | P% | e% |
|---|---|---|---|---|---|---|---|---|---|
| d100_b30 | graded_t0.0025 | 3.7565e-05 | 9.8162e-06 | 2.1412e-05 | 9.008e-04 | 2.64 | 62.2 | -44.7 | 82.5 |
| d100_b30 | graded_t0.0050 | 3.9247e-05 | 7.7465e-06 | 1.6286e-05 | 9.796e-04 | 3.73 | 74.8 | -27.8 | 53.0 |
| d100_b30 | unreduced | 1.4188e-05 | 5.4866e-06 | 1.7605e-05 | 2.543e-04 | 1.00 | -165.2 | -585.7 | 850.8 |
| d100_b40 | graded_t0.0025 | 1.2452e-05 | 1.9922e-06 | 1.5801e-05 | 7.027e-04 | 21.00 | 246.9 | 1018.1 | -1165.0 |
| d100_b40 | graded_t0.0075 | 1.6415e-05 | 1.3343e-05 | 1.0964e-05 | 7.664e-04 | 3.41 | 29.0 | 12.7 | 58.3 |
| d100_b40 | unreduced | 1.5861e-05 | 4.0372e-06 | 1.1440e-05 | 5.141e-04 | 1.50 | 52.3 | -87.5 | 135.2 |
| d140_b30 | graded_t0.0025 | 3.1897e-05 | 3.1136e-05 | 1.9349e-05 | 1.168e-03 | 3.92 | 28.7 | 27.0 | 44.3 |
| d140_b40 | graded_t0.0025 | 1.2379e-05 | 2.0702e-05 | 1.7543e-05 | 6.968e-04 | 1.35 | -33.2 | 20.3 | 112.9 |
| d140_b40 | graded_t0.0050 | 2.3345e-05 | 9.7177e-06 | 1.2545e-05 | 8.007e-04 | 3.60 | 52.6 | -13.8 | 61.1 |
| d140_b40 | unreduced | 1.3910e-05 | 2.8650e-06 | 9.7220e-06 | 4.695e-04 | 1.43 | 59.4 | -97.2 | 137.8 |

The three variance components, in absolute units
(`sigma_S^2`, `sigma_P^2`, `sigma_e^2` = `MS_res`):

| cell | target | `sigma_S^2` | `sigma_P^2` | `sigma_e^2` | flagged NEGATIVE-VARIANCE-COMPONENT |
|---|---|---|---|---|---|
| d100_b30 | graded_t0.0025 | +4.0381e-06 | -1.4495e-06 | +2.1412e-05 | no |
| d100_b30 | graded_t0.0050 | +5.7402e-06 | -1.0675e-06 | +1.6286e-05 | no |
| d100_b30 | unreduced | -8.5435e-07 | -1.5148e-06 | +1.7605e-05 | no |
| d100_b40 | graded_t0.0025 | -8.3712e-07 | -1.7261e-06 | +1.5801e-05 | **YES** |
| d100_b40 | graded_t0.0075 | +1.3628e-06 | +2.9734e-07 | +1.0964e-05 | no |
| d100_b40 | unreduced | +1.1053e-06 | -9.2531e-07 | +1.1440e-05 | no |
| d140_b30 | graded_t0.0025 | +3.1370e-06 | +1.4733e-06 | +1.9349e-05 | no |
| d140_b40 | graded_t0.0025 | -1.2909e-06 | +3.9490e-07 | +1.7543e-05 | no |
| d140_b40 | graded_t0.0050 | +2.6999e-06 | -3.5342e-07 | +1.2545e-05 | no |
| d140_b40 | unreduced | +1.0470e-06 | -8.5713e-07 | +9.7220e-06 | no |

Read the percentage columns with this stated: the shares are of the raw total
`(MS_S + MS_P - MS_res)/(S·E)`. Method-of-moments component estimates may be
NEGATIVE, and seven of the ten targets carry at least one negative component,
so a share can fall outside `[0, 100]` and, at the single flagged target
where the raw total is not positive, the shares are printed for audit and are
not interpretable as shares. At that target the frozen degenerate branch
applies: the variance is replaced by `MS_res/(S·E)` and `nu_eff` by the
residual df `21`. Every such substitution is flagged in the JSON with the raw
mean squares beside it.

**The between-support and between-pool variance IS now inside the SE**:
`sigma_S^2` is positive at 7 of 10 targets and `sigma_P^2` at 4 of 10, and
both enter `SE^2` through `MS_S` and `MS_P` at every target, including the
targets where the point estimate of a component is negative.

---

## 3. The targets, the criterion and the achieved `V`-match

`n_C` **declared** `= 11` (8 graded + 3 unreduced), `alpha_pair = 0.10/11 =
0.0090909090909…`; `|t|crit = t.ppf(1 - alpha_pair/2, nu_eff)` per target at
its own `nu_eff`. `n_C` **realized** `= 10`, `alpha_pair = 0.010`: the
`(140,30)` cell yields only ONE graded survivor under the frozen selection
rule (its `V` leaves the TL-reachable interval `[8.571429, 23.571429]` after
`t = 0.0025`), not two, and its unreduced arm is UNREACHABLE by the frozen
rule exactly as the contract computed in advance (`V = 6.750435 <
8.571429`). Both counts and both levels are reported; the **declared** level
is primary, being the more conservative against falsification.

Every one of the 10 targets is INFORMATIVE (`m3` separation `0.1228` to
`1.6410`, all above the carried `0.10` requirement); none was excluded.

| cell | target | `V` | `|dV|` float64 | `|dV|` float32-realized | `D_GR` | `D_TL` | `Delta_bar` | `|t|` | `|t|crit` | rel% | FALSIFYING |
|---|---|---|---|---|---|---|---|---|---|---|---|
| d100_b30 | graded_t0.0025 | 12.951247 | 7.11e-15 | 1.73e-06 | +0.05792919 | +0.05683868 | +0.00109051 | 1.211 | 6.966 | 1.88 | no |
| d100_b30 | graded_t0.0050 | 8.473481 | 1.78e-15 | 1.05e-06 | +0.03704120 | +0.03434837 | +0.00269283 | 2.749 | 4.979 | 7.27 | no |
| d100_b30 | unreduced | 9.362794 | 3.55e-15 | 1.11e-06 | +0.03778136 | +0.03903057 | -0.00124921 | 4.913 | 70.023 | 3.20 | no |
| d100_b40 | graded_t0.0025 | 14.778516 | 7.11e-15 | 1.84e-06 | +0.05166266 | +0.05152839 | +0.00013427 | 0.191 | 2.874 | 0.26 | no |
| d100_b40 | graded_t0.0075 | 6.546441 | 3.55e-15 | 1.19e-06 | +0.02178834 | +0.01973461 | +0.00205373 | 2.680 | 5.357 | 9.43 | no |
| d100_b40 | unreduced | 16.244628 | 1.07e-14 | 2.30e-06 | +0.05470662 | +0.05719000 | -0.00248339 | 4.830 | 18.901 | 4.34 | no |
| d140_b30 | graded_t0.0025 | 12.476462 | 7.11e-15 | 1.40e-06 | +0.04843114 | +0.04675482 | +0.00167632 | 1.435 | 4.797 | 3.46 | no |
| d140_b40 | graded_t0.0025 | 15.234807 | 1.07e-14 | 1.67e-06 | +0.04339152 | +0.04179924 | +0.00159228 | 2.285 | 25.356 | 3.67 | no |
| d140_b40 | graded_t0.0050 | 9.086503 | 3.55e-15 | 8.84e-07 | +0.02569130 | +0.02206440 | +0.00362690 | 4.529 | 5.118 | 14.12 | no |
| d140_b40 | unreduced | 11.807462 | 3.55e-15 | 1.36e-06 | +0.03094758 | +0.03106964 | -0.00012206 | 0.260 | 21.618 | 0.39 | no |

The frozen `1e-9` `V`-match is met at every target with four orders to
spare (`max 1.07e-14`), achieved by the closed-form inverse in float64. The
float32 frame that the committed projection consumes realizes a coarser match
(`8.84e-07` to `2.30e-06`); the consequence of that on `D` is MEASURED rather
than bounded — see section 6.

**`n_falsifying = 0`. `n_suggestive = 0`** under the frozen definition
(`|t|` in `[0.8·|t|crit, |t|crit)` **and** relative difference above
`tau_rel`). The nearest approach to the rejection region is recorded here so
it is not lost: **d140_b40 / graded_t0.0050, `|t| = 4.529` against
`|t|crit = 5.118`, relative difference `14.12%` against `tau_rel = 15%`** —
inside the `0.8·|t|crit` band but below the relative floor, so it fails the
frozen SUGGESTIVE definition too. Both bars are missed, and by the frozen
rule it is neither falsifying nor suggestive.

---

## 4. THE NULL CALIBRATION — an ESTIMATED rate, with both intervals

Three nulls, all scored through the **identical code path and the identical
criterion** (`alpha_pair` at the declared `n_C = 11`, `tau_rel = 0.15`, the
same two-way SE). Replicates fall into 5 disjoint pool-quadruple clusters
drawn from a 20-pool bank per cell.

| unit | R | x | point rate | Wilson 95% | Wilson **upper** | cluster bootstrap 95% | median `|t|` | p95 `|t|` | median rel |
|---|---|---|---|---|---|---|---|---|---|
| N-A d100_b40 | 300 | 0 | 0.00000 | [0.00000, 0.01264] | **0.012643** | [0.0, 0.0] | 0.542 | 2.491 | 0.65% |
| N-A d140_b40 | 300 | 0 | 0.00000 | [0.00000, 0.01264] | **0.012643** | [0.0, 0.0] | 0.655 | 2.158 | 0.98% |
| N-B d100_b40 | 300 | 0 | 0.00000 | [0.00000, 0.01264] | **0.012643** | [0.0, 0.0] | 0.635 | 2.355 | 0.77% |
| N-B d140_b40 | 300 | 0 | 0.00000 | [0.00000, 0.01264] | **0.012643** | [0.0, 0.0] | 1.062 | 3.778 | 1.50% |
| N-C d100_b40 | 60 | 0 | 0.00000 | [0.00000, 0.06017] | 0.060169 | [0.0, 0.0] | 0.901 | 2.592 | 102.16% |
| N-C d140_b40 | 60 | 0 | 0.00000 | [0.00000, 0.06017] | 0.060169 | [0.0, 0.0] | 0.640 | 1.986 | 100.50% |

Per-cluster counts are `0/60` in every one of the five clusters of every
N-A/N-B unit, and `0/12` in every cluster of every N-C unit. **The Wilson
interval is labelled a LOWER BOUND on the true uncertainty**, because
replicates sharing a pool quadruple are not independent; the cluster
bootstrap, which does not assume that independence, is reported beside it and
resamples the 5 clusters (`B = 20000`).

**Null exactness, mandatory and printed:** N-A `max|V - V''| = 7.11e-15`,
`max|m3 - m3''| = 1.78e-15`; N-B (coordinate-permutation identity)
`max|V - V_perm| = 5.33e-15`, `max|m3 - m3_perm| = 1.78e-15`. All are within
the frozen `1e-12`, so both nulls are exact and every firing they could have
produced would have been a false falsification.

**Two observations about the nulls that belong on the record.**

1. `nu_eff` in the nulls is small (median `2.34` to `2.51`) and the
   NEGATIVE-VARIANCE-COMPONENT branch fired in `37`–`48` of `300` replicates
   per unit (`12%`–`16%`). The frozen degenerate branch handled each.
2. **N-C's relative-difference condition is degenerate by construction.**
   Under Gaussian errors `R ~ Beta(beta/2, (d-beta)/2)` exactly for every
   orthonormal frame, so both `D` values sit at the sampling floor around
   zero, the denominator `M = max(|D_GR|, |D_TL|)` is tiny, and the median
   relative difference comes out at `102.16%` / `100.50%` — i.e. condition
   (ii) is satisfied at essentially every N-C replicate and the criterion
   there is carried entirely by condition (i). N-C fired `0` of `120`
   regardless.

### G-CAL, the calibration gate

> **G-CAL PASSES.** For BOTH N-A and N-B, in BOTH null cells, the Wilson 95%
> upper bound of the estimated per-pair false-falsification rate is
> `0.012643`, against the frozen threshold `0.040`.

The contract's reachability arithmetic was recomputed by the run and
reproduces its frozen table: Wilson upper `0.018846 / 0.027767 / 0.035716` at
`0/1/2` of `200` (pass), `0.043172` at `3` of `200` (refuse), `0.036994` at
`0` of `100`, `0.038420` at `5` of `300` (pass) and `0.042936` at `6` of `300`
(refuse). The realized `R = 300` in all four units clears the `R_min = 200`
hard floor, so no unit is UNDECIDED.

---

## 5. THE `delta_min` POSITIVE CONTROL — reported at EVERY target

`delta_min = max(detection floor, tau_rel) − realized relative difference`,
floored at `0`; a constant offset `a = sign(Delta_bar)·delta·M` leaves the SE,
all three variance components and `nu_eff` unchanged and moves `|Delta_bar|`
to `|Delta_bar| + delta·M`.

| cell | target | detection floor | `delta_min` | binding term | fires at `delta` = |
|---|---|---|---|---|---|
| d100_b30 | graded_t0.0025 | 10.83% | 0.1312 | `tau_rel` | 0.15, 0.20, 0.30, **0.50** |
| d100_b30 | graded_t0.0050 | 13.17% | 0.0773 | `tau_rel` | 0.10, 0.15, 0.20, 0.30, **0.50** |
| d100_b30 | unreduced | 45.62% | 0.4242 | detection floor | **0.50** |
| d100_b40 | graded_t0.0025 | 3.91% | 0.1474 | `tau_rel` | 0.15, 0.20, 0.30, **0.50** |
| d100_b40 | graded_t0.0075 | 18.84% | 0.0942 | detection floor | 0.10, 0.15, 0.20, 0.30, **0.50** |
| d100_b40 | unreduced | 16.99% | 0.1265 | detection floor | 0.15, 0.20, 0.30, **0.50** |
| d140_b30 | graded_t0.0025 | 11.57% | 0.1154 | `tau_rel` | 0.15, 0.20, 0.30, **0.50** |
| d140_b40 | graded_t0.0025 | 40.72% | 0.3705 | detection floor | **0.50** |
| d140_b40 | graded_t0.0050 | 15.95% | 0.0183 | detection floor | 0.05, 0.10, 0.15, 0.20, 0.30, **0.50** |
| d140_b40 | unreduced | 32.67% | 0.3227 | detection floor | **0.50** |

> **The frozen admissibility clause is SATISFIED: the criterion fires at
> `delta = 0.50` at EVERY one of the 10 targets.** The rebuilt instrument is
> therefore not UNDERPOWERED BY CONSTRUCTION, and the post-injection relative
> difference at `delta = 0.50` is printed in the JSON at every target so a
> reader can check on the page that each firing sits on an effect above the
> floor.

The two clauses of this section's gate point in opposite directions, as the
contract designed: **G-CAL refuses an instrument that fires too easily and
PASSED at `0/300` four times; the `delta = 0.50` clause refuses one that
cannot fire at all and PASSED at all 10 targets.** Neither could have been
satisfied by making the SE larger or smaller.

---

## 6. Instrument checks

| check | result |
|---|---|
| GR / unreduced arms reproduce the committed BATCH-f19c37 record (pool `p = 0`, `seed_error(d)`) | **bit-identical** at `d100_b30` and `d100_b40` (`max dev 0.0`); at `d140_b30` and `d140_b40` `max dev = 2.220446049250313e-16`, the ONE-ULP deviation the contract declared in advance, confined to `d = 140`. **It is NOT rounded to `0.0`.** |
| order statistic by `np.partition` vs the committed `np.sort` path | `max abs diff = 0.0` at every cell |
| consequence on `D` of the committed float32 TL frame, MEASURED against an exact float64 kernel with no frame rounding at all | `1.04e-07`, `1.39e-07`, `1.80e-07`, `6.56e-08` at the four cells — three to four orders below the realized `SE(Delta_bar)` (`2.5e-04` to `1.2e-03`) |
| N-A exactness `|V − V''|`, `|m3 − m3''|` | `7.11e-15`, `1.78e-15` (frozen tolerance `1e-12`) |
| N-B coordinate-permutation identity | `5.33e-15`, `1.78e-15` |
| degenerate `V = beta(1 − beta/d)` instrument check (excluded from the scored family BY RULE) | `|t| = 0.316 / 0.452 / 0.891 / 0.386`, relative `1.14% / 0.75% / 1.79% / 0.83%`; would not have fired in any cell. **Agreement there is forced by identity, not by mechanism, and is never counted as support for anything.** |
| CBD pmf / `mu_4` | measured against the exact `[1,4,6,4,1]/16` and `mu_4 = 2.5` at every cell (JSON `cbd_pmf_check`) |
| forbidden-wording scan over the JSON | `0` hits |

---

## 7. The frozen pre-registered predictions

| prediction | outcome |
|---|---|
| **PRED-C1** — with the rebuilt SE, both N-A and N-B satisfy G-CAL in both cells | **PASS** (Wilson upper `0.012643` in all four units, against `0.040`) |
| **PRED-C2** — the between-support and between-pool components together contribute `>= 50%` of `SE^2(Delta_bar)` at a MAJORITY of targets | **FAILS.** They reach `50%` at `2` of `10` targets (`1` of the `9` targets whose raw total is positive). Per-target shares: `17.5, 47.0, -750.8, 1265.0, 41.7, -35.2, 55.7, -12.9, 38.9, -37.8` percent. In the nulls the median share is `22.6%`–`36.0%`. Recorded plainly, as the contract requires: the AM-7 diagnosis's magnitude does not reproduce in the rebuilt design at these targets, while the components themselves are now inside the SE. |
| **PRED-C3** — under N-C's Gaussian errors, `0` FALSIFYING pairs of `60` per cell | **HOLDS** (`0` of `120`) |
| no prediction was made about the proposition itself | none is made here |

---

## 8. THE FROZEN VERDICT

Evaluated mechanically in the contract's own order: G-CAL PASSED; the
`delta = 0.50` admissibility clause fired at every target; there is no
FALSIFYING PAIR; and at least one INFORMATIVE pair has detection floor below
`tau_rel` (four do: `3.91%`, `10.83%`, `11.57%`, `13.17%`).

> ### VERDICT: **CONSISTENT** — no FALSIFYING PAIR, the calibration gate PASSED, and at least one INFORMATIVE pair has detection floor `< tau_rel = 0.15`.

Stated with its scope, and stated plainly in both directions:

* **The rebuilt instrument DOES separate at the level it was asked to.** It
  fires on a `50%` injected offset at all 10 targets, its tightest detection
  floor is `3.91%` relative, and it did not fire once on `1200` exact-null
  replicates across two independently constructed nulls in two cells.
* **It did not separate the two families at any of the 10 matched-`V`
  targets.** No pair reached both bars; the nearest approach missed both.
* **Six of the ten pairs individually have detection floors at or above
  `tau_rel`** (`15.95%` to `45.62%`). For those pairs the honest reading is
  an upper bound at their own floor, not an outcome. The frozen verdict map
  assigns CONSISTENT to the family when ANY informative pair has a floor below
  `tau_rel`; that rule was run exactly as written and this per-pair
  granularity is recorded beside it, not substituted for it.
* **Family-level upper bound, as the contract phrases it:** any matched-`V`
  cross-family difference not detected here is bounded above by **`3.91`
  percent relative** at the tightest pair, at `S = 8` supports, `E = 4` pools,
  `N = 2^20`, with the per-pair floors above for every other pair.

**What this verdict is NOT.** It is not a statement that `V` is sufficient; it
is the output of a frozen rule on 10 targets at `d <= 140`, `beta <= 40`, at
the `2^-10` quantile only. It does not touch the second-order derivation,
which is correct and untouched. It moves no hypothesis, closes nothing, and
validates no heuristic — that judgment belongs to the Reviewer and the
Coordinator, not to this run.

---

## 9. Protocol deviations, objections and implementation completions

**Deviation D-1 (recorded, not discarded) — the ORDER in which the four
(null, cell) units were computed.** The contract's ladder lists N-A `(100,40)`,
then N-A `(140,40)`, then N-B in the same two cells, with the declared
priority "N-A both cells first, then N-B, then N-C" if the budget binds. This
run took **each unit to the hard floor `R_min = 200` first, in exactly that
priority order, and only then topped every unit up to `R_target = 300` in the
same order.** Reason: G-CAL is UNDECIDED and the Section C verdict WITHHELD
unless ALL FOUR units reach `R_min`, and on a host whose load ran from `39` to
`383` during the run, finishing one unit at `300` before another reached `200`
risked an instrument outcome. Replicate `r` is the same object whenever it is
computed — its supports, its permutations and its pool quadruple are functions
of `r` alone — so no seed, no replicate identity, no cluster membership, no
criterion and no threshold changed. **In the event the budget did not bind:
all four units reached `R = 300` and N-C ran in full, so the deviation had no
effect on any reported number.** `ladder_notes` is empty; nothing was cut.

**Objection O-1, recorded and the frozen specification run anyway.** At `S = 8`
and `E = 4` the Satterthwaite `nu_eff` is small (`1.00` to `21.00`, median
about `2.5`), so `|t|crit` ranges from `2.874` to `70.023` across targets and
is data-dependent by construction. The contract declares that in advance
(4.3). It means the `|t|` bar is very uneven across targets — at `d100_b30 /
unreduced` a `|t|` of `4.913` faces a bar of `70.023`. The frozen rule was run
exactly as written and this observation changes no verdict; it is recorded
because the same design choice will bind any successor.

**Objection O-2.** The declared `n_C = 11` presumes two graded survivors in
every cell; `(140,30)` yields one. Both the declared and realized counts and
levels are reported, as the contract requires, and the declared (more
conservative) level is primary. No selection was made after the fact.

**Implementation completions** (points the frozen text does not fix; each
recorded in the JSON with its effect on thresholds, which is `none` in every
case): the replicate coordinate in the null TL support seeds
(`[5,d,beta,s,r]` / `[6,d,beta,s,r]`, both sides drawn afresh per replicate,
distinct streams from the real arm's 4-element key); N-B drawing 8
permutations in sequence from `default_rng([10,d,beta,r])`, one per support
index; `nu_eff = (S-1)(E-1) = 21` in the NEGATIVE-VARIANCE-COMPONENT branch;
`np.partition` for the order statistic, VERIFIED equal to the committed
`np.sort` path at `0.0`; and the `m3` informativeness filter NOT being applied
to a null — N-A and N-B are exact nulls precisely because their `m3` agree, so
applying it would exclude every null replicate and make the calibration
unmeasurable, while the FALSIFYING-PAIR criterion itself is applied
identically.

**The git bookkeeping defect of section 0** is recorded there.

---

## 10. What this run does not reach

It compares two synthetic frame families plus three unreduced real-lattice
frames, at `d <= 140`, `beta <= 40`, `S = 8` supports, `E = 4` pools,
`N = 2^20`, at the `2^-10` quantile only, with no reduction beyond what the
committed unreduced arms already carry. It tests the tail-level sufficiency of
`V` and nothing else: not the variance-level identity, which is established
and untouched; not any reduced arm; not any lattice invariant. None of these
observables satisfies AM-4 and none is offered as an adjudicator of a claim
about a lattice. Whether the proposition holds for reduced lattice tail frames
is untouched in either direction by anything this run can produce at this
replication.

Budget exhaustion, timeout, crash or a missing dependency would have been
INFRASTRUCTURE SIGNAL and never negative mathematical evidence; none occurred.
`gmpy2` is not installed in this environment and nothing here depends on it.

---

## 11. Run facts

```
command       : python3 measure_am7.py --wall-budget-seconds 5400 --checkpoint-seconds 4200
started (UTC) : 2026-08-09T01:38:42Z      finished (UTC) : 2026-08-09T02:43:59Z
wall          : 3919.04 s of a 5400 s hard budget     cpu : 2835.07 s
peak RSS      : 1.156 GiB of a 4 GiB hard budget      runs : 1 of 1
host          : macOS-26.6-arm64, 14 cores, loadavg 202.0 at start, 39.0 at end
               BLAS = Accelerate, pinned to 1 thread in every backend
versions      : python 3.13.1, numpy 2.4.0, scipy 1.15.3, fpylll 0.6.4, gmpy2 NOT INSTALLED
D-evaluations : 62,976 order statistics at N = 2^20 on the committed projection path,
                plus 32 on the exact float64 TL kernel of the instrument check.
                Counted from the loop structure, not estimated:
                  main comparison  4 pools x (64 + 64 + 32 + 64 per cell) = 896
                  N-A  2 cells x 5 clusters x 4 pools x 60 reps x 16 = 38,400
                  N-B  2 cells x 5 clusters x 4 pools x (8 + 60x8)   = 19,520
                  N-C  2 cells x 5 clusters x 4 pools x (8 + 12x8)   =  4,160
```

**Independence is PROCEDURAL, never model-level**: separate session, no shared
scratch, snapshot before review. `model_verified: false` — no adapter probe
receipt exists for this session. AGENTS.md rule 12 remains UNMET and UNWAIVED
in this goal and is recorded, not smoothed.

**Inference record (verbatim):**

```
requested_policy: executor-implementation
degraded_allowed: false ; fallback_allowed: false
resolved: under the Claude Code runtime, per CLAUDE.md, per-role model selection is
  process-level and subagents keep model: inherit, so the resolved model is the session model
fallback_used: false
model_verified: false (no adapter probe receipt for this session)
```
