# EXP-DS-001 v2 — implementation note

**Task:** TASK-20260731-022  
**Contract:** `experiments/EXP-DS-001/specification.v2.yaml` only (v1 not executed)  
**Approval:** snapshot `65f3c82b` / DEC-20260731-003  

## What was implemented

1. **`ds001_driver.py`** — modes `impl`, `measure`, `heur`, `finalize`.
2. **`verify_certificates.py`** — independent re-check of DL / decomposition certificates using `harness.toycurve` only.
3. Shared membership backend id: `ds001-v2-point-sum-membership+charged-units-v1`.

### Real arm (Semaev-shaped)

- Factor base: deterministic `harness.semaev.build_factor_base` + sorted x-list hash recorded per cell.
- **Naive:** enumerate (m−1)-tuples over signed factor-base points; remainder membership by point equality.
- **Degree-split claw:** build half-arity claw table keyed by `SHA-256(big-endian(N))` with `N = encode_intermediate(partial_sum.x, D(bits,m))`; query complementary half; optional B-smoothness early abort.
- Relations are planted random m-sums so yield is measurable within toy budgets (membership search cost still charged).

### Null arm (`NULL-DS-RANDOM-MULTIHOMOGENEOUS` / IDEA-20260731-011)

- Full-tuple membership via Blake2b oracle at matched multidegree vector `[2]*m`.
- Half-maps use **independent** left/right keys (structure destruction): claws do not compose into membership, so split does not inherit curve MITM structure.
- `null_object_spec_hash` recorded per cell.

### Controls

- **CTRL-RHO / CTRL-BSGS** on every completed instance.
- **CTRL-NULL-PLANT** on `RUN-DS-001-impl` (artificial /4 on split cost; detection flag recorded).
- **CTRL-BACKEND-IDENTICAL** via frozen `BACKEND_ID` + sign-stability note under ±10% wall noise.
- **CTRL-CERT:** rho DL re-verified; measurement arms set `certificate.kind: none` when no DL claimed.
- Cost identities follow v2 `cost_identities` (wall × rho_gop_per_second / max(yield,1)).

### HEUR-DS-1

- Frozen `D(bits,m)=2**(bits*d_half[m])`, `u*=ln(D)/ln(B)` tabulated before sampling.
- Samples intermediate integers from half-arity maps; RATE / KS / TAIL rules applied as specified.
- Inadequate samples (`n < 1e5`) are reported missing/inadequate — never fabricated into a pass.

## Protocol deviations

1. Membership oracle is **exact point-sum verification** with a frozen charged-units proxy for backend arity cost, not a per-attempt sympy Groebner call. Rationale: sympy GB at B∈{64,128,256}, m∈{4,5} is infeasible inside the declared CPU budget; both naive and split share the same backend id and charging function.
2. Measure matrix may stop early under `resource_exhaustion` / wall budget; incomplete cells are recorded, not imputed.
3. Planted relations (random m-sums) are used so usable-relation yield is observable; this measures membership-search cost, not sparse random-target success probability.
4. Pre-snapshot regeneration: a racing write of `RUN-DS-001-measure` with `--relations 15` was replaced before TASK-023 archive by a protocol-aligned `--relations 200` matrix after fixing a `T=None` (point-at-infinity) crash in split_search. No snapshot commit had bound the relations=15 tree.
4. Primary R / R_null harvest runs with `smoothness_abort=False` so the claw table retains complements; HEUR-DS-1 smoothness/LPF sampling and RATE/KS/TAIL rules run in `RUN-DS-001-heur`.
5. Inference: requested `executor-implementation`, resolved `cursor-grok-4.5`, `fallback_used: true`.

## Out of scope (honored)

- No edits to `specification*.yaml`, amendments, H-IC-001, H-STR-002.
- No commits (snapshot is TASK-20260731-023).
- No crypto-scale or asymptotic claims in artifacts.

---

# EXP-DS-001 v2.1-ctrl — CTRL-RT025-UNPLANTED (TASK-20260731-044)

**Control protocol:** `experiments/EXP-DS-001/controls/CTRL-RT025-UNPLANTED.yaml`  
**Amendment:** `PA-DS-001-v2-ctrl-unplanted` (APPROVED at TASK-20260731-043)  
**Parent contract:** `specification.v2.yaml` (immutable; not edited)  
**Run:** `RUN-DS-001-ctrl-unplanted`

## Driver extensions (prior planted modes preserved)

