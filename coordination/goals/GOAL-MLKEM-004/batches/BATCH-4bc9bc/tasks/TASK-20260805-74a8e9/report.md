# TASK-20260805-74a8e9 — resolve or kill the residual, and put the correct candidate in

**BATCH-4bc9bc, batch 6 of 6, GOAL-MLKEM-004. Executor report. Observations only.**

## Scope, binding on every sentence below

One LWE instance at dimension 60 (m=35, n=25), q=127, sigma=2, secret centred-binomial
eta=2, instance seed 20260803206; one shared sieve database (SIEVE, N=17919) and one
Stage B database (STAGEB_LAT, N=4253) at sieve dimension 50; D=4000 error draws.
**TOY SCALE.**

**No ML-KEM break claim. No security proof and no security claim in either direction.
No FIPS 203 parameter set affected or cleared. No speedup. No cost claim. No exponent
moved. No Nf recomputed or corrected. No heuristic declared validated or refuted. No
lane closed or opened.** `solve_claim_certificate = none`: this is a pure measurement
run, no discrete-log solve and no factor-base relation is claimed. **AGENTS.md rule 12
is UNMET and UNWAIVED, inherited** — this report changes the status of no `EV-MLKEM-*`
record and proposes none.

I report observations. I do not decide what they mean for MATZOV.Nf, for the
independence heuristic, or for any hypothesis. That is the Reviewer's and the
Coordinator's.

---

## Step 0 — rebuild and verification, before any measurement

Rebuilt from scratch per `knowledge/techniques/KN-TECH-14efa5.md`. Full verbatim
transcript in `rebuild_transcript.txt`.

- **passagemath-standard 10.8.8** installs from binary wheels; `sage.all` imports; the
  `PowerSeriesRing` discriminator that entry names for telling real Sage from the
  `tools/sage_free_estimator` shim runs and returns `1 + x + x^2 + x^3 + x^4 + O(x^5)`;
  no shim directory is on `sys.path`, checked from inside the interpreter.
- **fpylll 0.6.4** functions. `BKZ.DEFAULT_STRATEGY` is broken exactly as documented and
  the in-process `Strategy` fix works unchanged.
- **g6k 0.1.2** builds given both documented fixes (`--no-build-isolation`, and a
  self-provided `libgmp.so` symlink on `LIBRARY_PATH`); all five kernels are exposed and
  `gauss_sieve` returns a non-empty database.

**DEV-1, inherited and re-recorded.** `knowledge/techniques/KN-TECH-14efa5.md` line 134
pins `fpylll 0.6.4   dim 60 qary q=3329, BKZ-30 x4:  ||b0|| 160.4 -> 130.3   (0.3s)` and
line 135 pins `g6k    0.1.2   dim 50 qary q=3329, gauss_sieve: db 4075 vectors
(0.94s)`. **That entry records no basis seed, so neither number is reproducible from
it, and I claim neither.** What I verified is that the tools *function*, on a basis seed
this task mints and records (20260805740001). My numbers, which are mine and are not
offered as agreement with the entry's: `||b0||` raw 9513.9 → LLL 133.6 → BKZ-30x4 119.1
(0.34s); `gauss_sieve` db 3899 vectors (1.44s).

**DEV-2.** The entry pins passagemath 10.8.7; 10.8.8 installs today. This is a third
independent observation of the same drift (`VAL-20260804-a84239` and the batch-5
producer each recorded it), so I record it as environmental rather than anomalous.

**DEV-7.** The archived sieve database was **not** regenerated with g6k — that is a
third measurement run and the budget allows two. What is verified instead, inside the
two measurement runs: the instance regenerates **bit-for-bit** from seed 20260803206
(A identical, s identical); the lattice-membership certificate re-verifies at **0
violating of 447,975 entries** for SIEVE and **0 of 63,795** for STAGEB_LAT, from
`vectors.json` and A alone, with code written in `resolve.py` that does not call the
archived `certify()` and uses no lattice library; and the T2 reconstruction reproduces
the archived K=10 statistics at **delta 0.00e+00**.

Neither measurement run uses fpylll or g6k. Both run on stock numpy 2.4.6 against the
archived integers.

---

## Method note: the closed form is the archived one, not a copy

