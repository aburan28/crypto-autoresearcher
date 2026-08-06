# TASK-20260805-708b70 — execution report

**Left tail of `R = ‖π_{d−β}(e)‖² / ‖e‖²` for CBD_{η=2} errors against real
BKZ-reduced q-ary bases.**

| field | value |
|---|---|
| goal / batch / task | GOAL-MLKEM-005 / BATCH-a51f91 / TASK-20260805-708b70 |
| role | executor (observations only; no state transition, no promotion) |
| git commit at run | `096b9256b287810acd005f259825b6b9b0c9c42a` (branch `claude/mlkem-campaign-005`) |
| dirty tree at run | yes — only this untracked task directory |
| frozen prediction | `prediction_frozen.json`, sha256 `29797476fef01ab9f1691bb09623b7a5592642ae1db57df66ba642d5387cd8ce`, frozen **2026-08-05T16:38:29Z** |
| first research number | protocol run started **2026-08-05T16:44:53Z** |
| protocol runs | 1 of the 2 permitted (`RUN-20260805-708b70-001`), 337.3 s wall, 1.124 GB peak RSS |
| budget | 3000 s / 6 GB / 2 runs — all respected |
| certificate | `kind: none` (pure measurement; no DL solve, no factor-base relation). Independent recomputation V1–V7 stands in its place. |
| **Rule 12** | **UNMET and UNWAIVED. No ML-KEM break claim. No status change to any `EV-MLKEM-*` or `KN-*` record.** |

---

## 0. Outcome in one paragraph

The instrument built, ran, and reproduced itself under independent
recomputation. **The frozen 4·s sensitivity gate was NOT met in any of the four
cells** (shift/s = 0.79, 1.09, 1.97, 3.73 against a required 4.00). Per the
threshold declared before the run — *"If it does not, report an INSTRUMENT
FAILURE and record NO mathematical conclusion"* — **this task records an
INSTRUMENT outcome and NO mathematical conclusion about whether the Beta law
governs the left tail of `R`.** The P1 and P2 numbers below are reported as
required observations and are **not** admissible as validation or refutation of
the law. The cause of the gate failure is identified, is a *forced value that
the task card's demonstration arm did not derive in advance*, and is
constructively verified in §5.

---

## 1. What was measured

* Cells: `d ∈ {100,140}`, `k = d/2`, `q = 3329`, `β ∈ {30,40}`; **8 independent
  bases per cell** (independent `A`, independent fplll seeds), LLL then BKZ-β
  with `max_loops=2`; **2²⁰ = 1 048 576 CBD_{η=2} error vectors per basis**.
* `R` computed from the GSO as `Σ_{i>d−β} ⟨e,b*_i⟩²/‖b*_i‖²` divided by `‖e‖²`,
  implemented as `‖Qᵀe‖²/‖e‖²` with `Q` the orthonormal tail-GSO frame.
* Instrument: fpylll 0.6.4 + cysignals 1.12.5, manylinux wheels, task-local
  `--target` dir. No Sage, no g6k. Wheel sha256 in `receipt.json`.
* Three arms, **identical statistic and identical code path**: `real`,
  `haar_null` (the null), `demo_anisotropic` (the sensitivity demonstration).

**Why the denominator.** Dividing by `‖e‖²` is the load-bearing design choice
and was not changed. The pre-batch screen killed `IDEA-20260805-3d71ca`'s A-vs-B
rule as forced (the ratio of the two competing relative variances is the
identity `κ/2` exactly, verified to 5.55e-15); dividing by `‖e‖²` cancels the
norm fluctuation, hence cancels `κ`, hence removes that identity.

---

## 2. FORCED VALUES — reported as forced, carrying zero information

### 2.1 `E[R] = β/d` is FORCED

For any fixed rank-β projector `P` and `e` with iid equal-variance coordinates,
`E‖Pe‖² = σ²tr(P) = σ²β` and `E‖e‖² = σ²d`. **This holds for every basis,
reduced or not, and for the Haar arm equally.**

| cell | `E[R]` forced | measured, real arm | abs. deviation |
|---|---|---|---|
| d100_b30 | 0.300000 | 0.3000005 | 4.6e-07 |
| d100_b40 | 0.400000 | 0.4000157 | 1.6e-05 |
| d140_b30 | 0.2142857 | 0.2142940 | 8.3e-06 |
| d140_b40 | 0.2857143 | 0.2857270 | 1.3e-05 |

