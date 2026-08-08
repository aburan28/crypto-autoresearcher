# AM-3 — the AM-1 graded family re-run under the notarized replacement gate

TASK-20260806-e17677 / BATCH-a44d08 / GOAL-MLKEM-005 — **Section B**
Executor artifact. Observations, not interpretation.

**Claim tier TOY, unconditionally.** Nothing in this report bears on ML-KEM
security, on any FIPS 203 parameter set, on any attack cost, or on any cost
model. Every number is measured at `d in {100,140}`, `beta in {30,40}`,
`n = 8` draws, `N = 2^20` error vectors. Nothing is transported to
`beta = 606`, `d = 1420`, or to any other parameter set, by extrapolation or by
analogy. No hypothesis status moves, no evidence record is written, and no
heuristic is declared validated or refuted here.

---

## 0. The headline, stated first because the frozen text requires it

The mandatory positive control of pre-registration §3.5 **did not return
AM3-FAIL at `c = 6` in three of the four cells**. The frozen admissibility
clause of §3.5 reads:

> **if any cell fails to return AM3-FAIL at `c = 6`, the AM-3 gate is declared
> INADMISSIBLE for this goal and the demonstration reports that as its result**,
> with no verdict on the real arms.

Therefore:

> ### THE RUN'S RESULT: **THE AM-3 GATE IS INADMISSIBLE** by its own frozen admissibility clause.
> `d100_b30`, `d140_b30` and `d140_b40` return AM3-TIE at every `c` in
> `{1,2,3,4,6}`. Only `d100_b40` returns AM3-FAIL, at `c = 3`.

The AM-3 readings on the real arms **were computed and are recorded in full**
below and in `results_g3.json` — nothing is discarded — but under §3.5 they do
**not stand as a verdict on the real arms**, and they are marked WITHHELD
wherever a verdict would otherwise be stated. This is reported as an
instrument outcome. **It is not evidence about lattices in either direction.**

---

## 1. Notarized pre-registration verification (task constraint 1)

The frozen specification was loaded read-only, re-hashed, and checked against
**four independent carriers** plus the git record. It was not modified.

```
prereg path   : coordination/goals/GOAL-MLKEM-005/batches/BATCH-a44d08/
                tasks/TASK-20260806-843c40/prereg.md
prereg bytes  : 54928

sha256 recomputed by this run          : 8d00ca3f0977e7367cfd10f4eb01cc0d4d24dfdc1ecf9739ba3cc299ee2a6c80
sha256 expected by the task card       : 8d00ca3f0977e7367cfd10f4eb01cc0d4d24dfdc1ecf9739ba3cc299ee2a6c80
sha256 in prereg_sha256.txt (producer) : 8d00ca3f0977e7367cfd10f4eb01cc0d4d24dfdc1ecf9739ba3cc299ee2a6c80
sha256 in the notarized snapshot receipt (archive.path_sha256, and the
        separate prereg_sha256 field), TASK-20260806-0a1072
                                       : 8d00ca3f0977e7367cfd10f4eb01cc0d4d24dfdc1ecf9739ba3cc299ee2a6c80
sha256 OF THE BLOB INSIDE THE NOTARIZING COMMIT
        git show 9cb2d3e28ae7a474edbb116d694969470829e112:<prereg path>
                                       : 8d00ca3f0977e7367cfd10f4eb01cc0d4d24dfdc1ecf9739ba3cc299ee2a6c80

ALL FIVE AGREE. match = True. The abort-on-mismatch branch is implemented and
was not taken.
```

Git ordering, asserted against the **notarizing commit itself and not its
parent** (prereg §0.2, carried correction V-7):

```
git merge-base --is-ancestor 9cb2d3e28ae7a474edbb116d694969470829e112 HEAD  -> TRUE
HEAD at run time : 974ad579443984d9369ac050dadd800caa5d10f4
branch           : feat/crypto-autoresearcher-kb-adfc38
git log --follow -- <prereg path>  ->  EXACTLY ONE commit: 9cb2d3e28
worktree dirty   : yes, only untracked task directories of this batch's three
                   measurement tasks (see §9 anomaly A-2)
```

`prereg.md` was not modified by this task for any reason. No early durability
commit was made, for any reason (prereg §0.2). This task made no git commit.

**What this ordering does not close**, restated from prereg §0.3(1): git
ancestry cannot exclude off-repository pre-computation. That residue is closed
by harness structure, not by cryptography.

---

## 2. The seed-cache reproduction, re-verified BEFORE anything was scored

Task constraint 3. The reproduction was run and reported before the scorer was
called on any real datum. **NO NEW BKZ AND NO LLL WAS RUN.**

| check | what was compared | n | **max deviation observed** |
|---|---|---|---|
| **(a) the whole Section B measurement path** | every per-draw `r = q_emp(2^-10)/q_Beta(2^-10)` of all 13 graded arms and the Haar null arm, all four cells, regenerated from `seed_graded` / `seed_haar` / `seed_error`, against the committed BATCH-f19c37 record | **448** | **2.220446049250313e-16** |
| **(b) shared points vs BATCH-436ddd** | mean `r` at the six `t` shared with BATCH-436ddd, four cells | 24 | 4.440892098500626e-16 |
| **(c) basis generation half of the 32** | 32 unreduced q-ary bases regenerated from `seed_basis(d,beta,i)` via `FPLLL.set_random_seed` + `IntegerMatrix.random`, compared on `b0_norm_raw` (rel) and `gso_log2_slope_raw` (abs). **No reduction of any kind is run by this check.** | 32 | `b0_norm_raw` **0.0** exactly; slope **9.325873406851315e-15** |
| **(d) the LLL/BKZ half of the 32** | **NOT RE-RUN** — task constraint 3 forbids new BKZ | — | *[quoted, not measured here]* `32/32 at max deviation 0.0` against both prior batches [quoted: `EV-MLKEM-94c773`; BATCH-f19c37 `results.json` `instrument_checks`] |

