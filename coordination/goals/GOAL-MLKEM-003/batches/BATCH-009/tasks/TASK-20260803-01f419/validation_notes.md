# Validation notes — exactly what I recomputed

**Task** TASK-20260803-01f419 · **Batch** BATCH-009 · **Goal** GOAL-MLKEM-003
**Role** validator (independent; did not produce the package under review)
**Supersedes** TASK-20260802-08f428 (died on a provider session limit before writing a verdict)
**Package under review** snapshot commit `d0f2bf7f1770f26833be4e888b0faee0cb67e4a8`
**Report id** VAL-20260803-3346d2

Requested policy `review-adversarial`, reasoning effort `xhigh`, independent
session required. Resolved model `claude-opus-5`; `fallback_used: true` (the
policy alias routes to a GPT-5.6-family identifier this harness cannot resolve;
CLAUDE.md "Model policy note"). No probe verification was possible.

Everything below is a number I computed myself in this session from the raw
bytes or from my own re-derivation of Approximation 4.9. Where my digits differ
from the producer's I give both. Nothing is copied from the producer's
transcript, and nothing is copied from the superseded TASK-20260802-08f428
notes — see §12 for exactly what I did and did not read of those.

---

## 0. Archival binding

```
git log --oneline -1 d0f2bf7f1770   -> d0f2bf7f coordination: TASK-20260802-7c4aee
                                       snapshot of the BATCH-009 F1 comparison
git merge-base --is-ancestor d0f2bf7f1770 HEAD  -> ancestor of HEAD
```

The commit changes exactly five paths: the snapshot receipt plus the four
artifacts under review (`approx49_comparison.py`, `comparison_report.md`,
`comparison_results.json`, `receipt.json`). This is a Coordinator-committed
snapshot, not a working-tree-only receipt, so it is admissible for review.

Input file digests, recomputed with `hashlib.sha256`:

| file | sha256 |
|---|---|
| `Pwrong_…n43…N25971.out` | `50bd293cadf952516b092524c25f4404a1e4ca40983d1751286f96269dbf90bb` |
| `Pwrong_…n50…N25970.out` | `ce23181dca95a1c6a72463c2c39f14f645500a068b3af46c71d5b45af69ab459` |
| `Pgood_…n43…N25971.out`  | `f1e9cf478928e51fa772549ceb01359d98be0d90af25b784d5966bc1652dc5e1` |

These match the digests recorded in `comparison_results.json`.

---

## 1. Resolved band and counting floor — recomputed from the raw bytes

Loaded each `.out` file, parsed the `#` header, read the survival column.

| quantity | n=43 | n=50 |
|---|---|---|
| header `nb_iteration` | 4000 | 6000 |
| `nb_iteration · q^k_fft` | 55 990 084 000 | 83 985 126 000 |
| floor `1/(nb·q^k)` | `1.7860305406935986e-11` | `1.1906870271290657e-11` |
| floor log2 | **−35.70445229** | **−36.28941479** |
| data lines | 1804 | 2311 |
| last positive score | **1802** | **2309** |
| first zero score | 1803 | 2310 |
| last positive value == floor as exact IEEE-754 equality | **True** | **True** |
| all values from the first zero onward are exactly 0.0 | True | True |
| zeros strictly inside the band | 0 | 0 |
| survival monotone non-increasing over the band | True | True |
| log2 of the value at score 0 | −1.002880 | −1.005054 |

Every value in each band is an integer multiple of the quantum. Maximum
relative deviation from an integer multiple depends on the floating-point path:

| definition | n=43 | n=50 |
|---|---|---|
| `c = v·(nb·q^k)` (integer denominator) | 1.3605e-16 | 1.8152e-16 |
| `c = v/floor` (float reciprocal) | **2.164964e-16** | 1.8152e-16 |

The producer records 2.164964216343976e-16 and 1.815e-16, i.e. the `v/floor`
path. **Reproduced** once the path is fixed; the two paths differ only in
rounding.

**Both floors equal exactly `1/(nb_iteration · q^k_fft)`. Confirmed.**

### nb_iteration for n=50: header 6000 vs Fig 4.1 caption 4000 (check 8)

The producer used 6000, justified as "the file's own record of how it was
produced". That justification is weaker than what the data support. I tested
the hypothesis directly by asking which `nb_iteration` makes every value an
integer multiple of `1/(nb·241³)`:

| nb_iteration | max &#124;count − round(count)&#124; | all integer? |
|---|---|---|
| 4000 | 0.3333 | **No** |
| 5000 | 0.5 | No |
| **6000** | 3.8e-06 | **Yes** |
| 8000 | 0.3333 | No |
| 12000 | 7.6e-06 | Yes |

