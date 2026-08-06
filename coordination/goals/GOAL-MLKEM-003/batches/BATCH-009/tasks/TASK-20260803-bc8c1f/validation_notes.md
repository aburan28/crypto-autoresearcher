# Validation notes — TASK-20260803-bc8c1f

**Validator** · **Batch** BATCH-009 · **Goal** GOAL-MLKEM-003 · **Package under
review** Coordinator snapshot commit `d0f2bf7f1770f26833be4e888b0faee0cb67e4a8`
(TASK-20260802-7c4aee), producing task TASK-20260802-8bae8e.

This is the scoped repair of TASK-20260802-08f428, which terminated on a provider
session limit. **That failure was infrastructure and is not evidence about the F1
comparison in either direction (AGENTS.md rule 5).** I read the partial
`validation_notes.md` it left, which carries no verdict field, *after* reaching
my own numbers; nothing below rests on it. Where my work overlaps it I say so
explicitly at the end (§11).

I did not produce the package and repaired nothing in it. Every number below was
computed in this session from repository bytes by code I wrote, in
`<scratchpad>/val/` outside the repository.

Requested policy `review-adversarial`, `xhigh`, independent session; resolved
model `claude-opus-5`, `fallback_used: true` (CLAUDE.md model-policy note: the
GPT-5.6-family alias cannot be resolved under this harness). `model_verified:
false` — no backend is reachable, so `python3 -m orchestration.adapter doctor
--probe` was **not run** and is not asserted.

---

## 0. Artifact binding — verified against Git, then against bytes

```
git log -1 --format='%H %s' d0f2bf7f1770f26833be4e888b0faee0cb67e4a8
  -> d0f2bf7f...  coordination: TASK-20260802-7c4aee snapshot of the BATCH-009 F1 comparison
git merge-base --is-ancestor d0f2bf7f1770... HEAD          -> reachable (YES)
git show --stat d0f2bf7f1770...                            -> exactly 5 paths
git status --porcelain coordination/.../BATCH-009/ experiments/EXP-MLKEM-011/ \
                        inputs/MLKEM-DUAL-SOURCES-20260802/   -> clean
```

For each of the four producer artifacts I compared the working-tree SHA-256, the
committed blob SHA-256 (`git cat-file blob <sha>:<path> | sha256sum`), and the
`source_path_sha256` declared in
`archives/TASK-20260802-7c4aee/snapshot_receipt.json`. **All three agree for all
four paths**:

| artifact | sha256 |
|---|---|
| `approx49_comparison.py` | `74f34f8cb86d2af1a28af3692163bb9ad7c927751ba4fac0f3a99e4c67620285` |
| `comparison_results.json` | `ca377c062c58cdfccb7ae55c06f4533d6e2b50b25f0e54685d2f9b16184bbd5a` |
| `comparison_report.md` | `7ed2d0cb81c4d688f34244eb67b2bc3550e91f259597697930550e38c12d7478` |
| `receipt.json` | `a39f692d3bf017eb527828d7883338aee219835ae233692c608192dfce1dc0f7` |

Input bytes, recomputed with `sha256sum` and matched against the archived
upstream manifest
`inputs/MLKEM-DUAL-SOURCES-20260802/extracts/codeddualattack/file_sha256_manifest.txt`:

* `Pwrong_…n43…N25971.out` `50bd293cadf952516b092524c25f4404a1e4ca40983d1751286f96269dbf90bb`
* `Pwrong_…n50…N25970.out` `ce23181dca95a1c6a72463c2c39f14f645500a068b3af46c71d5b45af69ab459`
* `Pgood_…n43…N25971.out` `f1e9cf478928e51fa772549ceb01359d98be0d90af25b784d5966bc1652dc5e1`

Observation for the Coordinator's archive task, not a defect against the
producer: `snapshot_receipt.json` carries `commit_sha: null`, `parent_sha: null`
and `verification.status: pending_post_commit`. The receipt was committed inside
the very commit it describes, so it cannot carry its own SHA. Per CLAUDE.md
("Archive receipts bind to CONTENT first") the archive **content-verifies**, and
the commit is reachable from `HEAD`; the commit binding is simply unrecorded.