**Max deviation over everything this run actually re-ran: `9.325873406851315e-15`**
(the raw-GSO log2 slope in check (c)); over the Section B measurement path
proper (check (a)): **`2.220446049250313e-16`**.

### 2.1 The 2.2e-16 is not 0.0, and the report says so rather than rounding it

The carried figure is "32/32 at max deviation **0.0**". Check (a) returned
`2.220446049250313e-16` and not `0.0`, so the difference is stated and located
rather than described as agreement.

* The deviation is **exactly zero in all 224 values at `d = 100`**. At
  `d = 140` the deviation takes only two nonzero values, both sub-ULP or
  one-ULP at that magnitude. Exact census over all 448 values:

  | deviation | count, `d = 100` | count, `d = 140` | total |
  |---|---|---|---|
  | `0.0` (bitwise identical) | **224 of 224** | 24 of 224 | **248** |
  | `1.1102230246251565e-16` | 0 | 28 | 28 |
  | `2.220446049250313e-16` | 0 | 172 | 172 |

  No other deviation value occurs anywhere. All 28 `d = 140` arms are affected,
  including the Haar null arm.
* A uniform one-ULP offset across every arm of a `d` implicates the shared
  divisor. Directly checked: `q_Beta(2^-10) = betaincinv(beta/2,(d-beta)/2,2^-10)`
  is **bitwise identical** to the committed value at `d = 100`
  (`0.12944269539129516`, `0.2053686670775116`) and differs by **exactly −1 ULP**
  at `d = 140`: committed `0.08929288718043772` against `0.08929288718043771`,
  and committed `0.14038737713830948` against `0.14038737713830945`.
* The scipy/`betaincinv` reference constant is a deterministic special-function
  evaluation, not a measurement, and this run used scipy 1.15.3.
* Honest limit of that localization: reconstructing `q_emp = r * q_Beta` from the
  recorded values agrees to `<= 3.85e-16` and is bitwise identical in 393 of 448,
  but that round-trip is not an exact inverse, so **a residual ULP-level
  difference in the order statistic itself is not excluded by this check.** The
  claim made is the narrow one: the observed deviation is confined to `d = 140`,
  is uniform at one ULP, and coincides exactly with a one-ULP difference in the
  deterministic reference divisor at `d = 140`.
* Effect on anything scored: the relative size is `2e-16`. The smallest scored
  quantity (`Delta`, `epsilon`, `SE_step`) is of order `1e-4`. No verdict, no
  step statistic and no positive-control outcome is affected at any digit
  reported.

Instrument check carried through: measured CBD_{eta=2} per-coordinate variance
`0.99990015` (`d=100`) / `1.00009586` (`d=140`) against the exact `1.0`, and
fourth moment `2.49960993` / `2.50035924` against the exact `2.5`.

---

## 3. G1 and G2 — reported SEPARATELY, per cell, and NOT in the AM-3 family

G1 and G2 are **[carried]** verbatim from BATCH-f19c37 §4 and are two per-cell
gates. Per prereg §3.3 they are **not** in the AM-3 multiplicity family, they
are reported separately, and **no p-value or significance level is claimed for
them anywhere.**

* **G1** — the `t = 0` arm CLEARS the `4.0 x SE_diff` gate against the Haar null.
* **G2 FIRES** iff the `t = 1` arm CLEARS that gate; the design requires it
  **not** to fire.

| cell | **G1 clears?** | `t=0` shift / SE_diff | **G2 fires?** | `t=1` shift / SE_diff | `t=1` upper bound |
|---|---|---|---|---|---|
| `d100_b30` | **yes** | +47.80 | **no** | +2.193 | `\|D\| < 4.0 x SE_diff = 0.004566` |
| `d100_b40` | **yes** | +66.24 | **no** | +2.034 | `\|D\| < 4.0 x SE_diff = 0.005185` |
| `d140_b30` | **yes** | +52.56 | **no** | −1.356 | `\|D\| < 4.0 x SE_diff = 0.005973` |
| `d140_b40` | **yes** | +77.24 | **no** | +1.017 | `\|D\| < 4.0 x SE_diff = 0.005665` |

Every `t = 1` reading is stated as an **upper bound at the declared floor**, at
`n = 8` draws and `N = 2^20`. It is not described as absence.

Carried disclosure, restated wherever the gate is cited (prereg §1): **`4.0` is
a nominal factor, not a p-value.** The validator measured this gate's realized
one-sided false-positive rate at `0.0015–0.0025` against a nominal `3e-5`, a
factor of about 60 [quoted: BATCH-f19c37 `validation_report.yaml` item 4 / V-5].

