# Analysis — EXP-BINSTD-ef7fa4 / H-BINSTD-770ec3

Review plan: `experiments/EXP-BINSTD-ef7fa4/review/review-plan.yaml`
(`REVIEW-BINSTD-ef7fa4-20261001`). Producer: `TASK-20261001-2fe20a`
(package tip at review start ~`874d32f99`; implementation commit
`7dc6df250`). Evidence: `EV-BINSTD-e9b8ff`. Decision:
`DEC-20261001-670969`.

Class: **structural_certificate + toy heuristic validation** (product-
space saturation table; RC-1 spurious-lift census; Frobenius-arm
preregistered null). No ECDLP attack, no break, no rho competitiveness,
no exponent-moving claim. Transfer of measured spurious factors to
deployed solving cost is an explicit non-claim (direction only).

---

## Observation

**Validity.** Eight runs, all `completed_valid`:

| Run | Stage / arm | Status | Primary metrics |
| --- | --- | --- | --- |
| `RUN-BINSTD-fd509d` | 0 | `completed_valid` | n=131 + RC-1 tables; preregistered predictions; subfield control |
| `RUN-BINSTD-a81d6f` | 1 / P2 | `completed_valid` | explicit-span dims l=4..9 all `match=true` |
| `RUN-BINSTD-864de8` | 1 / l=4 | `completed_valid` | e_pooled=875; genuine=0; e/target=17.5; lift_agreement=1.0 (vacuous) |
| `RUN-BINSTD-5a6e49` | 1 / l=5 | `completed_valid` | e_pooled=51200; genuine=0; e/target=1024; lift_agreement=1.0 (vacuous) |
| `RUN-BINSTD-0a6a59` | 1 / l=6 | `completed_valid` | e_sampled=6589; genuine=57; scaled sf≈59185; lift_agreement=1.0; 57 decomposition certs |
| `RUN-BINSTD-540b42` | 2 / random | `completed_valid` | l=4 dims sum 31; l=5 sum 37; sampled sf LB≈1066/1064; lift_agreement=1.0 |
| `RUN-BINSTD-b2950c` | 3 / Koblitz | `completed_valid` | orbit_closure_ratio_mean=1.0; dim_V=8 |
| `RUN-BINSTD-6b3f87` | 3 / ordinary | `completed_valid` | orbit_closure_ratio_mean≈0.9998 |

Manifest metrics agree with `raw-result.json` and stage YAML summaries.
`n_runs=8 ≤ maximum_runs=20`. Seed `2026092731` on Stage 1/2 inputs.
Stage 0 commit `6c0b57cb5` precedes Stage 1 commit `c0cdff68c`.
Certificate kinds are in vocabulary (`none` on metric/Stage-0 manifests;
decomposition certificates with `verified: true` live in Stage 1/2
summaries — 57 at poly l=6; 6+6 at random l=4/5). No Bedrock. Producer
and stage artifacts set `no_break_guard: true` / observations-only.

**Stage 0.** Frozen before Stage 1: `dimension-table-n131.yaml` cells
`(5,23)` sum 335 vs ml 115; `(5,28)` 405 vs 140; `(6,22)` 447 vs 132;
`(6,24)` 481 vs 144; `(8,20)` 667 vs 160 — every cell
`sum_dims > ml`. RC-1 modeled rows for l=4..9. Preregistered
predictions: contract_stated spurious log2 `{9.6,13.6,17.6}`;
arithmetic-from-dims disclosed separately. Subfield proves-too-much
control: formula scoped to polynomial-basis subspaces;
`proves_too_much: false`.

**Stage 1 (P1/P2).** P2 explicit-span dims exact for l=4..9
(MEASURED). P1: at l=4,5 genuine ordered count 0/50 →
`spurious_factor: undefined_zero_genuine`; e/target 17.5 vs heuristic
16 (l=4) and 1024 vs 1024 (l=5). At l=6 sampling
`n_samples_per_target=2^24`, censoring 0.998046875; sampled sf lower
bound ≈115.6; **scaled estimate ≈59185** (`log2≈15.85`);
`ratio_estimated_to_contract_stated≈0.298` → **within factor 4** of
`2^{17.6}`; labeled ESTIMATED not exhaustive. `lift_agreement=1.0` on
57 genuine decompositions.

