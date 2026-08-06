# Red Team — B2-A: is the T2 departure a property of the basis or of the instrument?

TASK-20260806-fc0966 / BATCH-436ddd / GOAL-MLKEM-005
Reviewing: TASK-20260806-09ec68 (frozen), under DEC-20260805-4823db.

**Claim tier: TOY.** Nothing in this report supports any statement about ML-KEM
security or any FIPS 203 parameter set. Every number here is measured at
`d <= 140`, `beta <= 60`, `q = 3329`, `k = d/2`, and none of it is transported
to `beta = 606, d = 1420`. I change no research status.

I did not modify any frozen artifact. My own compute ran entirely outside the
repository; I write only inside this review directory.

---

## 0. Verdict, stated first

**The departure is a property of the BASIS PRESENTATION, not of the instrument.
B2-A's directional reading is correct. But B2-A's headline sentence is wrong,
its stated mechanism is geometrically false, and its strongest control is a
theorem rather than a control.**

Precisely:

1. **Not an instrument artifact.** I reproduced the 32 reductions independently,
   drew a **fresh error set** (seed `31415926+d` against the executor's
   `20260805+d`), and reproduced the headline: unreduced `D = +0.037841`
   (23.45 SE) against the executor's `+0.038967` (27.11 SE); LLL and BKZ arms
   null in both. The signal is not an error-draw accident.

2. **Not "absent after reduction" either.** The quantity the instrument
   estimates is a *deterministic scalar function of the tail frame*, computable
   exactly with zero error draws. Computed exactly on 16 bases per cell, the
   post-reduction departure is **not zero**: it is suppressed by 15–50× and
   remains **+10.2 sd (LLL, d=100), +16.6 sd (LLL, d=140), +9.9 sd (BKZ-30,
   d=140)** above the Haar expectation, with the same sign in **16 of 16 bases**
   in every cell where it is significant. The instrument reported "absent"
   because its 4·SE gate has a resolution floor roughly **10–50× above the
   residual**, not because the residual is zero.

So the third reading in the task card is the correct one, in a specific form
that neither of the two offered readings captures: **the departure is a
basis-presentation property, reduction suppresses it by one to two orders of
magnitude, and the instrument is blind to what survives.** "Absent below gate"
is an *upper bound*, and the report presents it as an absence.

3. **The mechanism B2-A claims is false.** The tail window does not sit in the
   `q·I` block. It sits, with energy fraction `1.00000`, in the *complementary*
   `I_k` block, and it is not "exactly coordinate-aligned" — it is a generic
   subspace *confined to a coordinate block*, a weaker and quantitatively
   different thing. Details in §2.

4. **The INVALID verdict is the governing decision's grid, not the
   instrument's failure.** I ran the counterfactual the executor correctly
   refused to run. On the grid the executor proposes as a successor, the
   statistic is **strictly monotone with 50.05 / 34.73 / 20.17 / 9.39 / 3.14 /
   1.00 SE separations** — G3 passes comfortably. The honest finding is about
   DEC-20260805-4823db, which froze `t in {0, 0.05, ...}`. §6.

---

## 1. Integrity checks (all pass)

| check | result |
|---|---|
| Snapshot receipt `path_sha256`, all 5 files | **match** (`b2a.py`, `b2a_report.md`, `b2a_results.json`, `b2bcd_notes.md`, `run_manifest.yaml`) |
| Pre-registration hash chain | **match.** sha256 of the report's inter-marker segment, computed with the script's own split rule, `= 2893a6b0cebf0a3ff40d779c6f66fb7852cad5830165a93079ddea6e6efd02b6 = b2a_results.json:prereg_sha256`. `prereg_text` in the JSON is byte-identical to the report segment. |
| Report tables vs `b2a_results.json` | Every figure I spot-checked in Parts 4–9 reconciles against the JSON. I found **no fabricated number**. |
| Basis generator | `IntegerMatrix.random(d,"qary",k=d//2,q=3329)` produces exactly `[[I_k, A],[0, q·I_{d-k}]]` with `A` uniform in `[0,q)`; `‖b_0‖ = 14346.748…` reproduces `b0_norm_raw` for `d100_b30_i0` **exactly**. The executor's stated basis form is correct. |
| Budget | **No overrun.** 1723.84 / 4000 core-seconds; 631.26 / 3000 s wall; 1.203 / 4 GB RSS. The script was additionally run with an internal cap of 3600 core-seconds and `timeout 2900`, both *below* the authorisation — conservative, and correctly reported. |

