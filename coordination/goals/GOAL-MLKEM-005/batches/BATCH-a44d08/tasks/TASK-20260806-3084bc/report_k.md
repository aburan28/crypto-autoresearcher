# Section A — `k != d/2`, the discriminating test between the two spill mechanisms

TASK-20260806-3084bc / BATCH-a44d08 / GOAL-MLKEM-005
Executor artifact of observations. **CLAIM TIER: TOY.**

Nothing in this report, and nothing the measurement it describes can produce,
bears on ML-KEM security, on any FIPS 203 parameter set, on any attack cost, or
on any cost model. No number measured at `d in {100, 140}` is transported to
`beta = 606`, to `d = 1420`, to any other parameter set, or to any reduction
regime, by extrapolation or by analogy.

No hypothesis status moves here. No evidence record is written here. This
document reports observations and the frozen verdicts of prereg section 2.5;
the judgement of what they support belongs to the Validator and the
Coordinator.

---

## 0. Notarized pre-registration — verification, quoted

```
file    coordination/goals/GOAL-MLKEM-005/batches/BATCH-a44d08/tasks/
        TASK-20260806-843c40/prereg.md
sha256 expected  8d00ca3f0977e7367cfd10f4eb01cc0d4d24dfdc1ecf9739ba3cc299ee2a6c80
sha256 observed  8d00ca3f0977e7367cfd10f4eb01cc0d4d24dfdc1ecf9739ba3cc299ee2a6c80
MATCH: yes.  The run proceeded.  On mismatch the script exits 2 without
       touching a lattice (prereg section 7); that branch was not taken.
receipt carrier  prereg_sha256.txt
                 = 8d00ca3f0977e7367cfd10f4eb01cc0d4d24dfdc1ecf9739ba3cc299ee2a6c80
                 (checked independently of the constant compiled into the script)
```

**Ancestry, asserted against the notarizing commit itself and not its parent**
(prereg section 0.2, carried correction V-7):

```
git merge-base --is-ancestor 9cb2d3e28ae7a474edbb116d694969470829e112 HEAD  ->  true
```

`9cb2d3e28` is `research: GOAL-MLKEM-005 TASK-20260806-0a1072 NOTARIZES the
BATCH-a44d08 pre-registration`. It predates this task. The pre-registration was
not modified for any reason; `git diff` of that path across every HEAD this
session observed is empty (see section 10, anomaly A-1).

**No early durability commit was made** (prereg section 0.2). Nothing in this
task directory has been committed by the Executor; the Coordinator archives.

---

## 1. Inference record (verbatim, as directed)

> requested_policy `executor-implementation`, degraded_allowed false,
> fallback_allowed false; resolved binding anthropic:claude-sonnet-5 per
> orchestration.adapter, but under the Claude Code runtime per CLAUDE.md
> per-role selection is process-level and subagents keep model: inherit, so the
> resolved model is the session model; fallback_used: false.

Independence in this batch is **procedural** — separate session, no shared
scratch, snapshot before review — and never model-level (prereg section 5.9).

---

## 2. What was run, and the two things checked before any object was built

Section A as frozen. Cells `(d, k)` = `(100,30)`, `(100,70)`, `(140,40)`,
`(140,100)`; `beta` grids `{15,25,30,35,50,65,70,75,85}` at `d = 100` and
`{20,35,40,45,70,95,100,105,120}` at `d = 140`; `n = 8` bases per arm; seeds
`810000/910000/920000 + d*1000 + k*10 + i` exactly as declared. Basis built
explicitly in exact integer arithmetic, `B = [[I_k, A],[0, q I_{d-k}]]`,
`q = 3329`, `K_I = coords 1..k`. Frame = last `beta` columns of `Q` from
`QR(B^T)` in float64. Arms: **A-unreduced** (primary) and **A-lll**
(secondary). **No BKZ was run.**

### 2.1 Check 1 — the implementation reproduces the FROZEN prediction table

Every entry of the four section-2.3 tables was transcribed verbatim into the
script and recomputed from the section-2.1 closed forms.

```
entries checked                     216  (36 grid points x 6 columns)
max abs deviation, value columns    < 1e-4   (the printed precision)
max abs deviation, ratio column     < 1e-3
result                              PASS
```

This is the check that the code scores against the notarized prediction rather
than against a re-derivation of it.

### 2.2 Check 2 — numerical integrity, by a second code path

Both observables were recomputed for one basis per `(d,k,beta)` through an
explicit `P = Q_tail Q_tail^T` and explicit projector traces, independently of
the `einsum` path the run uses:

```
max ||Q_tail^T Q_tail - I||_max     1.78e-15
max |diag(P) two-path difference|   9.99e-16
max |tr(P) - beta|                  1.42e-14
max |E_I two-path difference|       2.22e-16
max |V   two-path difference|       1.42e-14
capacity bounds respected           at every point of every cell
```

---

## 3. The observed `fpylll` q-ary basis convention (prereg section 2.6, constraint 7)

This is a read of integer entries. It is **not** a statistic and **not** a
scored arm.

The frozen call, `IntegerMatrix.random(100, "qary", k=50, q=3329)`, fpylll
0.6.4:

