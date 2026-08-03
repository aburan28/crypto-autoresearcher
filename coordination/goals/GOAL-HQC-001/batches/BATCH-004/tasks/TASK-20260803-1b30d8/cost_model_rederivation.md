# Cost-model re-derivation from measured machine constants

**Task**: `TASK-20260803-1b30d8` (executor) · **Batch**: `BATCH-004` ·
**Goal**: `GOAL-HQC-001` · **Question**: `RQ-HQC-001`
**Produced**: 2026-08-03 · **Branch**: `claude/goal-target-hqc-launch-vndegi`
**Repo commit during both measurement invocations**:
`2087441cb296ef520b50fa69d672880d9dafafec`
(tree clean except this task's own untracked directory; the sibling task
`TASK-20260803-04377d` writes elsewhere and nothing of it was read)

**Closes**: validator `DEF-3` (`.../BATCH-003/reviews/TASK-20260802-addcdd/
validation_report.yaml`), `EV-HQC-0e9116` D-6, `DEC-20260802-d94a64` D-6 —
*"`calib_m0.py` and `calib_m0b.py` … exist nowhere in the repository … every
cost number is CONDITIONAL ON UNVERIFIABLE INPUTS."*

**Claim tier: toy.** `certificate.kind: none` (pure measurement run; nothing is
claimed to be solved or decomposed, so there is nothing to certify).
**No security claim about HQC is made here in either direction.**
**`runs_authorized: 0` honoured**: no HQC object was constructed, sampled or
decoded by this task. No ring, no fixed-weight vector, no code, no decoder, no
failure indicator exists anywhere in the shipped scripts.

## inference

```yaml
inference:
  requested_policy: executor-implementation
  resolved_model_id: claude-opus-5
  fallback_used: true
  fallback_reason: >-
    The policy aliases in orchestration/model-policies.yaml do not resolve under
    this Claude Code harness; all subagents run `model: inherit`. The resolved
    model is the session model.
  model_verified: false
  independent_session: true
  degraded_allowed: false
  degraded_requirements: []
```

---

## 0. Findings, stated before the argument

| # | finding |
|---|---|
| **F1** | **The two scripts now exist and run.** Every number in `calibration_results.json` comes from code in this directory that a reviewer can re-run in ~60 s total. `DEF-3` is closed as an artifact defect. |
| **F2** | **BATCH-003's machine constants are broadly corroborated where they are reproducible.** The `R_add` sweep, the memory-bound rate, and the *slope* of the `t_sx` limb fit all land within 9 % of BATCH-003's values (§2). This is the like-for-like answer, and it is agreement, not a correction. |
| **F3** | **Substituting my constants into BATCH-003's own §9.2 formula LOWERS every cost.** `C_trial` comes out at **0.83–0.90×** BATCH-003's per set; the mandatory total is **`4.92e4` core-s against `5.58e4`, a factor 0.88** (§4). Run count is unchanged at 8. |
| **F4** | **`R_rng = 5.1e7 word/s` is not reproducible as a single number and should not be carried as one.** Measured PCG64 throughput varies from `8.5e6` to `2.6e8` word/s across batch size for the same API, and by a further factor 34 across three defensible readings of "PCG64 uint64 generation" (§2.4). BATCH-003's value sits inside the envelope, so it is *not falsified* — it is *underdetermined*. |
| **F5** | **THE COST MODEL'S COMPOSITION IS OPTIMISTIC IN TWO MEASURABLE WAYS, and together they cost more than the declared `2×` contingency covers.** (a) A cyclic ring product needs a masked **rotate**+XOR, measured at **2.02–2.25×** the bare shift+XOR §9.1 measured. (b) The `896·n_e` transform term runs on **length-128** vectors, where measured throughput is `3.04e8` elem/s — **16×** below the `R_add` the model divides by. Carrying both raises the mandatory total to **`1.61e5` core-s, 2.88×** BATCH-003's (§4.3). |
| **F6** | **ONE VERDICT-ADJACENT FIGURE FLIPS: the declared run budget, not the feasibility of the measurement.** Under F5's composition the mandatory work needs **14 runs** of 3600 s on 4 cores against the contract's declared `maximum_runs: 12`, and stage B1 needs **6** shards against the contract's declared **3** (§4.4). Under the like-for-like reading it needs 8, exactly as BATCH-003 states. |
| **F7** | **THE INFEASIBLE VERDICT DOES NOT FLIP, AND CANNOT.** `T_req` contains no machine constant. I reproduce BATCH-003's `T_req` at every published cell to ≤ 2.4 % (§3), including `PS-R1 = 2.915e7` **exactly** and the `dup = 2` cell `1.4729e24` against `1.473e24`. The `dup = 2` cost re-derives to `2.79e20` core-s (`0.87×` BATCH-003's `3.21e20`); making it affordable would need a **`2.8e15×`** speedup in `C_trial`. No machine flips this. |
| **F8** | **The red team's `dup = 2` rung re-costs to `1.73e4` core-s like-for-like (`0.86×` its quoted `2.005e4`), but to `5.36e4` core-s under F5's composition** — i.e. from 31 % of BATCH-003's mandatory budget to 96 % of it (§4.5). Its `T_req = 8.1624e7` reproduces exactly. Whether the rung is worth buying is the Coordinator's call; this task only re-prices it. |
| **F9** | **A defect in THIS TASK'S first derivation run is recorded, not hidden** (§7). The first full invocation produced a negative `C_samp` from an OLS extrapolation. It was caught, the code was fixed to interpolate between measured points, 115 automated self-checks were added so the class of defect fails the run, and both invocations are reported. |

