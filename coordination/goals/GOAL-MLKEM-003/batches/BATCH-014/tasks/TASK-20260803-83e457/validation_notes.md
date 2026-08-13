# TASK-20260803-83e457 — validation notes: exactly what I recomputed

Validator, independent session. GOAL-MLKEM-003, BATCH-014, EXP-MLKEM-011.
Reviewing Coordinator snapshot commit `e95fe60d7e` (archive TASK-20260803-ea29ce),
which carries the TASK-20260803-f81a66 package.

**Scope of this document.** Observations and recomputations only. Nothing here
promotes, retires or interprets any record. Toy tier (q=241, m=40, n=43 and
n=50), resolved band only, raw undivided score scale. **No ML-KEM or Kyber
security claim in either direction.** AGENTS.md rule 12 stays UNMET and
UNWAIVED: EV-MLKEM-011, EV-MLKEM-013 and EV-MLKEM-017 keep their status;
KN-FIND-031 stays withdrawn.

**Zero new sampling of the physical system.** No G6K, no network, no new `.out`
bytes. The only randomness I generated is seeded pseudo-random draws used to
calibrate *my own* estimator against synthetic null objects (disclosed in §2.4
and §2.5, seed `424242`), which is the null-object obligation of
`docs/inventor-protocol.md` §3, not a resampling of the archive. Every measured
quantity below is a deterministic function of the archived bytes.

---

## 0. What I did, in one paragraph

I wrote my own instrument loader, my own aggregated-Poisson-GLM dispersion
machinery (B-spline basis, BIC model selection, my own bin-placement rule, my
own damped-Newton optimiser, my own Gaussian elimination, my own Poisson /
gamma-Poisson / binomial-thinning samplers, my own Monte-Carlo calibration) and
my own derivation of the effective degrees of freedom and the attenuation
identity from their stated definitions. I did not read the producer's code
until after my Job A and Job B numbers were on screen; I then read it to
diagnose the two places where my numbers and theirs disagree. I additionally
re-executed the producer's own script to a scratchpad output path and diffed it
against the archived `results.json`.

Scratchpad (not a deliverable, outside the repository):
`…/scratchpad/{vinstrument.py, vglm.py, vjobA.py, vmc.py, vjobB.py}`.

---

## 1. Artifact and provenance checks

```
sha256sum coordination/goals/GOAL-MLKEM-003/batches/BATCH-014/tasks/TASK-20260803-f81a66/*
```

| artifact | sha256 | matches `archives/TASK-20260803-ea29ce/snapshot_receipt.json` |
|---|---|---|
| `dispersion_control_c1.py` | `6cbd457d…4740a` | yes |
| `results.json` | `5d52d8f6…31584` | yes |
| `report.md` | `0e22b769…4a2086` | yes |

Commit `e95fe60d7e` has parent `766caa43a5…`, matching the receipt's
`parent_sha`; it changes exactly the four declared paths; the working tree is
clean on that subtree. `git log` shows the receipt commit `7d12b7d5` on top.

Input bytes:

```
sha256sum experiments/EXP-MLKEM-011/vendor-lock/data/Pwrong_q241_m40_n{43,50}*.out
50bd293cadf952516b092524c25f4404a1e4ca40983d1751286f96269dbf90bb  (n=43)
ce23181dca95a1c6a72463c2c39f14f645500a068b3af46c71d5b45af69ab459  (n=50)
```

both match `results.json → provenance.input_files`. The BATCH-012 read-only
input `…/BATCH-012/tasks/TASK-20260803-36f572/results.json` hashes to
`efd047fcb6c446df7b3b1857e0851afeff82bbed9030f82ab105f71e163dc6fe`, matching.

**Reproducibility pointer exercised, not asserted.** I re-ran the producer's
script with the output redirected outside its own directory (so no producer
artifact was touched):

```
python3 coordination/.../TASK-20260803-f81a66/dispersion_control_c1.py \
        --reps 300 --out <scratchpad>/rerun_results.json
```

