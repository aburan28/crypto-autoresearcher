# BATCH-f75059 / TASK-20260803-5f11b7 — execution report

**Role:** Executor. **Goal:** GOAL-MLKEM-004, batch 2 of 6.
**Predecessor batch:** BATCH-d2a728 (`EV-MLKEM-da9e3b`, `DEC-20260803-d810d0`).

> **Scope, stated first and binding on every number below.**
> `m = 35`, `n = 25`, `d = 60`, `q = 127`, secret centred-binomial `eta = 2`, error
> rounded-Gaussian `sigma = 2`, one sieve algorithm (`g6k 0.1.2 bgj1_sieve`,
> `threads=1`), distinguishing form only with no FFT sub-block split. **This is
> TOY SCALE**: FIPS 203 uses `n = 256k` and `q = 3329`. Nothing here is a
> statement about FIPS 203 dimensions, and no numbered extrapolation heuristic
> is asserted by this batch. No ML-KEM break claim. No security proof and no
> security claim in either direction. No FIPS 203 parameter set affected or
> cleared. No cost claim, no speedup, no attack implemented or run.
> `certificate.kind` is `lattice_membership` only; the run claims no
> discrete-log solve and no factor-base relation.
> **AGENTS.md rule 12 is UNMET and UNWAIVED**, inherited from GOAL-MLKEM-003.
> This report changes the status of no `EV-MLKEM-*` record and no `KN-*` entry,
> and proposes none.
>
> **This report records observations. It does not conclude that the heuristic
> is validated or refuted** (agents/executor.md responsibility 13). That
> judgement belongs to the Reviewer and the Coordinator.

---

## 0. Headline, in the vocabulary the card asked for

| ingredient of the assumed law | verdict at this configuration | evidence |
|---|---|---|
| **1. per-vector advantage** `exp(-2 pi^2 sigma^2 \|\|x\|\|^2/q^2)` | **HOLDS**, to a -1.8% common offset with a 0.8% residual shape trend; the residual is almost entirely the law's continuous-Gaussian idealisation of a *discretised* error (post-hoc D1 reduces the shape residual 2.8x and removes the offset entirely) | S3 |
| **2. iid noise over wrong candidates — uniform group** | **HOLDS**, ratio to `sqrt(1/2N)` = 0.9978 after correcting the sample-sd bias of the estimator | S4.1 |
| **2. iid noise — secret-distribution group** | **DEPARTS**, 4.10x wider than iid and centred at +0.2816 rather than 0 — expected, and explained by the retained `y.(s-c)` term | S4.2 |
| **2. iid noise — near-miss group** | **DEPARTS**, 0.150x the iid spread: near-misses are 6.7x *more* concentrated than independence predicts | S4.3 |
| **vector-null (P2)** | the sieve database's 403x variance inflation is a **CONTROLLED NULL** — reproduced to 0.3% by random directions of matched `\|\|x\|\|`, and eliminated entirely by removing the shared error vector | S5 |
| **P1 well-posedness** | **no `(m, k_enum, k_fft, p, beta_bkz, beta_sieve)` tuple exists** | `wellposedness.md` |
| **P1b known-answer control** | **10 of 10 checks run and passed**, including a round trip against the pinned repository's own documented Kyber512 value | S2 |

**Agreement is the dominant outcome of this batch, and it is stated plainly.**
The law's two separable ingredients hold on the populations they describe, at
tighter tolerance than batch 1 could establish, and the tightening survives
9 additional independent instances. The one place the law's finite-sample
treatment departs is on the near-miss population, and that departure is now
replicated across 10 instances rather than resting on one.

---

## 1. Step 0 — instrument REBUILD (not a re-verification)

`RT-20260803-4064e1` OBJ-9 recorded the goal record's per-batch rebuild
requirement as NOT MET in batch 1, which found `/tmp/sagevenv` already present.
This batch **rebuilt** the instrument from `KN-TECH-14efa5` into a new venv at
`/tmp/sagevenv-f75059`; `/tmp/sagevenv` was never invoked. Every command and its
combined stdout+stderr is in `rebuild_transcript.txt`, appended verbatim by a
recorder script, unedited and unreordered.

```
python3 -m venv /tmp/sagevenv-f75059
/tmp/sagevenv-f75059/bin/pip install --no-cache-dir passagemath-standard      # 10.8.7
ln -sf /usr/lib/x86_64-linux-gnu/libgmp.so.10 <scratch>/gmplink-f75059/libgmp.so
env LIBRARY_PATH=<scratch>/gmplink-f75059 LDFLAGS=-L<scratch>/gmplink-f75059 \
    /tmp/sagevenv-f75059/bin/pip install --no-cache-dir --no-build-isolation g6k   # 0.1.2
```