**This agreement is not evidence of anything.** It is reported because the
completion gate requires it and because GOAL-MLKEM-005 C3 explicitly says
reporting only `E[R]` does not satisfy C3.

### 2.2 The Beta law is DERIVED, not fitted

`Var(R) = 2β(d−β)/(d²(d+2))` was quoted in the frozen file **before the run**,
precisely so that agreement cannot be presented as a discovery.

| cell | Var derived | Var measured (real) | Var measured (haar) |
|---|---|---|---|
| d100_b30 | 0.0041176 | 0.0041206 | 0.0041166 |
| d100_b40 | 0.0047059 | 0.0047030 | 0.0047059 |
| d140_b30 | 0.0023714 | 0.0023685 | 0.0023709 |
| d140_b40 | 0.0028744 | 0.0028707 | 0.0028761 |

**Agreement here is a discovery about nothing.** See defect **D1** in §7: two
entries of the frozen file's pre-tabulated variance *list* are arithmetically
wrong; the *formula* in the same file is correct and is what the code used.

---

## 3. Headline (a) — KS distance on the body (SANITY CHECK, NOT THE FINDING)

`sup|F_emp − F_Beta|` over `{x : 0.01 ≤ F_Beta(x) ≤ 0.99}`, pooled over 8 draws
(8 388 608 samples).

| cell | real | haar_null | demo_anisotropic |
|---|---|---|---|
| d100_b30 | 0.000221 | 0.000198 | 0.002896 |
| d100_b40 | 0.000236 | 0.000316 | 0.009383 |
| d140_b30 | 0.000408 | 0.000256 | 0.008905 |
| d140_b40 | 0.000302 | 0.000371 | 0.010519 |

Real and null are indistinguishable. The demonstration arm is 15–35× larger —
see §5, and note that **this is not the statistic the threshold was declared
on** and is not used to rescue the demonstration.

---

## 4. Headline (b) and (c) — the only non-forced content

### 4.1 (b) Lower-tail quantile ratios `q_emp(p)/q_Beta(p)`

Estimator frozen in advance: sort ascending, `q_emp(p) = R_sorted[k−1]`,
`k = round(p·N)`. Pooled figures use `N = 8·2²⁰` (so `k` = 8192 and 128);
per-basis figures use `N = 2²⁰` (`k` = 1024 and 16). CI95 is the
distribution-free binomial order-statistic interval.

**REAL-BASIS ARM**

| cell | pooled `r(2⁻¹⁰)` | CI95 | pooled `r(2⁻¹⁶)` | CI95 | per-basis `r(2⁻¹⁰)` mean ± sd | per-basis `r(2⁻¹⁶)` mean ± sd |
|---|---|---|---|---|---|---|
| d100_b30 | **0.99829** | [0.9963, 1.0005] | **1.00947** | [0.9954, 1.0216] | 0.99853 ± 0.00450 | 1.00609 ± 0.01859 |
| d100_b40 | **1.00054** | [0.9986, 1.0021] | **0.99950** | [0.9886, 1.0120] | 1.00031 ± 0.00160 | 1.00004 ± 0.01432 |
| d140_b30 | **0.99954** | [0.9973, 1.0016] | **0.99592** | [0.9737, 1.0096] | 0.99943 ± 0.00375 | 0.99040 ± 0.02748 |
| d140_b40 | **1.00100** | [0.9991, 1.0027] | **1.00104** | [0.9880, 1.0147] | 1.00093 ± 0.00287 | 1.00229 ± 0.01122 |

**HAAR NULL ARM — the same statistic, run and read FIRST** (KN-TECH-1a5b7e mode 4)

| cell | pooled `r(2⁻¹⁰)` | pooled `r(2⁻¹⁶)` |
|---|---|---|
| d100_b30 | 0.99857 | 1.00039 |
| d100_b40 | 0.99914 | 0.99967 |
| d140_b30 | 1.00102 | 0.99609 |
| d140_b40 | 0.99990 | 1.01481 |

Largest real-arm deviation from 1: **0.95 %** at `2⁻¹⁶` (d100_b30) and **0.41 %**
at `2⁻¹⁶` (d140_b30); at `2⁻¹⁰` the largest is **0.17 %** (d100_b30). Frozen
tolerances were 5 % and 10 %.

### 4.2 (c) Between-basis vs within-basis variance decomposition

All 8 bases of a cell share the same 2²⁰ error vectors, so the sampling noise in
the group means is common-mode and largely cancels; the raw figure is therefore
already close to the pure projector effect.