**The one-line summary a reader should not be able to mis-take**: *BATCH-003's
arithmetic is sound and its constants are close to mine; its **composition** is
the optimistic part, and the honest downward revision runs in the direction of
**more** cost, not less — `2.88×`, enough to breach its own declared run cap
while leaving every feasibility verdict intact.*

---

## 1. What the cost model consumes, and therefore what was measured

Read off `feasibility_analysis.md` §9.1–§9.2. The model is:

```
C_prod  = (omega + omega_r) * t_sx(n)                       [s]
C_dec   = ( N + [N if dup>1 else 0] + 896*n_e ) / R_add     [s]
C_samp  = ( 2*omega + 2*omega_r + omega_e ) / R_rng         [s]
C_trial = 2 * (C_prod + C_dec + C_samp)                     2x declared contingency
```

so exactly **three** constants are load-bearing, plus two that §9.1 reports
without consuming:

| constant | unit | consumed by | measured by |
|---|---|---|---|
| `R_add` | elements/s | `C_dec` | `calib_m0.py` |
| `R_rng` | words/s | `C_samp` | `calib_m0.py` |
| `t_sx(n)` | seconds | `C_prod` | `calib_m0b.py` |
| `R_add` memory-bound | elements/s | *(reported only)* | `calib_m0.py` |
| `R_xor64` | words/s | *(reported only)* | `calib_m0.py` |

Two constants are measured here that BATCH-003 did not measure, because the
composition consumes them whether or not the model names them (F5):

| constant | unit | why |
|---|---|---|
| `t_rotxor(n)` | seconds | a **cyclic** ring product needs a masked rotate per set bit, not a bare shift |
| `R_add` at short vectors | elements/s | the `896·n_e` term is `n_e` × 7 passes over **128**-element vectors |

**No other set was invented, and none of the five above was dropped.**

### 1.1 Scheme-independence: how HQC was kept out of the calibration

Every benchmark size in both scripts is a power of two or a round multiple of
16 limbs. The big-integer sweep runs over limb counts
`W ∈ {16,32,48,64,96,128,160,192,224,256,288,320,384,448,512,640,768,1024}`,
which **span and bracket** the five bit lengths BATCH-003 quotes
(`W = 92, 112, 180, 277, 561`) **without measuring at any of them**; an affine
model in `W` is fitted and the derivation evaluates that fit wherever it needs
to. Fit residuals are reported so the interpolation error is visible rather than
assumed away.

Consequence, stated plainly: **the calibration stays valid if `n`, `ω`, `n_e`,
`dup` or `p*` change**, which is the property BATCH-003's five-point table did
not have. `calibration_results.json` separates `calibration` (machine constants,
`hqc_quantities_used: []`) from `rederivation` (HQC parameters applied to those
constants, labelled *derived, not measured*).

---

## 2. Measured constants, with spread

Archived run: `2026-08-03T03:57:07Z` / `03:57:37Z`, 15 repetitions per
configuration (7 for the memory-bound point), 3 warmups discarded, each
repetition timing an auto-calibrated inner batch of ~30 ms. **Every
per-repetition sample is retained in the JSON**; the medians below are
recomputable from them.

Machine: `Intel(R) Xeon(R) Processor @ 2.80GHz`, 4 cores, 33 792 KB cache
reported, AVX-512 present, `Linux-6.18.5-x86_64-glibc2.39`, Python 3.11.15
(30-bit int digits), numpy 2.4.6. Load average `0.95 → 1.62` across the two
invocations — **the container was not idle and is not claimed to have been**.

### 2.1 `R_add` — int16 elementwise add, cache-resident

| N | median elem/s | min | max | cv | p10 | p90 |
|---|---|---|---|---|---|---|
| 4096 | **4.923e9** | 3.214e9 | 5.148e9 | **15.7 %** | 3.283e9 | 5.084e9 |
| 8192 | 6.622e9 | 6.222e9 | 6.719e9 | 2.0 % | 6.431e9 | 6.694e9 |
| 16384 | 7.949e9 | 7.814e9 | 8.132e9 | 1.1 % | 7.867e9 | 8.080e9 |
| 32768 | 8.928e9 | 8.034e9 | 9.081e9 | 3.0 % | 8.592e9 | 9.062e9 |
| 65536 | **1.006e10** | 9.716e9 | 1.030e10 | 1.6 % | 9.840e9 | 1.022e10 |

`np.subtract` cross-check over the same sizes: `5.11e9 … 1.025e10`, agreeing
with `np.add` to within 4 % at every size.

