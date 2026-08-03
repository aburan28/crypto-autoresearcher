# TASK-20260803-bddfa7 — validation notes

Independent validator session. Everything below was recomputed in this session
from archived bytes only. **Zero new sampling, no network, no G6K.** The
vendored PDF was opened read-only (its sha256 re-verified) and nothing was
written to it or to the extract directory. Nothing under
`coordination/goals/GOAL-MLKEM-003/batches/BATCH-012/tasks/TASK-20260803-36f572/`
was modified. No git commit was made.

Reviewed snapshot: **d274699aade09abc81815627d16afaf06085d91a**
(`snapshot: BATCH-012 exact-region-measure package (TASK-20260803-36f572)`),
receipt `../../archives/TASK-20260803-5b602c/snapshot_receipt.json`.

Toy tier throughout (q=241, m=40, n=43/50). **No ML-KEM or Kyber security claim
in either direction.** AGENTS.md rule 12 is UNMET and UNWAIVED: EV-MLKEM-011,
EV-MLKEM-013 and EV-MLKEM-017 keep their status.

---

## 0. Artifact and input integrity

```
$ python3 -c "import hashlib,glob; ..."   # sha256 of the three declared paths
c037b29498a07a8118f16cd93616dc52762eec3a4cbf9401d13efb07d48a5846  exact_region_measure.py
efd047fcb6c446df7b3b1857e0851afeff82bbed9030f82ab105f71e163dc6fe  results.json
9a58a32db51bef2887ba78ca072427344ea9cfd77e4291e561856e74be73a833  report.md
```

All three equal `path_sha256` in the snapshot receipt. Parent
`43978a6cdf4ab629c8b5fa5450bf165ea7b1877c` matches `git log`. Working tree clean.

Inputs:

```
50bd293cadf952516b092524c25f4404a1e4ca40983d1751286f96269dbf90bb  Pwrong_...n43...out
ce23181dca95a1c6a72463c2c39f14f645500a068b3af46c71d5b45af69ab459  Pwrong_...n50...out
083b142256eecaebfa72dfccf847151b2175666a3979cef4e7383376757b8005  Carrier-2022-1750-hal-05406481.pdf
```

All three equal the values recorded in `results.json`. The PDF hash equals the
value the report cites for its read-only access.

Extract directory listing (ANOM-3): `page23_approx_4_8_4_9.txt`,
`page25_pwrong_validation.txt`, `page26_fig41.txt`, `page27_threshold_choice.txt`,
`page37_tables_C1_C2.txt`, `pdf_metadata.json`. **No page 20.** ANOM-3 and the
Coordinator's own check are CONFIRMED a third time.

---

## 1. Part B — the counting-noise floor, re-derived from scratch

Script: `floor_indep.py` (this session). It does not import, read or reference
`exact_region_measure.py`. Independence points against the producer: my own
Poisson window (`14*sqrt(lam)+20` rather than `12*sqrt(lam)+20`), my own
branch switch (`2e5` rather than `1e5`), and a **three-term** asymptotic
`1/λ + (7/4)/λ² + 4/λ³` that I derived myself from
`ln(1+u)² = u² − u³ + (11/12)u⁴ − (5/6)u⁵ + (137/180)u⁶ + …` and the Poisson
central moments `μ₂=λ, μ₃=λ, μ₄=3λ²+λ, μ₅=10λ²+λ, μ₆=15λ³+25λ²+λ`.

### 1.1 Pooled-count recovery

`M = nb_iteration · q^{k_fft}`:

| file | nb_iteration | M | 1/M | log2(1/M) |
|---|---|---|---|---|
| n=43 | 4000 | 55 990 084 000 | 1.7860305406935986e-11 | −35.70445229335197 |
| n=50 | 6000 | 83 985 126 000 | 1.1906870271290657e-11 | −36.28941479407313 |

