# TASK-20260803-e9709a — validation notes

Validator session, GOAL-MLKEM-003 BATCH-010. Report:
`validation_report.yaml` (same directory). Verdict: **ADMISSIBLE_WITH_DEFECTS**.

Package under review: Coordinator snapshot commit
`be7ed9e36426517d91e7bb0206e01e52463ddbaf` (TASK-20260803-408684), carrying the
TASK-20260803-f95b4e producer package.

**Toy tier. No ML-KEM or Kyber security claim in either direction. AGENTS.md
rule 12 UNMET and UNWAIVED — `EV-MLKEM-011`, `EV-MLKEM-013`, `EV-MLKEM-017` keep
their status. ZERO NEW SAMPLING: only archived `.out` bytes and archived Carrier
text extracts were read; no network, no G6K, no Monte-Carlo.**

I did not commit anything, did not edit any producer artifact, and wrote only
the two declared deliverable paths.

---

## 1. Snapshot and artifact binding

```
git show --name-status be7ed9e36426517d91e7bb0206e01e52463ddbaf
git merge-base --is-ancestor be7ed9e3 HEAD      # reachable
```

* parent = `9b6b6ee8f83fb726ac366ba9b33b53d231044dea`, which is exactly the
  commit `report.md` declares as "repository commit at execution".
* Adds exactly five paths: the four declared artifacts plus
  `.../BATCH-010/archives/TASK-20260803-408684/snapshot_receipt.json`.
* Each of the four artifact blobs in the commit is byte-identical (sha256) to
  the working tree. `git status --porcelain` is empty.

Input hashes recomputed here with `sha256sum`:

| file | sha256 | matches package |
|---|---|---|
| `Pwrong_...n43...N25971.out` | `50bd293c…f90bb` | yes |
| `Pwrong_...n50...N25970.out` | `ce23181d…9ab459` | yes |

---

## 2. Model re-derivation (done before reading the producer's code)

From archived (4.22)/(4.27)–(4.29) and Model 4.7, with
`S(u) = P(D>u) = min(1, K (ln(N/u))^p)` on `0<u<N`:

```
Pwrong(T) = E[Q(T-D)] = Q(T) + INT_0^N S(u) phi(T-u) du
          = Q(T-u*) + K * INT_{u*}^{N} phi(T-u) (ln(N/u))^p du ,
u*  = N exp(-K^{-1/p}) ,  Q(x) = 0.5 erfc(x/sqrt N) ,
phi(s) = exp(-s^2/N)/sqrt(pi N)
```

Integration by parts turns this into the BATCH-009 statement
`Q(T) + INT_0^inf N e^{-v} phi(T-Ne^{-v}) min(1,K v^p) dv` exactly, so both
implementations compute the same object.

**My implementation is independent of the producer's**: I integrate in `u`
(they integrate in `v = ln(N/u)`), with my own panel layout (geometric near
`u*`, then two linear regimes), my own hand-rolled Gauss–Legendre rule (no
numpy/scipy available — confirmed in this session), and a golden-section search
on `u*` rather than their incremental `v*` sweep. No value was ever taken from
`results.json` into a computation.

Scratch files (session scratchpad, not repository artifacts):
`mymodel.py`, `fitscan.py`, `conv.py`, `subband.py`, `checkB.py`, `checkB2.py`,
`identcontrol.py`.

### Convergence

```
order= 8 cut=60 p=23.25 log2K=-67.971277 rms=0.425714144
order=12 cut=60 p=23.25 log2K=-67.971277 rms=0.425714144
order=16 cut=90 p=23.25 log2K=-67.971277 rms=0.425714144
fine panels (ratio 1.05 / step 3 / step 20)  rms=0.425714144
```
Identical to 9 decimals across four settings, and the same at `p=26.00`
(`0.705493537`). Quadrature is not in question.

---

## 3. Instrument checks

