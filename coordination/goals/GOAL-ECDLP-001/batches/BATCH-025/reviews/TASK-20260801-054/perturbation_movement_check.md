# DUTY 4 — PERTURBATION MOVEMENT (PERTURB-MOVE-1)

TASK-20260801-054. Reviewer role served by red-team. Independence **procedural, not
model-level**. *"THIS IS THE DUTY THE BATCH EXISTS TO ADD AND IT IS THE ONE
BATCH-024 DID NOT HAVE."*

Method as the contract requires: **movement derived from driver source FIRST**, then
checked against `perturbation_movement_report.json` row by row over all 210 rows.

---

## 0. Verdict on this duty

**FAILS.** One named REVISE condition is met: **two rungs with no recorded movement
are certified by the reading rule** (RTB-054-1).

Everything else passes. Neither family is invariant in law. No certifying statistic
is incapable of moving on any object in this experiment. The two struck statistics
are correctly struck. The D9 handling is **correct and not overcautious**.

---

## 1. Source-first derivation: can each family move each statistic AT ALL?

Derived from `lpf001_driver.py` before opening the table. Full construction analysis
is in `alternative_class_check.md` §1; the movement predictions follow.

### 1.1 The mechanism, per statistic

| statistic | what it reads | smooth plant (`P_max ≤ Bsm(u=4)`, matched magnitude) | rough plant (`P_max = q > √X`, `Z < 2`) |
|---|---|---|---|
| `STAT-RATE-u@u=2..4` | `P(P_max ≤ Bsm)` at `Bsm ≥ Bsm(u=4)` | **must rise**: every plant is `Bsm`-smooth by construction, so `Δp_hat ≈ γ(1 − p_hat)` | **must fall**: no plant is ever `Bsm`-smooth, so `Δp_hat = −γ·p_hat` |
| `STAT-RATE-u@u=5` | `P(P_max ≤ Bsm)`, `Bsm` = 84 / 256 | **weakly rises**: plant is `Bsm(u=4)`-smooth (256/1024) and is 84-/256-smooth only if all drawn primes are small | **falls, but only by `γ·p_hat` ≈ γ·1.6e-03**, tiny |
| `STAT-RATE-u@u=6` | `Bsm` = 40 / 102 | **essentially inert**: measured accident rate 7.64e-05 / 7.64e-06 → 0.5 / 0.05 added per replicate | **falls by `γ·p_hat` only**, ≈1.4 / 0.7 removed per replicate |
| `STAT-KS-DICK` | `sup|F_emp(z) − (1 − ρ(z))|` | moves — mass added at high `Z` deforms the CDF where `D⁺` lives | moves — mass added at `Z < 2` deforms the CDF near the body |
| `STAT-TAIL-DEEP` | 10th largest `Z` | **can only act through the top ten**: smooth plant's `Z` is concentrated near 3.8 with a very thin upper tail; rough plant's `Z < 2` **structurally**. Predicted: near-zero, dominated by eviction, slightly negative | **cannot insert**; can only evict → slightly negative |

### 1.2 The two a-priori predictions that matter

Made from source, before reading the table:

1. **`STAT-TAIL-DEEP` cannot be moved by the rough family, structurally.** `Z < 2`
   unconditionally (`r ≤ v//q ≤ p²/q < p < q`, so `P_max = q` and
   `Z = 1 + ln r/ln q < 2`), while `T_deep` sits near `Z ≈ 6`. The **only** available
   channel is eviction of null members, which pushes `T_deep` down by a fraction of
   a null sd. **This part of D1 is genuinely structural and I confirm it.**
2. **`STAT-TAIL-DEEP` is NOT structurally immune to the smooth family.** The smooth
   plant's `Z = ln m / ln(max drawn prime)` is a random variable bounded only by
   `ln(p²)/ln 2 ≈ 32`. Whether it reaches `Z ≈ 6` is empirical. **I measured it and
   it does, rarely** — see `attainability_check.md` §1.3. **D1's universal claim is
   false and is blocking defect RTB-054-2.** The *movement flag* is nevertheless
   correctly `False` at all 28 rows, because insertions (≈0.05/replicate) are
   outnumbered ~10:1 by evictions (≈0.5/replicate).

---

## 2. Row-by-row check of all 210 rows

All 28 plant sequences, signed shift in measured null sd, `*` = `LPF_movement_beyond_noise_flag` true.
Prediction column = my source-derived prediction from §1.