Max relative deviation of `value·M` from an integer: **1.3604664602099005e-16**
(n=43) and **1.8152171959918975e-16** (n=50) — the producer's 1.360e-16 /
1.815e-16, reproduced. Counts are monotone non-increasing; minimum count in
band is exactly 1 for both files; last positive score 1802 / 2309; band sizes
1803 / 1493 / 852 / 551 and 2310 / 1969 / 1132 / 636 — all reproduced.
121 rows carry count ≤ 2 for n=43 (report ANOM-4) — reproduced.
The recovery `C_T = value·M` is therefore **correct and exact**.

### 1.2 Conditioning on C ≥ 1

The band is defined by the last positive score, so every row in it has C ≥ 1 by
construction. The conditioning is therefore the right one and is implemented
correctly: `E[·|C≥1] = (Σ_{k≥1} …)/(1−e^{−λ})`.

### 1.3 Values (my numbers, computed before reading the producer's)

```
== n43  M=55990084000  band 0..1802
   whole        |idx|= 1803  truncPoisson=0.340570  delta=0.409366
   count>=10    |idx|= 1493  truncPoisson=0.163689  delta=0.154224
   count>=1000  |idx|=  852  truncPoisson=0.014627  delta=0.014620
   count>=1e5   |idx|=  551  truncPoisson=0.001072  delta=0.001072
== n50  M=83985126000  band 0..2309
   whole        |idx|= 2310  truncPoisson=0.327569  delta=0.334742
   count>=10    |idx|= 1969  truncPoisson=0.155755  delta=0.147603
   count>=1000  |idx|= 1132  truncPoisson=0.015192  delta=0.015185
   count>=1e5   |idx|=  636  truncPoisson=0.001357  delta=0.001357
```

**Every published digit of both columns of report.md §2, reproduced.** The
counting floor now has three independent computations.

I also exercised the reproducibility pointer:

```
$ python3 .../exact_region_measure.py --mode floor
```

runs from the committed snapshot in ~4 s, writes nothing, and prints exactly
those eight truncated-Poisson and eight delta-method values.

### 1.4 The asymptotic branch switch

```
lam=      100 exact=1.017913314379e-02  asym3 rel=1.31e-05   asym2 rel=4.06e-04
lam=     1000 exact=1.001754012810e-03  asym3 rel=1.28e-08   asym2 rel=4.01e-06
lam=    10000 exact=1.000175040021e-04  asym3 rel=2.14e-11   asym2 rel=4.00e-08
lam=   100000 exact=1.000017500420e-05  asym3 rel=1.97e-11   asym2 rel=4.20e-10
```

The `asym2` column is the producer's two-term expansion. Its relative errors
4.01e-6 / 4.00e-8 / 4.20e-10 at λ = 1e3 / 1e4 / 1e5 are exactly the cross-check
the producer reports (4.0e-6 / 4.0e-8 / 4.0e-10). Switching at λ = 1e5 costs at
most 4e-10 relative on those terms. **Immaterial. Verified.**

### 1.5 Is the plug-in λ = C_T defensible for the λ ≈ 1–3 rows?

Two checks.

(a) *Bias of the plug-in.* `E_{C~Poi(λ),C≥1}[g(C)]` against `g(λ)` for the exact
term `g`: ratio 0.98 (λ=1), 1.14 (1.5), 1.04 (2), 0.91 (3), 0.96 (5), 1.14 (10),
1.07 (20), 1.02 (50), 1.01 (100). Non-monotone excursions of order ±15 % in the
*variance* of a single row, i.e. ±7 % in that row's rms contribution.

(b) *Direct sensitivity.* I replaced the plug-in by a local log-linear smoother
of `ln C_T` in T (windows ±5, ±10, ±25) and recomputed the whole-band floor:

```
n43 whole: 0.340570 (plug-in) -> 0.340253 / 0.339957 / 0.339070
n50 whole: 0.327569 (plug-in) -> 0.327253 / 0.326923 / 0.326856
```

**The plug-in is defensible: it moves the whole-band floor by at most 0.44 %,
and it moves it DOWN.** This is a load-bearing negative result for ANOM-4: the
report's explanation (i) — "the floor uses the plug-in λ = C_T, itself noisy for
the many λ≈1–3 rows" — accounts for well under 1 %, not the 3 % by which n=50
sits under its floor, and it has the wrong sign. See §1.7.

