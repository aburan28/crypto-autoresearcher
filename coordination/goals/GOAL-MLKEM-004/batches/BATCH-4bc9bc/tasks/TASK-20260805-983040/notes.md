# VAL-20260805-983040 — what I actually re-derived

Validator notes for `TASK-20260805-983040`, reviewing snapshot `0d34dfcb3`
(`TASK-20260805-985c85` archiving `TASK-20260805-74a8e9`), GOAL-MLKEM-004,
BATCH-4bc9bc, batch 6 of 6.

**Scope binding on every number below.** Toy scale: m=35, n=25, d=60, q=127,
sigma=2, eta=2; one LWE instance, one sieve database. No ML-KEM break claim, no
security proof, no FIPS 203 parameter set affected or cleared, no speedup, no
exponent moved. AGENTS.md rule 12 UNMET and UNWAIVED; no `EV-MLKEM-*` or `KN-*`
status change is made or proposed. I did not produce this package and did not
repair it. I ran no `git commit`; `git status` was clean before and after.

**Verdict: ADMISSIBLE_WITH_DEFECTS.** Seven numbered defects in `report.yaml`.

---

## 1. What I ran

Four scripts, all writing only to my scratchpad:

1. `val_t1.py` — full independent T1 re-derivation (593.6 s). Regenerates the
   instance from seed 20260803206, re-verifies the membership certificate with
   my own code, reconstructs the candidate set from the archived seed, draws
   **my own 16-member ablated ensemble on seeds 8830550000–15** (disjoint from
   the producer's 20260805740000–15), implements the frozen rule from its
   definition, evaluates the real arm, and adds two arms the package does not
   have: **ABL-X-only** and **ABL-Y-only**.
2. `val_t2sens.py` — SENS-T2 re-derived three ways, with `margin_stats`,
   `calperm11` and the verdict rule reimplemented from their definitions rather
   than imported.
3. `resolve.py --stage t2 --outdir <scratch>` — the recorded command, with only
   the output directory redirected so no producer artifact could be overwritten.
4. `val_pool.py` — pooled 32-draw exact test, resampling stability, nesting
   audit.

Everything imports the closed form from the committed archived path
`coordination/goals/GOAL-MLKEM-004/batches/BATCH-a2bb63/tasks/TASK-20260804-f58d34/dependence.py`
(sha256 `82a41e39…`, matching that batch's receipt), never a copy.

---

## 2. T1 — does OUTSIDE survive my own draws?

### 2.1 The real arm reproduces exactly

| group | producer | validator | \|delta\| |
|---|---|---|---|
| near_miss_8 | 0.8645735620 | 0.8645735620 | 0.00e+00 |
| near_miss_25 | 0.7283259257 | 0.7283259257 | 0.00e+00 |
| uniform_8 | 0.9691921497 | 0.9691921497 | 0.00e+00 |
| uniform_25 | 0.9194287742 | 0.9194287742 | 0.00e+00 |
| secret_distribution_25 | 0.4149349955 | 0.4149349955 | 0.00e+00 |

Zero error at ten decimal places, from a separately written script. The three
values the log cross-checks also match the archived reviewer table at
`coordination/goals/GOAL-MLKEM-004/batches/BATCH-a2bb63/tasks/TASK-20260804-0ff29a/report.yaml`
line 294 (`SIEVE  0.7283  0.4149  0.9194`).

### 2.2 Is the interval constructed honestly? — yes on pipeline and scale

Both arms pass through the *same* closure in
`.../TASK-20260805-74a8e9/resolve.py`: same archived `phases`, same candidate
columns `C1[idx_cf]`, same archived `closed_form_cov`, same sigma, same q, same
`SUB` index sets and therefore the same K per group. Only X and Y differ.

The ablated X preserves the sieve's per-row `||x_i||` **exactly, row for row**,
and `closed_form_cov` reads X only through those norms and through `X X^T`.

I did not take the offset scale on trust — I measured it. Pushing the real Y and
an ablated Y through `dep.phases`:

| | off mod q mean | off mod q sd | cosPhi mean | cosPhi sd | max col-mean |
|---|---|---|---|---|---|
| real Y | 59.2636 | 50.7728 | +0.56937 | 0.61907 | 0.99390 |
| ablated Y | 59.1189 | 50.7516 | +0.56861 | 0.61999 | 0.99370 |

Matched to three decimals. **`OUTSIDE_LOW` is not an artifact of a mismatched
phase or offset scale.** This is the check the task card put first, and the
package passes it.

### 2.3 My own 16 draws — three survive, one flips

| group | producer interval | producer | my interval | mine |
|---|---|---|---|---|
| near_miss_8 | [0.8835, 0.9346] | OUTSIDE_LOW | [0.8981, 0.9493] | **OUTSIDE_LOW** |
| near_miss_25 | [0.7485, 0.8079] | OUTSIDE_LOW | [0.7364, 0.7970] | **OUTSIDE_LOW** |
| uniform_8 | [0.9691, 0.9887] | INSIDE | [0.9725, 0.9879] | **OUTSIDE_LOW** ← flips |
| uniform_25 | [0.9044, 0.9320] | INSIDE | [0.9062, 0.9299] | INSIDE |
| secret_distribution_25 | [0.4309, 0.5074] | OUTSIDE_LOW | [0.4305, 0.5089] | **OUTSIDE_LOW** |

**The three OUTSIDE_LOW verdicts survive.** `uniform_8` flips.

My leave-one-out returned exactly `1 LOW / 14 INSIDE / 1 HIGH` on all five
groups with pairwise-distinct draws, same as the producer's — as it must, since
that is an identity for a min/max interval, which the pre-registration says.

### 2.4 Pooling both ensembles: 32 draws

The producer's 16 and my 16 are independent draws of the same ensemble under
disjoint seeds, so they pool. Exact one-sided exchangeability
`p = (1 + #{ABL <= real}) / 33`:

| group | real | pooled [min, max] | #(ABL ≤ real) of 32 | p_exact |
|---|---|---|---|---|
| near_miss_8 | 0.8646 | [0.8835, 0.9493] | 0 | 0.0303 |
| near_miss_25 | 0.7283 | [0.7364, 0.8079] | 0 | 0.0303 |
| uniform_8 | 0.9692 | [0.9691, 0.9887] | 1 | 0.0606 |
| uniform_25 | 0.9194 | [0.9044, 0.9320] | 14 | 0.4545 |
| secret_distribution_25 | 0.4149 | [0.4305, 0.5089] | 0 | 0.0303 |

`0.0303 = 1/33` is the **floor** attainable with 32 draws — it means "below every
draw", not "p = 0.03 and no smaller".

### 2.5 Is 16 draws enough? — for three groups yes, for `uniform_8` no

Resampling 16 of the 32 pooled draws 2000 times and applying the frozen rule:

| group | P(OUTSIDE_LOW) | 16-draw minimum, 5th/50th/95th pct |
|---|---|---|
| near_miss_8 | 1.000 | 0.8835 / 0.8845 / 0.8981 |
| near_miss_25 | 1.000 | 0.7364 / 0.7440 / 0.7501 |
| uniform_8 | **0.495** | 0.9691 / 0.9691 / 0.9737 |
| uniform_25 | 0.000 | 0.9044 / 0.9044 / 0.9098 |
| secret_distribution_25 | 1.000 | 0.4305 / 0.4309 / 0.4465 |

**Answer to the task card's question 4: `uniform_8`'s INSIDE is a coin flip, and
the coin is fair to within a percentage point — 49.5%.** The real value 0.9692
sits inside the sampling distribution of the interval *endpoint*. `DEV-8` names
the boundary honestly ("Not a robust INSIDE; a seventeenth draw could move it")
but records it as a caveat; measuring it converts the caveat into a number, and
the number is 0.495.

There is a nice reflexive point here. `KN-TECH-1a5b7e` mode 5 exists to say
"a generated comparator is a measurement and needs a sample size — report the
interval, not the point". The entry stops one step short of its own lesson: an
interval's **endpoint** is also a point estimate with a sampling distribution,
and here that distribution is wide enough to decide a verdict.

### 2.6 The three stated bounds

- **"per-group false-`OUTSIDE_LOW` rate 1/16 = 6.25%"** — reproduced, with a
  correction. 1/16 is the leave-one-out rate on a 16-member set. The rate that
  applies to the verdict *actually emitted* is different: the real value is
  tested against an interval built from 16 *other* draws, so under the null
  there are 17 exchangeable values and `P(real is the minimum of 17) = 1/17 =
  5.88%`. Conservative by 0.37 pp, so nothing is oversold — but
  `KN-TECH-1a5b7e` promulgates the `1/n` form as a general prescription, where
  the right one is `1/(n+1)`. That is DEF-4.
- **"the groups share draws so rates must not be multiplied"** — correct, and
  understated. From `resolve.py`'s `SUB`, `near_miss_8` = `range(8)` is a strict
  subset of `near_miss_25` = `range(25)`, and `uniform_8` = `range(25,33)` is a
  strict subset of `uniform_25` = `range(25,50)`. The five groups are **three
  candidate families at two nesting levels**. "Three of five groups" is really
  "two of three families". That is DEF-5.
- **"z-scores −2.42 to −2.68"** — reproduced exactly, and correctly scoped to
  the three `OUTSIDE_LOW` groups (`uniform_8` is −1.90 and is not covered by the
  range). On my own ensemble the same three groups give −3.93, −2.78, −3.33, so
  z moves by more than a full unit between two equally valid 16-draw ensembles.
  The pre-registration calls z "reported never dispositive"; that caveat is
  load-bearing and is honoured.

### 2.7 The confound decomposition the package does not have

The pre-registration says the ablation removes "the ENTIRE dual family: the
q-ary lattice, the matrix A, the modulus, the sieve geometry of X, the shortness
of the dual vectors, and the X-Y coupling. Nothing algebraic survives."

That is a bundle. I split it, 6 draws each, through the identical pipeline.

| group | real | full ABL (16) | **ABL-X-only** (real Y kept) | **ABL-Y-only** (real sieve X kept) |
|---|---|---|---|---|
| near_miss_8 | 0.8646 | [0.8981, 0.9493] | [0.8822, 0.9375] | [0.8990, 0.9308] |
| near_miss_25 | 0.7283 | [0.7364, 0.7970] | [0.7334, 0.7917] | [0.7443, 0.8196] |
| uniform_8 | 0.9692 | [0.9725, 0.9879] | [0.9761, 0.9877] | [0.9740, 0.9860] |
| uniform_25 | 0.9194 | [0.9062, 0.9299] | [0.9108, 0.9270] | [0.9078, 0.9274] |
| secret_distribution_25 | 0.4149 | [0.4305, 0.5089] | [0.4329, 0.4818] | [0.4578, 0.4929] |

Real below the arm's minimum: `ABL-X-only` on 4 of 5 groups; `ABL-Y-only` on the
same 4 of 5 (all but `uniform_25`).

**Each half alone reproduces the full ablation.** In particular `ABL-Y-only`
holds the sieve geometry of X *exactly fixed* — the real database, the real
lattice, the real short vectors — and the entire departure is still there.

This is `docs/inventor-protocol.md` §3's decay test, and it comes back the wrong
way: the quantity does **not** decay when the component the framing credits it
to is restored. So `OUTSIDE_LOW` cannot distinguish "the real dual family is
structurally special" from "the statistic reads the exact algebraic relation
`y = A^T x mod q`, and no null matching only `sd(Y)` can preserve it". That is
DEF-1, and it is the most consequential thing I found.

To be fair to the producer: this does not make the ablation dishonest. It is the
declared ablation, applied identically to both arms, and the producer explicitly
declines to conclude the residual is object-specific. It means the *bundle is
not minimal*, and a non-minimal ablation cannot attribute its effect to any one
member of the bundle.

### 2.8 SENS-T1 and the "pinned" question (task card question 3)

The task card asks whether the two INSIDE groups being the pinned uniform ones
makes the pattern meaningful or the test vacuous. **Neither — the pattern does
not survive.**

- `uniform_8` did move (§2.3, §2.5).
- Only `uniform_25` is genuinely INSIDE, at pooled p = 0.4545, real value near
  the ensemble median.
- The uniform groups have the *narrowest* ablated intervals of the five (widths
  0.0196 and 0.0276, against 0.0511, 0.0594, 0.0765). If anything a departure
  should be easier to see there.

So the honest reading is that four of five groups sit at or near the pooled
ensemble's floor and one does not — a **broader** departure than the package
claims, with a **weaker** interpretation, at the same time.

Separately, SENS-T1 itself is a problem (DEF-3), and this is the one place the
package argues against a prior finding rather than absorbing it. Its stated
warrant, in the frozen PREREG block of `resolve.py`, is:

> RT-20260804-0ff29a OBJ-3 establishes that the uniform group's ST-6 ratio moves
> with the effective rank of X and with nothing else that varies between arms.
> A rank-5 X is therefore an object the statistic is known to be able to read

OBJ-3 draws the opposite conclusion from that same premise, at
`.../TASK-20260804-0ff29a/report.yaml`:

> Since every compared arm has full-rank X with matched norms, the uniform arm's
> 1.00 is a measurement of a quantity that was held constant. […] it is a null
> that fails only on a nuisance parameter nobody varied, so it reads as a
> demonstrated dynamic range while demonstrating none for the comparison at hand.

I measured `rank(real sieve X) = 35`; the ablated X is Gaussian and is also rank
35. **Effective rank is held constant between the arms actually compared.**
RANK5 varies exactly the direction the experiment does not.

And the scales do not line up. SENS-T1's pre-declared floor is a gap of 0.05 and
the demonstrated gap is 0.3952 — but the effects reported are `real − ensemble
min` of 0.0189, 0.0201 and 0.0160. The declared threshold is ~2.5× the largest
effect claimed; the demonstrated gap is ~20×. No positive control was run at the
effect's scale, and the gate was evaluated only on `uniform_25` — the one group
that returned INSIDE — and on none of the three that returned `OUTSIDE_LOW`.

---

## 3. T2 — RC-4 and DEV-5

### 3.1 Bit-reproducible

Re-running the recorded command (only `--outdir` redirected, so no producer file
could be touched) reproduces **every research field** of `results_t2.json`
identically — all 19 top-level keys excluding `log`, `timings`, `environment`.
`m_z` and `z` agree to the last bit at 17 significant figures, e.g. p=2 adjacent
`m_z = -0.27520327331785782`, `z = -3.1811249739498586`. `certificate`,
`T2_sensitivity.rows` and `known_answer_controls` are identical objects. The
archived K=10 known-answer cross-checks against BATCH-a2bb63 reproduce at
`abs_delta = 0.00e+00` in all six cells.

E1 met 2 of 3; E2 met at max |mean corr| = 0.0331 against the 0.15 bound; E3 NOT
met at 1 of 3, with the producer recording its own stated reason as wrong at
`report.md` lines 290–292; E4 no prediction by design. Scoring is mechanical in
code and matches the pre-declared refutation conditions.

One thing the summary layer drops (DEF-7): there are **four** departing cells,
not three. `uniform+correct` at p=5 is also `OP-HARDER`, at `z = −5.21` — the
largest magnitude of the three `OP-HARDER` labels. The producer's own table at
`report.md` line 311 carries it in bold, so this is an emphasis problem in the
narrative and the commit message, not a suppression. It matters because a larger
departure in the *uniform* family undercuts any reading in which the
adjacent-FFT-bin family is the structurally special one.

### 3.2 DEV-5's non-monotonicity — holds, three ways

**(a) Bit-reproduced on the producer's seed**, with `margin_stats`, `calperm11`
and the verdict rule reimplemented from their definitions rather than imported.
Matches `results_t2.json` `T2_sensitivity.rows` to four decimals on every row:
`m_z` = −0.8947 / −1.0989 / −1.1482 / −1.1296 / −0.8498, `z` = +1.61 / −34.83 /
−49.92 / −36.01 / +6.40, branches `OP-NULL, OP-HARDER, OP-HARDER, OP-HARDER,
OP-EASIER`.

**(b) Reproduced on my own seed, 11-point grid.** `OP-NULL` at t=0; `OP-HARDER`
at t = .05, .10, .20, .25, .35, .50, .60; `OP-EASIER` at t = .75, .85, .95.
Mean `corr(S_correct, S_k)` rises monotonically throughout, +0.0035 → +0.9747.
**The non-monotonicity is in the verdict, not in the dependence.**

**(c) Derived analytically, with no simulation at all.** For the SENS-T2
construction, `M = 0.5 + (1 − √t)·Z₀ − √(1−t)·max_k Z_k`, so

```
m_z(t) = (0.5 − √(1−t)·E[max₁₀]) / sqrt( (1 − √t)² + (1−t)·Var[max₁₀] )
```

with `E[max₁₀ N(0,1)] = 1.53844`, `sd = 0.58683`. This curve is **U-shaped**:
`m_z(0) = −0.8956`, minimum `−1.1849` at **t = 0.365**, `m_z(0.75) = −0.8346`,
and it crosses back through the independence baseline at **t\* = 0.7259**. My
analytic values track my simulated ones to ~0.02 across the whole grid.

So `OP-HARDER` is emitted for **every** shared fraction `t ∈ (0, 0.726)` and
`OP-EASIER` for `t > 0.726`. The map from dependence strength to verdict *sign*
is neither injective nor monotone.

This also shows the producer's pre-registered *mechanism* is wrong, in a
specific and identifiable way. The frozen block says "as t grows the common part
cancels in M and m_z rises". It does not, on `[0, 0.365]`: the shared component
enters the maximum as `√t·Z₀`, so raising t shrinks the margin's noise faster
than it lifts the margin's mean, and `m_z` *falls*. The producer's empirical
observation was right and its stated reason for what should have happened was
wrong — which is exactly the pattern it also recorded honestly for E3.

**Consequence confirmed and sharpened: no directional reading of `OP-HARDER` is
available anywhere in this campaign.** A two-point gate could not have caught
it, as the producer says; and the effect is structural, not a sampling accident,
which is a stronger statement than the producer made for itself.

### 3.3 A calibration note (DEF-6)

The comparator's own null-first leave-one-out fired a non-`OP-NULL` label in 2 of
48 applications — about 4.2% — against roughly 0.27% nominal for `|z| > 3` under
normality. The `sd` in z's denominator comes from 8 values, carrying about
`1/√(2(n−1)) = 27%` relative uncertainty. The two adjacent-family `OP-HARDER`
labels are `z = −3.18` and `z = −3.01`, i.e. 6% and 0.4% past the threshold; only
`z = +6.72` and `z = −5.21` are robust to that. The report does flag the tight
comparator spread as the reason `|z|` exceeds 3, which is the right instinct; it
does not flag the estimator uncertainty of that spread. The practical impact is
limited because DEV-5 already forbids signing the labels.

---

## 4. T3 and provenance

### 4.1 `report.md` extraction — verified, and clean

I recomputed it rather than accepting the Coordinator's assertion:
`results.json["report_markdown"]` UTF-8 encodes to **28,547 bytes**, sha256
`7432f56da05e98e3ae9ffbbbe46e4a24ef1dd704db1be064af989163acfff97c`; `report.md`
on disk is 28,547 bytes with the same digest; byte-identical `True`. The
declared hash and byte count in both the commit message and
`snapshot_receipt.json` are correct.

The pattern is worth endorsing: the producer, blocked by a runtime prohibition
on writing report `.md` files, placed the narrative in a JSON field **with a
declared sha256**, and the Coordinator verified that hash before extracting. It
converts an unavoidable manual step into a checkable one, and it is checkable by
a third party afterwards — I just did.

### 4.2 Both owed corrections land

`KN-TECH-1a5b7e` supersedes `KN-TECH-6c0e15` by **creation**, authorised by
`DEC-20260804-485fa6` NA-3. `git diff 049424129 0d34dfcb3 -- knowledge/techniques/`
shows only `KN-TECH-1a5b7e.md`, 660 insertions, 0 deletions — so the claimed 0
diff lines on `KN-TECH-6c0e15` and `KN-TECH-9d21c4` is verified.

Both corrections land, and land **twice each**: once in the front-matter "What
changed from `KN-TECH-6c0e15`, item by item" section, and once inline in the
body at the point of the original error, boxed as `CORRECTION 1` and
`CORRECTION 2`. That second placement is the one that matters — a stranger
reading the mode-4 case study encounters the correction where the wrong number
used to be, not in a changelog they may skip.

- **Correction 1** — cell count: "**33 of 33**: 21 T1 cells (3 families × 7
  groups), of which 7 are null cells, plus all 12 T2 cells", with the diagnosis
  that 18 was the count *displayed* in the log, not the count *scored*, sourced
  to `VAL-20260804-264ab9` DEF-3. Landed.
- **Correction 2** — the forcing is no longer scoped to `K > m` alone. The entry
  states the rank bound is correct and **vacuous at K = 8 and K = 25** ("because
  `8 <= 35` and `25 <= 35`. A `25 x 25` correlation matrix is not constrained by
  `rank <= 35`"), and then supplies the corrected mechanism for the `K ≤ m`
  regime — channel composition and Gram geometry, with the measured mean pairwise
  cosine +0.5562 against the predicted 0.5643. Landed, and it does the harder
  thing of replacing the wrong cause rather than merely deleting it.

`confidence` stays `single_run_experiment`, with a stated argument for not
raising it ("Two single runs are not a replication. Raising the field would be
the exact behaviour this entry exists to catch"). Correct.

### 4.3 Reading `KN-TECH-1a5b7e` as a stranger

It is a good entry, and better than the one it supersedes. Mode 5 is a real
addition: "if your comparator is generated […] it is a measurement and it needs
a sample size. Draw it at least 8 times before reading any residual against it,
and report the interval, not the point." The batch met its own rule (16 draws),
derived its rule's false-positive value before running, and stated the two right
cautions — that an n-draw min/max is a *tolerance* interval whose coverage is a
property of n alone, and that groups sharing draws must not have their rates
multiplied.

Two things I would put to a curator, neither of which is a status change and
neither of which I have made:

1. **DEF-4**: mode 5's `1/n` should be `1/(n+1)` for the rate quoted beside an
   OUTSIDE verdict. `1/n` is the leave-one-out rate that validates the rule's
   *implementation*; `1/(n+1)` is the exchangeability rate that applies to the
   *verdict*. The entry conflates them in a sentence written as a general
   prescription.
2. **§2.5 above**: mode 5 says report the interval not the point, and then reads
   a verdict off the interval's endpoint — which is itself a point estimate. On
   this batch's own data that endpoint's sampling spread decides a verdict 49.5%
   of the time. The entry could have derived that extension from the data it
   already had.

A discoverability gap, not a defect of this package: `KN-TECH-6c0e15.md` still
carries `superseded_by: null`, so the supersession is visible only from the newer
entry. `KN-TECH-9d21c4.md` is in the same state, so this is standing convention
forced by immutability, not a new lapse.

### 4.4 No wall-clock truncation; DEV-4 produced nothing

`resolve.py` contains **zero** `while` loops — every loop is
`for … in range(…)`; the one grep hit is the word "while" inside a prose string.
The imported `dependence.py` has four `while` loops, all testing integer
counters (`off < D`, `done < n_mc`, `off < N`, `done < Dm`). In neither file does
`time.time()` appear in a loop condition or in a branch deciding what is
measured. Verified, and stronger than asserted for `resolve.py`.

`DEV-4`: I probed the container directly. `/usr/bin/time` does not exist, and
`/usr/bin/time -v true` returns exit 127 with no program executed. The failure is
in the shell before Python starts, so that invocation **could not** have produced
a measurement. Correctly classified as infrastructure, per AGENTS.md rule 5.

`stdout_t1.log` is exactly 16,000 bytes, which looks like a truncation boundary
and is not one: it ends with `STAGE T1 COMPLETE`, and its 126-line common prefix
with the JSON `log` field is identical with no divergence (the two extra disk
lines are the `say()` calls that fire after `json.dump`).

Null-arm-first ordering, from `stdout_t1.log`: null header 9.4 s; ABL draws 00–15
from 26.0 s to 273.1 s; ensemble summary and leave-one-out at 273.1 s; SENS-T1
RANK5 at 288.6 s; real-arm section header at 288.6 s with the real values at
303.8 s. Verified. One precision note on the task card's phrasing: 288.6 s is
when the real-arm *section opens*; the real closed form is evaluated between
288.6 s and 303.8 s. Either way, strictly after every null-arm line was printed.

The derived-before-the-run value (`exactly 1 LOW / 14 INSIDE / 1 HIGH per
group`) is in the frozen PREREG dict, printed at t=0.0 s before any research
number, and met on all five groups — and on all five groups of my own ensemble.
Its evidential weight is nil by construction, since it is an identity for a
min/max interval over distinct values; the pre-registration says exactly that,
so it is not oversold.

---

## 5. Where this leaves the campaign's one open quantity

Not resolved, and now more precisely open than before.

**What is established.** The real dual family's ST-6 ratio sits below a
16-draw family-ablated ensemble on `near_miss_8`, `near_miss_25` and
`secret_distribution_25`, and it does so under *two* independent 16-draw
ensembles with disjoint seeds, at the tail floor (1/33) of the pooled 32 draws.
That is a genuine, replicated departure from the declared null, and it is more
than the campaign had before — the prior record was n = 2 draws.

**What is not.** That the departure is a property of the *dual family* — the
lattice, the sieve geometry, the shortness of the dual vectors. My ABL-Y-only
arm preserves all three exactly and reproduces the departure in full. The
question is now sharper than "is the residual object-specific": it is **is the
residual carried by the algebraic coupling `y = A^T x mod q` alone?** The
ablation that would answer it is one that *preserves* the coupling while
destroying the sieve geometry — resampling short dual vectors of the same
lattice by a different method, or a row operation that keeps the null arm inside
the true dual lattice.

Given batch 6 is the last under the current budget, that is forward guidance
rather than a next run: `docs/inventor-protocol.md`'s closure standard asks a
budget-exhausted stop to name what remains open, and this is it. It is not a
lane that has been shown dead; it is a lane with one specific, cheap,
un-run control standing between it and an interpretation.

**What must not be said.** Nothing here supports an ML-KEM claim, a security
claim in either direction, a cost claim, a correction to MATZOV.Nf, or a
statement about any FIPS 203 parameter set. `OP-HARDER` must not be read as
"dependence makes the attack harder" — DEV-5 forecloses that, and I have now
derived the foreclosure in closed form. Rule 12 remains UNMET and UNWAIVED, and
no `EV-MLKEM-*` record changes status on this report.

---

## 6. On the producer's conduct

Recording this because it is part of what a validation is for, and because the
defects above should not be read as bad faith.

This package repeatedly declined readings that were available and would have
flattered it. It ran interior grid points nobody asked for and reported the
anomaly they exposed (DEV-5) as the most important thing T2 produced — an
anomaly that *removes* the directional reading its own headline would otherwise
have had. It recorded its E3 reasoning as wrong rather than reinterpreting the
prediction. It flagged `uniform_8`'s 0.0001 margin itself. It recorded a
near-miss it caught before publishing (DEV-6, a relative difference that inverts
sign when `m_z < 0`), an invocation error that produced nothing (DEV-4), and
foreign scratch files in the shared container that it declined to read (DEV-9 —
those files are present and I confirmed I did not use them either). It states
"it does NOT conclude the residual is object-specific" and refers the call
upward.

DEF-3 is the one place it argued *against* a prior blocking objection instead of
absorbing it, and it did so in the open, citing the objection by ID in its own
frozen pre-registration. That is a reviewable error, which is the kind worth
having.

---

## 7. Files

- This report: `coordination/goals/GOAL-MLKEM-004/batches/BATCH-4bc9bc/tasks/TASK-20260805-983040/report.yaml`
- These notes: `coordination/goals/GOAL-MLKEM-004/batches/BATCH-4bc9bc/tasks/TASK-20260805-983040/notes.md`

Nothing outside that directory was created or modified. No `git commit` was run.