| family | cell | statistic | 0.0005 | 0.001 | 0.002 | 0.005 | 0.01 | 0.02 | 0.05 | flags | predicted | agrees |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SMOOTH | 16 | RATE u=2 | 0.500 | 0.750 | 1.247* | 2.748* | 5.272* | 10.290* | 25.382* | 5 | rise, strong | ✅ |
| SMOOTH | 16 | RATE u=3 | 0.707 | 1.415* | 2.868* | 7.062* | 14.126* | 28.304* | 70.698* | 6 | rise, strong | ✅ |
| SMOOTH | 16 | RATE u=4 | 1.685* | 3.406* | 6.811* | 16.992* | 34.052* | 68.137* | 170.340* | 7 | rise, strongest | ✅ |
| SMOOTH | 16 | RATE u=5 | −0.124 | −0.088 | 0.027 | 0.302 | 0.845 | 1.839* | 4.929* | 2 | weak rise | ✅ |
| SMOOTH | 16 | RATE u=6 | −0.172 | −0.172 | −0.182 | −0.211 | −0.241 | −0.290 | −0.290 | **0** | inert | ✅ |
| SMOOTH | 16 | KS-DICK | −0.151 | −0.207 | −0.291 | −0.528 | −0.955 | −1.795* | −4.278* | 2 | moves | ✅ |
| SMOOTH | 16 | TAIL-DEEP | 0.061 | 0.061 | 0.061 | 0.061 | −0.037 | 0.016 | −0.034 | **0** | inert, ~0 | ✅ |
| SMOOTH | 20 | RATE u=2 | 0.248 | 0.497 | 0.973 | 2.408* | 4.815* | 9.602* | 23.976* | 4 | rise | ✅ |
| SMOOTH | 20 | RATE u=3 | 0.900 | 1.572* | 2.904* | 6.865* | 13.508* | 26.728* | 66.433* | 6 | rise | ✅ |
| SMOOTH | 20 | RATE u=4 | 2.048* | 4.036* | 8.024* | 19.886* | 39.717* | 79.327* | 198.136* | 7 | rise, strongest | ✅ |
| SMOOTH | 20 | RATE u=5 | 0.017 | 0.036 | 0.097 | 0.181 | 0.289 | 0.628 | 1.516* | 1 | weak rise | ✅ |
| SMOOTH | 20 | RATE u=6 | −0.330 | −0.330 | −0.330 | −0.344 | −0.426 | −0.371 | −0.454 | **0** | inert | ✅ |
| SMOOTH | 20 | KS-DICK | −0.014 | −0.056 | −0.132 | −0.367 | −0.676 | −1.441* | **+11.846\*** | 2 | moves | ✅ (sign: see §4) |
| SMOOTH | 20 | TAIL-DEEP | −0.160 | −0.160 | −0.160 | −0.160 | −0.248 | −0.194 | −0.248 | **0** | inert, ~0 | ✅ |
| ROUGH | 16 | RATE u=2 | 0.122 | 0.003 | −0.244 | −0.882 | −2.061* | −4.366* | −11.248* | 3 | fall | ✅ |
| ROUGH | 16 | RATE u=3 | −0.046 | −0.108 | −0.242 | −0.528 | −1.073* | −2.165* | −5.345* | 3 | fall | ✅ |
| ROUGH | 16 | RATE u=4 | −0.025 | −0.041 | −0.092 | −0.179 | −0.356 | −0.696 | −1.701* | 1 | fall, weaker | ✅ |
| ROUGH | 16 | RATE u=5 | −0.198 | −0.212 | −0.218 | −0.262 | −0.353 | −0.457 | −0.829 | **0** | fall by γ·p_hat only | ✅ |
| ROUGH | 16 | RATE u=6 | −0.172 | −0.182 | −0.211 | −0.182 | −0.241 | −0.320 | −0.409 | **0** | inert | ✅ |
| ROUGH | 16 | KS-DICK | −0.154 | −0.187 | −0.276 | −0.534 | −0.938 | −1.763* | −4.199* | 2 | moves | ✅ |
| ROUGH | 16 | TAIL-DEEP | 0.061 | 0.061 | 0.033 | 0.042 | 0.035 | −0.126 | −0.056 | **0** | inert (structural) | ✅ |
| ROUGH | 20 | RATE u=2 | −0.096 | −0.207 | −0.447 | −1.102* | −2.217* | −4.566* | −11.206* | 4 | fall | ✅ |
| ROUGH | 20 | RATE u=3 | 0.204 | 0.164 | 0.055 | −0.202 | −0.660 | −1.596* | −4.180* | 2 | fall | ✅ |
| ROUGH | 20 | RATE u=4 | 0.056 | 0.048 | 0.012 | −0.089 | −0.260 | −0.544 | −1.605* | 1 | fall, weaker | ✅ |
| ROUGH | 20 | RATE u=5 | 0.008 | −0.011 | −0.021 | −0.044 | −0.072 | −0.190 | −0.462 | **0** | fall by γ·p_hat only | ✅ |
| ROUGH | 20 | RATE u=6 | −0.330 | −0.330 | −0.330 | −0.344 | −0.385 | −0.399 | −0.481 | **0** | inert | ✅ |
| **ROUGH** | **20** | **KS-DICK** | **−0.021** | **−0.049** | **−0.122** | **−0.358** | **−0.687** | **−1.403\*** | **−0.759** | **1** | moves | **⚠️ D9** |
| ROUGH | 20 | TAIL-DEEP | −0.160 | −0.160 | −0.160 | −0.180 | −0.191 | −0.221 | −0.338 | **0** | inert (structural) | ✅ |

