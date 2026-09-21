# Validation notes — exactly what I recomputed

**Task** TASK-20260802-08f428 · **Validator** · **Batch** BATCH-009 · **Goal**
GOAL-MLKEM-003 · **Package under review** snapshot commit `d0f2bf7f1770`
(parent `b7025f054111`, 5 paths) · **Produced by** TASK-20260802-8bae8e

I did not produce the package. Nothing here repairs it. Every number below was
computed in this session from repository bytes by code I wrote; where my digits
differ from the producer's I give both.

Requested policy `review-adversarial`, `xhigh`, independent session; resolved
model `claude-opus-5`; `fallback_used: true` (per CLAUDE.md's model-policy note,
the GPT-5.6-family alias cannot be resolved under this harness).

---

## 0. Archival binding — verified directly against Git, not asserted

```
git merge-base --is-ancestor d0f2bf7f1770 HEAD      -> reachable
git rev-parse d0f2bf7f1770^   -> b7025f054111539afc830622204f387642782592
git diff-tree --name-only -r d0f2bf7f1770 -> exactly 5 paths
git status --porcelain        -> clean tree
```

SHA-256 of each committed producer object vs the `source_path_sha256` declared
in `archives/TASK-20260802-7c4aee/snapshot_receipt.json` — all four match, and
worktree == committed blob for all four:

| artifact | sha256 (first 16) |
|---|---|
| `approx49_comparison.py` | `74f34f8cb86d2af1` |
| `comparison_results.json` | `ca377c062c58cdfc` |
| `comparison_report.md` | `7ed2d0cb81c4d688` |
| `receipt.json` | `a39f692d3bf017eb` |

Input data SHA-256, recomputed and matched against the archived upstream
manifest `inputs/MLKEM-DUAL-SOURCES-20260802/extracts/codeddualattack/file_sha256_manifest.txt`:

* n=43 Pwrong `50bd293cadf952516b092524c25f4404a1e4ca40983d1751286f96269dbf90bb`
* n=50 Pwrong `ce23181dca95a1c6a72463c2c39f14f645500a068b3af46c71d5b45af69ab459`

Defect: the archive receipt itself is still unbound (`commit_sha: null`,
`parent_sha: null`, `verification.status: pending_post_commit`), and commit
`598753f8`, whose message claims to record the SHA and per-path digests, changes
only `dispatch_plan.json`, `dispatch_plan.md` and `dispatch_queue.json` (task
states). The string `d0f2bf7f` appears in no committed coordination record. I
therefore performed the binding check myself, as above.

---

## 1. Resolved band and counting floor — recomputed from the raw bytes

Parsed both `.out` files myself (header + one float per line), took
`denom = nb_iteration * q**k_fft` from the file's own header:

| | n=43 | n=50 |
|---|---|---|
| lines | 1804 | 2311 |
| `nb_iteration` (header) | 4000 | 6000 |
| `q**k_fft` | 13 997 521 | 13 997 521 |
| `nb_iteration*q**k_fft` | 55 990 084 000 | 83 985 126 000 |
| floor `1/denom` | `1.7860305406935986e-11` | `1.1906870271290657e-11` |
| log2 floor | **−35.70445229** | **−36.28941479** |
| last positive index | **1802** | **2309** |
| first zero index | 1803 | 2310 |
| `values[last] == 1/denom` bit-for-bit | **True** | **True** |
| all values ≥ index after first zero are 0 | True | True |
| monotone non-increasing over the band | yes (0 violations) | yes (0 violations) |
| log2 v[0] | −1.002880 | −1.005054 |
| dynamic range | 34.7016 bits | 35.2844 bits |
| last score with pooled count ≥ 10 | **1492** (count 10) | **1968** (count 10) |

**Both floors equal `1/(nb_iteration · q^k_fft)` exactly, as IEEE-754
equality.** Bands `[0,1802]` and `[0,2309]` reproduced.

