# AM-1 measurement under the notarized pre-registration

TASK-20260806-ca4377 / BATCH-f19c37 / GOAL-MLKEM-005

Executor artifact. **OBSERVATIONS ONLY.** No status change, no hypothesis
disposition, no heuristic validated or refuted, no interpretation beyond the
verdicts the pre-registration declares, and **no claim about ML-KEM security or
about any FIPS 203 parameter set**. **Claim tier TOY.** Every number below is
measured at `d in {100, 140}`, `beta in {30, 40, 50, 60}` on q-ary bases with
`k = d/2`, `q = 3329`; none is transported to `beta = 606`, `d = 1420` or to any
other parameter set, by extrapolation or by analogy.

---

## 1. Notarization: the pre-registration sha256, verified

`measure.py` loads `prereg.md` **read-only**, re-hashes the file bytes, and
compares against the notarized receipt before touching a lattice. It aborts on
mismatch. The run printed:

```
NOTARIZED PRE-REGISTRATION VERIFICATION (prereg.md section 9)
  prereg_path      : coordination/goals/GOAL-MLKEM-005/batches/BATCH-f19c37/tasks/
                     TASK-20260806-5930ec/prereg.md
  prereg_bytes     : 31969
  recomputed_sha256                     : cc7f3e1992d9fc250c05b02fe0a2a03463ea2e795e1f236fbd1c72d0d731b302
  notarized_receipt_path_sha256         : cc7f3e1992d9fc250c05b02fe0a2a03463ea2e795e1f236fbd1c72d0d731b302
  notarized_receipt_prereg_sha256_field : cc7f3e1992d9fc250c05b02fe0a2a03463ea2e795e1f236fbd1c72d0d731b302
  producer_prereg_sha256_txt            : cc7f3e1992d9fc250c05b02fe0a2a03463ea2e795e1f236fbd1c72d0d731b302
  receipt_task_id  : TASK-20260806-53ad5c
  receipt_parent_sha: a2d0eba6703eb001ac0de35dd8e6e6f2a8b18128
  match            : True
  VERIFIED. The frozen specification is loaded read-only and unmodified.
```

Four independent carriers of that digest agree: the file recomputed here, the
receipt's `archive.path_sha256` entry, the receipt's separate `prereg_sha256`
field, and the producer's own `prereg_sha256.txt`. The notarizing commit
(TASK-20260806-53ad5c, parent `a2d0eba6`) is an ancestor of this run's HEAD
`d3e66a19`, so the freeze **predates this measurement in the git record** and
not merely in this report. Whether that closes the `EV-MLKEM-94f036` "HARNESS
GAP" is for the validator to judge against the git record, not for this
document to assert.

I did not edit `prereg.md`, re-derive any threshold, or add, remove or re-space
any grid point.

---

## 2. What was run

Same four cells, same frozen P1/P2 sampling parameters, same Haar null, same
null-arm-first discipline as BATCH-436ddd. The instrument (`reduce_one`, the
statistic, the frozen quantile estimator, `arm_stats`, `gate`, every seed
formula) is carried verbatim from that batch's `b2a.py`. Only the `t` grid, the
G3 rule, and the added `V` / L2 / novelty machinery differ.

| | |
|---|---|
| cells `(d, beta)` | (100,30), (100,40), (140,30), (140,40); `k = d/2`, `q = 3329` |
| error law | CBD_{eta=2}, `N = 2^20` per cell; plus iid N(0,1) for the null of the null |
| draws per arm | 8, every arm including the Haar null |
| grid | the 13 AM-1 points, verbatim |
| gate | `abs(D) >= 4.0 x SE_diff`, pooled two-arm SE, 8 draws each |
| G3 | tie-tolerant at `1.0 x SE_step`, scored under **both** conventions, **more severe recorded**; adjacency irrelevant |
| budget | **1898.56 of 3000 core-seconds (63.3%)**, 748.19 s wall, peak RSS 1.146 GB self + 0.062 GB children |

**The budget was not exhausted and no cell went unmeasured.** Timings:
stage A (reductions) 283.33 s wall / 1058.32 core-s; everything else 464.9 s
wall / 840.2 core-s. For comparison BATCH-436ddd spent 282.56 s / 1068.35 core-s
on the identical stage A, which is the first sign that the two runs are doing
the same thing.

Environment: Python 3.11.15, numpy 2.4.6, scipy 1.17.1, fpylll 0.6.4,
Linux-6.18.5-fc-v18-x86_64, 4 cores. scipy and fpylll were **not installed** in
the interpreter and were installed to a task-local `pip --target` directory
**outside** the repository, at exactly the versions BATCH-436ddd and
BATCH-a51f91 recorded. Version identity is what makes the reduction-reproduction
check below mean anything. Nothing was vendored into the repository.

---

## 3. The seeds are the cache -- regenerated and verified

No `.npz` reduction cache exists anywhere in the repository. All 32 reductions
were regenerated from `seed_basis(d, beta, i) = 700000 + d*1000 + beta*10 + i`
and compared, by tag, against the committed reduction metadata of **both** prior
batches:

| compared against | n | max b0-norm relative deviation | max GSO log2-slope absolute deviation |
|---|---|---|---|
| BATCH-436ddd (`b2a_results.json`) | 32 | **0.0** | **0.0** |
| BATCH-a51f91 (`results.json`) | 32 | **0.0** | **0.0** |

Thirty-two of thirty-two tags, exact in every compared field, against both
predecessors. These are the same 32 lattices.

Other instrument checks:

* QR tail frame vs fpylll GSO, max relative error `7.619107e-07`.
* Tail-frame orthonormality, max absolute deviation `5.565082e-08`.
* CBD_{eta=2} per-coordinate variance `0.999900` (d=100) / `1.000096` (d=140)
  against exactly `1.0`; fourth moment `2.499610` / `2.500359` against exactly
  `2.5`. The `mu_4 = 2.5` value is the one L2's `-0.5` coefficient rests on.