```
n43 lastpos 1802  val[1802]=1.7860305406935986e-11 == 1/(4000*241^3) exactly
    log2 floor = -35.70445229335197   first zero 1803
    max rel dev from integer multiple of the quantum: 2.2143e-16
n50 lastpos 2309  val[2309]=1.1906870271290657e-11 == 1/(6000*241^3) exactly
    log2 floor = -36.28941479407313   first zero 2310
    max rel dev: 2.2185e-16
own p = (beta_1+n_fft)/2 = 26.0 (n43), 24.5 (n50)
count>=10 sub-band sizes: 1493 (n43), 1969 (n50)
```
All reproduce the package and EV-MLKEM-019 O-1/O-2.

**Positive control (parameter-free `Q(T)`), n=43, raw score scale:**

```
T=  0 diff=+0.00288   T=200 diff=-0.01570   T=322 diff=-0.09982
T=100 diff=+0.00231   T=400 diff=-0.23676   T=471 diff=-0.51114
```
`Q(T)` alone tracks within 0.1 bit through score 322 — re-confirming O-3 and
excluding a silent `k_fft = 3` factor-of-three slip.

---

## 4. CHECK A — recomputed from the archived bytes

Both files, `p` over own ± 6.0 in steps of 0.25 (49 points), `K` profiled on the
whole resolved band at every `p`, rms of `log2 pred − log2 measured` over the
whole band.

### n = 43 (own `p` = 26.0) — my values

```
  p      log2K       rms          p      log2K       rms
20.00  -62.46876  0.706561     24.50  -70.11736  0.496543  (n50's p)
21.00  -64.14975  0.582234     25.00  -70.97997  0.555266
22.00  -65.84142  0.479670     26.00  -72.71162  0.705494  <- own p
22.50  -66.69134  0.444954     27.00  -74.45081  0.882887
23.00  -67.54397  0.427120     28.00  -76.19628  1.075950
23.25  -67.97128  0.425714 <-argmin  30.00  -79.70126  1.487293
23.50  -68.39924  0.429662     32.00  -83.21798  1.914706
24.00  -69.25707  0.453471
```

### n = 50 (own `p` = 24.5) — my values

```
18.50  -57.52031  0.932809     22.50  -63.94902  0.431911
19.50  -59.11112  0.752912     23.00  -64.76393  0.464683
20.50  -60.71307  0.585994     23.50  -65.58085  0.524423
21.50  -62.32599  0.461140     24.50  -67.21992  0.696881  <- own p
21.75  -62.73084  0.442593     25.50  -68.86463  0.907507
22.00  -63.13631  0.431098     26.00  -69.68861  1.020420  (n43's p)
22.25  -63.54238  0.427412 <-argmin  28.00  -72.99141  1.496546
                              30.50  -77.12480  2.112545
```

### Agreement with the producer

| quantity | producer | mine | Δ |
|---|---|---|---|
| n43 rms at own p | 0.705494 | 0.705494 | <1e-6 |
| n43 argmin p / rms | 23.25 / 0.425715 | 23.25 / 0.425714 | 1e-6 |
| n43 excess | +0.279779 | +0.279780 | 1e-6 |
| n50 rms at own p | 0.696881 | 0.696881 | <1e-6 |
| n50 argmin p / rms | 22.25 / 0.427413 | 22.25 / 0.427412 | 1e-6 |
| n50 excess | +0.269468 | +0.269469 | 1e-6 |
| n43 log2K at argmin | −67.97057 | −67.97128 | 7.1e-4 |
| n50 log2K at argmin | −63.54163 | −63.54238 | 7.5e-4 |
| n43 under p=24.5 | 0.496543 | 0.496543 | — |
| n50 under p=26.0 | 1.020420 | 1.020420 | — |
| cross-check rms at archived (p, K_fit) | 0.7054940 / 0.6968845 | 0.7054940 / 0.6968845 | — |
| peak delta | +1.5154077 @471 / +1.7108564 @420 | +1.515408 / +1.710856 | — |
| clipped fraction at peak | 0.376547 / 0.377878 | 0.376547 / 0.377878 | — |