| cell | arm | `Var_between` | `Var_within` | **between fraction** |
|---|---|---|---|---|
| d100_b30 | real | 2.84e-09 | 4.121e-03 | **6.89e-07** |
| d100_b30 | haar_null | 5.28e-09 | 4.117e-03 | 1.28e-06 |
| d100_b30 | demo | 6.26e-06 | 4.085e-03 | 1.53e-03 |
| d100_b40 | real | 3.50e-09 | 4.703e-03 | **7.44e-07** |
| d100_b40 | haar_null | 9.70e-10 | 4.706e-03 | 2.06e-07 |
| d100_b40 | demo | 1.43e-05 | 4.671e-03 | 3.05e-03 |
| d140_b30 | real | 1.32e-09 | 2.369e-03 | **5.57e-07** |
| d140_b30 | haar_null | 2.03e-09 | 2.371e-03 | 8.54e-07 |
| d140_b30 | demo | 3.95e-06 | 2.352e-03 | 1.68e-03 |
| d140_b40 | real | 1.42e-09 | 2.871e-03 | **4.96e-07** |
| d140_b40 | haar_null | 3.94e-09 | 2.876e-03 | 1.37e-06 |
| d140_b40 | demo | 6.09e-06 | 2.882e-03 | 2.11e-03 |

**The real arm's between-basis variance sits BELOW its own sampling floor.**
`Var(R)/N` is 3.93e-09, 4.49e-09, 2.26e-09, 2.74e-09 for the four cells, and the
measured `Var_between` is 0.52–0.78× that. So the between-basis component is not
merely below the 20 % threshold, it is **unresolvable at this sample size** —
the honest statement is an upper bound of order 1e-6 of the total, not a point
estimate.

**Scoping caution on (c), stated because the confounder it addresses is about
the tail, not the mean.** This decomposition is of `Var(R)`, i.e. of the
*mean* of `R` across bases. It does not bound the between-basis variation of the
*left-tail quantile*, which is what the best-of-M argument actually consumes.
Measured separately, and compared against the order-statistic sampling noise of
`N = 2²⁰` iid Beta draws (a post-hoc diagnostic, **not** part of the frozen
prediction):

| cell | level | iid-Beta sampling sd | real per-basis sd | ratio |
|---|---|---|---|---|
| d100_b30 | 2⁻¹⁰ | 0.00300 | 0.00450 | 1.50 |
| d100_b30 | 2⁻¹⁶ | 0.02094 | 0.01859 | 0.89 |
| d100_b40 | 2⁻¹⁰ | 0.00238 | 0.00160 | 0.67 |
| d100_b40 | 2⁻¹⁶ | 0.01653 | 0.01432 | 0.87 |
| d140_b30 | 2⁻¹⁰ | 0.00306 | 0.00375 | 1.22 |
| d140_b30 | 2⁻¹⁶ | 0.02125 | 0.02748 | 1.29 |
| d140_b40 | 2⁻¹⁰ | 0.00247 | 0.00287 | 1.16 |
| d140_b40 | 2⁻¹⁶ | 0.01699 | 0.01122 | 0.66 |

Ratios scatter around 1 (0.66–1.50; an 8-draw sd estimate carries ~27 % relative
uncertainty by itself), i.e. no between-basis tail variation is resolved either.
This is an observation, not a conclusion — the gate in §5 failed.

---

## 5. THE NULL, AND THE SENSITIVITY ADJUDICATION — the load-bearing section

### 5.1 The null as declared and as run

* **Object removed:** the *provenance of the projector* — the alignment between
  the reduced basis's GSO tail subspace and the q-ary/coordinate structure.
* **Object preserved:** the error law (CBD_{η=2}), `β`, `d`, the statistic, the
  code path, and the identical 2²⁰ error vectors. This is the **minimal**
  deletion; it deliberately does not delete the error law, the over-deletion
  that cost GOAL-MLKEM-004 batch 4.
* **Null arm:** projection onto a Haar-random β-dim subspace (QR of a Gaussian
  `d × β` matrix), 8 independent draws per cell.
* **Statistic on both arms:** identical — (a), (b), (c). All reported above.
* **Comparator, by name:** the **Haar-random-subspace arm** — the arm the null
  is about, not the most separating arm available.
* **`s`:** that arm's own between-draw sd of the `2⁻¹⁰` quantile ratio over its
  8 draws. Comparator drawn 8 times and reported as an interval, per
  KN-TECH-1a5b7e mode 5.

### 5.2 The 4·s adjudication — EXPLICIT, INCLUDING ITS FAILURE