* **Gaussian-error null of the null: PASS in all four cells** (N1 and N2). It is
  reported as an **instrument check, not a control**: for a rotationally
  invariant error and any fixed rank-`beta` projector,
  `R ~ Beta(beta/2,(d-beta)/2)` exactly, so it cannot fail unless the code is
  wrong. Largest `abs(r(2^-10) - 1)` over all Gaussian arms and cells
  `0.001711`; largest `abs(r(2^-16) - 1)` `0.017943`; `t = 0` gate under the
  Gaussian error reaches `-0.17 / +0.54 / +0.28 / +2.24 SE` against a threshold
  of 4.
* **Null-arm-first**: P1 and P2 were computed and emitted on the Haar arm before
  any real arm was read. Both pass in all four cells. P1 passing on the Haar arm
  is a unit test constructed by the theorem, not a control that passed. Under
  AM-2, P1/P2 are **not** an adjudicating predicate here.
* `E[R] = beta/d` is FORCED for every projector, reduced or not, and carries
  zero information.

---

## 4. The graded family at all 13 grid points, per cell

`D = mean_j r_A(2^-10) - mean_j r_haar(2^-10)`. `V` is exact, from the frame,
with **zero error draws**. `D_pred` is L2 evaluated at that `V`, zero fitted
parameters. Every non-clearing row carries its upper bound.

`NOVEL` marks the 25-point NOVEL subset; `shared` marks the six `t` also in
BATCH-436ddd's grid; `probe` marks the three `(100,30)` points the red team
measured post-hoc and recorded there as **not** pre-registered evidence.


### d100_b30 — `E[V]_haar = 0.411765`, `V` at exact coordinate alignment `21.0000`

| t | class | mean r(2^-10) | sd | D | D/SE_diff | gate | V | D_pred(V) | upper bound if not cleared |
|---|---|---|---|---|---|---|---|---|---|
| 0.0 | shared | 1.095416 | 0.005130 | +0.096767 | +47.80 | CLEARS | 21.0000 | 0.147207 | — |
| 0.0025 | NOVEL | 1.057587 | 0.004276 | +0.058937 | +33.50 | CLEARS | 12.9512 | 0.087020 | — |
| 0.005 | probe | 1.037050 | 0.004116 | +0.038401 | +22.44 | CLEARS | 8.4735 | 0.055675 | — |
| 0.0075 | NOVEL | 1.024754 | 0.002487 | +0.026105 | +20.75 | CLEARS | 5.8825 | 0.038168 | — |
| 0.01 | probe | 1.017653 | 0.002412 | +0.019004 | +15.33 | CLEARS | 4.3039 | 0.027716 | — |
| 0.015 | NOVEL | 1.008438 | 0.002359 | +0.009789 | +7.98 | CLEARS | 2.6146 | 0.016703 | — |
| 0.02 | probe | 1.003599 | 0.002674 | +0.004950 | +3.79 | no | 1.8015 | 0.011465 | `abs(D) < 4.0 x SE_diff = 0.005220` |
| 0.03 | NOVEL | 1.001457 | 0.003205 | +0.002808 | +1.94 | no | 1.0903 | 0.006916 | `abs(D) < 4.0 x SE_diff = 0.005787` |
| 0.05 | shared | 0.999861 | 0.002488 | +0.001211 | +0.96 | no | 0.6606 | 0.004182 | `abs(D) < 4.0 x SE_diff = 0.005032` |
| 0.1 | shared | 1.000469 | 0.003191 | +0.001819 | +1.26 | no | 0.4640 | 0.002935 | `abs(D) < 4.0 x SE_diff = 0.005772` |
| 0.25 | shared | 1.001207 | 0.002204 | +0.002557 | +2.15 | no | 0.4153 | 0.002626 | `abs(D) < 4.0 x SE_diff = 0.004761` |
| 0.5 | shared | 1.001307 | 0.002622 | +0.002658 | +2.06 | no | 0.4129 | 0.002611 | `abs(D) < 4.0 x SE_diff = 0.005167` |
| 1.0 | shared | 1.001152 | 0.001987 | +0.002503 | +2.19 | no | 0.4146 | 0.002622 | `abs(D) < 4.0 x SE_diff = 0.004566` |

`DR = m(0) - m(1) = 0.094264 = 46.56 SE_diff(t=0)`.

### d100_b40 — `E[V]_haar = 0.470588`, `V` at exact coordinate alignment `24.0000`

| t | class | mean r(2^-10) | sd | D | D/SE_diff | gate | V | D_pred(V) | upper bound if not cleared |
|---|---|---|---|---|---|---|---|---|---|
| 0.0 | shared | 1.086334 | 0.002746 | +0.087353 | +66.24 | CLEARS | 24.0000 | 0.113765 | — |
| 0.0025 | NOVEL | 1.052000 | 0.002755 | +0.053019 | +40.13 | CLEARS | 14.7785 | 0.067482 | — |
| 0.005 | NOVEL | 1.033590 | 0.002518 | +0.034609 | +27.45 | CLEARS | 9.5532 | 0.042756 | — |
| 0.0075 | NOVEL | 1.022860 | 0.003055 | +0.023878 | +17.04 | CLEARS | 6.5464 | 0.028973 | — |
| 0.01 | NOVEL | 1.016277 | 0.003142 | +0.017295 | +12.14 | CLEARS | 4.7448 | 0.020862 | — |
| 0.015 | NOVEL | 1.009191 | 0.002970 | +0.010209 | +7.41 | CLEARS | 2.8648 | 0.012510 | — |
| 0.02 | NOVEL | 1.005954 | 0.002496 | +0.006972 | +5.55 | CLEARS | 1.9852 | 0.008642 | — |
| 0.03 | NOVEL | 1.002970 | 0.003344 | +0.003989 | +2.69 | no | 1.2316 | 0.005347 | `abs(D) < 4.0 x SE_diff = 0.005925` |
| 0.05 | shared | 1.002122 | 0.002927 | +0.003140 | +2.30 | no | 0.7789 | 0.003376 | `abs(D) < 4.0 x SE_diff = 0.005466` |
| 0.1 | shared | 1.001249 | 0.002483 | +0.002268 | +1.81 | no | 0.5601 | 0.002426 | `abs(D) < 4.0 x SE_diff = 0.005008` |
| 0.25 | shared | 1.000955 | 0.002270 | +0.001973 | +1.64 | no | 0.4886 | 0.002116 | `abs(D) < 4.0 x SE_diff = 0.004802` |
| 0.5 | shared | 1.001110 | 0.002871 | +0.002129 | +1.57 | no | 0.4757 | 0.002060 | `abs(D) < 4.0 x SE_diff = 0.005406` |
| 1.0 | shared | 1.001619 | 0.002659 | +0.002637 | +2.03 | no | 0.4711 | 0.002040 | `abs(D) < 4.0 x SE_diff = 0.005185` |