Both link-level fixes in the recipe were needed and both worked. Wall clock
19:19:41Z to about 19:24:55Z, roughly 5 minutes end to end.

**Discriminators (KN-TECH-14efa5), re-run in the rebuilt venv:**

| check | recipe | this rebuild |
|---|---|---|
| `sage.all` resolves inside the venv, `PowerSeriesRing` works (shim would raise) | required | **yes**, 10.8.7, 0.87 s |
| fpylll dim 60 qary `q=3329`, BKZ-30 x4 | `\|\|b0\|\| 160.4 -> 130.3` (0.3 s) | **160.4 -> 130.3 (0.31 s)** — exact match |
| `BKZ.DEFAULT_STRATEGY` gotcha | must raise | `RuntimeError: Cannot open strategies file.` |
| `Siever(GSO.Mat(A))` gotcha | must raise | `ValueError: Siever requires UinvT enabled` |
| g6k dim 50 qary `q=3329`, `gauss_sieve` | db 4075 (0.94 s) | **db 4166 (0.89 s)** — see below |

**Deviation, recorded and not smoothed over.** The dim-50 `gauss_sieve` database
came out at 4166 rather than the recipe's 4075 (batch 1 reproduced 4075).
`KN-TECH-14efa5` pins neither the qary lattice seed nor the Siever seed for that
check, and this task's verification script calls `FPLLL.set_random_seed(1)`
before the fpylll check, consuming randomness before the g6k lattice is drawn.
The first database entry printed is byte-identical to batch 1's
(`(-10, 3, -2, -4, 5, 1, 3, -5)`), so it is the same lattice family. The 2.2%
difference is attributable to unpinned randomness in the recipe's own
verification figure. No measurement in this batch depends on it: every
measurement pins all of its own seeds.

Also recorded in the transcript and not elided: the executor's own verification
script failed first on `sage.__version__`, which does not exist. That is an
`implementation_error` in the check, not an instrument failure. The failure and
the corrected re-run are both kept.

---

## 2. P1b — known-answer control on `estimator.lwe_dual.matzov`

Inherited `CTRL-RT-4` / `CTRL-RT-6`: the callable four batches of GOAL-MLKEM-003
argued about, and none ever covered. **10 checks run, 0 not run, all passed.**
Pinned estimator at `/tmp/le`, commit `3e48ef421ec256afddb3e7d2249a77eab6e9ba12`,
**clean tree**.

**Callable identity** — the thing the card asked to check explicitly:

| id | check | result |
|---|---|---|
| KA-0a | public `LWE.dual_hybrid` **is** `estimator.lwe_dual.matzov` | **True** (`estimator/lwe.py:13`, `from .lwe_dual import matzov as dual_hybrid`) |
| KA-0b | `type(LWE.dual_hybrid).__name__` | **`MATZOV`** |
| KA-0c | `estimator.lwe_dual.dual_hybrid` is a **different** callable | **True** — a module-level *function* (line 742) wrapping `DH = DualHybrid()`, the [INDOCRYPT:EspJouKha20] attack, distinct from the MATZOV instance the public name resolves to |
| KA-0d | `matzov.Nf is MATZOV.Nf` (bound classmethod identity) | **True** |

**Known answers:**

| id | check | result |
|---|---|---|
| KA-1 | `MATZOV.Hf` equals an independent numpy reimplementation | pass (< 1e-9) |
| KA-2 | `MATZOV.Nf` equals an independent reimplementation, including an independent `deltaf`, over a 6-point tuple grid | pass, max rel err < 1e-9 |
| KA-3 | `Nf` is independent of `p` when `k_fft = 0` | pass, exact |
| KA-4 | `Hf` returns **bits** while `log p`, `log(1/mu)` are **nats** | confirmed, ratio `1/ln2` |
| KA-5 | `Nf` independent of `beta_bkz` when `beta_sieve = m + k_lat` | pass, exact |
| KA-6 | `matzov(Kyber512, RC.ADPS16)` against the **pinned repository's own documented value** (`estimator/lwe.py` docstring: `rop ~ 2^115.5, beta 395, p 5, zeta 0, t 40`) | **pass**: `2^115.5099`, `beta=395`, `p=5`, `zeta=0`, `t=40`, 4.6 s |

KA-6 is the strongest form available: the exact public callable reproduces a
value documented in the pinned repository itself, at cryptographic parameters.
KA-4 is recorded as an **observation about the callable**, not as a claim that
the estimator is wrong; its consequence for this task is an extra factor-`ln 2`
ambiguity in any `k_enum`-bearing reading of the log-term.

---