Frame `V` at the endpoints, deterministic, zero error draws:
`V(t=0)` = 21.0000 / 24.0000 / 23.5714 / 28.5714 against
`E[V]_haar` = 0.411765 / 0.470588 / 0.331992 / 0.402414, and `V(t=1)` =
0.4146 / 0.4711 / 0.3122 / 0.3943.

---

## 4. The AM-3 gate — reported SEPARATELY, per cell, exactly as frozen

Scored with prereg §3.2 exactly as written, with no re-derivation and no grid
change:

```
Delta_i         = m(t_{i+1}) - m(t_i),        m(t) = mean_j r_A(2^-10)
SE_step(i)      = sd_j( r_j(t_{i+1}) - r_j(t_i) ) / sqrt(8)     [ddof=1, paired]
epsilon_i       = 1.0 * SE_diff(A, t_i)
STEP VIOLATION iff (Delta_i - epsilon_i)/SE_step(i) > t_crit
t_crit          = t_{7,0.998} = 4.2071245566046755
```

`t_crit` recomputed independently here as `scipy.stats.t.ppf(0.998, 7) =
4.2071245566046755` — agrees to the last bit. `P(t_7 > t_crit)` recomputed as
`0.0019999999999982102` against the declared `0.002`.

**Per-cell AM-3 readings (recorded; WITHHELD as verdicts under §3.5, see §0):**

| cell | steps with `Delta_i > 0` | **step VIOLATIONS** | max AM-3 statistic | AM-3 reading | G1/G2 combined reading |
|---|---|---|---|---|---|
| `d100_b30` | 3 / 12 | **0 / 12** | −0.6547 | AM3-TIE | (would be PARTIAL) — **WITHHELD** |
| `d100_b40` | 2 / 12 | **0 / 12** | −1.2691 | AM3-TIE | (would be PARTIAL) — **WITHHELD** |
| `d140_b30` | 2 / 12 | **0 / 12** | −1.1441 | AM3-TIE | (would be PARTIAL) — **WITHHELD** |
| `d140_b40` | 2 / 12 | **0 / 12** | −0.1934 | AM3-TIE | (would be PARTIAL) — **WITHHELD** |

No step was `DEGENERATE` in any cell; the degenerate branch of §3.2 was
implemented and not taken.

### 4.1 Full step tables (all 48 comparisons, nothing omitted)

`stat` is `(Delta_i - epsilon_i)/SE_step(i)`; a VIOLATION requires
`stat > 4.2071245566046755`.

**`d100_b30`**

| i | t_lo → t_hi | Delta_i | epsilon_i | SE_step(i) | stat | incr | viol |
|---|---|---|---|---|---|---|---|
| 0 | 0.0 → 0.0025 | −3.783e-02 | 2.025e-03 | 1.793e-03 | −22.2222 | no | no |
| 1 | 0.0025 → 0.005 | −2.054e-02 | 1.759e-03 | 4.104e-04 | −54.3255 | no | no |
| 2 | 0.005 → 0.0075 | −1.230e-02 | 1.711e-03 | 9.609e-04 | −14.5764 | no | no |
| 3 | 0.0075 → 0.01 | −7.101e-03 | 1.258e-03 | 2.750e-04 | −30.3963 | no | no |
| 4 | 0.01 → 0.015 | −9.215e-03 | 1.240e-03 | 4.536e-04 | −23.0475 | no | no |
| 5 | 0.015 → 0.02 | −4.839e-03 | 1.227e-03 | 6.764e-04 | −8.9682 | no | no |
| 6 | 0.02 → 0.03 | −2.142e-03 | 1.305e-03 | 6.905e-04 | −4.9916 | no | no |
| 7 | 0.03 → 0.05 | −1.597e-03 | 1.447e-03 | 7.772e-04 | −3.9160 | no | no |
| 8 | 0.05 → 0.1 | **+6.080e-04** | 1.258e-03 | 4.528e-04 | −1.4357 | yes | no |
| 9 | 0.1 → 0.25 | **+7.379e-04** | 1.443e-03 | 1.077e-03 | −0.6547 | yes | no |
| 10 | 0.25 → 0.5 | **+1.008e-04** | 1.190e-03 | 5.497e-04 | −1.9819 | yes | no |
| 11 | 0.5 → 1.0 | −1.553e-04 | 1.292e-03 | 8.772e-04 | −1.6497 | no | no |

**`d100_b40`**

| i | t_lo → t_hi | Delta_i | epsilon_i | SE_step(i) | stat | incr | viol |
|---|---|---|---|---|---|---|---|
| 0 | 0.0 → 0.0025 | −3.433e-02 | 1.319e-03 | 1.592e-03 | −22.3956 | no | no |
| 1 | 0.0025 → 0.005 | −1.841e-02 | 1.321e-03 | 4.457e-04 | −44.2662 | no | no |
| 2 | 0.005 → 0.0075 | −1.073e-02 | 1.261e-03 | 8.494e-04 | −14.1165 | no | no |
| 3 | 0.0075 → 0.01 | −6.583e-03 | 1.401e-03 | 3.311e-04 | −24.1171 | no | no |
| 4 | 0.01 → 0.015 | −7.086e-03 | 1.425e-03 | 3.615e-04 | −23.5462 | no | no |
| 5 | 0.015 → 0.02 | −3.237e-03 | 1.378e-03 | 6.330e-04 | −7.2906 | no | no |
| 6 | 0.02 → 0.03 | −2.983e-03 | 1.255e-03 | 5.006e-04 | −8.4672 | no | no |
| 7 | 0.03 → 0.05 | −8.487e-04 | 1.481e-03 | 3.884e-04 | −5.9996 | no | no |
| 8 | 0.05 → 0.1 | −8.723e-04 | 1.367e-03 | 3.498e-04 | −6.4011 | no | no |
| 9 | 0.1 → 0.25 | −2.948e-04 | 1.252e-03 | 6.146e-04 | −2.5167 | no | no |
| 10 | 0.25 → 0.5 | **+1.554e-04** | 1.200e-03 | 3.957e-04 | −2.6412 | yes | no |
| 11 | 0.5 → 1.0 | **+5.088e-04** | 1.352e-03 | 6.641e-04 | −1.2691 | yes | no |