```
rows   0..49   carry the identity part, in columns  0..49
rows  50..99   are q times a unit vector, in columns 50..99
row 0 head = [1,0,0,0,0,0]   ||row 0|| = 12034.7   ||row 99|| = 3329.0
```

So the generator's structural form is **identity block first, in the LOW
coordinate indices; `q`-scaled rows last, in the HIGH coordinate indices** —
the same block placement as the prereg's explicit `B = [[I, A],[0, qI]]`. The
prereg's construction is therefore convention-compatible with the committed
data, and section 5 below confirms that numerically.

**Additional structural read** (a second integer inspection, not the frozen
disclosure, not a scored arm, reported because at `k = d/2` the frozen call
cannot answer it): `IntegerMatrix.random(100, "qary", k=30, q=3329)` gives

```
30 rows are q times a unit vector, at row indices 70..99, in columns 70..99
the identity part occupies rows 0..69 and columns 0..69
```

**Therefore fpylll's `k` parameter counts the `q`-SCALED rows, i.e. `|K_q|`,
not the identity-block size `|K_I|`.** The prereg's `k` is `|K_I|`. At
`k = d/2` the two labellings coincide, which is exactly the ambiguity the
prereg flagged as indistinguishable from all committed data. The consequence
for future work, stated plainly: the cell this report calls `(d=100, k=30)`
corresponds to the generator call `k=70`, and `(d=100, k=70)` to `k=30`. Any
committed record that read fpylll's `k` as the identity-block size is
mislabelled off the `k = d/2` diagonal. Nothing in this run depends on the
generator, because Section A builds its bases explicitly.

---

## 4. Result in one paragraph

Under the frozen rule of prereg section 2.5 the verdict is **NEITHER in all
four cells** — both mechanisms are falsified at at least one point in each
cell. The two arms did not fail together and their magnitudes are not
comparable. On the **`E_I` arm, M-K survives every one of the 36 points in all
four cells and M-D is falsified at every one of the 36**, with the measured
`E_I` agreeing with `min(1, k/beta)` to between `1e-8` and `1.3e-3` absolute
against a floor of `0.02`, while M-D misses by `0.167` to `1.000`, i.e. by
`8.3x` to `50x` its own tolerance. On the **`V` arm** (32 discriminating points
after the 4 excluded at `beta = d/2`), **M-D is falsified at 32 of 32 and M-K
at 22 of 32**: M-D misses by `-83%` to `+556%` relative, M-K by `+0.78%` to
`+32.9%` against a `2%` relative floor. The `NEITHER` verdicts are produced
entirely by the `V` arm and entirely by M-K's `V` magnitude, never by block
identity. A null result was a permitted and real outcome here; this is not one,
and neither is it a clean single-mechanism verdict.

---

## 5. Instrument check at `k = d/2` (not scored, non-discriminating by design)

The explicit construction of prereg section 2.6 was run at `k = d/2` on the
identical code path and compared with the committed anchors. `k = d/2` is where
M-K and M-D are numerically identical, so **no row here is evidence for either
mechanism** and none is scored as such.

| `d` | `beta` | `V` this code path | committed anchor | deviation |
|---|---|---|---|---|
| 100 | 30 | 9.3773 | 9.3628 | +0.155% |
| 100 | 60 | 16.2626 | 16.2690 | -0.039% |
| 140 | 30 | 6.7901 | 6.7504 | +0.588% |
| 140 | 40 | 11.7891 | 11.8075 | -0.156% |

Also reproduced, matching BATCH-436ddd's red-team values: window energy in the
`q*I` block `E_q = 5.8e-8` at `(100,30)` against a committed `0.00000`, and
`E_I = 0.833333` at `(100, beta=60)` against a committed `0.83333 = k/beta`.

**This code path reproduces the committed `k = d/2` data to within 0.6%.**

---

## 6. Per-cell results — every `(d, k, beta)` point, with separations

### 6.0 How separation is reported, and an objection to reporting it in SE alone

The task card asks for separations in SE. They are given below, and they must
be read with this caveat, which is a property of the design and not of the
data: `E_I` and `V` are **exact deterministic scalars of each frame** (prereg
section 2.5), so the only noise is between-instance dispersion, and on the
unreduced arm that dispersion is frequently at the float64 floor. `SE_{E_I}`
reaches `6.6e-11`. A separation of two predictions divided by that number is
`1e9` and carries no statistical content whatever. This is the same collapse
the prereg anticipated in section 2.5 when it required an absolute tolerance
component, and it is why the `E_I` floor `tol_E = max(4*SE, 0.02)` is governed
by the **absolute component `0.02` at every one of the 36 points in all four
cells** (`4*SE_max = 5.3e-3`). Both denominations are therefore reported:
**SE**, as asked, and **the frozen tolerance**, which is what actually decides.

Legend: `sep(SE)` = `|pred_MK - pred_MD| / SE`; `sep(tol)` =
`|pred_MK - pred_MD| / tol`, the discriminating power in units of the floor
that decides. `X` marks the `beta = d/2` points the prereg excludes from the
`V` verdict (section 2.4) and retains for the `E_I` arm.

### 6.1 `d = 100, k = 30` — verdict **NEITHER**

`E_I` arm, `tol_E = 0.02` at every `beta`:

| beta | `E_I` meas | SE | M-K pred | M-D pred | resid vs MK | resid vs MD | outcome | sep(SE) | sep(tol_E) |
|---|---|---|---|---|---|---|---|---|---|
| 15 | 1.000000 | 3.3e-09 | 1.0000 | 0.0000 | 7.0e-08 | 1.0000 | M-K survives, M-D FALSIFIED | 3.0e+08 | 50.0 |
| 25 | 1.000000 | 2.0e-08 | 1.0000 | 0.0000 | 2.1e-07 | 1.0000 | M-K survives, M-D FALSIFIED | 5.1e+07 | 50.0 |
| 30 | 0.999024 | 9.7e-04 | 1.0000 | 0.0000 | 9.8e-04 | 0.9990 | M-K survives, M-D FALSIFIED | 1.0e+03 | 50.0 |
| 35 | 0.857143 | 1.5e-08 | 0.8571 | 0.0000 | 1.8e-07 | 0.8571 | M-K survives, M-D FALSIFIED | 5.9e+07 | 42.9 |
| 50 | 0.600000 | 1.3e-09 | 0.6000 | 0.0000 | 3.2e-08 | 0.6000 | M-K survives, M-D FALSIFIED | 4.6e+08 | 30.0 |
| 65 | 0.461538 | 3.2e-10 | 0.4615 | 0.0000 | 1.4e-08 | 0.4615 | M-K survives, M-D FALSIFIED | 1.4e+09 | 23.1 |
| 70 | 0.428571 | 2.1e-10 | 0.4286 | 0.0000 | 1.1e-08 | 0.4286 | M-K survives, M-D FALSIFIED | 2.1e+09 | 21.4 |
| 75 | 0.400000 | 1.0e-10 | 0.4000 | 0.0667 | 7.9e-09 | 0.3333 | M-K survives, M-D FALSIFIED | 3.3e+09 | 16.7 |
| 85 | 0.352941 | 6.6e-11 | 0.3529 | 0.1765 | 3.3e-09 | 0.1765 | M-K survives, M-D FALSIFIED | 2.7e+09 | 8.8 |

`V` arm:

| beta | `V` meas | SE | M-K | M-D | dev vs M-K | tol_V(M-K) | outcome | sep(SE) | sep(tol_V MK) |
|---|---|---|---|---|---|---|---|---|---|
| 15 | 5.6337 | 4.1e-02 | 5.2500 | 0.9643 | +7.31% | 0.1623 | BOTH FALSIFIED | 106 | 26.4 |
| 25 | 14.8339 | 4.0e-02 | 14.5833 | 2.6786 | +1.72% | 0.2917 | M-K survives, M-D FALSIFIED | 298 | 40.8 |
| 30 | 20.9425 | 5.7e-02 | 21.0000 | 3.8571 | -0.27% | 0.4200 | M-K survives, M-D FALSIFIED | 302 | 40.8 |
| 35 | 18.6568 | 1.1e-02 | 18.1071 | 5.2500 | +3.04% | 0.3621 | BOTH FALSIFIED | 1.15e+03 | 35.5 |
| 50 X | 13.3689 | 1.9e-02 | 10.7143 | 10.7143 | +24.78% | 0.2143 | EXCLUDED — NOT DISCRIMINATING | — | — |
| 65 | 6.9726 | 1.9e-02 | 5.2500 | 18.1071 | +32.81% | 0.1050 | BOTH FALSIFIED | 694 | 122 |
| 70 | 4.2248 | 2.0e-02 | 3.8571 | 21.0000 | +9.53% | 0.0778 | BOTH FALSIFIED | 881 | 220 |
| 75 | 2.9945 | 1.9e-02 | 2.6786 | 14.5833 | +11.80% | 0.0740 | BOTH FALSIFIED | 643 | 161 |
| 85 | 1.1599 | 7.4e-03 | 0.9643 | 5.2500 | +20.29% | 0.0295 | BOTH FALSIFIED | 581 | 145 |

M-K falsified at `beta in {15, 35, 65, 70, 75, 85}` (`V` arm only, never
`E_I`). M-D falsified at all 9 `E_I` points and all 8 discriminating `V`
points.

### 6.2 `d = 100, k = 70` — verdict **NEITHER**

`E_I` arm (`tol_E = 0.02`): **M-K survives all 9 points, M-D FALSIFIED at all
9.** Measured `E_I` = `1.000000` for `beta <= 65`, `0.998672` at `beta = 70`,
`0.933333` at `75`, `0.823529` at `85`; residual vs M-K at most `1.33e-03`;
residual vs M-D from `0.1765` to `1.0000`, i.e. `8.8x` to `50x` the floor.
`sep(SE)` `3.3e+02` to `3.0e+09`; `sep(tol_E)` `8.8` to `50.0`.

`V` arm: M-K survives at `beta in {70, 75}` and is falsified at
`{15,25,30,35,65,85}` at `+2.86%` to `+31.90%`; M-D is falsified at all 8
discriminating points, `-80.07%` to `+478.30%`, at `12.2x` to `212x` its floor.
`beta = 50` excluded. `sep(SE)` `99.5` to `1.3e+03`; `sep(tol_V MK)` `24.9` to
`222`.

