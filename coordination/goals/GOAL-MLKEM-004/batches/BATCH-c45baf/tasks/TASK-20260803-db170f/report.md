# TASK-20260803-db170f — Stage A replication, then the successor design

**BATCH-c45baf (batch 3 of 6) / GOAL-MLKEM-004 / executor**

**SCOPE, binding on every sentence below.** m=35, n=25, q=127, secret
centred-binomial eta=2, error rounded-Gaussian sigma=2, g6k `bgj1_sieve`. **TOY
SCALE.** No ML-KEM break claim. No security proof. No FIPS 203 parameter set
affected or cleared. No speedup. No cost claim. No numbered extrapolation
heuristic to FIPS 203 dimensions is asserted. AGENTS.md **rule 12 is UNMET and
UNWAIVED**, inherited: this task changes the status of no `EV-MLKEM-*` record
and no `KN-*` entry, and proposes no change. This report states
**observations**; it does not conclude that any heuristic is validated or
refuted — that judgement belongs to the Reviewer and the Coordinator.

---

# 1. STAGE A VERDICT — FIRST AND UNAMBIGUOUS

> ## THE SEPARATION REPLICATES. IT IS NOT AN ARTIFACT OF ONE INSTANCE.
>
> On **all nine** replicate instances of BATCH-f75059, the row-permutation
> surrogate — which preserves the exact multiset of `x`, the exact multiset of
> `y` and every column marginal, and removes **only** which `y` pairs with
> which `x` — separates the real sieve database from its surrogate on both
> statistics the card named, in the **same direction** and at **comparable
> magnitude** to RT-20260803-dc7568's single-instance computation.
>
> | statistic | batch 2, 1 instance | **this task, 9 instances** |
> |---|---|---|
> | near-miss sd ratio, real | 0.142888 | **0.140324 +- 0.002260** |
> | near-miss sd ratio, permuted | 0.105408 +- 0.000991 | **0.106552 +- 0.000603** |
> | excess (real/permuted) | 1.356 (+35.6 %) | **1.3169 +- 0.0188 (+31.7 %)** |
> | sign agreement | — | **9 of 9 above 1**, pooled z = **+50.6** |
> | correct - best-of-8 near-miss, real | 0.001522 | **0.001547 +- 0.000032** |
> | correct - best-of-8, permuted | 0.001761 +- 0.000011 | **0.001740 +- 0.000025** |
> | excess (real/permuted) | 0.864 (-13.6 %) | **0.8893 +- 0.0115 (-11.1 %)** |
> | sign agreement | — | **9 of 9 below 1**, pooled z = **-28.8** |
>
> ## AND IT DOES NOT DECAY LIKE ITS SURROGATE.
>
> The surrogate's near-miss spread decays **exactly** as 1/sqrt(N'), so its
> ratio is flat. The real database's does not. Excess, pooled over 9 instances:
>
> | N' | 500 | 2000 | 8000 | 17919 |
> |---|---|---|---|---|
> | surrogate ratio | 0.105557 +- 0.001768 | 0.106222 +- 0.000724 | 0.106614 +- 0.001328 | 0.106552 +- 0.000603 |
> | real ratio | 0.107079 +- 0.003689 | 0.110822 +- 0.001564 | 0.122380 +- 0.003139 | 0.140324 +- 0.002260 |
> | **excess** | **1.0146 +- 0.0374** | **1.0434 +- 0.0174** | **1.1480 +- 0.0310** | **1.3169 +- 0.0188** |
> | batch 2 (1 instance) | 1.062 | 0.987 | 1.193 | 1.354 |
> | instances with excess > 1 | 8 of 9 | 9 of 9 | 9 of 9 | 9 of 9 |
>
> The excess is **monotone increasing in N'** on the pooled means and on every
> one of the nine instances individually from N'=2000 upward. The canonical
> artifact tell — a quantity that fails to decay when the parameter meant to
> destroy it increases — **fires here in the direction that says the effect is
> not a sampling artifact**, and it does so with nine instances rather than one.
>
> **The alternative outcome did not occur.** A separation that decayed like its
> surrogate across nine instances would have been dead and this report would
> have said so plainly in this box. It did not decay.

