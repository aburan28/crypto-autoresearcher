# EXP-YIELD-002 conditional CR-3 chance-alarm budget, re-derived independently

Task `TASK-20260729-029`. Report id `RT-20260729-029`.
Archived by `TASK-20260729-030`. **Not committed by this session.**

## 0. What this document is, and what it is not

**IT IS A PRE-REGISTERED CONTRACT QUANTITY.** `AMD-EXP-YIELD-002-V3` change `C-15`
binds the rule
`p_i(c) = Q(c sqrt(2) - delta_i) + Q(c sqrt(2) + delta_i)` with
`delta_i = (bias_i - r_i)/sem_001,i`, states that every term on the right is a
committed constant or exact arithmetic on one, and makes the numerical evaluation
a **dispatch gate** on `TASK-20260729-018`. This document is that evaluation. Its
value was fixed at the moment `C-15` was committed at `0548d8cc`; this session
evaluated it, it did not choose it.

**IT IS NOT A MEASUREMENT AND IT IS NOT EVIDENCE.** No run of `EXP-YIELD-002`
exists. Nothing here is an observation about `P_pred`, about the occupancy null,
about `CTRL-NULL-SUMSET`, about decomposition yield, about any curve, or about
any cryptanalytic quantity, in either direction. It is arithmetic on constants
already committed in `RUN-YIELD-001-NULL-RANDOM-SUMSET/results.json` at
`2fb2bb7a111d999859612e52990eea7dc6bbac1a` (`IN-1`).

**IT IS NOT AN APPROVAL.** It carries no determination on `EXP-YIELD-002`.

## 1. Provenance of every input

All 48 declared tuples were rebuilt from `IN-1` in this session by:

- reading the 49 committed cells;
- de-duplicating on `(k, m, B)` per `RC-C`, which merges exactly one pair —
  `(k=12, m=3, B=22)` at `beta=0.325` and `beta=0.350` — leaving 48. The retained
  member is the `beta=0.325` cell, confirmed by matching
  `mu_001 = 1438.82` and `s_001 = 20.207699302768514` against row
  `T-12-3-B22` of the committed criterion feasibility table. **The two merged
  cells are NOT identical measurements** (`beta=0.350` has `mu_001 = 1439.23`,
  `s_001 = 18.440105063352398`), so the choice of retained member is load-bearing
  and is recorded here rather than assumed;
- taking `mu_001 = antipodal.mean`, `s_001 = antipodal.sd`,
  `n_rep = replicates`, `N`, `C_red`, `P_pred`, and
  `s = |S_(m-2)| = P_pred_decomposition.S_m_minus_2_used` verbatim;
- `sem_001 = s_001/sqrt(n_rep)`, `lambda = C_red/N`, `T = s exp(-lambda)`.

**Replicate schedule confirmed independently: 37 tuples at 100 replicates, 11 at
30, none at 10.** This matches the `C-14` schedule and discharges the input to
`OI-10`.

`r_i` was computed as `mu_001,i - (P_pred,i - T_i)` and checked against `IN-1`'s
own recorded `residual_after_adding_back_S_m_minus_2_term`:
**maximum absolute difference over the 48 tuples = 0.0.**

`bias_i = m_rep,i - P_pred,i` uses the **exact** process mean of `P-REPAIRED`
from the frozen specification's `effect_size_arithmetic_OB_10`,

```
m_rep = N - (1 - s/N)[(N-1) A + C],   A = (1 - 2/N)^(C_red/2),  C = (1 - 1/N)^(C_red/2)
```

evaluated in log space. **No `f(lambda)` or `g(lambda)` approximation is used
anywhere in this note.** As a check, `bias_i/sem_001,i` reproduces the feasibility
table's section 5.2 figures to within rounding (`0.07519` at `T-12-2-B46`).

Cross-check of the whole pipeline against an independent quantity: the **literal**
`NB-1` reading gives a CR-3 counterfactual firing set of **19** tuples, the extra
member being `T-18-2-B58` at **3.4578738**, against `RT-20260729-025`'s reported
`3.4579`. Independent agreement to five decimals on a quantity computed by a
different route.

## 2. The variance model, restated in the form actually used

Under the hypothesis the contract calls *a perfectly correct repaired null*:

- `mu_001,i`, `s_001,i`, `sem_001,i`, `T_i`, `P_pred,i`, `N_i`, `C_red,i` are
  **committed constants**. They are not redrawn.
- The only random quantities in `CR-3` are the repaired arm's realised mean
  `mu_rep,i` and realised sample sd `s_rep,i`.
- `E[(mu_rep,i - mu_001,i) - T_i] = m_rep,i - mu_001,i - T_i = bias_i - r_i`,
  **exactly**, with no approximation. Define `delta_i = (bias_i - r_i)/sem_001,i`.

Writing `sigma_i` for the repaired arm's **true** standard error and
`u ~ chi2_{n-1}/(n-1)` for the scaled sample variance, the statistic is exactly

```
z_shift,i = |delta_i + rho_i z| / sqrt(1 + rho_i^2 u),    z ~ N(0,1) independent of u,
rho_i = sigma_i / sem_001,i.
```

**Model VM-1 as the amendment states it** sets `rho_i = 1` (**A1**) and replaces
`u` by its central value `1` (**A2**), giving
`z_shift ~ |N(delta_i, 1)|/sqrt(2)` and
`p_i(c) = Q(c sqrt(2) - delta_i) + Q(c sqrt(2) + delta_i)`.

**This note reports both**: the `A2` column, because `C-15` binds that rule; and
an **exact-A1** column with `A2` removed by integrating over `u`, because `A2` is
known to err in one direction and removing it costs nothing.

## 3. THE SCALE QUESTION, SETTLED FIRST (`OI-7`)

**The threshold on the underlying normal scale is `3.000 * sqrt(2) = 4.242641`,
not `3.000`.** Derivation, independent of both prior sessions: conditional on the
committed draw the numerator's standard deviation is `sigma_i` (only `mu_rep` is
random) while the denominator is `sqrt(sem_rep^2 + sem_001^2)`, which under `A1`
and `A2` equals `sqrt(2) sem_001`. Hence `Var(z_shift) = 1/2`, not `1`, and
`z_shift >= 3.000` is `|N(delta_i,1)| >= 3.000 sqrt(2)`. **Confirmed.**

**A separate matter, and the reason the two prior figure sets differ.** The
`TASK-20260729-028` receipt's model line reads
`delta_i = residual_after_adding_back_i / sem_001_i`, i.e. it sets `bias_i = 0`.
Recomputing under exactly that definition reproduces the receipt's figures to
five significant figures:

| quantity | this session with `bias_i = 0` | `-028` receipt |
|---|---|---|
| `E[CR-3 exceedances]` at 3.000 | 0.2329118 | 0.23291 |
| `p` at `T-18-2-B264` | 0.0942400 | 0.0942 |
| `p` at `T-14-2-B118` | 0.0583620 | 0.0584 |

**So the `-028` figures differ from `RT-20260729-025`'s not because of the scale —
both used the correct `sqrt(2)` scale — but because the `-028` session dropped the
exact process bias from `delta_i`.** The amendment's conjecture that the scale
explains the *earlier* `-026` discrepancy is not contradicted by anything here and
is not confirmed either; the `-026` computation is not recorded in enough detail
to reconstruct. **Including `bias_i` is correct**, because `E[mu_rep] = P_pred +
bias`, not `P_pred`. The figures in section 4 include it.

## 4. THE 48-TUPLE TABLE (`OI-1`, `OI-2`)

Ranked by `p_i(3.000)` under exact-A1. `df = n_rep - 1`.

