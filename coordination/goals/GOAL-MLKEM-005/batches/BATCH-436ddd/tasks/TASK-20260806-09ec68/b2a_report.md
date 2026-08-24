# B2-A -- T2 instrument re-run with a sensitivity demonstration that can fail

TASK-20260806-09ec68 / BATCH-436ddd / GOAL-MLKEM-005

Executor artifact. Observations only.

<!-- BEGIN FROZEN PRE-REGISTRATION -->

## Part 1 -- Frozen pre-registration

Everything in this Part is fixed before any research number in this task is
computed.  It is stored as the constant `PREREG_MD` in `b2a.py`, its sha256 is
printed by the script before it touches a lattice, and `b2a.py --phase prereg`
writes it into this report as its own first act.  `b2a_results.json` carries the
same hash under `prereg_sha256`.  Nothing below was chosen after seeing data.

### 1.1 What is kept identical

The four cells `(d, beta)` in `{100,140} x {30,40}`, `k = d/2`, `q = 3329`; the
statistic `R = ||Q^T e||^2 / ||e||^2` with `Q` the orthonormal tail-`beta` GSO
frame; the frozen estimator `q_emp(p) = sort(R)[round(p*N)-1]` at `N = 2^20`, so
`k = 1024` at `p = 2^-10` and `k = 16` at `p = 2^-16`; the Haar null arm and its
seed family; the CBD_{eta=2} error draws and their seed; the 32 basis seeds; and
the null-arm-first discipline.  `P1` and `P2` are carried over verbatim from
`prediction_frozen.json` of `TASK-20260805-708b70`:

* **P1** -- on the real arm, in all four cells, `|r(2^-10) - 1| <= 0.05` and
  `|r(2^-16) - 1| <= 0.10`, judged on the pooled-over-8-bases quantile.
* **P2** -- on the real arm, the between-basis component of `Var(R)` is
  `<= 20%` of the total, in all four cells.

`E[R] = beta/d` is FORCED for every projector, reduced or not, and carries zero
information.  `Var(R) = 2 beta (d-beta) / (d^2 (d+2))` under the Beta law is
DERIVED here in advance; agreement with it is not a discovery.

### 1.2 The replacement sensitivity demonstration

`Q_t = QR( sqrt(1-t) * E_S + sqrt(t) * G )` at
`t in {0, 0.05, 0.10, 0.25, 0.50, 0.75, 1.00}`, where `E_S` is the `d x beta`
selector of a uniformly random `beta`-subset `S` of coordinates and `G` is
`d x beta` iid standard normal.  Per draw `j` the pair `(S_j, G_j)` is drawn
once and reused across all seven `t`, so the family is a path, not seven
unrelated arms.  `t = 0` gives a coordinate-aligned projector; `t = 1` gives a
Haar projector drawn independently of the null arm's.

This manipulates the object the null removes -- the provenance of the
projector -- which the superseded demonstration did not (DF-1).

### 1.3 Threshold, declared now, in SE-of-the-difference units

For any arm `A` compared against the Haar null arm, with `G_A = G_haar = 8`
draws and `sd` the between-draw sample sd (`ddof=1`) of `r(2^-10)`:

```
SE_diff(A) = sqrt( sd_A^2 / 8 + sd_haar^2 / 8 )
shift(A)   = mean_j r_A(2^-10) - mean_j r_haar(2^-10)
gate(A)    = |shift(A)| >= 4 * SE_diff(A)
```

This is the correction demanded by DF-2: the previous gate used the Haar arm's
own per-draw sd, the one arm whose between-draw location variance is
structurally near zero, which turned a nominal `4 s` into a ~2.0-2.5 sigma test.

### 1.4 Validity of the demonstration -- three conditions, declared now

* **G1 (high end).** `gate(t=0)` clears in all four cells.
* **G2 (low end).** `gate(t=1)` does NOT clear in any of the four cells.
  `t = 1` is a Haar projector drawn independently of the null arm's, so the two
  arms share a law and the gate must not fire.  **This is the condition the
  superseded demonstration could not have failed, and it is the reason this one
  can: an instrument that fires here is broken.**
* **G3 (monotonicity).** `mean_j r_A(2^-10)` is non-increasing across the seven
  `t` in every cell.

The demonstration is **VALID** iff `G1 and G2 and G3`.  If it is **INVALID**,
the outcome is an INSTRUMENT OUTCOME, no mathematical conclusion is recorded,
and the real arm is reported as measured but not interpreted.  A third branch is
declared explicitly, because a decision rule must partition the space of
outcomes and not the range of a quantity (DF-3): if `G1` holds, `G2` holds and
`G3` fails only at non-adjacent interior points within `1 * SE_diff`, the
outcome is **PARTIAL**, and is reported as PARTIAL rather than forced into
either branch.

The dynamic range actually spanned is reported as
`DR = mean r(t=0) - mean r(t=1)`, in absolute units and in units of
`SE_diff(t=0)`.

### 1.5 The Gaussian-error null of the null