One caveat on the freeze, offered as a limit of degree and not an accusation:
the chain binds `b2a_report.md` to `PREREG_MD` **inside `b2a.py`**, and both are
in the same file the executor controlled. It is a self-attested freeze made
externally durable only later, by the snapshot commit. It is materially stronger
than no freeze and I treat it as honoured; it is not an independent timestamp.

---

## 2. The `q·I` mechanism is false, and the correct geometry is different

B2-A, Part 8: *"for `beta <= d - k = d/2` the tail-`beta` GSO window of the
unreduced q-ary basis `[[I_k, A],[0, q I_{d-k}]]` lies inside the `q I` block,
which is exactly coordinate-aligned."*

Take the orthogonal complement of the row span of `[I_k | A]`. It is
`{(-Az, z) : z ∈ R^{d-k}}`. Intersecting with the complement of
`span(e_{k+1},…,e_{d-beta})` — which is what the tail-`beta` GSO window is —
leaves `{(-Az, z) : z supported on the last beta coordinates}`. Since
`‖Az‖ ≈ q·sqrt(k/3) ≫ ‖z‖`, that subspace lies, to `O(1/q)`, **inside the
first `k` coordinates — the `I_k` block, not the `q·I` block.**

Measured on the executor's own frozen basis seeds (8 bases per `d`):

| d | k | beta | frame energy in `I_k` coords | frame energy in `q·I` coords | `T = Σ_a P_aa²` | `beta²/k` | `beta` (exact alignment) | `beta²/d` (Haar) |
|---|---|---|---|---|---|---|---|---|
| 100 | 50 | 30 | **1.00000** | 0.00000 | 18.357 | 18.000 | 30 | 9.000 |
| 100 | 50 | 40 | **1.00000** | 0.00000 | 32.245 | 32.000 | 40 | 16.000 |
| 100 | 50 | 50 | 0.99995 | 0.00005 | 49.995 | 50.000 | 50 | 25.000 |
| 100 | 50 | 60 | **0.83333** | 0.16667 | 52.269 | 72.000 | 60 | 36.000 |
| 140 | 70 | 30 | **1.00000** | 0.00000 | 13.195 | 12.857 | 30 | 6.429 |
| 140 | 70 | 40 | **1.00000** | 0.00000 | 23.236 | 22.857 | 40 | 11.429 |
| 140 | 70 | 50 | **1.00000** | 0.00000 | 36.044 | 35.714 | 50 | 17.857 |
| 140 | 70 | 60 | **1.00000** | 0.00000 | 51.633 | 51.429 | 60 | 25.714 |

Three corrections follow.

- **Wrong block.** The window's energy in the `q·I` block is `0.00000`.
- **Not "exactly coordinate-aligned".** `T` lands on `beta²/k` to within 2%,
  which is exactly what a *uniformly random* `beta`-subspace of a
  `k`-dimensional coordinate block gives. Exact coordinate alignment would give
  `T = beta`: at `beta=30, d=100` that is 30 against the measured 18.36.
- **Right boundary, wrong reason.** The executor names `beta <= d−k`; the
  geometry says `beta <= k`. Both tested `d` have `k = d/2`, so `d−k = k` and
  the two are numerically indistinguishable here. The `beta=60, d=100` energy
  fraction is `0.83333 = 50/60 = k/beta` exactly — the signature of a window
  confined to a `k`-dimensional block being forced to spill, which identifies
  the boundary as `k`. **Discriminating test: any `k ≠ d/2`.** The executor's
  Part 10 already lists "I did not vary `k`" as unevaluated; this is why it
  matters.