### 6.3 `d = 140, k = 40` — verdict **NEITHER**

`E_I` arm (`tol_E = 0.02`): **M-K survives all 9, M-D FALSIFIED at all 9.**
Residual vs M-K at most `5.5e-05`; residual vs M-D from `0.1667` to `1.0000`,
`8.3x` to `50x` the floor. `sep(SE)` `3.3e+04` to `4.7e+09`; `sep(tol_E)` `8.3`
to `50.0`.

`V` arm: M-K survives at `beta in {35, 40, 45}` and is falsified at
`{20, 95, 100, 105, 120}` at `+4.32%` to `+32.94%`; M-D falsified at all 8,
`-82.91%` to `+551.97%`, at `35.1x` to `265x`. `beta = 70` excluded.
`sep(SE)` `363` to `9.95e+03`; `sep(tol_V MK)` `38.8` to `262`.

### 6.4 `d = 140, k = 100` — verdict **NEITHER**

`E_I` arm (`tol_E = 0.02`): **M-K survives all 9, M-D FALSIFIED at all 9.**
Residual vs M-K at most `9.7e-06`; residual vs M-D from `0.1667` to `1.0000`,
`8.3x` to `50x`. `sep(SE)` `5.4e+04` to `7.1e+09`; `sep(tol_E)` `8.3` to
`50.0`.

`V` arm: M-K survives at `beta in {95, 100, 105}` and is falsified at
`{20, 35, 40, 45, 120}` at `+4.93%` to `+32.39%`; M-D falsified at all 8,
`-83.01%` to `+555.79%`, at `12.5x` to `265x`. `beta = 70` excluded.
`sep(SE)` `244` to `1.62e+04`; `sep(tol_V MK)` `42` to `262`.

### 6.5 Tally over the whole primary grid

| arm | points | M-K survives | M-K falsified | M-D survives | M-D falsified |
|---|---|---|---|---|---|
| `E_I` | 36 | **36** | 0 | 0 | **36** |
| `V` (discriminating) | 32 | 10 | 22 | 0 | **32** |
| `V` excluded at `beta = d/2` | 4 | — | — | — | — |

**Cell verdicts under the frozen rule: NEITHER / NEITHER / NEITHER / NEITHER.**

### 6.6 Where M-K's `V` misses, as an observation

The `V` residual of M-K is positive at 30 of 32 discriminating points and its
largest values cluster in the spill window `min(k,d-k) < beta <= max(k,d-k)`:
`+24.8%`, `+32.8%` at `(100,30)`; `+31.9%`, `+2.9%` at `(100,70)`; `+30.0%`,
`+32.9%` at `(140,40)`; `+32.4%`, `+1.9%` at `(140,100)`. Outside that window
the miss is `+0.78%` to `+20.3%`. The part of M-K that carries the `V`
magnitude is its "the excess `beta - c` dimensions spread generically over the
complement" clause; the part that carries block identity is `E_I`, and that
part is not falsified anywhere. Recorded as an observation. What it supports is
not for this report to say.

---

## 7. Null objects — run identically, scored identically

### 7.1 N-A1, Haar frame — the instrument is not manufacturing the answer

Prediction, exact: `E_I = k/d`, `V = 2 beta (d-beta)/(d(d+2))`.

* `E_I`: agrees at `|z| <= 1.7` across all 36 points, and within `0.005`
  absolute everywhere. Measured `0.2857`-`0.7150` per cell.
* `V`: agrees at `|z| <= 4.6`; largest three departures `-4.6` at
  `(140,40, beta=20)`, `-4.5` at `(100,70, beta=65)`, `-2.9` at
  `(100,70, beta=50)`. In absolute units those are `0.033`, `0.045`, `0.057`.
* Reported plainly rather than smoothed: 2 of 72 Haar comparisons exceed
  `|4|` SE against roughly `0.2` expected under an exact `t_7` reference. The
  9 `beta` values within a cell are **nested slices of the same 8 matrices**
  and so are strongly dependent, which makes the effective multiplicity far
  below 72 and makes a run of large `|z|` at neighbouring `beta` unsurprising.
  No verdict in this report changes under any reading of these two points: the
  absolute deviations, at most `0.057` in `V` units, are two to three orders of
  magnitude below the `4.3`-`24.0` `V`-unit separations the scored arm turns
  on.

**The decisive fact for section 8:** on the identical code path the Haar arm
returns `E_I = k/d`, strictly interior to `[0,1]`, at `0.2857` to `0.7150`. It
does not return the real arm's curve. The observable is not returning
`min(1,k/beta)` by construction.

### 7.2 N-A2, ambient coordinate permutation — the statistic reads the block, not the index

Same `B`, ambient coordinates permuted, scored against the **unpermuted** index
ranges. Prediction: `E_I -> k/d`.

* Measured `E_I` lands on `k/d` to within `0.032` absolute at every one of the
  36 points (`z` from `-5.5` to `+1.2`; the largest absolute miss is
  `0.68264` against `0.7143` at `(140,100, beta=70)`).
* Distance from the M-K prediction on the same points: `-22` to `-68` SE, and
  in absolute units up to `0.70` — i.e. permuting the ambient coordinates
  destroys the entire effect and returns the Haar value.

### 7.3 N-A3, block swap — the admissibility test, and it passes exactly