> **Comparison.** BATCH-003 reports the sweep as `4.3e9 … 9.8e9` and *uses*
> `R_add = 4.0e9` ("conservative end"). My sweep is `4.92e9 … 1.01e10` — the
> same shape, 2–15 % faster at each end. BATCH-003's chosen `4.0e9` is **19 %
> below my slowest measured point**, i.e. it was more conservative than its own
> sweep required. **This is corroboration.**

The `cv = 15.7 %` at `N = 4096` is the honest tell that the smallest size is
dispatch-overhead dominated and noisy; it is reported rather than smoothed, and
it is the size the conservative aggregation rule selects.

### 2.2 `R_add` at short vectors — NOT in BATCH-003's table

| N | median elem/s | cv |
|---|---|---|
| 64 | 1.544e8 | 1.9 % |
| **128** | **3.035e8** | 1.8 % |
| 256 | 6.004e8 | 0.9 % |
| 512 | 1.014e9 | 1.6 % |
| 1024 | 1.973e9 | 1.3 % |
| 2048 | 3.152e9 | 11.5 % |

Throughput at length 128 is **16×** below the conservative `R_add` and **33×**
below the peak. This is the measurement behind F5(b).

### 2.3 Memory-bound and XOR (reported, not consumed)

| primitive | measured | cv | BATCH-003 |
|---|---|---|---|
| int16 add, `N = 2^24` | **1.684e9** elem/s | 4.0 % | `1.8e9` (agrees to 6 %) |
| uint64 XOR, cache sweep | 2.259e9 (4096) → 2.998e9 (16384) → **1.122e9** (65536) | 2.1–8.7 % | `1.8e9`, inside my range |

The XOR sweep is **non-monotone**: it peaks at `N = 16384` and falls by 2.7× at
`N = 65536`, where the three-array working set (1.5 MB) leaves L2. A single
"uint64 XOR, cache-resident" number is therefore also underdetermined; BATCH-003's
`1.8e9` sits inside the range. Neither value affects any cost figure.

### 2.4 `R_rng` — and why it is not one number (F4)

| reading | 64 w | 256 w | 1024 w | 4096 w | 65536 w | 2^20 w |
|---|---|---|---|---|---|---|
| `PCG64.random_raw` | 7.74e7 | 1.73e8 | 2.52e8 | 2.94e8 | **3.01e8** | 2.08e8 |
| `Generator.integers(uint64)` | 8.54e6 | 3.11e7 | 9.42e7 | 1.89e8 | **2.64e8** | 1.83e8 |
| scalar draws, Python loop | **4.49e5** | — | — | — | — | — |

cv per cell 0.8–6.2 %. The spread across defensible readings is a factor
**670** (`4.49e5 … 3.01e8`); within one API it is a factor **31** across batch
size.

> **Comparison.** BATCH-003's `R_rng = 5.1e7 word/s` is **inside** this envelope
> and close to `Generator.integers` at a few-hundred-word batch — which is the
> regime the model evaluates. It is **not contradicted**. It is **not
> reproducible as stated**, because the phrase names no batch size and no API,
> and the original script does not exist to disambiguate it.
>
> The derivation therefore does **not** use a single `R_rng`. It interpolates
> the measured per-call time between the bracketing measured batch sizes, giving
> an *effective* `R_rng` of `2.6e7 … 4.2e7` word/s at the word counts the sets
> actually need (210–357). That is **1.2–2.0× slower** than BATCH-003's `5.1e7`.
> `C_samp` is 5.7 % (PS-A) to 16.6 % (PS-R1) of `C_trial`, so the difference
> raises `C_trial` by 1.1 % (PS-A) to 8.8 % (PS-R1) and the **mandatory total by
> 2.9 %** — the smallest of the effects catalogued here, and the only one whose
> direction is *against* BATCH-003.

### 2.5 `t_sx` and `t_rotxor` — big-integer primitives

Affine fits in limbs `W = ceil(bits/64)`, over the generic limb grid:

| fit | intercept `a` | slope `b` | R² | max abs relative residual |
|---|---|---|---|---|
| `t_sx` (shift + XOR) | `1.056e-7` s | **`2.875e-9`** s/limb | 0.9983 | 24 % |
| `t_rotxor` (masked rotate + XOR) | `3.182e-7` s | `5.608e-9` s/limb | 0.9958 | 56 % |
| BATCH-003 `t_sx` | `2.685e-7` s | **`2.646e-9`** s/limb | not reported | not reported |

**The slopes agree to 8.7 %.** The intercepts differ by 2.5×, which is a
per-operation overhead difference and matters only at small `W`. Evaluated at
BATCH-003's own five bit lengths:

| bits | BATCH-003 `t_sx` | this machine (fit) | ratio | `t_rotxor / t_sx` |
|---|---|---|---|---|
| 5888 | 5.12e-7 | 3.701e-7 | **0.723** | 2.254 |
| 7168 | 5.67e-7 | 4.276e-7 | 0.754 | 2.213 |
| 11520 | 7.47e-7 | 6.231e-7 | 0.834 | 2.131 |
| 17669 | 9.76e-7 | 9.020e-7 | 0.924 | 2.075 |
| 35851 | 1.75e-6 | 1.719e-6 | **0.982** | 2.016 |

Two observations, both reported rather than reconciled:

1. This machine is **faster on the shift+XOR primitive** than BATCH-003's table,
   by 28 % at the smallest length and 2 % at the largest. That is the single
   largest driver of F3's `0.88×`, since `C_prod` carries **64–84 %** of the
   pre-contingency per-trial cost (`C_dec` 10–20 %, `C_samp` 6–17 %).
2. The **rotate** variant costs **2.0–2.3×** the shift+XOR variant, monotonically
   decreasing in size (the fixed masking overhead amortises). BATCH-003 measured
   no rotate variant. This is F5(a).

A caution on the fit: `max abs relative residual` is 24 % (`t_sx`) and 56 %
(`t_rotxor`), both attained at the small-`W` end where the intercept dominates
and CPython's 30-bit digit packing makes the limb abstraction leaky. At the
`W = 93 … 561` range this derivation actually uses, residuals are far smaller,
but **the fit is an interpolation and is labelled as one**.

### 2.6 Between-invocation spread

This task ran the measurement layer twice (§7). Comparing the superseded
`03:53:22Z` invocation against the archived `03:57:07Z` one — different process,
different page mapping, same machine and code:

| constant | superseded run | archived run | difference |
|---|---|---|---|
| `R_add` (conservative) | 4.862e9 | 4.923e9 | 1.3 % |
| `R_add` memory-bound | 1.677e9 | 1.684e9 | 0.4 % |
| `R_xor64` | 1.111e9 | 1.122e9 | 1.0 % |
| `t_sx` slope | 2.761e-9 | 2.875e-9 | 4.1 % |
| `t_sx` intercept | 1.377e-7 | 1.056e-7 | **23 %** |
| `t_rotxor` slope | 5.52e-9 | 5.608e-9 | 1.6 % |
| `random_raw` @64 w | 8.214e7 | 7.737e7 | 5.8 % |

**Slopes and throughputs reproduce across invocations to ≤ 6 %; the fitted
intercept does not** (23 %), which is the expected behaviour of an OLS intercept
extrapolated below the measured range. Only the archived run is a deliverable;
the superseded run's numbers are quoted here as observed and its stdout is in
§7. A reviewer re-running gets an independent third sample.

---

## 3. `T_req` — machine-independent, and reproduced

`T_req = max(T_prec, T_stab)` is a function of `(n_e, q, k)` under the binomial
null only. **No calibration constant enters it.** No measurement on any machine
can move it, so every difference between this task's figures and BATCH-003's is
located entirely in `C_trial`. Re-derived here in **exact rational arithmetic**
(`fractions.Fraction`, no floating point until the final conversion) from
BATCH-003's own §3 rule:

| cell | `n_e` | `q` | `k` | `V` | `T_prec` | `s_90` | `P[S ≥ s_90]` | `T_stab` | **`T_req` here** | BATCH-003 | ratio |
|---|---|---|---|---|---|---|---|---|---|---|---|
| PS-R1 | 46 | 0.2306 | 16 | 4.944e4 | 4.116e5 | 26 | 1.029e-6 | 2.915e7 | **2.9150e7** | 2.915e7 | **1.0000** |
| PS-R3 | 56 | 0.370 | 17 | 623 | 5187 | 35 | 9.486e-5 | 3.163e5 | **3.1627e5** | 3.09e5 | 1.0235 |
| PS-R5 | 90 | 0.473 | 30 | 6442 | 5.363e4 | 63 | 1.102e-5 | 2.723e6 | **2.7232e6** | 2.72e6 | 1.0012 |
| PS-A | 46 | 5.588e-4 | 16 | 1.434e40 | 1.194e41 | 16 | 8.821e-41 | 3.401e41 | **3.4008e41** | 3.40e41 | 1.0002 |
| PS-A (obs. `q`) | 46 | 4.993e-4 | 4 | 1.070e8 | 8.908e8 | 4 | 9.973e-9 | 3.008e9 | **3.0080e9** | 3.01e9 | 0.9993 |
| **LADDER dup=2** | 46 | 8.94e-3 | 16 | 6.933e21 | 5.772e22 | 17 | 2.037e-23 | 1.473e24 | **1.4729e24** | 1.473e24 | **0.9999** |
| **PS-R2 (red team)** | 46 | 0.21932 | 16 | 7.843e4 | 6.530e5 | 26 | 3.675e-7 | 8.162e7 | **8.1624e7** | 8.164e7 | 0.9998 |

Also re-derived, no published value to compare: PS-R1 `k=2` → 626;
PS-A(obs `q`) `k=2` → 1.180e5, `k=3` → 1.614e7.

**Every published cell reproduces to ≤ 2.4 %, six of seven to ≤ 0.1 %.** The one
cell above 1 % is PS-R3, where BATCH-003 prints `3.09e5` against my `3.1627e5`;
the difference is consistent with rounding of `q = 0.370` and moves nothing.
`C2` (`T_stab`) binds at **every** cell, as BATCH-003 states.

This independently re-confirms the two structural results BATCH-003 rests on —
`T_req ≈ 1/P[S ≥ m]`, and the `dup = 1 → dup = 2` jump of `~10^17` — using code
that shares nothing with BATCH-003's (which does not exist to share).

