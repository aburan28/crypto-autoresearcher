# DUTY 3 — ALTERNATIVE CLASS (ALT-CLASS-LPF-1, DESIGN-TRAP-LPF-1, ABS-REL-LPF-1)

TASK-20260801-054. Reviewer role served by red-team. Independence **procedural, not
model-level**. Derived from driver source first; measured numbers regenerated or
recomputed in this session.

---

## 0. Verdict on this duty

**DESIGN-TRAP-LPF-1 re-derived independently and CONFIRMED for both families.**
Neither plant is the same-law replacement the trap describes; each moves mass into a
named, derivable part of the `Z`-distribution.

**ABS-REL-LPF-1 ruled on explicitly: PASSES.** No branch can be satisfied by a
two-sample agreement alone; the uniform arm is nowhere treated as the comparison; V1
is stated honestly and is the correct consequence of the design.

**The certified list OVERSTATES what the ladders reach in two places** — the two
miscertified rungs (RTB-054-1) and V8's deep-tail exclusion (RTB-054-2). **Nothing
under V1–V11 is silently claimed.** This duty **fails** on those two, both of which
are repairable in a superseding record.

---

## 1. DESIGN-TRAP-LPF-1 — independent re-derivation from source

The trap, restated: *a perturbation that replaces samples by fresh draws from the
**same** largest-prime-factor law leaves every statistic in STAT-LPF-1 invariant in
distribution and returns the nominal false-fire rate at every rung by construction,
looking like a finding of zero power while measuring nothing.*

I derived, per family, **from `lpf001_driver.py` source and not from the movement
table**, where the replacement moves mass and why it is not invariant in law.

### 1.1 OBJ-PLANT-SMOOTH — `build_smooth_replacement`, driver lines 716–747

**Construction.** Draw primes uniformly with replacement from
`primes_upto(Bsm(u=4))` — 54 primes ≤ 256 at bits 16, 172 primes ≤ 1024 at bits 20 —
multiplying into `m` while `m·q ≤ v`, stopping after 40 consecutive misses. The
replacement's **complete factorization is known by construction** and is verified by
`verify_known_factorization` (0 fallbacks at every smooth rung, confirmed against
`plant_construction_accounting`).

**Where it moves mass, derived.** `P_max(m) ≤ Bsm(u=4)` **deterministically**, while
`m ∈ (v/Bsm, v]` keeps the magnitude matched. Hence

```
Z(m) = ln m / ln P_max(m)  ≥  ln(v/Bsm) / ln Bsm  =  u_eff − 1 ,
```

so the replacement is pushed into the **high-`Z` (smooth) part** of the
distribution, bounded below by roughly `u = 4` and centred near
`ln(p²)/ln(typical largest of ~5 draws from the pool)`.

**Why it is not invariant in law.** A uniform integer on `[1, p²]` has
`P(P_max ≤ 256) ≈ ρ(4) ≈ 4.9e-03` at bits 16. The replacement has
`P(P_max ≤ 256) = 1` by construction — a factor **≈ 204** enrichment at that rung,
and larger at deeper rungs. **This is a law change of two orders of magnitude at the
rung the family certifies against, not a re-draw from the same law.** ✅ Not the trap.

**Measured `Z` distribution of the replacements** (130 820 top-rung plants per cell,
regenerated in this session): mean 3.8166 / 3.7968; q99 4.5943 / 4.4559; q99.9
5.0288 / 4.8190; max 5.9361 / 6.0314. Against a uniform-integer null whose `Z`
median sits near 1.4 and whose tenth-largest is ≈ 6.06 / 5.76. **The mass is moved
into the smooth body-to-upper-body, not into the extreme tail** — which is exactly
why `STAT-RATE-u` at `u = 2..4` moves by 24–198 null sd while `STAT-TAIL-DEEP` does
not move at all.

### 1.2 OBJ-PLANT-ROUGH — `build_rough_replacement`, driver lines 752–812

**Construction.** `m = q·r` with `q` prime drawn log-uniformly in `(p, v//64]` and
`r` prime in `(v//(2q), v//q]`. Factorization known by construction.

**Where it moves mass, derived.** `v ≤ X = p²` and `r ≤ v//q`, so
`r ≤ p²/q < p²/p = p < q`. Hence `P_max(m) = q` **exactly**, and

```
Z(m) = ln(q·r)/ln q = 1 + ln r / ln q  <  2  unconditionally.
```

**The family is confined to `Z < 2`, the roughest possible region.** ✅