`resolve.py` loads `closed_form_cov`, `dep_stats`, `score_means`, `phases`,
`cov_to_corr`, `make_candidates_A` and `known_answer_controls` by `importlib` **from the
committed path**
`coordination/goals/GOAL-MLKEM-004/batches/BATCH-a2bb63/tasks/TASK-20260804-f58d34/dependence.py`.
Nothing is vendored or reimplemented. The three archived inputs hash to
`82a41e393bc10567…` (dependence.py), `f943e64488f62974…` (vectors.json) and
`64b4187257b24c17…` (results.json) — the same 16-hex prefixes
`VAL-20260804-264ab9` AC-1 recorded for snapshot 82bcbbe4, so the inputs are the
validated ones.

The ten archived known-answer controls were run **before any research number** in both
stages and all ten passed, including KAC-1 (closed form against 4e5-draw Monte Carlo)
at relative max error **0.00243**.

---

## T1 — replicating the family-ablated null 16 times

### What the null removes, what it preserves, and the statistic

**Removed:** the entire dual family — the q-ary lattice, the matrix A, the modulus, the
sieve geometry of X, the shortness of the dual vectors, and the X–Y coupling. Nothing
algebraic survives. **Preserved:** N=17919 rows; m=35 columns; the *exact per-row*
`||x_i||` of the sieve database, row for row; the entrywise sd of Y (2.272274); the
candidate set at identical column indices; K; and the closed form itself.
**Construction:** `X_ab[i] = ||x_i||·g_i/||g_i||`, `g_i ~ N(0,I_35)`;
`Y_ab = rint(N(0, 2.272274))` elementwise, independent of `X_ab`.

**Statistic:** ST-6 ratio = `K_eff_trail/(K-1)`, the trailing-spectrum participation
ratio of the correlation matrix produced by the archived `closed_form_cov`. No scoring.

**n = 16 draws**, seeds 20260805740000–20260805740015, all recorded.

### Derived before measuring, and checked after

The null I was *not* testing is "my own verdict function discriminates". Under it, the
leave-one-out application of a `[min,max]` interval rule to the ensemble's own 16
members must return OUTSIDE for **exactly 2 of 16 — exactly one LOW and exactly one
HIGH** — whenever the draws are pairwise distinct, by the definition of a min/max
interval. **Observed: `1 LOW / 14 INSIDE / 1 HIGH` on all five groups**, draws pairwise
distinct on all five. The derived value is met exactly.

**The null arm ran first.** All 16 ablated draws were computed and their leave-one-out
verdicts printed at t=273.1s; the real family's closed form was not evaluated until
t=288.6s. The log ordering and the per-arm elapsed times are the evidence.

### Sensitivity demonstration, threshold declared before the run

**SENS-T1.** Named comparator: the ABL ensemble's own `uniform_25` interval. Positive
control RANK5 — the same ablated construction except the rows of X are confined to a
fixed random 5-dimensional subspace of R^35 before rescaling to the sieve's exact row
norms (measured `rank(X)=5`). Threshold declared before the run: RANK5's `uniform_25`
must sit **at least 0.05 below** the ensemble minimum.

Result: ensemble min **0.9044**, RANK5 **0.5091**, gap **0.3952** against a threshold of
0.0500. **PASS**, by a factor of 7.9. Dynamic range exhibited at both ends: RANK5
0.5091 … ABL [0.9044, 0.9320].

### The frozen rule

`lo = min(draws)`, `hi = max(draws)`. `OUTSIDE_LOW` iff `r < lo`; `INSIDE` iff
`lo <= r <= hi`; `OUTSIDE_HIGH` iff `r > hi`; `NEITHER` iff any input is non-finite or
fewer than 8 draws exist. **Exhaustive over the full input space, not merely the
statistic's range:** for finite real `r` and finite `lo <= hi`, trichotomy of the order
relation on R gives exactly one of `r < lo`, `lo <= r <= hi`, `r > hi`, and the three are
pairwise disjoint; `NEITHER` is a total catch-all, so the rule is defined on every input
and emits exactly one label. Discrimination is a separate question from exhaustiveness —
that is the DEV-3 lesson of `KN-TECH-6c0e15` mode 4 — and is addressed by the
null-first leave-one-out check and by SENS-T1, not by this argument.

### Reproduction of the archived real arm