### 1.6 Is the Poisson dispersion assumption right? (control the producer did not run)

The floor assumes `C_T ~ Poisson(λ_T)` marginally. The 5.6e10 pooled candidate
scores are **not** independent — q^{k_fft} = 1.4e7 of them share one lattice and
one target within each iteration — so I tested for over-dispersion directly on
the archived increments `D_T = C_T − C_{T+1}` (pooled candidates with score
exactly T), with a local degree-3 polynomial fit to `ln D_T` on a window of 81
and an **exact leverage correction** `φ = Σ r² / Σ (1−h_ii)/D_T`:

```
n43 T[150,700)  phi = 0.9166      n50 T[150,700)  phi = 1.2255
n43 T[200,900)  phi = 0.9580      n50 T[200,900)  phi = 1.0001
n43 T[900,1400) phi = 0.9549      n50 T[900,1400) phi = 1.0442
```

φ = 1 is Poisson. So Poisson is the right marginal noise model to within about
±20 % in variance (±10 % in rms) across the well-measured region. This
independently corroborates RT-12's dismissal of over-dispersion and is a
stronger version of it (leverage-corrected). It is **untested where increments
are small, i.e. the deep tail**, which is precisely where the whole-band statistic
gets most of its weight — the same gap RT-12 recorded.

Binomial (finite-M) correction: `Σ (1−p_T)/λ_T` versus `Σ 1/λ_T` agree to six
decimal places on the whole band for both files, because the only rows with
p not ≈ 0 are the ones with λ ~ 1e10 that contribute nothing. **Immaterial.**

### 1.7 The floor's ONE real defect: it is the floor for a model with no fitted parameter

Survival counts are **cumulative**: `C_T = Σ_{t≥T} D_t` with the `D_t`
independent Poisson. Hence for T < T′, `Cov(C_T, C_{T′}) = Var(C_{T′}) = λ_{T′}`,
so with `ε_T = ln(C_T/λ_T) ≈ (C_T−λ_T)/λ_T`

```
    Cov(ε_T, ε_{T'}) = min(1/λ_T, 1/λ_{T'}),
```

i.e. **ε is a Brownian motion in the time change τ_T = 1/λ_T**, not white noise.
The floor as published is `sqrt(mean_T E[ε_T²])`, the expected rms of a model
that is exactly right and carries **no** free parameter. But every rms in this
lane — M1, M1a, M2, M3, M4, and the BATCH-009/010/011 numbers — comes from a
protocol that **profiles one normalisation on the very rows being scored**, and
a profiled additive constant removes a large share of a Brownian residual.

For a pure additive offset the achievable floor is
`(1/n)Σ a_T − (1/n²)Σ_{T,T'} min(a_T,a_{T'})` with `a_T = 1/λ_T` (increasing in
T, so the double sum is `Σ_k a_k (2(n−k)−1)`). Computed on the archived counts:

| file / band | delta floor, no fit | delta floor, one profiled constant | ratio |
|---|---|---|---|
| n43 whole | 0.409366 | 0.377735 | 0.923 |
| n43 count≥10 | 0.154224 | 0.139078 | 0.902 |
| n43 count≥1000 | 0.014620 | 0.013266 | 0.907 |
| n43 count≥1e5 | 0.001072 | 0.001012 | 0.944 |
| n50 whole | 0.334742 | 0.306125 | 0.915 |
| n50 count≥10 | 0.147603 | 0.132956 | 0.901 |
| n50 count≥1000 | 0.015185 | 0.013580 | 0.894 |
| n50 count≥1e5 | 0.001357 | 0.001251 | 0.922 |

I then checked how close the fitted parameter is to a pure offset by measuring
`d ln(Pred_T)/d ln A` at the whole-band M2 optimum:

```
T=   0 200 400 600  800 1000 1200 1400 1600 1800
   0.031 0.097 0.204 0.755 0.997 0.993 0.983 0.963 0.924 0.856
```