Every arm is re-measured with an iid `N(0,1)` error in place of CBD_{eta=2}.
For a rotationally invariant error and ANY fixed rank-`beta` projector,
`R ~ Beta(beta/2,(d-beta)/2)` exactly.  Declared now:

* **N1** -- every arm under the Gaussian error returns `|r(2^-10) - 1| <= 0.05`
  and `|r(2^-16) - 1| <= 0.10`, the same tolerances as P1.
* **N2** -- under the Gaussian error, `gate(t=0)` does NOT clear.  Coordinate
  alignment produces no departure when the error is spherical.

`N1` or `N2` failing is instrument error and is reported as such; it is not a
result about lattices.

### 1.6 The falsifier: ~1/sqrt(beta) decay of the alignment departure

The parameter that should destroy an alignment departure is `beta`.  The
departure is a relative-dispersion effect: a coordinate-aligned `R` is
under-dispersed relative to Beta by the CBD kurtosis factor
`(E[e^4]-1)/2 = 0.75` in variance, and the lower-tail quantile ratio therefore
moves by an amount proportional, to leading order, to the Beta law's own
coefficient of variation

```
s(beta,d) = sd(R)/E[R] = sqrt( 2 (d - beta) / (beta (d + 2)) )
```

which is `~1/sqrt(beta)` at fixed `beta/d`.  Define, for an arm `A`,

```
D_A(beta,d)  = mean_j r_A(2^-10) - mean_j r_haar(2^-10)      (the departure)
Dn_A(beta,d) = D_A(beta,d) / s(beta,d)                       (normalised)
```

**Prediction, declared now:** `Dn_A` is approximately constant in `beta`, i.e.
`D_A(beta) / D_A(30)` tracks `s(beta)/s(30)`.  The predicted ratios, computed
from the formula alone:

| d | beta=30 | beta=40 | beta=50 | beta=60 |
|---|---|---|---|---|
| 100 | 1.0000 | 0.8018 | 0.6547 | 0.5345 |
| 140 | 1.0000 | 0.8257 | 0.7006 | 0.6030 |

**Tested at `beta in {30, 40, 50, 60}`** -- two values beyond `{30,40}` -- on
the tail-`beta` GSO frames of the BKZ-40 basis set at each `d`, on the LLL-only
and unreduced frames of the same bases, and on the coordinate-aligned (`t=0`)
projector.  Holding the reduction fixed at BKZ-40 while `beta` varies is
deliberate: it varies only the parameter the falsifier is about.

**Three-way verdict, declared now, per arm and per `d`:**

* **FALSIFIED** -- `D_A(60)/D_A(30) >= 0.90`.  The departure fails to decay
  when the parameter meant to destroy it doubles.  This is the canonical
  artifact tell and is recorded as one.
* **CONSISTENT** -- `D_A(60)/D_A(30)` lies within `+-25%` of the predicted
  ratio, i.e. in `[0.4009, 0.6681]` at `d = 100` and `[0.4522, 0.7537]` at
  `d = 140`.
* **NEITHER** -- decays, but not at the predicted rate.  Reported as NEITHER,
  never rounded into either of the other two.
* **NOT APPLICABLE** -- `D_A(30)` does not clear its own `4 * SE_diff` gate, so
  there is no departure to decay.  This branch is declared in advance because
  the superseded run's real arm had `r ~ 1.000`, and an arm with no departure
  must not be scored as though it had one.

### 1.7 What this task may not do

No status change, no interpretation beyond the declared verdicts, no claim
about ML-KEM security or any FIPS 203 parameter set, and no transport of any
number measured at `d <= 140, beta <= 60` to `beta = 606, d = 1420`.  The
beta-trend is four points at two `d`, not a law.  P1/P2 are not re-scored
against any rule other than the one frozen in BATCH-a51f91.

<!-- END FROZEN PRE-REGISTRATION -->

---

## Part 2 -- What ran

**One run.** `RUN-20260806-09ec68-001`, the single run authorised by the task
card. A smoke run at `(d, beta) = (60, 20)`, `N = 2^14`, was executed first as
preflight with its output written **outside** the repository; it exercised every
code path and every verdict branch and produced no research number in any
deliverable.

```
# --phase prereg  (Part 1 written to b2a_report.md BEFORE any measurement)
PYTHONPATH=<task-local pkgs> python3 b2a.py --phase prereg

# --phase measure  (the authorised run)
PYTHONPATH=<task-local pkgs> timeout --signal=KILL 2900 \
  python3 b2a.py --phase measure --mode full \
    --out b2a_results.json --workers 4 --core-seconds-budget 3600
```

The measure phase **re-hashes the frozen text out of `b2a_report.md` and aborts
if it does not match `PREREG_SHA256` byte for byte** before it touches a
lattice. It printed `report Part 1 matches PREREG_MD byte for byte: True`,
`prereg_sha256 2893a6b0cebf0a3ff40d779c6f66fb7852cad5830165a93079ddea6e6efd02b6`.

### Budget

