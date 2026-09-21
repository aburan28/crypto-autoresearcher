# AM-1 pre-registration — graded-family re-run on the bracketing `t` grid

TASK-20260806-5930ec / BATCH-f19c37 / GOAL-MLKEM-005
Executor artifact. **Claim tier TOY.** Nothing in this document, and nothing the
measurement it governs can produce, bears on ML-KEM security, on any FIPS 203
parameter set, or on any cost model.

Governing authority: `ledger/decisions/DEC-20260806-00deff.yaml`, amendment
**AM-1**, which supersedes `DEC-20260805-4823db` on the seven frozen `t` values
and on the G3 reading, and leaves everything else in that decision in force.

---

## 0. What this document is, and what was NOT done to produce it

This is the complete frozen specification of the AM-1 measurement:
what is measured, on what grid, against what thresholds, under what validity
rule, with what detection floor, and what observation would falsify what.

**No measurement of any kind was performed in producing it.** No lattice was
reduced, no basis was generated, no error draw was sampled, no arm statistic was
computed, no quantile was estimated, no `V` was evaluated, and no numerical
prediction was evaluated. Every number appearing below is either (a) fixed by
`DEC-20260806-00deff`, (b) quoted from a committed artifact with its source
named, or (c) a structural constant of the design carried unchanged from the
committed frozen text of BATCH-436ddd. Category (c) constants are marked
**[carried]**; category (b) quotations are marked **[quoted: source]**.

This split exists for one reason. BATCH-436ddd's freeze was hash-enforced and
the validator confirmed it three independent ways, but the snapshot followed the
run, so nothing *external* attested that the frozen text predated the
measurement (`EV-MLKEM-94f036`, `unresolved_confounds`, "HARNESS GAP"). This
document is snapshot-committed under TASK-20260806-53ad5c **before** the
measurement task TASK-20260806-ca4377 is dispatched. Its sha256 is written to
`prereg_sha256.txt` in this directory. The measurement loads this file
read-only, re-hashes it, compares against the notarized receipt, and **aborts on
any mismatch**.

**No quantity in this document is tunable to data that does not yet exist.**
Section 8 enumerates every constant with its provenance so that a reviewer can
check this claim mechanically rather than take it on trust.

---

## 1. Carried unchanged from the committed frozen text (not amended by AM-1)

All **[carried]**, from `DEC-20260805-4823db` as implemented in the frozen
pre-registration of BATCH-436ddd (`b2a_report.md` Part 1, sha256
`2893a6b0cebf0a3ff40d779c6f66fb7852cad5830165a93079ddea6e6efd02b6`, 7339 bytes)
and from `b2a_results.json` `config`/`seed_scheme`:

* **Cells.** `(d, beta) in {(100,30), (100,40), (140,30), (140,40)}`;
  `k = d/2`; `q = 3329`; error law CBD_{eta=2}.
* **Statistic.** `R = ||Q^T e||^2 / ||e||^2`, `Q` the orthonormal tail-`beta`
  GSO frame. `r(p) = q_emp(p) / q_Beta(p)`, with the frozen estimator
  `q_emp(p) = sort(R)[round(p*N)-1]` at `N = 2^20` error draws per cell, so
  index `1024` at `p = 2^-10` and index `16` at `p = 2^-16`.
* **Draw counts.** `8` draws per arm (`draws_per_arm = 8`), for every arm
  including the Haar null.
* **Seeds.** `seed_basis(d,beta,i) = 700000 + d*1000 + beta*10 + i`;
  `seed_error(d) = 20260805 + d`;
  `seed_haar(d,beta,j) = 900000 + d*1000 + beta*10 + j`;
  `seed_graded(d,beta,j) = 500000 + d*1000 + beta*10 + j`;
  `seed_gauss_error(d) = 20260806 + d`. **The seeds are the cache**: no `.npz`
  reduction cache exists anywhere in the repository, and BATCH-436ddd
  regenerated all 32 reductions from these seeds and verified them against
  BATCH-a51f91 at max deviation `0.0` in both compared fields
  **[quoted: `b2a_results.json` `instrument_checks.reduction_reproduction_vs_BATCH_a51f91`]**.
  The AM-1 measurement regenerates from seeds and reports the same verification.
* **Arms.** Haar null (`t = 1` law), unreduced, LLL-only, BKZ arms, and the
  graded family. **Null-arm-first discipline** is unchanged.