## 3. Ingredient 1 — the per-vector advantage law

**Law under test (frozen, as written):**
`E_e[cos(2 pi x.e/q)] = exp(-2 pi^2 sigma_e^2 ||x||^2/q^2)`, with the nominal
`sigma_e = 2`. This is the per-vector half of `MATZOV.Nf`'s exponential factor
`exp(4 (l sigma pi/q)^2) = 1/advantage^2`, and it is separable from the log-term
that has no referent here (`wellposedness.md`).

**Test:** the same database conditioned on `||x||^2` deciles — the axis the
sigma-sweep cannot move — with mean +/- sd over **2000 fresh error draws**.

| decile | count | `||x||^2` | predicted | measured (2000 draws) | ratio | shape ratio (common mode removed) |
|---|---|---|---|---|---|---|
| 1 | 1791 | 74-144 | 0.52787 | 0.52114 +/- 0.08435 | 0.9873 | **1.01748 +/- 0.07052** |
| 2 | 1792 | 144-157 | 0.47758 | 0.47111 +/- 0.08768 | 0.9864 | 1.01091 +/- 0.04864 |
| 3 | 1792 | 157-167 | 0.45205 | 0.44549 +/- 0.08912 | 0.9855 | 1.00659 +/- 0.03919 |
| 4 | 1792 | 167-175 | 0.43347 | 0.42665 +/- 0.08973 | 0.9843 | 1.00276 +/- 0.03322 |
| 5 | 1792 | 175-183 | 0.41684 | 0.40963 +/- 0.09129 | 0.9827 | 0.99819 +/- 0.03535 |
| 6 | 1792 | 183-190 | 0.40185 | 0.39492 +/- 0.09148 | 0.9827 | 0.99637 +/- 0.04019 |
| 7 | 1792 | 190-198 | 0.38741 | 0.38037 +/- 0.09184 | 0.9818 | 0.99314 +/- 0.04663 |
| 8 | 1792 | 198-207 | 0.37212 | 0.36560 +/- 0.09188 | 0.9825 | 0.99145 +/- 0.05381 |
| 9 | 1792 | 207-219 | 0.35407 | 0.34762 +/- 0.09179 | 0.9818 | 0.98808 +/- 0.06476 |
| 10 | 1792 | 219-282 | 0.32343 | 0.31681 +/- 0.09123 | 0.9795 | **0.98040 +/- 0.08660** |

Global ratio measured/predicted: **0.9838 +/- 0.2148** over 2000 draws
(sem 0.0048). The `||x||^2` range spanned is 1.76x on decile means (3.8x on the
raw `||x||^2` support, 74 to 282).

**What holds.** The functional form is confirmed across the whole range: after
removing the per-draw common mode, every decile lies within **+/-1.8%** of unity,
and the total spread across the 3.8x range of `||x||^2` is **3.8%**.

**What departs, honestly stated.** With 2000 draws the error bars are small
enough to resolve structure batch 1 could not: the shape ratio is **monotone
decreasing** in `||x||^2` (`corr = -0.9975`), and decile 1 (`1.01748`, sem
0.00158) and decile 10 (`0.98040`, sem 0.00194) are about 11 and 10 sem from
unity. The measured advantage decays slightly *faster* than the law as written.

**Post-hoc diagnostic D1 (computed after the run from `vectors.json`; the frozen
comparison above is NOT re-scored).** The law's exponential is the
characteristic function of a *continuous* Gaussian. The measured error is
`round(N(0,sigma))`, whose exact variance is `4.0833`, not `4`. Computing the
exact characteristic function of the actual discrete error distribution
(`Re prod_j phi(2 pi x_ij/q)`) gives:

| prediction used | ratio spread across deciles | shape trend corr |
|---|---|---|
| frozen, `sigma^2 = 4` continuous | 0.97952 .. 0.98726 (0.0077) | -0.9695 |
| **exact discrete characteristic function** | **1.00045 .. 1.00327 (0.0028)** | +0.7571 |

The -1.8% common offset disappears entirely and the shape residual shrinks by
**2.8x**. A +0.15% residual remains, unexplained.

**Reading, without interpretation beyond the data:** at this configuration the
per-vector advantage law is accurate to about 2% as written, and to about 0.3%
once the discreteness of the error the law idealises as continuous is accounted
for. That discreteness correction is a property of the *toy* modulus/sigma regime
(`sigma/q = 2/127`) and shrinks at cryptographic `q`; it is recorded as a
boundary of this measurement, not as a correction to the law.

**Replication across instances (S7):** global ratio **0.9877 +/- 0.0097** across
9 further independent instances (500 draws each).

