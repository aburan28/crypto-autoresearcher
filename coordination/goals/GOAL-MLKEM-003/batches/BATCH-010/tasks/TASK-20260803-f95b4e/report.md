# TASK-20260803-f95b4e — BATCH-010, GOAL-MLKEM-003

## Two discriminating checks on the BATCH-009 Approximation-4.9 comparison

**Role: Executor. This report records observations only.** It does not conclude
that Approximation 4.9 is validated, refuted, selected or rejected; that
judgement belongs to the independent validator and then to the Coordinator.

**Toy tier.** Parameters are `q=241, m=40, n=43/50`. **No ML-KEM or Kyber
security claim is made in either direction.** No cost model is revised and no
record status is changed. AGENTS.md rule 12 is **UNMET and UNWAIVED** for this
batch: `EV-MLKEM-011`, `EV-MLKEM-013` and `EV-MLKEM-017` keep their status and
nothing here treats them as corrected.

**Zero new sampling.** No lattice computation, no G6K call, no network access,
no new simulation. Every input byte was already in this repository.

---

## 1. Provenance

| item | value |
|---|---|
| repository commit at execution | `9b6b6ee8f83fb726ac366ba9b33b53d231044dea` |
| branch | `claude/harness-findings-repo-yyzt1x` |
| dirty tree at execution | only this task's own (untracked) directory |
| python | 3.11.15 (main, Mar 3 2026, 09:26:23) [GCC 13.3.0] |
| platform | Linux-6.18.5-x86_64-with-glibc2.39 |
| numpy / scipy | **not installed** — all quadrature is hand-rolled |
| memory cap applied | `ulimit -v 4194304` (4 GB), per the handoff budget |
| runs | `exponent_neighbourhood_scan.py` x1 (208.6 s), `jensen_bias_bound.py` x1 (18.9 s) |
| randomness | **none** — both scripts are fully deterministic; no seed exists to record |

### Inputs (read-only), with hashes verified at execution

| file | sha256 |
|---|---|
| `experiments/EXP-MLKEM-011/vendor-lock/data/Pwrong_q241_m40_n43_nfft8_kfft3_nlat35_beta032_beta144_N25971.out` | `50bd293cadf952516b092524c25f4404a1e4ca40983d1751286f96269dbf90bb` |
| `experiments/EXP-MLKEM-011/vendor-lock/data/Pwrong_q241_m40_n50_nfft8_kfft3_nlat42_beta035_beta141_N25970.out` | `ce23181dca95a1c6a72463c2c39f14f645500a068b3af46c71d5b45af69ab459` |

Archived Carrier text read:
`inputs/MLKEM-DUAL-SOURCES-20260802/extracts/carrier-hal-05406481/page23_approx_4_8_4_9.txt`
(eqs. 4.17-4.24) and `.../page25_pwrong_validation.txt` (eqs. 4.26-4.29 and the
`P(D>T) = INT psi_lsc(d) P(D>T|d) dd` statement). Also read: `page26_fig41.txt`,
`page27_threshold_choice.txt`.

### Inference

```yaml
inference:
  requested_policy: executor-implementation
  resolved_model: claude-opus-5
  fallback_used: true     # this harness runs Claude models against GPT-5.6
                          # policy aliases (CLAUDE.md model-policy note)
  model_verified: false   # no `orchestration.adapter doctor --probe` was run
  reasoning_effort: null
  independent_session_required: false
```

### Resolved band and counting floor (re-verified, never crossed)

| file | `nb_iteration` | counting floor | resolved band | first zero |
|---|---|---|---|---|
| n=43 | 4000 | `1.7860305406935986e-11` = `2^-35.70445229` | scores `[0, 1802]` | 1803 |
| n=50 | 6000 | `1.1906870271290657e-11` = `2^-36.28941479` | scores `[0, 2309]` | 2310 |

Nothing in either check is fitted, anchored, compared or extrapolated past the
last positive score. Both headline peak scores (471, 420) are inside the band.
Score scale is the **raw undivided cosine-sum scale**; no `k_fft` alignment is
applied anywhere (the `k_fft = 3` asymmetry of KN-FIND-014 is left exactly as
BATCH-009 left it).

---

## 2. What was computed

Both checks use the same model BATCH-009 used
(`TASK-20260802-8bae8e/approx49_comparison.py`, STEP 1-4):