* **P1 / P2**, verbatim: `|r(2^-10) - 1| <= 0.05` and `|r(2^-16) - 1| <= 0.10`
  on the pooled-over-8-bases quantile in all four cells; between-basis component
  of `Var(R)` at most `20%` of the total in all four cells. P1/P2 are **not**
  re-scored against any rule other than the one frozen in BATCH-a51f91, and
  under AM-2 they are **no longer treated as an adjudicating predicate** — the
  governing decision records that they return identical verdicts on the Haar
  null arm and the real arm in all four cells (between-fraction `0.0000000`).
* **The Gaussian-error null of the null (N1/N2)** is retained as an
  **instrument check, not a control.** For a rotationally invariant error and
  any fixed rank-`beta` projector, `R ~ Beta(beta/2, (d-beta)/2)` exactly, so
  N1/N2 cannot fail unless the code is wrong. It is reported in that language
  and the phrase "sharpest control" is not used.
* **`E[R] = beta/d` is forced** for every projector, reduced or not, and carries
  zero information. Recovering `Beta(beta/2,(d-beta)/2)` on the Haar arm is an
  instrument check constructed by the theorem, never a control that passed.

### 1.1 The graded family, and one implementation requirement the grid change forces

`Q_t = QR( sqrt(1-t) * E_S + sqrt(t) * G )`, `E_S` the `d x beta` selector of a
uniformly random `beta`-subset `S` of coordinates, `G` a `d x beta` iid standard
normal **[carried]**. Per draw `j` the pair `(S_j, G_j)` is drawn once and
reused across every `t`, so the family is a path.

**Requirement, frozen now:** `(S_j, G_j)` MUST be drawn from
`seed_graded(d,beta,j)` **before and independently of the `t` list**, in the
same draw order as BATCH-436ddd. Consequence: extending the grid from 7 to 13
points does not perturb the paths, and the six shared `t` values
(`0, 0.05, 0.1, 0.25, 0.5, 1.0`) are measured on the *same* paths as
BATCH-436ddd. This is what makes AM-1's "so the two runs remain comparable at
their shared points" clause checkable rather than aspirational.

**Reproduction check, frozen now:** the measurement reports, per cell and per
shared `t`, `mean_j r(2^-10)` from both runs and their difference in units of
`SE_diff`. A shared-point difference exceeding `1 * SE_diff` is an **instrument
discrepancy**, reported as such, and is not a result about anything.

---

## 2. The frozen `t` grid (AM-1)

```
t in [0, 0.0025, 0.005, 0.0075, 0.01, 0.015, 0.02, 0.03, 0.05, 0.1, 0.25, 0.5, 1.0]
```

Thirteen points, taken **exactly** as `DEC-20260806-00deff` AM-1 `new_grid`
freezes them. No point is added, removed, reordered or re-spaced by this
document.

Why this grid, restated from the governing decision so the measurement carries
its own justification: the family's expected coordinate overlap is
`A(t) = (1 + (beta-1)t) / (1 + (d-1)t)`, whose range-midpoint sits at
`t = 1/(d+1)` — `0.009901` at `d = 100` and `0.007092` at `d = 140`
**[quoted: `DEC-20260806-00deff` rationale]**. The superseded grid's first
interior point was `0.05`, five to seven times past the midpoint, so `88.5%` of
the alignment excess was already gone at the first interior sample and G3 was
left demanding a strict ordering among six exchangeable noise arms. The new grid
places **at least four points below** each midpoint (`0.0025, 0.005, 0.0075` and
`0` below `0.007092`; those plus `0.01` below `0.009901`) and **at least four
above** (`0.015, 0.02, 0.03, 0.05, 0.1, 0.25, 0.5, 1.0`), and retains
`0, 0.05, 0.1, 0.25, 0.5, 1.0` from the superseded grid for cross-run
comparability.

`t = 0` is the coordinate-aligned end. `t = 1` is a Haar projector drawn
independently of the null arm's, so the two share a law.

---

## 3. Threshold, in SE-of-the-difference units, at the declared draw count

Declared draw count: **8 draws per arm, both arms** **[carried]**.

For any arm `A` compared against the Haar null arm, with `sd` the between-draw
sample sd (`ddof=1`) of `r(2^-10)`:

```
SE_diff(A) = sqrt( sd_A^2 / 8 + sd_haar^2 / 8 )
shift(A)   = mean_j r_A(2^-10) - mean_j r_haar(2^-10)
shift_SE(A)= shift(A) / SE_diff(A)
gate(A)    = |shift_SE(A)| >= 4.0
```

**The gate threshold is `4.0` SE-of-the-difference units at 8 draws per arm**
**[carried: `gate_k = 4.0`, `N_DRAW = 8`]**.

Two honesty declarations about this threshold, made now:

1. It uses the *pooled* two-arm SE, not the Haar arm's own per-draw sd. That
   correction was made in BATCH-436ddd because the Haar arm is the one arm whose
   between-draw location variance is structurally near zero, which turned a
   nominal `4 s` test into an effective `~2.0-2.5 sigma` test. It is retained
   here unchanged.
2. **`4.0` is a nominal factor, not a p-value.** With 8 draws per arm the
   Welch degrees of freedom are at most 14, so the SE is itself estimated. No
   p-value, no significance level and no multiple-comparison correction is
   claimed anywhere in this design, and the measurement must not report one.

---

## 4. Validity of the demonstration: G1, G2, G3, and the rule

Let `m(t) = mean_j r_A(2^-10)` for the graded arm at grid point `t`, per cell.

* **G1 (high end).** `gate(t = 0)` clears, in all four cells. **[carried]**
* **G2 (low end).** `gate(t = 1)` does NOT clear, in any of the four cells.
  `t = 1` is a Haar projector drawn independently of the null arm's, so an
  instrument that fires here is broken. **This is the condition the demonstration
  can fail for the right reason.** **[carried]**
* **G3 (monotonicity, TIE-TOLERANT — this is what AM-1 replaces).**

### 4.1 The tie-tolerant G3

For each of the 12 consecutive pairs `(t_i, t_{i+1})` of the 13-point grid,
define the step

```
Delta_i = m(t_{i+1}) - m(t_i)
```

The design expects `m` non-increasing in `t`, so `Delta_i > 0` is an *increase*.
The SE of the step difference is computed two ways and **both are reported**:

```
SE_step_paired(i)   = sd_j( r_j(t_{i+1}) - r_j(t_i) ) / sqrt(8)      [ddof=1]
SE_step_unpaired(i) = sqrt( sd(t_{i+1})^2 / 8 + sd(t_i)^2 / 8 )      [ddof=1]
```

The paired form is the correct SE for this design, because `(S_j, G_j)` is
shared across `t` within a draw (§1.1). The unpaired form is the literal reading
of the superseded text. **Frozen resolution of the ambiguity: the recorded G3
outcome is the MORE SEVERE of the two readings** (`FAIL > TIE > PASS`), and both
readings are reported per step and per cell. This resolution is deliberately
conservative: it makes it impossible to gain permissiveness by choosing an SE
convention, which is the direction a reviewer should worry about given that AM-1
loosens G3.

Per cell, with `SE_step` denoting whichever reading is being scored:

* **G3-PASS** — no step has `Delta_i > 0`. `m` is non-increasing outright.
* **G3-TIE** — at least one step has `Delta_i > 0`, and **every** such step has
  `Delta_i <= 1.0 * SE_step(i)`.
* **G3-FAIL** — some step has `Delta_i > 1.0 * SE_step(i)`.

**Adjacency is irrelevant.** Consecutive ties do not promote TIE to FAIL. This
is the specific clause AM-1 removes: the superseded reading forced INVALID on
twelve violations whose largest was `0.765 SE`
**[quoted: `DEC-20260806-00deff` AM-1 `G3_replacement`]**.

**The tie tolerance is `1.0 * SE_step` at 8 draws per arm** **[fixed by AM-1]**.

### 4.2 The validity rule

Per cell:

| G1 | G2 | G3 | verdict |
|---|---|---|---|
| clears | does not fire | PASS | **VALID** |
| clears | does not fire | TIE | **PARTIAL** |
| clears | does not fire | FAIL | **INVALID** |
| fails | — | — | **INVALID** |
| — | fires | — | **INVALID** |

The **overall** verdict is the most severe cell verdict
(`INVALID > PARTIAL > VALID`). Per-cell verdicts and the overall verdict are
both reported; the overall verdict governs.

