# TASK-20260803-b214b1 — red team of BATCH-012's positive finding

BATCH-013, GOAL-MLKEM-003. Independent session. Reviewed snapshot
**d274699aade09abc81815627d16afaf06085d91a** (verified: `git cat-file -t` →
commit; ancestor of HEAD `90c42ef5`), ledger commit **4783b381** (ancestor of
HEAD). Target: `EV-MLKEM-553b83` P-1/P-2 and `DEC-20260803-3bba92`.

**Zero new sampling, no network, no G6K.** Every number below is a
deterministic function of bytes already in this repository. The vendored PDF
was not opened in this session at all — it was not needed. No producer or
validator artifact was modified. Nothing was committed. Toy tier (q=241, m=40,
n=43/50), resolved band only, raw undivided score scale. **No ML-KEM or Kyber
security claim in either direction.** AGENTS.md rule 12 is UNMET and UNWAIVED:
`EV-MLKEM-011`, `EV-MLKEM-013`, `EV-MLKEM-017` keep their status;
`KN-FIND-031` stays withdrawn.

---

## 0. Bottom line, stated before the argument

**The positive finding SURVIVES in its comparative form and DOES NOT SURVIVE in
its absolute form.**

I wrote three independent implementations in this session — of the counting
floor, of the Gaussian-Φ surrogate leg, and of the exact region measure with
its Υ evaluation, region assembly, ψ_lsc mixture and u-quadrature — and every
quantitative claim I was able to reach reproduces. I could not break Claim 1's
numbers, Claim 1's parameter count, or the attribution correction. I did break
the sentence the decision is built on.

What survives, restated at the strength the evidence carries:

> The region measure implied by (4.10)/(4.11)/(4.24), with **one fitted
> normalisation and no fitted exponent**, fits the archived band strictly and
> substantially better than BATCH-009's Gaussian-Φ surrogate: 0.3556 against
> 0.7055 bits (n=43) and 0.3172 against 0.6969 (n=50) at **matched parameter
> count**, and against 0.4271/0.4274 at the surrogate's two-parameter best.
> **98.6 % (n=43) and 90.8 % (n=50) of the matched-parameter improvement is
> contributed by the `count>=1000` rows, where the counting floor is
> negligible** — so the improvement is not a tail artifact and does not depend
> on any floor protocol. Two structurally different second parameters buy
> ≤ 2·10⁻⁴ bits on the whole band.

What does not survive:

* **"fits the whole band at 1.06–1.13× the counting-noise floor"** — and every
  variant of it: "at the floor", "CLOSED", "consistent with the counting floor
  to within the floor's own protocol correction", and ANOM-4's "below its
  floor". Six reasons below; two of them are individually decisive.
* **"the whole-band misfit ... was a property of the SURROGATE, not of
  Approximation 4.9's region measure"**, as an unqualified sentence.
* **"corrects three batches of this program's own work"** as a description of
  the record actually corrected.

Verdict: **`pass_with_constraints`**. This is not a package defect finding —
the package is the most carefully executed in this goal. It is a finding about
one statistic that the package, the review and the decision all read too
literally.

---

## 1. What I recomputed independently, and what agreed

Everything in this section is a check that *passed*. It is here because a red
team that reports only failures is not usable, and because these agreements are
what make §2 a statement about a statistic rather than about an implementation.

### 1.1 The counting floor — fourth independent computation

My own truncated-Poisson sum, own window (`15√λ+30` vs the producer's
`12√λ+20` and the validator's `14√λ+20`), own branch switch (`3e5` vs `1e5`
and `2e5`), own three-term asymptotic. Every published digit of both columns:

| | n=43 whole | ge10 | ge1000 | ge1e5 | n=50 whole | ge10 | ge1000 | ge1e5 |
|---|---|---|---|---|---|---|---|---|
| this session | 0.340570 | 0.163689 | 0.014627 | 0.001072 | 0.327569 | 0.155755 | 0.015192 | 0.001357 |

The floor now has **four** independent computations. **It is right as
arithmetic.** §2 is not an attack on its arithmetic.

### 1.2 The surrogate leg — fifth independent implementation