1. `uniform_random_curve_target` — samples `k*P` uniformly; not a planted m-sum.
2. `execute_cell(..., target_mode=)` — `planted_m_sum` (legacy) or `unplanted_uniform_random`.
3. `--mode ctrl-unplanted` — single cell bits=20,B=64,m=4,seed=101; writes run + `results/ctrl_unplanted/`.
4. `live_plant_detect` — companion-only live `/4` on reported split costs with null echo; **no** `synth_R`/`synth_Rn` OR-path.
5. Primary R / R_null always measured with plant OFF (`plant_applied_to_primary=false`).

## Protocol adherence

- Backend id unchanged: `ds001-v2-point-sum-membership+charged-units-v1`
- `smoothness_abort=false`
- `relations_target=200` (hit; `protocol_stop=relations_target_reached`)
- `cell_wall=7200` (budget available; finished early on relations)
- Null object `NULL-DS-RANDOM-MULTIHOMOGENEOUS` required and recorded
- R-1: primary plant OFF; live plant only in `live_plant_report.json`

## Protocol deviations

1. Same membership-backend proxy as planted package (exact point-sum + charged units; not sympy GB).
2. Unplanted empirical success probability was 1.0 on both real arms at this toy cell (every uniform subgroup target found a decomposition within the scan). Recorded in `attempted_targets_*` / `success_count_*` / `empirical_success_probability_*`; not imputed from planted yield.
3. Inference: requested `executor-implementation`, resolved `cursor-grok-4.5`, `fallback_used: true`.

## Out of scope (honored)

- No edits to `specification*.yaml` or amendment after approval.
- No changes to H-IC-001 / H-STR-002; FAEST/XEDN untouched.
- No commit (TASK-20260731-045 archives).
- Does not supersede planted EV-DS-002 package.

---

# EXP-DS-001 v2.3-ctrl-theater-r2 (TASK-20260731-067)

**Amendment:** `PA-DS-001-v2-ctrl-theater-r2` (APPROVED at TASK-20260731-066, snapshot `ecf99e6e`, bind `c31e3f00`)  
**Controls:** CTRL-RT056-PLANT-CLOSED-PATH + CTRL-RT056-RHO-CALIB-AUDITED + CTRL-RT056-NULL-SPLIT-HARD-DESTROY  
**Run:** `RUN-DS-001-ctrl-theater-r2` (single cell bits=20,B=64,m=4,seed=101)  
**Parent contract:** `specification.v2.yaml` immutable (sha256 `898304bf…a5636a`)

## Driver extensions

1. `--mode ctrl-theater-r2` — packaging-like `planted_m_sum` + `null_split_mode=composing`.
2. `null_split_search_composing` — claw/join via `(enc(L)+enc(R)) mod M == enc(T)`; same `claw_key` as real arm.
3. `plant_closed_path_detect` — inject `/4` in reporting path before gate; detection_path enum `{null_gate_f2_shape}` only; `echo_entailment_check=false`.
4. `measure_rho_calib_audited` — measured real/null rho wall/gop ratios (not hardcoded 1.0).
5. `null_split_hard_destroy_report` — `composition_repaired`; `destroy_demonstrated` iff measured primary plant-OFF `R_null<0.9`; `falsifiability_failed` is terminal non-discharge (not soft PASS).

## Protocol deviations

1. Same membership-backend proxy as prior packages (exact point-sum + charged units; not sympy GB).
2. Inference: requested `executor-implementation`, resolved `cursor-grok-4.5`, `fallback_used: true`, `model_verified: false`.
3. Unauthorized `RUN-DS-001-ctrl-theater` / `results/ctrl_theater` ignored as non-binding (not copied).

## Out of scope (honored)

- No edits to `specification.v2.yaml` or rejected BATCH-021 freeze blobs.
- No H-IC-001 / H-STR-002 changes; no STR reopen; no commit (TASK-068 archives).
- Toy claim ceiling; observations only; no S1_met.

---

# EXP-DS-001 v2.4-ctrl-plant-contrast (TASK-20260731-076)

**Amendment:** `PA-DS-001-v2-ctrl-plant-contrast` (APPROVED at TASK-20260731-075, archive `badafcdf`, amend snapshot `f41fd196`)  
**Control:** CTRL-PLANT-CONTRASTIVE-F2  
**Run:** `RUN-DS-001-ctrl-plant-contrast`  
**Parent contract:** `specification.v2.yaml` immutable (sha256 `898304bf…a5636a`)

