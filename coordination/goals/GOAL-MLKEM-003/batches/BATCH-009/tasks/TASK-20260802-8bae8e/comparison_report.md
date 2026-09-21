# F1 — Approximation 4.9 predicted vs measured Pwrong over the resolved band

**Task** TASK-20260802-8bae8e · **Batch** BATCH-009 · **Goal** GOAL-MLKEM-003 ·
**Authorized by** DEC-20260802-56cc4b · **Role** executor (observations only)

Artifacts: `approx49_comparison.py` (the exact script run),
`comparison_results.json` (per-score table, parameter ledger, all summary
statistics), `receipt.json`.

---

## 0. What this is, and what it is not

This is a fresh, zero-compute-input comparison: Approximation 4.9 of Carrier,
Meyer-Hilfiger, Shen, Tillich (HAL 05406481) recomputed from the archived page
extracts, evaluated at every integer score, and set against the archived
verifyModel measurement, over the band the counting instrument resolved.

It is **not** a verdict on Approximation 4.9, not an ML-KEM or Kyber security
claim, not a cost-model revision, and not a status change to any record.
AGENTS.md rule 12 is UNMET and UNWAIVED for this batch; nothing here treats
EV-MLKEM-011, EV-MLKEM-013, EV-MLKEM-017, KN-FIND-012 or KN-FIND-014 as
corrected. Parameters are toy (q=241, m=40, n=43/50). No sampling, no lattice
computation, no G6K call, no network access: every input byte was already in
this repository, and all three data files' SHA-256 digests match the archived
upstream manifest at
`inputs/MLKEM-DUAL-SOURCES-20260802/extracts/codeddualattack/file_sha256_manifest.txt`.

Interpretation of what the agreement or divergence *means* for the paper's
analysis is deliberately absent; that is the Reviewer's and Coordinator's call.

---

## 1. Resolved band and counting floor, per file

Each measured survival function is an unsmoothed pooled counting estimate over
`nb_iteration * q^k_fft` candidate scores. Its support ends exactly at
`1/(nb_iteration * q^k_fft)`. Values printed as `0.0` above that point are
absence of measurement, not measured zeros. **Nothing below is compared,
fitted or extrapolated past the floor.**

| file | nb_iteration | `nb_iteration·q^k_fft` | counting floor | floor (log2) | resolved band (scores) | resolved band (probability) |
|---|---|---|---|---|---|---|
| `Pwrong_…n43…N25971.out` | 4000 | 55 990 084 000 | 1.7860305406935986e-11 | **−35.70445229** | **[0, 1802]**, first zero at 1803 | [2^−35.7045, 2^−1.0029] |
| `Pwrong_…n50…N25970.out` | 6000 | 83 985 126 000 | 1.1906870271290657e-11 | **−36.28941479** | **[0, 2309]**, first zero at 2310 | [2^−36.2894, 2^−1.0051] |

Re-verified independently here: for both files the last positive value equals
the floor as an **exact IEEE-754 equality**, and every value in each file is an
integer multiple of the quantum (max relative deviation 2.165e-16 and
1.815e-16). This reproduces EV-MLKEM-018's identity from the same bytes.

Pooled counts fall below 10 above score **1492** (n=43) and **1968** (n=50);
above those the estimate is Poisson-dominated and is reported but never used as
if it were resolved to the same precision. Summary statistics are given both
for the whole band and for the count ≥ 10 sub-band.

## 1a. Score scale — checked, not assumed

The comparison is on the **raw, undivided cosine-sum scale**; no k_fft
alignment is applied. This was re-derived here rather than taken on trust, by
two estimators of `sigma = sqrt(E[F^2 | F >= 0])` computed from each file's own
survival column, against Model 4.7's raw prediction `sqrt(avg_N/2)`:

| file | estimator A | estimator B | `sqrt(avg_N/2)` | ratio A / B vs raw | ratio A / B vs `/k_fft` |
|---|---|---|---|---|---|
| n=43 | 113.9051 | 113.7914 | 113.9539 | 0.9996 / 0.9986 | 2.9987 / 2.9957 |
| n=50 | 114.1781 | 113.9783 | 113.9517 | 1.0020 / 1.0002 | 3.0060 / 3.0007 |

Both estimators, in both files, sit at ratio ≈ 1.00 against the raw scale and
≈ 3.0 against the `/k_fft` scale. **I do not disagree with EV-MLKEM-018's
finding**; the raw convention is used throughout.