---

## 4. Re-derived cost model

Three fully-specified variants. **All three use BATCH-003's §9.2 formula
unchanged** except where noted; the `2×` contingency is retained in all three
because it is part of the frozen model.

| variant | ring primitive | `896·n_e` term | generator | `R_add` |
|---|---|---|---|---|
| **V1 like-for-like** | shift+XOR | at `R_add` (lumped) | measured, batch-interpolated | conservative (slowest of sweep) |
| **V2 composition-aware** | **rotate+XOR** | at **short-vector rate** | measured, batch-interpolated | conservative |
| **V3 optimistic** | shift+XOR | lumped | asymptotic (fastest measured) | optimistic (fastest of sweep) |

V2's two changes are **mine and are flagged as mine**. They are not corrections
to BATCH-003's frozen model; they are a measurement of what that model's
composition assumption hides.

### 4.1 Per-trial cost

| set | BATCH-003 `C_trial` | **V1** | V1/b3 | **V2** | V2/b3 | **V3** | V3/b3 |
|---|---|---|---|---|---|---|---|
| PS-A | 3.35e-4 | **3.026e-4** | 0.90 | 8.309e-4 | 2.48 | 2.723e-4 | 0.81 |
| PS-R1 | 1.17e-4 | **9.718e-5** | 0.83 | 4.295e-4 | 3.67 | 7.287e-5 | 0.62 |
| PS-R3 | 1.47e-4 | **1.223e-4** | 0.83 | 5.327e-4 | 3.62 | 9.589e-5 | 0.65 |
| PS-R5 | 2.47e-4 | **2.121e-4** | 0.86 | 8.890e-4 | 3.60 | 1.785e-4 | 0.72 |
| LADDER dup=2 | 2.18e-4 | **1.897e-4** | 0.87 | 6.097e-4 | 2.80 | 1.617e-4 | 0.74 |
| PS-R2 (red team) | 2.456e-4 | **2.116e-4** | 0.86 | 6.561e-4 | 2.67 | 1.837e-4 | 0.75 |

Trials/s/core: BATCH-003 `2990 / 8540 / 6790 / 4050` (PS-A/R1/R3/R5);
V1 `3304 / 10290 / 8174 / 4715`; V2 `1204 / 2328 / 1877 / 1125`.

### 4.2 Components, V1 against BATCH-003

| set | `C_prod` V1 (b3) | `C_dec` V1 (b3) | `C_samp` V1 (b3) | effective `R_rng` |
|---|---|---|---|---|
| PS-A | 1.272e-4 (1.376e-4) | 1.555e-5 (1.91e-5) | 8.59e-6 (7.0e-6) | 4.16e7 |
| PS-R1 | 3.096e-5 (4.25e-5) | 9.568e-6 (1.18e-5) | 8.066e-6 (3.3e-6) | 2.60e7 |
| PS-R3 | 4.133e-5 (5.50e-5) | 1.165e-5 (1.44e-5) | 8.195e-6 (3.8e-6) | 2.97e7 |
| PS-R5 | 7.888e-5 (9.20e-5) | 1.872e-5 (2.30e-5) | 8.461e-6 (4.9e-6) | 3.77e7 |

`C_prod` and `C_dec` come out **lower** (faster machine on both primitives);
`C_samp` comes out **higher** (BATCH-003's `R_rng` is optimistic at the relevant
batch size). `C_prod` dominates, so the net is lower.

### 4.3 Stage budget

| stage | trials | BATCH-003 | **V1** | V1/b3 | **V2** | V2/b3 | **V3** |
|---|---|---|---|---|---|---|---|
| A calibration | 4 × 2e6 | 1.69e3 | 1.469e3 | 0.87 | 5.364e3 | 3.17 | 1.239e3 |
| B1 PS-A | 1.0e8 | 3.35e4 | 3.026e4 | 0.90 | 8.309e4 | 2.48 | 2.723e4 |
| B2 PS-R1 | 1.0e8 | 1.17e4 | 9.718e3 | 0.83 | 4.295e4 | 3.67 | 7.287e3 |
| B3 PS-R3 | 2.0e7 | 2.94e3 | 2.447e3 | 0.83 | 1.065e4 | 3.62 | 1.918e3 |
| B4 PS-R5 | 2.0e7 | 4.94e3 | 4.242e3 | 0.86 | 1.778e4 | 3.60 | 3.570e3 |
| C nulls | — | 1.01e3 | *1.01e3 carried* | — | *1.01e3 carried* | — | *1.01e3 carried* |
| **TOTAL mandatory** | | **5.58e4** | **4.915e4** | **0.881** | **1.608e5** | **2.883** | **4.225e4** |
| + D optional | 2 × 1e7 | 6.25e4 | 5.589e4 | — | 1.676e5 | — | 4.899e4 |

**Stage C is carried verbatim and is NOT re-derivable.** `feasibility_analysis.md`
§9.3 states no trial counts for the null arms, so its `1.01e3` core-s cannot be
reproduced from any set of machine constants. Carrying it unchanged makes every
total above **slightly optimistic** if the true constants are slower — it is
2.1 % of the V1 total and 0.6 % of the V2 total. Stage D is carried on the same
footing.