### 0a. Byte-level reproduction of the committed results

I copied the committed script (SHA-256 re-checked: `74f34f8c…`) into a sandboxed
directory tree that mirrors the repository-relative layout the script expects,
with `experiments/EXP-MLKEM-011/vendor-lock/data` and `inputs` symlinked to the
real repository, and ran it there so that **no producer artifact was touched**:

```
python3 <scratch>/mnt/coordination/goals/GOAL-MLKEM-003/batches/BATCH-009/\
        tasks/TASK-20260802-8bae8e/approx49_comparison.py
```

A recursive JSON diff of the re-executed output against the committed
`comparison_results.json` gives **exactly 6 differing leaves**, all timing:

```
/generated_at_utc      '2026-08-03T01:49:54Z'  vs  '2026-08-02T23:31:21Z'
/wall_clock_seconds     211.869                vs   242.965
/stdout_log[14], [20], [31], [37]  — four per-stage elapsed-time strings
```

**Every numerical field is bit-identical.** The committed results JSON is
reproducible from the committed script. (The receipt's `reproduction_note` names
only the first two fields; the four `stdout_log` timing strings are also
run-dependent. Trivial, recorded as D11.)

---

## 1. Measured survival values — recomputed from the raw bytes

I parsed both `.out` files myself (`#`-prefixed header, one float per line),
taking `denom = nb_iteration * q**k_fft` from each file's own header.

| | n=43 | n=50 |
|---|---|---|
| data lines | 1804 | 2311 |
| `nb_iteration` (header) | 4000 | 6000 |
| `q**k_fft` = 241³ | 13 997 521 | 13 997 521 |
| `nb_iteration·q^k_fft` | 55 990 084 000 | 83 985 126 000 |
| counting floor `1/denom` | `1.786030540693598580e-11` | `1.190687027129065666e-11` |
| log2 floor | **−35.70445229** | **−36.28941479** |
| last positive score | **1802** | **2309** |
| first zero score | 1803 | 2310 |
| `values[last] == 1/denom` (IEEE-754) | **True** | **True** |
| any positive value after the first zero | False | False |
| monotone non-increasing | yes | yes |
| log2 `values[0]` | −1.00288006 | −1.00505435 |
| max rel. deviation from an integer multiple of the quantum | **2.1650e-16** (score 520) | **1.8152e-16** (score 131) |
| last score with pooled count ≥ 10 | **1492** (count exactly 10) | **1968** (count exactly 10) |

Both floors equal `1/(nb_iteration·q^k_fft)` as exact float equality. Bands
`[0,1802]` and `[0,2309]` reproduced. The producer's integer-multiple figures
(2.164964216343976e-16 / 1.815e-16) reproduce.

Per-score measured values and pooled counts at every row of the report's §4.2
table (n=43) reproduce exactly:

| score | log2 measured (mine) | report | pooled count (mine) | report |
|---|---|---|---|---|
| 0 | −1.0029 | −1.0029 | 2.79392e10 | 2.79e10 |
| 180 | −4.1207 | −4.1207 | 3.21858e9 | 3.22e9 |
| 360 | −10.1502 | −10.1502 | 4.92715e7 | 4.93e7 |
| 471 | −15.2599 | −15.2599 | 1 427 026 | 1427026 |
| 540 | −18.6109 | −18.6109 | 139 854 | 139854 |
| 630 | −21.8645 | −21.8645 | 14 664 | 14664 |
| 720 | −23.7097 | −23.7097 | 4081 | 4081 |
| 900 | −26.3713 | −26.3713 | 645 | 645 |
| 1080 | −28.4471 | −28.4471 | 153 | 153 |
| 1260 | −30.2782 | −30.2782 | 43 | 43 |
| 1440 | −32.1195 | −32.1195 | 12 | 12 |
| 1616 | −33.1195 | −33.1195 | 6 | 6 |
| 1710 | −34.7045 | −34.7045 | 2 | 2 |
| 1802 | −35.7045 | −35.7045 | 1 | 1 |