| rank | tuple | n_rep | df | T | r_i | bias_i | sem_001 | delta_i | p_i(3.000) A2 | p_i(3.000) exact-A1 | p_i(4.000) exact-A1 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `T-18-2-B264` | 30 | 29 | 0.8753281 | -27.121262 | 0.056294 | 9.264144 | +2.93363 | 0.095265 | 0.104949 | 5.285e-03 |
| 2 | `T-14-2-B118` | 100 | 99 | 0.6577581 | +9.621193 | 0.122282 | 3.598098 | -2.63998 | 0.054505 | 0.056783 | 1.557e-03 |
| 3 | `T-16-3-B22` | 100 | 99 | 21.4107146 | +1.534056 | 0.013118 | 0.701847 | -2.16705 | 0.018966 | 0.020172 | 3.124e-04 |
| 4 | `T-18-2-B140` | 100 | 99 | 0.9632460 | -3.271398 | 0.017865 | 1.672625 | +1.96653 | 0.011420 | 0.012270 | 1.487e-04 |
| 5 | `T-16-2-B246` | 30 | 29 | 0.6306413 | -29.821402 | 0.127249 | 16.161196 | +1.85312 | 0.008435 | 0.010749 | 1.695e-04 |
| 6 | `T-14-3-B34` | 100 | 99 | 22.9085741 | -6.413732 | 0.118745 | 3.422283 | +1.90881 | 0.009802 | 0.010564 | 1.193e-04 |
| 7 | `T-16-2-B88` | 100 | 99 | 0.9427118 | +2.600500 | 0.027393 | 1.436958 | -1.79066 | 0.007104 | 0.007706 | 7.525e-05 |
| 8 | `T-18-2-B58` | 100 | 99 | 0.9935936 | +0.573575 | 0.003188 | 0.320473 | -1.77983 | 0.006893 | 0.007481 | 7.209e-05 |
| 9 | `T-16-2-B192` | 30 | 29 | 0.7551534 | -13.915154 | 0.098231 | 9.218217 | +1.52018 | 0.003240 | 0.004376 | 4.796e-05 |
| 10 | `T-18-2-B390` | 30 | 29 | 0.7478206 | -26.877266 | 0.100365 | 19.117644 | +1.41114 | 0.002316 | 0.003193 | 3.106e-05 |
| 11 | `T-14-3-B26` | 100 | 99 | 21.7869449 | -2.712432 | 0.070591 | 1.973876 | +1.40993 | 0.002308 | 0.002561 | 1.562e-05 |
| 12 | `T-16-3-B58` | 30 | 29 | 35.3283693 | +17.371138 | 0.130512 | 14.184607 | -1.21545 | 0.001234 | 0.001767 | 1.387e-05 |
| 13 | `T-14-2-B34` | 100 | 99 | 0.9658184 | +0.595747 | 0.016649 | 0.454655 | -1.27371 | 0.001494 | 0.001673 | 8.617e-06 |
| 14 | `T-16-2-B72` | 100 | 99 | 0.9612773 | +1.154892 | 0.018793 | 0.990105 | -1.14745 | 0.000983 | 0.001111 | 4.889e-06 |
| 15 | `T-18-3-B28` | 100 | 99 | 27.6102985 | -0.794924 | 0.006885 | 0.724573 | +1.10660 | 0.000856 | 0.000970 | 4.057e-06 |
| 16 | `T-18-3-B82` | 30 | 29 | 57.7128077 | -30.125536 | 0.112051 | 31.729912 | +0.95297 | 0.000502 | 0.000759 | 4.460e-06 |
| 17 | `T-12-2-B54` | 100 | 99 | 0.6946071 | +1.763061 | 0.114297 | 1.646638 | -1.00129 | 0.000595 | 0.000679 | 2.490e-06 |
| 18 | `T-16-3-B48` | 30 | 29 | 36.2385292 | -11.429470 | 0.098215 | 13.135574 | +0.87759 | 0.000383 | 0.000589 | 3.184e-06 |
| 19 | `T-16-3-B16` | 100 | 99 | 15.8331555 | +0.253424 | 0.005172 | 0.264086 | -0.94004 | 0.000479 | 0.000549 | 1.866e-06 |
| 20 | `T-16-2-B48` | 100 | 99 | 0.9826010 | +0.441144 | 0.008585 | 0.462294 | -0.93568 | 0.000472 | 0.000541 | 1.828e-06 |
| 21 | `T-18-3-B44` | 30 | 29 | 41.6742999 | -2.966764 | 0.025361 | 4.108999 | +0.72819 | 0.000221 | 0.000351 | 1.609e-06 |
| 22 | `T-14-2-B56` | 100 | 99 | 0.9099644 | +0.947767 | 0.041899 | 1.113133 | -0.81380 | 0.000303 | 0.000351 | 1.018e-06 |
| 23 | `T-18-2-B82` | 100 | 99 | 0.9872357 | -0.497331 | 0.006321 | 0.636436 | +0.79136 | 0.000279 | 0.000324 | 9.128e-07 |
| 24 | `T-12-2-B62` | 100 | 99 | 0.6185484 | -1.338022 | 0.129206 | 1.876940 | +0.78171 | 0.000269 | 0.000312 | 8.708e-07 |
| 25 | `T-14-2-B72` | 100 | 99 | 0.8555882 | +1.380728 | 0.064051 | 1.996589 | -0.65946 | 0.000170 | 0.000199 | 4.759e-07 |
| 26 | `T-14-2-B44` | 100 | 99 | 0.9434173 | -0.428124 | 0.027072 | 0.697858 | +0.65228 | 0.000166 | 0.000194 | 4.592e-07 |
| 27 | `T-12-3-B20` | 100 | 99 | 14.3079597 | -0.872668 | 0.108666 | 1.582249 | +0.62021 | 0.000147 | 0.000172 | 3.910e-07 |
| 28 | `T-18-3-B34` | 100 | 99 | 33.1580885 | +0.743979 | 0.012148 | 1.374054 | -0.53261 | 0.000105 | 0.000124 | 2.509e-07 |
| 29 | `T-18-3-B58` | 30 | 29 | 51.2191318 | +4.536647 | 0.053143 | 10.340896 | -0.43357 | 0.000071 | 0.000122 | 3.983e-07 |
| 30 | `T-12-3-B16` | 100 | 99 | 13.4722459 | +0.553495 | 0.068934 | 1.059195 | -0.45748 | 0.000078 | 0.000093 | 1.709e-07 |
| 31 | `T-18-2-B110` | 100 | 99 | 0.9771477 | -0.545467 | 0.011229 | 1.241929 | +0.44825 | 0.000075 | 0.000090 | 1.630e-07 |
| 32 | `T-14-3-B20` | 100 | 99 | 18.4506882 | +0.489351 | 0.036391 | 1.021080 | -0.44361 | 0.000074 | 0.000088 | 1.592e-07 |
| 33 | `T-16-2-B58` | 100 | 99 | 0.9746982 | +0.269665 | 0.012409 | 0.605447 | -0.42490 | 0.000069 | 0.000082 | 1.446e-07 |
| 34 | `T-12-2-B42` | 100 | 99 | 0.8021618 | +0.579545 | 0.083361 | 1.196852 | -0.41457 | 0.000066 | 0.000079 | 1.371e-07 |
| 35 | `T-12-2-B46` | 100 | 99 | 0.7676404 | -0.420781 | 0.094481 | 1.256528 | +0.41007 | 0.000065 | 0.000078 | 1.340e-07 |
| 36 | `T-18-2-B34` | 100 | 99 | 0.9977939 | -0.042191 | 0.001101 | 0.110901 | +0.39037 | 0.000060 | 0.000072 | 1.212e-07 |
| 37 | `T-16-2-B144` | 30 | 29 | 0.8538760 | -1.657580 | 0.064708 | 6.299854 | +0.27339 | 0.000039 | 0.000070 | 1.876e-07 |
| 38 | `T-18-2-B44` | 100 | 99 | 0.9963080 | +0.068011 | 0.001841 | 0.172960 | -0.38257 | 0.000059 | 0.000070 | 1.164e-07 |
| 39 | `T-18-3-B16` | 100 | 99 | 15.9579929 | +0.043548 | 0.001310 | 0.127936 | -0.33015 | 0.000048 | 0.000058 | 8.919e-08 |
| 40 | `T-14-2-B86` | 100 | 99 | 0.8005019 | +0.750759 | 0.083919 | 2.032280 | -0.32812 | 0.000048 | 0.000058 | 8.828e-08 |
| 41 | `T-12-3-B22` | 100 | 99 | 14.0926559 | +0.761640 | 0.124861 | 2.020770 | -0.31512 | 0.000045 | 0.000055 | 8.270e-08 |
| 42 | `T-16-2-B116` | 100 | 99 | 0.9025697 | -0.625637 | 0.045055 | 2.381197 | +0.28166 | 0.000040 | 0.000049 | 7.005e-08 |
| 43 | `T-18-2-B192` | 30 | 29 | 0.9319931 | +0.708344 | 0.032235 | 6.726274 | -0.10052 | 0.000024 | 0.000046 | 9.857e-08 |
| 44 | `T-12-2-B36` | 100 | 99 | 0.8504756 | +0.193034 | 0.066007 | 0.895930 | -0.14178 | 0.000026 | 0.000032 | 3.788e-08 |
| 45 | `T-16-3-B30` | 100 | 99 | 28.0077694 | -0.135784 | 0.031505 | 1.682591 | +0.09942 | 0.000024 | 0.000030 | 3.309e-08 |
| 46 | `T-18-3-B24` | 100 | 99 | 23.7889104 | +0.032452 | 0.004368 | 0.413259 | -0.06796 | 0.000023 | 0.000029 | 3.070e-08 |
| 47 | `T-16-3-B38` | 100 | 99 | 33.0510288 | +0.255024 | 0.058481 | 3.474959 | -0.05656 | 0.000023 | 0.000028 | 3.007e-08 |
| 48 | `T-16-2-B38` | 100 | 99 | 0.9890597 | +0.016682 | 0.005425 | 0.293299 | -0.03838 | 0.000022 | 0.000028 | 2.930e-08 |