**What this verdict is NOT.** It is nine instances of one design at dimension
60 with q=127, one sieve algorithm, one modulus. It is not evidence that the
dual-attack independence heuristic fails at cryptographic scale, not a
statement about ML-KEM, and not a cost claim. Section 5 records a Stage B
observation that cuts directly against reading it too broadly.

---

# 2. Step 0 — the rebuild

Verbatim in `rebuild_transcript.txt` (798 lines, every command echoed before it
runs, every output captured including exit codes).

- **Fresh venv `/tmp/sagevenv-c45baf`**, created by `python3 -m venv` after
  `rm -rf`. `/tmp/sagevenv` and `/tmp/sagevenv-f75059` are **never invoked** by
  this task — grep the transcript.
- `passagemath-standard 10.8.7` installed from binary wheels; `fpylll 0.6.4`
  arrives with it; `g6k 0.1.2` built from source with **both**
  KN-TECH-14efa5 fixes applied (`--no-build-isolation`, and a self-supplied
  `libgmp.so` symlink with `LIBRARY_PATH`/`LDFLAGS`).
- **V1-V5 all PASS**, `ALL_PASS True`:
  - numpy 2.4.6.
  - `sage.version.version = 10.8.7`; the **shim discriminator** works
    (`PowerSeriesRing` returns `1 + t + t^2 + t^3 + t^4 + O(t^5)`) and, checked
    from inside the interpreter, **no shim directory is on `sys.path`**.
  - fpylll: the recipe's **broken default is confirmed broken** —
    `BKZ.EasyParam(30)` raises `RuntimeError: Cannot open strategies file.` —
    and the in-process `Strategy` fix works: dim 60 qary q=3329, BKZ-30 x4,
    `||b0|| 10744.2 -> 129.6` in 0.38 s.
  - g6k: all five kernels exposed; dim 50 qary q=3329 `gauss_sieve` -> db 4259
    vectors in 0.88 s.
  - the `Siever(GSO.Mat(A))` gotcha reproduces: `ValueError: Siever requires
    UinvT enabled`.
- Pinned lattice-estimator at `/tmp/le`, commit
  `3e48ef421ec256afddb3e7d2249a77eab6e9ba12`, **clean tree**.

**Rebuild anomalies, recorded not explained away** (see section 7, D-2..D-4).

## The instances are BATCH-f75059's own, proved

Stage A regenerates the nine replicates from BATCH-f75059's **own seeds**
(`20260803206 + 1000*r`, fpylll `+1`, sieve `+2`, candidates `+3`). `a_x` is a
deterministic function of the instance and consumes no error draws, so it must
agree to all digits if the instances are identical. It does, on all nine:

```
rep 0..8:  N = 17919/17919 for all nine
           |a_x(this) - a_x(BATCH-f75059)| = 0.00e+00 for all nine
```

All nine `lattice_membership` certificates verified independently of g6k by
integer arithmetic from `A` and the reconstructed vectors: **0 violating
entries** of 9 x 17919 x 25 = 4,031,775 checked, 0 all-zero vectors, 0
duplicate `y` parts. `certificate.solve_claim_certificate` is `none`: this task
claims **no discrete-log solve and no factor-base relation**; the certificate
certifies the vectors, not any inference from their scores.

---

# 3. Stage A — full results, per candidate group, never pooled across groups

Every quantity: **2000 error draws** per arm per instance, **10 independent
row-permutation realisations**, all arms sharing one error-draw sequence so
every comparison is **paired by construction**. Pooled = mean +- sd **across
the nine instances** (ddof=1), the aggregation rule declared in `stage_a.py`'s
header before the run.

## 3.1 near_miss (8 candidates, `s + e_k`, BATCH-f75059's definition)