### 4.4 Run count — where a figure actually flips (F6)

At 4 cores under the contract's 3600 s per-run cap:

| variant | total wall @4c | runs required | BATCH-003 states | declared `maximum_runs` | breach |
|---|---|---|---|---|---|
| V1 | 12 288 s | **8** | 8 | 12 | no |
| V2 | 40 212 s | **14** | 8 | 12 | **YES** |
| V3 | 10 563 s | 7 | 8 | 12 | no |

Under V2, stage B1 alone needs **6** shards where the contract declares 3, and
B2 needs 3 where the contract declares 1. The two spare runs BATCH-003 reserves
"for infrastructure re-runs" would be consumed by composition overhead and then
exceeded by two. **This is the one figure in the package that changes category
rather than magnitude**, and it is a budget/contract fact, not a mathematical
one.

### 4.5 The `dup` ladder and the red team's rung

| cell | `T_req` (re-derived) | BATCH-003 cost | **V1** | **V2** | **V3** |
|---|---|---|---|---|---|
| `dup = 1` (PS-R1) at `T_req` | 2.9150e7 | 3.4e3 core-s | **2.83e3** | 1.25e4 | 2.12e3 |
| `dup = 2` (HQC-1 shape) at `T_req` | 1.4729e24 | 3.2e20 core-s | **2.79e20** | 8.98e20 | 2.38e20 |
| **PS-R2** (red team) at `T_req` | 8.1624e7 | 2.005e4 core-s | **1.73e4** | 5.36e4 | 1.50e4 |

The `dup = 1 → dup = 2` gap re-derives as **`9.9e16`** (V1), against BATCH-003's
stated `~10^17`. The gap is a property of `T_req`, not of the machine: `C_trial`
differs between the two rungs by only a factor 1.95.