Integer-multiple check: max relative deviation of `v·denom` from its nearest
integer, using `|c−round(c)|/round(c)` over the band and skipping zeros, is
**1.36e-16** (n=43) and **1.815e-16** (n=50). The producer reports 2.165e-16 and
1.815e-16; its script uses `|c−round(c)|/max(1,round(c))` over *all* lines. The
n=43 digit differs by convention only; the identity holds at the 1e-16 level
either way.

### nb_iteration: header 6000 vs Fig 4.1 caption 4000 (n=50)

The computation used the **header** value. That choice is not merely defensible
on provenance — it is forced by the data: with `nb_iteration=6000` the last
positive value of the n=50 file equals `1/(6000·241³) = 1.1906870271290657e-11`
bit-for-bit, whereas `1/(4000·241³) = 1.7860305406935986e-11`, a different
double. The caption's "4000 iterations for both panels"
(`extracts/carrier-hal-05406481/page26_fig41.txt`, line 43) is refuted for the
right-hand panel by the file's own quantisation. The producer's §2 justifies the
choice on provenance ("the file's own record of how it was produced") while
already holding the decisive argument in its §1.

`d_lat`: header 41.068986 / 57.889159 vs caption 42.00 / 58.60. I confirmed by
reading the script that `avg_dlat` is parsed and recorded but enters no
computation, so the disagreement does not propagate. Recorded, not resolved — as
the producer says.

---

## 2. Score scale — is any k_fft alignment applied? (explicitly answered: no)

Two independent routes, both mine:

**(a) Moment identity from the survival column.** `E[F²|F≥0] = Σ_t w(t)·S(t)/S(0)`.
With the right-endpoint convention `w(t)=2t+1` I get σ = **114.702** (n=43) and
**114.974** (n=50); with `w(t)=2t` I get 114.302 / 114.575. The producer's
estimators use `w(t)=2t−1` (exact only if F is integer-valued) and give
113.905 / 113.791 and 114.178 / 113.978. Against Model 4.7's raw prediction
`sqrt(avg_N/2)` = 113.9539 / 113.9517 the ratio is **≈1.00** on every
convention; against a `/k_fft` scale it is **≈3.0** on every convention. The
raw, undivided scale is the only one consistent with the data.

**(b) Source-code definition — a route the producer did not use.**
`experiments/EXP-MLKEM-013/vendor-lock/FFT_sample.py` (SHA-256
`2a5f3dedceb68b0836efc92f0b58294ce4193a9553493e7c0d4e4ce67b922531`, matching the
upstream manifest for `verifyModel/ScoreExperimentalDistribution/FFT_sample.py`)
defines

```python
class Score_Function:
    def compute_score(self, error, z):
        self.F = 0
        for (decoded, dual_vector) in self.decoded_dual_vectors:
            self.F += math.cos((2*math.pi/self.q)*(dot_product(dual_vector,error,self.q)
                                                   - dot_product(decoded,z,self.q)))
        return self.F
```

i.e. an **unnormalised** sum of N cosines, whose wrong-guess second moment is
N/2. That is the raw scale, matching (a) directly.

**Conclusion: no k_fft alignment is applied anywhere in the package, and none is
warranted.** The prohibited failure mode did not occur.

---

## 3. Approximation 4.9 — re-derived independently from the archived extracts

From `extracts/carrier-hal-05406481/page23_approx_4_8_4_9.txt` (4.22)–(4.24) and
`page25_pwrong_validation.txt`, working from the text and not from the
producer's code:

The prefactor of (4.22), `exp(−t²/N − (dlsc−µlsc)²/(2σ²lsc)) / (π σ_lsc √(2N))`,
is exactly the product of the N(0,N/2) density in `t`
(`exp(−t²/N)/√(πN)`) and the N(µlsc,σ²lsc) density in `dlsc` — I checked the
normalisation: `1/√(πN) · 1/(σ_lsc√(2π)) = 1/(π σ_lsc √(2N))`. So (4.22) is the
convolution Model 4.7 asserts.