Plus 14 `OBJ-CTRL-PRODUCT` rows (7 ids × 2 cells, `gamma_rung: null`): **all 14
flagged**, shifts 251.07 to 1097.12 null sd, detection 20/20 under DET-LPF-1. **All
210 rows accounted for.**

### 2.1 Every check the duty names

| duty check | result |
|---|---|
| a family invariant in law | **None.** Both derived from source to change the law by 2 orders (smooth) / deterministically (rough). ✅ |
| a certifying statistic incapable of moving on **any** object in this experiment | **None.** All seven ids — including both struck ones — move on `OBJ-CTRL-PRODUCT` at both cells, 20/20, with shifts 251–1097 null sd. `STAT-TAIL-DEEP` moves upward by 13.48 and 16.73 null sd. **No statistic in this apparatus is a dead instrument.** ✅ |
| a rung with no recorded movement that the reading rule certifies | ❌ **TWO. RTB-054-1.** |
| every family, rung, cell, statistic present | 210 = (1 + 7 + 7) × 2 cells × 7 ids. ✅ |
| both movement readings recorded per row | ✅, and they agree on every inert row |

### 2.2 The failure — RTB-054-1, in full

`certification.certified_ladders` freezes a `moving_rungs_bits_<cell>` list per
ladder, and the block's own note defines it as the per-rung power certificate:
*"Per-rung power is certified only at rungs whose own row moves; rungs below the
movement floor are UNCERTIFIED and are listed as such."* Recomputing all 28 lists
mechanically from `LPF_movement_beyond_noise_flag`:

| ladder | cell | frozen | recomputed | shift at the disputed rung | flag (sd) | flag (range) | DET-LPF-1 |
|---|---|---|---|---|---|---|---|
| ROUGH / RATE u=2 | 16 | [**0.005**, 0.01, 0.02, 0.05] | [0.01, 0.02, 0.05] | −0.882122 | `False` | `False` | 1/20, not detected |
| ROUGH / KS-DICK | 16 | [**0.01**, 0.02, 0.05] | [0.02, 0.05] | −0.937958 | `False` | `False` | 1/20, not detected |
| SMOOTH / RATE u=3 | 20 | [0.002, …] | [**0.001**, 0.002, …] | +1.572416 | `True` | `False` | 4/20, not detected |
| other 25 | — | — | identical | — | — | — | — |

**The first two certify rungs that are uncertified on every criterion the calibration
archives.** PERTURB-MOVE-1's `named_reviewer_duty` states the consequence in terms:

> *"A family that is invariant in law, or **a rung with no recorded movement that the
> reading rule nevertheless certifies, is a REVISE.**"*

I cannot waive a REVISE condition the contract names, and I do not. The direction
compounds it: both overstatements are in the **rough** direction, which the file
itself identifies as the measurably weaker one, and they claim power at a γ an octave
below where any movement was recorded. The third entry errs the other way and is
non-blocking (RTB-054-3).

**This is a transcription failure, not a measurement failure.** The archived table is
correct; the frozen summary of it is not. The repair is to generate `moving_rungs`
mechanically from the flag rather than by hand — no re-execution.

---

## 3. D9 — ruling on striking the whole ROUGH / KS-DICK / bits-20 ladder

### 3.1 The sequence — recomputed, exact

Rows 199 and 206 of 210 in row order, γ = 0.0005 → 0.05:

```
−0.02048864063723827
−0.04862444996303586
−0.12221041281508659
−0.35811835254670454
−0.68709089235589720
−1.40275045264261600   ← flag TRUE
−0.75872025485676250   ← flag FALSE at the TOP RUNG
```

**Identical to the frozen sequence, to every digit given.** ✅