## 5. HEADLINE CONDITIONAL FIGURES

| quantity | VM-1 as bound by `C-15` (A1+A2) | exact-A1 (`A2` removed) | `RT-20260729-025` | `-028` receipt |
|---|---|---|---|---|
| `E[CR-3 exceedances]` at 3.000 | **0.229893** | **0.252724** | 0.22989 | 0.23291 |
| `P(at least one CR-3 chance alarm)` | **0.210755** | **0.229568** | 0.2108 | 0.2132 |
| `P(CR-3 fails at 2 or more tuples)` | **0.018289** | **0.022007** | 0.0183 | not stated |
| `E[CR-3 exceedances]` at 4.000 | **0.005198** | **0.007888** | 0.0052 | 0.00529 |
| `P(any CR-3 tuple at or above 4.000)` | **0.005190** | **0.007872** | not stated | not stated |
| `p` at `T-18-2-B264` (rank 1) | **0.095265** | **0.104949** | 0.0953 | 0.0942 |
| `p` at `T-14-2-B118` (rank 2) | **0.054505** | **0.056783** | 0.0545 | 0.0584 |

**Every `RT-20260729-025` figure is independently confirmed to the precision it
was quoted at, under the model it used.** This is the first independent
confirmation of them by a session that did not produce them.

### 5.1 The top-tuple share, and why the `-028` receipt and the amendment do not
actually disagree