Demonstration arm: projector stays Haar (same 8 draws); the isotropic CBD error
is replaced by a two-block anisotropic error at matched total variance, sd ratio
2:1 between halves (`c₁ = √1.6 = 1.264911`, `c₂ = √0.4 = 0.632456`,
`(c₁²+c₂²)/2 = 1.000000` — verified).

| cell | haar mean `r(2⁻¹⁰)` | demo mean `r(2⁻¹⁰)` | signed shift | `s` | `4s` | **shift / s** | **MET?** |
|---|---|---|---|---|---|---|---|
| d100_b30 | 0.99865 | 1.00066 | **+0.00201** | 0.00254 | 0.01018 | **0.79** | **NO** |
| d100_b40 | 0.99898 | 0.99623 | **−0.00275** | 0.00252 | 0.01010 | **1.09** | **NO** |
| d140_b30 | 1.00076 | 0.99467 | **−0.00609** | 0.00309 | 0.01237 | **1.97** | **NO** |
| d140_b40 | 0.99984 | 1.00706 | **+0.00722** | 0.00194 | 0.00775 | **3.73** | **NO** |

Note the shift is **not even sign-consistent** across cells (+, −, −, +).

> **VERDICT: INSTRUMENT FAILURE IN ALL FOUR CELLS.**
> Per the frozen threshold, **no mathematical conclusion is recorded.** The P1
> and P2 figures in §4 and §6 are observations, not validations.

### 5.3 Why it failed — a forced value the demonstration did not derive

This diagnosis was derived **after** the run and is recorded as an instrument
finding. It changed nothing: the threshold was not adjusted and no run was
re-scored.

**Claim.** For a Haar-random rank-β projector `P` drawn *independently of* `e`,
the law of `R = ‖Pe‖²/‖e‖²` is **exactly** `Beta(β/2,(d−β)/2)` for **every**
fixed `e ≠ 0`, by rotation invariance of the Haar measure. Consequently the
**marginal** law of `R` on the demonstration arm is Beta for **any** error law,
isotropic or not. The declared demonstration statistic — the mean over Haar
draws of the `2⁻¹⁰` quantile ratio — therefore has expectation 1 on **both** the
Haar arm and the demonstration arm, and **its expected contrast is exactly
zero.**

This is `KN-TECH-1a5b7e` **mode 1** ("the null that cannot fail") applied to the
*sensitivity demonstration* rather than to the null. Power was not low; it was
zero in expectation. The card's own closed-form derivation
(`E[R] → tr(PΣ)/tr(Σ)`) is correct and is exactly the quantity whose Haar
average is `β/d`, which is why it predicts no shift in the mean — the
`d_eff = d/1.36` widening argument in the frozen file applies to the
*conditional-on-P* law, not to the marginal that the declared statistic reads.

**Constructive verification** (`verification.json`, independent code path):

* **V6a.** Fix `e = (1,0,…,0)` — the most anisotropic unit vector there is — and
  draw 16 384 Haar subspaces at `d=100, β=30`. Result: KS statistic 0.00611
  against `Beta(15,35)`, **p = 0.572**, mean 0.29955 vs `β/d = 0.3`. The error
  law is invisible to the marginal.
* **V6b.** Not a sample-size problem. At **64** projector draws (8× the declared
  8) and 2¹⁸ errors, the declared statistic moves by 0.00267, i.e.
  **1.09 standard errors**. More draws will not rescue it.
* **V6c.** Where the manipulation *is* loud: the between-draw variance of
  `E[R|P]` goes from **1.259e-08** (isotropic) to **1.508e-05** (anisotropic),
  a factor **1198**, against a first-order closed form
  `Var_Beta · (d/(d−1)) · (Σsᵢ⁴ − (Σsᵢ²)²/d)/(Σsᵢ²)²` = **1.497e-05** —
  agreement to **0.69 %**, and that closed form was derived, not fitted. The
  isotropic value sits at the sampling floor `Var(R)/N ≈ 1.6e-08`.
* Same signature inside the protocol run itself: the demonstration lifts the
  KS-body distance 15–35× (§3) and the between-draw variance fraction
  1192–14791× (§4.2), while leaving the declared statistic where it was.

**These do not rescue the demonstration and are not offered as a substitute.**
The threshold was declared on the `2⁻¹⁰` quantile ratio before the run; it was
not met; the outcome is INSTRUMENT FAILURE. Selecting a different statistic
after seeing the numbers is precisely the move the frozen threshold exists to
forbid.