**`d140_b30`**

| i | t_lo → t_hi | Delta_i | epsilon_i | SE_step(i) | stat | incr | viol |
|---|---|---|---|---|---|---|---|
| 0 | 0.0 → 0.0025 | −4.535e-02 | 1.765e-03 | 1.494e-03 | −31.5481 | no | no |
| 1 | 0.0025 → 0.005 | −2.062e-02 | 1.672e-03 | 1.111e-03 | −20.0632 | no | no |
| 2 | 0.005 → 0.0075 | −9.286e-03 | 1.716e-03 | 6.168e-04 | −17.8360 | no | no |
| 3 | 0.0075 → 0.01 | −5.391e-03 | 1.530e-03 | 5.338e-04 | −12.9656 | no | no |
| 4 | 0.01 → 0.015 | −5.298e-03 | 1.708e-03 | 6.130e-04 | −11.4300 | no | no |
| 5 | 0.015 → 0.02 | −2.722e-03 | 1.732e-03 | 4.910e-04 | −9.0696 | no | no |
| 6 | 0.02 → 0.03 | −2.961e-03 | 1.681e-03 | 7.662e-04 | −6.0589 | no | no |
| 7 | 0.03 → 0.05 | −2.024e-03 | 1.519e-03 | 7.093e-04 | −4.9944 | no | no |
| 8 | 0.05 → 0.1 | −1.369e-03 | 1.258e-03 | 6.024e-04 | −4.3602 | no | no |
| 9 | 0.1 → 0.25 | **+4.972e-04** | 1.297e-03 | 6.990e-04 | −1.1441 | yes | no |
| 10 | 0.25 → 0.5 | **+3.054e-04** | 1.234e-03 | 6.168e-04 | −1.5056 | yes | no |
| 11 | 0.5 → 1.0 | −5.681e-04 | 1.342e-03 | 4.604e-04 | −4.1484 | no | no |

**`d140_b40`**

| i | t_lo → t_hi | Delta_i | epsilon_i | SE_step(i) | stat | incr | viol |
|---|---|---|---|---|---|---|---|
| 0 | 0.0 → 0.0025 | −3.940e-02 | 1.077e-03 | 1.172e-03 | −34.5445 | no | no |
| 1 | 0.0025 → 0.005 | −1.725e-02 | 1.555e-03 | 6.275e-04 | −29.9639 | no | no |
| 2 | 0.005 → 0.0075 | −8.799e-03 | 1.141e-03 | 3.815e-04 | −26.0568 | no | no |
| 3 | 0.0075 → 0.01 | −5.634e-03 | 1.014e-03 | 6.960e-04 | −9.5515 | no | no |
| 4 | 0.01 → 0.015 | −5.991e-03 | 1.138e-03 | 7.866e-04 | −9.0631 | no | no |
| 5 | 0.015 → 0.02 | −2.285e-03 | 1.223e-03 | 3.155e-04 | −11.1201 | no | no |
| 6 | 0.02 → 0.03 | −1.959e-03 | 1.158e-03 | 7.921e-04 | −3.9346 | no | no |
| 7 | 0.03 → 0.05 | −7.310e-04 | 9.515e-04 | 5.876e-04 | −2.8633 | no | no |
| 8 | 0.05 → 0.1 | −7.137e-04 | 7.984e-04 | 4.328e-04 | −3.4935 | no | no |
| 9 | 0.1 → 0.25 | −4.692e-04 | 9.150e-04 | 8.372e-04 | −1.6535 | no | no |
| 10 | 0.25 → 0.5 | **+2.375e-04** | 1.085e-03 | 5.367e-04 | −1.5798 | yes | no |
| 11 | 0.5 → 1.0 | **+1.246e-03** | 1.357e-03 | 5.736e-04 | −0.1934 | yes | no |

### 4.2 Detection floor of the AM-3 gate on this run's own data

An increase is flagged with probability about `1/2` at
`Delta_50% = epsilon_i + t_crit * SE_step(i)` (prereg §3.4). Realized per cell:

| cell | `Delta_50%` absolute | in units of `SE_diff` | as a fraction of the `4.0 SE_diff` gate width |
|---|---|---|---|
| `d100_b30` | 2.415e-03 … 9.570e-03 | 1.92 … 4.73 | 0.48 … 1.18 |
| `d100_b40` | 2.794e-03 … 8.016e-03 | 1.99 … 6.08 | 0.50 … 1.52 |
| `d140_b30` | 3.279e-03 … 8.049e-03 | 2.19 … 4.56 | 0.55 … 1.14 |
| `d140_b40` | 2.550e-03 … 6.006e-03 | 2.08 … 5.58 | 0.52 … 1.40 |