Own Gauss–Legendre, own three-zone panel layout (1520 nodes vs the producer's
876 and the validator's 1960), own kernel cut (150 vs 120 and 150), own fit
schedule.

* BATCH-009 archived point: **0.705491** (n=43) and **0.696880** (n=50),
  against producer 0.705494/0.696885, validator 0.705502/0.696895, BATCH-010
  0.705494, BATCH-009 archived 0.705760/0.696721.
* M1a at the frozen own exponent: **0.705491** / **0.696877**.
* M1 whole band n=43: **0.427120 @ p=23.00** (producer 0.427122).

### 1.3 The exact region measure — third independent implementation

Υ_n by **Poisson's integral** in double precision (not the (4.11) alternating
series in 120-digit `Decimal`); the region assembled by **monotone-segment
inversion of Υ_a** with exact ξ^{β_sieve} endpoint measures (not the producer's
per-η root-finding, not the validator's τ-table); own η quadrature; own ψ_lsc
mixture `F` built from a tabulated `J(x)=∫_x^∞ ψ(d)d^{-n_fft}dd`; own
u-quadrature and fit.

```
Ups_a first zero  27.567944 (n=43, a=22)   25.955681 (n=50, a=20.5)
Ups_b first zero  6.380162
local log-log slope of G, n=43: 3:24.42 5:23.09 6:22.31 7:21.41 8:20.38
                                 9:19.32 10:19.06 11:21.54 12:26.24
local log-log slope of G, n=50: 3:22.92 5:21.57 6:20.76 7:19.83 8:18.77
                                 9:17.88 10:18.71 11:22.83 12:27.15
```

Both slope rows reproduce **every printed digit** (the n=50 row was
`unable_to_check`; see §4).

M2, all eight cells, producer's value in brackets:

```
n=43  whole 0.355633 [0.355665]  ge10 0.279761 [0.279823]
      ge1000 0.349394 [0.349477] ge1e5 0.205507 [0.205521]
      log2A -172.24695 [-172.247] -172.15373 [-172.154]
            -172.21875 [-172.219] -174.85162 [-174.852]
n=50  whole 0.317174 [0.317217]  ge10 0.276876 [0.276937]
      ge1000 0.355621 [0.355705] ge1e5 0.437667 [0.437757]
      log2A -155.50686 [-155.507] -155.44265 [-155.443]
            -155.41085 [-155.411] -155.76006 [-155.760]
```

Agreement to ≤ 9·10⁻⁵ bits on every cell and to five decimals on every
`log2 A`. **Claim 1's numbers are not in doubt.**

### 1.4 The null-object control the lane has never run — and it PASSES

`docs/inventor-protocol.md` §3 requires the identical measurement against an
object of the same shape known to carry no signal. The validator recorded its
absence "from the whole lane". I ran it. Four one-parameter families with no
source content whatever, each fitted by the same protocol on the same index
set, whole band, as a multiple of the published floor:

| family (1 free parameter) | n=43 | n=50 |
|---|---|---|
| `1{v ≥ v*}` (hard step) | 47.0× | 56.9× |
| logistic in v, slope frozen at 1 | 30.0× | 30.8× |
| logistic in v, slope frozen at 3 | 5.67× | 7.48× |
| `min(1, exp(k(v−v*)))`, k = p_own/7 | 4.86× | 6.70× |
| **M1a — surrogate, exponent frozen** | **2.07×** | **2.13×** |
| **M2 — exact measure, exponent frozen** | **1.04×** | **0.97×** |

**The Coordinator's first candidate objection fails.** A single fitted scale
does *not* rescue almost any monotone shape over this band: generic
one-parameter monotone families land at 4.9×–57×, not near 1×. The whole-band
statistic is not trivially satisfiable, and M2's position on it is not
manufactured by the fitted normalisation. I record this as a **failed
objection**, plainly.

### 1.5 A validator limitation discharged, in the package's favour

`validation_report.yaml` `limitations` records:

> "β_sieve is taken as the .out header's beta_1 (44 / 41) rather than beta_0. I
> could not verify that identification against the source ... it is an
> unverified premise underneath every number in the lane."

It is verifiable, from an extract already in the repository.
`inputs/MLKEM-DUAL-SOURCES-20260802/extracts/carrier-hal-05406481/page26_fig41.txt`,
lines 48 and 50:

```
βsieve = 44, dlat = 42.00, µlsc = 23.94 and σlsc = 3.38,
βbkz = 35, βsieve = 41, dlat = 58.60, µlsc = 23.87 and σlsc = 3.30.
```

against headers `beta_0=32, beta_1=44` (n=43) and `beta_0=35, beta_1=41`
(n=50). The source's own Fig 4.1 caption gives β_sieve = 44 and 41 and
β_bkz = 35 — **exactly the identification used**. The frozen exponent
(β_sieve+n_fft)/2 = 26.0 / 24.5 is the source's, not a modelling choice that
could have gone otherwise. This closed what would have been my sharpest attack
on "the exponent is frozen": had β_sieve been β_bkz, the frozen exponent would
have been 20.0 / 21.5, sitting inside the drift range, and the whole
one-fewer-parameter claim would have rested on a data-selected discrete choice.
It does not. **Recorded in the package's favour and the limitation is
dischargeable.**

### 1.6 The s-selection is real, not a flat likelihood

I suspected "two second parameters select their null value exactly and buy
nothing" was the signature of an insensitive statistic. It is not. The
producer's own whole-band s-curve is sharply curved: the three-point parabola
through (0.97, 0.375030), (1.00, 0.355665), (1.04, 0.402233) has vertex
s* = 0.9975 with curvature 25.9 bits per unit², and the n=50 curve has
s* = 1.0020 with curvature 39.6. The continuous minimum improves on s = 1.00 by
**1.6·10⁻⁴ bits** in both files. The selection is genuine.

---

## 2. The objection that lands: the whole-band ratio is not a goodness-of-fit statistic

### 2.1 Where the denominator comes from

Computed from the archived counts alone (`floor_row` applied per row, summed
per index set):

| | rows | share of rows | **share of whole-band floor variance** |
|---|---|---|---|
| n=43, C ≥ 1000 | 852 | 47.3 % | **0.087 %** |
| n=43, C < 10 | 310 | 17.2 % | **80.87 %** |
| n=43, C < 3 | 121 | 6.7 % | **37.04 %** |
| n=50, C ≥ 1000 | 1132 | 49.0 % | **0.105 %** |
| n=50, C < 10 | 341 | 14.8 % | **80.73 %** |

**99.91 % of the denominator of the headline ratio is supplied by rows the same
package reports as unmeasured-quality, and 81 % by 310 rows whose entire
measurement is fewer than ten pooled counts.**

### 2.2 Where the numerator comes from, and the exact identity

Decomposing each model's residual at its own whole-band fit (my implementation;
the M2 n=43 split agrees with the validator's 0.349849 to 8·10⁻⁵):

| model (whole-band fit) | rms on C≥1000 | ×floor | rms on C<1000 | ×floor |
|---|---|---|---|---|
| n=43 M1a (1 par) | 0.9470 | **64.7×** | 0.3745 | **0.799×** |
| n=43 M1 (2 par) | 0.4630 | **31.7×** | 0.3922 | **0.837×** |
| n=43 **M2 (1 par)** | 0.3498 | **23.9×** | 0.3608 | **0.770×** |
| n=50 M1a (1 par) | 0.9192 | **60.5×** | 0.3747 | **0.817×** |
| n=50 M1 (2 par) | 0.5311 | **35.0×** | 0.2953 | **0.644×** |
| n=50 **M2 (1 par)** | 0.3627 | **23.9×** | 0.2663 | **0.581×** |

Whence, exactly, for n=43:

```
   (whole-band ratio)^2  =  0.5919  +  (residual variance sum on the 852
                                        C>=1000 rows) / 209.126
```

and for n=50 with constant 0.3369 and divisor 247.86. Two consequences.

**(a) The measurable misfit is attenuated by ~10³.** M2's residual variance sum
on the C≥1000 rows is 104.28, which is **572×** the floor of those same rows
(0.18229). In the whole-band ratio that same quantity is divided by 209.126
instead — an attenuation of **1147×** (n=43) and **949×** (n=50). "1.04×" is
"23.9×" put through that divider and added to a constant.

**(b) There is a floor to the statistic that has nothing to do with fit
quality.** A model that were *exactly right* on all 852 measurable rows, with
M2's tail behaviour, would read **0.769×** (n=43) and **0.581×** (n=50), not
1.00×. The scale on which "1.04×" is being read as "at the floor" runs from
about 0.6 to about 2, not from 1 upward.

### 2.3 The controlled null for the tail component

Look at the last column of the table in §2.2. In the sub-band that supplies
99.9 % of the denominator:

* the exact measure scores **0.770× / 0.581×**;
* the surrogate at its own frozen exponent — which the *same statistic* rejects
  at **64.7× / 60.5×** on the measurable rows — scores **0.799× / 0.817×**.

**A model known to be wrong by a factor of sixty scores the same as the exact
one in the region that supplies almost the whole denominator, and both score
below the floor.** By `docs/inventor-protocol.md` §3 that is a controlled null,
not a finding: the tail component of the whole-band statistic has no
discriminating power at all, and it is what the ratio is mostly made of.

This is the precise sense in which the Coordinator's third candidate objection
— "does 'fits the whole band' mean anything when the whole-band statistic is
mostly low-count rows near the floor?" — is **upheld**, and it is stronger than
the framing suggested: it is not merely that those rows are noisy, it is that
they score *below* the floor for every model tested, including one that fails
by 60×.

### 2.4 The artifact tell: the quantity does not do what it should

`docs/inventor-protocol.md` §3 asks what parameter should destroy the reported
quantity. Here it is the one modelling choice the source leaves undetermined:
(4.22) integrates d_lsc from 0 against a *normal* density, so the model's deep
tail is governed by the left tail of a Gaussian approximation to a decoding
distance, where it has no physical support. The producer's own ANOM-7 declares
this and bounds it. I reproduced the variant independently (n=43, ψ_lsc
truncated below μ−4σ = 10.422836):

```
whole   0.322071 [producer 0.322072]   ge10   0.283815 [0.283812]
ge1000  0.354773 [0.354771]            ge1e5  0.206078 [0.206078]
ln_A   -119.30967 [-119.3096973737681]
```

and likewise for n=50 (`whole 0.306416 [0.3064170322]`, `ge10 0.278489
[0.2784880434]`, `ge1000 0.359358 [0.3593558528]`, `ge1e5 0.441210
[0.4412081927]`, `ln_A −107.74405 [−107.7440788952]`). I then decomposed both,
which the package did not:

| whole-band fit | whole rms | ×floor | C≥1000 | ×floor | C<1000 | ×floor |
|---|---|---|---|---|---|---|
| n=43 primary (ψ_lsc from 0) | 0.355633 | 1.044 | 0.34977 | **23.9×** | 0.36080 | **0.770×** |
| n=43 ANOM-7 variant | 0.322071 | 0.946 | 0.35582 | **24.3×** | 0.28851 | **0.616×** |
| n=50 primary | 0.317174 | 0.968 | 0.36265 | **23.9×** | 0.26625 | **0.581×** |
| n=50 ANOM-7 variant | 0.306416 | 0.935 | 0.36252 | **23.9×** | 0.24048 | **0.525×** |

**The undetermined modelling choice improves the headline whole-band statistic
by 9.4 % (n=43) and 3.4 % (n=50) while leaving the fit on the rows where the
data are good unimproved — worse for n=43, unchanged for n=50.** The entire
improvement is bought by descending further below the deep-tail floor, from
0.770× to 0.616× and from 0.581× to 0.525×. A statistic that rewards a change which degrades
the fit where the measurement is precise is measuring the tail, not the fit.
This alone disqualifies the whole-band ratio as evidence about the source
model, and it disqualifies quoting it to three significant figures: the same
package reports 1.04× and 0.95× for two readings of one undetermined choice.

### 2.5 The statistic's own sampling error is ~50×  the precision it is quoted at

This follows from the validator's own D-1, and I believe it is the single most
important number in this review.

D-1 establishes that survival counts are cumulative, so for the counting
residual ε_T = ln(C_T/λ_T),

```
    Cov(ε_T, ε_T') = min(1/λ_T, 1/λ_T')
```

— ε is Brownian in the time change 1/λ, not white. The validator used this to
correct the *mean* of the floor by 6–11 %. It also fixes the *variance* of the
whole-band statistic, which nobody computed. For Q = (1/n)Σ ε², the effective
degrees of freedom is

```
    dof = (Σ_T a_T)^2 / Σ_{T,T'} min(a_T, a_T')^2 ,     a_T = Var(ε_T)
```

Computed on the archived counts with the **exact** truncated-Poisson per-row
variances:

| | whole | count≥1000 |
|---|---|---|
| n=43 | **dof = 1.55** | dof = 1.81 |
| n=50 | **dof = 1.51** | dof = 1.90 |
| (white-noise comparison, n=43 whole) | dof = 422 | dof = 163 |

**dof ≈ 1.5.** A model that is *exactly right* therefore produces a whole-band
rms/floor ratio whose sampling standard deviation is

```
    sd(ratio) ≈ ½·sqrt(2/dof) ≈ 57 % (n=43),  58 % (n=50).
```

Consequences, all of which must be carried:

1. **"1.06–1.13×" is quoted to three significant figures on a statistic with a
   1σ spread of ±0.5.** So is "1.04×/0.97×", and so is my own leverage-corrected
   1.16× in §2.6. They are the same number.
2. **The entire D-1 debate is immaterial to any conclusion.** D-1 moves the
   ratio by 6–11 %; the statistic's own sd is 57 %. D-1 is a correction to
   *wording*, and `DEC-20260803-3bba92`'s weighing calls it "THE MOST IMPORTANT
   CORRECTION" of the review. It is the most important correction to the
   language; it is not evidence.
3. **ANOM-4 was never an anomaly.** A perfect model on n=50 has a ~58 % chance
   of reading below 1.00×, and about a 47 % chance under any reasonable
   calculation. Both the producer's plug-in explanation (D-8: <0.5 %, wrong
   sign) and the validator's Brownian explanation (D-1: 8–11 %) are explaining
   a 3 % deviation that needs no explanation.