## Driver extensions

1. `--mode ctrl-plant-contrast` — ladder ≤6 cells under `null_split_mode=composing`; writes `runs/RUN-DS-001-ctrl-plant-contrast/` + `results/ctrl_plant_contrast/`.
2. `plant_contrastive_f2_detect` — live `/4` inject before gate; credit `planted_bug_detected` only if plant-OFF `null_gate_f2_shape` false AND plant-ON true; `detection_path` enum `{null_gate_f2_shape}`; `echo_entailment_check=false`.
3. Default cell 20/64/4/101 recorded first (known non-discriminative / EV-DS-006); then suggested middle_band ladder. First discriminative cell wins; else honest `contrastive_fail`.
4. Does not require rho_calib / null_split_hard_destroy theater-r2 controls.

## Observed (no interpretation)

- Cells tried: 2 (stop at first discriminative).
- Default 20/64/4/101: plant_off F2 true → not credited (no F2-on-F2).
- Selected 16/128/4/102: plant_off F2 false, plant_on F2 true → `contrastive_discriminative=true`; `planted_bug_detected=true`.
- Run status: `completed_valid` / outcome_label `discriminative_pass`.

## Protocol deviations

1. Same membership-backend proxy as prior packages (exact point-sum + charged units; not sympy GB).
2. Inference: requested `executor-implementation`, resolved `cursor-grok-4.5`, `fallback_used: true`, `model_verified: false`.
3. Unauthorized `RUN-DS-001-ctrl-theater` / `results/ctrl_theater` ignored (not copied). Prior session `6b118753` stall was infrastructure; this run owns repair.

## Out of scope (honored)

- No edits to `specification.v2.yaml`, theater-r2 controls, or rejected BATCH-021 freeze blobs.
- No H-IC-001 / H-STR-002 changes; no STR reopen; no commit (TASK-077 archives).
- Toy claim ceiling; observations only; no S1_met / support interpretation.

---

# EXP-DS-001 v2.6-ctrl-structure-null-r2 (TASK-20260731-098)

**Amendment:** `PA-DS-001-v2-ctrl-structure-null-r2` (APPROVED at TASK-20260731-097 / DEC-20260731-027, archive `b27db960`, package snapshot `0d13ad5a`)  
**Control:** CTRL-NULL-OBJECT-STRUCTURE-DIRECTION-R2  
**Run:** `RUN-DS-001-ctrl-structure-null-r2`  
**Parent contract:** `specification.v2.yaml` immutable (sha256 `898304bf…a5636a`)

## Driver extensions

1. `--mode ctrl-structure-null-r2` — primary 16/128/4/102 + optional secondary 20/64/4/101 + harden ladder ≤6 under `null_split_mode=composing`; writes `runs/RUN-DS-001-ctrl-structure-null-r2/` + `results/ctrl_structure_null_r2/`.
2. `structure_null_direction_evaluate` — records `R`, `R_null`, `advantageous_R`, `structure_null_ok`, `structure_gate_eligible`, `rising_ladder_ok`, `structure_direction_pass` / `structure_direction_fail`, `packaging_rule_ref`, `raw_costs_ref`.
3. Reuses composing null-object packaging hygiene from CTRL-RT056-NULL-SPLIT-HARD-DESTROY (join evidence probe; blob not edited).
4. Pass IFF `structure_gate_eligible` (R<0.5 AND R_null≥0.9) OR documented `rising_ladder_ok`. Else honest `structure_direction_fail` as `completed_valid` (not infrastructure failure).
5. Does not rename plant-contrast / `planted_bug_detected` as structure support. No S1_met / support / asymptotic claim.

## Archive note

- `ds001_driver.py` is git assume-unchanged (`H`). Coordinator archive TASK-099 should hash via `git hash-object experiments/EXP-DS-001/implementation/ds001_driver.py`.

## Out of scope (honored)

- No edits to abandoned BATCH-024 stubs, `specification.v2.yaml`, H-IC-001, H-STR-002, or EXP-IT paths.
- No commit (TASK-099 archives). Toy claim ceiling; observations only.

---

# EXP-DS-001 v2.7-ctrl-ci-identity (TASK-20260731-115)

**Amendment:** `PA-DS-001-v2-ctrl-ci-identity` (APPROVED at TASK-20260731-114 / DEC-20260731-033, snapshot `405b8422`, package `07232da8`)  
**Control:** CTRL-RT025-CI-IDENTITY  
**Run:** `RUN-DS-001-ctrl-ci-identity`  
**Parent contract:** `specification.v2.yaml` immutable (sha256 `898304bf…a5636a`)

