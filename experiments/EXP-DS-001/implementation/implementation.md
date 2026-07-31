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