The `log2 K` gaps sit inside the producer's declared ~0.002-bit fit resolution
(DEP-A2) and move the rms by <1e-6 bits.

**Both curves are strictly unimodal** on their 49-point grids (monotone down to
the argmin, monotone up after it — verified point by point, no plateau, no
second minimum), and **both argmins are interior** (13 and 15 grid steps from
the nearest edge). "Smooth, single-minimum, not scan-width limited" reproduces.

### `log2 K` linearity

Full-grid slope **−1.72910** bits per unit `p` (n=43) and **−1.63376** (n=50);
local slope near the n=50 own exponent −1.642, which is the "−1.65" the report
quotes. Maximum departure from a straight line over the 49 points: 0.135 bits
(n=43), 0.110 bits (n=50), against a ~20-bit span. So "essentially linearly"
is accurate.

**But the inference drawn from it is not valid** (defect D3). `K ≈ v_eff^{-p}`
makes `log2 K ≈ −p log2 v_eff` by construction, so linearity would hold whether
or not the free scale absorbed the exponent change. What actually establishes
non-absorption is that `K` is profiled out at every `p` and the profiled rms is
still strongly non-flat — plus the control in §5.

---

## 5. CHECK A — controls I added

### C-3 identifiability / null-object control (deterministic, no sampling)

Replace the measured curve by the **model's own noiseless prediction** at the
file's archived `(p, K̄)` and rerun the identical scan.

```
n43 synthetic at p=26.00, log2K=-72.712581
    p=23.25 rms=0.53533943   p=23.75 rms=0.44257276
    p=26.00 rms=0.00000000  log2K recovered -72.712581
    ARGMIN p=26.00
n50 synthetic at p=24.50, log2K=-67.222505
    p=21.75 rms=0.65093372   p=22.25 rms=0.53668009
    p=24.50 rms=0.00000000  log2K recovered -67.222505
    ARGMIN p=24.50
```

**Passes exactly.** The estimator is unbiased on noiseless data of the same
shape, so the observed displacement is not an artifact of the fit protocol, the
band weighting, or the free scale.

**Second reading of the same control, and it matters.** A 2.75 displacement
costs 0.535 bits of rms on noiseless model data. On the real data the excess at
the own exponent is only **0.280** bits and the **best achievable rms is 0.426
bits, not zero**. The one-free-parameter family therefore fits at *no* exponent
in the window. The honest statement is "misspecified family whose least-bad
member sits below the archived exponent", not "a neighbouring exponent is the
right one". The package does not draw this distinction.

### C-4 band-weighting robustness (six weightings; the package reports one)

`K` profiled and rms reported on the **same** index set, own ± 6.0 step 0.25.

**n = 43 (own 26.00)**

| weighting | n | argmin p | rms at argmin | rms at own p | excess | argmin − own |
|---|---|---|---|---|---|---|
| whole band | 1803 | 23.25 | 0.425714 | 0.705494 | +0.279779 | −2.75 |
| count ≥ 10 | 1493 | 22.25 | 0.343388 | 0.737757 | +0.394369 | −3.75 |
| count ≥ 100 | 1137 | 21.25 | 0.298181 | 0.780884 | +0.482704 | −4.75 |
| count ≥ 1000 | 852 | **20.00 (grid edge)** | 0.241883 | 0.810306 | +0.568423 | −6.00 |
| head T ≤ 600 | 601 | **20.00 (grid edge)** | 0.235951 | 0.436150 | +0.200198 | −6.00 |
| every 20th | 92 | 23.25 | 0.421465 | 0.695861 | +0.274397 | −2.75 |
| **tail T > 1000** | 802 | **26.25** | 0.265359 | 0.266295 | **+0.000935** | **+0.25** |

On a wider 0.5-step grid the tail argmin is **exactly 26.00, excess 0.000000**.

**n = 50 (own 24.50)**