Consequences, declared now:

* **VALID** — the demonstration establishes that the instrument responds to the
  provenance of the projector across the graded path and returns to the null at
  the Haar end. It establishes nothing else. The real arm may then be reported
  *with* interpretation limited to the declared verdicts.
* **PARTIAL** — reported as PARTIAL, never rounded into either neighbour. The
  real arm is reported as measured, and interpreted only in the specific
  respects G1 and G2 license (dynamic range and null return), never in respects
  that rest on monotonicity.
* **INVALID** — an INSTRUMENT OUTCOME. No mathematical conclusion is recorded
  and the real arm is measured but NOT interpreted.

An INVALID verdict is **not** evidence about lattices, about reduction, or about
ML-KEM, in either direction. `AGENTS.md` rule 3 and the closure standard of
`docs/inventor-protocol.md` §4 both apply: a failed instrument is a statement
about the instrument.

### 4.3 Dynamic range

Reported per cell, in absolute units and in units of `SE_diff(t=0)`:

```
DR = m(t = 0) - m(t = 1)
```

Both ends of the dynamic range are reported at every cell, as the measurement
card requires, together with `shift_SE` at all 13 grid points.

---

## 5. The detection floor — mandatory, and what it forbids the measurement to say

`DEC-20260806-00deff` makes this a required field, not a courtesy: *"Any future
'absent' verdict in this goal states its floor or it is not a verdict."*

### 5.1 The two units the floor is stated in

**(a) In the statistic's own units.** The floor is `4.0 * SE_diff`, measured per
cell and per arm at 8 draws. Any arm not clearing its gate is reported as

> `|D| < 4.0 * SE_diff = <number>` (upper bound at 8 draws, `N = 2^20`)

and **never** as "absent", "no departure", "vanishes", "consistent with zero"
or any synonym. This wording requirement is frozen and is a completion-gate
item.

**(b) In `V` units — the mechanistically meaningful floor.** Define, exactly,
for a rank-`beta` projector `P = Q Q^T`:

```
V = sum_a ( P_aa - beta/d )^2   =   sum_a P_aa^2 - beta^2/d
```

`V` is a **deterministic scalar of the tail frame**: no error draws, no
quantiles, no sampling, milliseconds to evaluate. The Haar expectation is exact:
`E[V]_haar = 2*beta*(d-beta) / (d*(d+2))`.

**Frozen requirement: the measurement computes and reports `V` exactly for every
frame it touches** — all 13 graded grid points, the Haar null arm, the
unreduced/LLL/BKZ arms, and every beta-trend arm — alongside `E[V]_haar` and the
excess over it. This costs essentially nothing and it is the single cheapest
falsification route the red team identified.

**The floor in `V` units is reported as a measured bracket, not asserted.** The
graded path sweeps `V` continuously from the coordinate-aligned end to the Haar
end, so per cell the floor is the interval

```
[ max V among grid points whose gate does NOT clear ,
  min V among grid points whose gate DOES clear ]
```

with the midpoint quoted as the floor estimate. The AM-1 grid was designed to
bracket the transition, so this interval is a product of the design rather than
an extra measurement.

**Incumbent value, superseded by whatever the measurement brackets:** at
`(d = 100, beta = 30, 8 draws, N = 2^20)` the floor was bracketed at
`V in [1.801, 2.718]`, i.e. `V ~ 2.2` — the gate fires at `V = 2.718`
(`4.77 SE`) and fails at `V = 1.801` (`3.14 SE`)
**[quoted: BATCH-436ddd red-team report §3]**. No floor value is asserted here
for the other three cells; they are measured.

### 5.2 What the floor already forbids, before this run starts

Computed exactly on 16 bases per cell with zero error draws
**[quoted: BATCH-436ddd red-team report §4, recorded in `EV-MLKEM-94f036`]**:

| arm | d | beta | excess `V` over Haar | significance | bases positive |
|---|---|---|---|---|---|
| LLL only | 100 | 30 | +0.1863 | +10.2 sd | 16/16 |
| LLL only | 140 | 30 | +0.4386 | +16.6 sd | 16/16 |
| LLL+BKZ-30 | 140 | 30 | +0.1400 | +9.9 sd | 16/16 |