`B' = [[q I_{d-k}, 0],[A, I_k]]` with the same `A`, so `K_q` = coords `1..d-k`
and `K_I` = coords `d-k+1..d`.

| scored against | measured `E_I` | equals |
|---|---|---|
| the **relocated** `K_I` (coords `d-k+1..d`) | `1.000000, 0.857143, 0.600000, 0.461538, 0.428571, 0.400000, 0.352941, ...` | **exactly `min(1, k/beta)` — the M-K curve, at every point of every cell, SE `= 0` (`DEGENERATE_EXACT`)** |
| the **old index range** `1..k` | `0.000000` for `beta <= d-k`, then `0.0667, 0.1765, ...` | **exactly `max(0, 1-(d-k)/beta)` — the M-D curve** |

This is the frozen admissibility test of prereg section 2.6, and it is
unambiguous: **the measured quantity follows the `I`-block to its new
coordinate range, not the coordinate range.** Section A is therefore
**ADMISSIBLE** by its own declared criterion. It also shows, structurally, that
M-D's `E_I` prediction is precisely M-K's prediction scored against the wrong
block.

**An unexpected observation, recorded because it was not predicted.** The block
swap leaves `E_I` exactly invariant but **changes `V` by up to a factor of
2.3**: `V_swap` is `12.7500 / 18.7500 / 21.0000 / 22.7500 / 25.0000 / ...`
at `(100,30)` against `5.6337 / 14.8339 / 20.9425 / 18.6568 / 13.3689 / ...` on
the unswapped arm. The reason is structural: in `B'` the first `d-k` rows are
`q e_j` and span the coordinate block `K_q` exactly, so the tail GSO vectors
are exactly the unit vectors of `K_I` — **coordinate-aligned within the block**
rather than generic within it. `V_swap = beta(1 - beta/d)` exactly, which is
the global maximum of `V` over all rank-`beta` projectors, i.e. the object
recorded in `EV-MLKEM-94c773` as the one on which P3 attains its maximum
departure. Two consequences, both disclosed rather than used: (i) N-A3 is a
valid control for **block identity**, which is what it was frozen to test, and
is **not** `V`-comparable to the real arm; (ii) the run reproduces from a
second direction the batch's section-1.1 scope limit — `V` is a property of a
basis **presentation**, and here a pure reordering of the same construction
moves it by 2.3x.

### 7.4 The mirrored pair, as a control in its own right

`(100,30)` against `(100,70)` and `(140,40)` against `(140,100)` are the same
set of block sizes with the roles of `K_I` and `K_q` exchanged. A statistic
responding to block *size* or index *position* returns the same answer in both
members. It does not: at `beta = 65`, `E_I = 0.461538` at `k = 30` and
`1.000000` at `k = 70`; at `beta = 95`, `E_I = 0.421053` at `k = 40` and
`1.000000` at `k = 100`.

---

## 8. The arrangement in which this check could not fail, and why it is not running in it

Prereg section 2.7 names Section A's version. It is carried here in full, one
thing is added that the frozen text names only by half, and the demonstration
follows.

**Named arrangement (prereg section 2.7).** For every rank-`beta` projector `P`
and every coordinate set `S`, `tr(P Pi_S) <= min(beta, |S|)`, a sum of squared
cosines of principal angles. Hence `E_I(beta) <= min(1, k/beta)`
**identically** — for the real arm, for a Haar frame, for `Z^d`, for anything.
A design that declared "M-K predicts confinement breaks above `beta = k`" and
scored "`E_I < 1` for `beta > k`" would report an algebraic identity as a
measurement and would confirm M-K on a Haar frame. That is the P3 failure in
new clothes.

**The half the frozen text names only for M-K, stated here for both.** Prereg
section 2.7 point 4 discloses that M-K's `E_I` prediction coincides with the
capacity bound in `min(k,d-k) < beta <= max(k,d-k)` and can only be falsified
downward there. The symmetric fact, which the frozen text does not state and
which this run must: **`E_I^{M-K}(beta) = min(1, k/beta)` is the UPPER capacity
bound at EVERY `beta`, and `E_I^{M-D}(beta) = max(0, 1-(d-k)/beta)` is exactly
the LOWER capacity bound**, since
`tr(P Pi_I) = beta - tr(P Pi_q) >= beta - min(beta, d-k)`. The whole `E_I` arm
is therefore a test of *which algebraic extreme the frame sits at*. M-K can
only ever be falsified downward and M-D only upward, in every cell and at every
`beta`. This does not make the arm vacuous — a generic frame sits strictly
interior, and both extremes are attainable — but it is the exact shape of the
arrangement the program has been caught in six times, and it is disclosed here
before any reading is placed on the result.

**Six demonstrations that this run is not in it.** Each is a number from this
run, not an argument.

1. **The extremes are not forced by the instrument: the identical code path
   returns interior values.** The Haar null (section 7.1) returns
   `E_I = 0.2857`-`0.7150`, and the permutation null (section 7.2) returns the
   same, through the same `build -> QR -> slice -> diag` path with only the
   object changed. An instrument that returned `min(1,k/beta)` by construction
   would have returned it there too.