`DR = m(0) - m(1) = 0.084715 = 64.24 SE_diff(t=0)`.

### d140_b30 — `E[V]_haar = 0.331992`, `V` at exact coordinate alignment `23.5714`

| t | class | mean r(2^-10) | sd | D | D/SE_diff | gate | V | D_pred(V) | upper bound if not cleared |
|---|---|---|---|---|---|---|---|---|---|
| 0.0 | shared | 1.093523 | 0.003919 | +0.092762 | +52.56 | CLEARS | 23.5714 | 0.151331 | — |
| 0.0025 | NOVEL | 1.048169 | 0.003579 | +0.047408 | +28.35 | CLEARS | 12.4765 | 0.075902 | — |
| 0.005 | NOVEL | 1.027552 | 0.003741 | +0.026791 | +15.61 | CLEARS | 7.5085 | 0.044654 | — |
| 0.0075 | NOVEL | 1.018266 | 0.003027 | +0.017505 | +11.44 | CLEARS | 4.9882 | 0.029334 | — |
| 0.01 | NOVEL | 1.012875 | 0.003712 | +0.012114 | +7.09 | CLEARS | 3.5685 | 0.020854 | — |
| 0.015 | NOVEL | 1.007577 | 0.003798 | +0.006816 | +3.94 | no | 2.1336 | 0.012391 | `abs(D) < 4.0 x SE_diff = 0.006927` |
| 0.02 | NOVEL | 1.004855 | 0.003613 | +0.004094 | +2.43 | no | 1.4678 | 0.008500 | `abs(D) < 4.0 x SE_diff = 0.006726` |
| 0.03 | NOVEL | 1.001894 | 0.002981 | +0.001133 | +0.75 | no | 0.8923 | 0.005154 | `abs(D) < 4.0 x SE_diff = 0.006075` |
| 0.05 | shared | 0.999870 | 0.001761 | -0.000891 | -0.71 | no | 0.5413 | 0.003122 | `abs(D) < 4.0 x SE_diff = 0.005033` |
| 0.1 | shared | 0.998502 | 0.001972 | -0.002259 | -1.74 | no | 0.3722 | 0.002145 | `abs(D) < 4.0 x SE_diff = 0.005188` |
| 0.25 | shared | 0.998999 | 0.001618 | -0.001762 | -1.43 | no | 0.3212 | 0.001851 | `abs(D) < 4.0 x SE_diff = 0.004936` |
| 0.5 | shared | 0.999304 | 0.002200 | -0.001457 | -1.09 | no | 0.3141 | 0.001810 | `abs(D) < 4.0 x SE_diff = 0.005368` |
| 1.0 | shared | 0.998736 | 0.002877 | -0.002025 | -1.36 | no | 0.3122 | 0.001799 | `abs(D) < 4.0 x SE_diff = 0.005973` |

`DR = m(0) - m(1) = 0.094787 = 53.71 SE_diff(t=0)`.

### d140_b40 — `E[V]_haar = 0.402414`, `V` at exact coordinate alignment `28.5714`

| t | class | mean r(2^-10) | sd | D | D/SE_diff | gate | V | D_pred(V) | upper bound if not cleared |
|---|---|---|---|---|---|---|---|---|---|
| 0.0 | shared | 1.083027 | 0.002350 | +0.083185 | +77.24 | CLEARS | 28.5714 | 0.119288 | — |
| 0.0025 | NOVEL | 1.043630 | 0.003947 | +0.043788 | +28.17 | CLEARS | 15.2348 | 0.060634 | — |
| 0.005 | NOVEL | 1.026381 | 0.002581 | +0.026539 | +23.26 | CLEARS | 9.0865 | 0.035422 | — |
| 0.0075 | NOVEL | 1.017582 | 0.002116 | +0.017740 | +17.49 | CLEARS | 5.9694 | 0.023034 | — |
| 0.01 | NOVEL | 1.011948 | 0.002572 | +0.012106 | +10.63 | CLEARS | 4.2308 | 0.016234 | — |
| 0.015 | NOVEL | 1.005957 | 0.002867 | +0.006115 | +5.00 | CLEARS | 2.5011 | 0.009544 | — |
| 0.02 | NOVEL | 1.003672 | 0.002639 | +0.003831 | +3.31 | no | 1.7138 | 0.006523 | `abs(D) < 4.0 x SE_diff = 0.004630` |
| 0.03 | NOVEL | 1.001713 | 0.001868 | +0.001872 | +1.97 | no | 1.0464 | 0.003974 | `abs(D) < 4.0 x SE_diff = 0.003806` |
| 0.05 | shared | 1.000982 | 0.001160 | +0.001141 | +1.43 | no | 0.6493 | 0.002463 | `abs(D) < 4.0 x SE_diff = 0.003194` |
| 0.1 | shared | 1.000269 | 0.001716 | +0.000427 | +0.47 | no | 0.4630 | 0.001755 | `abs(D) < 4.0 x SE_diff = 0.003660` |
| 0.25 | shared | 0.999800 | 0.002381 | -0.000042 | -0.04 | no | 0.4072 | 0.001544 | `abs(D) < 4.0 x SE_diff = 0.004342` |
| 0.5 | shared | 1.000037 | 0.003312 | +0.000195 | +0.14 | no | 0.3984 | 0.001510 | `abs(D) < 4.0 x SE_diff = 0.005426` |
| 1.0 | shared | 1.001283 | 0.003506 | +0.001441 | +1.02 | no | 0.3943 | 0.001495 | `abs(D) < 4.0 x SE_diff = 0.005665` |