These residuals are **5 to 15 times below the `V ~ 2.2` floor**. Their effect on
`r(2^-10)` is roughly `+0.0007`, about `0.35 SE`; resolving one at `4 * SE`
would need on the order of **1000 frames per arm** against the **8** this design
runs.

Therefore, frozen now: **this instrument, at this configuration, cannot resolve
the known post-reduction residual, and the measurement is forbidden from
emitting any statement of the form "the departure is absent after reduction".**
Reduction suppresses the departure by 15–50x; it does not zero it. Every
negative this run can produce is an upper bound at the floor bracketed in §5.1,
and the report states the bound. `EV-MLKEM-94f036` records that this lane
reported an upper bound as an absence once; that is the specific error this
clause exists to prevent recurring.

---

## 6. The falsifier

The superseded pre-registration froze a single decay law — `Dn_A` approximately
constant in `beta`, i.e. `D_A(beta)/D_A(30)` tracking the Beta law's own
coefficient of variation `s(beta,d) = sqrt( 2(d-beta) / (beta(d+2)) )` — and the
red team then showed that a **zero-free-parameter geometry model predicts the
observed growth** (`D(60)/D(30) = 1.544` at `d = 140` against a measured `2.095`
and a pre-registered `0.603`) **and** predicts the `d = 100, beta = 60`
reversal. The pre-registered law was therefore **the wrong null to have frozen**:
it was derived for a `beta`-independent alignment excess and applied to an arm
whose alignment excess grows like `beta^2`, so its firing carried no information
about artifact status.

I do not repeat that mistake by picking one law and I do not repeat it by
picking the *other* law either — the geometry model was formulated **after**
seeing the growth it explains, and freezing a post-hoc winner as though it were
a prediction is the same error wearing the other hat. **I freeze both laws, in a
form where they make different predictions, and I declare in advance which
observation falsifies which, which comparisons are genuinely novel, and which
are reproductions of already-committed measurements.**

### 6.1 The two candidate laws, stated so that each can lose

**L1 — the dispersion law (the superseded falsifier, retained).**
A coordinate-aligned `R` is under-dispersed relative to Beta by a factor that
does not depend on `beta`, so the whole `beta` dependence of the departure sits
in the Beta law's coefficient of variation:

```
L1:   D_A(beta,d) / D_A(30,d)  =  s(beta,d) / s(30,d),
      s(beta,d) = sqrt( 2 (d - beta) / (beta (d + 2)) )
```

Predicted ratios, **[quoted: BATCH-436ddd frozen pre-registration §1.6, computed
there from the formula alone]**:

| d | beta=30 | beta=40 | beta=50 | beta=60 |
|---|---|---|---|---|
| 100 | 1.0000 | 0.8018 | 0.6547 | 0.5345 |
| 140 | 1.0000 | 0.8257 | 0.7006 | 0.6030 |

**L2 — the geometry law (`D` is a function of `V` alone).**
For iid coordinates with unit variance and fourth moment `mu_4`,
`Var(e^T P e) = 2*beta + (mu_4 - 3) * T` with `T = sum_a P_aa^2`. CBD_{eta=2}
has `mu_4 = 2.5` exactly, so the coefficient is `-0.5` and the entire
coordinate-alignment effect enters through the single scalar `V = T - beta^2/d`.
Normalising by `||e||^2`,

```
f(V) = 1 - V / ( 4 * beta * (1 - beta/d) )        [variance-deflation factor,
                                                   clipped below at 0]
```

To turn a variance deflation into a prediction for the `p = 2^-10` quantile
ratio **without a free parameter and without a normal approximation in a far
tail**, the frozen map is the exact Beta-quantile map: with `mu = beta/d`,
`nu = d/2 + 1`, let `Beta(a, b)` have `a = beta/2`, `b = (d-beta)/2` (mean `mu`,
variance `mu(1-mu)/nu`), and let `Beta(a', b')` be the Beta law with the **same
mean** and variance `f(V) * mu(1-mu)/nu`, i.e. `nu' = nu / f(V)`,
`a' = mu (nu' - 1)`, `b' = (1-mu)(nu' - 1)`. Then

```
L2:   D_pred(V) = Q_{Beta(a',b')}(2^-10) / Q_{Beta(a,b)}(2^-10)  -  1
```