`nb_iteration` header-vs-caption (6000 vs 4000 for the n=50 panel): the header
value is not merely better-sourced, it is **forced by the bytes** — the n=50
file's last positive value equals `1/(6000·241³)` bit-for-bit, and
`1/(4000·241³)` is a different double. The producer used the header value and
justified it on provenance; the decisive quantisation argument is available in
its own §1 and is not made.

---

## 2. Score-scale check — answered explicitly: raw, undivided; no `k_fft` alignment

Three independent routes.

**(a) Moment estimators from the survival column** (I re-implemented both):

* A (conditional, integer-grid identity): `E[F²|F≥0] = Σ_{t≥1}(2t−1)S(t)/S(0)`
* B (unconditional, using symmetry of F about 0): `E[F²] = 2Σ_{t≥1}(2t−1)S(t)`

| file | σ_A | σ_B | `sqrt(avg_N/2)` | A,B vs raw | A,B vs `/k_fft` |
|---|---|---|---|---|---|
| n=43 | 113.9051 | 113.7914 | 113.9539 | 0.9996 / 0.9986 | 2.9987 / 2.9957 |
| n=50 | 114.1781 | 113.9783 | 113.9517 | 1.0020 / 1.0002 | 3.0060 / 3.0007 |

All eight digits reproduce the report's §1a table exactly.

**(b) Source definition** — a route the package does not use.
`experiments/EXP-MLKEM-013/vendor-lock/FFT_sample.py:30` defines the score as
`self.F += math.cos((2*math.pi/self.q)*( … ))` summed over the decoded dual
vectors — an **unnormalised** sum of N cosines, wrong-guess second moment N/2.
That is the raw scale.

**(c) Parameter-free positive control.** `Q(T) = P(N(0,N/2) ≥ T) = 0.5
erfc(T/√N)` has zero free parameters and takes N from the header. I recomputed
that it tracks the measurement within **0.1 bit up to score 322 (n=43) / 273
(n=50)**, 0.5 bit to 469 / 401, 1 bit to 525 / 460. A factor-3 scale slip would
destroy this immediately. It is intact.

**Code audit.** `grep -n k_fft approx49_comparison.py`: `k_fft` enters the
counting denominator (`denom = nb_iteration * (q ** k_fft)`), the `/k_fft` ratio
*diagnostic*, and prose. It multiplies or divides **no score and no prediction**.

**Answer: the comparison uses the raw score scale. The known
`Pwrong = fftn/k_fft` vs `Pgood = raw cosine sum` asymmetry with `k_fft = 3` did
not slip into this package.**

---

## 3. Approximation 4.9 — re-derived by me from the archived extracts

Sources read: `inputs/MLKEM-DUAL-SOURCES-20260802/extracts/carrier-hal-05406481/`
`page23_approx_4_8_4_9.txt` (4.17)–(4.25), `page25_pwrong_validation.txt`
(4.26)–(4.29), `page26_fig41.txt` (Fig 4.1 caption), `page27_threshold_choice.txt`,
`page37_tables_C1_C2.txt`. I worked from the text before reading the producer's
implementation.

**Step 1 — the (4.22) weight.** `exp(−t²/N − (d−µ_lsc)²/(2σ²_lsc)) / (πσ_lsc√(2N))`.
I checked numerically (composite Simpson, 2·10⁵ panels) that
`∫exp(−t²/N)dt · ∫exp(−(d−µ)²/(2σ²))dd = 2419.3413118413` against
`πσ√(2N) = 2419.3413118416`, **ratio 1.000000000000**. So `t ~ N(0,N/2)` and
`d_lsc ~ N(µ_lsc,σ²_lsc)` and (4.22) is exactly Model 4.7's convolution
`P(D + N(0,N/2) ≥ T)`.

Writing `u = T − t`: `E(u)` is all of `R²₊` for `u ≤ 0` (so `min = 1`) and, with
`Φ ≤ 1`, empty for `u ≥ N`. Hence

```
Pwrong(T) = Q(T) + ∫_0^N φ(T−u)·min(1, I(u)) du ,  φ(s)=exp(−s²/N)/√(πN)
```

**Step 2 — `Φ_{d_lsc}(x,y)` is not in the archive.** It is introduced with
Approximation 4.6, whose page was not retrieved. I confirmed this myself: the
symbol appears in (4.17) and (4.23) with no definition anywhere in the extracts.
So is `α`; so is `n_lsc`; Lemma 2.9 is cited, not stated.