`DR = m(0) - m(1) = 0.081744 = 75.90 SE_diff(t=0)`.

**The grid did what AM-1 designed it to do.** The gate goes from CLEARS to
not-clearing inside the sampled range in every cell, rather than having
already crossed before the first interior point:

| cell | last t clearing | first t not clearing | midpoint t = 1/(d+1) |
|---|---|---|---|
| d100_b30 | 0.015 | 0.02 | 0.009901 |
| d100_b40 | 0.02 | 0.03 | 0.009901 |
| d140_b30 | 0.01 | 0.015 | 0.007092 |
| d140_b40 | 0.015 | 0.02 | 0.007092 |

---

## 5. G1, G2, G3 under **both** SE conventions, and the cell verdicts

`G1` (gate clears at `t = 0`) and `G2` (gate does not clear at `t = 1`) hold in
**all four cells**. The verdicts therefore turn entirely on G3.

| cell | G1 | G2 | increases | G3 paired | max step, paired | G3 unpaired | max step, unpaired | **recorded (more severe)** | **verdict** |
|---|---|---|---|---|---|---|---|---|---|
| d100_b30 | clears (+47.80 SE) | does not fire (+2.19 SE) | 3 | **FAIL** | **+1.343 SE** | TIE | +0.538 SE | FAIL (paired) | **INVALID** |
| d100_b40 | clears (+66.24 SE) | does not fire (+2.03 SE) | 2 | TIE | +0.766 SE | TIE | +0.368 SE | TIE (paired) | **PARTIAL** |
| d140_b30 | clears (+52.56 SE) | does not fire (-1.36 SE) | 2 | TIE | +0.711 SE | TIE | +0.551 SE | TIE (paired) | **PARTIAL** |
| d140_b40 | clears (+77.24 SE) | does not fire (+1.02 SE) | 2 | **FAIL** | **+2.171 SE** | TIE | +0.731 SE | FAIL (paired) | **INVALID** |

**Overall verdict = the most severe cell verdict = INVALID.**

Under the prereg's validity rule an INVALID overall verdict is an **INSTRUMENT
OUTCOME**: no mathematical conclusion is recorded, and the real arms are
reported as measured but **not interpreted**. `AGENTS.md` rule 3 and the
closure standard of `docs/inventor-protocol.md` section 4 both apply -- a failed
instrument is a statement about the instrument, and this verdict is **not**
evidence about lattices, about reduction, or about ML-KEM in either direction.

**The two conventions disagree, and the prereg's frozen tie-break decided it.**
Under the unpaired reading every cell is TIE and the overall verdict would be
PARTIAL. Under the paired reading -- which the prereg calls the correct SE for
this design, because `(S_j, G_j)` is shared across `t` within a draw -- two
cells FAIL. The prereg froze *record the MORE SEVERE of the two* precisely so
that permissiveness could not be bought by choosing a convention, and here that
clause is load-bearing rather than decorative: it is the difference between a
PARTIAL and an INVALID headline. Both readings are reported above and in
`results.json`.

Every step that increased, in every cell:

| cell | step | Delta (absolute) | Delta/SE_step paired | Delta/SE_step unpaired | Delta as fraction of that cell's DR | either endpoint clears its gate? |
|---|---|---|---|---|---|---|
| d100_b30 | `t = 0.05 -> 0.1` | +0.000608 | **+1.343** | +0.425 | 0.6% | no |
| d100_b30 | `t = 0.1 -> 0.25` | +0.000738 | +0.685 | +0.538 | 0.8% | no |
| d100_b30 | `t = 0.25 -> 0.5` | +0.000101 | +0.183 | +0.083 | 0.1% | no |
| d100_b40 | `t = 0.25 -> 0.5` | +0.000155 | +0.393 | +0.120 | 0.2% | no |
| d100_b40 | `t = 0.5 -> 1.0` | +0.000509 | +0.766 | +0.368 | 0.6% | no |
| d140_b30 | `t = 0.1 -> 0.25` | +0.000497 | +0.711 | +0.551 | 0.5% | no |
| d140_b30 | `t = 0.25 -> 0.5` | +0.000305 | +0.495 | +0.316 | 0.3% | no |
| d140_b40 | `t = 0.25 -> 0.5` | +0.000238 | +0.443 | +0.165 | 0.3% | no |
| d140_b40 | `t = 0.5 -> 1.0` | +0.001246 | **+2.171** | +0.731 | 1.5% | no |

Bold marks the two steps that exceed the frozen `1.0 x SE_step` tolerance under
the paired convention and therefore produce the two INVALID verdicts. An
objection about them is recorded in section 10.2; per prereg section 7.5 the
frozen specification was run anyway and these verdicts stand as computed.

---

## 6. The detection floor, as a **measured bracket** in `V` units

Per cell: the largest `V` among grid points whose gate does **not** clear, and
the smallest `V` among grid points whose gate does clear.

| cell | largest V not clearing (at t) | smallest V clearing (at t) | bracket | midpoint estimate |
|---|---|---|---|---|
| d100_b30 | 1.8015 (t = 0.02) | 2.6146 (t = 0.015) | **[1.8015, 2.6146]** | **2.2080** |
| d100_b40 | 1.2316 (t = 0.03) | 1.9852 (t = 0.02) | **[1.2316, 1.9852]** | **1.6084** |
| d140_b30 | 2.1336 (t = 0.015) | 3.5685 (t = 0.01) | **[2.1336, 3.5685]** | **2.8510** |
| d140_b40 | 1.7138 (t = 0.02) | 2.5011 (t = 0.015) | **[1.7138, 2.5011]** | **2.1074** |