Every "0 violations" above is therefore an **upper bound at that floor**: at
`n = 8` draws and `N = 2^20`, no step's increase reached the flagging threshold,
which ranges from `1.92` to `6.08 x SE_diff` across the 48 comparisons. That is
a bound at a stated floor and is not a statement of absence.

The prereg's §3.4 power figure was declared **conditional** on the measured
ratio `SE_step_paired/SE_diff = 0.3599–0.4228` recurring [quoted: BATCH-f19c37
`validation_report.yaml` item 3]. **Realized here: min 0.2186, median 0.4729,
max 1.2072** over the 48 steps. The condition therefore held near the median and
was exceeded at the top of the range; the prereg's conditional
`Delta_50% ~= 2.52–2.77 x SE_diff` understates the realized upper end (`6.08`).
Recorded as an observation. **The false-failure rate of §3.3 is not conditional
on this ratio and is unaffected by it.**

---

## 5. Realized false-failure behaviour against the DECLARED rate

**Declared in the pre-registration, before any datum of this batch existed:**

```
per-step level                         alpha = 0.002 = P(t_7 > 4.2071245566046755)
multiplicity family                    12 steps x 4 cells = 48 comparisons
DECLARED FAMILY-WISE FALSE-FAILURE RATE ON A FLAWLESS INSTRUMENT = 0.096
                                       union bound 48 x 0.002, valid under ANY
                                       dependence among the 48
Sidak reference, NOT the declared rate = 0.0916233087376801
```

All three reproduce here from `t_crit` and the family size alone:
`scipy.stats.t.sf(4.2071245566046755, 7) = 0.0019999999999982102`;
`48 x 0.002 = 0.096`; `1 - 0.998^48 = 0.0916233087376801`.

**Realized on this run:**

| quantity | value |
|---|---|
| comparisons scored | **48** (12 steps x 4 cells, exactly the declared family) |
| steps with `Delta_i > 0` | **9 / 48** |
| **step VIOLATIONS** | **0 / 48** |
| max AM-3 statistic over the family | **−0.1934** (`d140_b40`, step 11), against `t_crit = +4.2071` |
| degenerate steps | 0 |
| `min epsilon_i` over the 48 | 7.98423e-04 — **all 48 `epsilon_i >= 0`** |
| expected violation count under a flawless instrument (upper bound) | `48 x 0.002 = 0.096` |
| observed violation count | **0** |

**How this is to be read, and how it is not.** The declared `0.096` is an
**upper bound** on `P(at least one VIOLATION | flawless instrument)` in prereg
§3.3's sense (true `m(t)` non-increasing at every step; paired per-draw
differences exchangeable across the 8 draws). One run yields one Bernoulli draw
of that family-wise event, and it came out `0`. A single realized count is **not
an estimate of a rate**, and it bounds nothing about the instrument unless the
instrument is flawless — which this run cannot establish and does not claim.
What is on the record is the pairing: **declared `<= 0.096` before any data;
realized 0 of 48 firings, with the largest statistic in the family `4.40`
below `t_crit`.** For contrast, and quoted rather than recomputed, the
withdrawn AM-1 rule's `P(at least one FAIL) = 0.9902` on a flawless instrument
[quoted: `DEC-20260806-14ac13` rationale; BATCH-f19c37
`validation_report.yaml` item 3].

Reported. Not interpreted. Whether the AM-3 rate declaration discharges AM-3's
requirement is for the Reviewer and the Coordinator, not for this run.

---

## 6. THE MANDATORY POSITIVE CONTROL — every `c`, per cell

Frozen by prereg §3.5. The step injected is fixed by a **data-independent rule**
declared before any datum: `i` = the step whose **lower endpoint has the largest
`SE_diff`** in that cell (argmax over the twelve lower endpoints `t_0 … t_11`;
`t_12 = 1.0` is never a lower endpoint). A constant `c * SE_diff(A, t_i)` is
added to **every draw** at grid point `t_{i+1}`, and the AM-3 criterion is
re-scored over all 12 steps. The injection is arithmetic on already-recorded
values: it reduces no lattice, draws no error, and is not an additional
measurement of any object.

The full `SE_diff` table for all 13 grid points is in `results_g3.json`
(`positive_control.<cell>.se_diff_per_grid_point`) so the argmax is checkable by
a reader rather than taken on trust.

| cell | injected step `i` | `t_i → t_{i+1}` | `SE_diff(A,t_i)` | uninjected `Delta_i` | **c=1** | **c=2** | **c=3** | **c=4** | **c=6** | smallest `c` giving AM3-FAIL |
|---|---|---|---|---|---|---|---|---|---|---|
| `d100_b30` | 0 | 0.0 → 0.0025 | 2.02458e-03 | −3.78294e-02 | TIE | TIE | TIE | TIE | **TIE** | **none** |
| `d100_b40` | 7 | 0.03 → 0.05 | 1.48131e-03 | −8.48721e-04 | TIE | TIE | **FAIL** | **FAIL** | **FAIL** | **3** |
| `d140_b30` | 0 | 0.0 → 0.0025 | 1.76496e-03 | −4.53542e-02 | TIE | TIE | TIE | TIE | **TIE** | **none** |
| `d140_b40` | 1 | 0.0025 → 0.005 | 1.55467e-03 | −1.72489e-02 | TIE | TIE | TIE | TIE | **TIE** | **none** |