4. **What is *not* affected** is the model comparison. M2 versus M1 versus M1a
   is a paired comparison on one shared noise realisation, and §1.4/§2.2 show
   91–99 % of the matched-parameter improvement lands on rows whose counting
   noise is negligible. The comparison is highly significant; the absolute
   reading is not.

Cheapest check: the four-line computation above, on the archived `.out` counts.

### 2.6 D-1 is itself understated, and its count≥1000 leg has the wrong sign

The Coordinator asked whether the D-1 correction is right and whether a fully
correct protocol moves the exact model further. Answers: it is right in method,
it is understated in magnitude, and yes.

I reproduced the validator's §1.7 computation exactly. With a pure offset
(h ≡ 1) and delta-method per-row variances:

```
n=43 whole       0.409366 -> 0.377735   (0.923)   [validator: 0.923]
n=43 count>=1000 0.014620 -> 0.013266   (0.907)   [validator: 0.907]
```

Then I substituted the validator's **own measured leverage vector**
`d ln(Pred)/d ln A = 0.031, 0.097, 0.204, 0.755, 0.997, 0.993, 0.983, 0.963,
0.924, 0.856` at T = 0, 200, …, 1800, which it printed and then did not use:

```
n=43 whole       0.409366 -> 0.366645   (0.896)
n=43 count>=1000 0.014620 -> 0.010362   (0.709)
```