| weighting | n | argmin p | rms at argmin | rms at own p | excess | argmin − own |
|---|---|---|---|---|---|---|
| whole band | 2310 | 22.25 | 0.427412 | 0.696881 | +0.269469 | −2.25 |
| count ≥ 10 | 1969 | 21.75 | 0.388690 | 0.725197 | +0.336507 | −2.75 |
| count ≥ 100 | 1525 | 21.00 | 0.392913 | 0.768676 | +0.375763 | −3.50 |
| count ≥ 1000 | 1132 | 20.00 | 0.376293 | 0.828760 | +0.452467 | −4.50 |
| head T ≤ 600 | 601 | **18.50 (grid edge)** | 0.302512 | 0.690234 | +0.387722 | −6.00 |
| every 20th | 117 | 22.25 | 0.436487 | 0.694367 | +0.257880 | −2.25 |
| tail T > 1000 | 1309 | 23.75 | 0.215598 | 0.243727 | +0.028129 | −0.75 |

**Noise scale for reading that table** — naive independent-trial sd of
`log2 P̂` = `1/(ln2·√count)` (an order of magnitude only; the counts are
strongly positively correlated across scores, so this overstates point-to-point
scatter and understates coherent level error):

```
n43: T=500 -> 0.0020   T=900 -> 0.0568   T=1000 -> 0.0878   T=1200 -> 0.1763
     T=1400 -> 0.3856  T=1492 -> 0.4562  T=1802 -> 1.4427
     tail T>1000: rms 0.6130 bits      count>=1000: rms 0.0146 bits
n50: tail T>1000: rms 0.4446 bits      count>=1000: rms 0.0152 bits
```

Reading: every **low-noise** weighting moves the argmin *further* below the own
exponent and *enlarges* the excess. The single weighting that reverses the
direction is the deep tail, whose counting uncertainty (0.61 / 0.44 bits) is
more than twice its residual rms (0.27 / 0.24) — it discriminates nothing. So
the weighting dependence does not undercut Check A; the whole-band protocol
understates it. The tail exception is nevertheless unreported by the package
(defect D5), and two of these weightings *are* scan-width limited, which
qualifies the package's blanket "neither is scan-width limited".

---

## 6. CHECK B — recomputed independently

Independent quadrature (composite Gauss–Legendre in `v` on `[0,25]`, step 0.005,
no exact-kink split — a different scheme from both the producer's and my own
Check-A code), `K̄` taken from the archived BATCH-009 fit and never refitted.

```
=== n43  T*=471  p=26.00  log2 Kbar=-72.71258147256952 (archived, held fixed) ===
  log2 P_out (exact kink)   = -13.744464   [smooth-quad cross-check -13.744464]
  log2 measured             = -15.259872
  over-prediction           = +1.515408 bits
  log2 Q(T*)                = -15.771008
  reading-free bound        : -2.026543 <= Delta <= 0
  R1: s=0 -> -0.000000 ; 0.20 -> -0.004348 ; 0.375 -> -0.015262 ; 0.50 -> -0.027089
      1.00 -> -0.107142 ; 2.00 -> -0.408648 ; 3.00 -> -0.842895 ; 4.00 -> -1.312032
      5.00 -> -1.698657 ; 8.00 -> -2.022313 ; 12.00 -> -2.026543 (bound)
  s required to absorb +1.515408 : s = 4.480840 nats = sd(log2 k) = 6.4645 bits
  R2 (a*mu^2): 0.100 -> -0.001234 ; 0.194756 (alpha=2) -> -0.004705 ;
      0.500 -> -0.031230 ; 1.000 -> -0.122719 ; 2.000 -> -0.434454 ; 3.000 -> -0.804446
  v*=6.948193  u*=24.941752  clipped fraction at 471 = 0.376547

=== n50  T*=420  p=24.50  log2 Kbar=-67.22250543726885 (archived, held fixed) ===
  log2 P_out               = -10.765140
  log2 measured            = -12.475996
  over-prediction          = +1.710856 bits
  log2 Q(T*)               = -13.098605
  reading-free bound       : -2.333466 <= Delta <= 0
  R1: 0 -> -0.000000 ; 0.20 -> -0.004676 ; 0.375 -> -0.016421 ; 0.50 -> -0.029157
      1.00 -> -0.115654 ; 2.00 -> -0.446635 ; 3.00 -> -0.942561 ; 4.00 -> -1.505296
      5.00 -> -1.971793 ; 8.00 -> -2.329641 ; 12.00 -> -2.333465 (bound)
  s required to absorb +1.710856 : s = 4.394843 nats = sd(log2 k) = 6.3404 bits
  R2: 0.193705 (alpha=2) -> -0.004614 ; 1.000 -> -0.124389 ; 3.000 -> -0.875745
  v*=6.698211  u*=32.024035  clipped fraction at 420 = 0.377878
```