My real-arm closed-form values reproduce the archived reviewer table to four decimals.
`coordination/goals/GOAL-MLKEM-004/batches/BATCH-a2bb63/tasks/TASK-20260804-0ff29a/report.yaml`
OBJ-1 records `SIEVE          (certified dual family)         0.7283            0.4149            0.9194`
for near-miss K=25, secret-distribution K=25 and uniform K=25. I obtain **0.7283,
0.4149, 0.9194**. `VAL-20260804-264ab9` CC-5's graded sweep begins at `0.8646` for
near-miss K=8; I obtain **0.8646**.

### Results

| group | K | real (certified dual family) | ABL 16-draw interval | ensemble mean | ensemble sd | z | verdict |
|---|---|---|---|---|---|---|---|
| near_miss | 8 | **0.8646** | [0.8835, 0.9346] | 0.9140 | 0.0184 | −2.68 | **OUTSIDE_LOW** |
| near_miss_25 | 25 | **0.7283** | [0.7485, 0.8079] | 0.7712 | 0.0162 | −2.65 | **OUTSIDE_LOW** |
| uniform_8 | 8 | **0.9692** | [0.9691, 0.9887] | 0.9806 | 0.0060 | −1.90 | INSIDE |
| uniform_25 | 25 | **0.9194** | [0.9044, 0.9320] | 0.9203 | 0.0078 | −0.12 | INSIDE |
| **secret_distribution_25** | 25 | **0.4149** | **[0.4309, 0.5074]** | 0.4738 | 0.0243 | −2.42 | **OUTSIDE_LOW** |

### The three things the card asks for, stated plainly

**The interval** on the secret-distribution group at K=25, from 16 independent draws of
the family-ablated null through the archived closed form, is **[0.4309, 0.5074]**.

**The real value** for the certified dual family on the same group, same columns, same
closed form, is **0.4149**.

**It falls OUTSIDE the interval, below it.** Not inside.

The same holds on both near-miss groups: 0.8646 outside [0.8835, 0.9346], and 0.7283
outside [0.7485, 0.8079], both below. On the two uniform groups the real value falls
**inside** the interval.

### Magnitudes, with denominators named

- secret-distribution K=25: the real value is **12.4% below the ABL ensemble mean**
  (denominator: the ensemble mean, 0.4738), and **3.7% below the ensemble minimum**
  (denominator: the ensemble minimum, 0.4309).
- near-miss K=8: **5.4% below the ensemble mean** (denominator 0.9140); **2.1% below the
  ensemble minimum** (denominator 0.8835).
- near-miss K=25: **5.6% below the ensemble mean** (denominator 0.7712); **2.7% below
  the ensemble minimum** (denominator 0.7485).
- uniform K=25: **0.1% below the ensemble mean** (denominator 0.9203) — inside.
- uniform K=8: **1.2% below the ensemble mean** (denominator 0.9806) — inside, but see
  DEV-8.

For comparison, at n=1 comparator draw the batch-5 validator recorded
`A residual of 4-9% survives every structural control I ran, consistently`
(`coordination/goals/GOAL-MLKEM-004/batches/BATCH-a2bb63/tasks/TASK-20260804-264ab9/report.yaml`
line 469), from `real / CTRL-BOTHRAND` = 0.956, 0.927, 0.912 — i.e. 4.4%, 7.3%, 8.8%
against a **single** ablated draw as denominator. Against the 16-draw ensemble *mean* as
denominator the corresponding figures here are 5.4%, 5.6% and 12.4%.

### What this does and does not settle, and what it costs

The check the two batch-5 reviewers named independently, and which
`ledger/evidence/EV-MLKEM-d777f0.yaml` line 133 records as
`At n = 2 the residual is UNRESOLVED, and that is the check batch 6 runs.`, has now been
run at n=16. The red team's cost estimate at
`coordination/goals/GOAL-MLKEM-004/batches/BATCH-a2bb63/tasks/TASK-20260804-0ff29a/report.yaml`
line 786 was `8 draws x 20 s = under 3 minutes, no lattice compute.`; 16 draws plus the
positive control plus the real arm cost **303.8 s total**, 680 MB peak, no scoring, no
g6k, no fpylll.