* On the whole band the correction is **0.896, not 0.923** — because the fit is
  *not* a pure offset, and the residual it fails to absorb at small T is where
  the noise is not.
* On count≥1000 the correction is **0.709, not "between 0.90 and 1"**. The
  validator reasoned that a mean sensitivity of 0.42 means the fit absorbs
  *less*. The opposite is true: on that sub-band both a_T and h_T increase with
  T, so the profiled parameter is optimally targeted at exactly the
  high-variance rows, and it absorbs *more*.

Carrying that through: M2 whole band **1.16× (n=43)** and **1.09× (n=50)**, not
1.13×/1.06×; M2 count≥1000 **33.7×**, not 26.3×; M3 matched-parameter
**18.7×**, not 14.6×. Every model moves by the same factor so no comparison
changes — and by §2.5 none of it matters. It is recorded because
`DEC-20260803-3bba92` carries the 1.06–1.13× figures forward as if they were
measurements.

One further, separate defect in D-1's transfer: the correction factor is
derived under the **delta-method** covariance min(1/λ,1/λ′) and then applied to
the **truncated-Poisson** floor. Those two floors differ by +20 % on the whole
band (0.409366 vs 0.340570) precisely because of the low-λ rows that dominate
the correction. The transfer is safe at count≥1000 (0.014620 vs 0.014627) and
is unverified on the whole band, which is where it is used.