2. **In the region `beta <= min(k, d-k)` the capacity bound forbids neither
   mechanism.** There the upper bound is `1` and the lower is `0`, both
   mechanisms are permitted their full predictions, and they differ by the
   whole of `1.0000`. Any measured `E_I` strictly inside `(0,1)` — for instance
   the Haar value — falsifies **both**. Twelve of the 36 grid points lie in
   that region (3 per cell), and the measurement returned one of the two
   extremes at all of them rather than the interior.
3. **N-A3 shows the extreme tracks the block and not the index range.** The
   same object scored against the wrong coordinate range returns the *other*
   extreme exactly (section 7.3). If `E_I` were saturating for an algebraic
   reason, both scorings would saturate; one does and one does not.
4. **The mirrored pairs return different curves** (section 7.4). Block size and
   index position are held identical across a pair; only block identity
   changes; the answer changes.
5. **The `V` arm is not bound-limited except at two declared points, and it is
   where M-K actually failed.** `V^{M-K}` equals the global maximum
   `beta(1-beta/d)` only at `beta = k`, and `V^{M-D}` only at `beta = d-k`; the
   run flags those points (`(100,30,30)`, `(100,70,70)`, `(140,40,40)`,
   `(140,100,100)` for M-K). At the other 28 discriminating points both `V`
   predictions are interior and two-sided, and M-K was falsified at 22 of 32.
   **A check that could not fail did not just fail; it failed on the arm that
   was free to fail, and survived on the arm that was not.** That asymmetry is
   the honest summary of this section.
6. **The `beta = d/2` exclusion was honoured.** At `beta = 50` (`d=100`) and
   `beta = 70` (`d=140`) the two `V` curves cross exactly at `10.7143` and
   `14.0000`; those four points are recorded as NOT DISCRIMINATING for `V`
   regardless of what they show — and what they show is a `+24.4%` to `+30.1%`
   excess over the common prediction, scored nowhere. They are retained for the
   `E_I` arm as the prereg requires.

**What this section still cannot close.** It cannot exclude that a different
observable would test a different proposition, and the frozen `E_I`/`V` pair
was chosen by the pre-registration, not by this run. Prereg section 2.7's own
residual stands unchanged: Section A measures where the tail window of a
specific unreduced (and LLL-only) basis **presentation** sits relative to that
presentation's own blocks. It says nothing about any lattice invariant, nothing
about reduction, nothing about the `2^-10` tail law, and nothing about ML-KEM.
It is not offered as an AM-4 adjudicator and does not claim to satisfy AM-4.

---

## 9. Secondary arm A-lll (LLL only, no BKZ) — measured in full

All 32 reductions completed; no cell was dropped. Frozen verdict: **NEITHER in
all four cells**, with both mechanisms falsified at nearly every point — which
is the expected shape for an arm neither mechanism is about (both are claims
about the unreduced construction, prereg section 2.1).

| cell | `E_I` range after LLL | `k/d` | `V` range after LLL | `V` range unreduced |
|---|---|---|---|---|
| (100,30) | 0.3200-0.3928 | 0.3000 | 0.39-1.41 | 1.16-20.94 |
| (100,70) | 0.7127-0.7827 | 0.7000 | 0.30-0.78 | 1.15-20.83 |
| (140,40) | 0.3294-0.4611 | 0.2857 | 1.13-14.17 | 1.32-28.57 |
| (140,100) | 0.7381-0.8561 | 0.7143 | 0.53-1.79 | 1.32-28.57 |

Two observations, recorded without interpretation:

* LLL moves `E_I` off `min(1,k/beta)` and toward `k/d`, and **overshoots it in
  the same direction in all four cells**: the residual `E_I - k/d` is positive
  at all 36 points, from `+0.0037` to `+0.175`, decreasing with `beta`. A block
  preference survives LLL at this size on this presentation.
* `V` falls by roughly `4x` to `50x` at `d = 100`, the same order as the
  `15-50x` suppression recorded in `EV-MLKEM-94f036`.

Both are statements about the LLL-reduced presentation of these 32 bases at
`d <= 140`, at `n = 8`, and about nothing else.

---

## 10. Deviations, objections and anomalies — recorded, none discarded

**D-1 (protocol deviation, resolved and disclosed).** Prereg section 2.6 writes
the N-A3 block-swap basis as `B' = [[q I_{d-k}, 0],[A^T, I_k]]`. With `A` of
shape `(k, d-k)` as the same section fixes, `A^T` has shape `(d-k, k)` and
cannot occupy a block that must be `(k, d-k)`; the frozen text is
**dimensionally inadmissible as literally written**. The unique
shape-consistent object that "the same `A`" can denote there is `A` itself,
which is what was used, giving a non-singular `B'` of determinant `q^{d-k}`
with the block roles exchanged, which is the stated intent of the control.
Recorded here and in the manifest rather than silently resolved. No other
reading was run.