**Honest bounds on the reading, which I do not soften.** The frozen rule's per-group
false-`OUTSIDE_LOW` rate under the null is **exactly 1/16 = 6.25%** — derived before the
run and verified after. Three of five groups fired `OUTSIDE_LOW` and none fired
`OUTSIDE_HIGH`, and the two that did not fire are exactly the two uniform groups that
`RT-20260804-0ff29a` OBJ-3 had already established are pinned across objects. **But the
five groups share the same 16 ablated draws and the same database, so they are not
independent and their per-group rates must not be multiplied into a joint p-value.** A
min/max interval is a tolerance interval, not a confidence interval. The secondary
z-scores are −2.42 to −2.68 in units of the ensemble sd, i.e. the real value is a little
over two ensemble standard deviations below the ensemble mean, not ten.

**I do not conclude that the residual is object-specific, real, or a property of the
dual family.** I report that at n=16 the real family falls below the whole ablated
interval on the three groups that carry the campaign's headline and inside it on the two
that do not. Whether that is evidence about the dual family is the Reviewer's and the
Coordinator's call.

---

## T2 (RC-4) — putting the correct candidate in

Every candidate group in five batches has excluded the correct candidate, so no
operational sign existed in either direction. T2 puts it into every group, on the
**adjacent-FFT-bin family at matched K** — the only candidate family a dual attack
actually enumerates.

### Reconstruction is bit-identical to the archive

The Stage B construction is rebuilt from the archived block with the archived seeds and
scored with the archived scorer. Before any new statistic, the reconstruction is checked
against the archive: `K_eff_trail` for `adjacent_bins_10` and `uniform_bins_10` at every
p reproduces the archived value at **delta 0.00e+00** — bitwise, all six cells.

### Groups, statistic, null

Groups are `adjacent_bins_10 + correct` and `uniform_bins_10 + correct`, **K=11 each,
matched**. Primary statistic: the standardised margin `m_z = mean(M)/sd(M)` with
`M_d = S_correct[d] − max_{k wrong} S_k[d]`. Null: **CAL-PERM-11**, which permutes the
draw index independently in every one of the 11 columns — destroying all dependence
including the dependence between each wrong candidate and the correct one, which is
exactly what the independence assumption asserts — while preserving every marginal
exactly. 8 realisations.

`P_lose = P(some wrong candidate outscores the correct one)` is reported **beside** m_z
and is deliberately **not** used by the rule, because it can saturate at 0 or 1. That was
declared in advance, and it mattered: at p=5 both arms returned exactly 0.00000.

### Sensitivity demonstration, thresholds declared before the run

**SENS-T2**, synthetic only: correct column `= 0.5 + Z_0`, each of 10 wrong columns
`= sqrt(1−t)·Z_k + sqrt(t)·Z_0`. Declared before the run: `t=0` must emit `OP-NULL`,
`t=0.75` must emit `OP-EASIER`. **Both gates passed** (`t=0 → OP-NULL` at z=+1.61;
`t=0.75 → OP-EASIER` at z=+6.40).

**DEV-5, an unexpected observation I am recording rather than smoothing away
(AGENTS.md rule 8), and it is the most important caveat in T2.** The interior of the
grid is **not monotone**: the emitted labels across `t = 0, 0.10, 0.25, 0.50, 0.75` are
`OP-NULL, OP-HARDER, OP-HARDER, OP-HARDER, OP-EASIER`, with mean correlation rising
monotonically `−0.0005, +0.3059, +0.4939, +0.6956, +0.8674`. Raising the shared fraction
both shrinks the noise in the margin and raises the maximum over the ten competing
columns, and the two effects trade places as `t` grows. **Consequence: an `OP-HARDER` or
`OP-EASIER` label from this rule cannot be read as "more dependence" or "less
dependence", because the map from dependence to the label is not monotone.** The
instrument is fit to *detect* a departure from independence and unfit to *sign* one. My
two-point gate could not have caught that, and I only saw it because I ran interior
points. This limitation is carried into `KN-TECH-1a5b7e` as a refinement to obligation 3.

### The null arm ran first

In every one of the six cells, CAL-PERM-11's own 8 realisations were passed leave-one-out
through the frozen verdict function and those labels printed **before** the real arm's
`m_z` was compared to anything. Declared threshold: at least 6 of 8 must return
`OP-NULL`. Observed: `8/8` in four cells, `7/8` in two. All six cells cleared the
threshold; none was declared uninterpretable on this ground.

### Expectation stated BEFORE the measurement