What the archive *does* pin, and I verified numerically:

* the first factor of (4.19) is **exactly**
  `E_{d~N(µ,σ²)}[exp(−α π² d²/q²)]`. Checked at α ∈ {0.5, 2, 7}: ratios
  1.000000000000, 1.000000000000, 1.000000000000.
* the second factor of (4.19) is **exactly** the β_sieve-ball-norm average of
  `exp(−α(π x/q)²)`, with density `β_sieve t^{β_sieve−1}` on `[0,1]`, `x = d_lat t`.

So (4.19) pins the dependence of `Φ` on `x = ‖w_lat‖` as `exp(−a x²)`, and shows
a Gaussian dependence on the *decoding distance* `d_lsc`. **It does not constrain
the dependence on `y = ‖w_lsc‖`**, which is `Φ`'s second argument in (4.17)/(4.23)
and which is what fixes the exponent through `n_fft`. The producer's word
"forces" (report §2, script STEP 2) is therefore too strong for the half of the
reading that carries `n_fft`. See defect D4.

**Step 3 — the exponent.** Under `Φ = exp(−(a x² + b y²))`,
`E(u) = {a x² + b y² ≤ L}`, `L = ln(N/u)`, and with `λ ∝ x^{β_sieve−1}`,
`µ ∝ y^{n_fft−1}` from (4.24),

```
∫_{E(u)} λ µ = K · L^p ,   p = (β_sieve + n_fft)/2 = 26.0 (n=43), 24.5 (n=50)
```

with `K = C · a^{−β/2} b^{−n_fft/2} · G(β_sieve, n_fft)`. I verified the closed
form `G(β,n) = Γ(β/2)Γ(n/2)/(2(β+n)Γ((β+n)/2))` numerically at
(β,n) ∈ {(4,2),(6,4),(3,5)} — ratios 1.000000 in all three cases. Exponent
arithmetic: 44+8 = 52 → 26.0; 41+8 = 49 → 24.5. Both reproduce.

**Step 4 — my implementation, deliberately different from the producer's.**
The clip binds for `u ≤ u* = N exp(−K^{−1/p})`, so

```
Pwrong(T;K) = Q(T − u*) + K ∫_{u*}^{N} φ(T−u) ln(N/u)^p du
```

— i.e. I put the `min(1,·)` kink at its **exact** location and evaluate the
clipped piece in closed form, where the producer grids in `v = ln(N/u)` over
4370 fixed nodes and lets the kink fall wherever it falls inside a panel. I
integrate in `u` with composite Gauss–Legendre order 10 on a geometrically graded
mesh (`h = min(12, 0.04u)`), windowed at `|T−u| ≤ 12√(N/2)`. Convergence check:
re-running with `h = min(6, 0.02u)` and order 12 changed **no printed digit**.

---

## 4. Predicted curve — my implementation against the committed one

At the producer's exact `log2 K_fit = −72.71258147256952`, n=43:

| score | log2 pred (mine) | committed | Δ | log2 Q (mine) | committed |
|---|---|---|---|---|---|
| 0 | −0.701905 | −0.7017450 | −0.00020 | −1.00000 | −1.0000 |
| 180 | −3.318032 | −3.3176 | −0.00043 | −4.13034 | −4.1303 |
| 360 | −8.818581 | −8.8180 | −0.00058 | −10.30387 | −10.3039 |
| 471 | −13.744464 | −13.7438 | −0.00066 | −15.77101 | −15.7710 |
| 540 | −17.241531 | −17.2410 | −0.00053 | −19.82701 | −19.8270 |
| 630 | −21.250186 | −21.2500 | −0.00019 | −25.88439 | −25.8844 |
| 720 | −23.489712 | −23.4897 | −0.00001 | −32.81665 | −32.8166 |
| 900 | −26.371002 | −26.3710 | −0.00000 | −49.32518 | −49.3252 |
| 1080 | −28.684862 | −28.6849 | +0.00004 | −69.37968 | −69.3797 |
| 1260 | −30.682517 | −30.6825 | −0.00002 | −92.99576 | −92.9958 |
| 1440 | −32.464293 | −32.4643 | +0.00001 | −120.18315 | −120.1831 |
| 1616 | −34.052029 | −34.0520 | −0.00003 | −150.22572 | −150.2257 |
| 1710 | −34.849714 | −34.8497 | −0.00001 | −167.67399 | −167.6740 |
| 1802 | −35.601412 | −35.6014 | −0.00001 | −185.69747 | −185.6975 |