The incumbent value the prereg quotes for `(100,30)` -- `V in [1.801, 2.718]`,
floor `~2.2`, from the red team's independently-constructed frame families -- is
**reproduced**: the lower end is the same `V = 1.801` frame, the upper end
tightens from 2.718 to 2.615 because the AM-1 grid supplies a clearing frame the
red team's grid did not, and the midpoint lands at 2.2080. The other three cells
had no asserted floor and are measured here for the first time.

In the statistic's own units the floor is `4.0 x SE_diff` per cell per arm at 8
draws, which is the number printed in every upper-bound cell of the tables in
section 4 and section 7.

---

## 7. The lattice arms, and the statement this instrument is forbidden to make

Read only after the demonstration, per the null-arm-first discipline. `V` excess
is over the exact Haar expectation `2 beta (d-beta) / (d (d+2))`, and its
significance is quoted in sd of the 8-frame mean.

| cell | arm | pooled r(2^-10) | D | D/SE_diff | gate | V | V excess | excess in sd of mean | D_pred(V) |
|---|---|---|---|---|---|---|---|---|---|
| d100_b30 | unreduced | 1.037839 | +0.038967 | +27.11 | CLEARS | 9.3628 | +8.9510 | +313.7 | 0.061788 |
| d100_b30 | lll_only | 0.998646 | -0.000180 | -0.12 | no | 0.6075 | **+0.1957** | **+7.0** | 0.003845 |
| d100_b30 | real_bkz (BKZ-30) | 0.998295 | -0.000118 | -0.06 | no | 0.3759 | -0.0358 | -2.1 | 0.002377 |
| d100_b40 | unreduced | 1.055401 | +0.056512 | +42.26 | CLEARS | 16.2446 | +15.7740 | +923.5 | 0.074605 |
| d100_b40 | lll_only | 1.000736 | +0.001594 | +1.22 | no | 0.7437 | **+0.2731** | **+5.5** | 0.003223 |
| d100_b40 | real_bkz (BKZ-40) | 1.000538 | +0.001324 | +1.25 | no | 0.5025 | +0.0319 | +1.7 | 0.002176 |
| d140_b30 | unreduced | 1.023262 | +0.022249 | +15.62 | CLEARS | 6.7504 | +6.4184 | +347.9 | 0.040009 |
| d140_b30 | lll_only | 1.000584 | -0.000186 | -0.10 | no | 0.7557 | **+0.4237** | **+10.4** | 0.004363 |
| d140_b30 | real_bkz (BKZ-30) | 0.999538 | -0.001335 | -0.78 | no | 0.4704 | **+0.1384** | **+6.4** | 0.002712 |
| d140_b40 | unreduced | 1.029434 | +0.029750 | +22.95 | CLEARS | 11.8075 | +11.4050 | +585.2 | 0.046449 |
| d140_b40 | lll_only | 1.003294 | +0.003358 | +3.06 | no | 1.1175 | **+0.7150** | **+13.0** | 0.004245 |
| d140_b40 | real_bkz (BKZ-40) | 1.000998 | +0.001092 | +0.89 | no | 0.5135 | **+0.1111** | **+6.5** | 0.001947 |

Upper bounds for every arm whose gate does not clear, as the prereg's wording
requirement demands:

| cell | lll_only | real_bkz |
|---|---|---|
| d100_b30 | `abs(D) < 4.0 x SE_diff = 0.005919` | `abs(D) < 4.0 x SE_diff = 0.007309` |
| d100_b40 | `abs(D) < 4.0 x SE_diff = 0.005248` | `abs(D) < 4.0 x SE_diff = 0.004225` |
| d140_b30 | `abs(D) < 4.0 x SE_diff = 0.007171` | `abs(D) < 4.0 x SE_diff = 0.006871` |
| d140_b40 | `abs(D) < 4.0 x SE_diff = 0.004395` | `abs(D) < 4.0 x SE_diff = 0.004897` |

Each is **an upper bound at 8 draws, `N = 2^20`**, and nothing more.

**The statement this run is forbidden to emit, and does not emit.** The prereg
freezes, before any of these numbers existed, that this instrument at this
configuration cannot resolve the known post-reduction residual, and forbids any
statement asserting that the departure has been driven to zero by reduction. The measurement
confirms the premise of that prohibition rather than escaping it: the LLL-only
`V` excess is **positive in all four cells**, at +5.5 to +13.0 sd of the frame
mean, while **not one of those arms clears its 4.0 SE gate**. The exactly
computed excesses here (+0.1957, +0.2731, +0.4237, +0.7150 for LLL-only;
+0.1384 for BKZ-30 at d = 140) reproduce the residuals the prereg quotes from
the red team (+0.1863, +0.4386, +0.1400) to within the difference expected
between these 8 bases and their 16. These sit 5-15x below the `V ~ 2.2` floor
bracketed in section 6. Reduction suppresses the quantity this instrument
measures by roughly 15-50x; it does not drive it to zero, and the gate's silence
on these arms is a resolution limit, not a finding.

P1 fails on one arm -- `unreduced` at d100_b40, pooled `r(2^-10) = 1.055401`
against a 0.05 tolerance. P1/P2 are recorded, not used to adjudicate: AM-2
removed that role after they returned identical verdicts on the Haar null arm
and the real arm in all four cells.

---

## 8. F-A -- the falsifier on the graded path

L2's content stripped of its magnitude map: **`D` depends on the frame only
through `V`, and increases with `V`.** `V` is exact and free for all of these
frames. Scope: the 13 graded points plus `unreduced` / `lll_only` / `real_bkz`
at each cell's own `(d, beta)`; frames below the floor carry no information and
are excluded before scoring, by declaration made before any data existed. The
beta-trend frames are scored separately, in F-B.

### 8.1 The admissibility split, stated in the prereg's own words

**Only the 25-point NOVEL subset is admissible as a test of L2. The shared
points and the whole beta trend are reproduction, because L2 postdates those
numbers.** The all-points F-A result below is a reproduction check and the F-B
result in section 9 is a reproduction; neither is independent evidence for L2.

