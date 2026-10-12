# Analysis — EXP-BINSTD-5d3ec0 / H-BINSTD-4a07ff

Review plan: `experiments/EXP-BINSTD-5d3ec0/review/review-plan.yaml`
(`REVIEW-BINSTD-5d3ec0-20261001`). Producer: `TASK-20261001-eaf0c5`
(package tip at review start ~`9b66a9ee2`; implementation commit
`0f52dc598`). Evidence: `EV-BINSTD-1e1815`. Decision:
`DEC-20261001-08bcb1`.

Class: **heuristic_validation / structural_certificate** (Stage 0
arithmetic + Stage 1 collision genericity + Stage 2 HEUR-H2 escape
pricing). No ECDLP attack, no break, no rho competitiveness, no
exponent-moving claim. Scope: Stage-0 n=131 product-law arithmetic
only; executable cells at toy n=19.

---

## Observation

**Validity.** Twenty-two runs, all `completed_valid`; `invalid=[]`;
`failed=[]`; `n_runs=22 ≤ maximum_runs=40`:

| Run | Stage | Arm / role | Manifest cert | Primary metrics |
| --- | --- | --- | --- | --- |
| `RUN-BINSTD-6a2c31` | 0 | product-law + n19 order | `none` | γ13_log2≈71.011; attempts≈59.989; order=523492 |
| `RUN-BINSTD-0dea37` | 1 | koblitz w=1 l'=8 | `none` (per-seed DL) | mean=35875.74; pass=1.0 |
| `RUN-BINSTD-40ce4d` | 1 | koblitz w=1 l'=10 | `none` | mean=16507.52; pass=1.0 |
| `RUN-BINSTD-338f54` | 1 | koblitz w=1 l'=12 | `none` | mean=7836.16; pass=1.0 |
| `RUN-BINSTD-c23c45` | 1 | koblitz w=2 l'=8 | `none` | mean=30137.6; pass=1.0 |
| `RUN-BINSTD-7f876b` | 1 | koblitz w=2 l'=10 | `none` | mean=12790.76; pass=1.0 |
| `RUN-BINSTD-332c2d` | 1 | koblitz w=2 l'=12 | `none` | mean=4504.72; pass=1.0 |
| `RUN-BINSTD-06d553` | 1 | ordinary w=1 l'=8 | `none` | mean=23454.84; pass=1.0 |
| `RUN-BINSTD-0649c6` | 1 | ordinary w=1 l'=10 | `none` | mean=11722.76; pass=1.0 |
| `RUN-BINSTD-2ef3d5` | 1 | ordinary w=1 l'=12 | `none` | mean=5089.9; pass=1.0 |
| `RUN-BINSTD-15607c` | 1 | ordinary w=2 l'=8 | `none` | mean=23043.64; pass=1.0 |
| `RUN-BINSTD-c47958` | 1 | ordinary w=2 l'=10 | `none` | mean=9859.54; pass=1.0 |
| `RUN-BINSTD-0a24dd` | 1 | ordinary w=2 l'=12 | `none` | mean=4826.12; pass=1.0 |
| `RUN-BINSTD-3acf74` | 1 | relabelled w=1 l'=8 | `none` | mean=22416.72; pass=1.0 |
| `RUN-BINSTD-0fddb6` | 1 | relabelled w=1 l'=10 | `none` | mean=10946.2; pass=1.0 |
| `RUN-BINSTD-d3fe10` | 1 | relabelled w=1 l'=12 | `none` | mean=5141.46; pass=1.0 |
| `RUN-BINSTD-9a580a` | 1 | relabelled w=2 l'=8 | `none` | mean=23784.6; pass=1.0 |
| `RUN-BINSTD-cf1370` | 1 | relabelled w=2 l'=10 | `none` | mean=8933.64; pass=1.0 |
| `RUN-BINSTD-ca1217` | 1 | relabelled w=2 l'=12 | `none` | mean=5504.72; pass=1.0 |
| `RUN-BINSTD-f0e531` | 2 | coupled l'=8 | `none` | ratio_mean≈2.788; min≈2.733 |
| `RUN-BINSTD-83687b` | 2 | coupled l'=10 | `none` | ratio_mean≈2.673; min≈2.619 |
| `RUN-BINSTD-e024b1` | 2 | coupled l'=12 | `none` | ratio_mean≈2.560; min≈2.511 |