### 3.2 Is it the only one? — YES, on the predicate that matters

I scanned all 28 sequences. Ten are non-monotone in `|shift|`, but eight of those are
sign crossings at sub-noise magnitudes (e.g. ROUGH/RATE u=2/bits 16 starts at +0.122
and crosses zero going negative) and one is the SMOOTH/KS-DICK/bits-20 sign flip
(§4). **On the predicate the strike rule actually keys on — a flag `True` at an
intermediate rung and `False` at the top rung — this is the unique instance in the
210-row table.** The freeze's uniqueness claim is correct.

### 3.3 Ruling: **the whole-ladder strike is RIGHT, and it is not overcautious**

Four grounds.

1. **The text.** PERTURB-MOVE-1 contains two sentences. The per-rung sentence
   (*"may certify power at a rung only where that table records a shift beyond
   noise"*) is a **necessary** condition for certifying a rung. The top-rung sentence
   (*"A FAMILY WHOSE TOP RUNG SHOWS NO MOVEMENT IS STRUCK FROM THE CERTIFIED LIST"*)
   is a **sufficient** condition for striking. **Both are satisfied here in the
   direction of the strike, so there is no tension to resolve** — the freeze's
   reading of this is correct and I adopt it.
2. **The inventor protocol.** `docs/inventor-protocol.md` §3 names the canonical
   artifact tell: *"a quantity that should decay and does not"*, generalised as *ask
   what the measured quantity should do as the parameter meant to drive it
   increases*. Here γ is the parameter that is supposed to **grow** the shift, and
   the shift **shrank by 46 %** when γ was raised 2.5×. That is the tell, in the
   direction the protocol names. **Harvesting the one rung that moved out of a
   sequence that then reversed is selective reading**, and it is precisely what
   PERTURB-MOVE-1 was written after BATCH-024 to forbid.
3. **The mechanism, which is known and disqualifying.** D6 diagnosed it and I
   verified the diagnosis by execution: `stat_ks_dickman` returns `max(D⁺, D⁻)`, and
   at replicate 0 the null `D⁺/D⁻` are **0.04919123/0.00030** at bits 16 and
   **0.03823691/0.00006** at bits 20 — reproducing VAL-20260801-006's numbers
   exactly. Near the crossing the argmax switches, so `max(D⁺, D⁻)` is **not a
   monotone functional of the perturbation size**. A statistic that is not monotone
   in the driving parameter cannot support a per-rung power certificate on that
   ladder at all. **Certifying γ = 0.02 alone would certify a rung whose value is an
   argmax accident.**
4. **The consequence, which the freeze states rather than hides.** Certifying that
   rung would leave a certified ladder with an inert top rung, satisfying L-1's
   second leg on already-archived data and making L-2, L-3 and L-4 unreachable by
   construction. **That the honest alternative is a REVISE and a non-execution is
   recorded plainly, and recording it is what makes the choice reviewable.**

**Is it overcautious?** The cost of the strike is exactly V10 — no rough-direction
power certified against `STAT-KS-DICK` at bits 20 — and that cost is **zero in
practice**, because that ladder never reaches DET-LPF-1 detection at any rung anyway
(max 6/20 rejections at γ = 0.05, `NONE_ON_LADDER`). **The strike surrenders nothing
that was there.** OPEN-RR052-C's alternative is properly recorded and properly not
applied.

### 3.4 Ruling on the D6 consequence (OPEN-RR052-D)

**The frozen ruling is correct and I confirm it.** A `STAT-KS-DICK` band exit
establishes **that** the empirical `Z`-CDF departs from the Dickman CDF and not
**which way**, because the statistic is `max(D⁺, D⁻)` by construction and the argmax
demonstrably switches at these parameters. Direction under L-3 must be read from
`STAT-RATE-u`, whose sign is unambiguous (`p_hat` above band = smoother, below =
rougher).

**I add one binding the frozen text does not carry:** the same argument bars reading
directional *agreement* between cells from `STAT-KS-DICK` too — two same-signed
excursions may be produced by different argmaxes. **Only `STAT-RATE-u` establishes
direction, in agreement as well as in disagreement.**

---

## 4. An asymmetry I raise, which is not a defect but should be recorded

`SMOOTH / STAT-KS-DICK / bits 20` runs −0.014, −0.056, −0.132, −0.367, −0.676,
**−1.441\***, **+11.846\*** — the sign **reverses** between the two flagged rungs
while the magnitude jumps by 8×. This is the same `D⁺/D⁻` argmax switch as D9, in the
other family.

The ladder is certified, correctly: its **top rung moves**, so PERTURB-MOVE-1's strike
condition is not met, and unlike D9 the magnitude **grew** with γ rather than
shrinking, so the inventor-protocol artifact tell does not fire. **I am not asking
for this ladder to be struck.**

But the asymmetry deserves naming: the freeze applied the artifact-tell lens hard to
the rough/bits-20 ladder and did not apply it to the smooth/bits-20 ladder, where the
same instrument pathology is present in a form that happens not to trigger the rule.
The consequence is already contained — OPEN-RR052-D and V10 forbid reading any
direction from `STAT-KS-DICK` — but a reader of the certified list will see
`SMOOTH/KS-DICK` certified at both cells and will not see that its two cells'
top-rung shifts have **opposite signs from the same perturbation**. That fact belongs
beside the certification. **Forward guidance:** a KS-type statistic used for power
certification should be recorded as the signed pair `(D⁺, D⁻)` rather than as their
maximum, at every rung. The driver already computes both internally; only the
reporting collapses them.

---

## 5. The two strikes, checked against this duty

| | `STAT-TAIL-DEEP` | `STAT-RATE-u@u_target=6` |
|---|---|---|
| plant rung-cell rows | 28 | 28 |
| flagged, sd reading | **0** | **0** |
| flagged, range reading | **0** | **0** |
| max abs shift | 0.3379820826156079 | 0.4809110364879298 |
| moves on `OBJ-CTRL-PRODUCT`? | **yes**, +13.48 / +16.73 null sd | **yes**, +251.07 null sd, 20/20 |
| structural account | **rough half yes, smooth half NO** (RTB-054-2) | **yes**, independently measured: 10/130820 and 1/130820 accident rate |
| strike correct under PERTURB-MOVE-1? | ✅ | ✅ |

**Both strikes are correct. One justification is not (RTB-054-2).** Under CERT-LPF-1
a strike must be *"recorded **and justified**"*, and a justification contradicted by
a faithful re-execution of the frozen driver does not discharge that.

**The distinction is load-bearing and worth stating in one line:** CERT-LPF-1 forbids
reporting a struck statistic's inertness as "low power". D1 existed to establish that
the inertness was structural instead. For the **rough** family that is true and
derived from source. For the **smooth** family the truth is a *measured
near-disjointness with a 10:1 eviction-to-insertion ratio at γ ≤ 0.05* — neither "low
power" nor "structurally impossible", and the correct phrase is neither of the two
the file offers.

---

## 6. Standing lesson — endorsed, and sharpened

The freeze records the roadmap lesson: *"a certifying statistic must be checked for
reachability by its own perturbation objects at DESIGN time, by deriving the support
of the perturbed law against the region the statistic reads, not at calibration time
by measuring a shift."*

**I endorse it and sharpen it in the direction this review exposed.** Deriving the
*support* is not enough when the perturbed law is unbounded, which is the smooth
family's case: its `Z` has no upper bound below 32, so no support argument can settle
whether it reaches the deep tail. **The design-time check must be a derivation of the
perturbed law's TAIL against the ORDER STATISTIC the statistic reads** — here,
`P(Z_plant > z₍₁₀₎)` against the null's tenth-largest — and where that is not
analytically available, a cheap Monte-Carlo of the replacement construction (seconds,
no factorization) is the substitute. **That measurement should be archived as a
machine-readable array**, so no future record has to take a maximum-`Z` claim on
trust, which is exactly how RTB-054-2 entered the frozen file.

---

## 7. Summary

| item | result |
|---|---|
| movement derived from source before consulting the table | ✅ |
| all 210 rows checked | ✅ |
| any family invariant in law | **none** |
| any certifying statistic incapable of moving on any object here | **none** |
| any rung with no recorded movement certified by the reading rule | ❌ **2 — RTB-054-1, REVISE** |
| top-rung movement table (28 cells) matches frozen block | ✅ exact |
| certified/struck ladder statuses match the top-rung rule | ✅ 28/28 |
| `moving_rungs` lists match the flags | ❌ 25/28; 2 overstate, 1 understates |
| D9 sequence | ✅ exact, 7/7 values |
| D9 uniqueness on the operative predicate | ✅ unique in 210 rows |
| D9 whole-ladder strike | ✅ **correct, not overcautious**; costs nothing measurable |
| D6 / OPEN-RR052-D direction ruling | ✅ confirmed, and extended to bar directional *agreement* |
| both strikes correct under PERTURB-MOVE-1 | ✅ |
| STRIKE-1 justification survives execution | ❌ **RTB-054-2** |

**Duty 4 fails on RTB-054-1.**
