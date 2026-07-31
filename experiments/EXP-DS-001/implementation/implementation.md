# EXP-DS-001 v2 — implementation note

**Task:** TASK-20260731-022  
**Contract:** `experiments/EXP-DS-001/specification.v2.yaml` only (v1 not executed)  
**Approval:** snapshot `65f3c82b` / DEC-20260731-022  

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