Target-step statistic at each `c` (the injected step in isolation; a VIOLATION
needs `> +4.2071`):

| cell | c=1 | c=2 | c=3 | c=4 | c=6 |
|---|---|---|---|---|---|
| `d100_b30` | −21.0933 | −19.9644 | −18.8356 | −17.7067 | −15.4489 |
| `d100_b40` | −2.1854 | +1.6288 | **+5.4430** | **+9.2572** | **+16.8856** |
| `d140_b30` | −30.3664 | −29.1847 | −28.0030 | −26.8213 | −24.4578 |
| `d140_b40` | −27.4865 | −25.0091 | −22.5317 | −20.0543 | −15.0995 |

Every cell's **uninjected** AM-3 outcome is AM3-TIE, so no cell was already
firing and the control is not confounded by a pre-existing FAIL. In `d100_b40`
the gate fires because of the injection and at no smaller `c`.

### 6.1 The arithmetic of the three cells that do not fire, stated plainly

In `d100_b30`, `d140_b30` and `d140_b40` the argmax-`SE_diff` rule selects a
step in the steep-descent region of the graded family, where the measured
`Delta_i` is `−1.7e-02` to `−4.5e-02` while the injection unit `SE_diff(A,t_i)`
is `1.6e-03` to `2.0e-03`. The largest injection the frozen grid permits,
`6 x SE_diff`, is `9.3e-03` to `1.2e-02` — between one quarter and one third of
the descent it must first cancel. The injected `Delta_i` therefore stays
negative at `c = 6` (`−2.57e-02`, `−3.48e-02`, `−7.92e-03`) and no positive
increase exists to be flagged.

Stated as a property of the frozen control rather than as an opinion: §3.5
asserts that adding `c * SE_diff` creates "a known monotonicity violation of
exactly that size at step `i`". That identification holds only where the true
`Delta_i` is `0`. The rule that selects the step maximizes `SE_diff(A,t_i)`, and
`SE_diff` is largest where the arm's own dispersion is largest, which on this
family is at the top of the descent — the same steps where `|Delta_i|` is one to
two orders of magnitude above the injection unit. **The step-selection rule and
the injection scale are coupled through the same quantity**, and the control was
run exactly as frozen with that coupling in it.

This is an objection to the frozen text, recorded under prereg §5.5, and **the
frozen specification was run anyway and its verdict stands as written**: the
gate is INADMISSIBLE. No alternative injection point, no alternative `c` grid
and no rescoring was computed, here or anywhere in `results_g3.json`.

---

## 7. The arrangement in which this check could not fail (task constraint 7)

### 7.1 The two forms the pre-registration named for Section B (§3.6), carried verbatim

> * *Form 1 — the mirror of AM-1.* Setting `alpha` and `epsilon` so loose that no
>   real path can ever violate. Then "the instrument is VALID" is a property of
>   the gate, exactly as "INVALID" was a property of the withdrawn gate. Six
>   times this program has scored a control where its defect was invisible;
>   buying a `0.096` false-failure rate with a gate that cannot fire would be the
>   seventh.
> * *Form 2 — the AM-3 loophole.* Declaring a rate that is secretly conditional
>   on a nuisance quantity the run supplies, so that the declaration is not a
>   pre-registration at all.

### 7.2 Form 1: the test fired, and the frozen branch says so

Form 1 is exactly what §3.5's positive control exists to detect, and **on this
run it detected something**: three of four cells returned AM3-TIE at every `c`
up to `6 x SE_diff`. The frozen response is not a caveat — it is the
INADMISSIBLE branch, and it is this run's reported result (§0). The one cell
where the injected step was not in the descent region, `d100_b40`, fires at
`c = 3` with target statistic `+5.4430`, so the gate is not incapable of firing
in principle; what the control establishes is that **at the step the frozen rule
selects, in three of four cells, it did not fire at the frozen maximum `c`.**

Form 1's mirror — a gate that fires always — is addressed by §7.3 and by the
0-of-48 realized count in §5.

### 7.3 Form 2: the declared rate is mechanically free of every run-supplied quantity

The bound of prereg §3.3 is
`P(VIOLATION) <= P(Delta_i > t_crit * SE_step(i)) = P(t_7 > t_crit)`, and the
only property of the run it uses is `epsilon_i >= 0` pointwise. Checked
mechanically on this run: **all 48 `epsilon_i >= 0`, minimum `7.98423e-04`.**
The declared `0.096` recomputes from `t_crit` and the family size alone
(`48 x scipy.stats.t.sf(4.2071245566046755, 7)`), with no measured input. The
one statement that *is* conditional — the §3.4 power figure — is labelled
conditional in §4.2 and its realized ratios are printed there so the condition is
checkable.

### 7.4 The arrangement in which THIS RUN, specifically, could not have failed

Named, before the run, in `measure_g3.py` and reproduced here:

> A re-run that (i) re-derived the gate from the data it then scores, or
> (ii) scored only the injected positive control and not the real arms, or
> (iii) chose the "hardest" step after seeing where the gate fires most easily,
> or (iv) quietly computed the withdrawn `SE_step_paired` tolerance and reported
> whichever verdict read better. Any of these makes the reported verdict a
> property of the run rather than of the frozen gate.

Demonstration that this run is in none of them:

1. **(i) Not re-derived.** Every threshold is a module-level literal in
   `measure_g3.py` — `AM3_T_CRIT`, `AM3_EPSILON_K`, `AM3_ALPHA_PER_STEP`,
   `AM3_FAMILY_SIZE`, `AM3_DECLARED_FWER`, `GRADED_T`, `GATE_K`,
   `POSITIVE_CONTROL_C`, `POSITIVE_CONTROL_INADMISSIBLE_AT` — transcribed from a
   `prereg.md` whose sha256 is checked against five carriers including the blob
   inside the notarizing commit, with an implemented abort-on-mismatch. The
   ordering is a property of the git record (§1), not a claim by me.
2. **(ii) Both scored.** The real arms and the injected control are both scored,
   both reported, and every control run carries the cell's **uninjected** outcome
   beside it.
3. **(iii) Step choice is frozen and checkable.** `argmax` over the twelve lower
   endpoints of `SE_diff(A,t_i)`, a rule fixed in §3.5 before any datum of this
   batch existed. The full 13-point `SE_diff` table per cell is recorded so a
   reader can recompute the argmax. Note that this run had every incentive to
   pick a different step — the frozen choice is what produced the INADMISSIBLE
   result — and did not.
4. **(iv) The withdrawn rule is not implemented.** `grep` `measure_g3.py`: the
   withdrawn AM-1 G3 tolerance (a fixed multiple of `SE_step_paired` with no
   absolute floor and no multiplicity policy) appears nowhere. `SE_step_paired`
   occurs only as the denominator the frozen AM-3 statistic specifies, which is
   the correct scale for a paired design and a different object from the
   withdrawn **rule** (prereg §3.6 item 3). No post-hoc alternative rule was
   computed and none is presented beside the verdict (prereg §5.6). The
   validator's item-3 counterfactual is not cited and played no part in anything
   here.

An **implementation check of the frozen scorer** was run on synthetic inputs
whose correct outcome is fixed by construction — strictly decreasing → AM3-PASS;
one large injected increase → AM3-FAIL; an increase far below `t_crit` →
AM3-TIE. All three returned the expected outcome. This is a check that "the gate
returned X" is a statement about the gate rather than about a transcription
error. **It is not a result, not a control, and not an alternative rule.**

**The residue this run cannot close.** It cannot exclude off-repository
pre-computation, and it cannot make its own reading of the frozen text
independent of the text's author. It inherits every limit of the instrument:
`V` and every observable here are properties of a basis **presentation**, not of
a lattice (prereg §1.1); `n = 8` draws; and a criterion with a correctly
declared false-failure rate is still only a criterion about this instrument.

---

## 8. What this run does not reach

* **Claim tier TOY, unconditionally.** No number here transports to `beta = 606`,
  `d = 1420`, any FIPS 203 parameter set, any attack cost, or any other
  parameter set, by extrapolation or by analogy.
* No status change, no hypothesis movement, no evidence record. This is an
  executor artifact of observations.
* No interpretation beyond the frozen verdicts of prereg §3.2 and the frozen
  admissibility branch of §3.5. **This run does not declare the AM-3 repair
  adequate or inadequate, and does not declare any heuristic validated or
  refuted** — INADMISSIBLE here is the frozen text's own label for a
  positive-control outcome, not a judgement of the amendment.
* A VALID or PARTIAL reading would license only what G1, G2 and monotonicity
  license about the **instrument**; it adjudicates no law. `EV-MLKEM-94c773`
  records that this instrument at 8 draws is `9–13x` too coarse to resolve the
  residual that survives reduction [quoted: BATCH-f19c37
  `validation_report.yaml` item 5]. A new gate does not change that.
* No AM-4 adjudicator claim. `V` is presentation-dependent and no verdict here
  adjudicates a claim about a lattice.
* Independence in this batch is **procedural** — separate session, no shared
  scratch intended, snapshot before review — and **never model-level** (see
  anomaly A-1: the "no shared scratch" part did not hold in practice).
* **No arm anywhere in this report, in `results_g3.json`, or in `measure_g3.py`
  is described as "absent", showing "no departure", "vanishing", or "consistent
  with zero".** Every negative is an upper bound stated with its floor (§3, §4.2,
  §5).

---

## 9. Anomalies, deviations and objections — recorded, none discarded

**A-1 — infrastructure — the stdout capture of the authorized run was
corrupted by a concurrent writer.** `stdout` and `stderr` were redirected to
`stdout.log` / `stderr.log` in this session's scratchpad. A **concurrently
running sibling subagent — the Section C task TASK-20260806-c973e6, executing in
the same worktree** — resolved to the **same scratchpad directory** and wrote to
the **same `stdout.log` path**. The captured file therefore contains that task's
Section C verification header, a run of NUL/space padding, and only the **tail**
of this run's output (from the `[arms] d140_b40` line onward). The lost lines are
the four `[errors]`/`[arms]` progress lines. Impact assessment:
* The measurement process itself is unaffected: separate OS process, separate
  memory, deterministic seeds, its own output file
  (`results_g3.json`, written by this task's process at this task's path).
* Every number that was printed is also recorded in `results_g3.json`; the
  surviving tail agrees with the JSON at every digit.
* Corroboration that the computation was not disturbed: the seed-cache
  reproduction (§2) matches the committed record to `2.2e-16` with the deviation
  fully localized to a deterministic reference constant.