### 5.4 The unit test that is NOT a control

Projecting CBD vectors onto a Haar-random subspace and recovering
`Beta(β/2,(d−β)/2)` **constructs** that law by definition — it tests numpy's QR
and the CBD sampler's directional uniformity. It is recorded in `receipt.json`
as an **instrument check only** and is **not** recorded as a control that
passed. §5.3 shows exactly how strong that statement is: the recovery holds even
for `e = (1,0,…,0)`.

### 5.5 Mode-4 check: the frozen rule emits the same label on the null arm

| cell | P1 on haar_null | P1 on real | P2 on haar_null | P2 on real |
|---|---|---|---|---|
| d100_b30 | pass | pass | pass | pass |
| d100_b40 | pass | pass | pass | pass |
| d140_b30 | pass | pass | pass | pass |
| d140_b40 | pass | pass | pass | pass |

**The frozen decision rule returns the identical verdict on the null arm and on
the real arm in all four cells.** The frozen file anticipated this for P1 and
labelled it in advance ("expected to pass by construction"); it did **not**
anticipate it for P2. A rule that fires identically on its own null does not
discriminate, whatever its branch count. Recorded here; the judgement is the
Reviewer's and the Coordinator's.

---

## 6. The frozen prediction, scored exactly as specified

Scored mechanically on the pooled real-arm ratios. **Reported as observations
only**, because §5.2 failed.

| cell | \|r(2⁻¹⁰)−1\| | ≤0.05? | \|r(2⁻¹⁶)−1\| | ≤0.10? | **P1** | between frac | ≤0.20? | **P2** |
|---|---|---|---|---|---|---|---|---|
| d100_b30 | 0.00171 | yes | 0.00947 | yes | **pass** | 6.89e-07 | yes | **pass** |
| d100_b40 | 0.00054 | yes | 0.00050 | yes | **pass** | 7.44e-07 | yes | **pass** |
| d140_b30 | 0.00046 | yes | 0.00408 | yes | **pass** | 5.57e-07 | yes | **pass** |
| d140_b40 | 0.00100 | yes | 0.00104 | yes | **pass** | 4.96e-07 | yes | **pass** |

**Branch adjudicated: NEITHER — "sensitivity threshold missed; instrument
outcome only."** The frozen threshold clause is explicit that a missed gate
means *no mathematical conclusion*. The "P1 ∧ P2 hold → the selection law is
validated" branch is **NOT** taken and must not be read into the table above.
Whether this satisfies GOAL-MLKEM-005 criterion C3 — which names "NEITHER, with
the sensitivity demonstration's failure recorded as an INSTRUMENT outcome" as
one of its three admissible adjudications — is a Coordinator judgement, not
mine.

---

## 7. Deviations, defects and anomalies — recorded, none discarded

**D1 — arithmetic error inside the frozen prediction file.** Two of the four
entries of `forced_values_derived_in_advance.beta_law.variance_values` are
wrong:

| cell | frozen list | correct (`2β(d−β)/(d²(d+2))`) | rel. error |
|---|---|---|---|
| d100_b30 | 0.004117647058823529 | 0.00411764705882353 | 2.1e-16 |
| d100_b40 | 0.004705882352941176 | 0.004705882352941176 | 0 |
| **d140_b30** | **0.0024152803180914513** | **0.0023713710836447254** | **1.85e-02** |
| **d140_b40** | **0.0028747433264887066** | **0.002874389192296637** | **1.23e-04** |

The **formula** in the same file is correct, and `measure.py` computes the value
from the formula, never from the list. The wrong numbers sit inside a block
explicitly labelled forced / zero-information, and **nothing in P1, P2, (a),
(b), (c) or the 4·s adjudication depends on them.** The frozen file was **not
edited** — it is frozen and hash-checked by `measure.py` at run start. The
correction is recorded here and in `receipt.json`; an amendment request goes to
the Coordinator.