## Driver extensions

1. `--mode ctrl-ci-identity` — primary cell 20/64/4/101 (+ optional secondary 16/128/4/102); writes `runs/RUN-DS-001-ctrl-ci-identity/` + `results/ctrl_ci_identity/`.
2. `bootstrap_cost_identity_ci` — bootstrap CI on yield-charged `cost_identity_R = cost_split/cost_naive` resamples (not wall-ratio proxy).
3. `evaluate_ci_identity` — records `R_point`, `ci_of_cost_identity_R`, `ci_contains_point_estimate`, `ci_identity_pass` / `ci_identity_fail`, `raw_costs_ref`, and legacy wall-proxy CI for pathology comparison.
4. Honest `ci_identity_fail` is `completed_valid` (not infrastructure failure; not lane death).

## Observed (no interpretation)

- Primary 20/64/4/101 unplanted_uniform_random: `R_point≈0.0274`, cost-identity CI `[0.0272, 0.0279]`, `ci_identity_pass=true`.
- Legacy wall-ratio proxy CI `[0.085, 0.311]` does not contain `R_point` (wrong-quantity pathology documented).
- Optional secondary cell not run; primary-only within ≤2-cell cap.

## Archive note

- `ds001_driver.py` is git assume-unchanged (`H`). Coordinator archive TASK-116 should hash via `git hash-object experiments/EXP-DS-001/implementation/ds001_driver.py` → `b8732825324b62f3204a98d27c84e16bba1ed76c`.

## Out of scope (honored)

- No edits to `specification.v2.yaml`, H-IC-001, H-STR-002, EXP-IT, or theater WIP.
- No commit (TASK-116 archives). Toy claim ceiling; observations only; no S1_met / support.

---

# EXP-DS-001 v2.8-ctrl-sparse-p-success (TASK-20260731-136)

**Amendment:** `PA-DS-001-v2-ctrl-sparse-p-success` (APPROVED at TASK-20260731-135 / DEC-20260731-038, snapshot `e3b82f7b`, package `0d6a1a94`)  
**Control:** CTRL-RT025-SPARSE-P-SUCCESS  
**Run:** `RUN-DS-001-ctrl-sparse-p-success`  
**Parent contract:** `specification.v2.yaml` immutable (sha256 `898304bf…a5636a`)

## Driver extensions

1. `--mode ctrl-sparse-p-success` — 4-cell unplanted ladder (reference 20/64/4/101 + harder 24/64, 20/32, 24/32); writes `runs/RUN-DS-001-ctrl-sparse-p-success/` + `results/ctrl_sparse_p_success/`.
2. `evaluate_sparse_p_success_cell` — per-cell `p_hat = n_usable_naive/attempts`, yield-charged `R_per_attempt`, `total_expected_cost_* = per_attempt/p_hat`, `R_total_expected`.
3. `evaluate_sparse_p_success_ladder` — aggregate `p_hat_decay_observed`, `sparse_p_success_pass` / `sparse_p_success_fail`.
4. Honest `sparse_p_success_fail` is `completed_valid` (not infrastructure failure; not lane death).

## Observed (no interpretation)

- Reference 20/64/4/101: `p_hat=1.0`, `R_per_attempt≈0.0272`, `R_total_expected≈0.0272`.
- Harder 24/64/4/101: `p_hat≈0.704`, `R_per_attempt≈0.0425` (no decay vs threshold).
- Harder 20/32/4/101: `p_hat≈0.631`, `R_per_attempt≈0.104` (no decay vs threshold).
- Harder 24/32/4/101: `p_hat≈0.0676`, `p_hat_decay_observed=true`, `R_per_attempt≈0.0763`.
- Ladder aggregate: `sparse_p_success_pass=true`, `p_hat_decay_observed=true`.

## Archive note

- `ds001_driver.py` is git assume-unchanged (`H`). Coordinator archive TASK-137 should hash via `git hash-object experiments/EXP-DS-001/implementation/ds001_driver.py` → `628d81e5c56799ea5e6ad5f26ed9d9f240c8458d`.

## Out of scope (honored)

- No edits to `specification.v2.yaml`, H-IC-001, H-STR-002, EXP-IT, theater, or BATCH-027/028 paths.
- No commit (TASK-137 archives). Toy claim ceiling; observations only; no S1_met / support.