The executor's Part 8 argues the mechanism from a single point (`d=100,
beta=60`, the only series reversal). That inference was right; the reason given
for it was not.

---

## 3. What the instrument actually measures: one scalar

For a rank-`beta` projector `P = QQᵀ` and iid coordinates with unit variance and
fourth moment `μ₄`,

```
Var(eᵀPe) = 2·beta + (μ₄ − 3)·T ,        T = Σ_a P_aa²
```

CBD_{η=2} has `μ₄ = 2.5` exactly (the executor's own instrument check measures
2.49961 / 2.500359), so the coefficient is `−0.5` and the **entire**
coordinate-alignment effect enters through the single scalar `T`. Normalising by
`‖e‖²` and expanding,

```
Var(R)/Var_Beta ≈ 1 − V / (4·beta·(1 − beta/d)) ,     V = T − beta²/d
E[V] for a Haar frame = 2·beta·(d−beta) / (d·(d+2))   (exact)
```

This is not a fitted model — it has no free parameters. It reproduces the
executor's own `0.75` factor: for an exactly coordinate-aligned projector
`V = beta(1−beta/d)` and the factor is `0.75` for **every** `beta`.

**Empirical confirmation — one universal curve across three unrelated frame
families.** I ran the executor's own statistic (`N = 2^20`, 8 frames per arm,
`p = 2^-10`, independent error set) on: real unreduced/LLL/BKZ lattice frames;
synthetic frames that are a random `beta`-subspace of an `m`-dimensional
*coordinate block*; and the graded family. `d = 100`, `beta = 30`:

| arm | `V` | `D = r − r_haar` | shift / SE | gate (4·SE) |
|---|---|---|---|---|
| graded `t=0` (coord-aligned) | 21.000 | +0.094897 | 50.05 | CLEARS |
| graded `t=0.002` | 14.202 | +0.065201 | 34.73 | CLEARS |
| **block `m=50`** | 9.445 | **+0.037378** | 19.19 | CLEARS |
| **unreduced (real lattice)** | 9.363 | **+0.037841** | 23.45 | CLEARS |
| **graded `t=0.005`** | 8.473 | **+0.037341** | 20.17 | CLEARS |
| block `m=70` | 4.317 | +0.016617 | 10.03 | CLEARS |
| graded `t=0.01` | 4.304 | +0.017489 | 9.39 | CLEARS |
| block `m=80` | 2.718 | +0.007547 | 4.77 | CLEARS |
| graded `t=0.02` | 1.801 | +0.005221 | 3.14 | no |
| block `m=90` | 1.418 | +0.003683 | 1.87 | no |
| graded `t=0.05` | 0.661 | +0.001695 | 1.00 | no |
| `lll_only` (real lattice) | 0.607 | +0.002230 | 1.10 | no |
| block `m=100` (= unconfined) | 0.422 | +0.001667 | 1.08 | no |
| `haar_null` | 0.406 | 0 | — | no |
| `real_bkz` (real lattice) | 0.376 | −0.001969 | −1.02 | no |

Three frame families with nothing in common except `V` land on the same curve:
`V ≈ 9` gives `D ≈ 0.0374` whether the frame comes from a q-ary lattice, a
coordinate-block projector, or a graded interpolation. **`T2` is a noisy
estimator of `V`, and of nothing else at this resolution.**

The instrument's **detection floor** is therefore locatable: the gate fires at
`V = 2.7` (4.77 SE) and fails at `V = 1.8` (3.14 SE). Floor ≈ **`V ≈ 2.2`** at
(`d=100, beta=30`, 8 draws, `N = 2^20`).

---

## 4. "Absent after LLL and after BKZ" is false. It is an upper bound.

Because `V` is exact and free, I computed it directly — 16 bases per cell,
against a 2000-frame Haar reference and the exact Haar expectation
`2β(d−β)/(d(d+2))`.

`d = 100, beta = 30` (Haar `E[V] = 0.41176`, 2000-frame mean `0.41116 ± 0.00130`):

| arm | `V` | excess over Haar | significance | bases with positive excess |
|---|---|---|---|---|
| unreduced | 9.35940 ± 0.01692 | **+8.94824** | +527 sd | 16/16 |
| LLL only | 0.59748 ± 0.01814 | **+0.18632** | **+10.2 sd** | **16/16** |
| LLL+BKZ-30 | 0.38785 ± 0.01013 | −0.02331 | −2.3 sd | 4/16 |

`d = 140, beta = 30` (Haar `E[V] = 0.33199`, measured `0.33192 ± 0.00091`):

| arm | `V` | excess over Haar | significance | bases positive |
|---|---|---|---|---|
| unreduced | 6.74915 ± 0.01414 | **+6.41723** | +453 sd | 16/16 |
| LLL only | 0.77053 ± 0.02648 | **+0.43861** | **+16.6 sd** | **16/16** |
| LLL+BKZ-30 | 0.47187 ± 0.01415 | **+0.13995** | **+9.9 sd** | **16/16** |

Sweeping the tail window on the same reduced frames (free — the frames retain 60
GSO columns):

| d | beta | LLL excess (sd) | positive | BKZ-30 excess (sd) | positive |
|---|---|---|---|---|---|
| 100 | 30 | +0.1844 (+10.1) | 16/16 | −0.0252 (−2.4) | 4/16 |
| 100 | 40 | +0.2165 (+11.0) | 16/16 | −0.0081 (−0.5) | 7/16 |
| 100 | 50 | +0.2797 (+13.7) | 16/16 | +0.0008 (+0.1) | 8/16 |
| 100 | 60 | +0.2267 (+14.2) | 16/16 | +0.0205 (+1.6) | 10/16 |
| 140 | 30 | +0.4385 (+16.5) | 16/16 | **+0.1398 (+9.8)** | **16/16** |
| 140 | 40 | +0.6927 (+20.5) | 16/16 | **+0.2413 (+10.5)** | **16/16** |
| 140 | 50 | +0.8970 (+18.0) | 16/16 | **+0.3102 (+10.7)** | **16/16** |
| 140 | 60 | +1.0769 (+18.6) | 16/16 | **+0.3612 (+13.2)** | **16/16** |

**Read this carefully, because it is the single most consequential thing in this
review, and it cuts both ways.**

- The LLL residual is real, sign-consistent across every basis and every cell,
  and 10–20 sd from the null. The BKZ-30 residual is real at `d = 140` in all
  four windows and consistent with zero at `d = 100`. The instrument reported
  every one of these as "absent" (largest LLL shift anywhere: `+3.06 SE`).
- The residual is **1/15 to 1/50** of the unreduced value, and it is **5–15×
  below the instrument's own detection floor of `V ≈ 2.2`**. Its effect on `r`
  would be `≈ +0.0007`, about `0.35 SE`; resolving it statistically at 4·SE
  would need roughly **1000 frames per arm** rather than 8. That is why the
  instrument cannot see it, and it is not a bug.
- Its behaviour is exactly what a *presentation* artifact should do: larger at
  `d = 140` than `d = 100` (LLL is weaker relative to dimension), and reduced
  further by BKZ than by LLL. The natural candidate mechanism is that the tail
  of a weakly reduced basis retains partial `q`-vector structure. **I have not
  demonstrated that**, and I record it as a candidate, not a finding.
- **It is not a lattice property and I claim nothing from it.** `V` is a
  statistic of a *basis's* tail GSO frame. The same lattice under a different
  presentation gives a different `V`. Nothing here bears on attack cost, on any
  BKZ cost model, or on ML-KEM.

The correction to the report's headline is one word and it matters: replace
**"absent below gate in both LLL-only and BKZ arms"** with **"suppressed by
15–50× and, where measurable exactly, still nonzero"**.

---

## 5. The falsifier fired, and its firing carries no information about artifact status

The pre-registration predicts `D(beta)/D(30)` tracks `s(beta,d)`, the Beta law's
own coefficient of variation. Under the geometry of §3 that law is right in form
for the coordinate-aligned arm — where `V = beta(1−beta/d)` makes the variance
factor exactly `0.75` for all `beta`, so the whole `beta` dependence sits in the
Beta quantile — and **structurally wrong for the unreduced arm**, where
`V = beta²(d−k)/(kd)` grows quadratically in `beta`, giving a variance factor
`1 − beta/(4(d−beta))` that *falls* with `beta`. A growing departure was
predictable from the basis geometry before the run.

`D(60)/D(30)`:

| arm | d | measured | geometry model (§3, zero free parameters) | pre-registered `s(60)/s(30)` |
|---|---|---|---|---|
| unreduced | 100 | 1.1805 | 0.8040 | 0.5345 |
| unreduced | 140 | 2.0949 | **1.5441** | 0.6030 |
| coord `t=0` | 100 | 0.7249 | 0.5105 | 0.5345 |
| coord `t=0` | 140 | 0.7544 | 0.5534 | 0.6030 |

The model overshoots the *magnitude* of `D` by 1.0–1.7× — it is a second-moment
approximation applied to a `2^-10` tail quantile and should not be trusted for
magnitudes — but with no fitted parameters it gets the **sign**, the **rise at
`d=140`**, and the **`d=100, beta=60` reversal**: `V` falls from 24.995 to
16.269 when the window is forced out of the `k`-block (ratio 0.651) and measured
`D` falls 0.0786 → 0.0481 (ratio 0.612).

So: the executor was right to record FALSIFIED as it fell, and right that the
pre-registered law is "too crude". But the report then calls the firing *"the
canonical artifact tell named in the task card and in `docs/inventor-protocol.md`
Sec. 3, and I am recording it as one."* **That inference does not hold.** The
decay law was derived for a `beta`-independent alignment excess and applied to an
arm whose alignment excess grows like `beta²`. Its failure is a failure of the
predicted law, not a tell about the object. B2-A's most emphatic paragraph rests
on a mechanism that is false and a falsifier that was mis-specified for the arm
it was applied to.

The same correction applies more gently to the `NEITHER` verdict on the coord
arm: the geometry model gives 0.511/0.553 against the pre-registered 0.535/0.603
and a measured 0.725/0.754, so *both* laws miss in the same direction and
`NEITHER` reflects the crudeness of the second-moment mapping to a far-tail
quantile, not a property of the projector.

---

## 6. The INVALID verdict is the governing decision's grid. I measured the counterfactual.

`DEC-20260805-4823db` `next_actions` froze `t in {0, 0.05, 0.10, 0.25, 0.50,
0.75, 1.00}`. The executor implemented that grid, diagnosed it correctly
(range-midpoint at `t = 1/(d+1)` = 0.0099 / 0.0071, so the first interior point
is 5–7× past it), and refused to substitute a better one. **That was the right
call and I want it recorded as such.** The self-diagnosis in Part 6.3 is the
strongest piece of work in the package.

I ran the counterfactual the executor was right not to run. Same statistic, same
seeds, `d=100, beta=30`, on the grid the executor proposes as a successor:

| t | mean `r(2^-10)` | shift (SE) |
|---|---|---|
| 0.000 | 1.094824 | 50.05 |
| 0.002 | 1.065128 | 34.73 |
| 0.005 | 1.037267 | 20.17 |
| 0.010 | 1.017416 | 9.39 |
| 0.020 | 1.005148 | 3.14 |
| 0.050 | 1.001621 | 1.00 |

**Strictly decreasing, with every consecutive gap resolved at many SE.** G1
clears at 50.05 SE. G2's end is reproduced (the executor measured `t=1` at
1.02–2.19 SE; `t=0.05` here reads 1.00 SE). **G3 would pass.** The demonstration
would have returned **VALID**, and the real arm would have been interpretable.

Therefore: **the INVALID verdict is not a failure of the instrument. It is
self-punishment on a grid the governing decision chose badly**, and the honest
finding belongs against `DEC-20260805-4823db`, not against T2 or against the
executor.

*Discipline note on my own numbers:* this grid was chosen **after** seeing
B2-A's diagnosis. It is a red-team feasibility probe and is **not**
pre-registered evidence. It cannot discharge C3 and must not be cited as though
it could. It shows only that the repair works.

---

## 7. The Gaussian-error null of the null is a theorem, not a control

The report calls N1/N2 *"the sharpest control in the package"*. It is not; it is
the weakest, and the report's own Part 3 already contains the argument against
it: *"Recovering `Beta(beta/2,(d−beta)/2)` on the Haar arm is an INSTRUMENT
CHECK, never a control that passed. It is constructed by the theorem, not
discovered."*

Exactly the same holds for N2. The executor states the theorem himself in §1.5:
for a rotationally invariant error and **any** fixed rank-`beta` projector,
`R ~ Beta(beta/2,(d−beta)/2)` exactly. A statistic that is distribution-free by
theorem cannot fail unless the code is wrong. N2 therefore excludes exactly one
class: *a construction or code-path bug that manufactures a projector-dependent
reading independently of the error law*. That is a genuine and worthwhile unit
test, and it passed.

It does **not** exclude:

- anything running through the error's coordinate structure — which is
  everything the instrument exists to detect, and which §3 shows is a single
  scalar;
- a CBD sampler defect that only shows under CBD (partly covered by the separate
  moment checks, which pass);
- the entire blindness question of §4, since a spherical error is blind to
  coordinate structure *by construction*.

Recommend the Coordinator restate N1/N2 in the evidence record as an instrument
check, in the identical language Part 3 already uses for the Haar arm, and drop
"sharpest control".

---

## 8. Minor: Parts 7 and 8 report the same-labelled arm on different basis sets

`b2a.py` stage D reads `key = f"d{d}_b{ext_bkz}"` with `EXT_BKZ = 40`, so the
whole beta-trend — **including its `beta = 30` row** — uses `seed_basis(d,40,i)`,
while the cell tables in Part 7 use `seed_basis(d,30,i)`. Consequence, from the
JSON:

| | `D` | shift |
|---|---|---|
| Part 7, `d100_b30`, unreduced | 0.038967 | 27.11 SE |
| Part 8, `d=100, beta=30`, unreduced | 0.040738 | 20.30 SE |

Same label, same `(d, beta)`, 4.5% apart in `D` and 35% apart in SE, because
they are different lattices. This is **not** an error — the design note "holding
the reduction fixed at BKZ-40" is present and the JSON is fully consistent — but
the report never states that fixing the reduction also changes the basis seeds,
and the falsifier's `D(30)` denominator is therefore not the Part 7 headline. A
one-sentence note would close it. (The Haar arm *is* shared, since
`haar_frames` keys on the tail `beta`, so the discrepancy is purely the lattice
arm.)

---

## 9. Cheapest falsification of the headline

**Compute `V(Q) = Σ_a (P_aa − beta/d)²` on the frames the run already produced.
Milliseconds, zero error draws, zero quantile estimation, no statistics.**

That single number:

- falsifies "absent after LLL/BKZ" at 10–20 sd (§4);
- falsifies the `q·I` mechanism outright (§2);
- predicts the beta-trend's sign and its `d=100, beta=60` reversal with no fitted
  parameters (§5);
- makes the 4·SE gate, the 8-draw design, the `2^-20` error sets and the graded
  family redundant for the question actually asked.

Be precise about the saving, because it is not total: the 1068.35 core-seconds
of stage-A **reductions** are still needed — `V` is computed *from* a reduced
basis. What becomes unnecessary is the ~655 core-second measurement layer and,
more importantly, the entire inferential apparatus built on top of it. A
successor should measure `V` exactly and use the sampling instrument only where
`V` is *not* the sufficient statistic.

**The corresponding limit, which the campaign must record.** `T2` can see one
scalar. A tail frame with `V ≈ 0` but non-coordinate structure — alignment with
a secret direction, a rotated sparse structure, anything not expressible as
coordinate participation — is invisible to `T2` at any draw count. "Reduced tail
frames look Haar" is established *in `V`*; it is not established in general, and
the Gaussian null cannot establish it (§7).

---

## 10. Claim leakage

I found **no leakage into ML-KEM security claims**. `b2a_report.md` Part 11 is
clean and explicit. `b2bcd_notes.md` carries a Kyber512/768/1024 `dbeta` / bits
table but guards it hard: *"These are MODELLED cost-model estimates, not
measurements, and no row of this table is a property of ML-KEM"*, and *"none is
subtracted from the in-repo `primal_bdd` margins of 2.80 / 6.04 / 1.28 bits."*
The C1 Lane-A bound is derived as `X = 0` exactly from `M = 1`, with `Y = 0`, and
the derivation genuinely never enters a cost model.

One **wording risk**, not a violation: `b2bcd_notes.md` writes that `c(M)`
*"needs a distributional model of the projected error norm — which is exactly
what criterion C3 is measuring, and which B2-A adjudicates for the tested cells
only."* That sentence places a `d ≤ 140` toy instrument outcome inside a causal
chain whose other end is a Kyber1024 bit figure. The guardrail is present, but a
successor skimming for a chain from measurement to bits could join them. Suggest
the Coordinator harden it to name the scope gap in the same sentence.

---

## 11. What I could not check

- **`k ≠ d/2`.** The discriminating test between "window confined to the `I_k`
  block" (mine) and "window inside the `q·I` block" (the report's) needs a `k`
  where `k ≠ d−k`. Not run; cheap.
- **Whether the post-reduction `V` residual vanishes under stronger BKZ.** I ran
  BKZ-30 only (block size = `beta`, as the frozen code does). The `d=100` versus
  `d=140` contrast is *consistent* with a presentation artifact that reduction
  progressively removes, but two dimensions and one block size are not a trend.
- **`beta = 40` reduced frames at `d = 100`.** BKZ-40 costs ~47.9 s per basis;
  I used BKZ-30 frames and swept the tail window instead. That varies the window,
  not the reduction, exactly as the executor's own beta-trend does — and inherits
  the same limitation.
- **Whether `V` remains the sufficient statistic at `beta/d` far from the tested
  0.21–0.60.** The collapse in §3 is measured at `d=100, beta=30` only.
- **Anything at `beta = 606, d = 1420`.** Not attempted; out of scope.

**My compute.** Approximately 160 s of observed wall clock across reproduction,
geometry and Monte Carlo, in single-process runs with a possibly multithreaded
numpy. I did **not** instrument core-seconds, so treat that as an order of
magnitude and not a measurement. No repository file was written outside this
review directory; `fpylll 0.6.4` / `scipy 1.17.1` were installed to a scratchpad
target outside the repository, matching the versions in the run manifest.

---

## 12. Objections, ranked, for the Coordinator

1. **The headline sentence is wrong and should not enter an evidence record as
   written.** "Absent below gate in both LLL-only and BKZ arms in all four
   cells" is an upper bound reported as an absence. Exactly computed, the
   residual is +10.2 sd (LLL, `d=100`), +16.6 sd (LLL, `d=140`), +9.9 sd
   (BKZ-30, `d=140`), sign-consistent 16/16. Restate as suppression by 15–50×
   with a measured, nonzero remainder. (§4)

2. **The `q·I` block mechanism is false and must not be promoted to knowledge.**
   The window's energy in the `q·I` block is 0.00000; it lies in the `I_k` block
   with `T = beta²/k`. The boundary is `beta ≤ k`, right by coincidence at
   `k = d/2`. (§2)

3. **"The falsifier fired, therefore artifact" does not follow.** The
   pre-registered `1/sqrt(beta)` law was mis-specified for the unreduced arm; the
   growth it flags is predicted by the basis geometry with zero free parameters.
   Record FALSIFIED as the pre-registered branch it is, and delete the inference
   to "canonical artifact tell". (§5)

4. **The INVALID verdict is chargeable to `DEC-20260805-4823db`, not to the
   instrument or the executor.** On the successor grid the demonstration returns
   strictly monotone separations of 50.05 / 34.73 / 20.17 / 9.39 / 3.14 / 1.00
   SE and would pass G1∧G2∧G3. The decision froze a grid placed 5–7× past the
   family's informative range. Correct that in the decision record. (§6)

5. **Redesign the instrument around `V` before spending another batch on it.**
   `T2` is a `2^20`-sample estimator of a scalar computable exactly and freely
   from the same frames, with a resolution floor 10–50× above the effect that
   survives reduction. (§9)

6. **Downgrade N1/N2 from "sharpest control" to instrument check**, in the same
   language Part 3 already applies to the Haar arm. It is a theorem. (§7)

7. **A governance tension the Coordinator must resolve explicitly, in either
   direction.** `GOAL-MLKEM-005` C3 declares three branches and says *"NEITHER,
   with the sensitivity demonstration's failure recorded as an INSTRUMENT
   outcome"* is one of them, adding *"AGREEMENT SATISFIES C3 AS FULLY AS
   DEPARTURE."* Two batches have now adjudicated to that branch and both were
   recorded as C3 UNMET, each time because the *pre-registration* — not the
   statistic — was defective. That reading is defensible; a third pass under a
   third badly-placed grid would not be. Under CLAUDE.md rules 8 and 9 the
   Coordinator should either (a) state on the record why an instrument-outcome
   adjudication does not discharge a criterion whose text admits it, or (b)
   supersede C3's wording. The exit is now measured either way (§6), and the
   campaign has an unbounded budget, which makes a silent loop the expensive
   failure mode rather than the safe one.

**Nothing above changes any research status, and nothing above supports a
statement about ML-KEM security or any FIPS 203 parameter set.**