**D2 — specification-level defect in the sensitivity demonstration.** The
demonstration arm declared in the task card is forced-invariant in its declared
statistic (§5.3). Discovered at run time, after the freeze. **The demonstration
and threshold were run exactly as declared and the failure is reported as
declared.** Requested amendment (the Coordinator's to grant, not mine to take):
a demonstration whose statistic is not marginal-invariant — e.g. couple the
projector to the error law (rotate the Haar frame toward a coordinate block), or
declare the threshold on `Var_P(E[R|P])`, where the same manipulation moves the
statistic by a factor 1198 against a closed form it matches to 0.69 %.

**D3 — task-local `--target` dir placed outside the repository.** The card asks
for a task-local `--target` dir; a 41.6 MB vendored binary tree inside the
declared `write_scope` would be committed with the deliverables. The dir is
`<scratch>/pkgs` outside the repo; wheel filenames and sha256 are recorded in
`environment.json` and `receipt.json` so the instrument is reconstructible.

**D4 — fpylll `BKZ.DEFAULT_STRATEGY` unusable**, exactly as `KN-TECH-14efa5`
documents (it points at
`/project/local/share/fplll/strategies/default.json`, absent from the wheel).
Pruning-free strategies were built in-process as
`[Strategy(b) for b in range(β+1)]`. **Consequence, stated because it is a
protocol choice and not a free one:** the reduction is pruning-free BKZ-β, not
BKZ 2.0 with the fplll default pruning schedule. All four cells use the same
choice, so arms and cells are comparable, but the bases are not identical to
what a default-strategy BKZ would produce.

**D5 — fpylll double-precision GSO disagreement.**
`instrument_checks.qr_vs_fpylll_gso_max_rel_err` reaches 7.6e-07 at `d = 140`
(6.7e-10 at `d = 100`). This is fpylll's `float_type="d"` GSO, **not** the frame
used for projection. V7: numpy Householder QR backward residual
`‖Bᵀ−QR‖/‖B‖ = 5.5e-16`, orthonormality deviation 1.1e-15, and fpylll at
`float_type="ld"` agrees with the numpy QR to 1.1e-13. Not a measurement defect;
recorded because it is a visible number in `results.json`.

**D6 — the 8 bases of a cell share the same 2²⁰ error vectors.** Required by the
card ("same 2²⁰ CBD error vectors, same code path"). It makes the group-mean
sampling noise common-mode, which *tightens* the (c) estimate; it also means the
8 per-basis tail quantiles are not independent draws, so their sd is not a clean
8-sample standard error. Both directions recorded.

**D7 — pooled vs per-basis `2⁻¹⁶` quantile.** The pooled estimator uses
`k = 128` of `8·2²⁰` samples; the per-basis estimator uses `k = 16` of `2²⁰`.
P1 is scored on the pooled figure, as the frozen file specifies, with the
per-basis spread reported beside it.

**D8 — three invocations, all recorded.** One smoke run at `d=40, β=12, N=2¹⁴,
3 draws` (code-path validation; wrote to scratch, not to `results.json`); one
protocol run (`RUN-20260805-708b70-001`); one verification run (`verify.py`).
The second permitted protocol run was **not** used. No run was repeated to
obtain a different result.

**Anomaly A1 — the shift/s figures rise across the four cells** (0.79, 1.09,
1.97, 3.73, ordered d100_b30 < d100_b40 < d140_b30 < d140_b40). Recorded because
unexpected observations are recorded. **Four points are not a trend**, the signs
are inconsistent, and §5.3 gives an expected contrast of zero, so this is most
plausibly `s` fluctuating on 8 draws. No reading is attached.

---

## 8. Scope — binding, and none of it is negotiable

* **NOTHING MEASURED HERE IS TRANSPORTED TO `β = 606`, `d = 1420`.** The β-trend
  over `{30,40} × {100,140}` is **four points, not a law**, and this task
  computes no extrapolation.
* The mechanism under study is **session** recovery, not key recovery. **No
  number in this report may be subtracted from the in-repo `primal_bdd` margins
  of 2.80 / 6.04 / 1.28 bits.**
* Toy scale is never crypto-scale evidence (AGENTS.md rule 7).
* **AGENTS.md rule 12 is UNMET and UNWAIVED.** No ML-KEM break claim, no FIPS 203
  parameter set affected or cleared, no cost claim, no exponent moved. This is
  defensive vetting.
* The Executor records observations. Nothing here declares a hypothesis
  supported, rejected or closed, or a heuristic validated or refuted.

---

## 9. Reproduction

```
PYTHONPATH=<target>/pkgs python3 measure.py --mode full --out results.json \
    --cache-dir <scratch>/bkzcache --workers 4 --deadline-seconds 2700
PYTHONPATH=<target>/pkgs python3 verify.py
```

Exact command in `command.txt`; environment, wheel hashes and git state in
`environment.json`; seeds are the three families printed in
`results.json.seed_scheme` and are the only sources of randomness. `measure.py`
refuses to run if `prediction_frozen.json` does not hash to the value frozen
before the run.