Maximum disagreement **0.00066 bits**, and it tracks the clipped fraction
exactly — which is the signature of the kink-handling difference (D10), not of a
modelling difference. `Q(T)` agrees to every printed digit.

### 4.1 Full-band statistics at the producer's exact K

| | mine (n=43) | report | mine (n=50) | report |
|---|---|---|---|---|
| min Δ / at score | **−0.9325 / 1616** | −0.933 / 1616 | **−0.9170 / 2283** | −0.917 / 2283 |
| max Δ / at score | **+1.5154 / 471** | +1.516 / 471 | **+1.7109 / 420** | +1.710 / 420 |
| mean Δ | **+0.2449** | +0.245 | **+0.1920** | +0.192 |
| rms Δ (whole band) | **0.7055** | 0.706 | **0.6969** | 0.697 |
| sign changes / first | **12 / 888** | 12 / 888 | **14 / 1090** | 14 / 1090 |
| later crossings | 1682, 1693, 1741 | 1682/1693/1741 | 2044, 2084, 2286 | 2044/2084/2286 |

Every number, including the sign-change count and every crossing score,
reproduces.

### 4.2 My own fit

Golden section on `log2 K` over the **whole** band (all 1803 / 2310 scores),
my model:

| | mine (whole band) | committed (92-/117-point subsample) |
|---|---|---|
| n=43 `log2 K_fit` | −72.711622 | **−72.712581** |
| n=50 `log2 K_fit` | −67.219917 | **−67.222505** |