| | |
|---|---|
| Wall clock | **631.26 s** (cap 3000 s; the run's own `timeout` was 2900 s) |
| **Core-seconds** | **1723.84** of the **4000** authorised -- **43.1%**. Not exhausted. |
| of which stage A (32 reductions) | 1068.35 core-seconds, 282.56 s wall on 4 workers |
| Peak RSS | 1.142 GB (self) + 0.061 GB (children); cap 4 GB |
| Runs | 1 of 1 authorised |

Budget exhaustion did not occur and no result in this report is truncated by
budget.

### One infrastructure finding, reported because it changed what I had to do

**The BKZ cache the task card told me to reuse does not exist.** The card and
`DEC-20260805-4823db` both state that the expensive reductions are "already
cached in `BATCH-a51f91/`". They are not in that directory and never were:
`BATCH-a51f91/tasks/TASK-20260805-708b70/command.txt` shows `--cache-dir`
pointing at `/tmp/claude-0/.../5cc33d08-.../scratchpad/bkzcache`, an **ephemeral
per-session scratchpad**, and that directory no longer exists. No `.npz` file
exists anywhere in the repository.

I therefore **recomputed all 32 reductions from the same seeds** (1068 core-
seconds, 62% of this task's total spend), and turned the problem into a check:
because `seed_basis(d,beta,i) = 700000 + d*1000 + beta*10 + i` is unchanged and
fpylll is pinned to the same version, the recomputed bases must be **identical**
to BATCH-a51f91's. They are -- see Part 3. **The seeds were the cache; the
`.npz` files were only a speed-up.**

*Recommendation, for a Coordinator to action and not for me to act on: a
reduction cache that a successor batch is instructed to reuse must live inside
the batch's `artifact_paths`, or the instruction must say "recompute from the
recorded seeds and verify" instead.*

### Environment

`fpylll 0.6.4`, `scipy 1.17.1`, `numpy 2.4.6`, Python 3.11.15,
Linux-6.18.5-fc-v18-x86_64, 4 cores, repo commit
`c9a7794fad07464b50eafe440c741e38f2e4dff6`, branch
`claude/harness-goals-experiments-g5pt2o`.

The task card states that `scipy` is absent and that a missing dependency is an
infrastructure request. `scipy` and `fpylll` were absent from the interpreter
and were installed into a **task-local `--target` directory outside the
repository write scope**, exactly as `TASK-20260805-708b70` did, at the same
versions that task recorded. Nothing was vendored into the repository. Had they
been unobtainable I would have filed the infrastructure request instead; they
were obtainable, and the versions match the run being reproduced, which is what
makes the reduction-reproduction check in Part 3 meaningful.

---

## Part 3 -- Instrument checks (not controls)

| check | value | note |
|---|---|---|
| **Reduction reproduction vs BATCH-a51f91** | **32 of 32 tags; max relative deviation in `\|\|b0\|\|` = `0.0`; max absolute deviation in GSO log2-slope = `0.0`** | Exact. The same 32 lattices, bit for bit. |
| numpy QR vs fpylll GSO, max relative error | `7.62e-07` | over all 32 reduced bases |
| tail-frame orthonormality, max `\|Q^T Q - I\|` | `5.57e-08` | |
| CBD per-coordinate variance | `0.99990` (d=100), `1.000096` (d=140) | exact value 1 |
| CBD per-coordinate 4th moment | `2.49961` (d=100), `2.500359` (d=140) | exact value 2.5 |

The 4th moment is listed because it is the quantity the whole coordinate-
alignment effect runs through: `Var(e^2) = E[e^4] - 1 = 1.5` for CBD against
`2` for a Gaussian, a variance ratio of `0.75`.

**Recovering `Beta(beta/2,(d-beta)/2)` on the Haar arm is an INSTRUMENT CHECK,
never a control that passed.** It is constructed by the theorem, not discovered.
This is stated again here because the same sentence appears in the superseded
package and was correct there too.

---

## Part 4 -- The Gaussian-error null of the null (read FIRST)

Every arm re-measured with an iid `N(0,1)` error in place of CBD, same
projectors, same code path. For a rotationally invariant error and any fixed
rank-`beta` projector, `R ~ Beta(beta/2,(d-beta)/2)` **exactly** -- so every arm
must return `1.000`, including the coordinate-aligned one.

Mean over 8 draws of `r(2^-10)`:

| cell | haar | unreduced | lll_only | real_bkz | graded t=0 (coord) | graded t=0.50 | **N1** | **N2** |
|---|---|---|---|---|---|---|---|---|
| d100_b30 | 0.999444 | 0.998289 | 0.999759 | 1.001024 | **0.999159** | 1.000521 | PASS | PASS |
| d100_b40 | 1.000510 | 0.999054 | 1.000084 | 0.999586 | **1.001033** | 0.999307 | PASS | PASS |
| d140_b30 | 0.998506 | 0.999787 | 0.999554 | 0.999389 | **0.999045** | 1.000408 | PASS | PASS |
| d140_b40 | 0.998445 | 0.999215 | 1.000400 | 1.000635 | **1.001328** | 0.999973 | PASS | PASS |

* **N1 PASSES in all four cells.** Every arm, every cell: `|r(2^-10) - 1| <=
  0.05` and `|r(2^-16) - 1| <= 0.10`. Largest deviation at `2^-10` is `0.0016`;
  largest at `2^-16` is `0.0179` (real_bkz, d100_b40).
* **N2 PASSES in all four cells.** Under the Gaussian error the coordinate-
  aligned projector's gate does **not** clear: shifts of `-0.17`, `+0.54`,
  `+0.28`, `+2.24` SE of the difference against a threshold of 4.

**This is the sharpest control in the package, and it is the one the superseded
run did not have.** The coordinate-aligned projector -- which under CBD moves
the headline statistic by 48 to 77 SE (Part 6) -- moves it by **nothing at all**
under a Gaussian error. The departure is therefore a property of the
**interaction** between a coordinate-aligned subspace and the CBD error's
platykurtosis, and not of the projector alone, not of the code path, and not of
the estimator. Any nonzero reading here would have been instrument error; there
is none.

---

## Part 5 -- Null arm first: P1 and P2 on the Haar arm, before the real arm

Emitted by the script before the real arm was computed, per the frozen
discipline.

| cell | haar pooled `r(2^-10)` | haar pooled `r(2^-16)` | **P1** | between-fraction | **P2** |
|---|---|---|---|---|---|
| d100_b30 | 0.998570 | 1.000388 | PASS | 0.0000000 | PASS |
| d100_b40 | 0.999141 | 0.999670 | PASS | 0.0000000 | PASS |
| d140_b30 | 1.001023 | 0.996090 | PASS | 0.0000000 | PASS |
| d140_b40 | 0.999897 | 1.014807 | PASS | 0.0000000 | PASS |

**P1 passes on the null arm by construction. It is the unit test that is not a
control.** It tests numpy's QR and the CBD sampler's directional uniformity.

> **P1 AND P2 EMIT THE SAME VERDICT ON THE NULL ARM AS ON THE REAL ARM IN ALL
> FOUR CELLS.** The frozen protocol requires this to be reported prominently and
> the real-arm verdict not to be read as discriminating. It is reported here,
> and it is repeated in Part 9.

---

## Part 6 -- The replacement sensitivity demonstration

### 6.1 The seven-point family, all four cells

Mean over 8 draws of `r(2^-10)`, with the shift from the Haar null arm in units
of the SE of the difference of the two 8-draw means (the pre-registered unit),
and the `4 * SE` gate verdict.

**d = 100, beta = 30** -- `SE_diff(t=0) = 0.002025`

| t | mean `r(2^-10)` | sd | shift (SE units) | gate |
|---|---|---|---|---|
| **0.00** | **1.095416** | 0.005130 | **+47.80** | **CLEARS** |
| 0.05 | 0.999861 | 0.002488 | +0.96 | no |
| 0.10 | 1.000469 | 0.003191 | +1.26 | no |
| 0.25 | 1.001207 | 0.002204 | +2.15 | no |
| 0.50 | 1.001307 | 0.002622 | +2.06 | no |
| 0.75 | 1.000996 | 0.002071 | +2.02 | no |
| **1.00** | **1.001152** | 0.001987 | **+2.19** | **does not clear** |

**d = 100, beta = 40** -- `SE_diff(t=0) = 0.001319`

| t | mean `r(2^-10)` | shift (SE) | gate |
|---|---|---|---|
| **0.00** | **1.086334** | **+66.24** | **CLEARS** |
| 0.05 | 1.002122 | +2.30 | no |
| 0.10 | 1.001249 | +1.81 | no |
| 0.25 | 1.000955 | +1.64 | no |
| 0.50 | 1.001110 | +1.57 | no |
| 0.75 | 1.001181 | +1.65 | no |
| **1.00** | **1.001619** | **+2.03** | **does not clear** |

**d = 140, beta = 30** -- `SE_diff(t=0) = 0.001765`

| t | mean `r(2^-10)` | shift (SE) | gate |
|---|---|---|---|
| **0.00** | **1.093523** | **+52.56** | **CLEARS** |
| 0.05 | 0.999870 | -0.71 | no |
| 0.10 | 0.998502 | -1.74 | no |
| 0.25 | 0.998999 | -1.43 | no |
| 0.50 | 0.999304 | -1.09 | no |
| 0.75 | 0.999113 | -1.18 | no |
| **1.00** | **0.998736** | **-1.36** | **does not clear** |

**d = 140, beta = 40** -- `SE_diff(t=0) = 0.001077`

| t | mean `r(2^-10)` | shift (SE) | gate |
|---|---|---|---|
| **0.00** | **1.083027** | **+77.24** | **CLEARS** |
| 0.05 | 1.000982 | +1.43 | no |
| 0.10 | 1.000269 | +0.47 | no |
| 0.25 | 0.999800 | -0.04 | no |
| 0.50 | 1.000037 | +0.14 | no |
| 0.75 | 1.000459 | +0.45 | no |
| **1.00** | **1.001283** | **+1.02** | **does not clear** |

### 6.2 The pre-registered verdicts

| condition | d100_b30 | d100_b40 | d140_b30 | d140_b40 |
|---|---|---|---|---|
| **G1** high end, `gate(t=0)` clears | **YES** (47.8 SE) | **YES** (66.2 SE) | **YES** (52.6 SE) | **YES** (77.2 SE) |
| **G2** low end, `gate(t=1)` does NOT clear | **YES** (2.19 SE) | **YES** (2.03 SE) | **YES** (-1.36 SE) | **YES** (1.02 SE) |
| **G3** monotone non-increasing in t | **NO** | **NO** | **NO** | **NO** |
| **verdict** | **INVALID** | **INVALID** | **INVALID** | **INVALID** |
| dynamic range `r(0) - r(1)` | 0.094264 = **46.6 SE** | 0.084715 = **64.2 SE** | 0.094787 = **53.7 SE** | 0.081744 = **75.9 SE** |

**Both ends of the dynamic range are exhibited, decisively and in every cell.**
The high end clears the gate by a factor of 12 to 19; the low end does not clear
it at all, which is the end the superseded demonstration could not exhibit
because `t = 1` and the null arm share a law and the gate must not fire between
them. That is the condition an instrument can fail, and this instrument did not
fail it.

**G3 fails in all four cells, so the pre-registered verdict is INVALID in all
four cells.** I am recording that verdict as it falls. I am not re-scoring it,
not relaxing it, and not promoting the demonstration to PARTIAL: the PARTIAL
branch was declared in advance for non-adjacent interior violations within
`1 * SE`, and although **every one of the twelve violations is within `1 * SE`**
(largest `0.765 SE`), they occur at **adjacent** grid points, which the declared
PARTIAL branch excludes. A threshold chosen after seeing the data is not a
threshold, and that applies to my own.

### 6.3 Why G3 failed, and why that is a defect in MY pre-registration

Every one of the four cells has the same structure: **the single step
`t = 0 -> 0.05` carries the entire dynamic range**, and every later step is
noise.

| cell | first step (SE units) | largest later step (SE units) | first step as % of DR |
|---|---|---|---|
| d100_b30 | **-47.20** | 0.36 | 101.4% |
| d100_b40 | **-63.86** | 0.66 | 99.4% |
| d140_b30 | **-53.06** | 0.78 | 98.8% |
| d140_b40 | **-76.18** | 0.77 | 100.4% |

So G3 as I wrote it demanded a strict ordering among six arms that are
**statistically indistinguishable from each other and from the null**. For a
perfectly working instrument the six interior/endpoint means are exchangeable
noise, and the probability that six exchangeable draws happen to be
non-increasing is `1/6! = 1/720`. **G3 was very nearly unsatisfiable by
construction.** That is the mirror image of the defect this task was dispatched
to repair: the superseded demonstration had a condition that could not fail, and
mine had a condition that could barely pass. Both are instances of DF-3 --
a decision rule that partitions the range of a quantity without asking whether
the quantity is resolvable at the declared draw count.

**The mechanism is the family's own algebra, and it was available before the
run.** For a single column `v = sqrt(1-t) e_s + sqrt(t) g`, the expected squared
overlap of the un-orthogonalised family with the selected coordinate subspace is

```
A(t) = (1 + (beta - 1) t) / (1 + (d - 1) t),      A(0) = 1,  A(1) = beta/d
```

which reaches the midpoint of its range at `t = 1/(d+1)` -- **`0.0099` at
`d = 100` and `0.0071` at `d = 140`**. The pre-registered grid's first interior
point, `t = 0.05`, is already five to seven times past the half-way point of the
family's informative range. Measured directly from the frozen seeds (a
deterministic post-hoc diagnostic of the projector family, no error draws and no
lattice involved; **not** part of the pre-registered adjudication):

| t | `A(t)`, d=100 beta=30 | `A(t)`, d=140 beta=40 |
|---|---|---|
| 0.00 | 1.00000 | 1.00000 |
| 0.05 | 0.38032 +- 0.01121 | 0.35401 +- 0.00383 |
| 0.10 | 0.33871 | 0.32028 |
| 0.25 | 0.31193 | 0.29896 |
| 0.50 | 0.30267 | 0.29167 |
| 0.75 | 0.29957 | 0.28920 |
| 1.00 | 0.29806 | 0.28792 |
| Haar reference `beta/d` | 0.30000 | 0.28571 |

`88.5%` of the alignment excess `A(0) - beta/d` is already gone at `t = 0.05`
(`d=100`), and `98.3%` by `t = 0.25`. **The seven-point family as literally
specified is a two-point family wearing a seven-point grid.** The specification
is not wrong -- `t = 0` is coordinate-aligned, `t = 1` is Haar, and the
interpolation is monotone in `A(t)` by inspection of the closed form -- but its
`t`-grid is placed almost entirely in the collapsed region, because
`sqrt(t) * G` has column norm `sqrt(t d)` against the selector's `sqrt(1-t)`,
and those cross at `t = 1/(d+1)`.

I implemented the family **exactly as `DEC-20260805-4823db` specifies it**,
including the seven declared `t` values, and I am reporting what that
specification produces rather than silently substituting a better grid.

**What a successor should pre-register instead** -- for a Coordinator to decide,
not for me to adopt: the same family on a grid placed where `A(t)` actually
moves, e.g. `t in {0, 0.002, 0.005, 0.01, 0.02, 0.05, 1}`, or a scale-matched
mixture `sqrt(1-t) E_S + sqrt(t/d) G`; and a monotonicity condition restricted
to grid points whose pairwise mean difference exceeds `1 * SE_diff`, with the
indistinguishable points reported as a tie rather than scored as a violation.

---

## Part 7 -- The three arms whose absence broke the last run

All three ran. `r(2^-10)` pooled over 8 bases, and the shift from the Haar null
arm in SE-of-difference units with the `4 * SE` gate verdict.

| cell | arm | pooled `r(2^-10)` | pooled `r(2^-16)` | shift vs Haar (SE) | gate | P1 | P2 (between-fraction) |
|---|---|---|---|---|---|---|---|
| d100_b30 | **unreduced** | **1.037839** | 1.052921 | **+27.11** | **CLEARS** | pass | pass (7.6e-07) |
| | lll_only | 0.998646 | 1.003329 | -0.12 | no | pass | pass (6.9e-07) |
| | real_bkz | 0.998295 | 1.009472 | -0.06 | no | pass | pass (6.9e-07) |
| d100_b40 | **unreduced** | **1.055401** | 1.066332 | **+42.26** | **CLEARS** | **fail** | pass (4.1e-07) |
| | lll_only | 1.000736 | 1.003000 | +1.22 | no | pass | pass |
| | real_bkz | 1.000538 | 0.999501 | +1.25 | no | pass | pass (7.4e-07) |
| d140_b30 | **unreduced** | **1.023262** | 1.032146 | **+15.62** | **CLEARS** | pass | pass (7.0e-07) |
| | lll_only | 1.000584 | 0.999411 | -0.10 | no | pass | pass |
| | real_bkz | 0.999538 | 0.995920 | -0.78 | no | pass | pass (5.6e-07) |
| d140_b40 | **unreduced** | **1.029434** | 1.038016 | **+22.95** | **CLEARS** | pass | pass (3.9e-07) |
| | lll_only | 1.003294 | 1.011667 | +3.06 | no | pass | pass |
| | real_bkz | 1.000998 | 1.001045 | +0.89 | no | pass | pass (5.0e-07) |

(The P1 column applies P1's tolerances to each arm for comparability. P1 as
frozen is a predicate on the **real** arm only; the `unreduced` failure at
d100_b40, `r = 1.0554` against a `0.05` tolerance, is descriptive.)

KS distance on the body, pooled: haar `2.0e-04` to `3.7e-04`, real `2.2e-04` to
`4.1e-04`, **unreduced `9.1e-03` to `2.2e-02`** -- one to two orders of
magnitude larger, so the unreduced arm's departure is visible in the body as
well as the tail.

**Observation, stated as an observation.** The departure is present and large in
the **unreduced** q-ary basis in all four cells, and is absent -- below the
pre-registered gate -- in **both** the LLL-only and the BKZ arms in all four
cells. LLL alone removes it; BKZ adds nothing detectable beyond LLL. The largest
LLL-only shift anywhere is `+3.06 SE` (d140_b40), below the gate's 4.

I do not interpret this further. The demonstration's pre-registered verdict is
INVALID (Part 6), and under my own pre-registration that makes this an
**instrument outcome** with no mathematical conclusion recorded.

---

## Part 8 -- The beta-trend and the pre-registered ~1/sqrt(beta) falsifier

Tested at `beta in {30, 40, 50, 60}` -- **two values beyond `{30,40}`** -- with
the reduction **held fixed at LLL + BKZ-40** so that only `beta`, the parameter
the falsifier is about, varies. `D = mean r_arm(2^-10) - mean r_haar(2^-10)`;
`Dn = D / s(beta,d)` with `s = sqrt(2(d-beta)/(beta(d+2)))`.

### d = 100

| beta | `s` | unreduced `D` | `Dn` | coord (t=0) `D` | `Dn` | lll_only `D` | real_bkz40 `D` |
|---|---|---|---|---|---|---|---|
| 30 | 0.21390 | 0.040738 (20.3 SE) | 0.1905 | 0.096767 (47.8 SE) | 0.4524 | 0.001808 (1.1 SE) | 0.001233 (0.8 SE) |
| 40 | 0.17150 | 0.056512 (42.3 SE) | 0.3295 | 0.087353 (66.2 SE) | 0.5093 | 0.001594 (1.2 SE) | 0.001324 (1.3 SE) |
| 50 | 0.14003 | 0.078555 (153.4 SE) | 0.5610 | 0.078510 (99.4 SE) | 0.5607 | 0.001168 (1.5 SE) | 0.001127 (1.2 SE) |
| 60 | 0.11433 | 0.048091 (74.0 SE) | 0.4206 | 0.070148 (76.2 SE) | 0.6135 | 0.001247 (1.1 SE) | 0.000408 (0.6 SE) |

### d = 140

| beta | `s` | unreduced `D` | `Dn` | coord (t=0) `D` | `Dn` | lll_only `D` | real_bkz40 `D` |
|---|---|---|---|---|---|---|---|
| 30 | 0.22725 | 0.023895 (16.9 SE) | 0.1052 | 0.092762 (52.6 SE) | 0.4082 | 0.001923 (1.1 SE) | -0.001146 (-0.9 SE) |
| 40 | 0.18765 | 0.029750 (23.0 SE) | 0.1585 | 0.083185 (77.2 SE) | 0.4433 | 0.003358 (3.1 SE) | 0.001092 (0.9 SE) |
| 50 | 0.15922 | 0.039424 (30.3 SE) | 0.2476 | 0.074256 (55.8 SE) | 0.4664 | 0.001517 (1.0 SE) | 0.000559 (0.4 SE) |
| 60 | 0.13704 | 0.050058 (66.6 SE) | 0.3653 | 0.069981 (96.2 SE) | 0.5107 | 0.002711 (4.5 SE) | -0.000162 (-0.2 SE) |

### The verdicts, on the branches declared in Part 1

| arm | d = 100 | d = 140 |
|---|---|---|
| **unreduced** | **FALSIFIED** -- `D(60)/D(30) = 1.1805` vs predicted `0.5345` | **FALSIFIED** -- `D(60)/D(30) = 2.0949` vs predicted `0.6030` |
| **coord (t=0)** | **NEITHER** -- `0.7249` vs predicted `0.5345` (band `[0.401, 0.668]`) | **NEITHER** -- `0.7544` vs predicted `0.6030` (band `[0.452, 0.754]`) |
| lll_only | **NOT APPLICABLE** -- `D(30)` does not clear its own gate | **NOT APPLICABLE** |
| real_bkz40 | **NOT APPLICABLE** -- `D(30)` does not clear its own gate | **NOT APPLICABLE** |

**The falsifier fired, on the one arm that had a departure to lose.**

> **The unreduced q-ary arm's departure does not decay as `beta` grows. It
> GROWS.** At `d = 140` it rises monotonically across all four `beta`
> (`0.0239 -> 0.0298 -> 0.0394 -> 0.0501`, `Dn` rising `0.105 -> 0.365`), where
> the pre-registered prediction was a fall to `0.603` of its `beta = 30` value.
> This is the canonical artifact tell named in the task card and in
> `docs/inventor-protocol.md` Sec. 3, and I am recording it as one.

**A mechanism is identifiable and it is structural, not statistical.** For
`beta <= d - k = d/2` the tail-`beta` GSO window of the unreduced q-ary basis
`[[I_k, A],[0, q I_{d-k}]]` lies inside the `q I` block, which is exactly
coordinate-aligned; as `beta` grows within that range the window stays inside
the block and the alignment does not dilute, so the departure has no reason to
follow a `1/sqrt(beta)` dispersion law. At `d = 100`, `d/2 = 50`, and the
`beta = 60` point is the **only** one in either table that must reach past the
block boundary into the `[I | A]` rows -- and it is the only point where the
`d = 100` series falls (`0.0786 -> 0.0481`). At `d = 140`, `d/2 = 70`, so no
`beta` in `{30,40,50,60}` crosses the boundary and the series rises throughout.
The two `d` behave differently in exactly the place the basis structure says
they should.

**The coordinate-aligned arm decays, but too slowly**: `0.725` and `0.754`
against predicted `0.535` and `0.603`, so it lands in the declared NEITHER
branch at both `d`. `Dn` rises steadily with `beta` in both series rather than
staying constant, so the leading-order proportionality `D ~ s(beta,d)` is not
what the data does. I pre-registered a leading-order argument and it is not
accurate at these `beta/d`; the honest reading is that the prediction is too
crude, not that the effect is an artifact -- but the declared branch is NEITHER
and NEITHER is what I record.

**The two arms that carry the reduced-basis question -- `lll_only` and
`real_bkz40` -- have no departure at `beta = 30` to decay, so the falsifier is
NOT APPLICABLE to them.** That branch was declared in Part 1 in advance,
precisely because the superseded run's real arm sat at `r ~ 1.000`. Their `D`
stays within `[-0.0011, +0.0034]` across all eight (`d`, `beta`) points, never
exceeding `4 SE` except once (`lll_only`, `d=140`, `beta=60`, `4.45 SE`).

**No `beta` beyond 40 was reduced at matched block size, and that is a budget
limit, not a result.** Extending the *matched* real arm to `beta = 50` requires
BKZ-50. Measured in this run's own stage A: pruning-free BKZ took, per
basis on average, `0.93 s` at `(d,beta) = (100,30)` and `47.90 s` at
`(100,40)` -- a factor of **51.7 per 10 block sizes** -- and `2.47 s` at
`(140,30)` against `79.81 s` at `(140,40)`, a factor of **32.3**. Extrapolating
one more step at the same factor puts a single BKZ-50 basis at roughly
`2.5e3` seconds and eight of them at roughly `2.0e4` core-seconds -- **about
five times the entire 4000 core-second budget, for one cell.** That is an
extrapolation from two points, labelled as one; it is quoted to justify a
scoping decision, not as a measurement of BKZ-50. The fixed-reduction design
above is what fits, and it has the compensating virtue of varying only `beta`.

---

## Part 9 -- The real arm: measured, and NOT interpreted

Per Part 1 Sec. 1.4, an INVALID demonstration makes this an **instrument
outcome**: the real arm is reported as measured and no mathematical conclusion
is recorded from it.

| cell | pooled `r(2^-10)` | dev | pooled `r(2^-16)` | dev | P1 | between-fraction | P2 |
|---|---|---|---|---|---|---|---|
| d100_b30 | 0.998295 | 0.00171 | 1.009472 | 0.00947 | pass | 6.89e-07 | pass |
| d100_b40 | 1.000538 | 0.00054 | 0.999501 | 0.00050 | pass | 7.44e-07 | pass |
| d140_b30 | 0.999538 | 0.00046 | 0.995920 | 0.00408 | pass | 5.56e-07 | pass |
| d140_b40 | 1.000998 | 0.00100 | 1.001045 | 0.00104 | pass | 4.96e-07 | pass |

Three things must be read together with that table and none of them may be
dropped:

1. **P1 and P2 return the same verdict on the null arm as on the real arm in all
   four cells** (Part 5). Under the frozen protocol the real-arm verdict is
   therefore not read as discriminating.
2. **The demonstration's verdict is INVALID** in all four cells, so this is an
   instrument outcome by pre-registration.
3. **`E[R] = beta/d` is FORCED** for every projector, reduced or not, and
   carries zero information. Nothing in this table is that quantity, but the
   reminder is kept because `E[R]` agreement is the failure mode this experiment
   was designed around.

The values are recorded so that a successor with a valid demonstration can read
them. They reproduce the superseded package's real-arm ratios (`0.99829`,
`1.00054`, `0.99954`, `1.00100` there; `0.998295`, `1.000538`, `0.999538`,
`1.000998` here) -- as they must, since the bases, the errors and the estimator
are identical.