**Length sub-comparison (see `wellposedness.md` S5).** MODELED `lsigma_s`
(MATZOV, reading R-A) = 24.406 against a MEASURED effective `l*sigma` of 29.274,
ratio 0.834; MODELED per-vector advantage 0.4824 against MEASURED
`reference_zero` mean score 0.3280 +/- 0.0722 (2000 draws), i.e. the modeled
value sits +2.1 sd of the measured distribution. Recorded as a labelled
modeled-vs-measured comparison at one toy configuration with no null of the right
shape; **not** licensed as a departure claim.

---

## 4. Ingredient 2 — the iid noise model, PER CANDIDATE GROUP

**Law under test:** wrong-candidate mean scores are averages of `N` independent
contributions, so their spread is `sqrt(Var(score)/N)`; for a candidate whose
phase is uniform mod `q` this is `sqrt(1/2N) = 0.005282` at `N = 17919`.

**No pooled wrong-candidate statistic is computed anywhere in this batch.**
`results.json` contains none. Batch 1's `18 of 33` and `-0.04 sd` are not
reproduced, restated, or relied on (`INT-3`, `DEC-20260803-d810d0`).

All rows: mean +/- sd over **2000 fresh error draws**.

| group | n | mean of group mean scores | sd across candidates within a draw | ratio to iid | ratio, sample-sd bias corrected (D2) |
|---|---|---|---|---|---|
| uniform `Z_q^n` | 16 | +0.000462 +/- 0.001075 | 0.005184 +/- 0.000940 | 0.9814 +/- 0.1780 | **0.9978** |
| secret-distribution (CB eta=2) | 8 | +0.281637 +/- 0.062294 | 0.020924 +/- 0.004664 | 3.9612 +/- 0.8829 | **4.1047** |
| near-miss (`s` + 1 in one coord) | 8 | +0.405268 +/- 0.088481 | 0.000766 +/- 0.000206 | 0.1450 +/- 0.0389 | **0.1503** |
| *correct secret* | 1 | +0.407926 +/- 0.089049 | — | — | — |
| *reference zero* (phase = `x.b`) | 1 | +0.328049 +/- 0.072180 | — | — | — |

D2 is a post-hoc correction for a known bias of the *estimator*, not of the data:
`E[s] = c4(n) * sigma` with `c4(16) = 0.983484`, `c4(8) = 0.965030`.

### 4.1 Uniform group — the law HOLDS

Ratio to the iid prediction **0.9978** (raw 0.9814 +/- 0.1780, sem 0.00398). This
is the population MATZOV's independence assumption describes, and on it the
assumption is accurate to **0.2%** over 2000 draws. Batch 1 reported ratio 1.00
on a coarser estimator; this batch confirms it at higher precision and, in S7,
across 10 instances (1.0021 +/- 0.0521).

Separation from the correct secret: paired delta **+0.407464 +/- 0.088932**
against the group mean and **+0.398149 +/- 0.088956** against the best of 16.
`P(correct ranks first within group) = 1.000` over 2000 draws, and 1.000 in every
one of the 9 replicate instances.

### 4.2 Secret-distribution group — DEPARTS, and is expected to

Centred at **+0.2816**, not 0, and **4.10x** wider than iid. Both are
consequences of the retained `y.(s-c)` term with `s-c` small, not of any sieve
property: `a_y = 2 pi^2 Var(s) <||y||^2> / q^2 = 0.1586`, `exp(-a_y) = 0.8534`.
(Reconciliation with `RT-20260803-4064e1`, which quotes `a_y = 0.3171`: RT uses
`Var(s-s') = 2 sigma_s^2`; this report uses `Var(s) = sigma_s^2`. The two differ
by exactly the factor 2 and describe the same measurement.)

Paired delta correct minus group mean **+0.126289 +/- 0.027073**; against the best
of 8, **+0.098937 +/- 0.021875**; `P(correct first) = 1.000` over 2000 draws.

### 4.3 Near-miss group — DEPARTS, and this is the batch's live observation

The near-miss group is **6.7x more concentrated** than independence predicts
(ratio 0.1503). Independence over candidates is the assumption; on this
population it is not merely inaccurate but wrong in the *direction that matters
for a union bound*: correlated candidates make the bound conservative on random
candidates and optimistic on adjacent ones.

| statistic (2000 draws) | value | per-draw `t` |
|---|---|---|
| paired delta, correct minus near-miss **group mean** | +0.002658 +/- 0.000633 | 4.20 |
| paired delta, correct minus **best of 8** near-misses | +0.001523 +/- 0.000719 | 2.12 |
| `P(correct ranks first within group)` | **0.986** | — |
| mean rank of correct within the 9 | 1.014 +/- 0.124 | — |

