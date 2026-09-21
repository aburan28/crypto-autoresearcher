# Round 019 Results — PO-009′: flat-volcano m=3 Semaev sweep (T2 sub-leading falsification)

Date: 2026-06-01. Track ISO. Reproduction: `round019_PO009prime_flat_volcano_m3.sage` (+ `.log`,
`_result.json`). Sharpens round018-T2 (which used a tall-volcano toy + a non-discriminating m=2 metric).

## Setup (fixes both round018-T2 weaknesses)

- **Genuine flat volcano (f=1):** start curve E0: y²=x³+4041x+4067 / F_4099, order N=4021 (prime),
  D=t²−4p=−10155 **fundamental (conductor f=1)**, class number h(D)=**20**. So this is a faithful
  P-256 analog: the 7 collected same-order curves are **horizontal Cl(O_K)-neighbors** (pure L3
  coefficient variation, all with End=O_K), not different volcano levels.
- **m=3 with S_4 (3 coupled summand variables):** S_4 built by resultant and **VERIFIED** — vanishes
  10/10 on x-coords of real 4-tuples summing to O, nonzero 10/10 on random tuples (deg(S_4)=12).
- Metrics per curve: true degrevlex GB max degree + #solutions, and the audited leading-form gated
  meter (d_ff, D_reg, gate_meaningful). Plus a different-order negative control.

## Result — NO FALSIFICATION (invariant across the flat-volcano class)

| curve | S4 verify | maxGBdeg | #sols | found | d_ff | D_reg | gate_meaningful |
|---|---|---|---|---|---|---|---|
| E0 + ℓ=3,5,7,7,11,11 (7 same-order) | 10/10, 10/10 | **3** | **7** | True | **None** | 7 | **False** |
| CTRL (different order) | 10/10, 10/10 | 3 | 7 | True | None | 7 | False |

All 7 horizontal same-order neighbors give **identical** true solving degree (3), solution count (7),
and leading-form meter (no early fall, gate_meaningful=False). **No neighbor solves or falls strictly
lower.** Headline NOT falsified at the sub-leading level.

## Interpretation + honest caveat

**Claim (NR-034).** `NEGATIVE RESULT` (TOY-EVIDENCE; flat volcano f=1, h=20; m=3, S_4 verified). On a
genuine flat-volcano isogeny class, the x-ring 3-point Semaev decomposition exhibits **no
coefficient-level (L3) weakness**: true solving degree, solution count, and the leading-form gate
verdict are invariant across all horizontal Cl(O_K)-neighbors. Together with the **rigorous Part A**
(top_form(S_m) is (a,b)-blind, round018-T2), this closes T2 for **both** the leading-form analysis and
the true x-ring solving degree across the flat-volcano class.

**Caveat (scope, honest).** The metrics are *generic*: the different-order control matches the
same-order curves, so maxGBdeg/#sols/d_ff cannot distinguish isogenous from non-isogenous here. Thus
this rules out a weakness that would show up in the **solving degree or fall structure of the x-ring
Semaev system**, but does **not** probe a weakness visible only in a finer metric — relation-probability
constants, e-ring crossbred cutoffs below D_reg, larger |FB|/m, or a non-Semaev decomposition. That
residual is the **same open frontier as the whole prime-field campaign** (NR-019/027/032) and is **not
isogeny-specific**: the isogeny class adds no new vulnerability beyond a generic prime-field curve —
empirically consistent with Jao–Miller–Venkatesan random self-reducibility.

**What this closes / leaves open.**
- CLOSED: L1 (NR-033), L2 (f=1, vacuous), L3 leading-form (Part A) + L3 true x-ring solving degree (NR-034).
- OPEN (and not isogeny-specific): a weakness in a metric finer than x-ring solving degree — i.e. the
  campaign's standing crossbred/e-ring/large-|FB| frontier, now known to be **class-invariant at the
  leading-form level** so no isogeny neighbor can have it without a generic prime-field curve having it too.

## Net

The isogeny-transfer trapdoor is now empirically closed at every level a toy can probe (L1/L2/L3-leading/
L3-solving-degree); the only residual is the generic, non-isogeny-specific prime-field IC frontier. The
remaining theory-map avenues are the non-Semaev ones: T3 (self-pairings), T7 (Kani relation engine), T8
(vectorization atlas).

## Push #2 — e-ring crossbred-cutoff sweep across the flat-volcano class (`round019b_*`)

Reproduction: `round019b_ering_sweep_flat_volcano.sage` (+ `.log`, `_result.json`).

The e-ring m=3 model (FB membership rows sharing a common factor — the configuration most likely to
open a crossbred cutoff below D_reg; NR-027) swept across the same flat-volcano class (E0 + 7 horizontal
neighbors + different-order control):

| curves | d_ff | D_reg | fires | summation_support | gate_meaningful |
|---|---|---|---|---|---|
| all 7 same-order + control | 3 | 6 | True | **0** | **False** |
| POS-C (Weil/extension) control | 4 | 42 | True | >0 | **True** |

**Result.** `NEGATIVE RESULT`. Every flat-volcano class member has the e-ring fall at d_ff=3 with
**summation_support=0 ⇒ gate_meaningful=False** — the fall is FB-constraint-localized, not a real
decomposition cut, for the *entire class*. The POS-C positive control **fires** (gate_meaningful=True),
so this is a real negative, not a dead meter. **NR-027 (e-ring crossbred is FB-localized over prime
fields) holds class-wide**: no horizontal Cl(O_K)-neighbor opens a crossbred-weak e-ring cut the start
curve lacks. This was the one fine-metric residual of NR-034 that was directly testable, and it is
closed (at the leading-form/gate level) across the class.

## Push #3 — T3: CHM-2023 self-pairing attack does NOT apply to P-256 (two reasons)

Literature-verified (Castryck–Houben–Merz–Mula–van Buuren–Vercauteren, CRYPTO 2023, ePrint 2023/549,
Prop 4.8 + §6.1 + §7; Macula–Stange 2024; CHVW22). `NEGATIVE RESULT` (scoped).

1. **Squarefree obstruction.** The §6.1 self-pairing *attack* (recovering the secret ideal class)
   requires a **square factor m² | Δ_O**. disc(P-256) is **squarefree** (f=1; 5 distinct primes), so
   m² ∤ D for every m≥2 — the precondition fails. P-256 sits in the "(nearly) prime Δ_O" regime that
   CHM+23 §7 **explicitly identifies as immune**.
2. **Wrong problem.** Even granting a self-pairing, it breaks **vectorization** (find the ideal class
   connecting two oriented curves = isogeny-finding), **not** the EC discrete log on a single curve. It
   yields the connecting-isogeny torsion-scalar μ, giving no info on the DLP scalar k in E(F_p).

(The 2-rank-4 genus characters break *decisional* DDH for the Cl(O_K)-action — again class-group-action,
not EC-DLP.) Confirms the L4 separation concretely: the strongest class-group-action leakage attacks the
bridge, never the destination, and for P-256's squarefree D does not even reach the bridge.