### 2.7 The yardstick is not calibrated where 99.9 % of it lives

Every model tested sits **16 % to 42 % below** the counting floor on the
C<1000 rows (§2.2: 0.581×–0.837×). D-1 accounts for ~10 % of that at most
(§2.6); the plug-in-λ smoothing test accounts for ≤0.44 % and has the wrong
sign (validator D-8). The remainder is unexplained, and it is not a curiosity:
it is the region supplying 99.91 % of the floor variance that the headline
divides by.

Two named, unclosed candidates, both recorded as limitations by the validator
and neither quantified anywhere in the lane:

1. **Deep-tail dispersion.** The validator's leverage-corrected φ test covers
   T ∈ [150, 1400] only, and it explicitly says it is "UNTESTED in the deep
   tail, where the whole-band statistic gets most of its weight". I attempted
   it twice in this session and **neither attempt settles it**, which I record
   rather than pass off: a local unweighted quadratic detrend on 51-row blocks
   gives φ = 0.68–0.81 (n=43) and 0.20–0.65 (n=50), but unweighted OLS overfits
   sparse counts and biases φ *down*; a global log-linear Poisson trend on
   16/24/40-row windows gives φ = 1.27–1.54 and 1.82–2.72, but a log-linear
   rate underfits a rate falling by three orders over the sub-band and biases φ
   *up*. The two attempts bracket the answer uselessly. **The control has still
   not been run.**
2. **Band-truncation selection.** The band ends at the last positive score, so
   the deepest rows enter conditional on an upward fluctuation. The floor
   conditions per-row on C ≥ 1, which is not the same event. Nobody has
   quantified the difference; RT-12 and the validator both record the gap.

Until one of these is closed, no absolute reading of the whole-band ratio is
interpretable in either direction — including a reading that would *favour* the
package.

---

## 3. Three further objections, smaller but checkable

### 3.1 A parameter-free misfit that the P-2 sentence conceals