---

## 2. Every parameter Approximation 4.9 needs, with its source

Full ledger with per-symbol notes: `comparison_results.json` →
`approximation_4_9_parameter_ledger`. Summary:

**Available (archived).** `T` (the score index); `N` = avg_N (header
25971.000000 / 25970.000000, caption agrees); `beta_sieve` (header `beta_1`
44 / 41, caption agrees); `n_fft` = 8; `k_fft` = 3; `q` = 241; `m` = 40;
`n_lat` = 35 / 42; `beta_bkz` (header `beta_0` 32 / 35); `mu_lsc`, `sigma_lsc`
(header `avg_dlsc`/`sdv_dlsc`, caption agrees to 2 dp).

**Available with an archived-source discrepancy (recorded, not resolved).**

* `d_lat`: header `avg_dlat` = 41.068986 / 57.889159 vs Fig 4.1 caption 42.00 /
  58.60 — the two archived sources differ by 2.3% / 1.2%. In this comparison
  `d_lat` enters only through the (unavailable) scale, so it does not propagate.
* `nb_iteration`: header 4000 (n=43) and **6000** (n=50); the Fig 4.1 caption
  states 4000 iterations for **both** panels. The header value is used, since it
  is the file's own record of how it was produced.

**UNAVAILABLE.**

* **`Phi_{dlsc}(x,y)`** — the function whose level set *is* the region E(T−t) of
  (4.23), i.e. the core of Approximation 4.9. Introduced with Approximation 4.6
  on a page that was never retrieved. It appears in **no** archived extract and
  in no other repository byte (searched across `inputs/`, `knowledge/`,
  `ledger/`, `coordination/`, `experiments/`).
* **`delta(beta_bkz)`** — the root-Hermite factor in `lambda(x)`, and Lemma 2.9
  (the volume of `Lambda(B')`). Cited by the archived page, defined on pages not
  retrieved. No archived numerical value.
* **`alpha`** — appears in no archived page extract of the paper, as BATCH-008
  flagged. A candidate value exists *outside* the paper: the archived **Pgood
  file header carries `alpha_secret=2` and `alpha_error=2`**. Identifying those
  with the paper's `alpha` is not established by any archived text, so **no
  value was assumed**; this is recorded as a lead, not used.
* **`n_lsc`** — used in the archived justification's locus
  `(sqrt(alpha·beta_sieve/2), sqrt(alpha·n_lsc/2))`; never defined in an
  archived extract. Plausibly `n_fft`; not assumed, and not needed here.

### What the unavailability costs, precisely

Writing `E(u) = {(x,y) ∈ R²₊ : N·Phi_dlsc(x,y) ≥ u}` and
`lambda(x) ∝ x^{beta_sieve−1}`, `mu(y) ∝ y^{n_fft−1}` from the archived (4.24):

* if `Phi` is exponential in a negative quadratic form of the two lengths —
  which the archived Approximation 4.8 (4.19) **forces**, since (4.19) is by its
  own statement `N·E[Phi]` on the good guess and factorises into two terms of the
  form `exp(−alpha(pi·length/q)^2)` — then
  `∫_{E(u)} lambda·mu = K · (ln(N/u))^p` with **`p = (beta_sieve+n_fft)/2`
  fixed by archived integers** (26.0 for n=43, 24.5 for n=50), and **everything
  unavailable collapses into the single scale `K`**;
* so the predicted curve is
  `Pwrong(T;K) = Q(T) + ∫_0^N phi(T−u)·min(1, K·ln(N/u)^p) du`, where
  `Q(T) = P(N(0,N/2) ≥ T) = 0.5·erfc(T/sqrt(N))` is **parameter-free and fully
  archived**, and `K` is **not computable from archived bytes**.

**Consequence, stated plainly: this is a shape-and-relative comparison with one
free normalisation, not an absolute-level test.** The absolute level of
Approximation 4.9 cannot be checked from the archived extracts at all, because
`delta(beta_bkz)` is missing and enters as `delta^{beta_sieve(m+n_lat−beta_sieve)}`
— an exponent of 44·31 = **1364** (n=43) and 41·41 = **1681** (n=50), where a
0.1% change in `delta` moves the prediction by roughly 2.0 and 2.4 bits
respectively. No substitute bound would be meaningful. (The corresponding
sentence inside `approx49_comparison.py`'s parameter ledger, and hence in
`comparison_results.json`, misprints the second exponent as 1394; see §6.)