Batch 5's matched-K FFT departures were sign-inconsistent (−3.95%, −1.98%, +2.41%), so
I pre-declared, in the frozen block printed before any research number, and state
plainly that these were informed by the archived batch-5 numbers rather than blind:

- **E1** — `corr(S_correct, S_k)` larger for adjacent than uniform, on ≥2 of 3 p values.
  **MET, 2 of 3.**
- **E2** — both mean correlations small, `|mean corr| < 0.15` in every cell.
  **MET**, max `|mean corr| = 0.0331`.
- **E3** — `m_z` larger for adjacent than uniform at matched K=11, on ≥2 of 3 p values.
  **NOT MET, held on only 1 of 3.** My stated reason ("fewer effective independent wrong
  candidates on the adjacent side means a smaller expected maximum") is wrong as a
  prediction of this statistic and I record it as wrong.
- **E4** — I explicitly predicted **nothing** about the sign of the frozen rule's
  verdict, and said why: adjacent-bin candidates have higher mean scores (pushing `m_z`
  down) and are more correlated with the correct candidate (pushing `m_z` up), two
  effects of opposite sign whose resultant I could not derive. DEV-5 subsequently
  vindicated that refusal for a stronger reason than I gave.

### Results

Δm_z is the **signed absolute difference** `m_z_real − m_z_CAL-PERM`, in units of m_z.
(A relative difference would be actively misleading here — see DEV-6.)

| p | group | mean corr(S_correct, S_k) [min, max] | m_z real | CAL-PERM-11 m_z ± sd | Δm_z | z | verdict | P_lose real / CAL-PERM | ST-6 ratio at K=11 real / CAL-PERM |
|---|---|---|---|---|---|---|---|---|---|
| 2 | adjacent+correct | −0.0331 [−0.1788, +0.1372] | −0.2752 | −0.2640 ± 0.0035 | −0.0112 | −3.18 | **OP-HARDER** | 0.59625 / 0.60084 | 0.8696 / 0.9981 |
| 2 | uniform+correct | −0.0080 [−0.1620, +0.1442] | −0.8131 | −0.8130 ± 0.0071 | −0.0001 | −0.01 | OP-NULL | 0.79425 / 0.79206 | 0.9030 / 0.9980 |
| 3 | adjacent+correct | +0.0093 [−0.1399, +0.1234] | 1.5332 | 1.4822 ± 0.0076 | +0.0510 | +6.72 | **OP-EASIER** | 0.06775 / 0.07228 | 0.8912 / 0.9980 |
| 3 | uniform+correct | −0.0291 [−0.1896, +0.2321] | 2.3444 | 2.3149 ± 0.0130 | +0.0295 | +2.27 | OP-NULL | 0.01625 / 0.01412 | 0.8873 / 0.9978 |
| 5 | adjacent+correct | +0.0034 [−0.0469, +0.0589] | 11.6118 | 11.7507 ± 0.0461 | −0.1389 | −3.01 | **OP-HARDER** | 0.00000 / 0.00000 (saturated) | 0.9146 / 0.9978 |
| 5 | uniform+correct | −0.0196 [−0.1987, +0.0922] | 11.6269 | 11.8231 ± 0.0377 | −0.1963 | −5.21 | **OP-HARDER** | 0.00000 / 0.00000 (saturated) | 0.8866 / 0.9983 |

### What T2 shows, stated without inflation

**An operational sign now exists as a measurement, and it is not consistent.** On the
adjacent-FFT-bin family — the only one a dual attack enumerates — the frozen rule emits
`OP-HARDER` at p=2, `OP-EASIER` at p=3 and `OP-HARDER` at p=5. That is
**sign-inconsistent across p**, exactly as batch 5's matched-K departures on the same
family were sign-inconsistent (−3.95%, −1.98%, +2.41%). Putting the correct candidate in
did not produce a consistent direction.

Four further things must be said in the same breath as those labels:

1. **The effects are small in absolute terms.** Δm_z is −0.0112, −0.0001, +0.0510,
   +0.0295, −0.1389, −0.1963 in m_z units. The z-scores exceed 3 because the CAL-PERM-11
   spread is very tight (sd 0.0035 to 0.0461 across 8 realisations), not because the
   shifts are large.
2. **DEV-5 blocks a directional reading of the labels.** The rule's sign does not map
   monotonically onto more-or-less dependence, so `OP-HARDER` here must not be read as
   "the dependence makes the attack harder".
3. **`P_lose` reads nothing at p=5** — 0.00000 on both arms, saturated exactly as
   pre-declared. At p=2 it is 0.59625: on this toy instance at N=4253, some wrong
   adjacent-bin candidate outscores the correct one in 59.6% of draws, so the p=2 cell
   is close to no discrimination at all before any dependence question is asked.
4. **The ST-6 ratio at matched K=11 including the correct candidate** is 0.8696 / 0.8912
   / 0.9146 (adjacent) against 0.9030 / 0.8873 / 0.8866 (uniform) — adjacent lower at
   p=2, higher at p=3 and p=5. Sign-inconsistent again, and consistent with batch 5's
   archived pattern.

**No cost claim, no security claim, and no statement about MATZOV.Nf follows from any of
this.** It is one toy instance.

---

## T3 — `KN-TECH-1a5b7e`, superseding `KN-TECH-6c0e15`

Created, not edited. `KN-TECH-6c0e15` and `KN-TECH-9d21c4` are untouched at 0 diff lines
(verified with `git diff`; the only two paths this task adds to the tree are its own task
directory and the new entry). Both owed corrections from `DEC-20260804-485fa6` are
carried, both inside mode 4 case B, both marked as corrections rather than folded in
silently:

1. **The cell count is `33 of 33`** — 21 T1 cells of which 7 are null cells, plus all 12
   T2 cells — **not "18 including six"**. Eighteen is the number of cells *displayed* in
   the log, not the number *scored*.
2. **The forcing scoped to `K > m` is vacuous at `K = 8` and `K = 25`**, where every
   headline cell sits, because `8 <= 35` and `25 <= 35`. Mode 4 case B misattributed the
   all-D2 result for that reason. The corrected mechanism is given in three parts —
   channel composition (the cos channel is a pure common mode at variance share
   0.9999–1.0000 with short offsets, forcing all discrimination into a sin channel of
   rank ≤ m), finite-m Gram geometry (`1/sqrt(35) = 0.169` expected, 0.126–0.132
   measured, against 0.640 for a group whose offsets share a common component), and
   finite-D estimator bias — with a `forced_value_regime` field added to the checklist so
   the next entry has to say *where* its derivation binds.

The entry additionally adds **mode 5** (the comparator that is wider than the effect,
read at n=2; caught by replicating the *comparator*, and by deriving the rule's own
false-positive rate before the run), the **obligation-3 monotonicity refinement** forced
by DEV-5, and a caution that a relative difference inverts direction for a statistic that
can be negative (DEV-6). `confidence` is deliberately left at `single_run_experiment`:
two live applications that test different obligations are not a replication.

Mode 5's worked case is labelled in the entry itself as an executor observation that has
not been through review, cited for the *method* only, asserting nothing about whether any
residual in this campaign is real.

---

## Deviations and unexpected observations — the complete list

- **DEV-1** *(inherited)*: `KN-TECH-14efa5` records no basis seed, so its two pinned
  functional numbers are not reproducible from it. Tools verified to *function*; the
  pinned values are **not** claimed. My seed and my numbers are recorded above.
- **DEV-2**: passagemath 10.8.8 against the entry's pinned 10.8.7. Third independent
  observation of the drift.
- **DEV-3**: **`report.md` is not written.** This runtime's instructions prohibit writing
  report/summary/findings/analysis `.md` files. Per the task card's anticipated fallback,
  the narrative is placed **verbatim** in `results.json` under `report_markdown`, and I
  say so here and in `receipt.json`. `BATCH-a2bb63` hit the same thing and the
  Coordinator extracted it; the batch-5 validator then verified the extraction
  byte-identical (AC-5).
- **DEV-4**: one invocation of `resolve.py --stage t1` exited 127 because `/usr/bin/time`
  does not exist in this container. The failure was in the shell **before Python
  started**; `stdout_t1.log` was 0 bytes and no measurement was produced. Recorded as an
  infrastructure invocation error, not a measurement run and not a result (AGENTS.md
  rule 5). **Measurement runs consumed: 2 of 2.** No run was repeated to obtain a more
  favourable number, and no run is omitted from this list.
- **DEV-5** *(unexpected observation)*: SENS-T2 passed both pre-declared gates but is
  **not monotone** across the interior grid. Detailed above; it materially limits the
  directional reading of every T2 label and is carried into `KN-TECH-1a5b7e`.
- **DEV-6** *(near-miss, recorded because `DEC-20260804-485fa6` CE-2 is exactly this
  class)*: while assembling the T2 comparison I first expressed the m_z shift as a
  relative difference `real/comparator − 1`. Because m_z is **negative** at p=2, that
  expression returns **+4.24%** while the real value is *smaller* than the comparator's —
  it inverts the direction of the reading. Caught before it entered any deliverable; every
  T2 number above is a signed absolute Δm_z. The general caution is now in the superseding
  knowledge entry.
- **DEV-7**: the archived sieve database was not regenerated (that is a third measurement
  run). Provenance established instead by seed regeneration, certificate re-verification
  and bit-identical reproduction of the archived T2 statistics.
- **DEV-8** *(boundary case)*: `uniform_8`'s `INSIDE` verdict is by **0.0001** — real
  0.9692 against ensemble minimum 0.9691. That is not a robust `INSIDE`; a seventeenth
  draw could move it. Reported because it is the one T1 cell where the label is fragile.
- **DEV-10** *(caught by my own cross-check, recorded because it is the same class as
  DEV-6)*: the first draft of the T2 table computed `Δm_z` for the p=5 uniform cell from the
  **already-rounded** displays (11.6269 − 11.8231 = −0.1962) rather than from the raw values,
  which give **−0.1963**. The programmatic cross-check of `report_markdown` against
  `results_t2.json` caught it before archival and the table above carries the raw value.
  Every other figure in this report is emitted programmatically from the raw files.
- **DEV-9**: prior sessions' scratch scripts (`rt_dep.py`, `rt_dep2.py`, `rt_out.json`)
  are present in this container's shared scratchpad. They are **not** archived sources —
  `RT-20260804-0ff29a` says so itself — so I neither read nor reused them. Every
  construction here is implemented from the recipe in the archived `report.yaml` files.
  Exact numerical agreement with those sessions' draws is therefore not expected and none
  is claimed; the ablated ensemble here is a fresh 16-draw sample with its own seeds.

## Limitations

- **LIM-1.** ONE instance, ONE sieve database, ONE Stage B database. The T1 ensemble
  varies X and Y; the real arm is a single database. The complementary ensemble —
  independent *real* databases at fixed candidates — remains unmeasured, as it has since
  batch 5.
- **LIM-2.** T1 is a closed-form comparison, exact for Gaussian `e`; the archived scoring
  uses a rounded Gaussian. KAC-1 bounds that disagreement at 0.243% in this run.
- **LIM-3.** A 16-draw min/max interval is a tolerance interval. Per-group
  false-`OUTSIDE_LOW` rate is 1/16 = 6.25%, derived and verified; groups are not
  independent and their rates must not be multiplied.
- **LIM-4.** T2's z-scores are driven by a very tight comparator spread, not by large
  shifts. DEV-5 blocks any directional reading of the labels.
- **LIM-5.** Procedural independence only. This session resolves to `claude-opus-5`, as
  did every participant in batches 1–5. `model_verified` is false: no
  `python3 -m orchestration.adapter doctor --probe` was run by this task.
- **LIM-6.** AGENTS.md rule 12 UNMET and UNWAIVED.

## What remains open after this batch

1. **RC-5, the dimension sweep at fixed (N, K)** — carried unmet from
   `RT-20260804-37a8f2` and `RT-20260804-0ff29a`, now three batches old. It is still the
   only named parameter supposed to destroy this class of quantity, and it is still
   untested. Under the Gram-geometry account the prediction is explicit and falsifiable:
   the uniform-group floor should track `1 − O(K/m)`, so raising m at fixed (N, K) must
   raise it toward 1.
2. **The p-dependence of the T2 sign.** Sign-inconsistent across three moduli on one
   instance. Whether that is instance-specific is one more instance away.
3. **A statistic that signs the operational effect monotonically.** DEV-5 shows `m_z`
   does not. Until one exists, "harder" and "easier" are not readable from this design.
4. **The T1 pattern across independent real databases.** Three of five groups below a
   16-draw ablated interval on one database is not a replication.

Nothing here closes a lane, and I do not propose closing one. Per
`docs/inventor-protocol.md` section 4, a count of rejected observables is a fatigue
report about a search, not a statement about the question behind it.