`EV-MLKEM-553b83` P-2 says the whole-band misfit "really was a property of the
SURROGATE, not of Approximation 4.9's region measure".
`DEC-20260803-3bba92` central_adjudication says "It does not [misfit]. A
Gaussian-Φ surrogate does." Both are too strong, and the producer's own
`results.json` refutes them:

| T | pooled count C | M2 residual (bits) | delta counting sd (bits) | significance |
|---|---|---|---|---|
| 270 | 516 917 328 | **+0.46669** | 6.35·10⁻⁵ | **≈ 7350 σ** |
| 405 | 12 624 958 | **+0.54764** | 4.06·10⁻⁴ | **≈ 1348 σ** |

and the measured leverage `d ln Pred / d ln A` at those scores is 0.10–0.20, so
removing +0.55 bits at T = 405 would require δ log₂A ≈ 2.7 bits, which would
displace every T ≥ 800 row by 2.7 bits. **The discrepancy is not absorbable by
the one free parameter.** Approximation 4.9's exact region measure is
measurably wrong on this archive, in the best-measured part of the band, at a
level that no floor-protocol argument touches.

P-4 and P-5 already record the aggregate of this (23.9×, S-shaped, lag-1
autocorrelation 0.99907), and they are correct and are strengthened here. What
must not stand is the unqualified sentence. The honest form is: *the deep-tail
component of the whole-band misfit was the surrogate's; the well-measured
component is shared, and under the exact measure it is 23.9× the floor.*

Check: `results.json → files[0].results.M2_residual_profile_whole_band_fit`,
entries T = 270 and T = 405; counts are in the same records.

### 3.2 Scope inflation in the decision, not in the evidence

`DEC-20260803-3bba92`: "For three batches this goal reported that Approximation
4.9's family misfits the archived whole-band data. It does not."

`EV-MLKEM-2e668d` (BATCH-011) had already struck both halves of that:

* **C-1**: "the whole-band excess is only 1.25x and 1.30x the floor, which is a
  weak basis for any misspecification claim. **THAT ARGUMENT IS STRUCK.**"
* **C-3**: "What BATCH-009 and BATCH-010 fitted is **NOT** Approximation 4.9's
  family. It is BATCH-009's **GAUSSIAN-Φ SURROGATE**."

So the record BATCH-012 corrected consists of one argument already struck and
one attribution already corrected, both one batch earlier. BATCH-012's genuine
addition — the first instantiation of the object, and the demonstration that it
beats the surrogate at matched parameter count — is a real and sufficient
result. It does not need, and is weakened by, the larger frame. The evidence
record's own `relation_to_prior_records` states the narrower version correctly;
the decision's `central_adjudication` does not.

Check: `ledger/evidence/EV-MLKEM-2e668d.yaml`, observations C-1 and C-3,
verbatim.

### 3.3 "Selects its null value EXACTLY" is a grid statement

The producer's s-grid (step 0.07) does not contain 1.00; the validator's (step
0.05) does, and its neighbours are 0.95 and 1.05. "Exactly" is not resolvable on
either. The three-point parabolas (§1.6) put the continuous vertex at
s* = 0.9975 (n=43) and 1.0020 (n=50), buying 1.6·10⁻⁴ bits. The `c` grid for
`F(A·G·v^c)` is not published, and its two reported argmins (0.0 and −2.0)
suggest integer steps. **The claim is true in substance and over-stated in
word**: the right form is "within one grid cell of its null value, buying
≤ 2·10⁻⁴ bits". Cheapest check: golden-section on s and on c instead of a grid,
reporting the vertex and the curvature.

---

## 4. The four claims the validator could not reach (Job 2)

All four are answered by independent recomputation in this session. None
required new sampling.

### 4.1 n=50's M1 whole-band argmin — **ANSWERED: reproduced, and interior**

Wide scan p = 8 … 32 on my own implementation:

```
p=  8 2.621374   10 2.327099   12 2.024095   14 1.709478   16 1.377236
p= 18 1.023530   20 0.666586   21 0.515408   22 0.431099
p= 22.25 0.427413  <-- ARGMIN
p= 23 0.464680   24 0.603895   26 1.020423   28 1.496541   30 1.988850   32 2.483071
```

**0.427413 @ p = 22.25** against the producer's 0.427416 @ p = 22.25 — agreement
to 3·10⁻⁶ bits, and the optimum is **genuinely interior** (p=22 → 0.431099,
p=23 → 0.464680). The 1.30× n=50 whole-band surrogate baseline stands.

I also settled two n=50 sub-bands the validator did not scan:

* **count≥1000**: argmin **p = 20.00, rms 0.376293 (24.77×)**, interior (p=19 →
  0.404347, p=21 → 0.407081), against the producer's 0.376295. **Claim 2's n=50
  surrogate baseline (24.8×) is now independently confirmed as a genuine
  interior optimum**, which the validator had established for n=43 only.