The NOVEL subset, declared in the prereg before the run: `t in {0.0025, 0.0075,
0.015, 0.03}}` in all four cells (16 points), plus `t in {0.005, 0.01, 0.02}` in
the three cells other than `(100,30)` (9 points) -- **25 points, of which 18
clear their gate** and are scorable.

### 8.2 F-A1 (ordering -- the falsifier that counts)

L2 is FALSIFIED if some pair of gate-clearing frames has `V_1 > V_2` and
`D_1 < D_2 - 1.0 x SE(D_1 - D_2)`. Both SE conventions are reported; the paired
SE is the smaller and therefore makes falsification **easier**, so reporting it
is the reading adverse to L2.

| cell | subset | frames clearing | violating pairs, unpaired | violating pairs, paired | verdict (both conventions) | most adverse pair, in SE |
|---|---|---|---|---|---|---|
| d100_b30 | all points | 7 / 16 | 0 | 0 | **CONSISTENT** | -0.308 |
| d100_b30 | **NOVEL only** | 3 / 4 | 0 | 0 | **CONSISTENT** | -13.462 |
| d100_b40 | all points | 8 / 16 | 0 | 0 | **CONSISTENT** | -2.360 |
| d100_b40 | **NOVEL only** | 6 / 7 | 0 | 0 | **CONSISTENT** | -2.360 |
| d140_b30 | all points | 6 / 16 | 0 | 0 | **CONSISTENT** | -2.827 |
| d140_b30 | **NOVEL only** | 4 / 7 | 0 | 0 | **CONSISTENT** | -3.184 |
| d140_b40 | all points | 7 / 16 | 0 | 0 | **CONSISTENT** | -2.245 |
| d140_b40 | **NOVEL only** | 5 / 7 | 0 | 0 | **CONSISTENT** | -4.400 |

The *most adverse pair* column is the largest value of `(D_2 - D_1)/SE` over
pairs with `V_1 > V_2`; it is **negative in every case**, meaning that even the
least favourable ordered pair still has the higher-`V` frame carrying the larger
`D`, by the stated margin. Zero violating pairs anywhere, under either
convention, on either subset.

The tightest all-points case is instructive: at `(100,30)` the real `unreduced`
lattice frame (`V = 9.3628`, `D = +0.038967`) and the synthetic graded
frame at `t = 0.005` (`V = 8.4735`, `D = +0.038401`) -- two frames with
nothing in common but `V` -- sit 0.308 SE apart in the L2-favourable
direction.

### 8.3 F-A2 (shape -- scored, not falsifying on its own)

`rho(t) = [D_meas(t)/D_meas(0)] / [D_pred(V(t))/D_pred(V(0))]`, declared band
`[0.5, 2.0]`.

| cell | subset | points scored | verdict | max abs(log2 rho) | rho range |
|---|---|---|---|---|---|
| d100_b30 | all points | 6 | **CONSISTENT** | 0.1656 | 0.892 - 1.049 |
| d100_b30 | **NOVEL only** | 4 | **CONSISTENT** | 0.1656 | 0.892 - 1.040 |
| d100_b40 | all points | 7 | **CONSISTENT** | 0.1107 | 1.000 - 1.080 |
| d100_b40 | **NOVEL only** | 7 | **CONSISTENT** | 0.1107 | 1.000 - 1.080 |
| d140_b30 | all points | 5 | **CONSISTENT** | 0.0776 | 0.948 - 1.019 |
| d140_b30 | **NOVEL only** | 5 | **CONSISTENT** | 0.0776 | 0.948 - 1.019 |
| d140_b40 | all points | 6 | **CONSISTENT** | 0.1433 | 0.919 - 1.104 |
| d140_b40 | **NOVEL only** | 6 | **CONSISTENT** | 0.1433 | 0.919 - 1.104 |

Every scored point lies within `rho in [0.89, 1.10]`, well inside the declared
`[0.5, 2.0]` band. Note plainly that the band was set generously -- at the order
of the map's own documented 1.0-1.7x magnitude bias -- and that a CONSISTENT
verdict against a factor-of-two band is a weak test that the data happened to
pass by a wide margin. The margin is reported; the verdict is the declared one.

### 8.4 F-A3 (magnitude -- diagnostic only, no verdict attached)

| cell | D_meas / D_pred over gate-clearing graded points |
|---|---|
| d100_b30 | 0.586 - 0.690 |
| d100_b40 | 0.768 - 0.829 |
| d140_b30 | 0.581 - 0.625 |
| d140_b40 | 0.641 - 0.770 |

The L2 map overshoots the magnitude by roughly 1.2-1.7x, inside the 1.0-1.7x
range the prereg declared as L2's known defect **in advance**. Per section 6.1 no
threshold is attached to this and no verdict turns on it. Full per-point values
are in `results.json` under `F_A.F_A3_magnitude_diagnostic_only`.

---

## 9. F-B -- the beta trend, where L1 and L2 disagree

**F-B is a REPRODUCTION.** The unreduced, LLL-only, BKZ-40 and coord arms at
`beta in {30,40,50,60}` at both `d` were all measured in BATCH-436ddd, and L2
was formulated after those measurements were seen. Re-running them tests
reproducibility, the implementation, and L1 -- which was genuinely
pre-registered before the data existed -- but **it does not constitute an
independent test of L2.** The independent test of L2 in this batch is F-A on
the NOVEL subset (section 8).

**The basis-set caveat BATCH-436ddd's report did not state.** Holding the
reduction fixed at BKZ-40 means the beta trend reads `seed_basis(d, 40, i)`. Its
`beta = 30` row is therefore a **different basis set** from the `(d, 30)` cell
tables of sections 4 and 7, and its `D(30)` is **not** the cell-table headline.
For example `unreduced` at `d = 100`: the beta-trend row gives `D(30) = +0.040738`
on the BKZ-40 basis set, while the `(100,30)` cell table gives `+0.038967` on the
BKZ-30 basis set. Both are correct; they are different objects and must not be
quoted interchangeably.