**O-1 (objection, recorded; the frozen specification was run anyway per prereg
section 5.5).** The `V` arm's absolute tolerance component is `2%` of the
prediction, justified in prereg section 2.5 by "the `<= 2%` agreement the
closed-form `V` already shows against committed `k = d/2` values". The
committed anchors do not show that: `V_k(30) = 9.00` against `9.3628` is
`-3.9%`, `V_k(30) = 6.43` against `6.7504` is `-4.7%`, `V_k(40) = 11.43`
against `11.8075` is `-3.2%`, `V_k(40) = 16.00` against `16.2446` is `-1.5%`,
`V(60) = 16.00` against `16.269` is `-1.7%`. The `2%` floor was therefore set
below the closed form's own already-committed disagreement with measurement, on
three of five anchors. This is the mechanism by which M-K is falsified on the
`V` arm at points where it misses by `+0.78%` to `+7.5%`. **This objection
changes nothing that was scored**: the frozen rule was applied exactly as
written, no threshold was altered, and the verdicts stand as computed. It is
recorded so the Validator and Coordinator can weigh it.

**O-2 (objection, recorded).** Reporting separations in SE alone is not
meaningful on this arm; see section 6.0. Both denominations are given.

**A-1 (infrastructure anomaly, no effect on the measurement).** The worktree
`HEAD` advanced **during** the session, by a concurrent branch-sync merge of
`origin/main` that this task did not initiate:
`a240a854a` (observed at task start) -> `adf55b0d4` (recorded by the script at
run time) -> `974ad5794` (observed after the run). Checked and recorded:
`9cb2d3e28`, the notarizing commit, is an ancestor of **all three**;
`a240a854a` is an ancestor of `974ad5794`, so no history was rewritten; and
`prereg.md` is **byte-identical at all three commits and in the working tree**,
sha256 `8d00ca3f...` in every case, with an empty `git diff` across the range.
The installed `python 3.13.1 / numpy 2.4.0 / scipy 1.15.3 / fpylll 0.6.4` are
unchanged before and after. No input to the measurement changed. The run was
**not** repeated, because `maximum_runs` is 1 and nothing bearing on it moved.

**A-2 (host condition, recorded).** Load average `424 / 479 / 425` at start and
`375 / 421 / 415` at end on 14 cores, shared. The measurement was run as a
single process with all BLAS thread counts pinned to 1
(`OMP/OPENBLAS/MKL/VECLIB/NUMEXPR_NUM_THREADS=1`) and no internal parallelism.
Timings below are wall-clock on that loaded host and are not clean benchmarks.

**A-3 (no cell dropped).** The budget did not bind. Every planned cell, every
`beta`, both arms and all three nulls were measured. Nothing was truncated,
nothing extrapolated.

**A-4 (nomenclature hazard, from section 3).** fpylll's `k` counts `q`-rows,
the prereg's `k` counts identity rows. Off the `k = d/2` diagonal these are
different parameters with the same name.

---

## 11. Wording rule (prereg section 2.5, section 5.4) — compliance and the scan

The frozen rule, quoted once:

> No arm may be reported as "absent", "no departure", "vanishes", "consistent
> with zero" or any synonym. Every negative is an upper bound at the floor
> above, stated with the floor.

Every negative in this report is stated as an upper bound at a declared floor,
in these terms:

* **`E_I` arm, M-K not falsified at any of 36 points.** Upper bound: the
  measured `E_I` lies within `1.3e-3` of `min(1, k/beta)` at every point,
  against a floor of `tol_E = 0.02`, at `n = 8` bases. This is **not** a
  statement that M-K is correct.
* **`V` arm, M-K not falsified at 10 of 32 discriminating points.** Upper bound
  at those points: the measured `V` lies within `tol_V(M-K)`, which ranges from
  `0.0704` to `0.6889` in `V` units across the four cells, of M-K's prediction
  at `n = 8` bases.
* **M-D was falsified at every point of both arms in all four cells**, so no
  upper-bound statement is owed for M-D anywhere in the primary grid.
* **No cell returned NOT SEPARATED.** Had one, it would be reported as "the two
  mechanisms differ by at most `<tol>` in `E_I` / `V` units at `n = 8` bases".

Scan output (`python3 measure_k.py --wording-scan`), run against the script and
the JSON before this file existed, every hit classified:

```
measure_k.py:24   [absent] [no departure] [vanish] [consistent with zero]
                  -- the module docstring stating the wording rule itself
measure_k.py:981  [absent] [no departure] [vanish] [consistent with zero]
                  -- the scanner's own token list
measure_k.py: 8 hit(s), all in the two lines above
results_k.json: 0 hit(s)
```

Re-running the scan after this file exists reports 11 further hits, all of them
in this section and all of them classified: 2 at the block-quotation of the rule
immediately above, and 9 in the quoted scan output just above (the two script
lines, reproduced verbatim). Full final scan: `report_k.md` 11 hits at lines
561, 585 and 587 only; `run_manifest.yaml` 0 hits; `results_k.json` 0 hits;
`measure_k.py` 8 hits at lines 24 and 981 only. No hit anywhere in any artifact
is a description of a measured arm.

---

## 12. Novelty accounting (prereg section 2.7), stated as required

* **REPRODUCTION at new block sizes.** That the tail window sits in the `I`
  block rather than the `q*I` block was already measured at `k = d/2`
  (`E_q = 0.00000`, `E_I = 0.83333 = k/beta` at `beta = 60 > k`
  [quoted: BATCH-436ddd red_team_report.md section 2]). Its confirmation at
  `k in {30,70,40,100}` is a reproduction at new block sizes and is labelled
  so.