**Stage 2 (P3).** Random subspaces (same seed stream): dims
`[4,10,17]` sum 31 and `[5,15,17]` sum 37 — faster growth than
poly-basis `[4,7,10]` / `[5,9,13]`. Sampled spurious LB ≫ 1 with
`lift_agreement=1.0`. `P3_ge_poly: null` because poly P1 undefined at
those l (disclosed).

**Stage 3 (P4).** Koblitz n=17 sibling: mean orbit_closure_ratio=1.0.
Ordinary RC-1 null: mean≈0.999793. `abs_diff≈2.07e-4`. Consistent
with preregistered null (no Koblitz-structure drop).

---

## Comparison

Blind re-derivation this review session (from hypothesis / specification
parameters; without reading producer implementation for the quantities):

| Quantity | Predicted / frozen | Recomputed | Match |
| --- | --- | --- | --- |
| n=131 (5,23) dims | 23,45,67,89,111 sum 335 | same | yes |
| n=131 (5,28) dims | 28,55,82,109,131 sum 405 | same | yes |
| n=131 (6,22)/(6,24)/(8,20) | as Stage-0 table | same | yes |
| RC-1 l=4..9 dims | min(k(l-1)+1,17) | same as P2 measured | yes |
| l=5 E[e/target] | 2^{27-17}=1024 | measured 1024 | yes |
| l=4 E[e/target] | 2^{21-17}=16 | measured 17.5 | ≈yes |
| l=4/5 E[genuine/50] | ≈0.26 / ≈2.08 | measured 0 / 0 | plausible / low |
| l=6 E[genuine/50] | ≈16.7 | measured 57 | same order |
| l=6 scaled sf vs 2^{17.6} | within ×4 | ratio≈0.298 | yes |
| P4 abs_diff | ~0 (null) | ≈2e-4 | yes (null) |

Subfield control: applying subspace growth formula to `V=F_q` would
falsely predict saturation — packet correctly scopes it away
(`proves_too_much: false`).

Success-criterion mapping: Stage 0 complete; P2 exact; P1 within ×4 at
**one** scoreable cell (l=6 scaled) with e-count side consistent at
l=4,5; lift_agreement=1.0; P3 direction holds, numeric P3≥P1 unscored;
P4 null. Not DO-2 (scaled sf ≫ 1). Not DO-3. Not DO-4. Not DO-5.

---

## Inference

Stages 0–3 package is **valid**. Claim A (product-space saturation /
no unknown reduction from S_m symmetrisation on polynomial-basis
subspace bases at listed ECC2K-130 balanced cells) is supported by
unconditional Stage-0 arithmetic plus exact RC-1 P2. Claim B
(Frobenius arm preregistered null / a77711 shape) holds at the n=17
Koblitz sibling vs ordinary null. HEUR-BINSTD-770ec3-H1 is
**partially** supported: e-space counts track the uniform model at
l=4,5; l=6 scaled spurious factor lies within the preregistered ×4
band of `2^{17.6}` with `lift_agreement=1.0`; ratio P1 is undefined at
l=4,5 (zero genuine). Official decision: **support** (scoped
structural certificate + partial heuristic consistency) at strength
**preliminary**. Hypothesis `approved → supported`. Experiment
`approved → analyzed`. No break / rho / exponent. No KN-FIND
(strength below replicated/strong).

---

## Limitation

- Toy tier: executable cells at n=17 only; n=131 is Stage-0 arithmetic.
- P1 ratio scoreable at only one of three l (l=6); l=4,5 genuine=0 over
  50 targets (conservation-plausible at l=4; low vs ~2 expected at l=5).
- l=6 spurious factor is a **scaled sampling estimate**, not exhaustive;
  censoring fraction ≈0.998 disclosed.
- P3≥P1 numeric comparison unscored (poly P1 undefined).
- Contract-stated spurious log2 `{9.6,13.6,17.6}` differs from exact
  arithmetic-from-dims by ~2 bits at l=4,5 (disclosed at Stage 0; primary
  band remains contract_stated).
- Manifests dirty-at-write; pooled Stage-1 metric manifests use
  `certificate.kind: none` with decomposition certs in summaries.
- Coordinator-direct PD-1; single unreplicated package.
- No transfer of measured factors to deployed attack cost; no rho /
  exponent / break claim.