| arm | sd ratio to iid | correct - best-of-group |
|---|---|---|
| **real** | **0.140324 +- 0.002260** | **0.001547 +- 0.000032** |
| NULL-ROWPERM (10 realisations) | 0.106552 +- 0.000603 | 0.001740 +- 0.000025 |
| NULL-RANDDIR (5) | 0.107115 +- 0.001365 | 0.001812 +- 0.000019 |
| NULL-COLPERM (5) | 0.106439 +- 0.001170 | 0.001742 +- 0.000018 |
| SENS-2 rearrangement max | 0.109733 +- 0.002654 | 0.001668 +- 0.000033 |
| SENS-2 rearrangement min | 0.110018 +- 0.002630 | 0.001774 +- 0.000032 |
| SENS-2c length-sorted pairing | 0.105860 +- 0.003042 | 0.001664 +- 0.000038 |
| SENS-1 `y := 0` | 0.000000 +- 0.000000 | 0.000000 +- 0.000000 |

`P(correct first within near-miss)`: real 0.9870 +- 0.0031, rowperm
0.9956 +- 0.0009, randdir 0.9966 +- 0.0009, colperm 0.9955 +- 0.0008.

Per-instance excess (real/rowperm), sd ratio:
`1.3056 1.2901 1.3461 1.3130 1.2969 1.3403 1.3112 1.3220 1.3274`
correct-best: `0.9010 0.9095 0.8746 0.8890 0.8943 0.8773 0.8928 0.8865 0.8786`

RT-20260803-dc7568's `randx_randy` values (0.104707 +- 0.001475 and
0.001808 +- 0.000011) are reproduced here at 0.107115 +- 0.001365 and
0.001812 +- 0.000019 on nine different instances with independent code.

## 3.2 uniform (16 candidates) — NO separation

| statistic | real | rowperm | excess | pooled z vs 1 |
|---|---|---|---|---|
| sd ratio to iid | 1.000466 +- 0.053953 | 0.991916 +- 0.051939 | 1.0087 +- 0.0192 | +1.37 |
| correct - best | 0.399046 +- 0.002052 | 0.399141 +- 0.001988 | 0.9998 +- 0.0004 | -1.75 |

5 of 9 instances above 1 on the sd ratio. This is what a group with no
detectable dependence on the pairing looks like, measured on the same nine
instances with the same code — an internal contrast to 3.1, not an external one.

## 3.3 secret_distribution (8 candidates) — a SMALL separation, 9 of 9, NOT in batch 2's table

| statistic | real | rowperm | excess | pooled z vs 1 | 9/9? |
|---|---|---|---|---|---|
| sd ratio to iid | 3.412228 +- 1.451964 | 3.338147 +- 1.440595 | 1.0254 +- 0.0113 | +6.78 | 9 of 9 above |
| correct - best | 0.100765 +- 0.024665 | 0.098459 +- 0.024253 | 1.0238 +- 0.0022 | +32.42 | 9 of 9 above |

**Unexpected observation, recorded not discarded** (section 7, OBS-A1). The
secret-distribution group separates too, at about +2.4 % rather than the
near-miss group's about +32 %, and unanimously across instances. Batch 2's
table did not report this group under the row-permutation null. Note the
**direction** differs from the near-miss group's `correct - best` (there the
real database scores *worse*, here *better*), and the group's own
across-instance sd is huge (1.45 on 3.41), so the excess is far better
determined than the level.

---

# 4. Null sufficiency — object, statistic, and sensitivity demonstration (PD-2)

DEC-20260803-264d6a PD-2 requires all three for **every** null. Naming the
object is necessary and not sufficient. Full machine-readable registry:
`stage_a_results.json -> nulls`, `stage_b_results.json -> nulls`.

## 4.1 SENS-0 — the proof of batch 2's defect, and it applies to this task too

**Object**: the x-y pairing. **Statistic**: the correct-secret score
`mean_i cos(2 pi x_i.e/q)` — NULL-V's statistic.
**Sensitivity demonstration: NONE EXISTS, provably.**

The correct candidate's phase offset is `y_i.(s - s) = 0` for every `i`,
whatever `y` sits in row `i`. So the correct-secret score is **bitwise
unchanged** by any row permutation of `Y`, and its power against this null is
**exactly zero**. Verified numerically on all nine instances:
`max |delta| = 0.0` exactly, over 10 realisations x 2000 draws x 9 instances.