exit 0, 216.0 s wall clock, peak RSS 0.0258 GB (recorded: 216.4 s, 0.0257 GB).
A recursive leaf-by-leaf diff of the rerun against the archived `results.json`,
excluding the `provenance` block, returns **0 differing leaves**. The package
is bit-reproducible from the committed script and the committed inputs.

DEV-1 (no `runs/` tree) and DEV-2 (seeded synthetic nulls) are as the
Coordinator described. I concur that DEV-2 is not a ZERO-NEW-SAMPLING breach; I
took the same deviation myself and disclose it.

---

## 2. Job A — my own construction

### 2.1 Instrument, recovered independently

```
python3 <scratchpad>/vinstrument.py
n43 M= 55990084000 band=[0,1802] n_scores= 1803 maxdev= 1.3604664602099005e-16
   sum(D) = 27939211089  C_0 = 27939211089  equal: True
   first T with C_T<1000: 852 C= 997 events in [lo,last]= 997 n_scores= 951
   first T with C_T<10:   1493 C= 9 rows= 310 events= 9
n50 M= 83985126000 band=[0,2309] n_scores= 2310 maxdev= 1.8152171959918973e-16
   sum(D) = 41845703221  C_0 = 41845703221  equal: True
   first T with C_T<1000: 1132 C= 993 events in [lo,last]= 993 n_scores= 1178
   first T with C_T<10:   1969 C= 9 rows= 341 events= 9
```

`M = nb_iteration · q^{k_fft}`, the integrality deviations, the resolved bands,
the region boundaries, the 997/993 pooled deep-tail events and the
**310 rows / 9 events** and **341 rows / 9 events** extreme tails all reproduce
exactly. ANOM-6 is confirmed: the `C_T < 10` region carries nine pooled events
per file and admits no dispersion statistic under any binning rule.

### 2.2 How my estimator differs from the producer's

| element | producer | this validation |
|---|---|---|
| rate basis | Chebyshev polynomial, log link | clamped **B-splines** (Cox–de Boor), degrees 1–3 with 0–4 interior knots |
| model selection | forward deviance test at χ²(1,0.95)=3.841 | **BIC** = deviance + p·ln K over a 9-model grid |
| bin placement | accumulate fitted rate to target, merge short bins into the **smaller neighbour**, iterate | accumulate fitted rate to target, merge the terminal short bin **backward**, iterate to a fixed point |
| bin target | 10 | swept over **10, 15, 20, 30** |
| optimiser | Fisher scoring + log-likelihood line search | damped Newton on the exact aggregated log-likelihood + backtracking |
| windows | 6–7 contiguous groups of equal *bin count* | 3, 4 and 5 **equal-event** windows |
| sd | analytic + own MC (seed 20260803) | analytic + own MC (**seed 424242**) |

The residual-variance identity is the same because it is forced: I re-derived
`Σ_j S_kj² μ_j = G_k^T I⁻¹ (Σ_j G_j G_j^T/μ_j) I⁻¹ G_k = G_k^T I⁻¹ G_k = h_kk μ_k`,
hence `Var(Y_k − μ̂_k) = μ_k(1 − h_kk)`. The producer's §2.1(c) algebra is
correct.

### 2.3 Primary reading — the deep tail, `C_T < 1000`

```
python3 <scratchpad>/vjobA.py n43 ; python3 <scratchpad>/vjobA.py n50
```

n=43, T∈[852,1802], 951 rows, 997 events:

| bin target | p=2 (linear) | p=3 (quadratic) | p=4 (cubic) | BIC pick | min exp | max leverage |
|---|---|---|---|---|---|---|
| 10 | 1.1171 | **0.9494** | 1.0022 | p=3 | 10.038 | 0.738 |
| 15 | 0.9762 | 0.9186 | 0.8450 | p=4 | 14.988 | 0.973 |
| 20 | 1.0283 | 0.8631 | 0.8270 | p=3 | 19.776 | 0.857 |
| 30 | 1.1501 | 0.9514 | 1.0323 | p=3 | 29.858 | 0.928 |

n=50, T∈[1132,2309], 1178 rows, 993 events:

| bin target | p=2 | p=3 | p=4 | BIC pick | min exp | max leverage |
|---|---|---|---|---|---|---|
| 10 | 1.2649 | **1.1229** | 1.1150 | p=4 (1.1150) | 10.002 | 0.792 |
| 15 | 1.2012 | 1.0787 | 1.0225 | p=4 | 15.012 | 0.955 |
| 20 | 1.4770 | 1.0603 | 1.3627 | p=3 | 20.075 | 0.922 |
| 30 | 1.3344 | 1.7978 | 1.3225 | p=2 | 30.053 | 0.492 |

Every model of order ≥ 5 fails to converge on the n=43 deep tail and most fail
on n=50 — independently reproducing ANOM-2's finding that this region cannot
support more than 3–4 parameters. That is a property of the data, not of either
implementation.

**Range: n=43 φ ∈ [0.827, 1.150]; n=50 φ ∈ [1.022, 1.798] across bin target ×
model order.** The producer's 0.895 / 1.062 sit inside both.

### 2.4 My own Monte-Carlo calibration (seed 424242, disclosed)

```
python3 <scratchpad>/vmc.py n43 400 200 ; python3 <scratchpad>/vmc.py n50 400 200
```

Null objects are per-row draws from my own fitted rate, pushed through my whole
pipeline (re-binned and refitted from the pilot each replicate).

| | n=43 (φ_obs = 0.9494) | n=50 (φ_obs = 1.1229) |
|---|---|---|
| MC Poisson null, mean ± sd (reps) | 0.9935 ± 0.1580 (391/400, 9 non-convergent) | 1.0143 ± 0.1674 (396/400, 4 non-convergent) |
| (φ_obs − null mean)/sd_MC | **−0.28** | **+0.65** |
| bias-corrected φ | 0.9556 | 1.1071 |
| estimator bias against its own null | −0.65 % | +1.4 % |

Producer, for comparison: MC-A 0.9850 ± 0.1542 (n=43) and 1.0022 ± 0.1665
(n=50); z = −0.58 and +0.36. Two independent implementations agree on the sd to
2–3 %.

### 2.5 Power, in both directions (the producer tested one)

Seeded alternatives of the same shape, 200 replicates each, pushed through my
whole pipeline. Over-dispersion by gamma-Poisson mixing; under-dispersion by
binomial thinning (`m = round(λ/(1−φ))`, `p = λ/m`, so `Var = φλ` exactly).

| alternative | n=43 recovered | n=43: φ_obs is | n=50 recovered | n=50: φ_obs is |
|---|---|---|---|---|
| φ_true = 0.60 | 0.6167 ± 0.1048 | **+3.18 sd** (excluded) | 0.6232 ± 0.0958 | **+5.22 sd** (excluded) |
| φ_true = 0.80 | 0.8126 ± 0.1326 | **+1.03 sd** (NOT excluded) | 0.8079 ± 0.1288 | +2.45 sd (excluded) |
| φ_true = 1.30 | 1.2943 ± 0.2086 | −1.65 sd (not excluded) | 1.2942 ± 0.1850 | −0.93 sd (not excluded) |
| φ_true = 1.50 | 1.5038 ± 0.2529 | −2.19 sd (excluded) | 1.5312 ± 0.2406 | **−1.69 sd (NOT excluded at 2 sd)** |

Producer's MC-C: 1.4586 ± 0.2365 (n=43) and 1.5209 ± 0.2468 (n=50). **The power
control reproduces**: the estimator recovers a seeded φ_true = 1.5 as ≈1.5 with
no attenuation, on a second, independently written implementation. So the null
really is informative and not empty.

Two qualifications that the report does not draw:

* the *exclusion* of φ = 1.5 is 2.4 sd for n=43 (producer's own numbers:
  (0.895−1.459)/0.237) but only **1.9 sd** for n=50 ((1.062−1.521)/0.247). On
  my construction, 2.19 sd and **1.69 sd**. "The test would have seen real
  over-dispersion" is a fair statement about n=43 and an over-statement about
  n=50 taken alone;
* the power control was run **only upward**. Downward, φ = 0.80 is 1.03 sd from
  n=43's own reading — not excluded. See §2.8.