Reconciliation with batch 1's review: `RT-20260803-4064e1` OBJ-8 reported
`+0.002606 +/- 0.000987` (`t ~ 2.6`) for the correct-vs-*one*-near-miss delta over
600 draws. This batch measures `+0.002658 +/- 0.000633` against the group mean
over 2000 draws — the **central value reproduces to 2%**, and the narrower sd is a
consequence of averaging 8 near-misses rather than one. Against the *best of 8*,
which is the stricter and more relevant statistic, the per-draw `t` is 2.12.

### 4.4 Success probability against subsample size `N'`, per group, never pooled

Success = the correct secret's mean score exceeds **every** member of the named
group, on a random subsample of `N'` vectors. 1000 fresh error draws per cell.

| `N'` | vs 16 uniform | vs 8 secret-shaped | vs 8 near-miss |
|---|---|---|---|
| 25 | 0.818 | 0.559 | 0.008 |
| 100 | 0.995 | 0.907 | 0.036 |
| 400 | 1.000 | 0.999 | 0.114 |
| 1600 | 1.000 | 1.000 | 0.457 |
| 6400 | 1.000 | 1.000 | 0.900 |
| 17919 | 1.000 | 1.000 | **0.989** |

Caveat stated with the table (`RT OBJ-5`): subsampling holds the **length**
distribution fixed, whereas a genuinely smaller sieve returns *shorter* vectors
and would do better. Separately, `N = 17919` is a **g6k library default**
(`ceil(3.2 * (4/3)^30)`), not a chosen parameter — and `N` is precisely the
quantity `Nf` computes.