It is ≈ 1 for T ≳ 700 — where the counting noise lives and where the whole-band
floor gets its weight — and small at small T where `Q(T)` dominates the
prediction. So on the whole band the pure-offset idealisation is close and the
correction factor is near 0.92; on count≥1000 (T ≤ 851, mean sensitivity 0.42)
the fit absorbs less and the true factor lies between 0.90 and 1.

**Consequence.** The protocol-correct whole-band floors are ≈ 0.314 (n=43) and
≈ 0.300 (n=50), so

* M2 whole band: **1.04× → up to 1.13×** (n=43) and **0.97× → up to 1.06×** (n=50);
* the surrogate's best-over-p: 1.25× → up to 1.36× and 1.30× → up to 1.43×;
* M2 count≥1000: 23.9× → up to 26.3× and 23.4× → up to 26.2×.

**Every model's ratio moves by the same factor, so no comparative statement in
the package changes.** What changes is the absolute reading: "the exact model
sits AT the counting floor" and "n=50 is BELOW its floor" are both artifacts of
scoring a one-parameter-profiled fit against a zero-parameter floor. This is
defect D-1 and it also revises EV-MLKEM-2e668d C-1 and C-2 in the direction that
*strengthens* their conclusions (the surrogate's whole-band excess is larger, not
smaller, than 1.25×/1.30×).

---

## 2. Part A — the exact region measure, re-implemented independently

Script: `indep_model.py` + `run_indep.py` (this session). It does not import or
read `exact_region_measure.py`. Independence points:

* **Υ_n is evaluated by Poisson's integral, not by the alternating series (4.11)
  and not in Decimal arithmetic**:
  `Υ_n(x) = [Γ(n+1)/(Γ(n+½)Γ(½))] ∫_{−1}^{1}(1−t²)^{n−½} cos(xt) dt`,
  by 600–900-node Gauss–Legendre in double precision. This route has **no
  cancellation at all**, so it is an independent check of the producer's claim
  that 120-digit arithmetic was needed and got the right answer.
* the ξ-side measure `∫_{sign·Υ_a ≥ e^{−τ}} ξ^{β_sieve−1} dξ` is precomputed once
  as a 1-D table in τ and interpolated (the producer root-finds inside every
  η node);