* **count≥1e5**: argmin **p = 16.00, rms 0.188832 (139.1×)**, against the
  producer's grid-edge value 0.295562 @ p = 18.5 (217.8×). **Defect D-2's n=50
  leg is now measured rather than expected**: the validator wrote "the n=50
  count≥1e5 argmin is also at its grid edge (p=18.5) and is expected to behave
  the same way, though I did not scan it". It does. So the n=50 count≥1e5 row of
  tables 3.2 and 3.4 ("218× → 125×") must be struck alongside the n=43 row: 125×
  against ≤139× is a tie, not a reduction.

### 4.2 n=50's M3 s-curve — **ANSWERED: reproduced, and the published argmin is grid-limited**

Every producer grid point reproduced (producer's value in brackets):

```
whole    s=0.90 0.600372 [0.6003741]  0.97 0.357642 [0.3576660]
         s=1.00 0.317174               1.04 0.374127 [0.3741881]
ge1000   s=0.90 0.310099 [0.3101151]  0.97 0.305598 [0.3056651]
         s=1.00 0.355621               1.04 0.454574 [0.4546702]
```

New point, off the producer's 0.07 grid:

```
whole    s=0.94 0.447535
ge1000   s=0.94 0.285907   <-- better than the published argmin
```

The whole-band argmin s = 1.00 is confirmed with a tighter bracket. But the
**count≥1000 argmin is grid-limited**: the published matched-parameter figure
for n=50 is 0.305665 (20.12×) at s = 0.97, and s = 0.94 already reaches
**0.285907 (18.82×)**. So P-4's "20.1×" is an upper bound and the correct
matched-parameter value is ≤ 18.8×. This is the same class of defect as D-2 and
it points the *other* way — it makes the matched-parameter comparison
(24.8× → ≤18.8×) more favourable to the exact model than published. It is
recorded for accuracy, not as an attack. The analogous n=43 parabola vertex sits
at s ≈ 0.883, giving ≈ 12.97× rather than the published 13.23×.

### 4.3 n=50's slope row — **ANSWERED: reproduced to every printed digit**

```
v=3:22.92  5:21.57  6:20.76  7:19.83  8:18.77  9:17.88  10:18.71  11:22.83  12:27.15
```

by an implementation that shares no code and no evaluation route with the
producer's (Poisson integral for Υ; monotone-segment inversion for the region;
different η quadrature). Υ_{20.5} first zero 25.955681, matching. The
v-dependent slope, its descent to 17.88 and its non-monotone turn back up at
v ≈ 11 as the second (negative × negative) lobe pair activates, are real for
n=50 as well as n=43. RT-9's mechanism is confirmed a third time.

### 4.4 The ANOM-7 ψ_lsc sensitivity variant — **ANSWERED, both files; see §2.4**

```
n=43  whole  0.322071 [0.322072]   ge10  0.283815 [0.283812]
      ge1000 0.354773 [0.354771]   ge1e5 0.206078 [0.206078]
      ln_A  -119.30967 [-119.3096973737681]
n=50  whole  0.306416 [0.3064170322]  ge10  0.278489 [0.2784880434]
      ge1000 0.359358 [0.3593558528]  ge1e5 0.441210 [0.4412081927]
      ln_A  -107.74405 [-107.7440788952]
```

All eight cells reproduced to 10⁻⁶ bits and both `ln A` to six decimals. The
producer's stated conclusion — *the count≥1000 verdict is unchanged under either
reading* — **holds**: 23.9× → 24.3× (n=43) and 23.9× → 23.9× (n=50). But the
variant is far more consequential than ANOM-7 presents it, for the reason in
§2.4: it moves the whole-band headline by 9.4 % / 3.4 % in the favourable
direction with no improvement at all on the measurable rows, and it is the
cleanest available demonstration that the whole-band statistic is measuring the
tail rather than the fit.

---

## 5. Attacks I ran that FAILED to break the finding

Recorded so nobody re-runs them.

1. **"One fitted scale rescues any monotone shape."** Refuted — §1.4. Generic
   one-parameter monotone families score 4.9×–57×.
2. **"The improvement is a deep-tail artifact."** Refuted — §2.2. 98.6 % (n=43)
   and 90.8 % (n=50) of the matched-parameter improvement, and 77.7 % (n=43) of
   the improvement over the two-parameter surrogate, lands on the C≥1000 rows.
3. **"The exponent is frozen only after a modelling choice that could have gone
   otherwise (β_sieve = beta_1 vs beta_0)."** Refuted — §1.5. The source's own
   Fig 4.1 caption fixes β_sieve = 44 / 41.