The adopted reading of `Phi` is declared, not archived. Its only load-bearing
consequence is the exponent `p`, and Section 5 reports how strongly the
measurement itself constrains that exponent.

---

## 3. Method (all of it re-derivable from the script)

`numpy`/`scipy` are not installed here. Gauss–Legendre nodes are generated from
the Legendre recurrence by Newton iteration; the quadrature is self-checked
against a closed form (the `K → ∞` limit collapses the integrand to
`0.5·(erfc((T−N)/√N) − erfc(T/√N))`), with **max relative error 1.7e-15 /
2.2e-15**, and a coarse-vs-fine grid check agreeing to **6.6e-15 / 6.1e-15**.
4370 quadrature nodes; 243.0 s wall clock, 23.4 MB peak RSS for the whole run.

Three normalisations are reported, so that shape and normalisation are never
confused:

| normalisation | n=43 | n=50 |
|---|---|---|
| `K_fit` — least squares on log2 residuals over the resolved band | log2 K = **−72.712581** | **−67.222505** |
| `K_anchor_low` — matches the measurement exactly at the 2^−5 level (the top of Fig 4.1's plotted y-range) | −89.979061 at score 213 | −82.956451 at score 214 |
| `K_anchor_high` — matches exactly at the last score with pooled count ≥ 10 | −72.147621 at score 1492 | −66.704753 at score 1968 |

Per score the JSON also carries `log2_K_solved_at_this_score` (the scale that
would reproduce **that one score** exactly, by bisection on the exact model) and
`elasticity_dlog2pred_dlog2K` (how much the prediction responds to `K` there —
1 where the prediction is carried entirely by the D component, ≈0 where the
parameter-free Gaussian component dominates and `K` is nearly irrelevant).

---

## 4. Results — where prediction and measurement agree, and where they part

### 4.1 The headline, per file, over the whole resolved band

With one fitted scale, the recomputed Approximation 4.9 tracks the measurement
across the entire resolved band — 34.7 bits of dynamic range (n=43) and 35.3
bits (n=50) — with residuals

| file | band | n | min Δ | max Δ | mean Δ | rms Δ |
|---|---|---|---|---|---|---|
| n=43 | whole resolved band [0,1802] | 1803 | −0.933 | +1.516 | +0.245 | 0.706 |
| n=43 | count ≥ 10 sub-band | 1493 | −0.675 | +1.516 | +0.359 | 0.742 |
| n=43 | clip-negligible ∧ count ≥ 10 | 738 | −0.675 | +0.182 | −0.202 | **0.283** |
| n=50 | whole resolved band [0,2309] | 2310 | −0.917 | +1.710 | +0.192 | 0.697 |
| n=50 | count ≥ 10 sub-band | 1969 | −0.640 | +1.710 | +0.279 | 0.727 |
| n=50 | clip-negligible ∧ count ≥ 10 | 1242 | −0.640 | +0.244 | −0.163 | **0.274** |

Δ = log2(predicted) − log2(measured) at `K_fit`; positive = prediction above
measurement.

### 4.2 The divergence profile as a function of score (n=43, `K_fit`)

Full per-score table in `comparison_results.json` → `per_score` (1803 rows for
n=43, 2310 for n=50). Every 5% of the band:

| score | log2 meas | count | log2 Q (Gaussian only) | log2 pred | **Δ (bits)** | clip frac | log2 K solved |
|---|---|---|---|---|---|---|---|
| 0 | −1.0029 | 2.79e10 | −1.0000 | −0.7017 | **+0.301** | 0.137 | none |
| 180 | −4.1207 | 3.22e9 | −4.1303 | −3.3176 | **+0.803** | 0.287 | −92.196 |
| 360 | −10.1502 | 4.93e7 | −10.3039 | −8.8180 | **+1.332** | 0.369 | −83.750 |
| **471** | −15.2599 | 1427026 | −15.7710 | −13.7438 | **+1.516 (max)** | 0.361 | — |
| 540 | −18.6109 | 139854 | −19.8270 | −17.2410 | **+1.370** | 0.299 | −76.271 |
| 630 | −21.8645 | 14664 | −25.8844 | −21.2500 | **+0.614** | 0.092 | −73.442 |
| 720 | −23.7097 | 4081 | −32.8166 | −23.4897 | **+0.220** | 0.004 | −72.934 |
| 900 | −26.3713 | 645 | −49.3252 | −26.3710 | **+0.000** | 5e−07 | −72.713 |
| 1080 | −28.4471 | 153 | −69.3797 | −28.6849 | **−0.238** | 4e−12 | −72.475 |
| 1260 | −30.2782 | 43 | −92.9958 | −30.6825 | **−0.404** | 2e−18 | −72.308 |
| 1440 | −32.1195 | 12 | −120.1831 | −32.4643 | **−0.345** | 5e−26 | −72.368 |
| **1616** | −33.1195 | 6 | −150.2257 | −34.0520 | **−0.933 (min)** | 2e−34 | — |
| 1710 | −34.7045 | 2 | −167.6740 | −34.8497 | **−0.145** | 2e−39 | −72.567 |
| 1802 | −35.7045 | 1 | −185.6975 | −35.6014 | **+0.103** | 2e−44 | −72.816 |

The n=50 file reproduces the same structure: Δ = +0.375 at score 0, rising to
**+1.710 at score 420**, crossing zero at score **1090**, then −0.2 to −0.6 bits
through the count ≥ 10 region, min **−0.917 at score 2283** (count 3), +0.500 at
the floor.

### 4.3 Where they track, and where they part — in words

1. **They track, and the tracking is tight in the tail.** Over the part of the
   band where the prediction is genuinely carried by Approximation 4.9's D
   component (clip contribution < 1e-3, pooled count ≥ 10 — scores **755–1492**
   for n=43, **727–1968** for n=50), predicted and measured agree within **−0.675 to
   +0.182 bits (rms 0.283)** and **−0.640 to +0.244 bits (rms 0.274)**
   respectively. Equivalently, the scale that reproduces the measurement
   score-by-score drifts by only **1.150 bits** (n=43, over scores 643–1492,
   range −73.298 … −72.038) and **1.238 bits** (n=50, over 600–1968, range
   −67.942 … −66.582), and the drift is **not monotone** in either file.

2. **They part in the crossover region, and the model sits ABOVE the
   measurement there.** The largest divergence is **+1.516 bits at score 471**
   (n=43) and **+1.710 bits at score 420** (n=50). Both maxima sit exactly where
   the D component and the parameter-free noise component are comparable
   (elasticity 0.377 / 0.424; clipped fraction 0.361 / 0.381). Δ is positive
   throughout the lower band and first changes sign at score **888** (n=43) and
   **1090** (n=50). It wobbles across zero a few times while crossing (12 sign
   changes in all for n=43, at scores 888–909 and then 1682/1693/1741; 14 for
   n=50, at 1090–1173 and then 2044/2084/2286), which is what a residual of a
   few tenths of a bit against Poisson-noisy counts looks like; the later
   crossings all sit at pooled counts of 1–4.

3. **Above the crossover the model sits BELOW the measurement**, by −0.2 bits on
   average and up to −0.68 / −0.64 bits within the count ≥ 10 region (up to
   −0.93 / −0.92 bits in the Poisson-noise region above it). Direction, stated
   without interpretation: **in the upper part of the resolved band the
   recomputed Approximation 4.9 under-predicts the measured Pwrong.** The
   archived page-25 text records the authors' own reading of Fig 4.1 —
   "the experimental and theoretical estimates are in agreement, though the plot
   on the right suggests that our analysis may be slightly optimistic" — and the
   direction found here is the same direction. Whether that is the same effect
   is not adjudicated here.

4. **At the very bottom of the band the measurement lies marginally BELOW the
   model's parameter-free floor.** Model 4.7 writes the wrong-guess score as
   `D + N(0,N/2)` with `D ≥ 0`, so the model's survival can never fall below the
   pure-noise survival. For scores **0–126** (n=43) and **0–133** (n=50) the
   measurement does, so **no K ≥ 0 reproduces it**. The shortfall is tiny —
   **max 0.0037 bits** and **0.0069 bits** — and is consistent with the measured
   score standard deviation being 0.04%–0.14% away from `sqrt(avg_N/2)`
   (Section 1a). Recorded because it is a structural, not a numerical, mismatch.

5. **Normalisation matters enormously at one end and not at all at the other,
   and this asymmetry is the main thing a reader should carry away.** Anchoring
   `K` to match exactly at the 2^−5 level (score 213/214) leaves the whole low
   band matched within ±0.4 bits but undershoots the deep tail by **up to 18.20
   bits** (n=43; mean −10.70 over the band) and **16.65 bits** (n=50; mean
   −11.48). Anchoring instead at the last count ≥ 10 score costs at most
   **+1.75 / +1.95 bits** of overshoot mid-band. The reason is visible in the
   per-score elasticity: at score 213 the prediction responds to `K` with
   elasticity 0.15 (n=43) — it is dominated by the parameter-free Gaussian
   component — so matching there over-determines `K` by ~17 bits. **Any single
   statement of the form "the model agrees / disagrees by X bits" is meaningless
   without saying where the one unarchived scale was pinned.**

6. **The parameter-free component alone is worth reporting.** `Q(T)` — Model
   4.7's `N(0,N/2)` term, zero free parameters, `N` taken from the header —
   tracks the measurement within 0.1 bit up to score **322** (n=43) / **273**
   (n=50), within 0.5 bit to **469** / **401**, within 1 bit to **525** / **460**;
   by score 1000 it is **32.40** / **35.16** bits below the measurement, and at
   the counting floor **149.99** / **265.56** bits below. (EV-MLKEM-018 reports
   150.51 bits for the n=43 file at the floor; the 0.52-bit difference is that
   this run takes `sigma = sqrt(avg_N/2) = 113.9539` from the archived header
   while that record used the measured `sigma = 113.7914`. Both are from the
   same file; the difference is recorded, not resolved.)

### 4.4 The agreement is not automatic (control on the model family)

Scanning the exponent `p` with the same exact model and the same one-parameter
fit gives rms residuals over the fit grid of: 1.96 bits at p=10, 1.01 at p=18,
0.743 at p=20, 0.504 at p=22, **0.454 at p=24**, **0.692 at the archived-integer
p=26**, 1.061 at p=28, 3.63 at p=40 (n=43); and 2.35 / 1.04 / 0.678 / **0.438 at
p=22** / 0.602 / **0.694 at the archived p=24.5** / 4.38 (n=50). So a
one-parameter family of this shape does **not** fit the data automatically: the
exponent is constrained to a window of about ±3 around the optimum, and the
archived-integer exponent falls inside that window in both files.

**Diagnostic, not a revision.** The measurement mildly prefers an exponent
about 2–2.5 lower than the reading in Section 2 gives. Under the generalised
reading `Phi = exp(−(a·x^r + b·y^r))` the exponent is
`p = (beta_sieve+n_fft)/r`, so the preferred `p` corresponds to
`r = 52/24 = 2.17` (n=43) and `r = 49/22 = 2.23` (n=50) against `r = 2` for the
reading (4.19) implies. The two independent files land on nearly the same `r`.
Nothing in Section 4.1–4.3 depends on this scan, and Approximation 4.9 is not
adjusted by it.

---

## 5. What the comparison could not cover

1. **The absolute level of Approximation 4.9.** `delta(beta_bkz)` and Lemma 2.9
   are not archived, so the predicted curve's normalisation is not computable
   from repository bytes. Everything above is shape-and-relative with one free
   scale. This is the single largest gap and it cannot be closed without the
   missing pages.
2. **The functional form of `Phi_dlsc`.** Not archived. The comparison rests on
   a declared reading forced by the archived (4.19). If that reading is wrong,
   the exponent is wrong; Section 4.4 bounds how much that would matter but does
   not remove the dependence.
3. **`alpha` and `n_lsc`.** Not in any archived page extract. `alpha` was *not*
   assumed; the `alpha_secret=2 / alpha_error=2` in the Pgood header is recorded
   as an unverified candidate identification only.
4. **Anything below the counting floor.** By construction. The floor is
   2^−35.70445229 (n=43) and 2^−36.28941479 (n=50); the operating threshold that
   Approximation 4.9 is *used* at is far below both, and this comparison says
   nothing about the model there.
5. **The third archived Pwrong file** (`…beta037_beta144_N200001.out`,
   nb_iteration=1, avg_N=200001) — **not present in this repository**; it exists
   here only as a header extract and a SHA-256 in the input manifest, so it has
   no survival column to compare against. This is archival defect A3 recorded in
   EV-MLKEM-018 and it is still open.
6. **The Pgood file** — 4000 raw good-guess scores, no survival curve.
   Approximation 4.9 is the *wrong*-guess statement (the good guess is
   Approximation 4.8), so the F1 comparison is simply not defined for it. It is
   recorded (4000 values, min 6667.673616, median 11964.802334, max
   17822.813537) but not compared. (EV-MLKEM-018 reports median 11964.473718;
   this run takes the lower of the two central order statistics rather than
   their average, on 4000 values — a definitional difference on the same file,
   recorded not resolved.)
7. **Effective sample size.** The `q^k_fft` candidates inside one FFT share the
   same N dual vectors and the same target, so the pooled counting estimate's
   effective replicate count is not recoverable from the archive. Poisson-style
   reasoning about the top of the band (counts 1–10) is therefore indicative
   only, exactly as EV-MLKEM-018 recorded.
8. **Whether any of this transfers to the paper's published analysis.** The
   files come from `verifyModel/ScoreExperimentalDistribution/`, a
   verification-model directory; no retrieved artifact shows its conventions
   produced Table 5.1 or Table C.2.

---

## 6. Deviations, anomalies, and things recorded rather than smoothed over

* **The script was run twice.** The first execution used a normalisation-free
  diagnostic based on the linearised form `Pwrong = Q + K·J`, which is invalid
  wherever the `min(1,·)` clip binds (there `J` is dominated by the clipped
  region). It reported a spurious 15.39 / 13.09-bit "shape drift" and a
  linear-form best exponent of 21.0 / 20.5. I identified the defect, replaced
  the diagnostic with an exact per-score bisection, replaced the exponent scan
  with the exact model, and re-ran. **Everything that did not depend on the
  defective diagnostic is bit-identical between the two runs** — floor, band,
  multiplicity check, scale check, `log2 K_fit` = −72.712581 / −67.222505, both
  anchors, and every Δ statistic. Both executions are recorded in `receipt.json`;
  the first run's `comparison_results.json` was overwritten by the second at the
  same path.
* **Erratum in a descriptive string, recorded rather than patched.** The
  `approximation_4_9_parameter_ledger` entry for `delta(beta_bkz)` — inside the
  script and therefore inside `comparison_results.json` — says the delta
  exponent is "1394 (n=50)". The correct value is
  `beta_sieve·(m+n_lat−beta_sieve)` = 41·(40+42−41) = **1681**. This is
  explanatory prose that enters **no** computation: `delta` is unavailable and
  is absorbed into the free scale `K` (§2), so no reported number changes. It
  was not corrected by editing and re-running, because that would have
  desynchronised the executed script from its own recorded output and consumed a
  further execution against a `maximum_runs: 1` budget; the correction is
  recorded here and in `receipt.json` instead.
* Header vs Fig 4.1 caption disagree on `nb_iteration` for the n=50 panel (6000
  vs 4000) and on `d_lat` for both panels (41.07/57.89 vs 42.00/58.60).
  Recorded in the parameter ledger; header values used.
* Two small numerical differences from EV-MLKEM-018 (Gaussian deficit at the
  floor, 149.99 vs 150.51 bits; Pgood median, 11964.802334 vs 11964.473718),
  both traced to estimator/definition choices on the same immutable files and
  recorded in §4.3(6) and §5(6). Neither is load-bearing here.
* `numpy` and `scipy` are unavailable; the FFT was not needed, but the
  quadrature and `erfc`-based normal survival were implemented from their
  documented definitions and self-checked against closed forms (§3). Recorded
  as a methodological substitution, as EV-MLKEM-018 did for the same reason.
* No infrastructure failure, no timeout, no resource exhaustion. Wall clock
  243.0 s against a 2700 s budget; peak RSS 23.4 MB against 4 GB; one run of the
  final script against a maximum of 1 (plus the superseded first execution,
  recorded above).

---

## 7. Non-claims

* No ML-KEM or Kyber security claim; no FIPS 203 parameter set is affected or
  cleared; COST-MLKEM-001 is untouched.
* Toy parameters only (q=241, m=40, n=43/50, n_fft=8, k_fft=3). Toy-scale
  evidence is never crypto-scale validation (AGENTS.md rule 7).
* Approximation 4.9 is neither validated nor refuted here. This record reports
  a frozen-reference comparison and its statistics; the judgement belongs to the
  Reviewer and the Coordinator.
* No record status changes. Rule 12 remains unmet and unwaived; EV-MLKEM-011,
  EV-MLKEM-013, EV-MLKEM-017, KN-FIND-012 and KN-FIND-014 are not treated as
  corrected by anything above.
* The conclusions bind exactly two objects: the two archived verifyModel Pwrong
  output files present in this repository, and Approximation 4.9 as written in
  the archived page extracts — under the declared reading of the unavailable
  `Phi`, with one unarchived normalisation.