* a different panel layout (`[1e-4,1] × 10`, `[1,600] × 90`, `[600,6000] × 120`,
  `[6000,N] × 25`, GL order 8 → 1960 nodes vs the producer's 876), a different
  kernel cut (150 vs 120), a different η-panel count (4 vs 3) and GL order
  (24 vs 16), a different coarse-grid/golden-section schedule.

### 2.1 Source transcription, checked against the archive and the read-only PDF

`page23_approx_4_8_4_9.txt` gives (4.22), (4.23), (4.24) verbatim as reported,
including `λ(x) ∝ x^{β_sieve−1}` and `μ(y) ∝ y^{n_fft−1}` and the fact that every
remaining constant (`δ(β_bkz)`, the q-powers, the Γ factors) is v-independent
and T-independent. The (4.22) prefactor identity
`sqrt(πN)·σ_lsc·sqrt(2π) = π σ_lsc sqrt(2N)` is correct.

PDF page 20 (read-only, hash verified in the same command) gives

```
Φ_{dlsc}(i,j) = Υ_{βsieve/2}((2π/q) dlat i) · Υ_{nfft/2−1}((2π/q) dlsc j)      (4.10)
Υ_n(x) = Γ(n+1) J_n(x)/(x/2)^n = Σ_ℓ (−1)^ℓ (x/2)^{2ℓ} / (ℓ! Π_{s=1..ℓ}(n+s))  (4.11)
```

**Transcription verified exactly.** α appears in none of (4.21)–(4.24) — ANOM-2
confirmed on the archived page-23 extract.

### 2.2 Υ_n cross-check

```
Ups_3 zeros : 6.380161895923983  9.761023129981687
              (j_{3,1}=6.3801618959239835, j_{3,2}=9.7610231299817)
Ups_22   first zero 27.567943891252305   (producer 27.567944)
Ups_20.5 first zero 25.955680785030715   (producer 25.955681)
log2(Ups_3 / exp(-x^2/16)) : x=4 -0.1894  x=5 -0.5813  x=6 -2.0471
                             x=7 Ups_3 = -2.344801e-02 (NEGATIVE)
log2(Ups_22 / exp(-x^2/92)): -0.0009 -0.0023 -0.0047 -0.0151 -0.0806
```

Every number of report.md §3.5 reproduced, by a completely different evaluation
route. RT-9's mechanism is confirmed a second time.

### 2.3 The four models, recomputed

n=43 (my run, producer's value in brackets):

```
CROSSCHECK B009 (p=26.0, log2K=-72.712581): rms 0.705502  [producer 0.705494, BATCH-009 archived 0.705760]
M2 whole          log2A=-172.24683  rms=0.355665  [0.355665]
M2 count_ge_10    log2A=-172.15379  rms=0.279823  [0.279823]
M2 count_ge_1000  log2A=-172.21884  rms=0.349478  [0.349477]
M2 count_ge_1e5   log2A=-174.85244  rms=0.205521  [0.205521]
M4 whole          rms=0.368853  [0.368852]
M4 count_ge_1000  rms=0.436679  [0.436680]
```

n=50:

```
CROSSCHECK B009 (p=24.5, log2K=-67.222505): rms 0.696895  [producer 0.696885, archived 0.696721]
M2 whole          log2A=-155.50680  rms=0.317216  [0.317217]
M2 count_ge_10    log2A=-155.44271  rms=0.276937  [0.276937]
M2 count_ge_1000  log2A=-155.41089  rms=0.355705  [0.355705]
M2 count_ge_1e5   log2A=-155.76024  rms=0.437757  [0.437757]
M4 whole          rms=0.349776  [0.349772]
M4 count_ge_1000  rms=0.435235  [—]
```

**Agreement to 1e-6 bits on every M2 and M4 value and to five decimals on every
log2 A.** Two independent implementations, different Υ route, different
quadrature, same answers. A fourth implementation (BATCH-010's, at the archived
B009 point) is corroborated to 8e-6 bits.

Local log-log slope of G, n=43 (my G, producer in report §3.5):

```
v=3:24.42  5:23.09  6:22.31  7:21.41  8:20.38  9:19.32  10:19.06  11:21.54  12:26.24
```

Identical to the printed digits. The v-dependent slope, and its non-monotone
turn back up at v≈11 as the second (negative × negative) lobe pair activates,
are real.

### 2.4 Parameter count (the "one fewer free parameter" claim)

Read from the code and confirmed by the fits:

* `rho_M2(lnA) = [F(lnA + g) for g in lnG]` — **exactly one free scalar**, a
  normalisation. Everything else (`β_sieve = header beta_1`, `n_fft`, `N`,
  `μ_lsc`, `σ_lsc`, `q`, `k_fft`) is read from the `.out` header; none is fitted.
* `d_lat` provably cancels (reduction R2), so the header/Fig-4.1 discrepancy
  cannot enter — I confirmed this by construction in my own implementation,
  where `d_lat` never appears.
* The exponent is not a parameter at all: M2 is not a power law. Its *effective*
  exponent is whatever (4.10)/(4.11)/(4.24) give — asymptotically
  `(β_sieve+n_fft)/2 = 26.0 / 24.5` as v → 0, because
  `Υ_n(x) ≈ exp(−x²/(4(n+1)))` near 0 makes E(v) an ellipse quadrant and
  `G(v) ∝ v^{β_sieve/2 + n_fft/2}` — and drifting over [17.9, 26.2] at larger v.
  That is a **derived** quantity, not a tuned one. **Claim confirmed.**
* M1 has two (K, p); M1a has one (K) with p frozen at the same 26.0 / 24.5.
  So M2-vs-M1 is genuinely 1-vs-2, and M2-vs-M1a is 1-vs-1.

### 2.5 Is the matched-parameter comparison (Claim 2) fair?

Two attacks, both of which the package survives.

**(a) Was the surrogate's optimum grid-limited?** The producer's exponent grid is
`p_own ± 6` in steps of 0.75, i.e. [20.0, 32.0] for n=43, and the count≥1000 and
count≥1e5 argmins land on its lower edge. I scanned p from **8 to 32** on my own
implementation (n=43):

```
count>=1000  argmin p=20.0 rms=0.241897  (16.54x)
   8:0.6283 ... 18:0.2841 19:0.2479 20:0.2419 21:0.2788 22:0.3528 ... 32:1.5975
count>=1e5   argmin p=15.0 rms=0.071339  (66.55x)
   8:0.1480 ... 13:0.0977 14:0.0797 15:0.0713 16:0.0826 ... 20:0.1899 ... 32:0.2324
whole        argmin p=23.0 rms=0.427124  (1.25x)
```

At **count≥1000** the optimum is genuinely interior at p ≈ 20 (rms 0.2419), so
the surrogate's 16.5× is real and the 16.5× → 13.2× comparison is **fair**. (RT-8's
0.2406 at p=19.5 is consistent with my grid step of 1.0.)

At **count≥1e5** the edge value is badly scan-limited: 0.1899 at p=20 against
0.0713 at p=15, a factor 2.66. So report.md §3.2's sentence *"The rms value at
the edge is not scan-limited, only the argmin location"* is **false**, and the
count≥1e5 row of table 3.4 ("177x → 61.4x") must be struck: the correctly
scanned surrogate reaches ≈ 66.5×, statistically indistinguishable from M3's
61.4×. This is defect D-2.

**(b) Does the second parameter flatter the exact model because M3 = F(A·G^s) is
the executor's own family?** I built a structurally different two-parameter
embedding, `F(A·G(v)·v^c)` (a v-power multiplier rather than a power of G), and
optimised both on my own implementation:

```
whole          F(A G^s)    argmin s=1.00  rms=0.355665  (1.04x)
whole          F(A G v^c)  argmin c=0.0   rms=0.355665  (1.04x)
count_ge_1000  F(A G^s)    argmin s=0.90  rms=0.193582  (13.23x)
count_ge_1000  F(A G v^c)  argmin c=-2.0  rms=0.198553  (13.57x)
```

Two conclusions, both favourable to the package. On the whole band **both**
second parameters select their null value exactly and return M2's own rms:
adding a second degree of freedom of either kind buys nothing, which is the
strongest possible form of the "one fewer parameter" claim. On count≥1000 the
alternative embedding lands at 13.57× against M3's 13.23× — so **13.2× is not an
artifact of the specific family**; a different second parameter reaches
essentially the same place. My finer s-grid (step 0.05, containing s = 1.00)
also confirms ANOM-5's merged reading: the M3 whole-band argmin *is* s = 1.00.

### 2.6 ANOM-8: what is the count≥1000 ratio measuring?

At my own whole-band M2 fit (n=43):

```
rms=0.355665 mean=+0.1061 min=-0.3640 max=+1.3275
T=0:+0.139  270:+0.467  540:+0.264  810:-0.174  1080:-0.190  1350:+0.158  1620:+0.191
rms on count>=1000 rows at the WHOLE-band fit: 0.349849  (at its own fit: 0.349478)
lag-1 autocorrelation of the residual on count>=1000: 0.99907
high-frequency (2nd-difference) noise sd on count>=1000: 0.000739 bits
```

Every number of report ANOM-8 reproduced. **The answer to the Coordinator's open
question is yes, unambiguously.** The residual on count≥1000 has lag-1
autocorrelation 0.99907 and a high-frequency content of 0.00074 bits against a
level of 0.349 bits; it is essentially pure low-frequency systematic shape error.
Refitting on the sub-band changes it by 0.0004 bits (0.349849 → 0.349478), so the
sub-band ratio is not created by the fit either. The 23.9× **is** the S-shaped
residual, and it is 24× the counting floor at level while carrying 20× *less*
high-frequency content than the floor — exactly what a shape error looks like.

One caution I raise against myself: I also fitted plain smooth polynomials in T
to `log2 P̂` directly (degree 12 reaches 0.7× the floor on count≥1000). That is
**not** evidence that 0.0146 bits is achievable by a physical model, because
counting noise here is Brownian (§1.7) and a Brownian path puts ≈ 99.6 % of its
energy in its first 12 Karhunen–Loève modes, so a degree-12 polynomial absorbs
almost all of it. I record the calculation and explicitly decline to use it.

### 2.7 ANOM-1

The fix is correct.

* `build_u_nodes` now `pairs.sort(key=lambda t: t[0])` before returning, and the
  panels are already increasing, so the returned node list is globally ascending
  in u.
* With ascending u, `{j : (T−u_j)²/N < KERNEL_Z_CUT}` = `{j : |T−u_j| < sqrt(120N)}`
  is an interval in u and therefore contiguous in j. The runtime assertion in
  `build_kernel` (`elif j != prev + 1: raise`) fires on exactly the right
  condition and cannot be satisfied vacuously — it is inside the same loop that
  builds the row, for every score in the band.
* My own implementation carries the identical construction and assertion, and it
  never fired, and it reproduces 0.355665. So the post-fix number is right.
* The pre-fix value 0.369045 I did not reproduce and did not need to.

**BATCH-010 is genuinely unaffected.** Verified by reading both of its scripts:

* `exponent_neighbourhood_scan.py::accumulate` loops
  `for i in range(len(band)): ... J[i] += c*math.exp(-z)` — it addresses the
  **full** band for every node and the `z < 700.0` test only skips an addition.
  There is no index bookkeeping and no slice at all.
* `jensen_bias_bound.py::integrate` does
  `for (v,u,base), W in zip(nodes, Wvals)` — a parallel zip, order-independent;
  and `panel_edges` calls `out.sort()` anyway.

Neither script can express the defect. BATCH-010's numbers do not move. I also
corroborate BATCH-010's 0.705494 independently at 0.705502.

### 2.8 Controls, checked

| control | my finding |
|---|---|
| quadrature convergence (2.147e-07 / 2.185e-07 bits) | not reproduced as such, but a stronger statement holds: my different node layout, order and cut agrees with the producer's M2 rms to 1e-6 bits on all eight (file, band) cells |
| region-measure grid truncation | **the stated justification is invalid**: the script's own `envelope_checks` record `upsilon_a_envelope_dominates_last_lobe: false` AND `upsilon_b_envelope_dominates_last_lobe: false` for both files (e.g. n=43: last-lobe max 1.7450e-07 vs envelope 1.3077e-07; n=50: 3.4934e-07 vs 9.0388e-08). report.md §4 states the envelope numbers as bounds and declares the truncation IMMATERIAL without saying the check returned false. **The conclusion is nevertheless correct**: I re-ran G(v) with the grids enlarged from (ξ≤34, η≤120) to (ξ≤45, η≤200) and got zero difference in double precision for v ≤ 14 and 1.09e-04 relative at v = 16, while F saturates to 1−1e−12 at v = 10.72. Defect D-3. |
| integrality of recovered counts | reproduced exactly |
| Υ series vs Bessel zeros | reproduced by an independent evaluation route |
| floor exact vs asymptotic | reproduced (4.01e-6 / 4.00e-8 / 4.20e-10) |
| floor vs red team C1 | agrees, but see D-5 |
| BATCH-009/010 reproduction | reproduced (0.705502 / 0.696895 here) |
| fit-bracket edge guard | present in `fit_one_parameter`, self-widens up to 3 times, records `bracket_widenings`; none triggered |
| ψ_lsc left-tail sensitivity (ANOM-7) | not independently recomputed (`unable_to_check`); the literal reading is the primary result and the count≥1000 verdict is stated to be unchanged under either |
| kernel contiguity assertion | verified correct (§2.7) |
| **Poisson dispersion of the counts** | control the producer did not run; I ran it (§1.6); it passes at φ ≈ 0.92–1.22 in the well-measured region and is untested in the deep tail |
| **null-object / decay control** | **absent from the package and from the whole lane.** No statement is made of what any of these rms quantities *should* do as a parameter meant to destroy the signal increases. See the limitation in the report. |

---

## 3. Provenance and artifact-policy items

`results.json.provenance` carries command, argv, cwd, script sha256, git commit
+ dirty state + dirty paths + branch, environment and dependency availability,
input sha256s, PDF sha256, determinism block, wall clock 803.979 s, user/system
CPU, captured stderr, `inference`, `certificate: {kind: none}` and `validity`.
`stdout_log` carries the transcript. This does close the BATCH-010 DEV-1 gap.

Two blemishes: report.md states peak RSS 0.0685 GB, `results.json` top level says
`peak_rss_gb: 0.06849…` but `provenance.resource_measurements.peak_rss_gb_ru_maxrss`
says `0.07438…` — two values for one quantity (D-4). And
`inference.model_verified: false` with the note that
`python3 -m orchestration.adapter doctor --probe` was not run, so the resolved
model identifier is unverified configuration by AGENTS.md's own standard; the
fallback is recorded honestly with a reason, as CLAUDE.md's model-policy note
requires.

`git_dirty_tree: true` at run time, with the dirty path being only this task's own
untracked directory. The snapshot commit d274699a then froze exactly those bytes,
whose hashes I re-verified. Acceptable.

---

## 4. Scope statements I re-verified and am bound by

* Resolved band only: scores 0..1802 (n=43) and 0..2309 (n=50); the counting
  quantum is 2^-35.70445229 and 2^-36.28941479; printed zeros above the band are
  absence of measurement and nothing was fitted or extrapolated past them.
* Raw undivided score scale; no k_fft alignment applied anywhere in my recomputation.
* RT-11 stands: median F(solution) = 11964.5 against last measured score 1802, so
  the resolved band is ~15 % of the operating threshold and **no region in this
  archive is the security-relevant region**.
* The normalisation is fitted to the data being compared; this is a *shape*
  comparison with one free scale and tests nothing about absolute level.
* Toy tier. Nothing here bears on ML-KEM or Kyber security in either direction,
  nor on Carrier et al.'s cost figures or Table 5.1. AGENTS.md rule 12 unmet and
  unwaived; EV-MLKEM-011, EV-MLKEM-013, EV-MLKEM-017 keep their status.
* `dominated_by`: n/a — no attack is advanced and no cost frontier is occupied.
  `sota_delta`: zero.

## 5. Commands run in this session (all read-only on producer artifacts)

```
git show --stat d274699aade09abc81815627d16afaf06085d91a
python3 -c "<sha256 of the three declared paths and the three inputs>"
python3 <scratch>/floor_indep.py            # independent counting floor
python3 <scratch>/floor_stress.py           # branch switch + plug-in bias
python3 <scratch>/overdisp.py               # Poisson dispersion, uncorrected
python3 <scratch>/overdisp2.py              # Poisson dispersion, leverage-corrected
python3 <scratch>/floor_fitted.py           # floor under a profiled normalisation
python3 <scratch>/shape.py                  # smoothed-lambda floor, polynomial baselines
python3 <scratch>/run_indep.py              # independent M2/M4 fits, n=43
python3 <scratch>/run_indep_n50.py          # independent M2/M4 fits, n=50
python3 <scratch>/run_adv2.py               # wide surrogate scan, alternative embeddings
python3 <scratch>/final_checks.py           # parameter leverage, residual structure, grid enlargement
python3 <scratch>/slope.py                  # local log-log slope of G
python3 .../TASK-20260803-36f572/exact_region_measure.py --mode floor   # writes nothing
python3 - <<'EOF'  # pypdf read-only extraction of PDF page 20 to stdout, hash re-verified
```

`<scratch>` is this session's scratchpad. No producer artifact was written.