`D_pred` has **zero fitted parameters**: `V` is computed exactly from the frame
(§5.1b) and everything else is `(d, beta, p)`. Sanity anchors that fix the map's
form and are not free: for an exactly coordinate-aligned projector
`V = beta(1 - beta/d)`, giving `f = 0.75` for **every** `beta` — reproducing the
CBD kurtosis factor the superseded text derived independently; for the unreduced
q-ary arm the geometry gives `V ~ beta^2 (d-k) / (k d)`, growing quadratically
in `beta`.

**Known defect of L2, declared now:** the map is a second-moment expansion
applied to a `2^-10` tail quantile, and it is documented to overshoot the
*magnitude* of `D` by `1.0-1.7x` **[quoted: red-team report §5]**. Magnitude is
therefore **not** scored (§6.2). This is a limitation of L2 declared in advance,
not an escape hatch discovered later.

### 6.2 F-A — the within-run test on the graded path (the genuinely novel one)

L2's content, stripped of its magnitude map, is: **`D` depends on the frame only
through `V`, and increases with `V`.** The AM-1 run measures three frame
families in one pass — the 13-point graded path, the real lattice arms
(unreduced / LLL-only / BKZ), and the beta-trend arms — and `V` is exact and
free for all of them.

* **F-A1 (ordering — parameter-free, and this is the falsifier that counts).**
  Over all measured frames in a cell whose gate clears (§5: frames below the
  floor carry no information and are excluded, by declaration, before any data
  exists), L2 is **FALSIFIED** if there exists a pair with `V_1 > V_2` and
  `D_1 < D_2 - 1.0 * SE(D_1 - D_2)`. It is **CONSISTENT** if no such pair
  exists. The largest such inversion is reported whether or not it crosses the
  threshold.
* **F-A2 (shape — reported, scored, but not falsifying on its own).** Per cell,
  for gate-clearing grid points, `rho(t) = [D_meas(t)/D_meas(0)] / [D_pred(V(t))/D_pred(V(0))]`.
  A constant multiplicative bias in the map cancels exactly in this ratio.
  Declared band: `rho(t) in [0.5, 2.0]` for all scored points is **CONSISTENT**;
  any point outside is **SHAPE-DISTORTED**. `max |log2 rho|` is reported.
  **Declared now: a SHAPE-DISTORTED outcome with F-A1 CONSISTENT is recorded as
  a failure of the second-moment-to-far-tail map, NOT as falsification of L2 as
  a mechanism.** The factor-of-two band is set at the same order as the map's
  documented `1.0-1.7x` magnitude bias; it is not derived from any unmeasured
  quantity, and no verdict in this document turns on it alone.
* **F-A3 (magnitude — diagnostic only, no verdict).** `D_meas / D_pred` is
  reported per point. No threshold is attached to it, for the reason stated in
  §6.1.

**Novelty accounting for F-A, declared now so that no reproduction is later
presented as a prediction.** Already-measured points, which F-A scores but which
constitute **reproduction, not independent evidence for L2**:

* all four cells at `t in {0, 0.05, 0.1, 0.25, 0.5, 1.0}` (BATCH-436ddd's
  graded grid, which also included `0.75`, not on the AM-1 grid);
* `(d=100, beta=30)` additionally at `t in {0.005, 0.01, 0.02}` (the red team's
  post-hoc feasibility probe, explicitly recorded there as **not**
  pre-registered evidence).

**The NOVEL subset — 25 points never measured — is declared now and scored
separately:** `t in {0.0025, 0.0075, 0.015, 0.03}` in all four cells (16
points), plus `t in {0.005, 0.01, 0.02}` in the three cells other than
`(100,30)` (9 points). F-A1 and F-A2 are reported **twice**: over all points,
and over the NOVEL subset alone. **Only the NOVEL-subset result is admissible as
a test of L2.** The all-points result is a reproduction check.

### 6.3 F-B — the beta trend, where L1 and L2 disagree

Measured as before at `beta in {30, 40, 50, 60}` at each `d`, with the reduction
held fixed at BKZ-40 so that only `beta` varies **[carried]**. Note, because
BATCH-436ddd's report did not state it: fixing the reduction at BKZ-40 means the
beta-trend reads `seed_basis(d, 40, i)`, so its `beta = 30` row is a **different
basis set** from the `(d, 30)` cell tables and its `D(30)` is not the cell-table
headline. The measurement states this explicitly in its report.