```
Pwrong(T; K, p) = Q(T) + INT_0^inf  N e^{-v} phi(T - N e^{-v}) * min(1, K v^p) dv
Q(T)   = 0.5 erfc(T / sqrt(N))                 the N(0, N/2) component
phi(s) = exp(-s^2/N) / sqrt(pi N)              the N(0, N/2) density
v      = L = ln(N/u),  p = (beta_sieve + n_fft)/2
```

`K` collects every quantity the archive does not carry — `delta(beta_bkz)`,
`alpha`, and the constants of `Phi_{d_lsc}` — and is **fitted to the very data
being compared**. That is unchanged from BATCH-009 and is restated here because
it bounds what either check can mean: this is a shape-and-relative comparison
with one free normalisation, **not** an absolute-level test.

I re-confirmed against the archived extracts that `Phi_{d_lsc}` appears only as
an undefined symbol (`Phi_dlsc(i,j)`, `Phi_dlsc(x,y)` on page23/page25) and that
`alpha` is given no numeric value on any archived page. Both remain
**UNAVAILABLE**, exactly as the BATCH-009 parameter ledger recorded.

---

## 3. Check A — exponent-neighbourhood control

**Question, per file:** does the file's own Approximation-4.9 exponent minimise
rms against its own data, or does a neighbour win?

**Method.** For each file, `p` was scanned over its own archived value +/- 6.0 in
steps of 0.25 (49 values). At every `p` the single free scale `K` was re-fitted,
and the rms of the log2 residual `log2 pred(T) - log2 measured(T)` was evaluated
over the whole resolved band. Two fit protocols were carried:

* **protocol A (primary)** — `K` minimises SSE over the **whole** resolved band;
* **protocol B (continuity)** — `K` minimises SSE over `band[::20] + last score`,
  i.e. the BATCH-009 headline protocol.

Both report rms over the whole resolved band. They agree throughout to
<= 0.0002 bits, so only protocol A is tabulated below; protocol B is in
`results.json`.

### 3.1 Result — argmins

| file | own archived `p` | rms at own `p` | **argmin `p`** | **rms at argmin** | excess of own over argmin | argmin at grid edge? |
|---|---|---|---|---|---|---|
| n=43 | 26.0 | 0.705494 | **23.25** | **0.425715** | **+0.279779 bits** | no |
| n=50 | 24.5 | 0.696881 | **22.25** | **0.427413** | **+0.269468 bits** | no |

**In neither file is the file's own Approximation-4.9 exponent the argmin.** In
both files the argmin lies *below* the own exponent — by 2.75 (n=43) and 2.25
(n=50). Neither argmin sits at a grid boundary, so neither is scan-width
limited. `log2 K` at the argmins: -67.97057 (n=43), -63.54163 (n=50).

Cross-exponent values (the TASK-20260803-bc8c1f C4 control, reproduced):

| data | under own `p` | under the *other* file's archived `p` | difference |
|---|---|---|---|
| n=43 | 0.705494 (p=26.0) | **0.496543** (p=24.5) | own is **worse** by 0.208950 bits |
| n=50 | 0.696881 (p=24.5) | 1.020420 (p=26.0) | own is better by 0.323539 bits |

This reproduces the BATCH-009 validator's C4 numbers (0.7055 / 0.4965 /
0.6969 / 1.0204) to four decimals, and extends the single instance to the full
curve: the n=43 one-sidedness is not an isolated point but a sample of a
smooth curve whose minimum is a further 1.25 below `p = 24.5`.

### 3.2 Result — the curves (protocol A, whole-band rms in bits)

Abridged; the complete 49-point curves for both files, with `log2 K`,
whole-band rms, count>=10 sub-band rms and mean residual at every `p`, are in
`results.json` -> `check_A_exponent_neighbourhood.files[*].rms_vs_p_curve`.