The last positive value is exactly `2/3` of the 4000-quantum
(`1.1906870271290657e-11 × 4000 × 241³ = 0.666667`). **The caption's 4000 is
excluded by the file's own bytes; the data force `nb_iteration ∈ {6000, 12000,
…}` and the header says 6000.** The choice is correct, is stated, and is in
fact forced — the report under-argues it. EV-MLKEM-018 already recorded
`nb_iteration=6000` for this file (line 148 of that record), consistent.

Pooled-count boundaries, recomputed: the last score with pooled count ≥ 10 is
**1492** (count exactly 10) and **1968** (count exactly 10). Matches.

---

## 2. Score scale — is any k_fft alignment applied? (check 4, explicitly answered)

**Answer: no k_fft alignment is applied anywhere in the package, and the raw
undivided convention is the one the data support.** I re-derived the two σ
estimators from each file's own survival column without reading the producer's
code. For an integer-valued score `F` with `S(i) = P(F ≥ i)`,
`E[F²·1{F≥0}] = Σ_{i≥1}(2i−1)S(i)`, so

* estimator A `= sqrt(E[F²|F≥0]) = sqrt(Σ(2i−1)S(i)/S(0))`
* estimator B `= sqrt(2·Σ(2i−1)S(i))` (symmetric about 0)

| quantity | n=43 | n=50 |
|---|---|---|
| estimator A (mine) | **113.9050762921** | **114.1780904095** |
| estimator A (producer) | 113.90507629207004 | 114.1780904095 |
| estimator B (mine) | **113.7914383483** | **113.9782591255** |
| estimator B (producer) | 113.79143834833933 | 113.9782591255 |
| Model 4.7 raw `sqrt(avg_N/2)` | 113.9539380627 | 113.9517441727 |
| A / raw, B / raw | 0.999571, 0.998574 | 1.001986, 1.000233 |
| A / (raw/k_fft), B / (raw/k_fft) | 2.998714, 2.995722 | 3.005959, 3.000698 |

I guessed the estimator definitions from the report's one-line description and
hit the producer's digits exactly, which is itself a strong cross-check.
Both estimators, in both files, sit within 0.2% of the raw prediction and at
≈3.0 against the `/k_fft` prediction. This reproduces EV-MLKEM-018's finding
that `FFT()`'s `/k_fft` cancels a duplicate accumulation in `init()`, from the
same bytes and by my own arithmetic. **The prohibited k_fft alignment is not
applied.**

---

## 3. Approximation 4.9 — re-derived independently from the archived extracts

I wrote my own implementation before reading `approx49_comparison.py`, from
`inputs/MLKEM-DUAL-SOURCES-20260802/extracts/carrier-hal-05406481/page23_approx_4_8_4_9.txt`.

Model 4.7: score ~ `D + N(0,N/2)` with **standard deviation** `sqrt(N/2)`, so
`Q(T) := P(N(0,N/2) ≥ T) = 0.5·erfc(T/sqrt(N))` and the noise density is
`φ(t) = exp(−t²/N)/sqrt(πN)`.

The prefactor of (4.22), `exp(−t²/N − (d−µ)²/2σ²)/(π σ sqrt(2N))`, is exactly
`φ(t)·ψ_lsc(d)` — I verified the normalisation algebraically:
`1/(sqrt(πN)·σ sqrt(2π)) = 1/(π σ sqrt(2N))`. So (4.22) is
`E_{t,d}[ min(1, ∫_{E(T−t)} λµ) ]`, a convolution, as the Fig 4.1 legend
`(D + N(0,N/2) ≥ T)` says.

**Declared reading of the unarchived Φ.** With `Φ_d(x,y) = exp(−(a x² + b y²))`,
`E(u) = {a x² + b y² ≤ L}`, `L = ln(N/u)`; with `λ ∝ x^{β_sieve−1}`,
`µ ∝ y^{n_fft−1}` from (4.24), the substitution `x = sqrt(L/a)s`, `y = sqrt(L/b)w`
gives `∫_{E(u)} λµ = K·L^p` with

```
p = (beta_sieve + n_fft)/2   ->   p = 26.0 (n=43),  p = 24.5 (n=50)
```

and `K` absorbing `δ(β_bkz)`, `α`, the Γ factors and the `q` powers. I confirm
independently that **every unavailable quantity collapses into the single scale
`K`, and that the exponent `p` is fixed by archived integers.** Hence

```
Pwrong(T;K) = Q(T) + [Q(T−u*) − Q(T)] + K·∫_{u*}^{N} φ(T−u)·ln(N/u)^p du
u* = N·exp(−K^{−1/p})   (the point where K·ln(N/u)^p = 1)
```

**Quadrature (mine, independent).** Composite Gauss–Legendre in `u`, panels
placed at `T + c·sqrt(N/2)` for `c ∈ {−14,…,+14}`, evaluated in log space.
Self-checks I ran:

* against `scipy.integrate.quad` with `epsrel=1e-12`: max relative difference
  **3.1e-14** over `T ∈ {0,180,471,900,1440,1802}`;
* node-count convergence 60 → 120 → 240 nodes: agreement to 1e-15;
* the `[0,u*]` clip mass is closed form (`Q(T−u*) − Q(T)`), not quadrature.

**Cross-check against the producer's own intermediate.** Their
`model.quadrature.coarse_vs_fine_J` records `J_fine(T=1802) =
148448286316.18793`. My integral at their `log2 K` is `1.4844828631618698e11` —
agreement to **6e-15 relative**. (Their `J` at smaller `T` is the *unclipped*
`∫_0^N`, a different quantity, which is why it is larger there; that is an
internal diagnostic, not the prediction.)

`numpy 2.4.6` and `scipy 1.17.1` import successfully in my session under the
same recorded Python (3.11.15) and platform. The producer's receipt records
`numpy_available: false`. I could not reproduce that environment claim; it may
be a sandbox difference between sessions. It changes nothing — I verified their
numerics against scipy and they hold.

---

## 4. Recomputed statistics — my own fit, and at the producer's exact K

### 4.1 My own least-squares fit on log2 residuals over the resolved band

| quantity | mine | producer | Δ |
|---|---|---|---|
| n=43 `log2 K_fit` | **−72.711622** | −72.712581 | 0.00096 |
| n=50 `log2 K_fit` | **−67.219917** | −67.222505 | 0.00259 |

Residual `Δ = log2(pred) − log2(meas)`:

| file | band | n | min | max | mean | rms |
|---|---|---|---|---|---|---|
| n=43 | whole [0,1802] | 1803 | **−0.9316** (−0.933) | **+1.5158** (+1.516) | **+0.2456** (+0.245) | **0.7055** (0.706) |
| n=43 | count ≥ 10 | 1493 | −0.6740 (−0.675) | +1.5158 | +0.3591 (0.359) | 0.7419 (0.742) |
| n=43 | clip-negligible ∧ count ≥ 10 | **737** (738) | −0.6740 (−0.675) | +0.1807 (+0.182) | −0.2013 (−0.202) | **0.2823** (0.283) |
| n=50 | whole [0,2309] | 2310 | −0.9144 (−0.917) | +1.7120 (+1.710) | +0.1942 (0.192) | 0.6969 (0.697) |
| n=50 | count ≥ 10 | 1969 | −0.6378 (−0.640) | +1.7120 | +0.2816 (0.279) | 0.7278 (0.727) |
| n=50 | clip-negligible ∧ count ≥ 10 | **1242** (1242) | −0.6378 (−0.640) | +0.2471 (+0.244) | −0.1605 (−0.163) | **0.2722** (0.274) |

(producer's value in parentheses). Sub-band ranges: mine **[756,1492]** vs their
**[755,1492]** for n=43; **[727,1968]** for n=50, identical.

`argmax Δ` = **471** (n=43) and **420** (n=50); `argmin Δ` = **1616** and
**2283**. All four match.

### 4.2 The decisive check — my model evaluated at *their* K

Setting `log2 K` to their published value and comparing my `log2 pred` against
their `log2_pred_Kfit` column at every one of the 1803 / 2310 scores:

```
n=43  max |mine − theirs| = 6.57e-04 bits   (worst at score 459)
n=50  max |mine − theirs| = 4.65e-04 bits   (worst at score 401)
log2 Q column:            max diff 2.8e-14 / 5.7e-14 bits
log2 measured column:     max diff 0.0    / 0.0
log2 P(D ≥ T) column:     max diff 7.1e-15 / 7.1e-15
```

**The producer's implementation of Approximation 4.9 reproduces under an
independent re-implementation to better than 7e-4 bits across the whole band.**
The remaining 6e-4 bits sits in the crossover region and is a clip-boundary
quadrature difference. Every statistic the report quotes to three decimals is
insensitive to it.

### 4.3 Anchors, elasticity, Gaussian-only component

| quantity | mine | producer |
|---|---|---|
| first score with meas ≤ 2^−5 | 213 / 214 | 213 / 214 |
| `log2 K_anchor_low` | −89.978460 / −82.956085 | −89.979061 / −82.956451 |
| `log2 K_anchor_high` (at 1492 / 1968) | **−72.147621 / −66.704753** | −72.147621 / −66.704753 (exact) |
| deep-tail undershoot at `K_anchor_low` | **−18.198 / −16.651** bits | −18.20 / −16.65 |
| mean Δ at `K_anchor_low` | −10.697 / −11.476 | −10.70 / −11.48 |
| max overshoot at `K_anchor_high` | +1.752 / +1.945 | +1.75 / +1.95 |
| elasticity at score 213 at `K_fit` | ≈0.15 (0.134 at 180, 0.260 at 360) | 0.15 |
| elasticity at score 471 / 420 | 0.3767 / 0.424 | 0.37671 / 0.424 |

The `K_anchor_low` values differ in the 4th decimal while `K_anchor_high` is
exact to 6 decimals. That is the expected consequence of the elasticity: at
score 213 the elasticity at the anchoring K is 0.006, so a 1e-6-bit difference
in the prediction is amplified ~175× in `K`. The report's own point 5 — that
anchoring where the parameter-free Gaussian dominates over-determines `K` by
~17 bits — is reproduced and is correct.

Parameter-free Gaussian component `Q(T)` alone, zero free parameters:

| threshold | n=43 | n=50 |
|---|---|---|
| &#124;log2 Q − log2 meas&#124; ≤ 0.1 bit up to score | **322** | **273** |
| ≤ 0.5 bit up to | **469** | **401** |
| ≤ 1.0 bit up to | **525** | **460** |
| deficit at score 1000 | **32.4000** bits | **35.1561** bits |
| deficit at the floor | **149.9930** bits | **265.5570** bits |

All reproduce. The 149.993 vs EV-MLKEM-018's 150.51 is explained exactly by
`sqrt(avg_N/2) = 113.9539` vs the measured `113.7914`, as the report says.

### 4.4 Per-score table of report §4.2 (n=43), recomputed

| score | log2 meas | count | log2 Q | log2 pred | Δ |
|---|---|---|---|---|---|
| 0 | −1.0029 | 27 939 211 089 | −1.0000 | −0.7019 | +0.301 |
| 180 | −4.1207 | 3 218 577 702 | −4.1303 | −3.3179 | +0.803 |
| 360 | −10.1502 | 49 271 503 | −10.3039 | −8.8183 | +1.332 |
| 471 | −15.2599 | 1 427 026 | −15.7710 | −13.7441 | **+1.516** |
| 540 | −18.6109 | 139 854 | −19.8270 | −17.2410 | +1.370 |
| 630 | −21.8645 | 14 664 | −25.8844 | −21.2494 | +0.615 |
| 720 | −23.7097 | 4 081 | −32.8166 | −23.4888 | +0.221 |
| 900 | −26.3713 | 645 | −49.3252 | −26.3700 | +0.001 |
| 1080 | −28.4471 | 153 | −69.3797 | −28.6839 | −0.237 |
| 1260 | −30.2782 | 43 | −92.9958 | −30.6816 | −0.403 |
| 1440 | −32.1195 | 12 | −120.1831 | −32.4633 | −0.344 |
| 1616 | −33.1195 | 6 | −150.2257 | −34.0511 | **−0.932** |
| 1710 | −34.7045 | 2 | −167.6740 | −34.8488 | −0.144 |
| 1802 | −35.7045 | 1 | −185.6975 | −35.6005 | +0.104 |

Every measured value and pooled count matches exactly; every prediction matches
to ≤0.001 bits (the `log2 K_fit` difference). n=50 spot checks: score 420
Δ=+1.712, score 1090 Δ=+0.002, score 2283 Δ=−0.914, score 2309 Δ=+0.503 —
all match.

### 4.5 The measurement below the model's parameter-free floor

`Q(T)` is a hard lower bound on the model's survival because `D ≥ 0`. I find
the measurement strictly below `Q` on a **contiguous** run of scores:

| file | scores | max shortfall |
|---|---|---|
| n=43 | **0 … 126** | **0.00369 bits** |
| n=50 | **0 … 133** | **0.00693 bits** |

Reproduced (producer: 0–126 / 0–133, ≤0.0037 / ≤0.0069). No `K ≥ 0` reproduces
those scores; the statement is structurally correct.

### 4.6 The sign-change wobble

My residual first changes sign at **891** (n=43) and **1094** (n=50) with 10
and 18 sign changes; the producer's own table gives 888 / 1090 with 12 and 14,
and I verified those counts directly from their `delta_Kfit_bits` column. The
difference is entirely the ~0.001-bit `K_fit` offset acting on residuals that
are already crossing zero. Substantively identical (the same wobble clusters,
888–909 and 1090–1173); the exact count is fit-tolerance noise and should not
be quoted to that precision.

### 4.7 Per-score solved `K` drift — the one number that does not survive as stated

The producer's §4.3(1) says the per-score solved scale "drifts by only **1.150
bits** (n=43, over scores 643–1492, range −73.298 … −72.038)". I recompute over
the same score range:

| file | range | min | max | **max − min** | endpoint(hi) − endpoint(lo) |
|---|---|---|---|---|---|
| n=43 | 643–1492 | −73.298 | −72.038 | **1.260** | 1.150 |
| n=50 | 600–1968 | −67.943 | −66.582 | **1.361** | 1.238 |

Their `comparison_results.json` labels both correctly
(`drift_bits_low_to_high` = 1.1504 / 1.2377; `min`/`max` whose difference is
1.2604 / 1.3603). The **report sentence** puts the endpoint-to-endpoint drift
and the min…max range side by side as if they were the same statistic, and a
reader subtracting the quoted endpoints gets 1.260, not 1.150. The larger
figure is the conservative one and is the one that bears on how well a single
`K` serves the sub-band. Numbered defect D1.

Over my own clip-negligible ∧ count ≥ 10 sub-bands the drift is 0.855 bits
(756–1492) and 0.885 bits (727–1968). Non-monotone in both files — reproduced.

---

## 5. Nothing compared, fitted or extrapolated past the counting floor (check 4)

Verified directly against `comparison_results.json`:

* `per_score` has 1803 rows, scores 0…1802 contiguous; and 2310 rows, 0…2309.
  Both stop exactly at the last resolved score.
* no `measured` value in either table is ≤ 0; the minimum equals the counting
  floor as an exact float equality.
* every derived grid lies inside the band: exponent-scan `fit_scores` [0,1802]
  and [0,2309]; anchors 213/1492 and 214/1968; shape-test ranges [643,1492] and
  [600,1968].

**No comparison, fit, anchor, scan point or extrapolation touches a score at or
above the first zero. The first prohibited failure mode is absent.**

---

## 6. Controls — the producer's, reproduced; then sharper ones I ran (check 3)

### 6.1 Reproduction of the producer's exponent scan

Their scan fits `K` on a subsampled grid (`n_fit_scores` = 47 and 59 — a fact
the report does not state, though it does say "over the fit grid"). Mine refits
`K` on the **whole resolved band**:

| p | mine (n=43) | producer | mine (n=50) | producer |
|---|---|---|---|---|
| 10 | 1.893 | 1.960 | 2.327 | 2.348 |
| 18 | 0.968 | 1.010 | 1.024 | 1.037 |
| 20 | 0.707 | 0.743 | 0.667 | 0.678 |
| 22 | 0.480 | 0.504 | **0.431** | 0.438 |
| 24 | **0.454** | 0.454 | 0.604 | 0.602 |
| 24.5 | 0.497 | — | 0.697 | **0.694** |
| 26 | 0.706 | **0.692** | 1.020 | 1.016 |
| 28 | 1.076 | 1.061 | 1.497 | 1.492 |
| 40 | 3.626 | 3.632 | 4.382 | 4.383 |

Reproduced to ≤0.07 bits, the difference being the fit grid.

### 6.2 A fine sweep — how wide is the basin?

Sweep `p` from 10 to 40 in steps of 0.5, refitting `K` at each `p`, on the
whole band and on the clip-negligible ∧ count ≥ 10 sub-band:

| file | grid | best p | rms at best | rms at archived p | {p : rms ≤ rms(p_archived)} | {p : rms ≤ 1 bit} |
|---|---|---|---|---|---|---|
| n=43 | whole band | 23.0 | 0.427 | 0.706 (p=26) | **[20.5, 26.0]** width 5.5 | [18.0, 27.5] width 9.5 |
| n=43 | sub-band | 24.5 | 0.111 | 0.198 (p=26) | [23.0, 26.0] width 3.0 | [15.0, 33.5] width 18.5 |
| n=50 | whole band | 22.0 | 0.431 | 0.697 (p=24.5) | **[20.0, 24.5]** width 4.5 | [18.5, 25.5] width 7.0 |
| n=50 | sub-band | 23.0 | 0.077 | 0.220 (p=24.5) | [22.0, 24.5] width 2.5 | [16.5, 29.5] width 13.0 |

**In both files the archived exponent is the upper endpoint of its own
acceptance set.** `p = 10` and `p = 40` sit 13–18 units from the optimum, far
outside the basin, so the producer's non-degeneracy control tests a regime the
data never made plausible. The report does disclose the preference for a lower
exponent (§4.4) and derives `r = 2.17 / 2.23`; nothing is concealed. But the
control as run does not establish that the data select the archived exponent.

Alternative readings `Φ = exp(−(a x^r + b y^r))`, `p = (β_sieve+n_fft)/r`:

| r | p (n=43) | whole-band rms | p (n=50) | whole-band rms |
|---|---|---|---|---|
| 1 | 52.00 | 5.943 | 49.00 | 6.282 |
| 1.5 | 34.67 | 2.492 | 32.67 | 2.647 |
| **2** | **26.00** | **0.706** | **24.50** | **0.697** |
| 3 | 17.33 | 1.053 | 16.33 | 1.320 |
| 4 | 13.00 | 1.566 | 12.25 | 1.986 |

Among the integer/half-integer readings, `r = 2` is the best in both files.
That is a real, if coarse, discrimination in the declared reading's favour.

### 6.3 What the tail comparison actually is, dimensionally

Where the D component carries the prediction, `log2 pred ≈ log2 K + p·X` with
`X = log2 ln(N/T)`. Over the clip-negligible ∧ count ≥ 10 sub-band,

```
n=43: X spans 1.5144 … 1.8224   (range 0.3080)
n=50: X spans 1.3673 … 1.8383   (range 0.4709)
```

**A lever arm of one third to one half of one octave in the fit variable.**
Free two-parameter straight line in `X`:

| file | fitted slope b | archived p | rms |
|---|---|---|---|
| n=43 | **26.515** | 26.0 | 0.1048 |
| n=50 | **24.549** | 24.5 | 0.0987 |

Slope fixed at the archived `p`, intercept only: rms 0.1143 / 0.0989.

This is the strongest single result in the package and the producer did not
extract it: **the empirical tail exponent recovered with no constraint is
26.515 against an archived-integer prediction of 26.0, and 24.549 against
24.5.** Moreover the exact-model sub-band optimum shifts by exactly **1.50**
between the two files (24.50 → 23.00), matching the archived prediction
`Δp = (44−41)/2 = 1.50`; equivalently `r = 52/24.5 = 2.122` and
`r = 49/23.0 = 2.130`, agreeing across two independent files to 0.4%. A pure
fitting artifact would not have to pass a cross-file consistency check.

Note also that the *exact* clipped model at the archived `p` fits the sub-band
worse (rms 0.198 / 0.220 with `K` refit there) than the bare straight line with
the same slope (0.114 / 0.099). The Gaussian-convolution curvature that the
exact model adds over that window is not supported by the data at the 0.1-bit
level.

### 6.4 Null-object control (inventor-protocol §3) — not run by the producer

Best two-parameter fit of `log2(measured)` on the same clip-negligible ∧
count ≥ 10 sub-band, one shape variable each:

| family | rms n=43 | rms n=50 |
|---|---|---|
| `a + b·log2 ln(N/T)` (the Approximation 4.9 tail form) | **0.1048** | **0.0987** |
| `a + b·T^{1/3}` | 0.1051 | 0.1007 |
| `a + b·√T` | 0.1110 | 0.1541 |
| `a + b·log2 T` | 0.1242 | 0.1092 |
| `a + b·T` | 0.1723 | 0.3455 |
| `a + b·T²` | 0.3481 | 0.7204 |

Over the window where Approximation 4.9's D component actually carries the
prediction, **its functional form is not distinguishable from a cube-root or
log-power tail at the same number of free parameters.** Only the Gaussian shape
is clearly excluded. The shape agreement is therefore consistent with
Approximation 4.9 but does not select it.

### 6.5 Effective sample size

Residual autocorrelation over the sub-band:

| lag | 1 | 10 | 50 | 100 | 200 |
|---|---|---|---|---|---|
| n=43 | 0.992 | 0.908 | 0.574 | 0.349 | 0.176 |
| n=50 | 0.996 | 0.958 | 0.814 | 0.663 | 0.450 |

Naive AR(1) effective sample size: **3.1 of 737 points** (n=43) and **2.6 of
1242** (n=50). The measurement is one pooled cumulative count from 4000 / 6000
iterations; consecutive scores are nearly the same statistic. "~1800 points" is
not ~1800 independent constraints, and the report's §5(7) already says the
effective replicate count is not recoverable from the archive.

Regime decomposition of the "34.7 bits of dynamic range":

| file | scores where `Q` ≥ 50% of the prediction | bits carried there | rms of `log2 Q − log2 meas` there (**zero** free parameters) | bits carried above |
|---|---|---|---|---|
| n=43 | 0 … 234 | 4.61 | **0.0100** | 30.06 |
| n=50 | 0 … 172 | 2.91 | **0.0059** | 32.35 |

The low band is tracked to a hundredth of a bit by Model 4.7's parameter-free
Gaussian, not by Approximation 4.9's D component. The report says this in
§4.3(6), but the headline sentence merges the two regimes.

### 6.6 The divergence profile is confounded with the report's own reduction

The script states that replacing `K(dlsc)` by one effective `K̄` is exact only
in the unclipped regime and is "an approximation rather than an identity"
where the clip binds. `min(1, K·L^p)` is **concave in K**, so by Jensen
`E_dlsc[min(1, K(d)L^p)] ≤ min(1, K̄ L^p)`: the single-`K̄` prediction is an
**upper bound** wherever the clip binds. That is the sign of the reported
divergence. I measured the association:

| file | corr(Δ, clipped fraction) | mean Δ where clip > 1% | mean Δ where clip ≤ 0.1% | argmax Δ (clip there) | argmax clip |
|---|---|---|---|---|---|
| n=43 | **0.916** | **+0.959** (n=702) | −0.231 (n=1047) | 471 (0.377) | 409 (0.388) |
| n=50 | **0.904** | **+1.103** (n=668) | −0.193 (n=1583) | 420 (0.378) | 337 (0.400) |

The entire positive-residual structure lives in the clip-active region. Upper
bound on how much of it this can explain: zeroing the whole clip contribution
moves the prediction by at most **0.682 bits** (n=43) and **0.685 bits** (n=50)
at the residual peak, so the effect accounts for at most ~45% of the +1.516 /
+1.710 peaks — a partial, not a complete, explanation. The report notes the
maxima coincide with a clipped fraction of 0.361 / 0.381 but reads that as the
D-vs-Gaussian crossover only; it does not record that it is also the region
where its own reduction is not an identity, nor the direction of that bias.

---

## 7. The four "unavailable" parameters — searched, not assumed (check 5)

I searched `inputs/`, `knowledge/`, `ledger/`, `coordination/` and
`experiments/`, excluding the producer's own task directory.

* **`Φ_dlsc(x,y)`** — occurs only in `page23_approx_4_8_4_9.txt` (eqs 4.17,
  4.18, 4.23) and `page25_pwrong_validation.txt` (4.23 restated), always *used*,
  never *defined*. Approximation 4.6, which introduces it, is referenced on
  page 23 and its page is not in the archive. **Genuinely absent.**
* **`δ(β_bkz)` / Lemma 2.9** — symbolic in (4.24) only. No numerical value
  anywhere. `knowledge/techniques/KN-TECH-020.md` names the root-Hermite factor
  and says a BKZ-2.0 simulator predicts it, but gives no formula and no number.
  **Genuinely absent.**
* **`α`** — appears in the extracts only symbolically, inside (4.19) and inside
  the page-25 locus `(sqrt(αβ_sieve/2), sqrt(α n_lsc/2))`. No numerical value in
  any archived page. **Genuinely absent.**
* **`n_lsc`** — occurs once, in that same page-25 locus, undefined; and once as
  a truncated word fragment in `source_reads.json`'s Fig 4.1 caption snippet.
  **Genuinely absent.**

**Is "the absolute level is untestable from archived bytes" right?** Yes, and
the report under-argues it while mis-attributing it. The report pins the
untestability on `δ(β_bkz)` and its exponent
`β_sieve(m+n_lat−β_sieve)`; I confirm the arithmetic — `44·31 = 1364` and
`41·41 = 1681`, and `1.001^1364 → 1.97 bits`, `1.001^1681 → 2.42 bits`, matching
the quoted "roughly 2.0 and 2.4 bits". But `α` and Φ's constants are *each
independently sufficient* to make the level uncomputable, and δ is the weakest
of the three links because the root-Hermite factor is a standard predictable
quantity in the wider literature. The conclusion stands on the stronger legs;
the stated reason is narrower than the true one.

Related prose inconsistency: §2 of the report says the archived (4.19)
"**forces**" Φ to be exponential in a negative quadratic form, while §5(2)
calls it "**a declared reading**". These are different epistemic statuses.
(4.19) fixes one functional of Φ (its good-guess expectation) and rules out
readings with no decay in `y` (the `µ` integral would diverge), but does not
determine Φ. The script's own text uses the correct weaker phrasing
("EXPLICITLY AS A DERIVED READING AND NOT AS AN ARCHIVED DEFINITION").

---

## 8. The producer's two self-reported items (check 6)

**Two executions.** `receipt.json` records execution 1 (49.6 s, superseded:
a linearised `Pwrong = Q + K·J` diagnostic invalid where the `min(1,·)` clip
binds) and execution 2 (243.078 s, final). The disclosure is complete, names
the defect, quotes the superseded numbers (spurious drift 15.3854 / 13.0930
bits; linear-form best `p` 21.0 / 20.5) and states the artifact disposition.
That is the right shape for a disclosure.

The claim that *"everything not derived from the defective diagnostic is
bit-identical between the two runs"* is **unable_to_check**: execution 1's
`comparison_results.json` was overwritten in place at the same path and is not
in the snapshot, so no artifact exists to diff. I record it as an
unverifiable producer self-report. It is *consistent* with my re-derivation —
`log2 K_fit`, both anchors and every Δ statistic reproduce independently — but
consistency with my run is not evidence about their first run.

**Budget.** The handoff for TASK-20260802-8bae8e sets `maximum_runs: 1`. Two
executions were performed. The receipt records `script_executions_performed: 2`,
`maximum_runs_allowed: 1` and `budget_exceeded: false`. The boolean is wrong;
the overrun is disclosed everywhere else. Numbered defect D5.

**The 1394 / 1681 erratum.** `1394` occurs exactly once in the script (line
1002) and once in `comparison_results.json`, both inside the descriptive
`what_this_blocks` string of the `delta(beta_bkz)` ledger entry. I confirmed by
exhaustive search that the token enters no computation, and that the correct
value is `β_sieve(m+n_lat−β_sieve) = 41·(40+42−41) = 1681`. The companion
`1364` for n=43 is correct. **Erratum confirmed, and confirmed harmless.**

---

## 9. `alpha_secret` / `alpha_error` (check 7)

The Pgood header carries `# alpha_secret=2` and `# alpha_error=2` (lines 2–3 of
that file). Every occurrence of `alpha` in `approx49_comparison.py` is one of:
a comment reproducing (4.19); the parameter-ledger prose recording `α` as
unavailable; the two `header_alpha_secret` / `header_alpha_error` fields that
copy the header strings into `files_not_compared`; and the stdout line that
prints them. **No numeric `α` is ever bound to a variable that enters a
computation**, and the exponent `p = (β_sieve+n_fft)/2` does not contain `α` by
construction (α is absorbed into `K` by the substitution in §3). The
identification is recorded as an unverified candidate and is not used.
**Confirmed as claimed.**