**Every one of these matches the package to the printed precision**, from an
implementation that shares no code with it.

Derived percentages I recomputed: `0.004705/1.515408 = 0.3105 %` and
`0.004614/1.710856 = 0.2697 %` — the report's "0.31 %" and "0.27 %".
`alpha = 2` equivalent: `2·(π·μ_lsc/q)² = 0.194761` (n=43) and `0.193707`
(n=50), matching `results.json` to 5 decimals.

### 6.1 Is the `d_lsc` integral in the position (4.22) specifies?

**Yes.** Read directly from the archived extracts:

* `page23_approx_4_8_4_9.txt` (4.22): `INT_{-inf}^{+inf} INT_0^{+inf}
  min(1, INT_{E(T-t)} λ(x)μ(y) d(x,y)) · e^{-t²/N-(d_lsc-μ_lsc)²/2σ²} /
  (πσ_lsc√(2N)) dd_lsc dt` — the region integral is **inside** `min`, the
  `d_lsc` integral is **outside**.
* `page25_pwrong_validation.txt` (4.27)–(4.29) and the closing display
  `P(D>T) = INT ψ_lsc(d_lsc) P(D>T|d_lsc) dd_lsc` — same order.

The producer's `W(v) = E_d[min(1, k(d) v^p)]` is exactly that; BATCH-009's
`min(1, K̄ v^p)` is exactly the collapsed one. BATCH-009's own STEP 3 concedes
the collapse is exact only "in the unclipped regime", and the clipped fraction
at both peak scores is 0.377–0.378 — so it is not exact where it matters.

**Countervailing element the package omits (defect D7):** Model 4.7's (4.18)
*defines* `D = N ∫ψ_lsc(d_lsc) max_{i,j:N_{i,j}=1} Φ_{d_lsc}(i,j) dd_lsc`, with
the `d_lsc` integral **inside**, which also makes "the survival function of D
knowing `d_lsc`" in the (4.27) justification ill-typed. The source is internally
inconsistent on exactly the point Check B is about. This does not change the
sign or the bound; it changes how confidently the collapse is a defect of the
*implementation* rather than of the *source*.

### 6.2 Was `K̄` genuinely held fixed?

**Yes**, three ways:

1. **Code.** `jensen_bias_bound.py` assigns `Kbar` exactly once, at line 434,
   from the hard-coded constant `log2_K_fit_BATCH009`. There is no optimiser in
   the file; the only SSE accumulator (line 616) feeds the reporting-only
   `rms_whole_band_bits_with_Kbar_HELD_FIXED`.
2. **Arithmetic.** My independent `P_out` at the archived `K̄` matches their
   `log2 P_out` to 12 significant digits. A different scale could not do that.
3. **Structure.** `Δ(s=0) = 0` and `Δ(a=0) = 0` to 1e-13, which pins both
   branches to the same `K̄`. `E[k] = K̄` holds exactly for R1 (lognormal with
   the `−s²/2` correction — verified analytically) and to 1.7e-16 for R2.

### 6.3 Audit of the two-sided bound's provenance

The package says concavity gives only the **sign**, and the finite bound comes
from `P_in ≥ Q(T)`. **Both halves are correct.**