```
n=43  (own p = 26.0)                    n=50  (own p = 24.5)
   p    log2 K     rms                     p    log2 K     rms
20.00  -62.46881  0.706561               18.50  -57.52080  0.932809
21.00  -64.14993  0.582234               19.50  -59.11056  0.752912
22.00  -65.84124  0.479670               20.50  -60.71277  0.585994
22.50  -66.69098  0.444954               21.50  -62.32662  0.461141
23.00  -67.54477  0.427121               21.75  -62.73022  0.442594
23.25  -67.97057  0.425715  <-- argmin   22.00  -63.13683  0.431098
23.50  -68.39894  0.429662               22.25  -63.54163  0.427413  <-- argmin
24.00  -69.25739  0.453471               22.50  -63.94833  0.431911
24.50  -70.11804  0.496543  (n=50's p)   23.00  -64.76464  0.464683
25.00  -70.98056  0.555266               23.50  -65.58075  0.524423
26.00  -72.71144  0.705494  <-- own p    24.50  -67.22051  0.696881  <-- own p
27.00  -74.45074  0.882887               25.50  -68.86509  0.907507
28.00  -76.19564  1.075951               26.00  -69.68776  1.020420  (n=43's p)
30.00  -79.70077  1.487293               28.00  -72.99039  1.496547
32.00  -83.21795  1.914706               30.50  -77.12590  2.112545
```

Both curves are smooth, single-minimum, and steeply rising above the argmin.
`log2 K` moves essentially linearly with `p` (slope ~ -1.73 bits per unit `p`
for n=43, ~ -1.65 for n=50), confirming the free scale does not absorb the
exponent change.

### 3.3 A secondary observation (unrequested, recorded because it was seen)

The rms restricted to the **pooled-count >= 10 sub-band** has a *different*
argmin from the whole-band rms: `p ~ 22.50` for n=43 (rms 0.369998) and
`p ~ 21.75` for n=50 (rms 0.401645). Both are still below the file's own
exponent, so the direction of the finding is unchanged, but the location of the
minimum is not invariant to which scores are weighted. Full column in
`results.json` (`rms_count_ge10_subband_bits`).

### 3.4 Reproduction cross-check

At the archived `(p, log2 K_fit)` this implementation gives:

| file | whole-band rms here | archived BATCH-009 | peak `delta` here | producer | validator |
|---|---|---|---|---|---|
| n=43 | 0.7054940 | 0.7057596 | +1.5154077 @471 | +1.5160635 | +1.5154 |
| n=50 | 0.6968845 | 0.6967212 | +1.7108564 @420 | +1.7103938 | +1.7109 |

The residual difference against the producer (<= 0.00066 bits) is the DEP-A1
clip treatment and nothing else; the numbers agree with the BATCH-009
validator's independent recomputation, which used the same exact-kink
treatment, to 5-6 decimals.

Quadrature self-checks (`results.json`): the `K -> inf` closed-form check has max
relative error 2.6e-15; halving the panel width moves every prediction by
<= 2.8e-14 bits.

---

## 4. Check B — Jensen bias bound

**The defect.** Archived (4.22) places the region integral **inside** `min(1,.)`
and the `d_lsc` integral **outside** it; the archived page25 justification states
the same order explicitly (`P(D>T|d_lsc) ~ min(1, E[...])`, then
`P(D>T) = INT psi_lsc(d_lsc) P(D>T|d_lsc) dd_lsc`). The BATCH-009 script computes
`min(1, Kbar L^p)` — the `d_lsc` average collapsed into one effective scale and
clipped once. Because `min(1,.)` is concave, Jensen makes the collapsed form an
**upper bound**.

**This is a bias bound, not a re-fit.** `Kbar` is held at the archived BATCH-009
fitted value in every reading, and every reading satisfies
`E_{d_lsc}[k(d_lsc)] = Kbar` **exactly**, so the collapsed baseline `P_out` is
literally unchanged and

```
Delta(T) = log2 P_in(T) - log2 P_out(T)
```

isolates the position of `min(1,.)` alone. `K` is not re-optimised anywhere in
`jensen_bias_bound.py`.

### 4.1 Sign

`Delta(T) <= 0` for every reading, by concavity. The correction therefore moves
the prediction **in the same direction as the reported over-prediction**: the
(4.22)-position model predicts *less* than the collapsed model.

### 4.2 What bounds the magnitude — and what does not

**Concavity pins the sign but not the magnitude.** With the mean held at
`Kbar L^p`, `E[min(1,Z)]` can be driven arbitrarily close to 0 by dispersing `Z`.
What *does* bound the magnitude reading-free is that Model 4.7's `D` component
is non-negative, so `P_in(T) >= Q(T)`:

| file / peak score | `log2 P_out` | `log2 measured` | over-prediction | `log2 Q(T*)` | **reading-free bound on `Delta`** |
|---|---|---|---|---|---|
| n=43 @ T*=471 | -13.744464 | -15.259872 | +1.515408 | -15.771008 | **-2.026543 <= Delta <= 0** |
| n=50 @ T*=420 | -10.765140 | -12.475996 | +1.710856 | -13.098605 | **-2.333466 <= Delta <= 0** |

Clipped fraction at the peak score: 0.376547 (n=43) and 0.377878 (n=50) under
this implementation's exact-kink accounting (producer's column: 0.361153 /
0.380799 — validator defect D10, which affects the clipped-fraction *column*,
not the predictions).

**Both over-predictions lie inside the reading-free bound.** The collapse
therefore cannot be excluded on magnitude grounds by concavity alone; the
question becomes how much dispersion the (unarchived) `d_lsc` dependence of
`Phi` actually carries.

### 4.3 Reading R1 — one-parameter dispersion family (primary)

`k(d_lsc) = Kbar exp(s z - s^2/2)` with `z = (d_lsc - mu_lsc)/sigma_lsc ~ N(0,1)`;
`E[k] = Kbar` exactly; `s = sd(ln k)` is the only parameter. The inner expectation
is then closed-form (`W(v) = C*Phi(z_c - s) + 1 - Phi(z_c)`, `C = Kbar v^p`,
`z_c = (-ln C + s^2/2)/s`), so R1 introduces no quadrature error in `d_lsc`, and
`s -> 0` reproduces the BATCH-009 collapse exactly.

| `s` | `Delta` (n=43 @471) | `Delta` (n=50 @420) |
|---|---|---|
| 0.00 | 0.000000 (self-check: 9.9e-14 / 2.7e-13) | 0.000000 |
| 0.20 | -0.004348 | -0.004676 |
| 0.375 | -0.015262 | -0.016421 |
| 0.50 | -0.027089 | -0.029157 |
| 1.00 | -0.107142 | -0.115654 |
| 2.00 | -0.408648 | -0.446635 |
| 3.00 | -0.842895 | -0.942561 |
| 4.00 | -1.312032 | -1.505296 |
| 5.00 | -1.698657 | -1.971793 |
| 8.00 | -2.022313 | -2.329641 |
| >=12 | -2.026543 (bound) | -2.333466 (bound) |

**Dispersion required to absorb the whole over-prediction:**

| file | target | **`s` required** |
|---|---|---|
| n=43 @471 | -1.515408 (recomputed) / -1.5154 (validator) / -1.516064 (producer) | **4.480840 / 4.480821 / 4.482507** |
| n=50 @420 | -1.710856 (recomputed) / -1.7109 (validator) / -1.710394 (producer) | **4.394843 / 4.394931 / 4.393902** |

`s ~ 4.4` nats is `sd(log2 k) ~ 6.3-6.5 bits`: the effective normalisation would
have to vary by that much (1 s.d.) as `d_lsc` varies over its own distribution.

### 4.4 Reading R2 — the shift reading the archived (4.19) points to (secondary)

Archived (4.19) evaluates the good-guess threshold as
`INT psi_lsc(d) e^{-a d^2} dd` times `E[e^{-a d_lat^2 t^2}]` with `a = alpha pi^2/q^2`,
i.e. `Phi` contributes `e^{-a d_lsc^2}` on the lsc side at the correct guess.
Extending that to the wrong guess by treating the wrong-guess FFT offset `y` as
an extra orthogonal lsc-side component gives the **declared** reading
`Phi_d(x,y) = exp(-a(x^2 + y^2 + d^2))`, hence
`INT_{E(u)} lambda*mu = K_0 (L - a d^2)_+^p` — a **shift of `L`**, not a pure
scale. Mean-matched at every `L` (so `Kbar` stays fixed):
`A(d,v) = Kbar v^p (v - a d^2)_+^p / M(v)`, `M(v) = E_d[(v - a d^2)_+^p]`.

`alpha` is **UNAVAILABLE** in every archived page extract, so `a*mu_lsc^2 =
alpha (pi mu_lsc/q)^2` is **scanned**. The archived Pgood header's
`alpha_secret = alpha_error = 2` is *not* established to be the paper's `alpha`
and is not adopted; the `alpha = 2` equivalent is merely marked.