- `0.095265 / 0.229893 = 41.44 %` — the top tuple's share of the **conditional**
  CR-3 total. The `-028` receipt's `40.5 %` is this quantity computed with
  `bias_i = 0`.
- `0.095265 / 0.18726 = 50.87 %` — the top tuple's share of the **declared
  marginal** CR-3 budget line. The amendment's `about 51 percent` is this
  quantity, and the amendment says so in terms (`of the entire declared 48-tuple
  CR-3 budget of 0.18726`).

**The recorded disagreement is a denominator mismatch, not an arithmetic error in
either session.** Both statements are true of different denominators. The
amendment's phrasing is nevertheless confusing, because it divides a conditional
numerator by a marginal denominator; **objection RT29-1 records this.**

Two tuples take `0.095265 + 0.054505 = 0.149770`, which is `79.98 %` of the
declared `0.18726`. The amendment's `about 80 percent` is confirmed.

### 5.2 `OI-10` RESOLVED — the degrees of freedom, and the exact factor

- **`T-18-2-B264` has `n_rep = 30`, hence 29 degrees of freedom**, hence the
  declared per-tuple reference that applies to it is **`0.00552`**, not `0.00342`.
- Factor `= 0.095265 / 0.00552 = ` **17.26** under VM-1 as bound, **19.01** under
  exact-A1.
- `T-14-2-B118` has `n_rep = 100`, 99 df, reference `0.00342`, factor **15.94**.

**The amendment's range `about 17 to about 28` is correct as a range but its upper
end is unattainable: the resolved factor is 17.3.** The narrower and correct
statement is *between about 17 and about 19 times the declared per-tuple
reference*. This resolution makes the amendment's own claim **weaker**, and is
recorded for that reason.

## 6. THE CONDITIONAL UNION TOTAL (`OI-3`), AND A CORRECTION TO BOTH PRIOR SESSIONS