This is why batch 2's NULL-V could not fail. Under PD-2 that (object,
statistic) pair is **not an admissible null**, and this task does not use it as
one.

## 4.2 NULL-ROWPERM — the null under test

- **Object removed**: which `y` pairs with which `x`, i.e. membership of the
  pair in `L = {(x,y) : y = A^T x mod q}`. Nothing else.
- **Preserved**: exact multiset of `x` rows, exact multiset of `y` rows, every
  column marginal of `X` and of `Y`, every `||x||`, every `||y||`.
- **Statistic**: near-miss / uniform / secret-distribution sd ratio, correct -
  best-of-group, `P(correct first)`. Per group, never pooled.
- **The statistic reads the object, structurally**: near-miss candidate `k` is
  `s + e_k`, so its phase offset is exactly `-Y[i,k]` — the statistic evaluates
  `Y` in the **same row** as `x_i`. Change the pairing and every near-miss
  score changes.

### Sensitivity demonstrations, and which one serves which statistic

**SENS-1 — `y := 0` (analytic, verified).** Every phase offset becomes 0, so
all candidate scores collapse onto the correct one: near-miss sd ratio exactly
0 (measured max 6.2e-15 over nine instances) and correct - best exactly 0.0.
Against real values about 0.140 and about 0.00155. **The statistics read `y`.**

**SENS-2 — the rearrangement bound (ANALYTIC, inside the null's own object
class).** Because the rounded Gaussian is symmetric, `E_e[sin(2 pi x.e/q)] = 0`
*exactly*, so for any pairing pi

```
E_e[score_j]  =  mean_i  w_i * cos(phi_{pi(i),j}),   w_i = E_e[cos(2 pi x_i.e/q)]
```

with `w_i` computed exactly from the discrete rounding probabilities (not from
the continuous-Gaussian idealisation — that is BATCH-f75059's D1/Sheppard
correction, and using it here would have been an error). By the **rearrangement
inequality** the maximum and the minimum of that expectation **over the class
of all N! pairings** are obtained by co-sorting and anti-sorting `w` against
`cos phi`. Both extremal pairings preserve both multisets and every column
marginal. Instance 0, near-miss candidate 0:

| pairing | predicted delta from real | measured delta from real |
|---|---|---|
| rowperm (realisation 0) | +6.886e-05 | +7.026e-05 |
| rearrangement **max** | +4.576e-04 | +4.563e-04 |
| rearrangement **min** | -3.777e-04 | -3.729e-04 |

Agreement to <= 3.8e-05 across all nine instances, against an effect of
4.6e-04. The identity holds and the extremal pairings **provably differ**. On
the **correct - best-of-group** statistic this demonstrates sensitivity
directly: paired z = **-12.2** between the two extremal pairings.

**SENS-2 is NOT sufficient for the sd-ratio statistic, and I record that rather
than hide it**: paired z = 3.21, below the |z| > 5 criterion declared before the
run. The rearrangement construction is extremal for the *per candidate mean
score*, which is the wrong functional for a *spread across candidates*. Its
analytic range on that statistic is only 8.35e-04.