---

## 10. Two further checks the report does not survive cleanly

**Pgood median.** I sorted the 4000 values:

```
v[1999] = 11964.145101     (lower central order statistic)
v[2000] = 11964.802334     (upper central order statistic)
average = 11964.473718     (= EV-MLKEM-018's value, = numpy median)
min     =  6667.673616     max = 17822.813537     mean = 11983.505048
```

The producer reports `median = 11964.802334` and explains the difference from
EV-MLKEM-018 as "this run takes **the lower** of the two central order
statistics rather than their average". **11964.802334 is the upper, not the
lower.** The number is a genuine order statistic of the file; the stated
definition of it is wrong. Non-load-bearing — the Pgood file is not compared.
Numbered defect D2.

**Clipped-fraction column.** At the producer's own `K`, my exact clip mass
`Q(T−u*) − Q(T)` divided by the prediction differs from their
`clipped_fraction_of_pred_Kfit` by ratio 1.028–1.103 (n=43) and 0.978–0.995
(n=50). The sign of the disagreement flips between files, which points to a
quadrature treatment of the clip boundary rather than a different definition.
Consequence: the declared "clip-negligible" sub-band starts at 755 in their
report and 756 in mine, changing `n` from 738 to 737 and the sub-band statistics
in the 3rd decimal. Numbered defect D3.