* *Sign.* `min(1,·)` is concave, so for any family with `E_d[k] = K̄`,
  `E_d[min(1, k v^p)] ≤ min(1, K̄ v^p)` pointwise in `v`, hence `P_in ≤ P_out`
  and `Δ ≤ 0`. Verified numerically at every scanned point of both readings.
* *Magnitude is NOT bounded by concavity.* With the mean fixed at `m`, take
  `Z = M` with probability `m/M` and `0` otherwise: `E[min(1,Z)] = m/M → 0` as
  `M → ∞`. So no bound on `|Δ|` follows from concavity at all.
* *Where the finite bound comes from.* `P_in(T) = Q(T) + ∫(nonneg) ≥ Q(T)`,
  therefore `Δ ≥ log2 Q(T*) − log2 P_out(T*)`. Recomputed:
  `−15.771008 + 13.744464 = −2.026543` and `−13.098605 + 10.765140 = −2.333466`.
  R1's saturation at exactly those values for `s ≥ 12` is the same statement
  from the other side.

This is the claim a reader could easily invert, and the package states it
correctly.

### 6.4 Is the Jensen bias large enough to account for the over-prediction?

**Not excluded, not supported, and reading-dependent with the reading
UNAVAILABLE.**

* **Reading-free:** yes arithmetically — `+1.515408 < 2.026543` and
  `+1.710856 < 2.333466`, so both over-predictions lie inside the bound and the
  collapse is not excluded on magnitude. But the bound is close to vacuous: it
  says only that the corrected model cannot fall below its own Gaussian floor,
  and that floor sits just 0.511 / 0.623 bits below the measurement. Saturating
  it needs `s ≥ 12` nats, i.e. the `D` component contributing essentially
  nothing at the peak.
* **Under R1** (the pure-scale dispersion family — which is, notably, the family
  BATCH-009's *own* STEP-2 multiplicative `Φ` implies): absorbing the whole
  over-prediction needs `s = 4.480840 / 4.394843` nats, `sd(log2 k) = 6.46 /
  6.34` bits — the effective normalisation swinging ~6.4 bits per standard
  deviation of `d_lsc`, on a variable whose own `μ/σ` is 7.08. Nothing in the
  archive suggests dispersion of that size.
* **Under R2** (the only reading the archived text motivates — (4.19)'s first
  factor is exactly `E_{d~N(μ,σ²)}[e^{-a d²}] = e^{-aμ²/(1+2aσ²)}/√(1+2aσ²)`
  with `a = απ²/q²`, verified analytically, so `Φ` does carry `e^{-a d_lsc²}`),
  at the only numerically archived candidate `α = 2`: **−0.004705 / −0.004614
  bits, i.e. 0.31 % / 0.27 %** of the over-predictions. Even at `a·μ² = 3`
  (`α ≈ 31`) it reaches only about half.

I also re-derived R2's shift consequence myself: with
`Φ_d(x,y) = exp(−a(x²+y²+d²))`, `E(u) = {x²+y² ≤ (L − a d²)/a}` and
`∫_E λμ ∝ (L − a d²)_+^{(β_sieve+n_fft)/2}` — a shift of `L` at the **same**
exponent `p`. The producer's DEP-B3 observation (BATCH-009's multiplicative
`Φ = exp(−(a x² + b(d_lsc) y²))` gives no `d_lsc` dependence at `y = 0`, so it
cannot reproduce (4.19)'s factor, whereas the shift reading can) is confirmed at
line 91 of the BATCH-009 script's docstring.

**Conclusion: the BATCH-009 headline over-prediction remains unattributed.**
The collapse cannot be ruled out as its cause, but nothing positively supports
it, and the one textually-motivated calibration accounts for about a
three-hundredth of it.

---

## 7. What I could not check

* **DEV-3 "each deliverable script executed exactly once."** Not checkable from
  the archive: no run counter, no execution identifier, and `results.json` is
  written twice by design (each script merges its own top-level key), so the
  committed bytes cannot witness the first write. Timestamps are *consistent*:
  Check A's `generated_at` 02:32:00Z minus 208.6 s starts ~02:28:31, after its
  script's 02:25 mtime; Check B's 02:35:44Z minus 18.9 s starts ~02:35:25, after
  its script's 02:31 mtime; `results.json` 02:36 and `report.md` 02:41 follow.
  Consistency is not verification. The substantive risk — a number not produced
  by the committed code — is retired separately by independent re-derivation.
* **DEV-3 "the probes produced none of the reported numbers."** Nothing outside
  the repository is visible here. Same substitution applies.
* **The producer's internal self-checks** (`K→∞` closed form 2.6e-15, panel
  halving 2.8e-14, R2 mean-match 5.5e-16, dropped outer weight 3.4e-17). I did
  not re-execute their scripts; my own convergence evidence supersedes them in
  substance but is not the same check.