**Why it is not invariant in law.** A uniform integer on `[1, p²]` has
`P(Z < 2) = P(P_max > √X) = ln 2 ≈ 0.693` (Dickman), while the replacement has
`P(Z < 2) = 1`. More sharply, `P(P_max ≤ Bsm) = 0` for every rung of the ladder,
against a null `p_hat(2) ≈ 0.359`. **The replacement removes smooth mass
deterministically.** ✅ Not the trap.

**Construction fallbacks** (`v < 64p`, or no prime found in 60 attempts) return
`(0, [])` and leave the **original null sample** in place — so a fallback weakens the
perturbation but cannot contaminate it. Total 344 fallbacks over 926 160 requested
replacements (0.0371 %), worst per-rung rate 0.2217 % (D3). **No fallback introduces
a value from a different law.** ✅

### 1.3 Ruling on DESIGN-TRAP-LPF-1

**CONFIRMED. Neither family is invariant in law, and both are demonstrably so from
source without reference to the measured table.** The smooth family moves mass to
high `Z` (bounded `P_max`, matched magnitude); the rough family to `Z < 2` (`P_max`
above `√X` by construction). The contract's own statement of the trap is accurate and
the design correctly avoids it.

**One asymmetry the contract does not state and I add.** The two families are *not*
equally strong perturbations. The smooth family changes the smoothness probability at
its target rung by a factor of ~200; the rough family changes `P(Z<2)` by a factor of
1/0.693 ≈ 1.44 and removes only the `p_hat` mass it displaces, i.e. its effect is
**bounded by γ** whereas the smooth family's is not. This is the mechanism behind
the measured asymmetry the freeze reports honestly as "ROUGH-DIRECTION POWER IS
MEASURABLY WEAKER THAN SMOOTH-DIRECTION POWER AT THESE CELLS": smooth-direction
top-rung shifts run to 198 null sd, rough-direction to 11.2. **The asymmetry is
structural in the construction, not a sampling accident**, and any future ladder
wanting comparable rough-direction power must perturb more than a γ-fraction or
perturb differently.

---

## 2. ABS-REL-LPF-1 — explicit ruling on the three questions put

### 2.1 Can any branch be satisfied by a two-sample agreement alone? — **NO**

`STAT-KS2-CAL` is the only two-sample statistic. Verified:

- the specification declares it `certifying: false` **in advance and for a stated
  reason** (spec lines 515–523: "A two-sample statistic is blind by construction to
  any deviation both arms share (U1)");
- RR-LPF-1 gives it **no band, no cut, no reject boolean, and no `null_spread`
  entry**, and it is **absent from `statistic_ids(bits)`** in the driver, so the
  measurement loop never bands it;
- I read all six branch conditions clause by clause: **none names `STAT-KS2-CAL` or
  any two-sample quantity.** L-2, L-3 and L-4 read `STAT-RATE-u`, `STAT-KS-DICK` and
  `R(u)`; L-0, L-1 and L-5 read integrity, decay, movement, identity count, product
  detection and Dickman reproduction.

**No branch can be satisfied, blocked or diverted by a two-sample agreement.** ✅
This is the correct treatment: the heuristic's absolute limb is exactly about a
component both arms could share, so a two-sample test is structurally blind to the
thing under test.

### 2.2 Is the uniform arm anywhere treated as the comparison rather than the calibration? — **NO**

Checked at three levels.

- **Bands.** Every one of the 28 edges is an order statistic of `LPF-CAL-A`
  `OBJ-NULL-UNIF` replicates, recomputed exactly. That is the apparatus's **null
  calibration**, not a comparison arm — the object under test is compared to the
  **Dickman law** (LIMB A via `STAT-KS-DICK` and `R(u)`, LIMB B via `[1/8, 8]`), and
  the uniform arm only supplies the **finite-sample sampling distribution** of those
  absolute statistics.
- **Statistics.** `stat_rate_u` divides `p_hat` by the driver's **own solved `ρ(u)`**,
  and `stat_ks_dickman` compares the empirical `Z`-CDF to `1 − ρ(z)`. Both are
  **absolute** comparisons to the analytic law; neither takes a uniform-arm argument.
  The analytic law enters through the **statistic**, the measured null only through
  the **threshold** — which is precisely what RV012-A1 and AP-2 require.
- **Branch conditions.** L-2's third conjunct and L-3's second leg do read a fresh
  uniform arm's `R(u)`, but only as a **decidability gate** — they ask whether the
  apparatus can decide LIMB B at that rung, not whether the real arm differs from the
  uniform arm. A real-vs-uniform difference is never a condition anywhere.

**The uniform arm is the calibration and never the comparison.** ✅

### 2.3 Is the V1 cost of the measured band stated honestly? — **YES**

V1: *"Any departure from the Dickman law that a matched-bitlength uniform sample
exhibits at the same magnitude and sign — absorbed by LIMB A's measured band by
construction; only LIMB B can see it."*

This is the **exact and unavoidable** price of AP-2 (no threshold may be frozen that
has never been measured against its own null) and it is stated without hedging.
**And it is a large price at these cells, which the file does not quantify and should.**
The uniform arm's own `R(u)` is 1.170, 1.452, 2.052, 4.571 at bits 16 and 1.128,
1.306, 1.644, 2.445 at bits 20 — i.e. **the uniform integers are themselves 17 % to
357 % "smoother than Dickman" at these `X`**, and every bit of that is absorbed by
LIMB A's band and invisible to it. LIMB B is the only limb that can see it, and
RTB-054-6 shows LIMB B's own headroom is asymmetrically eaten by the same effect.

**The statement is honest. Its magnitude is not stated and should be**, because a
reader could take V1 for a small residual when at u = 5 it is a factor of 4.6.

---

## 3. Does the certified list overstate what the ladders reach?

### 3.1 S1 (smooth direction) — floors correct, per-rung list has one understatement

`LPF_gamma_det_both_cells` recomputed from the archived detection table:

| statistic | frozen S1 floor | archived | ✓ |
|---|---|---|---|
| `STAT-RATE-u@u_target=4` | 0.002 | 0.002 | ✅ |
| `STAT-RATE-u@u_target=3` | 0.005 | 0.005 | ✅ |
| `STAT-RATE-u@u_target=2` | 0.01 | 0.01 | ✅ |
| `STAT-KS-DICK` | 0.05 | 0.05 | ✅ |
| `STAT-RATE-u@u_target=5` | NONE_ON_LADDER | NONE_ON_LADDER | ✅ |

**Every S1 detection floor is correct.** The per-rung `moving_rungs` list for
SMOOTH / `u_target=3` / bits 20 omits γ = 0.001 (shift 1.572416, flag `True`) —
**understates** by one rung (RTB-054-3, conservative, non-blocking).

### 3.2 S2 (rough direction) — floors correct, per-rung list overstates twice

| statistic | frozen S2 floor | archived | ✓ |
|---|---|---|---|
| `STAT-RATE-u@u_target=2` | 0.02 | 0.02 | ✅ |
| `STAT-RATE-u@u_target=3` | 0.05 | 0.05 | ✅ |
| everything else incl. `STAT-KS-DICK` | NONE_ON_LADDER | NONE_ON_LADDER | ✅ |

**The floors are right.** But the `moving_rungs` lists claim per-rung power at
ROUGH/`u_target=2`/bits 16 γ = 0.005 (shift −0.882122, flag `False`) and at
ROUGH/`STAT-KS-DICK`/bits 16 γ = 0.01 (shift −0.937958, flag `False`). **Both are
uncertified under the sd reading, the range reading and DET-LPF-1 alike.** This is
**RTB-054-1**, blocking, and it is an overstatement in the rough direction — the
direction the file itself flags as the weaker one, which makes the overstatement
worse rather than better.

One further note in the file's favour: the freeze attributes rough `STAT-KS-DICK`'s
`NONE_ON_LADDER` to "whose bits-20 ladder is struck under D9". The archived reason is
simpler — bits-20 rough never reaches 19/20 detection at any rung (max 6/20 at
γ = 0.05), so it would be `NONE_ON_LADDER` with or without the D9 strike. The
conclusion is right; the reason given is not the operative one.

### 3.3 S3 (product control) — correct and correctly caveated

Detected 20/20 by **all seven** statistic ids at **both** cells, verified from
`apparatus_identity_report.json`. Correctly described as **"A SINGLE OBJECT AND NOT A
LADDER; it certifies no gamma floor."** That characterisation is load-bearing for the
OPEN-RR052-A ruling and it is accurate: `gamma_rung` is `null` on every
OBJ-CTRL-PRODUCT row.

⚠️ I add one caveat the file does not carry: at bits 16 the product control's
`STAT-RATE-u@u_target=2` mean is **exactly 1.0 with `plant_sd = 0.0`** — every sample
is 65536-smooth, i.e. the statistic is **saturated at its ceiling**. Its "502.12 null
sd" is a censored quantity. D2 already forbids reading these shifts as effect sizes;
**saturation is a second, independent reason**, and it applies specifically to the
S3 demonstrations.

### 3.4 The `certified_against` scope, as a whole

Correctly narrowed by the strikes and correctly refusing to add anything to the
certified side. `C0` (the EXP-EQD-001 `e₁`-marginal class) is correctly carried as
"A STATEMENT ABOUT A DIFFERENT MEASUREMENT that does not transfer".

---

## 4. Is anything under V1–V11 silently claimed?

Checked each against the branch conditions and the certified list.

| | claim | silently claimed anywhere? |
|---|---|---|
| V1 | departures a matched uniform sample shares | **No** — absorbed by construction, only LIMB B sees it, and LIMB B is read in L-2/L-3 with the uniform arm's decidability as a gate. Honest. |
| V2 | departures below γ = 0.0005 | **No** — and demonstrated: OBJ-PLANT-SMOOTH at γ = 0.0005 produces no band rejection at either cell. |
| V3 | joint law of two largest factors, factorization pattern, factor arithmetic | **No** — the driver computes only `P_max`, the smoothness indicator, `Z`, and functionals of them. Verified in `all_statistics`. |
| V4 | `u` outside [2, 6] | **No** — `BSM_LADDER` has exactly five rungs and no branch reads outside. |
| V5 | objects other than the two toy cells / INT-1 / ENC-B / m=4 / d_half=2 / Bfb=512 / i<j | **No** — all hash-bound constants. |
| V6 | behaviour at cryptographic `D` | **No** — and `forbidden_in_every_branch` bars asymptotic and crypto-scale claims explicitly. |
| V7 | determinism vs small-x-window confound RT049-B6 | **No** — untouched here and said to be. |
| **V8** | deep-tail-only departures | ⚠️ **The exclusion is stated too strongly.** "NEITHER FROZEN PLANT FAMILY CAN PLACE MASS THERE" is false for the smooth family (RTB-054-2). The *operative* content — no certified power against a deep-tail-only departure — is correct and if anything strengthened, but the reason given is falsified by the frozen pipeline's own output. |
| V9 | departures visible only at `u ≈ 6` | **No** — correct, and independently supported by my STRIKE-2 measurement. |
| V10 | rough-direction departures visible only via `STAT-KS-DICK` at bits 20 | **No** — correct, and true for a second reason (never reaches DET-LPF-1 detection). |
| V11 | rough-direction departures at `u = 5` | **No** — correct; top-rung shifts −0.829 and −0.462, both below the floor. |

**Nothing is silently claimed. One exclusion (V8) is over-argued in the direction of
false confidence about the apparatus's construction.**

The AP-3 sentence — *no deliverable may describe this experiment as having power
against "departures from Dickman" without naming which of S1, S2 or S3 the claim
rests on and without carrying V1 through V11* — is correct and I endorse it.

---

## 5. The rejection-versus-power distinction

The file's `validity_of_a_rejection_versus_certification_of_power` block states that a
rejection against a measured band is valid wherever it occurs, including in a
direction whose *power* is uncertified, because the band is an order statistic of a
measured null and does not depend on any plant.

**I confirm this is correct and it is an important thing to have gotten right.** The
worked example is right too: a below-band rejection of `STAT-RATE-u@u_target=5` at
both cells would fire L-3 legitimately, while V11 continues to say no rough-direction
power was certified at that rung. **A false-fire probability is a property of the
band's construction; a detection probability is a property of the plant. Conflating
them in either direction is the error, and this file does not make it.**

---

## 6. Summary

| item | ruling |
|---|---|
| DESIGN-TRAP-LPF-1 re-derived from source | **CONFIRMED**, both families, with the mass-movement region derived and measured |
| smooth family invariant in law? | **No** — `P(P_max ≤ 256)` goes 4.9e-03 → 1 |
| rough family invariant in law? | **No** — `Z < 2` unconditionally; `P(P_max ≤ Bsm)` goes `p_hat` → 0 |
| ABS-REL-LPF-1: two-sample agreement can satisfy a branch? | **No** |
| ABS-REL-LPF-1: uniform arm ever the comparison? | **No** |
| ABS-REL-LPF-1: V1 cost stated honestly? | **Yes**, but its magnitude (up to 4.6× at u = 5) is unquantified |
| S1/S2/S3 detection floors | all correct |
| per-rung certified power | **2 rungs overstated (RTB-054-1, blocking), 1 understated (RTB-054-3)** |
| V8 deep-tail exclusion | **over-argued (RTB-054-2, blocking)**; operative content correct |
| anything under V1–V11 silently claimed | **No** |
| rejection-vs-power distinction | correct and correctly stated |

**Duty 3 fails on RTB-054-1 and RTB-054-2.** Both are text defects in one YAML file,
repairable in a superseding record with no re-execution.