Cell-level Stage-1 manifests correctly use `certificate.kind: none`
(aggregate metric). Independent re-check of **900/900** per-seed
`certificate_dl` entries in `raw-result.json`: koblitz/ordinary
`verify_discrete_log` schoolbook pass; relabelled additive
`Q ≡ k·P (mod 523492)` pass; `k_match=true` throughout;
`certificate_pass_rate=1.0` on every cell. Seeds exactly
`2026092601..2026092650`. Manifest means agree with raw instance
arrays (0 mismatches). No Bedrock.

Stage 0 commit `8eee0ef17` (2026-10-01T19:10Z) precedes Stage 1–2
package `0f52dc598` (2026-10-01T19:19Z). Stage0 run finished
19:10:11Z; first Stage1 cell started 19:14:41Z.

**Stage 0.** Blind re-derivation (combinatorics alone, not reading
`product-law-n131.yaml` / implementation):

- `C(131,13)×2^13` → `log2 ≈ 71.01089176218689` (Δ≈0.011 from 71)
- `attempts_w13 log2 = 131 − that ≈ 59.98910823781311` (Δ≈0.011 from 60)

Both within 0.5-bit tolerance. n=19 order measured 523492 = 4×130873;
130873 prime; unique affine 2-torsion `(0,1)`; 2-Sylow cyclic;
`μ=41811` with `ord_ell(μ)=19`. Exact `|Gamma_1|=38`, `|Gamma_2|=608`
at n=19 (upper 38 / 684). Preregistered predictions frozen before
Stage 1. Measured vs modeled: Stage-0 γ/attempts columns are **modeled
arithmetic** (upper bound), not a solved ECDLP.

**Stage 1.** Collision-form DLP cost (scalar multiplications to
representative collision + solve) at n=19, 50 seeds/cell:

Blind genericity ratios (from cell means):

| w | l' | K/O | in band? | K/R | in band? |
| --- | --- | --- | --- | --- | --- |
| 1 | 8 | 1.5296 | no | 1.6004 | no |
| 1 | 10 | 1.4082 | yes | 1.5081 | no |
| 1 | 12 | 1.5396 | no | 1.5241 | no |
| 2 | 8 | 1.3078 | yes | 1.2671 | yes |
| 2 | 10 | 1.2973 | yes | 1.4318 | yes |
| 2 | 12 | 0.9334 | yes | 0.8183 | yes |