`MATZOV.Nf`'s own prediction at the L2 reading is `N ~ 24.9`
(`wellposedness.md` S4). Against the uniform population its assumption describes,
`N' = 25` already gives 0.818 and `N' = 100` gives 0.995 — the prediction is of
the right order. Against the near-miss population the full `N = 17919`
(at least 700x the law's own `N`) gives 0.989.

---

## 5. P2 — the nulls. Every null names the object whose removal it tests

Corrective rule from `DEC-20260803-d810d0` PD-1, applied literally: each entry in
`results.json -> S8_nulls_P2` carries a `removes_object` field, a `preserves`
field, and a `can_it_fail` field.

### NULL-V — the vector-null (the one batch 1 did not run)

- **Object removed:** *the sieve database itself* — its lattice membership, its
  integrality, the exact 3-term algebraic relations among its vectors, and its
  ball-saturation structure. This is the object whose independence
  `MATZOV.Nf` asserts.
- **Preserved:** `N`, `m`, `q`, `sigma_e`, and the exact empirical `||x||`
  distribution (each surrogate vector carries the norm of the sieve vector it
  replaces), so `a_x` is identical by construction.
- **Can it fail?** **YES.** If the concentration were a property of *sieving*,
  random directions would not reproduce it.
- **Draws:** 1000, **paired** — the surrogate arm and the sieve arm see the
  identical error sequence.

| vector population | mean | sd over `e` | iid sd | variance inflation | `N_eff` |
|---|---|---|---|---|---|
| **sieve database** (bgj1, dim 60) | +0.403821 | **0.088015** | 0.004383 | 403.3x | **44.4** |
| **random directions, matched `||x||`** | +0.403799 | **0.087785** | 0.004384 | 401.0x | **44.7** |

**The surrogate reproduces the sieve database to 0.3%.** The 403x variance
inflation is a **CONTROLLED NULL** (inventor protocol S3) with respect to the
hypothesis "sieve correlations break the independence assumption". It must not
be reported by any later batch as evidence about sieve output. This reproduces
`RT-20260803-4064e1` OBJ-2 under contract and *tightens* it: RT's unpaired
comparison left a factor 1.6 in `N_eff` (38 vs 63); with paired draws the two
agree to within 1%.

**Modeled analytic prediction, derived in this task (not from MATZOV).** For a
vector family spread over directions, the database mean depends on `e`
essentially through `||e||^2` alone, `S(e) ~ exp(-a_x ||e||^2/(m sigma^2))`; with
`Var(||e||^2) = 2 m sigma^4` this gives `sd(S) ~ S * a_x * sqrt(2/m)`,
**independent of `N`**. Predicted **0.085933** against measured **0.088015** —
2.4%. The mechanism is therefore identified, not merely controlled.

### NULL-IID — the shared error vector removed

- **Object removed:** *the shared `m`-dimensional error vector `e`* — the single
  object that couples the `N` per-vector contributions. Each vector is scored
  against its own fresh error draw, which is what "`N` independent samples"
  literally means.
- **Preserved:** the sieve database exactly, `N`, `m`, `q`, `sigma_e`.
- **Can it fail?** **YES.** If the coupling were negligible this would match the
  sieve database's variance.

| result (1000 draws) | mean | sd | iid prediction | inflation | `N_eff` |
|---|---|---|---|---|---|
| independent error per vector | +0.407555 | **0.004368** | 0.004416 | **0.98x** | **18319** vs `N = 17919` |

Removing the shared error restores **exact** iid behaviour. Combined with NULL-V,
this pins the mechanism completely: the inflation is entirely attributable to the
shared `e`, and not at all to any property of the database.

### NULL-SWEEP — `m`-sweep and `N`-sweep of the surrogate (CTRL-RT-2)

- **Object removed:** the sieve database (as NULL-V), while additionally varying
  `m` and `N` — the two parameters that would have to control the effect if it
  were, respectively, a small-dimension artifact or a genuine loss of independent
  samples.
- **Preserved:** `a_x`, by reusing the measured `||x||` distribution at every `m`.
- **Can it fail?** **YES.** If the inflation were a loss of independent samples
  from the database, `N_eff` would depend on `N`.

| `m` (`N = 17919`) | sd over `e` | `N_eff` | modeled analytic sd (this task) |
|---|---|---|---|
| 35 | 0.08698 | **44.9** | 0.08735 |
| 70 | 0.06070 | **93.8** | 0.06137 |
| 140 | 0.04458 | **173.8** | 0.04371 |
| 280 | 0.03157 | **349.7** | 0.03065 |

| `N` (`m = 35`) | sd over `e` | `N_eff` |
|---|---|---|
| 1000 | 0.08995 | 42.2 |
| 5000 | 0.08824 | 44.0 |
| 17919 | 0.09159 | 40.6 |
| 60000 | 0.08850 | 43.8 |

`N_eff` grows essentially linearly in `m` (`N_eff/m` = 1.28 / 1.34 / 1.24 / 1.25)
and is **independent of `N`** across a 60x range. Both of
`RT-20260803-4064e1`'s claims are reproduced under contract with independent
code, and the modeled analytic `sd` tracks the measurement to 1-3% at every `m`.

### NULL-T — batch 1's target-null, reproduced and correctly labelled

- **Object removed:** *the LWE structure in the target `b`*. It does **not**
  remove or perturb the sieve database.
- **Can it fail?** **NO.** With `b` uniform on `Z_q^m`, `x.b` is uniform mod `q`
  for every fixed nonzero `x`, so every phase is uniform and every mean score is
  0 in expectation. Any code that reads `b` passes it. Reproduced here only for
  continuity, and reported with that label attached.

Per group, 1000 fresh uniform targets:

| group | mean score | rank of nominal secret within group | `P(nominal first)` |
|---|---|---|---|
| uniform (16) | +0.000001 +/- 0.001315 | 9.139 +/- 4.865 of 17 | 0.055 |
| secret-distribution (8) | -0.000175 +/- 0.004611 | 5.051 +/- 2.571 of 9 | 0.110 |
| near-miss (8) | -0.000206 +/- 0.005300 | 5.043 +/- 1.485 of 9 | 0.002 |
| nominal secret | -0.000215 +/- 0.005326 | — | — |

**This resolves a batch-1 unexplained observation.** `VAL-20260803-535d15`
defect 7 / `EV-MLKEM-da9e3b` OBS-6 recorded that under the null *all 8*
secret-shaped candidates beat the nominal secret (9 of 9, `z = -2.31`) and that
this went unnamed by the producer. Over 1000 fresh null targets the mean rank is
**5.051 +/- 2.571 of 9** — dead mid-pack, exactly as a null must be. Batch 1's
`9 of 9` was a single-draw fluctuation. The near-miss group's `P(first) = 0.002`
is likewise an order-statistic effect: the 8 near-misses are near-copies of the
nominal secret, so the max of 8 nearly always exceeds it under pure noise.

No pooled null rank is computed.

---

## 6. Certificate and integrity

| check | result |
|---|---|
| `certificate.kind` | `lattice_membership` |
| every `v = (x,y)` satisfies `y == A^T x (mod q)` | **17919/17919**, 0 violating entries of 447,975 |
| all-zero vectors | 0 |
| duplicate `y`-parts | 0 (all 17,919 distinct — reproduces a batch-1 structural fact) |
| method | numpy int64 integer arithmetic from `A` and the reconstructed lattice vectors, independent of g6k's internal representation |
| independent identity check | `x.b - y.c == x.e + y.(s-c) (mod q)` recomputed by two different routes for all 34 candidates x 17,919 vectors: **exact equality** |
| solve-claim certificate | **none** — no discrete-log solve and no factor-base relation is claimed |
| replicate instances | 9/9 certificates verified, 0 violating entries |

**Free reproduction check of batch 1.** The primary instance deliberately reuses
batch 1's instance/candidate/sieve/fpylll seeds. The rebuilt instrument produced
`N = 17919` vectors with `||v||^2` min 218 / median 315 / max 329 and mean
311.405 — identical to `BATCH-d2a728`, in a freshly built venv. Sieve 16.28 s
(batch 1: 16.55 s).

**Emitted for reviewers (`RT OBJ-3`):** `vectors.json`, 3,751,898 bytes,
sha256 `7f8c545da970d37c20a0e12ae169dd5305f9376d38c86bc9c7cb5d12aceed343`,
containing `x` and `y` for all 17,919 vectors plus `A`, `s`, every candidate, and
the certificate — so a reviewer can score any candidate and re-verify the
certificate without re-running the sieve, and without relying on the *accidental*
recoverability RT had to exploit in batch 1.

---

## 7. Instance replication (inherited CTRL-RT-5) — added, not requested

`RT-20260803-4064e1` recorded CTRL-RT-5 as `NOT RUN` and named
instance-to-instance variance as the one uncertainty neither reviewer could
bound. This batch runs **9 further independent instances** (fresh `A`, `s`,
sieve, candidates), 500 error draws each, 4500 draws in total. All 9 certificates
verified. This is an **addition** to the card's protocol and is recorded as such
in S9.

| quantity (per instance: mean +/- sd over 500 draws) | mean across 9 instances | sd across instances | min | max |
|---|---|---|---|---|
| correct-secret mean score | 0.410109 | **0.00407** | 0.402309 | 0.415228 |
| ingredient-1 global ratio (measured/predicted) | **0.98771** | **0.00968** | 0.970229 | 0.998990 |
| ingredient-2 uniform sd ratio to `sqrt(1/2N)` | **1.00207** | **0.05209** | 0.926140 | 1.083721 |
| near-miss paired delta vs best of 8 | **0.001571** | **0.000043** | 0.001483 | 0.001647 |

`P(correct first within near-miss)` per instance:
0.996 / 0.988 / 0.990 / 0.988 / 0.992 / 0.990 / 0.972 / 0.992 / 0.988
(primary instance: 0.986).
`P(correct first within uniform)`: **1.000 in all 9**.

Two consequences worth recording:

1. **The ~20% "unreported uncertainty" of `OBS-4` is a within-instance
   error-draw spread, not an instance-to-instance spread.** The correct-secret
   mean has sd 0.089 over error draws but only **0.0041 across instances** — 22x
   smaller. Every ingredient ratio in this report is therefore far better
   determined across instances than the per-draw sd suggests.
2. **The near-miss departure replicates.** Its paired delta varies by
   +/-0.000043 across 10 independent instances — 2.7% relative. It is no longer a
   single-instance observation.

---

## 8. Where batch 1's single realisation sits

| candidate | batch-1 single draw | resampled mean +/- sd (2000 draws) | z |
|---|---|---|---|
| correct | +0.427375 | +0.407926 +/- 0.089049 | +0.22 |
| `zero_vector` | +0.338447 | +0.328049 +/- 0.072180 | +0.14 |
| `nearmiss_00` | +0.424413 | +0.405292 +/- 0.088468 | +0.22 |
| `uniform_00` | +0.000679 | -0.000575 +/- 0.004592 | +0.27 |
| `secretdist_00` | +0.280397 | +0.273048 +/- 0.060586 | +0.12 |

Batch 1's realisation is an unremarkable draw (`RT OBJ-3` reported +0.29 sd on a
different random stream; reproduced at +0.22 sd here). Nothing in batch 1's
headline numbers was a lucky draw.