* **Wall-clock and memory.** No independent timing receipt exists and my
  algorithm is different. **No memory measurement is recorded anywhere in the
  package**, only the `ulimit -v` cap that was applied.
* **Statistical significance of the Check A displacement.** The control that
  would settle it — resampling the survival curve under its counting model — is
  a simulation, forbidden by ZERO NEW SAMPLING. Read the 2.75 / 2.25
  displacement as a point estimate, not as a test.
* **Byte-level re-execution of the committed scripts.** Not done. My method
  catches errors in the mathematics; it would not catch a bug living only in the
  producer's I/O or bookkeeping.

## 8. On DEV-1

The absent `runs/<RUN-ID>/` tree is the handoff's fault and the Coordinator has
accepted that. But that explains only the missing *directory*. Assessing the
question actually asked — are the required provenance fields genuinely present
*inside* `results.json`? — the answer is **no**. Present: input sha256s, raw
headers, python/platform, numpy/scipy absence, `generated_at_utc`,
`wall_clock_seconds`, captured stdout, `zero_new_sampling`. Absent: git commit,
dirty-tree state, exact command, the whole `inference` block
(`requested_policy` / `resolved_model` / `fallback_used` / `model_verified` /
`reasoning_effort`), any determinism-or-seed statement, memory, stderr, validity
status and reason, and any run identifier. The first group exists as prose in
`report.md` only; memory, stderr and validity status exist nowhere. Nothing
about the four-path handoff prevented these from being carried inside the
declared JSON.

---

## 9. Bottom line

**Check A came back ONE-SIDED and ADVERSE to Approximation 4.9, and it survives
independent re-derivation.** Neither file's own archived exponent minimises rms
against its own data; both argmins lie below (by 2.75 and 2.25), the curves are
strictly unimodal with interior minima, and the estimator provably recovers a
known exponent on noiseless data of the same shape. Every low-noise sub-band
weighting pushes the argmin further below, so the finding is understated rather
than overstated by the whole-band protocol. Two qualifications the package does
not make: the best achievable rms is 0.426 bits, not 0, so the family is
misspecified at *every* exponent tested; and on the deep tail `T > 1000` the
n=43 own exponent *is* the argmin — in the one region too noisy to discriminate.

**Check B reproduces exactly, and its careful claim is correct.** Concavity
fixes the sign only; the finite two-sided bound genuinely comes from
`P_in ≥ Q(T)`; `K̄` is genuinely held fixed with no re-fit; the `d_lsc` integral
is genuinely evaluated in the position (4.22) specifies. Both over-predictions
lie inside the reading-free bound, so the collapse is not excluded — but that
bound is nearly vacuous, and under the only textually-motivated reading at the
only archived candidate `α` the bias is 0.31 % and 0.27 % of the effect.

**Verdict: ADMISSIBLE_WITH_DEFECTS** (D1–D8 in `validation_report.yaml`). None
of the defects changes a reported number. This report authorizes no promotion
and no status change, and bears on ML-KEM security in neither direction.