* **The run was NOT repeated** — `maximum_runs = 1` is a hard limit. The
  corrupted log is reported as corrupted rather than reconstructed and presented
  as a capture. Nothing in this report is transcribed from the damaged file.
* Class: `infrastructure_error`, not `invalid_measurement`. It damaged an
  artifact of the reproduction package, not a measurement.

**A-2 — host condition.** Load average `177.97 / 249.19 / 385.03` at start and
`185.90 / 244.33 / 378.56` at end, on 14 shared cores. Run as a **single
process** with all BLAS thread counts pinned to `1`
(`OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=VECLIB_MAXIMUM_THREADS=NUMEXPR_NUM_THREADS=1`).
Timings are wall-clock under that load and are not clean benchmarks. The
worktree was dirty at run time with three untracked directories, all of them
this batch's own measurement-task directories (`-3084bc`, `-c973e6`, `-e17677`);
no tracked file was modified.

**A-3 — budget.** The budget did not bind: wall clock `28.97 s` of `5400 s`
(0.5%); peak RSS `1.264 GB` of `4 GB` (32%); `1` run of `1`. Nothing was
truncated, no cell was dropped, nothing was extrapolated. The `SIGALRM`
wall-clock guard and the per-cell RSS guard were both implemented and neither
fired.

**A-4 — reproduction deviation, `2.2e-16`, located.** See §2.1. The carried
figure is `0.0`; the observed figure on the Section B path is
`2.220446049250313e-16`, confined to `d = 140`, uniform across all 28 `d = 140`
arms, and coinciding exactly with a one-ULP difference in
`betaincinv(beta/2,(d-beta)/2,2^-10)` at `d = 140` under scipy 1.15.3. Reported
rather than rounded to "identical".

**A-5 — unexpected observation — the step-selection rule and the injection
scale are coupled.** See §6.1. `SE_diff(A,t_i)` sets both which step the control
injects into and how large the injection is, and on this family it is largest at
the top of the steep descent, where `|Delta_i|` is 10–40x the injection unit.
Recorded as an observation about the frozen control, not as grounds for changing
it.

**A-6 — unexpected observation — `SE_step/SE_diff` exceeds the quoted range.**
Realized `0.2186 … 1.2072` (median `0.4729`) against the quoted `0.3599 / 0.4228`
at BATCH-f19c37's two failing steps. The §3.4 power statement was declared
conditional on that ratio and the condition is only partly met; §3.3's rate is
not conditional on it.

**O-1 — objection recorded, frozen specification run anyway (prereg §5.5).** The
positive control of §3.5 cannot demonstrate what §3.6 needs it to demonstrate at
the step its own selection rule chooses, for the arithmetic reason in §6.1. The
frozen text was implemented exactly as written, the frozen INADMISSIBLE branch
was taken, and no repair, alternative injection point, alternative `c` grid or
rescoring was computed anywhere. Any adjustment is an amendment for the
Coordinator to record as a new decision; this run does not make one and does not
propose a specific one.

**No protocol deviation.** The frozen Section B specification was implemented as
written. `prereg.md` was not modified. No early durability commit was made. This
task made no git commit and pushed no branch.

---

## 10. Reproduction

```
git checkout 974ad579443984d9369ac050dadd800caa5d10f4
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
VECLIB_MAXIMUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
python3 coordination/goals/GOAL-MLKEM-005/batches/BATCH-a44d08/tasks/\
TASK-20260806-e17677/measure_g3.py
```

Exit status 0, empty stderr, wall 28.97 s, peak RSS 1.264 GB.
Environment: Python 3.13.1, numpy 2.4.0, scipy 1.15.3, fpylll 0.6.4
(used only by reproduction check (c)), macOS arm64, 14 cores.
Sources of randomness: exactly four seed formulas and nothing else —
`seed_error(d) = 20260805 + d`, `seed_haar(d,beta,j) = 900000 + d*1000 +
beta*10 + j`, `seed_graded(d,beta,j) = 500000 + d*1000 + beta*10 + j`, and
`seed_basis(d,beta,i) = 700000 + d*1000 + beta*10 + i` (reproduction check (c)
only). The chunk size `2^15` is part of the RNG consumption order and is
carried unchanged for that reason.

## 11. Inference record (verbatim, as dispatched)

> requested_policy `executor-implementation`, degraded_allowed false,
> fallback_allowed false; resolved binding anthropic:claude-sonnet-5 per
> orchestration.adapter, but under the Claude Code runtime per CLAUDE.md
> per-role selection is process-level and subagents keep model: inherit, so the
> resolved model is the session model; fallback_used: false.

## 12. Artifacts

```
coordination/goals/GOAL-MLKEM-005/batches/BATCH-a44d08/tasks/TASK-20260806-e17677/measure_g3.py
coordination/goals/GOAL-MLKEM-005/batches/BATCH-a44d08/tasks/TASK-20260806-e17677/results_g3.json
coordination/goals/GOAL-MLKEM-005/batches/BATCH-a44d08/tasks/TASK-20260806-e17677/report_g3.md
coordination/goals/GOAL-MLKEM-005/batches/BATCH-a44d08/tasks/TASK-20260806-e17677/run_manifest.yaml
```

Artifact sha256 values are listed in `run_manifest.yaml` and are to be
re-verified by the Coordinator at snapshot time. The Executor made no commit
and no early durability commit.