The report's stated resolution ("true φ anywhere in roughly [0.6, 1.4] is not
excluded") is honest and, at the low end, slightly conservative: I measure
φ = 0.60 as excluded at 3.2 sd (n=43) and 5.2 sd (n=50). The genuinely
unexcluded band is about **[0.78, 1.40] for n=43** and **[0.85, 1.55] for n=50**.

### 2.6 My own windowing

Equal-**event** windows (the producer used equal-bin-count windows), from my
target-10 quadratic fit, analytic per-window sd:

```
n43, 3 windows: 0.910 (−0.30) | 0.860 (−0.50) | 1.058 (+0.18)
n43, 4 windows: 0.566 (−1.20) | 1.109 (+0.33) | 0.891 (−0.34) | 1.139 (+0.37)
n43, 5 windows: 0.621 (−0.92) | 1.290 (+0.76) | 0.591 (−1.15) | 1.215 (+0.62) | 0.974 (−0.06)
n50, 3 windows: 1.244 (+0.86) | 0.937 (−0.24) | 1.209 (+0.58)
n50, 4 windows: 1.202 (+0.61) | 0.949 (−0.16) | 1.061 (+0.21) | 1.280 (+0.63)
n50, 5 windows: 1.424 (+1.14) | 0.956 (−0.12) | 0.718 (−0.82) | 1.126 (+0.38) | 1.422 (+0.78)
```

**No window in either file, at any of my three windowings, departs from 1.0 by
more than 1.20 of its own standard deviation.** The window-level statement in
the report survives a different analyst's windowing (and my worst case, 1.20, is
milder than the report's 1.6).

Two smaller notes on the report's window table: the sign of the departure does
**not** alternate (n=43 reads −,+,−,−,+,−; n=50 reads +,−,−,−,+,+,−), and the
"sd" column there is the **analytic** sd, which ANOM-3 itself says is the one
not to read.

### 2.7 Controls I re-ran

| control | producer n=43 / n=50 | mine n=43 / n=50 |
|---|---|---|
| Σ leverage = #parameters | 3.0000000 / 3.0000000 | **3.0000000000 / 3.0000000000** |
| min *fitted* expected count | 10.026 / 10.003 | **10.038 / 10.005** |
| plug-in λ = own count | 0.000 / 0.000 | **0.0000000000 / 0.0000000000** |
| no leverage, Pearson/K | 0.858 / 1.031 | 0.9209 / 1.0913 |
| no leverage, Pearson/(K−P) | 0.891 / 1.068 | 0.9559 / 1.1303 |
| trimmed to leverage ≤ 0.5 | 0.888 (−0.007) / 1.073 (+0.011) | 0.9611 (+0.0117) / 1.1355 (+0.0126) |
| greedy **observed**-count binning | 0.9270 / 1.2200 | **0.9270 / 1.2198** |

Three things follow.