### d100 -- reduction held at LLL + BKZ-40

| arm | D(30) | D(40) | D(50) | D(60) | V(30) | V(60) | ratio_meas | ratio_L1 | ratio_L2 | L1 | L2 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| unreduced | +0.040738 | +0.056512 | +0.078555 | +0.048091 | 9.357 | 16.269 | **1.1805** | 0.5345 | 0.8040 | **FALSIFIED** (artifact tell) | **FALSIFIED** |
| lll_only | +0.001808 | +0.001594 | +0.001168 | +0.001247 | 0.581 | 0.750 | — | 0.5345 | 0.5933 | NOT APPLICABLE | NOT APPLICABLE |
| real_bkz40 | +0.001233 | +0.001324 | +0.001127 | +0.000408 | 0.397 | 0.496 | — | 0.5345 | 0.5740 | NOT APPLICABLE | NOT APPLICABLE |
| coord_t0 | +0.096767 | +0.087353 | +0.078510 | +0.070148 | 21.000 | 24.000 | **0.7249** | 0.5345 | 0.5105 | NOT DISCRIMINATING | NOT DISCRIMINATING |

### d140 -- reduction held at LLL + BKZ-40

| arm | D(30) | D(40) | D(50) | D(60) | V(30) | V(60) | ratio_meas | ratio_L1 | ratio_L2 | L1 | L2 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| unreduced | +0.023895 | +0.029750 | +0.039424 | +0.050058 | 6.767 | 25.919 | **2.0949** | 0.6030 | 1.5442 | **FALSIFIED** (artifact tell) | **FALSIFIED** |
| lll_only | +0.001923 | +0.003358 | +0.001517 | +0.002711 | 0.840 | 1.477 | — | 0.6030 | 0.6860 | NOT APPLICABLE | NOT APPLICABLE |
| real_bkz40 | -0.001146 | +0.001092 | +0.000559 | -0.000162 | 0.392 | 0.693 | — | 0.6030 | 0.6900 | NOT APPLICABLE | NOT APPLICABLE |
| coord_t0 | +0.092762 | +0.083185 | +0.074256 | +0.069981 | 23.571 | 34.286 | **0.7544** | 0.6030 | 0.5534 | NOT DISCRIMINATING | NOT DISCRIMINATING |

**Reading the verdicts against the frozen table.**

* **`unreduced` is the arm that discriminates**, and `ratio_meas` falls outside
  the `+-25%` band around *both* laws at both `d`. The frozen table's
  outside-both-bands row makes that **L1 FALSIFIED and L2 FALSIFIED**, and that
  is what is recorded. L1 additionally trips the `0.90` artifact-tell branch
  (`ratio_meas >= 0.90` with `ratio_L1 <= 0.7`) at both `d`. For the record and
  without softening either verdict: L2 gets the *sign* right at `d = 140`
  (predicting growth, 1.5442, against a measured 2.0949) where L1 predicts decay
  (0.6030), and the two laws are separated by 50% at `d = 100` and 156% at
  `d = 140`. The frozen rule scores band membership, not sign alone, and both
  laws miss the band.
* **`lll_only` and `real_bkz40` are NOT APPLICABLE** at both `d`: `D(30)` does
  not clear its own `4.0 x SE_diff` gate, so there is no gate-clearing departure
  whose decay ratio could be scored. Each is reported as an upper bound at the floor:
  * d100 lll_only: `D(30)` at +1.07 SE, `|D| < 4.0 x SE_diff = 0.006762 (upper bound at 8 draws, N = 2^20)`
  * d100 real_bkz40: `D(30)` at +0.79 SE, `|D| < 4.0 x SE_diff = 0.006274 (upper bound at 8 draws, N = 2^20)`
  * d140 lll_only: `D(30)` at +1.05 SE, `|D| < 4.0 x SE_diff = 0.007352 (upper bound at 8 draws, N = 2^20)`
  * d140 real_bkz40: `D(30)` at -0.87 SE, `|D| < 4.0 x SE_diff = 0.005261 (upper bound at 8 draws, N = 2^20)`
  Their `V` values are nevertheless positive and rising with `beta` in every
  row, which is exactly the sub-floor regime section 7 describes.
* **`coord_t0` is NOT DISCRIMINATING by declaration**, made in the prereg before
  the run: at `t = 0`, `V = beta(1 - beta/d)` forces `f = 0.75` for every `beta`,
  collapsing L2's entire `beta` dependence into the same Beta quantile where L1
  puts it. Its raw scoring would have been FALSIFIED for both laws (measured
  0.7249 / 0.7544 against L1 0.5345 / 0.6030 and L2 0.5105 / 0.5534); that raw
  reading is recorded in `results.json` and is **not** counted, because
  agreement or disagreement on a non-discriminating arm carries no information
  about either law.

The `d = 100, beta = 60` reversal reproduces exactly: `V` falls from
24.995 at `beta = 50` to 16.269 at `beta = 60` (the tail window is
forced out of the `k`-block) and measured `D` falls from +0.078555 to
+0.048091 -- ratios 0.651 and 0.612.

`V` at the coordinate-aligned arm equals `beta(1 - beta/d)` to the printed digit
at every `beta` and every `d` (21.000, 24.000, 25.000, 24.000 at d = 100;
23.571, 28.571, 32.143, 34.286 at d = 140), which is the closed-form anchor the
prereg names and a check on the `V` code.

The beta trend is four points at two `d`. It is not a law.

---

## 10. Reproduction at the six shared `t`, and one objection

### 10.1 The shared points land on the same paths -- bitwise

The prereg requires `(S_j, G_j)` to be drawn from `seed_graded` **before and
independently of the `t` list**, so that going from 7 to 13 grid points cannot
perturb the paths. `measure.py` hoists that draw out of the `t` loop, which is
bit-identical to BATCH-436ddd's draw order and makes the independence
structural rather than incidental.