`CR-1`, `CR-2` and `CR-4` do **not** contain `mu_001` in any form, so **their
conditional reference law equals their marginal one**; only `CR-3` changes.
Recomputed here from the same 48 tuples with the same exact bias, carrying the
`t`-shaped denominator:

```
CR-1  E[exceedances at 3.000]  = 0.187718     (contract 0.18726; v2 C-4 0.18686)
CR-1  E[exceedances at 4.000]  = 0.008973     (v2 C-4 8.92e-03)
CR-2  E[exceedances at 3.000]  < 4e-15        (v2 C-7; not recomputed here)
CR-3  E[exceedances at 3.000]  = 0.252724     exact-A1   / 0.229893 under A2
CR-4  P(fires)                 = 0.002302     (v2 C-5 0.002302)
E[n_neg]                       = 23.50435     (v2 C-5 23.504)
------------------------------------------------------------------
SUM OF EXPECTED COUNTS         = 0.442744     exact-A1   / 0.419913 under A2
```

The `A2` figure `0.419913` reproduces `RT-20260729-025`'s `0.4196`. **Confirmed.**

**BUT THE INFERENCE BOTH PRIOR SESSIONS DREW FROM IT IS WRONG, AND THIS IS
OBJECTION RT29-2.** `RT-20260729-025` states that `0.4196` is a union-bound total
`WHICH THE DECLARED 0.377 DOES NOT BOUND`, and `C-15` adopts that, declaring
`0.377` `NOT TO BOUND THE CONDITIONAL TOTAL`. The sentence section 8 of the
feasibility table actually asserts is a **probability**, not a sum of counts:
*the probability that at least one criterion registers a chance alarm under a
perfectly correct diagnostic is AT MOST 0.377*. Computed exactly below, that
probability is **0.341** (exact-A1) or **0.292** (A2). **`0.377` therefore remains
a true upper bound on the quantity it was asserted about, conditionally as well as
marginally.**

The correct and narrowest statement is: **`0.377` is no longer a *derived* bound —
the derived conditional union bound is `0.4427` — but it happens to remain a
*true* bound on `P(at least one chance alarm)`, whose conditional value is
`0.341`.** `C-15`'s relabelling therefore states the contract's position as
**worse than it is**. That direction is conservative and is not a loosening, but
it is an inaccuracy in a pre-registered sentence and must not be carried into a
run record unqualified.

## 7. THE SPURIOUS `MISS-STRUCTURED` CHANCE RATE (`OI-5`) — SINGLE PRE-DATA FIGURE

`MISS-STRUCTURED` fires if **any** of: `CR-1` at 2 or more tuples; `CR-1` at any
tuple with `|z_sem| >= 4.000`; `CR-2` at 1 or more; `CR-3` at 2 or more tuples;
`CR-3` at any tuple with `|z_shift| >= 4.000`; or `CR-4` fires.

These routes are **not** independent, and they must not be summed. Conditional on
the committed draw, at a fixed tuple `CR-1`'s and `CR-3`'s numerators differ by
the **constant** `r_i`, and both statistics are deterministic functions of the
same pair `(mu_rep,i, s_rep,i)`; `sign(mu_rep,i - P_pred,i)` is a third function of
the same pair. Across tuples the streams are distinct by construction per `RC-C`.

The exact computation therefore parameterises each tuple by
`(z, u)` with `z ~ N(0,1)`, `u ~ chi2_{n-1}/(n-1)`, giving
`CR-1 = |b_i + z|/sqrt(u)` with `b_i = bias_i/sem_001,i`,
`CR-3 = |delta_i + z|/sqrt(1+u)`, and `neg = [b_i + z < 0]`; the joint 3x3x2 state
law per tuple is integrated on a 40000-node equal-probability `u` grid with
analytic normal mass in `z`, and the 48 tuples are convolved exactly by dynamic
programming over `(CR-1 count capped at 2, CR-3 count capped at 2, n_neg)`.

```
                                          VM-1 as bound (A1+A2)   exact-A1
P(CR-1 at 2 or more tuples)                      0.007654         0.015301
P(CR-1 at any tuple >= 4.000)                    0.003066         0.008934
P(CR-3 at 2 or more tuples)                      0.018289         0.022007
P(CR-3 at any tuple >= 4.000)                    0.005190         0.007872
P(CR-4 fires)                                    0.002302         0.002302
P(CR-2 at 1 or more)                             < 4e-15          < 4e-15
naive sum of the routes                          0.036500         0.056415
EXACT JOINT P(MISS-STRUCTURED)                   0.033758         0.050095
```