Both laws are evaluated per arm per `d`, with L2's prediction computed from each
arm's own exactly-computed `V(beta, d)`:

```
ratio_meas = D_A(60,d) / D_A(30,d)
ratio_L1   = s(60,d) / s(30,d)                       (0.5345 at d=100; 0.6030 at d=140)
ratio_L2   = D_pred(V_A(60,d)) / D_pred(V_A(30,d))   (computed at run time from exact V)
```

**Which observation falsifies which — declared now:**

| observation | L1 | L2 |
|---|---|---|
| `ratio_meas` within `+-25%` of `ratio_L1` and outside that band around `ratio_L2` | CONSISTENT | **FALSIFIED** |
| `ratio_meas` within `+-25%` of `ratio_L2` and outside that band around `ratio_L1` | **FALSIFIED** | CONSISTENT |
| within `+-25%` of both (bands overlap) | NOT DISCRIMINATING | NOT DISCRIMINATING |
| outside both bands | **FALSIFIED** | **FALSIFIED** |
| `ratio_meas >= 0.90` on an arm where `ratio_L1 <= 0.7` | **FALSIFIED** (the departure fails to decay when the parameter meant to destroy it doubles) | judged by the rows above |
| `D_A(30,d)` does not clear its own `4.0 * SE_diff` gate | NOT APPLICABLE | NOT APPLICABLE |

The `+-25%` band is **[carried]** from the superseded `CONSISTENT` clause. The
`0.90` artifact-tell threshold is **[carried]**. The NOT APPLICABLE branch is
**[carried]** and is now additionally reported as an upper bound at the floor
(§5.1a) rather than as a missing departure.

**Where the two laws can and cannot discriminate — declared now, so that
agreement on a non-discriminating arm is not counted as support:**

* **The coordinate-aligned arm (`t = 0`) CANNOT discriminate.** There
  `V = beta(1 - beta/d)` makes `f = 0.75` for every `beta`, so L2's entire
  `beta` dependence collapses into the Beta quantile — the same place L1 puts
  it. The two laws predict nearly the same ratio there by construction. Any
  agreement or disagreement on this arm is recorded as NOT DISCRIMINATING
  regardless of what it shows.
* **The unreduced arm DISCRIMINATES.** There `V ~ beta^2 (d-k)/(k d)` grows
  quadratically, so L2 predicts a ratio near or above `1` (growth) while L1
  predicts `0.53 / 0.60` (decay). This is the arm the table above is really
  about.
* **The LLL-only and BKZ-40 arms discriminate weakly**, since their `V` excesses
  are small; they are scored and their discriminating power is reported via the
  separation between `ratio_L1` and `ratio_L2`, not assumed.

**Novelty accounting for F-B, stated plainly: F-B is a REPRODUCTION.** The
unreduced, LLL-only, BKZ-40 and coord arms at `beta in {30,40,50,60}` at both
`d` were all measured in BATCH-436ddd, and L2 was formulated after those
measurements were seen. Re-running them tests reproducibility and the
implementation, and it tests L1 (which was genuinely pre-registered before the
data existed), but **it does not constitute an independent test of L2, and the
measurement report must say so in those words.** The independent test of L2 in
this batch is F-A on the NOVEL subset (§6.2).

### 6.4 The cheapest falsification of L2, named and placed out of scope

L2 locates the departure in a `beta`-dimensional subspace confined to a
`k`-dimensional coordinate block, which puts the spill boundary at `beta <= k`;
the superseded mechanism put it at `beta <= d - k`. Both tested `d` have
`k = d/2`, so the two are numerically indistinguishable in every cell this
design measures. **The discriminating test is any `k != d/2`.** It is named in
`DEC-20260806-00deff` `next_actions` as carried, it is **not** in this
measurement's scope, and the measurement must not claim to have tested it. Its
absence is the largest single hole in L2's support and is reported as such.

---

## 7. What the measurement governed by this document may not do

1. No status change, no hypothesis movement, no evidence record. The measurement
   is an executor artifact of observations.
2. No claim about ML-KEM security, about any FIPS 203 parameter set, or about
   any cost model. **Claim tier TOY.** No number measured at `d <= 140`,
   `beta <= 60` is transported to `beta = 606`, `d = 1420`, or to any other
   parameter set, by extrapolation or by analogy.