* **NOVEL, and unavailable at `k = d/2` by construction.** (i) **The
  boundary.** The confinement boundary tracks `k` and not `d - k`: at
  `(100,70)`, `E_I` remains `1.000000` through `beta = 65` and departs only
  above `beta = 70 = k`, while `d - k = 30` is crossed at `beta = 35` with no
  change; the mirrored cell `(100,30)` departs from `1` at `beta = 35 > k = 30`
  while `d - k = 70` is irrelevant. The same pattern holds at `d = 140` with
  `k = 40` and `k = 100`. (ii) **The `V` magnitude**, whose two predictions
  differ by `((d-k)/k)^2` = `5.44` to `6.25` here and by exactly `1` at
  `k = d/2`: measured `V` sits within `+0.78%`..`+32.9%` of `V_k` and
  `-83%`..`+556%` of `V_{d-k}` at every discriminating point.

---

## 13. Budget and reproduction

```
maximum_runs        1        used 1
wall clock budget   10800 s  used 327.6 s   (3.0%)
memory budget       8 GB     peak RSS 46.7 MB (0.6%)
LLL sub-budget      6000 s   used 315.2 s   (declared before the arm ran)
```

Per-cell wall clock (loaded host, single process, single BLAS thread):

| cell | unreduced | Haar | perm | swap (both scorings) | LLL (8 bases) | cell total |
|---|---|---|---|---|---|---|
| (100,30) | 0.003 s | 0.006 s | 0.004 s | 0.003 s | 53.7 s | 53.7 s |
| (100,70) | 0.206 s | 0.101 s | 0.213 s | 0.009 s | 42.8 s | 43.3 s |
| (140,40) | 0.505 s | 0.005 s | 0.320 s | 0.073 s | 141.0 s | 142.5 s |
| (140,100) | 0.004 s | 0.889 s | 0.120 s | 0.006 s | 77.7 s | 78.9 s |

Environment actually used: `python 3.13.1`, `numpy 2.4.0`, `scipy 1.15.3`,
`fpylll 0.6.4`, `macOS-26.6-arm64-arm-64bit-Mach-O`, 14 cores.

Reproduction: from the repository root,

```
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
VECLIB_MAXIMUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
python3 coordination/goals/GOAL-MLKEM-005/batches/BATCH-a44d08/tasks/\
TASK-20260806-3084bc/measure_k.py
```

The only randomness is `numpy.random.default_rng` at the three declared seed
formulas; there is no other source. Every reported statistic is a deterministic
function of those seeds under a fixed numpy/LAPACK.

---

## 14. Certificate

```
certificate.kind: none
reason: pure measurement run. No discrete-log solve and no factor-base
        relation is claimed, so docs/claims-and-verification.md requires no
        solution certificate. The independent re-verifications this run does
        carry are the second-code-path recomputation of both observables
        (section 2.2) and the reproduction of the committed k = d/2 anchors
        (section 5).
```

---

## Appendix — POST-HOC, uncitable as a result (prereg section 5.6)

Computed after the frozen verdicts, presented for forward guidance only. **This
is not a result, is not a rescoring, and may not be cited as evidence for or
against either mechanism.** It is recorded because prereg section 5.6 requires
that any post-hoc quantity computed be labelled and disclosed rather than
suppressed.

If, in the region `beta <= min(k, d-k)`, the tail frame is taken to be a
Haar-random `beta`-subspace **of the `k`-dimensional block** rather than a
generic one in the sense the closed form uses, then
`P_aa ~ Beta(beta/2, (k-beta)/2)` on `K_I` gives
`V = beta^2/k + 2 beta (k-beta) / (k(k+2)) - beta^2/d`:

| `(d,k)` | beta | `V` meas | `V_k` frozen | dev | `V` refined | dev |
|---|---|---|---|---|---|---|
| (100,30) | 15 / 25 / 30 | 5.6337 / 14.8339 / 20.9425 | 5.2500 / 14.5833 / 21.0000 | +7.31% / +1.72% / -0.27% | 5.7188 / 14.8438 / 21.0000 | -1.49% / -0.07% / -0.27% |
| (100,70) | 15 / 25 / 30 | 1.1484 / 2.9772 / 4.1858 | 0.9643 / 2.6786 / 3.8571 | +19.10% / +11.15% / +8.52% | 1.2917 / 3.1250 / 4.3333 | -11.09% / -4.73% / -3.41% |
| (140,40) | 20 / 35 / 40 | 7.4511 / 22.0460 / 28.5671 | 7.1429 / 21.8750 / 28.5714 | +4.32% / +0.78% / -0.02% | 7.6190 / 22.0833 / 28.5714 | -2.20% / -0.17% / -0.02% |
| (140,100) | 20 / 35 / 40 | 1.3156 / 3.7618 / 4.8548 | 1.1429 / 3.5000 / 4.5714 | +15.11% / +7.48% / +6.20% | 1.4566 / 3.9461 / 5.0420 | -9.68% / -4.67% / -3.71% |

The refinement moves the residual from `+0.78%..+19.10%` to
`-0.02%..-11.09%` — it overshoots where the frozen form undershoots and does
not close the gap. It is offered only as a direction for a successor design and
carries no verdict.