4. **"The second-parameter null selection is a flat likelihood."** Refuted —
   §1.6. Curvature 25.9 / 39.6 bits per unit².
5. **"ANOM-1's node-ordering assumption survives elsewhere."** Not found. I read
   the producer's `build_u_nodes` / `build_kernel` / `predict`: the fix sorts
   globally in u, the kept set `{|T−u| < sqrt(120N)}` is then an interval, and
   the assertion `elif j != prev + 1: raise` fires inside the row-building loop
   for every score and cannot be vacuous. My own implementation carries the
   identical contiguity assertion, with a different node layout and a different
   kernel cut, and it never fired while reproducing every M2 cell. There is no
   second slice-addressed structure in the script: `region_measure` and the
   mixture `F` do not index across nodes.
6. **"The numbers do not reproduce."** Refuted at every point I could reach —
   §1.1–§1.3, §4.

---

## 6. What the finding is entitled to claim

**Entitled:**

* The exact region measure implied by (4.10)/(4.11)/(4.24), instantiated with
  **one fitted normalisation and no fitted exponent**, fits the two archived
  toy files strictly and substantially better than BATCH-009's Gaussian-Φ
  surrogate: whole-band log₂ rms **0.3556 vs 0.7055** (n=43) and
  **0.3172 vs 0.6969** (n=50) at matched parameter count, and vs
  **0.4271 / 0.4274** at the surrogate's two-parameter best.
* **91–99 % of the matched-parameter improvement is contributed by rows with
  pooled count ≥ 1000**, where the counting floor is 0.0146/0.0152 bits and
  therefore negligible; the improvement is independent of every floor-protocol
  question.
* On the well-measured sub-band, the exact measure reduces the misfit from
  **64.7×/60.5×** (surrogate, matched 1 parameter) to **23.9×/23.9×** the
  counting floor. It does **not** close it, and at matched *two* parameters the
  surrogate's own best (16.5×/24.8×) is comparable.
* Two structurally different second parameters buy ≤ 2·10⁻⁴ bits on the whole
  band; the exponent is a derived quantity fixed by the source's own
  β_sieve = 44/41 (verified against page 26 of the archived extracts).
* The attribution correction stands: what BATCH-009 and BATCH-010 fitted was a
  surrogate. (First recorded in BATCH-011 as C-3; confirmed positively here.)

**Not entitled:**

* Any absolute statement about where the whole band sits relative to the
  counting floor — "1.06–1.13×", "at the floor", "CLOSED", "below its floor",
  "consistent with the counting floor to within the floor's own protocol
  correction". The statistic has ≈1.5 effective degrees of freedom, a sampling
  sd of ~57 %, a denominator supplied 99.91 % by rows that do not discriminate,
  and a 9.4 % sensitivity to an undetermined modelling choice that simultaneously
  degrades the measurable fit.
* "The whole-band misfit was a property of the surrogate, not of Approximation
  4.9's region measure", unqualified. The exact measure misfits by +0.55 bits at
  T = 405 at ≈1348 σ, unabsorbably.
* "Corrects three batches of this program's own work." One argument and one
  attribution, both already corrected in BATCH-011.
* Anything about ML-KEM or Kyber security in either direction, about Carrier et
  al.'s cost figures, or about Table 5.1. Nothing here touches them.

**Baseline comparison.** `dominated_by: null` with basis "no attack advanced, no
cost frontier occupied" is checked and correct: this package occupies no time,
memory or data/query axis, advances no algorithm, and claims no security-bit
reduction, so there is no frontier row to compare against and `null` is not a
fabrication under AGENTS rule 5. `sota_delta: zero` is likewise correct. There
is no Pollard-rho / BSGS / specialized-baseline comparison to make, because no
attack is claimed; recording that explicitly rather than omitting it.

---

## 7. Boundaries of this review

* Two archived toy files, resolved band only (scores 0–1802 and 0–2309), raw
  undivided score scale. RT-11 stands: the band reaches ~15 % of the operating
  threshold, so no region in this archive is the security-relevant region.
* Everything I recomputed is a goodness-of-fit statistic on archived counts. I
  advance no mechanism for the S-shaped residual and no claim about
  Approximation 4.9's correctness at any other parameter set.
* One session, one reviewer. My implementations agree with the producer's and
  the validator's; agreement of three implementations is not proof that a shared
  premise (e.g. the (4.22) → R1/R2 reduction, which I verified algebraically but
  did not re-derive from the PDF in this session) is right.
* My deep-tail dispersion attempts are inconclusive **by construction** and are
  reported as such, not as evidence in either direction.
* `dominated_by`: n/a — no attack advanced, no cost frontier occupied.
  `sota_delta`: zero.