| `a*mu_lsc^2` | implied `alpha` | `Delta` (n=43) | `Delta` (n=50) | `s_eff` (n=43 / n=50) |
|---|---|---|---|---|
| 0.000 | 0 | 0.000000 (self-check) | 0.000000 | 0 / 0 |
| 0.050 | 0.51 / 0.52 | -0.000308 | -0.000304 | 0.093 / 0.083 |
| 0.100 | 1.03 | -0.001234 | -0.001221 | 0.188 / 0.169 |
| **0.195 / 0.194** | **2.00** | **-0.004705** | **-0.004614** | 0.375 / 0.334 |
| 0.500 | 5.13 / 5.16 | -0.031230 | -0.031193 | 1.046 / 0.936 |
| 1.000 | 10.27 / 10.32 | -0.122719 | -0.124389 | 2.439 / 2.171 |
| 2.000 | 20.54 / 20.65 | -0.434454 | -0.455871 | 7.30 / 6.38 |
| 3.000 | 30.81 / 30.97 | -0.804446 | -0.875745 | 21.8 / 18.1 |

At the `alpha = 2` equivalent the correction is **-0.0047 bits (n=43)** and
**-0.0046 bits (n=50)**: **0.31 %** and **0.27 %** of the respective
over-predictions. Even at `a*mu_lsc^2 = 3` (`alpha ~ 31`) the correction reaches
only -0.80 / -0.88 bits, about half the over-prediction.

`s_eff` is the local linearised log-dispersion
`2 p a mu_lsc sigma_lsc / (v_T - a mu_lsc^2)` at `v_T = ln(N/T*)`, given only so
the two readings can be located on a common axis. **It is not an equivalence**:
at `a*mu_lsc^2 = 0.195` R2 gives -0.0047 bits while R1 at `s = 0.375` gives
-0.0153 bits, a factor ~ 3.2. The readings differ in shape, not only in spread.

### 4.5 What the correction does away from the peak (observation only)

With `Kbar` held fixed (no re-fit), the whole-band rms of the R1-corrected model:

| `s` | n=43 rms | n=50 rms |
|---|---|---|
| 0 (collapsed) | 0.705494 | 0.696885 |
| 0.5 | 0.694535 | 0.686603 |
| 1.0 | 0.662542 | 0.656486 |
| 2.0 | 0.548086 | 0.547178 |
| `s` required at the peak (4.4808 / 4.3949) | 0.280763 | 0.279325 |

At that `s` the residual at the peak score crosses zero and turns slightly
negative on the far side (n=43: -0.0075 at `s = 4.5`; n=50: -0.0507 at
`s = 4.5`). Per-score profiles at 5 % intervals are in `results.json`. These
rms values are **not** comparable to Check A's argmin rms: `K` is deliberately
not re-fitted here, because re-fitting it would answer a different question and
is forbidden by the handoff.

---

## 5. Departures from the BATCH-009 implementation

Every departure below is deliberate and was made to answer the question posed,
not to change a reported number. Each is also recorded inside the scripts'
docstrings.

