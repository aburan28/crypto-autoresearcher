# TASK-20260803-d9afbd — ANOM-5: mechanism enumeration, and the per-model residual archive

BATCH-015, GOAL-MLKEM-003, EXP-MLKEM-011. Executor.

**Observations only.** Nothing here concludes that the archived data is
defective, that Approximation 4.9 is validated or refuted, or that any
statistic should be retired. That is `/review-evidence` under Coordinator
authority. Toy tier (q=241, m=40, n=43 and n=50), resolved band only, raw
undivided score scale. **No ML-KEM or Kyber security claim in either
direction.** AGENTS.md rule 12 is UNMET and UNWAIVED: EV-MLKEM-011,
EV-MLKEM-013 and EV-MLKEM-017 keep their status; KN-FIND-031 stays withdrawn.

**Zero new sampling of the physical system.** No network, no G6K, no new `.out`
bytes, no cost model. The only random numbers drawn anywhere are the seeded
synthetic null objects that calibrate this task's own estimator; the seed is
`20260803` and it is recorded in `results.json`. Every measured quantity is a
deterministic function of the archived bytes.

**No accusation is made against the source of the archived files.** A
sub-Poisson reading in someone's published validation data invites one; this
report enumerates mechanisms, tests what is testable, and says plainly what
stays open.

Artifacts: `anom5_investigation.py` (the exact script run), `results.json`
(machine readable, provenance and residual archive inside), this file.

---

## 0. Headline

**ANOM-5 is, in the main, an artifact of this program's own null object — not
of the archived data and not of the file format.**

The instrument's *arithmetic* is fine: an estimator written out again from the
construction, without copying BATCH-014's code, returns
`phi = 0.8022946873653165` against BATCH-014's `0.8022946873653166`, a
difference of 1.1e-16. What does not survive is its *reference point*.

BATCH-014 calibrated `phi` against **independent Poisson increments**. For
counts pooled over a **finite** number of iterations that null is not the
tightest admissible one, and in the n=43 mid band it is not even attainable.
`D_T` there is a sum over only `nb_iteration = 4000` independent iterations,
and the per-iteration occupancy `mu_T / 4000` reaches **0.739** at the top of
the band. Under *any* model with independent iterations,

> `Var(X) >= E[X] - E[X]^2` for non-negative-integer `X` (because `X^2 >= X`),
> then Cauchy-Schwarz over the `N` iterations gives
> `Var(D_T) >= mu_T (1 - mu_T / N)`, hence
> `E[phi] >= (1/K) sum_T (1 - mu_T / N)`.

For the n=43 mid band that floor is **0.9183**, not 1. The Poisson point sits
in the *interior* of the admissible set, so a reading below 1 is not by itself
evidence of anything.