With `λ(x) ∝ x^{βsieve−1}`, `µ(y) ∝ y^{nfft−1}` from (4.24) and the declared
reading `Φ_dlsc(x,y) = exp(−(a x² + b y²))`, `E(u) = {a x²+b y² ≤ ln(N/u)}` and

  `∫_{E(u)} λµ = K · ln(N/u)^p`, `p = (βsieve+nfft)/2` — 26.0 and 24.5,

so `Pwrong(T;K) = Q(T) + ∫_0^N φ(T−u)·min(1, K ln(N/u)^p) du`,
`Q(T) = 0.5 erfc(T/√N)`. I confirmed the exponent arithmetic: 44+8=52→26.0;
41+8=49→24.5.

**My implementation differs from the producer's.** I put the `min(1,·)` kink at
its exact location `u* = N exp(−K^{−1/p})` and integrate the two pieces
separately, so

  `Pwrong(T;K) = 0.5 erfc((T−u*)/√N) + K·I(T,u*)`,
  `I(T,u*) = (1/√(2π)) ∫ e^{−s²/2} ln(N/(T−σs))^p ds`, `σ = √(N/2)`,

evaluated by composite Gauss–Legendre in the Gaussian variable `s` with panels
graded toward `s_hi`. The producer instead grids in `v = ln(N/u)` with 4370
nodes. `numpy`/`scipy` are absent here too; Legendre and Hermite nodes were
generated by Newton iteration from the recurrences.

**Self-checks on my quadrature** (all run this session):

* `p = 0` collapses the integrand to a closed form
  `0.5(erfc((T−u*)/√N) − erfc((T−N)/√N))`: **max relative error 0 (exact)** over
  T ∈ {0,100,471,900,1500,1802} × u* ∈ {1, 28.9, 500}.
* coarse (24 panels/16 nodes) vs fine (64 panels/28 nodes, wider span):
  **max relative difference 2.25e-15** over T ∈ {0,213,471,755,900,1200,1492,1802}.
* `K → ∞` limit reproduces `0.5 erfc((T−N)/√N)` exactly.

---

## 4. Recomputed statistics — my fit and at the producer's exact K

Fitting `log2 K` myself by golden section on the sum of squared log2 residuals:

| | mine (whole band) | mine (band[::20], the producer's fit grid) | producer |
|---|---|---|---|
| n=43 log2 K_fit | −72.71162 | −72.70631 | **−72.712581** |
| n=50 log2 K_fit | −67.21992 | −67.223472 | **−67.222505** |

All three agree within 0.007 bits; the spread is quadrature/optimiser tolerance.

**Evaluated at the producer's exact K**, my independent model gives:

| statistic | n=43 mine | n=43 report | n=50 mine | n=50 report |
|---|---|---|---|---|
| max Δ (bits) / at score | **+1.5154 / 471** | +1.516 / 471 | **+1.7109 / 420** | +1.710 / 420 |
| min Δ (bits) / at score | **−0.9325 / 1616** | −0.933 / 1616 | **−0.9170 / 2283** | −0.917 / 2283 |
| mean Δ | **+0.2449** | +0.245 | **+0.1920** | +0.192 |
| rms Δ (whole band) | **0.7055** | 0.706 | **0.6969** | 0.697 |
| first sign change | **888** | 888 | **1090** | 1090 |
| number of sign changes | **12** | 12 | **14** | 14 |

At my own K the corresponding numbers are −0.9316/+1.5158, rms 0.7055 (n=43) and
−0.9144/+1.7120, rms 0.6969 (n=50) — i.e. the residual statistics are stable to
~0.003 bits under a 0.001–0.003-bit change of K.

Sub-band (clip contribution < 1e-3 ∧ pooled count ≥ 10), at my K:

| | mine | report |
|---|---|---|
| n=43 range / n | 756–1492 / 737 | 755–1492 / 738 |
| n=43 min, max, mean, rms | −0.6740, +0.1807, −0.2013, **0.2823** | −0.675, +0.182, −0.202, **0.283** |
| n=50 range / n | 727–1968 / 1242 | 727–1968 / 1242 |
| n=50 min, max, mean, rms | −0.6378, +0.2471, −0.1605, **0.2722** | −0.640, +0.244, −0.163, **0.274** |

(The one-score boundary difference at 755 is my clip-fraction definition,
`clip/pred`, against the producer's; it moves nothing.)

Anchors and elasticity, mine vs report:

| | mine | report |
|---|---|---|
| n=43 score first below 2^−5 | 213 | 213 |
| n=43 log2 K anchored low / high | −89.97846 / −72.14762 | −89.979061 / −72.147621 |
| n=43 elasticity at score 213 | **0.1545** | 0.15 |
| n=43 anchor-low worst undershoot / mean | **−18.198 / −10.697** | −18.20 / −10.70 |
| n=43 anchor-high worst overshoot | **+1.752** | +1.75 |
| n=50 score first below 2^−5 | 214 | 214 |
| n=50 log2 K anchored low / high | −82.95608 / −66.70475 | −82.956451 / −66.704753 |
| n=50 anchor-low worst / mean | **−16.651 / −11.476** | −16.65 / −11.48 |
| n=50 anchor-high worst overshoot | **+1.945** | +1.95 |

Parameter-free component `Q(T)`, mine vs report — exact agreement:

| | n=43 | n=50 |
|---|---|---|
| within 0.1 / 0.5 / 1 bit up to score | **322 / 469 / 525** | **273 / 401 / 460** |
| deficit at score 1000 | **32.400** bits | **35.156** bits |
| deficit at the counting floor | **149.993** bits | **265.557** bits |

The 0.52-bit difference from EV-MLKEM-018's 150.51 is reproduced and explained:
with σ = 113.79144 (that record's measured estimator) `z = 1802/σ = 15.8360`,
`log2 Q = −186.2151`, deficit **150.5106**; with σ = √(avg_N/2) = 113.95394,
`z = 15.8134`, `log2 Q = −185.6975`, deficit **149.9930**. Difference 0.5176.
The producer's explanation is exactly right.

Structural sub-floor dip (no K ≥ 0 reproduces the measurement):

| | mine | report |
|---|---|---|
| n=43 contiguous scores below Q | 0–**126** (127 scores, none elsewhere) | 0–126 |
| n=43 max shortfall | **0.0036883** bits | 0.0037 |
| n=50 contiguous scores below Q | 0–**133** (134 scores, none elsewhere) | 0–133 |
| n=50 max shortfall | **0.0069336** bits | 0.0069 |

Pgood file, recomputed: n = 4000, min 6667.673616, max 17822.813537,
`sorted(v)[2000]` = **11964.802334** (the producer's figure),
`0.5(v[1999]+v[2000])` = **11964.473718** (EV-MLKEM-018's figure),
`v[1999]` = 11964.145101. Both reproduce. Note that `v[2000]` is the **upper**
of the two central order statistics; the report calls it the lower.

---

## 5. Nothing compared, fitted, or extrapolated past the counting floor

* `per_score` in `comparison_results.json` has exactly 1803 and 2310 rows, with
  score range `[0,1802]` and `[0,2309]`; no row has `measured <= 0`.
* the fit grid is `band[::20]` and the exponent-scan grid `band[::40]`, both
  slices of the band; no point exceeds the last positive score.
* the K-solved profile is restricted to elasticity > 0.9 ∧ count ≥ 10.
* the `instrument.note` in both file records states the rule and I confirmed the
  code obeys it.

**The prohibited past-the-floor failure mode did not occur.**

---

## 6. Controls — the producer's, reproduced; then sharper ones I designed

### 6.1 Reproduction of the producer's exponent scan

Same scan grid (`band[::40]`), same one-parameter fit, my own model. rms in bits:

| p | 10 | 14 | 18 | 20 | 22 | 24 | 24.5 | 26 | 28 | 32 | 40 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| n=43 mine | **1.9602** | 1.5074 | **1.0102** | **0.7426** | **0.5045** | **0.4540** | 0.4917 | **0.6921** | **1.0609** | 1.9049 | **3.6319** |
| n=43 report | 1.96 | — | 1.01 | 0.743 | 0.504 | 0.454 | — | 0.692 | 1.061 | — | 3.63 |
| n=50 mine | **2.3478** | 1.7259 | **1.0368** | **0.6784** | **0.4379** | **0.6018** | **0.6938** | 1.0160 | 1.4921 | 2.4801 | **4.3829** |
| n=50 report | 2.35 | — | 1.04 | 0.678 | 0.438 | 0.602 | 0.694 | — | — | — | 4.38 |

Every reported scan value reproduces to the quoted precision.

### 6.2 Continuous optimum and the between-file contrast (my control)

Golden section on p with K refit at each p:

* n=43: `p* = 23.35`, rms 0.4357 — against the archived `p = 26`, rms 0.6921.
* n=50: `p* = 22.27`, rms 0.4329 — against the archived `p = 24.5`, rms 0.6938.

Under the generalised reading `Φ = exp(−(a x^r + b y^r))`, `p = (βsieve+nfft)/r`,
so `r = 52/23.35 = 2.227` (n=43) and `r = 49/22.27 = 2.200` (n=50) against
`r = 2` for the declared reading. The producer's §4.4 says 2.17 / 2.23 from its
grid; on the continuous optimum the two files land closer together, which
strengthens rather than weakens its qualitative point.

**The between-file exponent contrast is the sharpest test available**, because a
per-file free `K` cannot absorb it. Archived prediction:
`Δp = 26 − 24.5 = 1.5`. Measured: `Δp* = 23.35 − 22.27 = 1.08`. Same sign, right
order of magnitude. Given that rms degrades only from 0.436 to ~0.50 within ±1
of the optimum, `Δp*` is determined to no better than about ±1.4, so this is a
pass but not a discriminating one.

### 6.3 Matched-degrees-of-freedom nearby-object control (my control)

A second natural reading of the unavailable Φ — heavy-tailed rather than
Gaussian, `Φ_dlsc(x,y) = (1 + a x² + b y²)^{−1}`, giving
`∫_{E(u)} λµ = K (N/u − 1)^p` with the **same** archived p and the **same**
single free K:

* n=43 rms **11.197 bits** (vs 0.692 for the declared exponential reading)
* n=50 rms **10.977 bits** (vs 0.694)

So the log-power shape is doing real work; the fit is not indifferent to the
reading of Φ. This is a stronger control than p=10 / p=40 because it changes the
functional form while holding the exponent and the parameter count fixed.

### 6.4 Null-object deformation control (my control, per inventor-protocol §3)

Fit the archived-p model, one free K, to the measurement **horizontally
stretched** by a factor c — a deformation that one free multiplicative constant
must not be able to absorb. rms in bits on the fit grid:

| c | 0.85 | 0.90 | 0.95 | **1.00** | 1.05 | 1.10 | 1.15 |
|---|---|---|---|---|---|---|---|
| n=43 | 0.4467 | **0.3492** | 0.4548 | **0.6959** | 1.0141 | 1.3502 | 1.6983 |
| n=50 | **0.4200** | 0.4497 | 0.5434 | **0.6944** | 0.8808 | 1.0879 | 1.3112 |

The fit quality **does** decay as the deformation grows in the stretch
direction, but it does **not** peak at the true measurement: a 10–15 % *compressed*
version of the archived data fits the archived-exponent model roughly twice as
well as the archived data itself. This is the same statement as §6.2 seen
differently (compressing the curve mimics lowering p), and it is the honest
measure of how much the "tracks with one free normalisation" claim is worth.

### 6.5 The dlsc integral belongs inside the min(1,·) — a defect test

Archived (4.22) integrates over `dlsc` **inside** `min(1, ∫_{E(T−t)} λµ)`, and
`E` depends on `dlsc` through `Φ_dlsc`. The producer collapses that integral into
a single constant K, i.e. it computes `min(1, E[K] L^p)` where (4.22) specifies
`E[min(1, K(dlsc) L^p)]`. Because `min(1,·)` is concave, the collapse is an
**upper bound**, exact only where the clip does not bind — and the report's
headline divergence peak sits exactly where its own clipped fraction is
0.36–0.38.

Under the same declared factorisation, with the lsc factor carrying the decoding
distance, `K(dlsc) = K₀·(d_lsc/µ_lsc)^{−n_fft}`; `µ_lsc`, `σ_lsc` and `n_fft` are
all archived (`avg_dlsc`, `sdv_dlsc`, `n_fft`), so this needs no extra
unarchived parameter. Implementing it with a 15-node Gauss–Hermite outer
quadrature (checked: Σw = 1.000000000000000, Σw z² = 1.000000000000001), one
free `K₀`:

| | producer's collapsed model | dlsc-integrated (4.22) |
|---|---|---|
| n=43 whole-band rms | 0.7055 | **0.6166** |
| n=43 max Δ / at score | +1.5154 / 471 | **+1.3092 / 471** |
| n=43 first sign change | 888 | **919** |
| n=50 whole-band rms | 0.6969 | **0.6218** |
| n=50 max Δ / at score | +1.7109 / 420 | **+1.5036 / 422** |
| n=50 first sign change | 1090 | **1180** |

So the collapse inflates the reported peak by ~0.21 bits and moves the crossover
by 30–90 scores, in the direction concavity predicts. The structural point — the
`dlsc` integral is inside the min — is forced by the archived text. My 0.21-bit
quantification additionally assumes the lsc factor is the one carrying `d_lsc`,
which is a plausible but not forced reading; it is illustrative of size, not
definitive.

---

## 7. The four "unavailable" parameters — searched, not assumed

Repository-wide search (`inputs/`, `knowledge/`, `ledger/`, `coordination/`,
`experiments/`, excluding `.git`):

* **`Φ_dlsc(x,y)`** — confirmed absent. The only matches are the producer's own
  four files. The vendor-locked code computes scores, not the model. **The
  producer's claim stands.**
* **`n_lsc`** — confirmed absent except as a token in
  `inputs/.../source_reads.json`. **Stands.**
* **`δ(β_bkz)`** — **does not stand.**
  `experiments/EXP-MLKEM-013/vendor-lock/utilitary.py`, SHA-256
  `87b8cc77e67a52599d87061d580afa7bfa1811cfbce9bdc71a55c9686d186af2`, matching
  the upstream manifest entry for
  `verifyModel/ScoreExperimentalDistribution/utilitary.py` — the same
  hash-verified source tree that produced the Pwrong data — contains

  ```python
  def root_hermite_factor(beta):
      return ((beta/(2*math.pi*math.e))*((math.pi*beta)**(1/beta)))**(1/(2*(beta-1)))
  ```

  which is δ(β). Evaluated: **δ(32) = 1.012528410**, **δ(35) = 1.012604644**,
  so `δ^1364 = 2^24.501` and `δ^1681 = 2^30.377`. The same file supplies
  `volume_lattice(q,m,n) = q**n` and `expected_length_short_vector`, and the
  archived (4.24) already carries Lemma 2.9's result explicitly in the
  `δ^{βsieve(m+nlat−βsieve)}` factor, so Lemma 2.9 is not separately needed.
  (The producer's sensitivity arithmetic is right: a 0.1 % change in δ moves the
  prediction by `1364·log2(1.001) = 1.967` and `1681·log2(1.001) = 2.424` bits.)
* **`α`** — not in any archived page extract; the producer's classification is
  literally correct. But the same repository already narrows it:
  EV-MLKEM-018 (which this report cites four times for other purposes) records
  that (4.19) at the caption parameters reproduces the raw Pgood median at
  `α = 2.0125`, with `α = 2` giving 12021.89 against the measured 11964.47
  (0.48 %) — scanned, not read, and explicitly non-load-bearing there, but not
  nothing.

**On `alpha_secret=2 / alpha_error=2`.** I confirmed by reading the script that
these are parsed into `header_alpha_secret` / `header_alpha_error`, printed to
the log, and stored in the JSON — and are used in **no** computation anywhere.
Every other occurrence of `alpha` in the script is prose. **Item 7 verified: the
candidate was recorded, never assumed.** But the archive says more than the
producer records: the same vendor-locked `utilitary.py` shows
`create_sample(A, alpha_secret, alpha_error, q)` builds
`Centered_Binomial(alpha_secret)` and `Centered_Binomial(alpha_error)`, so those
header fields are the centred-binomial parameters of the secret and error
distributions, not the α of (4.19). They are identified, not merely unverified.

**Consequence for "the absolute level is untestable".** The conclusion is
directionally right but the stated reason is misattributed: δ is available, and
Lemma 2.9 is already substituted into archived (4.24). What actually blocks the
absolute level is α together with Φ's exact functional form. That distinction
matters because it forecloses a test that *is* available: the **ratio**
`K_43/K_50` depends on α only as `α^{−1.5}` (the exponents differ by 1.5), so
with δ in hand the ratio is a near-α-free check on the absolute-level machinery.
I did not run it — it needs further declared readings of how `d_lat`/`d_lsc`
enter Φ's quadratic form, and I would be adding my own assumptions to a package
I am validating — but I record that "no substitute bound would be meaningful"
is too strong.

---

## 8. The producer's two self-reported items

**The double execution.** `receipt.json` discloses execution 1 (49.6 s,
superseded), its defect (a linearised `Pwrong = Q + K·J` diagnostic invalid
where the `min(1,·)` clip binds), the two numbers that changed (shape drift
15.3854/13.0930 → 1.1504/1.2377; linear-form best p 21.0/20.5 → exact 24.0/22.0),
and the fact that execution 1's JSON was overwritten at the same path. Because
that artifact no longer exists, **I cannot verify the bit-identity claim
directly** — that is `unable_to_check`. I can say something stronger about the
substance: I independently recomputed every number the receipt lists as
"identical across both executions" — floor, band, exact-equality and
integer-multiple checks, the scale check, `log2 K_fit`, both anchors and their
anchor scores, and every Δ statistic — and all of them reproduce. The disclosure
is also the right shape: the defect is named, the superseded numbers are quoted
so an auditor can see what moved, and the direction of the change (drift
15.39→1.15 bits) is *unfavourable-to-favourable*, which is exactly the case where
disclosure matters; nothing in my recomputation contradicts it.

Two executions against `maximum_runs: 1` is nevertheless an overrun. The receipt
records `script_executions_performed: 2` and `budget_exceeded: false`. Those two
fields contradict each other.

**The 1394 erratum.** Verified. `approx49_comparison.py` line 1002, inside the
`PARAM_LEDGER` data structure, reads
`"of order delta^{1364} (n=43) / delta^{1394} (n=50); "`. The string
`delta^{1394}` occurs exactly once in `comparison_results.json` and
`delta^{1681}` zero times. The correct exponent is
`βsieve·(m+nlat−βsieve) = 41·(40+42−41) = 1681`; for n=43,
`44·(40+35−44) = 1364` is right. The string sits in a `what_this_blocks`
description field; `delta` is unavailable to the computation and absorbed into
the free scale, and I confirmed no code path reads that field. **No computed
value is affected.** The report's §6 correction is accurate.

---

## 9. Two further arithmetic checks the report does not survive cleanly

**The drift sentence.** Report §4.3(1): "the scale that reproduces the
measurement score-by-score drifts by only **1.150 bits** (n=43, over scores
643–1492, range −73.298 … −72.038)". I bisected K at every score in [643,1492]
myself and obtain min **−73.298**, max **−72.038**, non-monotone — the range
endpoints reproduce exactly, but their spread is **1.260 bits**, not 1.150. The
JSON is correct and carries both statistics separately:
`drift_bits_low_to_high = 1.1504` (first score to *last score*, −73.29806 →
−72.14762) and `min`/`max` = −73.29806 / −72.03763. The report's sentence pairs
the endpoint drift with the min–max range and so understates the spread. Same
for n=50: my window [600,1968] gives min −67.943, max −66.582, spread **1.361
bits** against the report's 1.238 with range "−67.942 … −66.582"; the JSON
carries `drift_bits_low_to_high = 1.2377` and `min/max` −67.94249/−66.58214.

**The sub-floor-dip explanation.** §4.3(4) says the dip is "consistent with the
measured score standard deviation being 0.04 %–0.14 % away from `sqrt(avg_N/2)`".
That range comes from estimators that treat F as integer-valued. The
right-endpoint convention gives +0.66 % / +0.90 %. The discretisation convention
alone moves σ by ~0.7 %, five times the quoted spread, so the quoted precision is
not supported by the data. (The k_fft conclusion — ratio ≈1 versus ≈3 — is
robust to the convention and is unaffected.)

---

## 10. Timestamps

`approx49_comparison.py` writes `generated_at_utc` from `time.gmtime(t_start)`,
i.e. the **start** of the run. The committed `comparison_results.json` carries
`generated_at_utc = 2026-08-02T23:31:21Z` and `wall_clock_seconds = 242.965`, so
the final execution ran 23:31:21–23:35:24Z. But `receipt.json` records
`final_script_execution_started_utc = 2026-08-02T23:47:36Z` (16 minutes later)
and `task_completed_utc = 2026-08-02T23:58:00Z` — nine minutes **after** the
snapshot commit `d0f2bf7f` (author date 23:49:11Z) that contains the receipt.
The receipt's own note designates `generated_at_utc` authoritative, so this is a
self-inconsistent bookkeeping field rather than a fabricated measurement; the two
wall-clock figures (243.078 s wrapper-measured, 242.965 s in-script) are mutually
consistent and no computed number depends on the timestamps.

---

## 11. What I could not check

1. Bit-identity of execution 1's retained outputs — the artifact was
   overwritten. Substituted by independent recomputation of every retained
   number (§4).
2. Whether the declared reading of `Φ_dlsc` is the paper's — the page defining
   Approximation 4.6 is not in the archive. Confirmed absent, not assumed.
3. The absolute level of Approximation 4.9 — still blocked by `α` and Φ's exact
   form, though not by `δ` (§7).
4. The third Pwrong file (`…beta037_beta144_N200001.out`) — not in the
   repository; header and SHA-256 only. Archival defect A3 of EV-MLKEM-018,
   still open.
5. The effective sample size of the pooled counting estimator — the `q^k_fft`
   candidates inside one FFT share dual vectors and target, so counts of 1–10
   support only indicative Poisson reasoning. The producer records this.
6. Whether verifyModel's conventions produced the paper's Table 5.1 / C.2 — no
   retrieved artifact connects them.
7. `python3 -m orchestration.adapter doctor --probe` — no backend is reachable
   here, so `model_verified` remains false for this report as for the producer's.

---

## 12. Non-claims of this validation

Toy parameters only (q=241, m=40, n=43/50, n_fft=8, k_fft=3). Nothing here is an
ML-KEM or Kyber security claim, a crypto-scale statement, or a cost-model
revision (AGENTS.md rule 7). Nothing here changes any record's status. AGENTS.md
rule 12 is unmet and unwaived: EV-MLKEM-011, EV-MLKEM-013, EV-MLKEM-017,
KN-FIND-012 and KN-FIND-014 are **not** treated as corrected by anything above,
and my §7 finding about `δ` and `α` is an observation about parameter
availability, not a correction to any of them. An admissible receipt is not a
verdict on Approximation 4.9; that judgement belongs to the Reviewer and the
Coordinator.