3. No interpretation beyond the declared verdicts of §4 and §6, and none at all
   on the real arm if the overall verdict is INVALID.
4. No "absent", in any wording, without its floor (§5).
5. No editing of this document, no re-derivation of its thresholds, and no
   substitution of a "better" grid. If the measurement believes a threshold here
   is wrong, it records the objection in its report **and runs the frozen
   specification anyway** — which is exactly what BATCH-436ddd's executor did
   with the grid it had, correctly.
6. Budget exhaustion, timeout, crash or any infrastructure failure is
   **never** negative mathematical evidence (`AGENTS.md` rule 3). It is reported
   as infrastructure and the affected cell is reported as not measured.
7. P1/P2 are not offered as an adjudicating predicate; AM-2 removed that role.
8. The beta trend is four points at two `d`. It is not a law.

---

## 8. Provenance of every constant in this document

| constant | value | provenance |
|---|---|---|
| `t` grid | 13 values, §2 | fixed verbatim by `DEC-20260806-00deff` AM-1 `new_grid` |
| G3 tie tolerance | `1.0 * SE_step` | fixed by `DEC-20260806-00deff` AM-1 `G3_replacement` |
| gate factor | `4.0 * SE_diff` | carried, `b2a.py` `GATE_K = 4.0` |
| draws per arm | `8` | carried, `b2a.py` `N_DRAW = 8`, `config.draws_per_arm` |
| error draws per cell | `N = 2^20` | carried, `config.errors_per_cell = 1048576` |
| tail levels | `2^-10`, `2^-16` | carried, `config.tail_levels` |
| cells | `{100,140} x {30,40}` | carried, `config.cells` |
| beta-trend betas / reduction | `{30,40,50,60}` at BKZ-40 | carried, `config.ext_betas`, `ext_bkz_blocksize` |
| all seed formulas | §1 | carried, `results.json` `seed_scheme` |
| P1 / P2 tolerances | `0.05`, `0.10`, `20%` | carried from BATCH-a51f91 via the frozen text |
| L1 predicted ratios | table in §6.1 | quoted from BATCH-436ddd frozen pre-registration §1.6 |
| `+-25%` CONSISTENT band | `+-25%` | carried from the superseded §1.6 |
| `0.90` artifact-tell | `0.90` | carried from the superseded §1.6 |
| `mu_4` for CBD_{eta=2} | `2.5` exactly | closed form; measured at `2.49961 / 2.500359` as an instrument check |
| `E[V]_haar` | `2 beta (d-beta) / (d(d+2))` | exact closed form |
| incumbent floor | `V in [1.801, 2.718]`, `~2.2` | quoted, red-team report §3, `(100,30)` only; superseded per cell by the measured bracket |
| known post-reduction residuals | `+0.1863 / +0.4386 / +0.1400` | quoted, red-team report §4, recorded in `EV-MLKEM-94f036` |
| geometry-model reference points | `1.544` vs measured `2.095` at `d=140` | quoted, red-team report §5 |
| F-A2 band | `rho in [0.5, 2.0]` | set here, at the order of the map's documented `1.0-1.7x` bias; no verdict turns on it alone (§6.2) |
| NOVEL subset | 25 points, §6.2 | derived from the committed grids of BATCH-436ddd and the red-team probe |

Nothing in this table depends on a measurement that has not yet been made. The
only quantities computed at run time are those explicitly declared as such:
`SE_diff`, `SE_step`, the measured `V` per frame, `D_pred(V)` evaluated at those
`V`, and the per-cell floor bracket.

---

## 9. Notarization

* `prereg_sha256.txt` in this directory contains the sha256 of this file and
  nothing else.
* TASK-20260806-53ad5c snapshot-commits this directory **before**
  TASK-20260806-ca4377 is dispatched. The measurement verifies this file's
  sha256 against the notarized receipt and **aborts on mismatch**.
* If the measurement finds a mismatch, that is a harness failure, not a result,
  and the run does not proceed.
* This ordering — freeze, notarize externally, then measure — is the specific
  gap `EV-MLKEM-94f036` records as open. Whether it is now closed is for the
  validator (TASK-20260806-64089c) to judge against the git record, not for this
  document to assert.

**Declaration, on the record: no lattice was reduced, no draw was sampled, and
no arm statistic, quantile or `V` was computed in the production of this
document.**