w=2 cells all inside preregistered `[0.67,1.5]`. w=1 cells are
DO-3-shaped (largest K/R≈1.60 at w=1,l'=8). Ordinary-vs-relabelled
ratios stay near 1.0 on w=1, so the excess is Koblitz-vs-both-controls.

Documented prediction-band exceptions (`mean_over_prediction < 1/1.5`
vs frozen `2^{n−l'/2}`): six cells
(ordinary w=2 l'=12; ordinary w=1 l'=12; koblitz w=2 l'=12; ordinary
w=2 l'=10; relabelled w=2 l'=10; relabelled w=1 l'=12). Success
criterion allows documented exceptions; bands not retuned.

Disclosed instrument confounders (implementation.md /
execution_report): (i) ordinary measured order `2×261823` (ell ≠
Koblitz 130873); (ii) relabelled Rep size `2^{l'}` (no trace filter)
vs thinner curve `F_{V'}` — may inflate Koblitz/relabelled ratios on
w=1.

**Stage 2.** Coupled one-hot vs summed per-pattern work
(pure-Python boolean GE pivots + ANF support, D≤4; SAT arm skipped):

Blind re-derivation from raw `targets[].ratio` (20 targets each):

| l' | mean | min | ≥1? |
| --- | --- | --- | --- |
| 8 | 2.788216 | 2.732551 | yes |
| 10 | 2.673256 | 2.619143 | yes |
| 12 | 2.560013 | 2.511219 | yes |

`DO2_triggered=false` (no cell with ratio < 0.5). Matches
`coupled-ratio-summary.yaml`. No n=131 extrapolation.

---

## Comparison

Against preregistered predictions
(`stage0/preregistered-predictions.yaml` / contract):

| Prediction | Outcome |
| --- | --- |
| Stage 0 γ13 / attempts within 0.5 bit of 71 / 60 | **Pass** (Δ≈0.011) |
| n=19 order = 4×130873 | **Pass** |
| Stage 1 Koblitz/control ratios in [0.67,1.5] on every cell | **Fail on w=1** (DO-3-shaped); **Pass on w=2** |
| Stage 1 costs within 1.5× of `2^{n−l'/2}` OR documented exception | **Pass** via documented exceptions on six cells; koblitz w=1 cells within band |
| Stage 2 ratio ≥ 1.0 on every cell (H2) | **Pass** (min≈2.51) |
| certificate_pass_rate = 1.0 | **Pass** (900/900 DL) |
| DO-2 (ratio < 0.5 at two cells) | **Not fired** |

Controls: ordinary (null, no τ) and relabelled Z/(4ℓ) are present;
ordinary–relabelled agreement near 1 argues the instrument is
internally consistent on non-Koblitz arms. Certificate vocabulary
respected (`none` at cell aggregate; `discrete_log` per seed).

vs HEUR-H1 coverage / collision band: several cells cheaper than
`2^{n−l'/2}/1.5` at toy n with large `|Gamma|` — consistent with
disclosed optimistic coverage model over-estimating when
`|Gamma|` is large relative to group order; not retuned.

vs HEUR-H2 (KN-FIND-47da4e transplant, provenance `kb` on hypothesis):
toy coupled ratios ≈2.56–2.79 sit above the independent-summand
1.00–1.47× band, in the predicted ≥1 direction under a **different
work unit** (GE+ANF, not the original instrument). Direction agrees;
magnitude not claimed transferable.

vs dominated_by / matched rho (KN-FIND-aa2efc, `kb`): Stage-0 attempts
column ≈2^60 is an **upper-bound free-oracle** figure, not a solving
cost. Enumerated collision form remains modeled
`2^{131−l'/2} ≥ 2^66` — still above matched rho ≈2^60.809. No
rho-beating claim.

---

## Inference

1. **Stage 0 arithmetic holds** (DO-4 not triggered). Product-law /
   `|Gamma_13|` upper-bound re-derivation and n=19 order check are
   valid structural certificates within the declared tolerance.

2. **Stage 1 does not license DO-1 structural_closure.** w=1
   Koblitz/control ratios leave `[0.67,1.5]` with certificates intact.
   Per distinguishable outcome DO-3, the honest reading is instrument-
   defect / repair — especially with disclosed ordinary-ell and Rep-size
   confounders — **not** a curve-structure attack advantage and **not**
   a clean reject of the Gamma_w genericity claim on this single
   unreplicated package.

3. **Stage 2 does not fire DO-2.** Under the pure-Python work unit at
   n=19, w=2, HEUR-H2’s predicted ratio ≥ 1 holds on all three l'
   cells (min≈2.51). This is a **toy, instrument-scoped** observation;
   it does not transfer to n=131 and does not authorize an escape claim.

4. **Joint decision: refine**, not support, not reject_scoped.
   Protocol success path is reachable via “documented DO-3” + Stage-2
   ratio≥1 + Stage-0 pass, but the scientific DO-1 closure reading is
   blocked until the instrument is repaired / remeasured on w=1.
   Hypothesis and experiment → `analyzed`. Strength **preliminary**
   (Coordinator-direct PD-1; single unreplicated package; DO-3
   confound). No KN-FIND.

5. **No break / rho / exponent / deployed attack.** Any such
   reading fails the proves-too-much control.

Refutation artifact basis for any adverse genericity reading:
`empirical_only` (ratio measurements), unreplicated → may support
`weaken`/`refine`, **not** `reject_scoped` (AGENTS.md /
claims-and-verification). Here the preferred map is refine (DO-3),
not weaken of the mathematical object.

---

## Limitation

- Toy tier only (n=19 executable; n=131 Stage-0 arithmetic).
- Ordinary control ell=261823 ≠ Koblitz 130873 (disclosed).
- Relabelled Rep size = `2^{l'}` thicker than curve `F_{V'}`.
- Stage-2 work unit is pure-Python GE+ANF, not SAT; optional SAT arm
  skipped — within-instrument comparison only.
- `|Gamma_13|` is an upper bound `C(131,13)2^13`, not exact enumeration.
- Six Stage-1 cells below the factor-1.5 prediction band (documented;
  optimistic H1 coverage at toy n).
- Coordinator-direct review without independent validator/red-team
  (PD-1).
- Single unreplicated Stages 0–2 package; strength preliminary.
- Solinas ≈2^5.5 constant remains `recalled` and is not used in
  measured Stage-1 units (scalar multiplications).
- No transfer of Stage-2 ratios or Stage-1 costs to deployed curves.