On **PS-R2**: like-for-like it is *cheaper* than the red team quoted
(`1.73e4` vs `2.005e4`, because this machine's ring primitive is faster).
Under the composition-aware reading it is `5.36e4` core-s — **96 % of
BATCH-003's entire mandatory budget** rather than the 36 % the red team quoted
against its own numbers. Both figures are reported. **Whether the rung is worth
buying is a Coordinator decision and is not made here**; the sibling task
`TASK-20260803-04377d` evaluates the rung on its merits and this task did not
read, depend on, or coordinate with it.

### 4.6 Internal inconsistencies found in BATCH-003's own arithmetic

Reported because a reviewer re-deriving from the document will hit them. All are
sub-3 % and **none changes any verdict**; they are bookkeeping observations.

1. **`C_samp` applies two different formulas.** §9.2 states
   `(2ω + 2ω_r + ω_e)/R_rng`. PS-A's printed `7.0e-6` matches that
   (`357/5.1e7`). PS-R1/R3/R5's printed `3.3e-6 / 3.8e-6 / 4.9e-6` match
   `(2ω + 2ω_r)/R_rng` with **`ω_e` omitted** (`166/192/252` over `5.1e7`).
   Effect on `C_trial`: ≤ 2 %.
2. **`C_prod`'s evaluation point alternates between `n` and `N`.** §9.2 states
   `t_sx(n)`. PS-A's `1.376e-4 = 141 × 9.76e-7` uses the table value at
   `n = 17669`. PS-R1's `4.25e-5 = 83 × 5.12e-7` uses the table value at
   `5888 = N`, not at `n = 5923`. Effect: ≤ 1 %.
3. **Printed `C_trial` exceeds `2 ×` the printed components** by 0.4 % (PS-R3),
   1.6 % (PS-R1), 2.3 % (PS-A), 3.0 % (PS-R5) — consistent with rounding of the
   printed components, and well inside the spread of any constant in §2.
4. The **stage layer is exact**: every stage total is `trials × printed C_trial`
   to the printed precision, confirming the validator's finding that "the cost
   MODEL composes those constants correctly … the defect is in the inputs".

---

## 5. What these constants do NOT cover

Named because a microbenchmark on this container is not a prediction for another
machine, and because the next reviewer should attack the carrying assumptions
rather than the timings.

### 5.1 Assumptions carrying a measured primitive to a modeled total

| # | assumption | status | direction |
|---|---|---|---|
| **A1** | The declared `2×` implementation contingency covers everything unmeasured in the composition. | **VIOLATED by measurement.** V2/V1 is `2.5–3.7×` from **two** composition effects alone, before any other unmeasured cost. | **OPTIMISTIC** |
| **A2** | Perfect 4-core scaling. | **Unmeasured.** Every benchmark here is single-core. Four workers share one 33 MB L3; the memory-bound rate is already `6×` below the cache-resident peak (§2.3), so per-core cache-resident throughput at 4× concurrency is *not* what §2.1 measured. | **OPTIMISTIC** |
| **A3** | The `896·n_e` transform term runs at large-array `R_add`. | **VIOLATED by measurement**: `3.04e8` vs `4.92e9` elem/s at length 128 (§2.2). Largest single term in V2. | **OPTIMISTIC** |
| **A4** | A bare shift+XOR prices a cyclic ring-product step. | **VIOLATED by measurement**: the masked rotate costs `2.02–2.25×` (§2.5). | **OPTIMISTIC** |
| **A5** | `R_rng = 5.1e7` at the operating batch size. | Measured effective rate `2.6e7–4.2e7` (§2.4). | **OPTIMISTIC** (mildly; `C_samp` ≤ 8 % of `C_trial`) |
| **A6** | Stage C (and D) cost what BATCH-003 says. | **Not re-derivable at all** — no trial counts are stated. Carried verbatim. | **OPTIMISTIC** (understates if constants are slower) |
| **A7** | Python big integers are the ring representation. | Neither BATCH-003 nor this task measured a bit-sliced or numpy-packed ring product, which could be far faster. | **PESSIMISTIC** — stated so the flagging is not one-sided |
| **A8** | The machine is otherwise idle. | **False.** Load average `0.95 → 1.62` on 4 cores during measurement; `cv` up to 15.7 % at the smallest size. Medians, not minima, are used. | **PESSIMISTIC** (medians absorb contention) |
| **A9** | The limb-linear fit interpolates correctly at `W = 93 … 561`. | R² `0.998`/`0.996`; max relative residual 24 %/56 % **at the small-`W` end**, outside the range used. | mild, both directions |
| **A10** | `q`, `p*`, `γ` and the parameter sets are as BATCH-003 states. | **Assumed, not checked here.** They are HQC quantities; this task measured none of them and validates none of them. `T_req` inherits them. | not assessed |

### 5.2 Out of scope entirely

- **No composed pipeline was run.** Component throughputs only. This is the same
  limitation BATCH-003 declares, and it is not removed — it is *quantified* for
  two of its components.
- **No HQC object was constructed, sampled or decoded.** `runs_authorized: 0`.
- **No memory measurement.** BATCH-003's `< 1 GB` peak RSS and `2 GB` cap are
  **not verified by this task**; nothing was run whose RSS would be informative.
- **Not portable.** These numbers bind to this CPU (AVX-512, 2.80 GHz, 33 MB
  cache), this CPython (30-bit digits — a build with different digit packing
  moves `t_sx` directly), and numpy 2.4.6. A machine without AVX-512 would move
  `R_add`; a faster single-thread machine would move `t_sx`.
- **No claim about HQC's security, DFR, or the correctness of its published
  model**, in either direction.
- **Not admissible toward the AGENTS.md rule 13 closure quorum**: independent
  session, same resolved backend as BATCH-003's producer and both reviewers.

---

## 6. Reproduction

```sh
cd coordination/goals/GOAL-HQC-001/batches/BATCH-004/tasks/TASK-20260803-1b30d8
PYTHONDONTWRITEBYTECODE=1 python3 calib_m0.py  --out calibration_results.json
PYTHONDONTWRITEBYTECODE=1 python3 calib_m0b.py --out calibration_results.json
```

`calib_m0b.py` exits non-zero if any of its 115 self-checks fail. `--smoke` runs
either script in ~1 s for a functional check (not a measurement; the JSON records
`smoke: true`). `--no-rederive` measures without deriving. Defaults:
`--seed 20260803 --reps 15 --warmup 3 --target-ms 30`.

Total runtime of the archived run: **59.9 s** (30.0 + 29.9), single-core, peak
working set ~96 MB (the `2^24`-element memory-bound point), well inside the
task's 3600 s / 2 GB budget.

Artifact hashes at the time of writing:

| file | sha256 |
|---|---|
| `calib_m0.py` | `1cce587cfcb50ef1a4677d769d4fa24a15fe8f334ad46928cdc5e37eb4635b12` |
| `calib_m0b.py` | `35ca82448a414e6198ba62cfac747126a82a9e22e85910974d888862ccc22287` |
| `calibration_results.json` | `8e9590ac8f18da15021f9e908b06e7ddf176ab911875f9e564a14789873c6f47` |

Timings will not reproduce exactly and are not claimed to. What reproduces: the
procedure, the seeded operands, the sizes, the statistics, the entire
`rederivation` block given the same `calibration` block, and — exactly — the
`T_req` table of §3, which is deterministic rational arithmetic.

**Determinism verified, not asserted.** `build_rederivation()` was re-invoked
against the archived `calibration` block alone and its output compared field by
field with the archived `rederivation` block: **byte-identical after JSON
normalisation**, and identical across repeated invocations. So a reviewer who
distrusts the derivation can re-run it against the archived measurements without
re-measuring, and a reviewer who distrusts the measurements can re-measure and
watch the derivation move. Independently, a scan of both `calibration` blocks for
any integer equal to an HQC parameter (`n`, `N`, `n_e`, `n_2`, `ω`, `ω_r`, `ω_e`
across every set and ladder rung) returns only `384`, appearing as a limb count
in the generic grid and as a `working_set_bytes` figure — coincidences of round
numbers, not leaks.

---

## 7. Deviations, and every invocation run

Recorded under AGENTS.md rule 8 and the Executor's obligation to record every
attempt rather than only the successful one.

| # | invocation | disposition |
|---|---|---|
| 1 | `calib_m0.py --smoke`, ×3 during development (scratchpad output) | functional checks, not measurements; `smoke: true`, not archived |
| 2 | `calib_m0b.py --smoke`, ×2 during development (scratchpad output) | same |
| 3 | **`calib_m0.py` + `calib_m0b.py`, full, `2026-08-03T03:53:22Z`** | **INVALID DERIVATION — superseded.** Measurement layer sound; derivation defective. |
| 4 | **`calib_m0.py` + `calib_m0b.py`, full, `2026-08-03T03:57:07Z`** | **ARCHIVED.** 115/115 self-checks pass. |

**The defect in invocation 3, in full.** The generator's per-call time was
modeled by an OLS line `t(w) = c0 + c1·w` fitted across batch sizes spanning
`64 … 2^20` words. That fit is dominated by its largest points and returned
`c0 = -1.529e-5 s`. Evaluated at the 210–357-word batches the model needs, it
gave **negative `C_samp`** (`-1.415e-5 s` at PS-R1). The symptom in the totals
was that `V3_optimistic` — optimistic in every constant by construction — came
out **more expensive** than `V1_like_for_like` (`4.343e4` vs `3.880e4` core-s),
which is impossible.

Verbatim stdout of the superseded derivation:

```
[m0b] V1_like_for_like         total = 3.88e+04 core-s (0.70x BATCH-003's 5.58e4), runs=7 (declared max 12)
[m0b] V2_composition_aware     total = 1.534e+05 core-s (2.75x BATCH-003's 5.58e4), runs=14 (declared max 12)
[m0b] V3_optimistic            total = 4.343e+04 core-s (0.78x BATCH-003's 5.58e4), runs=7 (declared max 12)
```

**Remedy applied**: `interp_piecewise()` replaced the fit with piecewise-linear
interpolation between **measured** points, which cannot go negative and does not
extrapolate below the measured range; the OLS fit is retained in the JSON as a
diagnostic with `USED_FOR_EVALUATION: false` and its negative intercept on
display. A `self_checks` block of **115** assertions was added — strict positivity
of every cost component, the ordering `V3 ≤ V1 ≤ V2` at every parameter set, and
agreement of every re-derived `T_req` with BATCH-003 to 5 % — and `calib_m0b.py`
now **exits 3** if any fails.

**No conclusion in §0–§5 rests on invocation 3.** Its measurement layer is quoted
only in §2.6, as an independent second sample of the same constants, and it
agrees with the archived run to ≤ 6 % on every throughput and slope.

Verbatim stdout of the archived invocation 4:

```
[m0] R_add            = 4.923e+09 elem/s (sweep 4.92e+09 .. 1.01e+10)
[m0] R_add_membound   = 1.684e+09 elem/s
[m0] R_xor64          = 1.122e+09 word/s
[m0] R_rng raw bulk   = 7.737e+07 word/s
[m0] R_rng integers   = 8.54e+06 word/s
[m0] R_rng scalar     = 4.488e+05 word/s
[m0b] t_sx     fit: a=1.056e-07 s, b=2.875e-09 s/limb, R2=0.99828, max|rel resid|=0.239
[m0b] t_rotxor fit: a=3.182e-07 s, b=5.608e-09 s/limb, R2=0.99580, max|rel resid|=0.558
[m0b] V1_like_for_like         total = 4.915e+04 core-s (0.88x BATCH-003's 5.58e4), runs=8 (declared max 12)
[m0b] V2_composition_aware     total = 1.608e+05 core-s (2.88x BATCH-003's 5.58e4), runs=14 (declared max 12)
[m0b] V3_optimistic            total = 4.225e+04 core-s (0.76x BATCH-003's 5.58e4), runs=7 (declared max 12)
[m0b] self-checks: 115 run, all_passed=True
```

**Other protocol notes.**

- The task's `maximum_runs: 1` was interpreted as one archived measurement run;
  invocation 3 was a second full invocation and is declared as such above rather
  than omitted. Development smoke runs wrote only to scratchpad.
- Write scope honoured: exactly the four declared files exist in this directory.
  Nothing was written to `experiments/`, `ledger/`, or `knowledge/`. No
  `__pycache__` was created (`PYTHONDONTWRITEBYTECODE=1`; no cross-script
  import). No state-mutating git command was run.
- The sibling task `TASK-20260803-04377d` was not read and is not depended on.
  §4.5 re-prices the `dup = 2` rung purely as arithmetic and takes no position on
  whether it belongs in the protocol.

---

## 8. What this task does NOT decide

- It does **not** say the measurement should or should not be run, at any set.
- It does **not** say BATCH-003's cost model is wrong. Its arithmetic composes
  correctly and its constants are corroborated; what is quantified here is the
  size of two composition assumptions it declared but did not measure.
- It does **not** revise the frozen `2×` contingency, the parameter sets, the
  stopping rules, or `maximum_runs`. F6 reports that 14 > 12; **amending the
  contract is a Coordinator act** and this task requests, but does not make, that
  judgement.
- It does **not** conclude anything about `A17`, `HEUR-HQC-*`, the `dup = 2`
  rung's merit, or HQC's security.
- It does **not** validate `q`, `p*`, `γ`, or any published HQC quantity.