**SENS-3 — dose-response (measured, inside the null's own object class).**
`pi_t` shuffles a random subset of `round(t*N)` rows and fixes the rest; every
`pi_t` preserves both multisets and every column marginal, and `t` **is** the
fraction of the pairing removed. Pre-declared prediction, written into the
script before the run: *a statistic that reads the pairing is monotone in `t`;
one blind to the pairing is flat in `t`.* Pooled over nine instances:

| t | 0.00 (real) | 0.05 | 0.20 | 0.50 | 0.80 | 1.00 (full rowperm) |
|---|---|---|---|---|---|---|
| near_miss sd ratio | 0.140324 | 0.136897 | 0.128694 | 0.114948 | 0.109177 | 0.107382 |
| near_miss correct-best | 0.001547 | 0.001570 | 0.001624 | 0.001710 | 0.001736 | 0.001737 |
| **uniform** sd ratio | 1.000466 | 0.998114 | 0.995518 | 0.987232 | 0.997834 | 0.995123 |
| **uniform** correct-best | 0.399046 | 0.399055 | 0.399078 | 0.399204 | 0.399066 | 0.399049 |

The near-miss curves are **monotone in `t` on the pooled means for both
statistics** and the response is **graded**, not a step. The uniform curves are
**flat** (every value within 0.005 of the mean, against an across-instance sd
of 0.054), and strict per-instance monotonicity holds for 0 of 9 instances
there. That contrast is the demonstration: the same statistic, the same code,
the same nine instances, responding to `t` in one group and not in another.

**Honest limit**: strict per-instance monotonicity for near_miss is 5/9 (sd
ratio) and 1/9 (correct-best), because the curve flattens between t=0.8 and
t=1.0 where consecutive steps are inside the noise. The pooled curves are
monotone; the per-instance ones are monotone where the steps exceed noise.

## 4.3 NULL-RANDDIR and NULL-COLPERM

- **NULL-RANDDIR** removes everything except the two length multisets (`x` and
  `y` both replaced by random directions of matched norm). Same statistic; same
  demonstrations apply unchanged.
- **NULL-COLPERM** removes the joint structure of `Y` across its own
  coordinates by permuting each column independently, preserving every column's
  exact empirical marginal and the whole of `X`. Same statistic; near-miss
  candidate `k` reads column `k` in row `i`, so it reads the object.

Both land at the same place as NULL-ROWPERM (3.1), which locates the effect in
the **x-y pairing** rather than in column-marginal heterogeneity — reproducing
RT-20260803-dc7568's `realx_colperm` finding on nine instances.

---

# 5. Stage B — the successor design

Stage B was **reached**. Stage A was complete and written to disk
(`stage_a_results.json`, 1,543,241 bytes) before Stage B began.

## 5.1 The Nf tuple, stated explicitly, and its admissibility

Adopting `k_lat = 15`, `k_fft = 10`, `p in {2,3,5}`, `beta_sieve = 50`:

> **`(m = 35, k_enum = 0, k_fft = 10, p in {2,3,5}, beta_bkz = irrelevant,
> beta_sieve = 50)`, with `k_lat = 15`.**

**ADMISSIBLE**, checked against the line-540 identity with the pinned
estimator's own callable (`/tmp/le`, `3e48ef4`, clean tree):

```
estimator/lwe_dual.py:540   k_lat = params.n - k_fft - k_enum   # p.15
                            15    = 25      - 10    - 0          OK  (KA-1)
```

`k_lat + k_fft + k_enum = 15 + 10 + 0 = 25 = n`. The obstruction
BATCH-f75059's P1 hit — R1 forcing `k_lat = n` while R2 forced
`k_enum + k_fft = n` — **does not arise**: `m + k_lat = 35 + 15 = 50 =
beta_sieve` (KA-2), so the sieve runs on exactly the lattice `Nf` describes
**without** forcing `k_enum + k_fft = 0`. `beta_bkz` drops out again because
`deltaf(beta_bkz)^(m + k_lat - beta_sieve)` has exponent 0; verified as
`Nf(beta_bkz=45) == Nf(beta_bkz=60) == Nf(beta_bkz=300)` exactly (KA-3).

All 8 known-answer controls PASS, including the callable-identity checks and an
independent re-derivation of `Nf`'s factorisation from the source at
`lwe_dual.py:551-555` compared against the callable's return value (KA-4).

## 5.2 The adjacent-FFT-bin term — turned ON. **MODELED, not measured.**

`exp(k_fft/3 * (sigma_s pi/p)^2)`, with `sigma_s = 1` exactly for centred
binomial eta=2:

| p | adjacent-bin term | log2 | `Nf` at the tuple (modeled) |
|---|---|---|---|
| 2 | **3731.89** | **2^11.8657** | 45128.8 |
| 3 | **38.6833** | **2^5.2736** | 716.55 |
| 5 | **3.72828** | **2^1.8985** | 99.2663 |

In the BATCH-f75059 design (`k_fft = 0`) this term is **exactly 1.0** —
verified to 1e-15 (KA-5) — which is why batch 2 could not test it in either
direction.

**Reference figure, MODELED and reproduced here from the pinned estimator's own
arithmetic**: at ML-KEM-512's `Xs = CBD(eta=3)` with the estimator's optimum
`k_enum = 0`, `k_fft = 40`, `p = 5`, the term is **2685.6647 = 2^11.391**,
reproducing the card's and RT-20260803-dc7568 section 6(b)'s 2685.7 = 2^11.39
(KA-6). **This is arithmetic inside a cost model at FIPS 203 parameters. It is
not a measurement, not an extrapolation of anything this task measured, and
asserts nothing about ML-KEM's security.** Rule 4 applies in full.

## 5.3 The measurement — and a null result I am NOT entitled to call blindness

3 instances, sieve dimension `m + k_lat = 50`, N = 4253 vectors each, all three
`lattice_membership` certificates verified independently of g6k (0 violating
entries). 2000 error draws, 10 row-permutation realisations, scoring verified
against a fully independent route (build `b = As+e`, score bins directly) to
**2.0e-15**. Near-misses now have the **principled definition** the design
buys: **adjacent FFT bins** `c* +- e_j mod p`, 20 of them (10 for p=2, where
`+1 = -1`).

| p | group | real sd ratio | rowperm sd ratio | excess |
|---|---|---|---|---|
| 2 | near_miss (adjacent bins) | 1.074121 +- 0.031468 | 1.117909 +- 0.015952 | 0.9607 +- 0.0187 |
| 3 | near_miss (adjacent bins) | 1.049051 +- 0.051282 | 1.040532 +- 0.060075 | 1.0088 +- 0.0281 |
| 5 | near_miss (adjacent bins) | 0.989018 +- 0.113754 | 1.013190 +- 0.115843 | 0.9762 +- 0.0228 |

Full per-group tables (uniform, secret_distribution, near_miss; all three `p`)
in `stage_b_results.json -> B3_pooled`. **No separation was detected on any
group statistic at any `p`**: every excess lies within about one to two
across-instance sd of 1, and the sign is not consistent across `p`.

### The structural improvement this design does deliver

Unlike BATCH-f75059's design, the **correct bin's own score reads the
pairing**: because `k_lat < n`, `s_lat` is never guessed and its contribution
`psi_i = 2 pi (y_lat,i . s_lat)/q` stays in the residual. Stage A's SENS-0 —
bitwise invariance of the correct-candidate score under a row permutation —
**does not apply here**, and the measurement confirms it: the correct bin moves
under NULL-ROWPERM with paired |z| median 14.8-31.3 and max 101.0. **The
successor design supports a null the batch-2 design structurally could not.**

### PD-2 APPLIED TO MY OWN RESULT — the Stage B null is NOT sufficient

For the Stage B **group** statistics I ran the sensitivity demonstrations and
**they did not succeed**:

- **SENS-1** (`y_lat := 0`) barely moves the near-miss sd ratio: 1.09472 ->
  1.14012 (p=2), 0.99013 -> 0.98734 (p=3), 1.10933 -> 1.15401 (p=5).
- **SENS-3** dose-response is **not monotone in `t` on 0 of 3 instances** for
  any `p`; the p=2 curve drifts *upward* with `t` (1.074 -> 1.183) and p=3/p=5
  wander inside their noise.

**Therefore, under PD-2, I do not report Stage B's group-level null result as
blindness, absence of an effect, or a negative observation about the design.**
I have not demonstrated that those group statistics can read the pairing in
this design, so "no separation detected" is **exactly as uninformative as batch
2's NULL-V was**, and calling it more would repeat the error this batch exists
to avoid. The one Stage B statistic with a demonstrated sensitivity — the
correct bin's score — **does** move under the null.

What Stage B's B3 section therefore supports: the measurement ran, the
certificates verified, the principled near-miss group exists and its raw sd
ratio is about 1.0 rather than batch 2's about 0.14 (an observation about the
two definitions, section 7 OBS-B1), and the design admits a null that batch 2's
did not. Nothing more.