---

## 11. Timestamps, resources, budget of this validation

* Wall clock of my own computations: ~11 minutes, dominated by the 440 s
  exponent sweep. Budget 2400 s.
* Peak memory well under 4 GB (largest array 1803×13×40 doubles ≈ 7 MB).
* One dispatched run (`maximum_runs: 1`) — this validation performed no
  sampling and no new experiment; all computation is deterministic
  recomputation from committed bytes. No seed exists to record.
* Scratch scripts written under the session scratchpad, not into the
  repository; the only repository writes are the two deliverables inside
  `.../TASK-20260803-01f419/`. No `git commit` was run.

---

## 12. What I read of the superseded TASK-20260802-08f428 notes

I read `infra_failure_receipt.yaml` in full, and of `validation_notes.md` I read
**only the section-heading lines** (a `grep` of lines beginning `#`/`##` plus
lines containing "defect"/"verdict"), and only *after* every computation in
§§1–10 above was already complete and recorded. I read none of its body text,
tables or numbers.

Effect on my conclusions: **none of my numbers or findings comes from it.**
Two of its headings ("The dlsc integral belongs inside the min(1,·)" and "Two
further arithmetic checks the report does not survive cleanly") indicate
overlapping coverage with my §6.6 and §10, which I had already derived and
written. I did not read either section. I mention the overlap here only because
the handoff requires disclosure; it should not be read as corroboration, since
that session never reached a verdict and its work was never checked.

---

## 13. What I could not check

1. **Bit-identity of the superseded execution 1** — its output was overwritten;
   no artifact exists to diff.
2. **The absolute level of Approximation 4.9** — `Φ`, `α`, `δ(β_bkz)` and
   `n_lsc` are absent from every repository byte. The package is a
   shape-and-relative comparison with one free normalisation, exactly as it
   says.
3. **The correctness of the declared reading of `Φ`** — untestable from the
   archive. §6.2 bounds how much the exponent would move; it does not remove
   the dependence.
4. **The third Pwrong file** (`…beta037_beta144_N200001.out`) — header and
   SHA-256 only, no survival column in this repository. Archival defect A3 of
   EV-MLKEM-018, still open.
5. **Effective replicate count** — the `q^k_fft` candidates inside one FFT
   share dual vectors and target, so Poisson reasoning at counts 1–10 is
   indicative only. My §6.5 autocorrelation is a lower-bound-style diagnostic,
   not a resolution of this.
6. **Whether the producer's environment genuinely lacked numpy/scipy** — not
   verifiable from the archive; immaterial, since I verified their numerics
   against scipy independently.
7. **Whether any of this transfers to the paper's published analysis** — the
   files come from a `verifyModel/` directory and no retrieved artifact ties
   its conventions to Table 5.1 or C.2.

---

## 14. Non-claims of this validation

* This is an evidence-integrity verdict on one comparison package. It is **not**
  a verdict on Approximation 4.9, which is neither validated nor refuted here.
* **No ML-KEM or Kyber security claim. No break claim.** All parameters are toy
  (q=241, m=40, n=43/50, n_fft=8, k_fft=3); AGENTS.md rule 7 forbids reading any
  of this as crypto-scale validation.
* **AGENTS.md rule 12 remains UNMET and UNWAIVED.** Nothing here changes or
  treats as corrected EV-MLKEM-011, EV-MLKEM-013, EV-MLKEM-017, KN-FIND-012 or
  KN-FIND-014.
* An admissible receipt is not a promotion, a hypothesis-status change, or a
  cost-model revision. Those are the Reviewer's and Coordinator's calls.