| cell | shared t compared | max absolute difference vs BATCH-436ddd | max difference in SE_diff | instrument discrepancy? |
|---|---|---|---|---|
| d100_b30 | 6 | **0.0** | 0.0 | no |
| d100_b40 | 6 | **0.0** | 0.0 | no |
| d140_b30 | 6 | **0.0** | 0.0 | no |
| d140_b40 | 6 | **0.0** | 0.0 | no |

All 24 shared points are **bitwise identical** to the committed BATCH-436ddd
values -- not merely within 1 SE_diff, but exactly equal. The prereg's clause
*so the two runs remain comparable at their shared points* is therefore
checkable and checked. No instrument discrepancy is present in any cell. The
extension from 7 to 13 grid points did not perturb the paths.

### 10.2 Objection recorded under prereg section 7.5, frozen specification run anyway

The prereg permits recording an objection to a frozen threshold **provided the
frozen specification is run regardless**, which is what happened; the section 5
verdicts stand exactly as the frozen rule computes them. The objection:

The paired `SE_step` and the gate's `SE_diff` are not commensurable, and the two
G3 FAILs live in the region where the gate has no resolution. Because
`(S_j, G_j)` is shared across `t`, adjacent frames at large `t` are nearly the
same frame, so the paired step differences are strongly correlated and
`SE_step_paired` becomes very small -- small enough to resolve steps far below
the instrument's own detection floor. Concretely:

| cell | violating step | Delta | that cell's gate width `4.0 x SE_diff` at those points | Delta/SE_step paired | either endpoint clears its gate? |
|---|---|---|---|---|---|
| d100_b30 | `t = 0.05 -> 0.1` | +0.000608 | 0.005772 | +1.343 | **no** |
| d140_b40 | `t = 0.5 -> 1.0` | +0.001246 | 0.005665 | +2.171 | **no** |

In both cases the step is smaller than the gate width at the very points being
compared, and **neither endpoint clears its gate** -- they are among the frames
the same design declares to carry no information. This is an observation about
the interaction of two thresholds, not a request to change either, and not a
claim that the PARTIAL reading is the right one. A successor that wants G3 and
the gate to speak the same language would have to state the relation between
`SE_step` and `SE_diff` in advance -- before seeing which steps violate.

---

## 11. What I could not evaluate

* **`k != d/2`.** L2 puts the spill boundary at `beta <= k` and the superseded
  mechanism puts it at `beta <= d - k`; both tested `d` have `k = d/2`, so the
  two are numerically indistinguishable in every cell measured here. The prereg
  names this the cheapest falsification of L2 and places it **out of scope**;
  this measurement did not test it and does not claim to have. That untested
  discriminator remains the largest single hole in L2's support.
* **A matched real arm at `beta > 40`.** The beta trend varies `beta` on a
  reduction held fixed at BKZ-40; BKZ-50/60 reductions were not run. This run's
  own stage A measures the growth that makes them unaffordable: mean BKZ seconds
  per basis
  0.9 s at (100,30), 46.6 s at (100,40), 2.5 s at (140,30), 80.7 s at (140,40).
  One more step at that factor puts eight BKZ-50 bases well past this task's
  entire budget. This is an infrastructure limit, not a result, in either
  direction.
* **Whether the notarization closes the `EV-MLKEM-94f036` harness gap.** The
  prereg assigns that judgement to the validator against the git record. I
  report the hashes and the parent commit and stop there.
* **Any statistical statement about the LLL/BKZ `V` residuals.** They are
  exactly computed on 8 frames per arm and are positive at 5.5-13.0 sd of the
  frame mean, but this instrument's sampling layer cannot resolve their effect
  on `r(2^-10)` at 4 SE; the prereg's estimate is that roughly 1000 frames per
  arm would be needed against the 8 this design runs. No such run was attempted.
* **Nothing about ML-KEM.** No FIPS 203 parameter set was touched, no cost model
  was entered, and no number here is transported anywhere.

---

## 12. Deliverables and how to re-verify

Four files, all inside `tasks/TASK-20260806-ca4377/`: `measure.py`,
`results.json`, `report.md`, `run_manifest.yaml`.

1. `sha256sum` the pre-registration and compare against the notarized receipt
   and `prereg_sha256.txt` -- three carriers, all quoted in section 1.
2. Re-run `measure.py --mode full`; it re-checks the hash and aborts on
   mismatch. All 32 reductions regenerate from seeds; `instrument_checks`
   carries the per-tag deviations against both prior batches.
3. Recompute any gate from `results.json`: every arm's per-draw `r(2^-10)`
   values are serialised under `ratio_p2em10_over_draws.values`, and every G3
   step carries both SE conventions under
   `sensitivity_demonstration.G3_tie_tolerant.steps`.
4. `V` is deterministic and free -- recompute it from any frame in milliseconds
   with zero error draws and compare against `frame_V`.

A note on provenance, recorded rather than smoothed over: the measurement
execution resolved the paths to the two prior batches one directory level too
high and therefore **silently skipped** both reproduction comparisons. The paths
were corrected and the two comparisons recomputed with `measure.py --postcheck`
at 2026-08-06T12:47:06Z, **entirely from values this run had already recorded**
-- no lattice was reduced, no error drawn, no arm statistic recomputed. Every
measured number in `results.json` comes from the single authorised run; the
post-check adds only the two derived comparison blocks, and `results.json`
carries a `postcheck` record saying so. A re-run of the corrected script
produces both blocks inline.

---

## 13. Scope

Claim tier **TOY**. This is an executor artifact of observations under a
notarized frozen specification. It changes no status, disposes of no hypothesis,
promotes no knowledge, and adjudicates nothing. The overall demonstration
verdict is **INVALID**, which under the pre-registration is an instrument
outcome and is not evidence about lattices, about reduction, or about ML-KEM in
either direction; the real arms are reported as measured and are not
interpreted. Every negative this instrument can emit is an upper bound at the
floor bracketed in section 6, and every such arm carries that bound explicitly.