Agreement 0.001 / 0.003 bits. At my own K the residual statistics are
n=43 min −0.93158 max +1.515771 mean +0.245633 rms 0.705494; n=50 min −0.914363
max +1.711953 mean +0.194151 rms 0.696881 — stable to ~0.003 bits under the K
difference. Sub-band (clip < 1e-3 ∧ count ≥ 10): n=43 scores 756–1492, n = 737,
min −0.673968 max +0.180672 mean −0.20132 **rms 0.282294** (report: 755–1492,
n = 738, −0.675/+0.182/−0.202/**0.283**); n=50 scores 727–1968, n = **1242**
(exact match), min −0.637778 max +0.247056 mean −0.16048 **rms 0.272238**
(report: −0.640/+0.244/−0.163/**0.274**). The one-score boundary offset at 755
is D10.

### 4.3 Anchors and elasticity

| | mine | report |
|---|---|---|
| n=43 first score below 2^−5 | 213 (meas 3.123893e-02) | 213 |
| n=43 `log2 K` anchored low / high | −89.978460 / −72.147622 | −89.979061 / −72.147621 |
| n=43 anchor-low worst undershoot / mean | −18.1984 / −10.6965 | −18.20 / −10.70 |
| n=43 anchor-high worst overshoot | +1.7524 | +1.75 |
| n=50 first score below 2^−5 | 214 | 214 |
| n=50 `log2 K` anchored low / high | −82.956085 / −66.704754 | −82.956451 / −66.704753 |
| n=50 anchor-low worst / mean | −16.6505 / −11.4762 | −16.65 / −11.48 |
| n=50 anchor-high worst overshoot | +1.9454 | +1.95 |

Elasticity at score 213: the committed `per_score` row gives 0.1535 (report
"0.15"); the column is defined at `K_fit`, and I confirm that at `K_low` it is
0.0057, i.e. **even less** sensitive than the report says. The point the report
makes with it stands a fortiori.

### 4.4 Parameter-free component and the sub-floor dip

| | mine (n=43) | report | mine (n=50) | report |
|---|---|---|---|---|
| `Q` within 0.1 / 0.5 / 1 bit to score | 322 / 469 / 525 | 322 / 469 / 525 | 273 / 401 / 460 | 273 / 401 / 460 |
| `Q` deficit at score 1000 | 32.400 bits | 32.40 | 35.156 bits | 35.16 |
| `Q` deficit at the counting floor | 149.993 bits | 149.99 | 265.557 bits | 265.56 |
| measurement below `Q` at scores | 0–126 | 0–126 | 0–133 | 0–133 |
| max shortfall | 0.0037 bits (at 51) | 0.0037 | 0.0069 bits (at 57) | 0.0069 |

### 4.5 Pgood file (recorded, not compared)

n = 4000, min **6667.673616**, max **17822.813537**, mean **11983.50504752** —
all reproduce. Sorted: `v[1999] = 11964.145101`, `v[2000] = 11964.802334`,
`0.5(v[1999]+v[2000]) = 11964.473718 = statistics.median`. The package reports
11964.802334, which is the **upper** central order statistic; report §5(6) and
`receipt.json → anomalies` both call it "the lower". See D9.

### 4.6 Exponent scan (the package's model-family control)

Reproduced from the committed JSON's own `free_exponent_diagnostic` (grid
`band[::40]` + last score; 47 and 59 points): n=43 rms 1.9602 @ p=10, 1.0102 @ 18,
0.7426 @ 20, 0.5045 @ 22, **0.4539 @ 24**, **0.6924 @ 26 (archived)**, 1.0610 @ 28;
n=50 2.3478 @ 10, 1.0368 @ 18, 0.6784 @ 20, **0.4379 @ 22**, 0.6020 @ 24,
**0.6936 @ 24.5 (archived)**. Every value the report quotes matches its own JSON,
and the whole JSON is byte-reproducible from the script (§0a). **Both files
prefer an exponent about 2–2.5 below their archived value.** The report discloses
this and does not adjust the model.

---

## 5. Resolved-band check — answered explicitly: PASS

* `per_score` in the committed JSON has exactly **1803** rows over `[0,1802]` and
  **2310** rows over `[0,2309]`; no row carries `measured ≤ 0`.
* fit grid `band[::20]` + last, exponent-scan grid `band[::40]` + last, anchors
  213/1492 and 214/1968, and the K-solved profile (elasticity > 0.9 ∧ count ≥ 10,
  scores 643–1492 and 600–1968) are all slices of the band.
* the floors `2^−35.70445229` and `2^−36.28941479` are `1/(nb_iteration·q^k_fft)`
  and are the *instrument's* resolution, not a property of the distribution; the
  package says so in `instrument.note` and I confirmed the code obeys it.
* **Nothing is compared, fitted, anchored, scanned or extrapolated past the last
  positive score.**

One nuance, a limitation rather than a violation: `scale_check` sums the moment
series over the whole file column including the trailing zeros. Those contribute
exactly 0, so no unmeasured value is used *as* a value, but the second moment is
biased low by the unresolved tail (bounded above by ~`1802²·1.8e-11 ≈ 6e-5`
relative). It does not affect the ≈1.00-vs-≈3.0 conclusion.

---

## 6. Controls

**Present in the package.** (i) A parameter-free positive control: `Q(T)`, zero
free parameters, tracking the measurement within 0.1 bit over the first ~320
scores (§2c, §4.4). (ii) A model-family control: the exponent scan (§4.6),
showing rms degrades to 1.96/2.35 bits at p=10 and 3.63/4.38 at p=40, so a
one-parameter family of this shape does not fit automatically.

**Absent.** No **null-object control** in the sense of
`docs/inventor-protocol.md` §3 — the same one-parameter fit is never run against
a structurally null survival curve of the same shape. The exponent scan is a
within-family sensitivity, not a null object. Because the package reports a
goodness-of-shape comparison rather than a correlation, bias or excess, I do not
treat this as fatal, but it is the reason the "tracks across 34.7 bits" sentence
cannot be read as a measurement of the model's specificity.

**My own nearby-object control.** I fitted the model built with one file's
archived `(p, N)` to the *other* file's measured curve, one free K, whole-band
rms:

| data | model p=26.0, N=25971 (n=43) | model p=24.5, N=25970 (n=50) |
|---|---|---|
| n=43 | 0.7055 (matched) | **0.4965 (swapped — better)** |
| n=50 | 1.0204 (swapped) | 0.6969 (matched) |

The discrimination is one-sided: the n=43 measurement fits the **other** file's
archived exponent better than its own. This is the same fact as the package's own
§4.4 (both files prefer p ≈ 2 lower), seen in a form that cannot be absorbed by
the free K. It is disclosed in substance by the producer; I record it because it
bounds what "the recomputed Approximation 4.9 tracks the measurement" is entitled
to mean.

---

## 7. Parameter availability — searched myself

* **`Φ_{d_lsc}(x,y)`** — I confirm it is defined in no archived extract. The
  producer's UNAVAILABLE classification stands.
* **`n_lsc`** — stands.
* **`α`** — not in any archived page extract; stands. The producer recorded the
  Pgood header's `alpha_secret=2 / alpha_error=2` as an unverified candidate and
  **used no value**; I confirmed by code reading that both are parsed, logged and
  stored and enter no computation. I also note that
  `experiments/EXP-MLKEM-013/vendor-lock/utilitary.py:95,100,102` shows
  `create_sample(A, alpha_secret, alpha_error, q)` building
  `Centered_Binomial(alpha_secret)` and `Centered_Binomial(alpha_error)` — these
  are the secret/error distribution parameters, so the candidate identification
  with (4.19)'s α is not merely unverified, it is refutable from repository
  bytes. Nothing depends on it.
* **`δ(β_bkz)`** — **the producer's classification does not stand.**
  `experiments/EXP-MLKEM-013/vendor-lock/utilitary.py:16`, in the same
  hash-verified vendor-locked upstream tree that produced the Pwrong data,
  defines

  ```python
  def root_hermite_factor(beta):
      return ((beta/(2*math.pi*math.e))*((math.pi*beta)**(1/beta)))**(1/(2*(beta-1)))
  ```

  which is δ(β). I evaluated it: **δ(32) = 1.012528410**, **δ(35) = 1.012604644**,
  hence `δ^1364 = 2^24.501` and `δ^1681 = 2^30.377`. The archived (4.24) already
  carries Lemma 2.9's result inline as the `δ^{β_sieve(m+n_lat−β_sieve)}` factor,
  so Lemma 2.9 is not separately needed either. See D3. (The producer's
  sensitivity arithmetic is correct: `1364·log2(1.001) = 1.967` and
  `1681·log2(1.001) = 2.424` bits, quoted as "roughly 2.0 and 2.4".)

---

## 8. The `d_lsc` integral

Archived (4.22) integrates over `d_lsc` **inside** `min(1, ∫_{E(T−t)}λµ)`, and
`E` depends on `d_lsc` through `Φ_{d_lsc}`. The script's STEP 3 replaces
`E_{d_lsc}[min(1, K(d_lsc)L^p)]` by `min(1, K̄ L^p)`. Its docstring states the
reduction is exact only where the clip does not bind and reports the clipped
fraction per score — honest, but **no bound on the collapse error is given**, and
`min(1,·)` is concave, so by Jensen the collapsed model is an **upper bound** on
(4.22). The report's two headline divergences (+1.516 at score 471, +1.710 at
score 420) sit at clipped fractions 0.361 and 0.381 — squarely inside the regime
where the reduction is an approximation, and biased in the same direction as the
reported over-prediction. See D5. I did not quantify the size of the effect,
because doing so requires a further declared reading of how `d_lsc` enters Φ's
quadratic form, and adding my own unarchived assumption to a package I am
validating would not be a check.

---

## 9. Receipt-integrity checks

* `git_commit_at_execution: 5f8bb4eb49b7391ef4fbeabcee03590fd5d39a1a` — the
  object exists in this repository. `dirty_tree_at_execution: true`, with the one
  untracked path being the task's own write scope; disclosed.
* `randomness: "none"` — the computation is deterministic and I confirmed it: the
  re-execution reproduced every numerical field bit-for-bit (§0a). No seed exists
  to record, correctly.
* `environment` — python 3.11.15, Linux-6.18.5, numpy/scipy absent. My own
  session sees the identical interpreter string and the same absence.
* resources: 243.078 s wall (wrapper) vs 242.965 s in-script; peak RSS 23.4 MB
  against 4 GB. Internally consistent.
* `maximum_runs_allowed: 1`, `script_executions_performed: 2`,
  `budget_exceeded: false` — the last two contradict each other. See D6.
* execution 1's `comparison_results.json` was overwritten at the same path, so
  the "bit-identical apart from the defective diagnostic" claim is
  **unable_to_check** (D7). I independently recomputed every quantity the receipt
  lists as unchanged and all of them reproduce, which corroborates but does not
  verify it. I note that the disclosed change ran from *unfavourable to
  favourable* (shape drift 15.39 → 1.15 bits), which is the case where disclosure
  matters most, and that it is disclosed with the superseded numbers quoted.
* timestamps: `comparison_results.json` records `generated_at_utc =
  2026-08-02T23:31:21Z` (written from the run's start) with 242.965 s, so the
  final execution ran 23:31:21–23:35:24Z; `receipt.json` records
  `final_script_execution_started_utc = 23:47:36Z` and `task_completed_utc =
  23:58:00Z`, the latter **after** the snapshot commit at 23:49:11Z whose
  committed blob already contains that string. See D8.

---

## 10. What I could not check

1. Bit-identity of execution 1's retained outputs — the artifact was overwritten
   (D7). Substituted by independent recomputation.
2. Whether the declared reading of `Φ_{d_lsc}` is the paper's — the page defining
   Approximation 4.6 is not in the archive. Confirmed absent; not assumed.
3. The absolute level of Approximation 4.9 — blocked by `α` and by `Φ`'s exact
   functional form (**not** by δ, see D3).
4. The third Pwrong file (`…beta037_beta144_N200001.out`) — header extract and
   SHA-256 only, no survival column in this repository. Pre-existing archival
   gap; not introduced here.
5. The effective sample size of the pooled counting estimator — the `q^k_fft`
   candidates inside one FFT share dual vectors and target, so counts of 1–10
   support indicative Poisson reasoning only. The package records this.
6. Whether verifyModel's conventions produced the paper's Table 5.1 / C.2 — no
   retrieved artifact connects them.
7. `python3 -m orchestration.adapter doctor --probe` — no backend reachable;
   `model_verified` stays false for this report as for the producer's. Not run,
   not asserted.

---

## 11. Relationship to the partial artifact of TASK-20260802-08f428

I reached §§0–9 before opening
`…/tasks/TASK-20260802-08f428/validation_notes.md`. That file carries no verdict
field and its own §12 disclaims being one. Read afterwards, it overlaps my §§0–4
and §§7–9 and its digits agree with mine where they overlap; it also contains
work I did **not** reproduce and on which I place no reliance — its §6.2
continuous-optimum figures, its §6.3 heavy-tailed-Φ control, its §6.4 horizontal
stretch control, and its §6.5 quantification of the `d_lsc` collapse (0.21 bits).
**No claim in this report or in `validation_report.yaml` rests on that file.**
Where we agree — the δ finding, the drift-sentence arithmetic, the timestamp
inconsistency, the Pgood-median direction, the `d_lsc` structural point — I
verified each independently in this session and give my own commands and values
above. Its termination was a provider session limit, i.e. infrastructure, and
under AGENTS.md rule 5 that is evidence about neither the producer's work nor the
mathematics.

---

## 12. Non-claims of this validation

Toy parameters only (q=241, m=40, n=43/50, n_fft=8, k_fft=3). Nothing here is an
ML-KEM or Kyber security claim, a crypto-scale statement, or a cost-model
revision (AGENTS.md rule 7). Nothing here changes any record's status. **AGENTS.md
rule 12 remains UNMET and UNWAIVED: EV-MLKEM-011, EV-MLKEM-013 and EV-MLKEM-017
keep their status**, and my §7 finding about δ and α is an observation about
parameter availability, not a correction to any of them. An admissible receipt is
not a verdict on Approximation 4.9; that judgement belongs to the Reviewer and
the Coordinator. No new sampling, no G6K run, no network access, no producer
artifact edited, no commit made.