---

## 9. Protocol deviations, additions, and anomalies — all recorded

| id | class | what |
|---|---|---|
| D-1 | **addition** | 9 replicate instances (inherited CTRL-RT-5) were run. Not requested by the card; added because RT named instance variance as unbounded. S7. |
| D-2 | **addition** | A `zero_vector` reference candidate (group `reference_zero`) was added, so the R-A "pure distinguisher" reading of the law has a measurable counterpart (`wellposedness.md` S5). Reported separately; **never pooled** into the three wrong-candidate groups. |
| D-3 | **addition** | NULL-IID was run in addition to the required vector-null and `m`-sweep. S5. |
| D-4 | **addition** | Two post-hoc diagnostics (D1 discretisation, D2 sample-sd bias) computed **after** the single run from the archived `vectors.json`/`results.json`. The frozen comparison was **not** re-scored; both are reported alongside it. Source and output verbatim in `rebuild_transcript.txt`. |
| D-5 | **deviation** | Null/sweep statistics use **1000** error draws rather than the primary's 2000, to stay inside the wall-clock budget. Every reported quantity still carries at least 1000 draws, as the completion gate requires. |
| D-6 | **deviation** | The primary instance deliberately reuses batch 1's instance/candidate/sieve/fpylll seeds, so it is the *same* database, not an independent one. Deliberate: it makes batch-2 statistics directly comparable and yields a free reproduction check. Instance independence is supplied separately by S7. |
| D-7 | **anomaly (instrument)** | Rebuild reproduced KN-TECH-14efa5's fpylll figure exactly but gave `gauss_sieve` db 4166 vs the recipe's 4075; the recipe pins no seed for that check. S1. |
| D-8 | **anomaly (executor error)** | The executor's own instrument-verification script failed on `sage.__version__` before being corrected. `implementation_error` in the check, not an instrument failure. The failure is kept verbatim in the transcript. |
| D-9 | **observation** | `MATZOV.Hf` returns bits while `log p` and `log(1/mu)` in the same sum are nats (KA-4). Recorded as an observation about the callable; no claim that the estimator is wrong. |
| D-10 | **observation** | Ingredient 1 shows a small monotone shape residual that batch 1's precision could not resolve, and post-hoc D1 attributes most of it to the law's continuous-Gaussian idealisation of a discretised error. S3. |
| D-11 | **record** | The soft wall-clock guard (`--max-seconds 1000`) was never triggered; all 9 replicates ran. Total 312.8 s, peak RSS 795.1 MB against a 6 GB cap. |