1. **The observed-count-binning control agrees to four decimals between the two
   implementations** (0.9270 vs 0.92698; 1.2198 vs 1.2200). That is expected and
   useful: observed-count binning fixes the bin edges from the data alone, and a
   degree-2 B-spline with no interior knots spans the same quadratic space as a
   Chebyshev degree-2 fit, so the two codes must agree there. It cross-validates
   both implementations, and it isolates the remaining difference between my
   0.9494 and the producer's 0.8954 to **bin placement alone**. Two defensible
   implementations of the *same stated* expected-count rule move φ by 0.054
   (n=43) and 0.061 (n=50), about a third of a standard deviation. ANOM-4's
   substance — the binning rule is a live analysis choice at this resolution —
   is confirmed; its *direction* is not a rule (the observed-count shift is
   **down** for n=43 on my construction and up on the producer's).
2. **`Σ h = #parameters` is an algebraic identity, not a check.**
   `Σ_k h_kk = tr(I⁻¹ Σ_k G_k G_k^T/μ_k) = tr(I⁻¹ I) = p` holds at *any* β,
   converged or not. It is listed in the report's control table as though it
   diagnosed something. Likewise `expected_count_ge_10_holds` is true by
   construction of the binning rule (edges are placed by accumulating the fitted
   rate until it crosses 10, then short bins are merged). Neither is wrong;
   neither is evidence.
3. **The plug-in control is a tautology.** The code is

   ```python
   lamb = float(b["Y"])                       # line 772
   plug.append(((b["Y"] - lamb) ** 2) / lamb) # line 774
   ```

   The numerator is `(Y − Y)²`. It is identically zero for any input, and no
   archived byte enters it. "Leverage exactly 1" is asserted in the adjacent
   note and never computed. It is also not `λ = C_T`: `b["Y"]` is the bin's own
   *increment* count, not the cumulative tail count. The producer's report
   presents it correctly as a demonstrated failure mode; the Coordinator's
   snapshot headline promotes it to "the construction the earlier attempts
   leaned on cannot produce a dispersion reading at all, in either direction",
   and **that does not follow**. The two S-11 attempts
   (`BATCH-013/tasks/TASK-20260803-b214b1/objections.md` §2.7) were (i) a local
   unweighted quadratic detrend on 51-row blocks and (ii) a global log-linear
   Poisson trend on 16/24/40-row windows. Neither is a plug-in; both fit a
   trend and both returned non-zero φ. The plug-in control says nothing about
   either.

### 2.8 The reading that bounds Claim A

n=43's deep tail does not exclude φ = 0.80 (1.03 sd). §3 below measures
φ = 0.802 in n=43's mid band at −2.36 sd against a null object of the same
shape. So the deep-tail result is correctly stated as *consistent with Poisson
at ±0.16*, and it is simultaneously **consistent with the exact departure the
same instrument resolves 300 rows shallower in the same file**. That is not a
contradiction and it does not defeat Claim A; it is the size of the claim.

---

## 3. ANOM-5, assessed with my own null-object control

Mid band (`1000 ≤ C_T < 1e5`), one bin per row (every row already carries ≥10
expected events), B-spline rate models from p=2 to p=33:

```
n43 [551,851], 301 rows, 98419 events
   p= 4  phi=0.9067   p= 6  phi=0.8101   p= 8  phi=0.8032   p=10  phi=0.8020
   p=13  phi=0.8037   p=18  phi=0.7940   p=23  phi=0.7865   p=33  phi=0.8024
n50 [636,1131], 496 rows, 98230 events
   p= 4  phi=1.1082   p= 6  phi=1.0937   p= 8  phi=1.0916   p=10  phi=1.0945
   p=13  phi=1.0934   p=18  phi=1.0910   p=23  phi=1.0793   p=33  phi=1.0827
```

Null-object controls, 60 replicates each, seed 424242, same pipeline:

| | observed | Poisson null of the same shape | departure | seeded φ_true = 0.80 recovered as |
|---|---|---|---|---|
| n=43 mid band | 0.8020 | 0.9923 ± 0.0806 | **−2.36 sd** | 0.8020 ± 0.0665 |
| n=50 mid band | 1.0916 | 0.9924 ± 0.0639 | **+1.55 sd** | 0.8026 ± 0.0548 |

Producer's own null: 0.9952 ± 0.0843 (n=43, −2.29 sd) and 0.9804 ± 0.0667
(n=50, +1.89 sd).

**ANOM-5 is real, it is not an instrument artifact, and it is not a
rate-model artifact.** The estimator is unbiased on a null object of the same
shape (0.992 in both files), it recovers a seeded sub-Poisson alternative
exactly, and the n=43 reading is flat at 0.79–0.81 while the rate model is
given 6 → 33 parameters. Adding parameters can only *inflate* φ towards 1 by
absorbing misfit; a 20 % variance deficit that survives 33 spline parameters is
a variance deficit. The two archived files genuinely disagree about mid-band
dispersion, in opposite directions, at −2.4 sd and +1.6 sd.

It does not undercut Claim A directly — a different region, a different regime,
and 100× more events per row. It does bound Claim A, as §2.8 says, and it is
the single most interesting unexplained observation in this package. Note also
that n=50 reads over-dispersed in *every* measurable region (mid band +1.89,
shallow +1.54, C<1e5 +1.93 on the producer's own MC z-scores) while n=43 does
not: this looks like a file-level property, not a band-level one.

---

## 4. ANOM-3, assessed

Confirmed and, if anything, worse in my construction than in the producer's. My
analytic sd blew up to 1240.8, 4.5·10⁷ and 7.5·10¹² on fits whose maximum bin
leverage reached 1.0000; the producer records 1560 and 12415 in the `C < 1e5`
region. The mechanism is `1/(1−h)` in `Var(r²) = (2 + 1/μ)/(1−h)²` when a wide
terminal bin is essentially fitted by itself.

**Yes, the Monte-Carlo sd is the one to read throughout**, and I read it. Two
consequences the report does not carry through:

* the primary region's analytic sd (0.185, 0.178) *over*-states the sd relative
  to the MC value (0.154, 0.166), because the analytic form ignores the negative
  correlation the smoother induces between neighbouring residuals. So using it
  is conservative there — but it is used, unlabelled, in the per-window tables
  in §2.2 of the report, whose "(φ−1)/sd" column is therefore computed with the
  quantity ANOM-3 declares unstable. The headline "no window departs by more
  than 1.6 sd" inherits that. If the per-window MC/analytic ratio matched the
  region's (0.83, 0.93), n=50's window 0 would read ≈1.9 sd rather than 1.57;
* the analytic sd should not be quoted at all in the `C < 1e5` and `deep tail
  C < 1e5` rows, where it is 1560 and 0.695; `results.json` does quote it beside
  the MC value, which is the right thing to have archived.

---

## 5. Job B1 — effective degrees of freedom, third derivation

```
python3 <scratchpad>/vjobB.py
```

`a_T^exact = E[(log2 λ_T − log2 C)² | C ≥ 1]` with `λ_T := C_T`, computed by
exact truncated-Poisson summation for λ ≤ 20000 and by the moment expansion
`(1/λ + 1.75/λ² + 47/12 λ⁻³)/ln²2` above; `a_T^delta = 1/(λ_T ln²2)`;
`ν = (tr Σ)²/tr(Σ²)`. I evaluated `tr(Σ²) = Σ_{i,j} Σ_ij²` **by brute force
over all n² pairs** as well as by the sorted collapse, and the two agree.

| quantity | n=43 mine | producer | n=50 mine | producer |
|---|---|---|---|---|
| Σ a_exact (whole-band noise budget) | **209.125905994** | 209.125905994369 | **247.866028308** | 247.86602830759918 |
| floor (bits) | **0.3405697373165** | 0.3405697373164575 | **0.3275687881280** | 0.32756878812803675 |
| Σ a_delta | 302.147037791 | — | 258.839912062 | — |
| delta-method floor | 0.409365564 | — | 0.334741557 | — |
| ν white, exact variances | **422.158433** | 422.1584332561959 | **471.082747** | 471.08274717827766 |
| ν white, delta variances | 245.152756 | 245.15275638819347 | 326.949143 | 326.94914262486617 |
| ν D-1, delta variances | 2.059985 | 2.0599848007681736 | 2.040459 | 2.0404588341878345 |
| ν D-1, correlation-scaled exact | 2.348577 | 2.348576706979706 | 1.842122 | 1.842122338018778 |
| ν D-1, **literal** min(a,a′) exact | **1.573411** | *(reported as 1.545428738)* | **1.519356** | *(reported as 1.513482010)* |
| ν, C≥10 sub-band | 1.822204 | 1.8222044432536841 | 1.942108 | 1.9421081681338437 |
| ν, C≥1000 sub-band | **1.808799** | 1.8087992966745403 | **1.899175** | 1.8991753774212465 |
| ν white, C≥1000 | **162.465801** | 162.46580130699456 | **237.582174** | 237.58217423744733 |
| ν, C≥1e5 sub-band | 1.983790 | 1.9837899207325027 | 1.819182 | 1.8191819280451533 |

The four archived counting floors also reproduce against BATCH-012's own
`counting_floors` block to 13 digits (`0.3405697373164576`,
`0.16368862345983295`, `0.014627143423849945`, `0.001071947155002997`, and the
delta-method `0.40936556421392906`). This is a fourth independent computation of
those floors.

### 5.1 The one number that does not reproduce, and why

Every quantity above reproduces to 10+ digits **except the headline whole-band
`nu_D1_min_of_variances_exact`**. The report states the formula as

> `dof = (Σ a_T)² / Σ_{T,T′} min(a_T, a_T′)²` with exact truncated-Poisson `a_T`

and the `results.json` field is *named* `nu_D1_min_of_variances_exact` with the
convention string "`min(a_T,a_T')` with a_T exact". Evaluated literally, by
brute force over all 1803² and 2310² pairs, that expression is

```
n=43: nu = 1.573411205        n=50: nu = 1.519355998
```

not 1.545428738 / 1.513482010. I then tested the two candidate collapses:

```
H_A  T-order collapse  sum_i (1 + 2(n-1-i)) a_i^2      n43 1.545428738  n50 1.513482010
H_B  sorted / brute force, literal min(a_i,a_j)        n43 1.573411205  n50 1.519355998
H_C  Sigma_ij = a at the row with the LARGER lambda    n43 1.545428738  n50 1.513482010
```

The producer's number is H_A ≡ H_C. The two conventions differ because
`a_exact` is **not monotone in T**: at exactly one step in each file it falls,

```
n=43: T=1681 C=3 a=0.678572  ->  T=1682 C=2 a=0.614974
n=50: T=2283 C=3 a=0.678572  ->  T=2284 C=2 a=0.614974
```

(the C≥1 truncation biting at λ=2), and `results.json` records this as
`variance_sequence_non_monotone_steps: 1`. It is confined to the deep tail,
which is why **every sub-band value agrees exactly** — the sub-bands exclude the
non-monotone step — and only the whole-band figure moves.

Which convention is right is arguable: the covariance
`Cov(C_T,C_T′) = min(λ_T,λ_T′)` is governed by the *larger-λ* row, so H_C is a
defensible extension of the delta-method structure to exact variances. But the
report and the field name both say H_B, and H_B is what an independent checker
computes. The consequence for the headline is concrete:

* under H_C, `1.5454 → 1.55`, and "exact to published digits" against the red
  team's 1.55 holds;
* under H_B as written, `1.5734 → 1.57`, and it **does not**.

I cannot determine which convention the red team used without their code, so I
cannot say whose number is being reproduced. This is defect **D-1**.

### 5.2 Claim C, assessed and extended

The producer's three conventions give, on my own arithmetic, 1.5454 / 2.0600 /
2.3486 (n=43) and 1.5135 / 2.0405 / 1.8421 (n=50) — reproducing the reported
1.51–2.35 span exactly. Adding the literal-min convention of §5.1 makes it
**four** conventions spanning 1.5135–2.3486. Sampling sd of the whole-band
ratio, `0.5·sqrt(2/ν)`: 56.9 % at ν=1.5454, 57.5 % at 1.5135, 56.4 % at 1.5734,
46.1 % at 2.3486 — all reproduced.

**Claim C is correct and understated.** The qualitative reading is robust: every
convention gives ν between 1.51 and 2.35 against n = 1803/2310 rows and a
white-noise ν of 422/471 — two orders of magnitude of degree-of-freedom
deficit, in all four. The two-significant-figure "1.55" is not robust, and it is
*less* robust than the report says, because the fourth convention is the one
that separates "reproduces exactly" from "0.03 off".

---

## 6. Job B2 — the attenuation identity, third derivation

| | n=43 mine | producer | n=50 mine | producer |
|---|---|---|---|---|
| whole-band budget | **209.125905994** | 209.125905994369 | **247.866028308** | 247.86602830759918 |
| measurable budget (C≥1000) | **0.182288233** | 0.18228823268003574 | **0.261261785** | 0.2612618 |
| deep-tail budget | **208.943617762** | 208.94361776168896 | **247.604766523** | 247.60477 |
| deep-tail floor (951 / 1178 rows) | **0.468731669** | 0.46873166870479455 | **0.458465706** | 0.458466 |
| attenuation A | **1147.226581×** | 1147.2265813308998 | **948.726689×** | 948.73 |
| measurable share of the denominator | **0.087167 %** | 0.08717 % | **0.105404 %** | 0.10540 % |

Per-model decomposition, computed from BATCH-012's archived rms values and my
own floors:

| model / file | ratio whole | ratio C≥1000 | deep rms (bits) | deep ratio | identity constant C | sqrt(C) | identity `ratio_whole² = C + ratio_M²/A` |
|---|---|---|---|---|---|---|---|
| M2, n=43 | 1.044324 | 23.8924 | 0.361119 | **0.77042** | **0.5930256** | **0.77008** | 1.0906124573 = 1.0906124573 |
| M4, n=43 | 1.083044 | 29.8541 | 0.295131 | 0.62964 | 0.3960976 | 0.62936 | 1.1729851531 = 1.1729851531 |
| M2, n=50 | 0.968397 | 23.4140 | 0.275206 | 0.60028 | 0.3599504 | 0.59996 | 0.9377922599 = 0.9377922599 |
| M4, n=50 | 1.067783 | 28.6486 | 0.240575 | 0.52474 | 0.2750601 | 0.52446 | 1.1401610381 = 1.1401610381 |

All of the producer's M2/M4 figures reproduce to 6+ digits, and the identity
closes to 10 digits on every model. The red team's 0.5919 → 0.769× is 0.19 %
away from 0.5930 → 0.7701×, in the direction the producer predicts from
separately-profiled normalisations; I confirm the direction of the argument and
I **cannot check the red team's value**, for exactly the reason ANOM-7 records:
BATCH-012 archived rms summaries, not per-row residual vectors. ANOM-7's
`reconstruction_valid: false` flags are correct and no unsupported number is
reported for the four unreconstructible rows. The successor the producer names
(archive `residuals[T]` per model per fit) is the right and cheap fix.

One framing point. `sqrt(C) = 0.77008` is *not* a structural instrument
quantity. `A = 1147×` is. `C` is `Σ_deep r_T² / (n·floor²)` for **M2's own
residuals**, so "a perfect model reads 0.7701×" means "*given M2's deep-tail
residuals*, a model perfect on the measurable rows reads 0.77×". Had M2's
deep-tail residuals sat *at* the counting floor, C would be 208.944/209.126 =
0.99913 and the same perfect model would read 0.9996×. The 0.77 figure is
therefore carried entirely by the unexplained sub-floor deficit that S-11 is
about. The report's §4.3 places it correctly under model-dependent quantities;
the Coordinator's snapshot headline lists it among "structural quantities" that
"reproduce exactly on every structural quantity". Defect **D-4**.

## 7. The binding requirement (`DEC-20260803-52a750`)

No whole-band ratio is quoted here without its effective dof beside it, and the
C≥1000 comparison is reported:

| model / file | **C ≥ 1000 ratio** (ν_D1 = 1.8088 / 1.8992; ν_white = 162.47 / 237.58) | whole-band ratio (ν_D1 = 1.5454 as implemented, 1.5734 as written / 1.5135, 1.5194; ν_white = 422.16 / 471.08) |
|---|---|---|
| M2, n=43 | **23.89×** | 1.044× |
| M2, n=50 | **23.41×** | 0.968× |
| M4, n=43 | 29.85× | 1.083× |
| M4, n=50 | 28.65× | 1.068× |

The n=50 M2 whole-band ratio of 0.968× — a model scoring *better* than the
counting floor — is the cleanest single illustration of why the whole-band
statistic is uninterpretable, and it reproduces here independently.

## 8. Budget and honesty notes

Wall clock across all my recomputations ≈ 2100 s, peak RSS well under 1 GB, one
producer-script re-execution plus my own scripts. Seeded randomness: seed
`424242`, used only for synthetic null objects (Poisson, gamma-Poisson,
binomial thinning) of my own estimator; every measured quantity above is
seed-independent. No network, no G6K, no new `.out` bytes, no producer artifact
edited. `dominated_by`: not applicable — no attack advanced, no cost frontier
occupied. `sota_delta`: zero.