---

# 6. Budget and runs — every attempt recorded

| | allowed | used |
|---|---|---|
| wall clock | 3000 s | **about 578 s** of measured compute (rebuild 306 s, Stage A 258.9 s, Stage B 9.7 s, smoke 3.5 s) |
| memory | 6 GB | peak RSS **561.8 MB** (Stage A), 442.4 MB (Stage B); `RLIMIT_AS` set to 6 GB inside both scripts |
| measurement runs | 2 | **2** (one Stage A, one Stage B) |
| smoke runs | — | **5**, all recorded in `receipt.json`, all writing only to scratch, none touching an archived artifact |
| discarded / repeated / unreported runs | — | **0** |

No soft wall-clock guard triggered; all 9 Stage A instances and all 3 Stage B
instances ran to completion.

---

# 7. Deviations, anomalies and unexpected observations — recorded, none discarded

| id | class | what |
|---|---|---|
| D-1 | record | Fresh venv at `/tmp/sagevenv-c45baf`, following KN-TECH-14efa5's `/tmp/sagevenv` pattern. `/tmp/sagevenv` and `/tmp/sagevenv-f75059` were never invoked. |
| D-2 | anomaly_instrument | dim-50 `gauss_sieve` db **4259** vectors against the recipe's 4075 and BATCH-f75059's 4166. The recipe pins no seed for this check; I pinned `FPLLL.set_random_seed(20260803)`, which the recipe's own run did not. Recorded, not explained away. |
| D-3 | anomaly_instrument | My BKZ "before" figure (10744.2) is measured **pre-LLL**, so it is not comparable to the recipe's 160.4. The post-BKZ value 129.6 vs the recipe's 130.3 is the comparable one. My check, not the instrument, differs. |
| D-4 | deviation | I applied both KN-TECH-14efa5 link fixes **preemptively** rather than reproducing the two failures first. So this rebuild confirms the recipe **works**; it does **not** re-establish that either fix is necessary in this container today. |
| D-5 | deviation | Scores use the cosine addition formula rather than BATCH-f75059's modular route, so that every null arm shares one set of transcendentals and is paired by construction. Mathematically identical; verified against the modular route at **3.1e-14** (Stage A) and against a fully independent `b = As+e` route at **2.0e-15** (Stage B). |
| D-6 | deviation | Stage A uses **2000** error draws per arm (BATCH-f75059's replicates used 500) and **10** row-permutation realisations (RT-20260803-dc7568 used 5). Both exceed the card's >=1000 requirement. |
| D-7 | deviation | In the decay control the row permutation is applied **within** the subsample of size N', so the surrogate's y-multiset matches the subsample's own. RT-20260803-dc7568's script is scratch and not archived, so whether it did the same is unknown. If it did not, its N'<full points confound the null with the subsampling; mine do not. |
| D-8 | deviation | My first-choice sensitivity demonstration (SENS-2c, pairing by matched length rank) **failed** to move the statistic at smoke scale. It was replaced by the rearrangement construction and the dose-response **before** the official run; SENS-2c is retained and reported (3.1) because its null result is informative about what the statistic reads. No official run was repeated. |
| D-9 | deviation | Stage B ran **3** instances, not 9. Its across-instance sd carries 2 degrees of freedom and is correspondingly weak. |
| D-10 | deviation | Stage B's group-level null carries **no sufficient sensitivity demonstration** and is reported as inadmissible for a blindness conclusion (5.3). |
| OBS-A1 | observation | **The secret_distribution group separates too**, 9 of 9 instances, excess 1.0254 +- 0.0113 (sd ratio) and 1.0238 +- 0.0022 (correct - best), pooled z +6.78 and +32.42. Batch 2's table did not report this group under the row-permutation null. The magnitude (about +2.4 %) is an order of magnitude below the near-miss group's, and the **sign of the `correct - best` effect is opposite** to the near-miss group's. |
| OBS-A2 | observation | The near-miss excess is **monotone increasing in N'** across 500 -> 17919 on the pooled means, and the surrogate's ratio is flat to within 0.001 across a 36x range of N'. At N' <= 2000 the excess is 1.01-1.04 and would not have been detected; RT-20260803-dc7568's own "invisible at N' <= 2000" caveat is confirmed on nine instances. |
| OBS-B1 | observation | Under the **principled** near-miss definition (adjacent FFT bins) the raw sd ratio is **about 1.0**, not batch 2's about 0.14. The 6.7x-concentration that batches 1-2 measured is a property of the **ad-hoc `s + e_k` definition**, whose phase offset `-Y[.,k]` is small, not of near-misses in general. An adjacent FFT bin differs by a full bin and decorrelates. This is an observation about two candidate definitions, not about the independence heuristic. |
| OBS-B2 | observation | Stage B's `Nf` at the adopted tuple spans 99.3 (p=5) to 45129 (p=2) — a 454x range driven almost entirely by the adjacent-bin term. The design's `p` choice is therefore not a detail. MODELED. |
| A-1 | anomaly_executor_error | None of my scripts failed during an official run. The four Stage A smoke runs exist because two designed-in sensitivity demonstrations (SENS-2 as originally written; SENS-2's aggregation helper) were found inadequate or buggy at smoke scale and fixed before the official run. All four are recorded in `receipt.json`. |

---

# 8. Explicit non-claims

- No ML-KEM break. No attack implemented, run, or claimed. No speedup.
- No security proof and no security claim in either direction.
- No FIPS 203 parameter set affected or cleared. dim 60 / dim 50, q = 127 is
  toy scale and AGENTS.md rule 4 applies in full.
- **No numbered extrapolation heuristic to FIPS 203 dimensions is asserted.**
  The 2^11.391 figure in 5.2 is the pinned estimator's own arithmetic at
  ML-KEM-512 parameters, labelled MODELED, and is not derived from any
  measurement in this task.
- **No conclusion that the dual-attack independence heuristic is validated or
  refuted.** Stage A replicates a separation on 9 toy instances of one design;
  that judgement belongs to the Reviewer and the Coordinator.
- **No blindness conclusion from Stage B.** Section 5.3 states why I am not
  entitled to one.
- `certificate.kind` is `lattice_membership` only, in both stages. It certifies
  the vectors, not any inference from their scores. **No discrete-log solve and
  no factor-base relation is claimed.**
- AGENTS.md rule 12 is UNMET and UNWAIVED, inherited from GOAL-MLKEM-003. No
  `EV-MLKEM-*` record and no `KN-*` entry changes status, and none is proposed.

---

# 9. What a reviewer should attack first

1. **The aggregation rule is mine, not the card's.** The card gave reference
   values for one instance; the excess-ratio definition, the pooling over
   instances and the |z|>5 sensitivity criterion were declared in `stage_a.py`'s
   header before the run but were not pre-registered by the Coordinator. A
   reviewer should check they were not chosen to flatter the result — the
   absolute differences are reported alongside every ratio for exactly this
   reason (`pooled -> *_absolute_difference_*`).
2. **The nine instances share BATCH-f75059's seeds and my error draws.** They
   are nine independent LWE instances but one error-draw seed family
   (`20260803401 + rep`) and one surrogate seed family. Instance-level
   independence is real; draw-level independence across instances is by
   distinct seeds, not by distinct entropy sources.
3. **Monotone-in-N' is consistent with more than one mechanism.** A component
   of near-miss spread that does not decay as 1/sqrt(N) is what the measurement
   shows. Whether that component is the algebraic dependence the campaign is
   looking for, or a finite-database artifact that grows with N' for a different
   reason, is not settled by this task.
4. **Stage B has 3 instances and no valid group-level null.** Do not let 5.3's
   table be read as an absence of effect.
5. **Every participant so far resolves to the same model.** This task's
   executor is `claude-opus-5`, as were batch 1's producer, batch 2's producer
   and all four reviewers. Independence remains procedural, not model-level.

---

**Artifacts**: `rebuild_transcript.txt`, `stage_a.py`, `stage_a_results.json`,
`stage_b.py`, `stage_b_results.json`, `report.md`, `receipt.json` — all under
`coordination/goals/GOAL-MLKEM-004/batches/BATCH-c45baf/tasks/TASK-20260803-db170f/`.
No `git commit` was run by this task.