**No run was discarded, repeated for a better result, or omitted.** One smoke run
and one official measurement run were executed; both are in the transcript.

---

## 10. What this batch does NOT establish

- **Nothing about ML-KEM.** No break, no security proof, no FIPS 203 parameter
  set affected or cleared, no cost claim, no speedup, no attack.
- **No statement about FIPS 203 dimensions.** This batch asserts no numbered
  extrapolation heuristic. `H-SCALE-1` as offered by RT is *already known
  incomplete* — this batch's own `m`-sweep confirms `N_eff` is not a function of
  `(a_x, N)` alone — and it is not adopted here.
- **That the independence law is validated or refuted.** Both are Reviewer /
  Coordinator judgements. This report records that ingredient 1 and the uniform
  arm of ingredient 2 agree at the stated tolerances, and that the near-miss arm
  departs, at this configuration.
- **That the near-miss departure means anything at cryptographic scale.** The
  measurement sits at per-vector advantage about 0.41; the law's operating point
  at cryptographic `N` is of order `1e-8` (`RT OBJ-7`). The regimes are
  qualitatively different.
- **That sieve structure matters.** It is *measured* to matter less than a
  random-direction surrogate can distinguish (NULL-V, 0.3%). RT's `HC-2`
  relation count (7,248 + 10,041 exact 3-term relations) is real structure, and
  this batch measures no statistic sensitive to it. The `PAC-1` identifiability
  objection stands unrefuted.
- **Any comparison against `MATZOV.Nf` as a whole.** None exists; see
  `wellposedness.md`.
- **That the length sub-comparison (S3, `wellposedness.md` S5) is a departure.**
  One toy configuration, no null of the right shape for a length claim.

## 11. Pareto position

`dominated_by`: any version of this measurement at more than one `(m, q)` pair,
or with a statistic sensitive to the exact 3-term relations, would dominate it on
every claim it makes. Checked against the frontier rows this batch could affect:
time, memory, and data/queries are all unclaimed, because no attack is proposed.

`sota_delta`: **none claimed.** No attack is improved, no exponent moved, no cost
reduced. The contribution is that a well-posedness question was answered
negatively with a proof-by-enumeration, that the law's separable ingredients were
measured against error bars and replicated across instances, and that the
largest apparent effect in the data was shown to be a controlled null by two
independent routes.

---

## Artifacts

All seven declared deliverables are present; byte counts and sha256 values for
each are recorded in `receipt.json`.

| file | role |
|---|---|
| `rebuild_transcript.txt` | step 0 rebuild + smoke run + official run + post-hoc diagnostics, verbatim |
| `wellposedness.md` | P1: the declaration that no tuple exists, with the reasoning |
| `compare.py` | the exact script run |
| `vectors.json` | `x` and `y` for every sieve vector, plus `A`, `s`, candidates, certificate |
| `results.json` | P1/P1b/P2/P3 machine-readable, per candidate group, mean +/- sd |
| `report.md` | this file |
| `receipt.json` | state, commands, environment, timestamps, policy and resolved model |