### THE PRE-DATA FIGURE THIS CONTRACT REQUIRES

> **UNDER A PERFECTLY CORRECT REPAIRED NULL, THE PROBABILITY THAT
> `EXP-YIELD-002` RECORDS `MISS-STRUCTURED` — AND THEREBY SUPERSEDES
> `EV-ECDLP-008` OBSERVATION `O-4` AND RECORDS THAT THE `BATCH-011` VOID
> REFLECTS A MEASUREMENT FAULT — IS `0.050`.**
>
> Stated to the precision it is worth: **5.0 percent**, with `0.034` the value
> under the amendment's own `A2` approximation, which is a lower bound.
> **`0.050` is the figure to be carried, because `A2` is known to understate.**

This **contradicts** `RT-20260729-025`'s `roughly 3 to 4 percent` and is recorded
as **objection RT29-7**. Two independent causes: that estimate used `A2`
throughout, which understates by about 48 percent here; and it proposed to
*subtract* a `1/sqrt(2)` correlation term from a sum of route probabilities, where
the exact joint calculation shows the overlap correction is only `0.0027` under
`A2` (`0.0365 -> 0.0338`) and `0.0063` under exact-A1 (`0.0564 -> 0.0501`).

### The number no session has stated, and it is the largest one here (RT29-8)

The same computation yields the full branch law under a **perfectly correct**
repaired null:

```
                       VM-1 as bound (A1+A2)   exact-A1
P(P-CORE)                    0.708                0.659
P(MISS-MARGINAL)             0.258                0.291
P(MISS-STRUCTURED)           0.034                0.050
```

**Even if the diagnostic is exactly right, this design records the pre-registered
prediction as NOT MET about one time in three.** That is a property of requiring
four criteria to hold simultaneously at 48 tuples at a per-tuple threshold of
3.000, it is not a new defect introduced by any amendment, and the contract's own
`MISS-MARGINAL` branch exists for it. But it is nowhere stated, and a reader of a
`MISS-MARGINAL` record needs it more than any other figure in this note.

## 8. `OI-4` — RULING ON COROLLARY VM-1a

**CONFIRMED, WITH ITS EFFECT QUANTIFIED.** Conditional on the committed draw,
`CR-3`'s numerator equals `CR-1`'s numerator minus the constant `r_i`; the two
statistics are deterministic functions of the same `(mu_rep, s_rep)`. The
`1/sqrt(2)` figure section 8 names is the **marginal** correlation, obtained by
treating `mu_001` as redrawn, and is not the conditional dependence. Any
conditional total that subtracts a `1/sqrt(2)` correlation term — including the one
in `RT-20260729-025`'s own `NB-2` discharging change — uses the wrong figure.

**Quantified effect, which the amendment left open:** the overlap correction to the
`MISS-STRUCTURED` route sum is `0.0027` under `A2` and `0.0063` under exact-A1,
i.e. **small and favourable**. `VM-1a` is right and its numerical consequence is
minor; it changes no disposition.

## 9. `OI-6` — RULING ON A1, A2 AND COROLLARY VM-1b

**A2 — the amendment's declared direction is CORRECT and the magnitude is larger
than the amendment implies.** Replacing the random denominator by its central
value understates the tail. Removing `A2` moves `E[CR-3 exceedances]` from
`0.229893` to `0.252724` (`+9.9 %`), the 4.000 figure from `0.005198` to
`0.007888` (`+52 %`), and `P(MISS-STRUCTURED)` from `0.0338` to `0.0501`
(`+48 %`). **`A2` should not have been carried as a declared approximation when
removing it is a single quadrature.** Recommendation, non-blocking: the exact-A1
column governs the record.

**A1 — the amendment declares its direction and magnitude UNKNOWN. That is
over-cautious and this session bounds it.** Writing `rho = sigma_true/sem_001`:

```
rho     E[CR-3 @3]   E[CR-3 @4]   P(>=1)     max p_i
0.85     0.26542      0.006632     0.24189    0.12748
0.95     0.25675      0.007536     0.23342    0.11185
1.00     0.25272      0.007887     0.22957    0.10495
1.05     0.24892      0.008182     0.22596    0.09860
1.15     0.24195      0.008628     0.21946    0.08737
```

Over `rho` in `[0.85, 1.15]` — far wider than either error source justifies — the
budget moves by at most `+5.0 %` / `-4.3 %`. The two contributions to `rho - 1`
are (i) the structural change in spread from pre-marking `s` bins, which is
`O(s/N)` and at most `22/4001 = 0.55 %` at `m=3` and `1/4001` at `m=2`, and
(ii) the sampling error in `s_001` itself, relative sd `1/sqrt(2(n_rep-1))`, i.e.
`7.1 %` at `n=100` and `13.1 %` at `n=30`. **`A1` is therefore ADEQUATE for a
pre-registered budget**, and the amendment is right that no criterion depends on
it, because `CR-3`'s denominator uses the measured `sem_rep` and the committed
`sem_001` and never `sigma_true`.

**Corollary VM-1b — CONFIRMED, and it is exactly right.** `z_shift` is
`Z_delta / sqrt(1 + u)` where a Student-`t` at `n-1` df would be `Z / sqrt(u)`.
Replacing `u` by `(1+u)/2` halves the relative variability of the denominator, so
the law lies strictly between `N(delta, 1/2)` and `t_{n-1}/sqrt(2)` and is
**strictly lighter-tailed than the `t` section 8 assumes**, for every finite
`n_rep`. The amendment's refusal to net this against the non-centrality is
correct: the tail-shape error is worth about `-0.0027` in `E[CR-3 exceedances]`
(the gap between using `t` and using the true mixed law at `delta = 0`), while the
non-centrality is worth `+0.065`, so they do not cancel and netting them would
have hidden a factor of twenty-four.

## 10. A CONTROL THE CONTRACT DOES NOT ASK FOR, AND ITS RESULT

If the conditional non-centrality `delta_i` were **not** ordinary sampling noise —
if, say, its spread across the 48 tuples were far from unity — then the committed
`BATCH-011` antipodal arm would itself be inconsistent with the analytic
as-recorded process, and the conditional budget would be a **symptom** rather than
a nuisance. Cheapest discriminating check, computed here:

```
delta_i over the 48 tuples:  mean +0.0122,  sd 1.1303,  rms 1.1185,  max|delta| 2.9336
|delta| > 1 at 16 tuples (N(0,1) expects 15.3);  |delta| > 2 at 3 tuples (expects 2.2)
```

Under `N(0,1)` the sd of a 48-sample sd is about `0.103`, so `1.13` is about
`+1.3` standard deviations. **The committed draw is consistent with being a fair
sample of the analytic as-recorded process, and the conditional non-centrality is
ordinary sampling error, not a symptom.** This supports — it does not prove — the
amendment's decision to treat `NB-2` as an accounting defect rather than a design
defect. It establishes nothing about decomposition yield and nothing about any
curve.

## 11. Method, reproducibility and limits

- Python 3, `numpy 2.4.0`, `scipy 1.15.3`, on the reviewing host, **outside the
  repository**. `Q` from `math.erfc`; `t` and `chi2` tails from `scipy.stats`;
  Poisson-binomial by exact convolution; the joint branch law by the dynamic
  program of section 7 on a 40000-node equal-probability `u` grid.
- **ZERO CURVE COMPUTE.** No sum set, no factor base, no census, no curve
  arithmetic, no `EXP-YIELD-002` driver, no simulation of either arm.
- The scratch scripts were **not** archived and are **not** evidence. Everything
  load-bearing is either a formula stated above or a figure in the tables above,
  both re-derivable from `IN-1` at `2fb2bb7a` by any session with an interpreter.
- Figures are quoted to six decimals where the computation supports it; the
  quadrature and convolution errors are below `1e-6` on all reported totals.

## 12. What is dispatch-gating, restated

`C-15` forbids dispatching a run until a conditional CR-3 exceedance table **and**
a conditional `MISS-STRUCTURED` chance rate are on the committed record. Sections
4, 5 and 7 supply both. **The gate is satisfied only once `TASK-20260729-030`
commits this file**; until then it is a working-tree artifact and is not durable.