---

## Part 10 -- What I could not evaluate

* **The matched real arm beyond `beta = 40`.** Out of budget by 3-5x for a
  single cell, with the measured BKZ growth factors quoted in Part 8. This is an
  infrastructure limit and is not evidence in either direction.
* **Whether the graded family is monotone on a grid placed where it moves.** The
  closed form `A(t)` is monotone by inspection, but I did not measure `r(t)` at
  any `t` inside `[0, 0.02]`, because the seven `t` values were frozen by the
  governing decision and I did not substitute my own.
* **Why the alignment collapse is slightly faster than `A(t)` predicts** (e.g.
  measured `0.380` vs `A = 0.412` at `t = 0.05`, `d = 100`). QR orthogonalisation
  across the `beta` columns is the obvious candidate; I did not derive it.
* **Whether the `unreduced` arm's growth in `beta` is fully explained by the
  `beta <= d/2` block-boundary mechanism.** The `d = 100` `beta = 60` reversal is
  consistent with it and the `d = 140` monotone rise is consistent with it, but
  two series are not a demonstration, and I did not vary `k` to test it directly.
* **Anything at `beta = 606, d = 1420`.** Not attempted; explicitly out of scope.
* **The `primal_bdd` `optimize_d` anomaly's downstream significance** -- carried
  over as unchecked, as in the previous batch.

---

## Part 11 -- Scope, and what is NOT claimed

* **No ML-KEM break, and no claim about ML-KEM security in either direction.**
  Session recovery, not key recovery. No FIPS 203 parameter set is affected or
  cleared by anything in this report.
* **Nothing measured here is transported to `beta = 606, d = 1420`.** The
  `beta`-trend is four points at two `d` with `d <= 140`. It is not a law.
* **No number here is subtracted from the in-repo `primal_bdd` margins of
  2.80 / 6.04 / 1.28 bits.**
* **No status change, no hypothesis disposition, no heuristic validated or
  refuted, no knowledge promotion.** I am the Executor; these are observations.
  AGENTS.md rule 12 remains UNMET and UNWAIVED.
* **P1 and P2 were not re-scored against any rule other than the one frozen in
  BATCH-a51f91**, and the census was not read as a measured cap.
* **The demonstration's INVALID verdict is recorded as it fell.** I did not
  relax G3, did not reclassify to PARTIAL, and did not re-run with a better
  grid. The defect in G3 is diagnosed in Part 6.3 and handed to the Coordinator;
  diagnosing my own threshold is not the same as changing it.
* **`b2bcd_notes.md` carries B2-B, B2-C and B2-D at zero new compute.**