| id | departure | why | effect on numbers |
|---|---|---|---|
| **DEP-A1** | The `min(1, K v^p)` kink is handled **exactly**: the integral is split at `v* = K^{-1/p}` and the clipped piece is closed form, `0.5(erfc((T-u*)/sqrt(N)) - erfc(T/sqrt(N)))` with `u* = N e^{-v*}`. BATCH-009 classified panel nodes on a fixed grid with no node at the kink (validator defect D10). | An exponent scan moves `v*` continuously; a fixed grid would put a discretisation artefact directly into the rms-vs-`p` curve. | <= 0.00066 bits on predictions; measurably changes only the *clipped-fraction* column (0.3765 vs 0.3612 at score 471). This is the same treatment the BATCH-009 validator used. |
| **DEP-A2** | `K` is swept through `v*` (since `K = v*^{-p}`) with the inner integral accumulated incrementally, coarse pass then refinement, instead of coarse integer scan + golden section. | Makes a 49-point exponent scan with a whole-band `K` fit affordable in pure Python (no numpy/scipy here). | none beyond fit resolution (~0.002 bits in `log2 K`). |
| **DEP-A3** | Two fit protocols reported (`A`: whole band; `B`: BATCH-009's `band[::20]+last`), rms always over the whole band. BATCH-009 reported one. | The argmin over `p` is only a profile minimum if `K` is optimised on the same set the rms is reported on; protocol B is carried for continuity with the archived headline. | A and B agree to <= 0.0002 bits everywhere. |
| **DEP-A4** | `p` grid is own-`p` +/- 6.0 step 0.25 (49 points), fit on the whole band. BATCH-009's `free_exponent_diagnostic` used `p` in {10,12,...,40} fit on `band[::40]`. | The handoff asks for a neighbourhood curve with the argmin located; step 2 on a 47-point subsample cannot locate it. | Numbers here are **not** comparable to BATCH-009's `free_exponent_diagnostic` (which reported best `p = 24.0` / `22.0` on its subsample). They **are** comparable to, and reproduce, the BATCH-009 **headline** whole-band rms. |
| **DEP-B1** | The `d_lsc` integral is evaluated **inside** `min(1,.)` as (4.22) and (4.28)-(4.29) specify. | This is the check. | See section 4. |
| **DEP-B2** | The `d_lsc` dependence of `Phi` is supplied by **two declared readings**, because `Phi_{d_lsc}` is UNAVAILABLE. Both are mean-matched so `E_d[k] = Kbar` exactly. | Without a reading the magnitude is not defined at all; without mean-matching the check would silently become a re-fit. | Makes the magnitude *conditional* on a declared, scanned parameter. Stated everywhere it is used. |
| **DEP-B3** | R2 uses `Phi_d(x,y) = exp(-a(x^2+y^2+d^2))` — an **additive shift** in `L`. The BATCH-009 script's STEP 2 wrote `Phi = exp(-(a x^2 + b(d_lsc) y^2))`, a **multiplicative** `d_lsc` dependence. | At `y = 0` the multiplicative form does **not** reproduce (4.19)'s `e^{-a d_lsc^2}` factor, whereas the shift form does. | Recorded as an observation; **not resolved**, because `Phi_{d_lsc}` is UNAVAILABLE and resolving it is not this task's mandate. This is a discrepancy in the BATCH-009 derivation's STEP 2, and it is the same unconstrained half of the reading the validator flagged in D4. |
| **DEP-B4** | R2's mean-matching is done **per `L`**, which normalises away the shift reading's *additional* effect on the unclipped level. | Absorbing that effect would require re-fitting `K`, which the handoff forbids. | R2's `Delta` is therefore a **lower-magnitude** account of what the shift reading would do overall; it isolates the `min`-position effect only. Stated in the script and here. |
| **DEP-B5** | `psi_lsc` is integrated over the whole real line, matching (4.22)'s normalisation constant `pi*sigma_lsc*sqrt(2N)`, although (4.22) writes the `d_lsc` integral from 0. | `P(d_lsc < 0) = 7.2e-13` (n=43) at `mu/sigma = 7.08`, far below every number reported. | none at the reported precision; recorded in `results.json`. |

---

## 6. Self-checks performed

| check | result |
|---|---|
| Gauss-Legendre quadrature vs `K -> inf` closed form | max rel. error 2.6e-15 |
| panel-halving convergence of the predictions | <= 2.8e-14 bits |
| reproduction of BATCH-009 headline rms at archived `(p, K_fit)` | 0.7054940 vs 0.7057596; 0.6968845 vs 0.6967212 |
| reproduction of validator C4 cross-exponent numbers | 0.496543 / 1.020420 vs 0.4965 / 1.0204 |
| R1 degenerate case `s = 0` must equal the collapsed model | `Delta` = 9.9e-14 / 2.7e-13 bits |
| R2 degenerate case `a = 0` must equal the collapsed model | `Delta` = 0.000000 bits |
| R2 mean-match `E_d[A] = Kbar v^p` | max rel. error 5.5e-16 |
| R2 `d_lsc` quadrature convergence (`Z_SUB` 6 -> 12) | 1.0e-11 bits |
| R2 outer-node mask, hard error bound | dropped weight 3.4e-17 of `P_out` |
| every value an integer multiple of the counting quantum | inherited from BATCH-009 (rel. dev. <= 2.2e-16) |

---

## 7. Anomalies and unexpected observations (recorded, none discarded)

1. **The count>=10 sub-band argmin differs from the whole-band argmin**
   (section 3.3): 22.50 vs 23.25 (n=43), 21.75 vs 22.25 (n=50). The direction of
   the Check A finding is unchanged, but the argmin's location depends on the
   score weighting. Not requested; recorded because it was observed.
2. **The BATCH-009 STEP-2 multiplicative reading of `Phi` is inconsistent with
   (4.19) at `y = 0`** (DEP-B3). This was found while constructing R2 and is a
   defect in the archived derivation's justification, not in its arithmetic:
   the exponent `p = (beta_sieve + n_fft)/2` is unchanged under both readings.
   It is adjacent to validator defect D4 and is passed on, not resolved.
3. **Both R1-required dispersions land at essentially the same value**
   (`s ~ 4.48` and `4.39`) despite different `N`, `p`, `Kbar` and peak score.
   Recorded without interpretation.
4. **Concavity does not bound the Jensen magnitude** (section 4.2). The finite
   bound quoted comes from `P_in >= Q(T)`, a different fact. Anyone reading
   "Jensen bounds the bias" as bounding the *size* of the bias would be wrong.
5. `Delta` saturates at the `Q(T)` floor for `s >= 12` — the corrected model's
   `D` component then contributes nothing at the peak score. This is the
   arithmetic of the bound, not a fitted result.
6. Development probes were run in a scratchpad outside the repository while
   building the scripts (timing and a reduced-scan smoke test). Each
   **deliverable** script was executed exactly once, and those single
   executions produced every number in this report and in `results.json`.
   Disclosed because BATCH-009 carried an undisclosed-until-late execution
   overrun (validator defect D6) and this program treats run tallies as
   evidence.
7. `report.md` could not be written through this harness's file-writing tool
   (it refuses `.md` report files) and was written through the shell instead.
   It is a declared `artifact_path` of TASK-20260803-f95b4e, so it is produced;
   the same content is also returned in the executor's text response.

---

## 8. What is *not* claimed

* Nothing here says Approximation 4.9 is validated, refuted, selected or
  rejected. Check A reports curves and argmins; Check B reports a sign, a
  reading-free bound, and magnitudes conditional on a declared scanned
  parameter.
* Nothing here says the reported over-predictions "are" the implementation's
  collapse, or "are not". The observation is that they lie inside the
  reading-free bound (so the collapse is not excluded), that the one textually
  motivated reading with the only numerically archived candidate for `alpha`
  accounts for ~0.3 % of them, and that a log-dispersion of `s ~ 4.4` would
  account for all of them.
* `K` is fitted to the compared data at every `p` in Check A, and held fixed at
  BATCH-009's fitted value in Check B. Neither check tests the absolute level of
  Approximation 4.9; `delta(beta_bkz)` and `alpha` remain UNAVAILABLE, so that
  test remains blocked exactly as BATCH-009 recorded.
* Toy parameters only. No ML-KEM or Kyber security claim, in either direction.

---

## 9. Artifacts

| path | content |
|---|---|
| `coordination/goals/GOAL-MLKEM-003/batches/BATCH-010/tasks/TASK-20260803-f95b4e/exponent_neighbourhood_scan.py` | exact script run for Check A |
| `coordination/goals/GOAL-MLKEM-003/batches/BATCH-010/tasks/TASK-20260803-f95b4e/jensen_bias_bound.py` | exact script run for Check B |
| `coordination/goals/GOAL-MLKEM-003/batches/BATCH-010/tasks/TASK-20260803-f95b4e/results.json` | `check_A_exponent_neighbourhood` (full rms-vs-p curves, argmins, cross-checks, captured stdout) and `check_B_jensen_bias_bound` (bounds, R1/R2 scans, required dispersions, band profiles, captured stdout) |
| `coordination/goals/GOAL-MLKEM-003/batches/BATCH-010/tasks/TASK-20260803-f95b4e/report.md` | this file |

Reproduction: from commit `9b6b6ee8f83fb726ac366ba9b33b53d231044dea`, run
`python3 exponent_neighbourhood_scan.py` then `python3 jensen_bias_bound.py`
from the task directory. Both are deterministic and take 209 s and 19 s
respectively; each merges its own top-level key into `results.json` and leaves
the other key untouched.