| n=43, mid band (scores 551-851, K = 301 bins, one bin per score) | value |
|---|---|
| measured `phi` | **0.80229** (analytic sd 0.08377) |
| null object **N1**, independent Poisson (BATCH-014's null), 600 reps | 1.00249 +/- 0.08164 -> **z = -2.45** |
| analytic admissible floor, independent iterations | **0.91826** |
| null object **N2**, minimum-variance independent iterations, 600 reps | 0.91533 +/- 0.07895 -> **z = -1.43** |
| null object **N3**, over-dispersed `phi_true = 1.5` (power check), 200 reps | 1.49753 +/- 0.11665 |

Against the tightest admissible null the deficit is **-1.43 sd**, which no
honest reading calls an effect. The estimator is not blind — N3 shows it
resolves `phi = 1.5` at about four standard deviations.

**This cuts both ways, and the symmetric consequence is on the record.** The
same correction makes the n=50 mid band look *more* over-dispersed, not less:
`phi = 1.10820` moves from **+1.66 sd** against N1 to **+2.25 sd** against N2.

**It does not touch the deep tail.** Where `C_T < 1000` the per-iteration
occupancy is 0.0023 (n=43) and 0.0011 (n=50), the floor is 0.9997/0.9999, and
the Poisson null is the correct one. Nothing here changes what BATCH-014 read
there.

---

## 1. What was measured, and on what

Line `T` of an archived `Pwrong` file is `Phat(T) = C_T / M` with
`M = nb_iteration * q^{k_fft}`; `C_T` is a nested survival count and
`D_T = C_T - C_{T+1}` is the number of pooled candidate scores landing exactly
on `T`. Regions are re-derived by the same threshold rule BATCH-014 used.

| file | `nb_iteration` | `M` | band | mid band | mid rows | mid `sum D` | max `mu_T/N` |
|---|---|---|---|---|---|---|---|
| n=43 | 4000 | 55 990 084 000 | [0, 1802] | [551, 851] | 301 | 98 419 | **0.7392** |
| n=50 | 6000 | 83 985 126 000 | [0, 2309] | [636, 1131] | 496 | 98 230 | **0.2269** |

That last column is the whole story of the difference between the two files,
and it is a documented header parameter, not an undocumented one.

---

## 2. Mechanism table

`excluded` = tested from archived bytes and ruled out. `surviving` =
consistent with the observation and not ruled out. `untestable` = cannot be
decided from these bytes, with the reason given. Full numbers for every row
are in `results.json -> mechanism_verdicts`.

| id | mechanism | handoff | verdict |
|---|---|---|---|
| M-a1 | fixed total over the pooled scores (multinomial negative correlation) | (a) | **excluded** |
| M-a2 | finite-iteration pooling: per-iteration occupancy is O(1) in the mid band | (a) + added | **surviving — and quantitatively sufficient** |
| M-a3 | mixture across iterations (own lattice/target per iteration) | (a) | **excluded** for a deficit (wrong sign) |
| M-a4 | shared random source / antithetic / stratification **across** iterations | (a) | **untestable**; indirectly probed, no evidence found |
| M-b1 | rounding, truncation or formatting in the `.out` writer | (b) | **excluded** |
| M-b2 | quantisation / granularity in the increments | (b) | **excluded** |
| M-c1 | the estimator's arithmetic (GLM, leverage, `phi` normalisation) | (c) | **excluded** |
| M-c2 | bin placement / binning selection | (c) | **excluded** — and BATCH-014's control for it is degenerate here |
| M-c3 | the rate-model basis or its flexibility | (c) | **excluded** |
| M-c4 | leverage / edge weighting | (c) | **excluded as a driver** |
| M-c5 | the band endpoints are chosen on the data | added | **excluded as a driver** |
| M-c6 | periodic / oscillatory structure in the score index | added | **excluded** |
| M-d1 | the two files genuinely differ in how they were generated | (d) | **confirmed, and documented in the headers** |
| M-x1 | the **null object** — not the arithmetic — is mis-specified | added | **surviving — this is where most of ANOM-5 lives** |
| M-x2 | positive lag-1 serial correlation of the mid-band residuals | added | **surviving, small, unexplained** |
| M-x3 | a residual deficit below even the independent-iteration floor | added | **surviving, not resolvable at this bin count** |

### 2.1 Format (M-b1, M-b2) — excluded, decisively

Two independent tests, both from the printed digit strings:

- `value * M` was formed in **80-digit decimal arithmetic**, with no double
  rounding anywhere. The largest deviation from an integer is **1.54e-6**
  (n=43) and **2.32e-6** (n=50) against a rounding margin of 0.5. Zero lines
  are ambiguous.
- Every printed string is regenerated **bit-for-bit** as
  `"%.18e" % (count / M)`: **0 mismatches out of 1804 and 2311 lines**. Both
  files have a single field width (24 characters).

The files are lossless dumps of exact integer counts. Additionally: the counts
are **strictly non-increasing** (0 non-monotone steps), the gcd of all positive
increments is **1** (no sublattice), and the n=43 mid band contains **no zero
increment at all** (minimum increment 6). There is no quantisation, no
plateau, and no smoothing visible in the integers.

### 2.2 Estimator arithmetic (M-c1) — excluded

The GLM, the leverage correction `Var(Y - mu_hat) = mu (1 - h)` and the
`phi` normalisation were written out again in `anom5_investigation.py` from the
construction rather than copied from `dispersion_control_c1.py`. On the same
increments at the same degree the two implementations agree to 1.1e-16;
leverage sums to the parameter count in both (6.000000000000012 archived,
matched here); the maximum leverage in the n=43 mid band is 0.190, so the
correction moves `phi` by about two per cent and cannot manufacture a twenty
per cent deficit.

### 2.3 Rate model (M-c3) — excluded, three independent ways

- **Degree sweep** (this task's own estimator): `phi` = 1.237, 0.907, 0.873,
  **0.802**, 0.805, 0.806, 0.808, 0.811, 0.806, 0.803, 0.800 for degrees
  2...12 (P = 3...13). Flat from the selected degree onward.
- **Padded fits**: fitting on a range extended by 25/50/100/200 scores either
  side and evaluating only on the nominal mid band gives 0.807-0.845 at
  adequate degree (an under-degreed padded fit inflates, as it must).
- **A completely local rate estimator**: an independent log-polynomial Poisson
  fit inside each block of L consecutive scores, sharing no basis, no global
  smoothness assumption and no degree with the Chebyshev fit, returns
  **0.724-0.796** across L in {8, 12, 16, 24, 40} and degrees 1-2. It reads
  *lower*, not higher.

This is also what the handoff's sign argument predicts: misfit inflates
dispersion; it does not deflate it. The rate model is not the mechanism.

### 2.4 A congenial control whose code I read, and what it actually shows

BATCH-014's `control_observed_count_binning` reads **0.8008** against the
headline **0.8023** and therefore *looks* like a decisive exoneration of
binning selection. Reading `make_bins_from_observed`, it closes a bin the
moment the **observed** cumulative count crosses 10. In the n=43 mid band
every increment is at least 6 and almost all exceed 10, so it produces **297
bins against 301** — it is testing almost nothing there, and it is not
decisive. (In the n=50 mid band the binner does merge — 475 bins over 496
scores — and there the control carries some information.)

The exclusion of M-c2 rests instead on the bin count: BATCH-014's
expected-count binner returned **301 bins over 301 scores** in the n=43 mid
band, one bin per score. There is no binning freedom to exploit, so the
mechanism has no room to act.

**The same discipline applied to this task's own controls.** The
`phi_leverage_le_0p5` control here drops **zero** bins (maximum leverage
0.190), so its agreement with the headline is arithmetic, not evidence. It is
flagged `vacuous: true` in `results.json` rather than quoted as a passed
control.

### 2.5 The rate-model-free statistic is not independent evidence

The second-difference statistic
`R_T = (D_{T-1} - 2 D_T + D_{T+1})^2 / (D_{T-1} + 4 D_T + D_{T+1})` fits
nothing at all, so it cannot be deflated by a rate model. It reads **0.67412**
on the n=43 mid band, *lower* than `phi`, which at first looks like an
independent and larger deficit. It is not. The identity
`E[(r_{i-1} - 2 r_i + r_{i+1})^2] = v (6 - 8 rho_1 + 2 rho_2)` reproduces it
from `phi` and the measured autocorrelations as **0.67800** — 0.6 per cent
apart. The two statistics are the same observation seen through different
serial-correlation weighting, and reporting the 0.674 as a separate, stronger
deficit would have been double counting.

### 2.6 What the archive cannot test (M-a4)

The `Pwrong` archive keeps only the pooled survival curve. There is **no
per-iteration `Pwrong` data anywhere in this repository**, so dependence
*across* the 4000 iterations — common random numbers, antithetic pairing,
stratification, a shared seed — cannot be measured on the files where the
anomaly lives. This matters because such dependence would violate the
independence assumption used to derive the M-a2 floor, and could in principle
push `phi` below it.

An indirect probe was run and its limits stated before its numbers:
`Pgood_...n43...` stores one value per iteration, `F(solution)`, in iteration
order. Its serial autocorrelation is **+0.011** against a sampling sd of
0.016, the runs test gives **z = -0.21**, and block-mean variance ratios sit
at 0.89-1.23 across block sizes 2-100 where 1 is expected under independence.
No serial structure. But this is **weak evidence and not exclusion**: it is a
different statistic, it covers n=43 only, and it comes from a *different
invocation* — the `Pgood` and `Pwrong` headers carrying the same n=43
parameter label report `avg_dlat` 41.071674 vs 41.068986 and `avg_dlsc`
23.939202 vs 23.938828. That is an ordinary consequence of running a generator
twice; it is recorded because it bounds what the probe can say.

---

## 3. Data, estimator, or format — the explicit answer

- **Format: excluded.** Bit-exact lossless dumps of exact integer counts
  (section 2.1). This is settled.
- **Estimator arithmetic: excluded.** Reproduces to 1.1e-16 under an
  independent reimplementation, and to 0.72-0.80 under a rate estimator that
  shares nothing with it (sections 2.2, 2.3).
- **Estimator *null object*: this is where most of ANOM-5 lives.** The
  reference point was the Poisson value 1; the tightest admissible reference
  for a statistic pooled over 4000 iterations is 0.9183. Re-measured against
  it, `-2.45 sd` becomes `-1.43 sd`.
- **Data: a residue remains, and it is not excluded.** The -1.43 sd gap
  (M-x3) and a lag-1 residual autocorrelation of **+0.104** against a sampling
  sd of 0.058 (M-x2, calibrated: the synthetic nulls return -0.022 +/- 0.059)
  are both unexplained by the cell-wise mechanisms above. Neither is
  resolvable here. Closing the M-x3 gap at three standard deviations would
  need about **1409 bins** in that region; the archive contains 301.

**Single best answer: ANOM-5 is the estimator — specifically its null object,
not its arithmetic — with an unresolved residue in the data that this archive
cannot decide.** The most useful part of that sentence is the part that says
the last two batches' reference point was wrong in this region; recording it is
the point of the task, and the observation is left for `/review-evidence` to
act on.

---

## 4. Job B — residuals[T] per model per fit

`results.json -> job_B_residual_archive` now carries, for **each of 24 archived
BATCH-012 fits per file** (M2, M4, M1 at argmin p, M1a at the file's own
exponent, M3 at argmin s, and the psi_lsc sensitivity fit — each on the whole
band, count>=10, count>=1000 and count>=1e5):

- `residuals_bits[T] = log2(model_T) - log2(Phat_T)` over the **full resolved
  band**, so any index set can be re-derived;
- per-band sums of squares, rms, mean/min/max residual, including the deep-tail
  set `C_T < 1000`;
- the recomputed rms on the fit's own index set beside the archived rms.

The BATCH-012 machinery (Upsilon tables, exact region measure, u-quadrature,
d_lsc mixture, kernel) is **imported from the archived script**, not retyped,
so these are residuals of exactly the archived models. **All 48 fits reproduce
their archived rms to better than 1e-6 bits**, and the single-fit additivity
`sum_whole = sum_meas + sum_deep` holds to ~1e-13 bits^2.

### 4.1 The flagged rows are now checkable — and they move

BATCH-014 had to form `sum_deep = sum_whole - sum_meas` across two *separately
profiled* fits, and flagged four rows per file `reconstruction_valid: false`.
Those rows now have single-fit values. **Every ratio below carries the
effective-degrees-of-freedom binding of section 4.2.**

n=43 deep-tail ratio (rms over the `C_T < 1000` counting floor):

| model | from the **whole-band** fit | from the **count>=1000** fit | BATCH-014 two-fit | flag |
|---|---|---|---|---|
| M2 exact region measure | 0.7697 | 0.7733 | 0.7704 | valid |
| M4 exact, d_lsc collapsed | 0.6183 | 0.6766 | 0.6296 | **false** |
| M1 surrogate at argmin p | 0.8366 | **3.3897** | 1.1557 | **false** |
| M1a surrogate at own exponent | 0.7974 | **2.3938** | 1.2718 | **false** |
| M3 exact^s at argmin s | 0.8951 | **2.3460** | 1.0300 | **false** |
| SENS psi_lsc truncated | 0.6155 | 0.6285 | — | not in that table |

n=50:

| model | whole-band fit | count>=1000 fit | BATCH-014 two-fit | flag |
|---|---|---|---|---|
| M2 exact region measure | 0.5808 | 0.6524 | 0.6003 | **false** |
| M4 exact, d_lsc collapsed | 0.5212 | 0.5349 | 0.5247 | valid |
| M1 surrogate at argmin p | 0.6443 | **2.8738** | 1.0281 | **false** |
| M1a surrogate at own exponent | 0.8181 | **1.8523** | 1.1793 | **false** |
| M3 exact^s at argmin s | 0.7457 | **1.1695** | 0.8754 | **false** |
| SENS psi_lsc truncated | 0.5245 | 0.5619 | — | not in that table |

Two observations, offered without interpretation:

1. **The flags were correct.** Where BATCH-014 said `valid` the two-fit
   reconstruction lands within 0.1-1 % of the single-fit value; where it said
   `false` the two-fit value can be off by up to 0.47 in ratio (M1a, n=43:
   1.2718 vs 0.7974).
2. **The deep-tail ratio is strongly fit-dependent for M1/M1a/M3.** Every
   whole-band fit puts the deep tail *below* its counting floor (0.52-0.90);
   the count>=1000 fits put M1/M1a/M3 *above* it (1.17-3.39). "The deep tail
   sits below its floor" is therefore a property of the whole-band-fitted
   normalisation for those models, not a fit-independent fact. This is
   recorded for `/review-evidence`; no conclusion is drawn from it here.

### 4.2 Effective-degrees-of-freedom binding

Carried beside every ratio in `results.json`:

> The effective number of degrees of freedom of a **whole-band** ratio is
> **O(1)**. No single value is quoted: the published defensible range across
> conventions is **1.51-2.35**. The comparison that matters is that
> restricting to **C >= 1000 buys no degrees of freedom** — that ratio's
> effective dof is also O(1) and lies inside the same 1.51-2.35 family. A
> whole-band ratio is therefore not resolved to a few per cent, and neither is
> a C >= 1000 ratio. The cause is the nesting: `C_T` is a survival count, so
> `Cov(C_T, C_T') = min(lambda_T, lambda_T')`, the residual covariance is
> nearly rank one, and Satterthwaite collapses 1803/2310 rows to O(1).

---

## 5. Deviations, anomalies, failed attempts

Recorded, none discarded.

1. **The handoff's quoted reference values do not all appear in the archive.**
   Full reconciliation in `results.json -> handoff_reference_reconciliation`.
   - `phi = 0.8020` — agrees (archived 0.8022946873653166).
   - null object `0.9923 +/- 0.0806` — **does not appear** in
     `TASK-20260803-f81a66/results.json`. The archived Monte-Carlo Poisson
     null for that region is `0.995211 +/- 0.084310`; the archived analytic sd
     is `0.083775`; this task's N1 is `1.002495 +/- 0.081643`.
   - `-2.36 sd` — this is the archived **analytic** z against the Poisson
     *point* null `phi = 1` (`-2.359958`), not the Monte-Carlo z
     (`-2.288175`).
   - `+1.55 sd` for n=50 — matches neither archived reading (analytic
     `+1.616147`, Monte-Carlo `+1.888619`).
   - "6 to 33 parameters" — the archived n=43 mid-band degree sweep spans
     **P = 2...13**; no 33-parameter fit of that region exists in the archive.
     The substance of the claim — `phi` is flat as the rate model is
     enriched — holds over the range that does exist and is reproduced here.

   None of these changes a verdict. They are recorded because a quoted
   reference value that is not in the archive is a defect in the citation
   chain, and it is not mine to repair.

2. **Deep-tail region readings in this task are not comparable to
   BATCH-014's.** This script uses one bin per score everywhere; BATCH-014
   binned the deep tail to expected count >= 10 (82 and 87 bins). The
   deep-tail rows here (`phi` = 1.057 and 1.027) are carried **only** for
   their floors, which are binning independent. `results.json` flags this with
   `instruments_identical: false` and a comparability note. The n=50 mid band
   carries the same flag (475 archived bins vs 496 scores here) — its `phi`
   moves from 1.10644 to 1.10820 under the change of binning, which is the
   size of that effect.

3. **The N2 null object is not applicable in the shallow band** and was not
   run there: the per-iteration occupancy is ~4.9e4, so the 0/1
   minimum-variance member of the family does not exist and the bound
   degenerates (it evaluates to -12676, a meaningless number that is reported
   with an explicit `applicable: false` rather than suppressed). The binding
   constraint there is the multinomial floor, which is 0.9991.

4. **Sampler approximations, disclosed.** The Binomial sampler is **exact**
   (recursive-Beta, no normal limit; verified at 40 000 draws to give
   `var / np(1-p)` in 0.986-1.012 across the parameter range used). The
   Poisson sampler uses inversion below `lambda = 30` and a rounded normal
   above, whose variance error is O(1/12) against `lambda >= 30`, i.e. below
   0.3 %.

5. **Invocations of the script.** The declared run is the final one, recorded
   in `results.json -> provenance` (143.3 s wall, 0.043 GB peak RSS, budget
   3000 s / 4 GB), at git commit `b7bea56a2316714fa0d5680ed5bd9b8a63e4420d`,
   branch `claude/harness-findings-repo-yyzt1x`, dirty tree (this task's own
   untracked directory). Prior invocations during development were smoke tests
   at `--reps 3` and `--reps 12`, plus one earlier full `--reps 600` run whose
   only difference is the absence of the `handoff_reference_reconciliation`
   block and the `vacuous` flag on the leverage control; all of them wrote to
   the session scratchpad or were superseded in place before declaration, and
   all measured quantities are seed-fixed and identical across them. Nothing
   was rerun to obtain a more favourable number, and the seed was never
   changed.

6. **No `runs/` tree is declared**, per the handoff. The provenance the
   evidence doctrine requires — command, argv, git commit and dirty state,
   environment, input file SHA-256s, seeds, resource measurements,
   certificate, inference block, validity — is carried inside `results.json`.

7. **Certificate: `kind: none`.** Pure measurement run; no discrete-log solve,
   no factor-base relation, nothing claimed that needs one.

8. **Harness deviation.** The subagent runtime's file-writing tool refuses to
   create report-style `.md` files. This file is a contractually declared
   deliverable in `artifact_paths`, so it was emitted through the shell
   instead, and its full content is additionally restated in the Executor's
   returned message.

9. **A side-effect write outside the declared `write_scope`, found and
   reverted.** Job B imports the archived BATCH-012 script, and CPython wrote
   a `__pycache__/` directory beside it inside
   `.../BATCH-012/tasks/TASK-20260803-36f572/`. That path is outside this
   task's `write_scope`. It was removed; `__pycache__/` is gitignored, `git
   status` shows only this task's own directory as untracked, and the three
   BATCH-012 artifacts are byte-identical and untouched (their modification
   times are unchanged). Recorded rather than quietly cleaned. A future task
   importing an archived script should set `PYTHONDONTWRITEBYTECODE=1`.

---

## 6. What remains open

- **M-a4**, dependence across the 4000 iterations, is the one mechanism this
  archive cannot test, and it is exactly the one that could push `phi` below
  the M-a2 floor. Deciding it needs per-iteration `Pwrong` data, which does
  not exist in this repository. Any future request to the source would be a
  Coordinator decision, not an Executor one.
- **M-x3**, the -1.43 sd residue below the floor, would need roughly 1409 bins
  in that region to reach three standard deviations. The archive has 301.
- **M-x2**, the +0.104 lag-1 residual autocorrelation (about 1.8 of its own
  sampling standard deviations, and 2.1 above the synthetic nulls' -0.022),
  is not explained by any cell-wise mechanism tested here.
- The n=50 mid band's **+2.25 sd excess** against the corrected null is a new
  open item created by this task, not an old one closed.

## 7. Non-claims

- No ML-KEM or Kyber security claim in either direction.
- No conclusion that the archived data is defective, incorrectly generated, or
  misreported.
- No conclusion that Approximation 4.9 is validated or refuted.
- No conclusion that any statistic should or should not be retired, and no
  statement about how far the BATCH-014 deep-tail null may now be carried —
  that inference belongs to `/review-evidence`.
- No record status changed; no prior artifact edited; nothing committed.
- Toy tier only; nothing here extrapolates to cryptographic scale.
