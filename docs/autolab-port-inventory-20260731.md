# Autolab → crypto-autoresearcher port inventory (2026-07-31)

Source: `/Volumes/SSD990/crypto-autoresearcher/inputs/refs` @ `dca04ac33e9ffcfc51edb3ae7e7bd558b1962d95`
Port tag: `autolab-port-20260731`
Tool: `tools/port_autolab_experiments.py`

## Ported

Total EXP packages: **84**

### ALPF (32)

| EXP | Source | Finding |
|---|---|---|
| `EXP-ALPF-001` | `round001_exp1_firstfall` | d_ff(symmetric prime-field Semaev) stays bounded (flat) across >=3 sizes for fixed m, strictly below D_reg |
| `EXP-ALPF-002` | `round002_exp002_m3_firstfall` | failed |
| `EXP-ALPF-003` | `round002_exp003_multitarget` | **Category**: 8 AMORTIZATION — NOT an ECDLP exponent break |
| `EXP-ALPF-004` | `round003_exp003b_multitarget` | INCONCLUSIVE |
| `EXP-ALPF-005` | `round003_exp004_firstfall_reps` | failed |
| `EXP-ALPF-006` | `round004_exp005_validated_firstfall` | inconclusive |
| `EXP-ALPF-007` | `round004_exp006_ratmap_pullback` | INCONCLUSIVE -- meter not validated; 'no early fall' results cannot be promoted to NEGATIVE (DEFECT-A unmet). |
| `EXP-ALPF-008` | `round004_exp007_vw_multitarget` | **Category**: 8 AMORTIZATION -- NOT an ECDLP exponent break |
| `EXP-ALPF-009` | `round005_exp008_fixeddeg_fb` | SCOPED_NEGATIVE -- d_FB fixed, D_reg fixed, BUT descent blocked |
| `EXP-ALPF-010` | `round005_exp009_crossbred` | POTENTIAL SURVIVOR -- crossbred field-op cost within 10x of rho on >=1 verified cell. FLAG: extrapolate size trend befor |
| `EXP-ALPF-011` | `round006_exp010_validated_resweep` | POSITIVE (SURVIVED) -- at least one PRIME-FIELD m=3 representation genuinely early-falls (d_ff < D_reg) under the valida |
| `EXP-ALPF-012` | `round006_exp011_binary_fppr` | survived |
| `EXP-ALPF-013` | `round007_exp012_localization_gate` | {'base_meter_loaded': True, 'base_self_valid': False, 'ering_powersum_fail_gate': True, 'posc_passes_gate': True, 'synth |
| `EXP-ALPF-014` | `round007_exp013_posc_anchor` | {'n_cells_attempted': 10, 'n_cells_valid': 10, 'n_fire': '10', 'n_gate_pass': '10', 'n_gate_meaningful': '10', 'n_gb_bel |
| `EXP-ALPF-015` | `round007_exp014_binary_fppr_corrected` | survived |
| `EXP-ALPF-016` | `round008_exp015_m4_semaev_gated` | failed |
| `EXP-ALPF-017` | `round008_exp016_efp_fixeddeg_fb` | NEGATIVE RESULT (SCOPED): No E(F_p)-native fixed-degree membership condition yields (i) d fixed + /FB/-independent, (ii) |
| `EXP-ALPF-018` | `round009_exp017_abelian_surface` | failed |
| `EXP-ALPF-019` | `round009_exp018_vw_optimal_fleet` | **Category**: 8 AMORTIZATION (H11) + 9 CONSTANT-FACTOR (H09) NOT an ECDLP exponent break |
| `EXP-ALPF-020` | `round010_exp020_crossbred_m4` | {'meter_self_validated': True, 'meter_detail': {'POS_A': {'d_ff': 4, 'D_reg': None, 'fires': False}, 'NEG_1': {'fires':  |
| `EXP-ALPF-021` | `round011_exp021_crossbred_m4_ering` | {'experiment': 'EXP-021 crossbred/XL m=4 e-ring admissibility', 'm': '4', 'seed': '42', 'd_S_symbolic_2^(m-1)': 8, 'd_S_ |
| `EXP-ALPF-022` | `round011_exp022_solvegate_ic_vs_rho` | **Date:** 2026-05-31 **Seed base:** 20260531 **m:** 3 |
| `EXP-ALPF-023` | `round012_exp028_theta_kummer_surface` | failed |
| `EXP-ALPF-024` | `round013_exp029b_bsmooth_psin_fb` | failed |
| `EXP-ALPF-025` | `round015_exp030b_theta_redo` | Round 15. Experiment-engineer. Bounded redo of the round-13 EXP-030 measurement |
| `EXP-ALPF-026` | `round015_exp031_torus_semaev` | inconclusive |
| `EXP-ALPF-027` | `round015_exp032_symbolic_s5_ering` | inconclusive |
| `EXP-ALPF-028` | `round017_exp033_precomputed_dp_rho` | Status: OBSERVATION / TOY-EVIDENCE / HEURISTIC. |
| `EXP-ALPF-029` | `round018_T2_isogeny_gatedmeter` | Historical Autolab experiment with retained result artifacts. |
| `EXP-ALPF-030` | `round019_PO009prime` | Historical Autolab experiment with retained result artifacts. |
| `EXP-ALPF-031` | `round019b_ering_sweep` | Historical Autolab experiment with retained result artifacts. |
| `EXP-ALPF-032` | `round020_solvegate` | {'e_ic_decomp_ops': 0.8892717464264962, 'e_rho_empirical': 0.25922705660116446, 'rho_theory_exponent': '0.50000000000000 |

### ALBIN (11)

| EXP | Source | Finding |
|---|---|---|
| `EXP-ALBIN-001` | `bin_exp001` | **Date:** 2026-05-31. Script: `bin_exp001_weil_descent_gate.sage`. Log: `bin_exp001_weil_descent_gate.log`. |
| `EXP-ALBIN-002` | `bin_exp002` | **Date:** 2026-05-31. Script: `bin_exp002_solving_degree.sage`. Log: `bin_exp002_solving_degree.log` (RC=0, 5/5 cells, R |
| `EXP-ALBIN-003` | `bin_exp003` | **Date:** 2026-05-31. Script: `bin_exp003_m3_fixed_target.sage`. Log: `bin_exp003_m3_fixed_target.log` (RC=0, 2/2 cells, |
| `EXP-ALBIN-004` | `bin_exp004` | **Date:** 2026-05-31. Script: `bin_exp004_larger_n.sage`. Log: `bin_exp004_larger_n.log`. Per-cell 240s hard timeout. |
| `EXP-ALBIN-005` | `bin_exp005` | **Date:** 2026-05-31. Script: `bin_exp005_cost_balance.sage`. Log: `bin_exp005_cost_balance.log` (RC=0, 12/12 cells, RES |
| `EXP-ALBIN-006` | `bin_exp006` | **Date:** 2026-05-31. Script: `bin_exp006_m_scaling.sage`. Log: `bin_exp006_m_scaling.log` (RC=0, 10/10 cells, RESULTS_J |
| `EXP-ALBIN-007` | `bin_exp007` | **Date:** 2026-05-31. Script: `bin_exp007_wdsat.sage` (+ extra cells `bin_exp007b_extra.log`). Solver: CryptoMiniSat via |
| `EXP-ALBIN-008` | `bin_exp008` | **Date:** 2026-05-31. Scripts: `bin_exp008_solving_degree_vs_n.sage` (system generation, PolyBoRi probe) + `msolve` 0.9. |
| `EXP-ALBIN-009` | `bin_exp009` | **Date:** 2026-06-01. Script: `bin_exp009_m4_diagonal.sage` + `msolve` 0.9.5. Log: `bin_exp009_m4_diagonal.log`. |
| `EXP-ALBIN-010` | `bin_exp010` | **Date:** 2026-06-01. Script: `bin_exp010_m5_diagonal.sage` (resultant Semaev evaluator through S₆ + eval-descent + msol |
| `EXP-ALBIN-011` | `bin_exp011` | **Date:** 2026-06-01. Script: `bin_exp011_diagonal_capstone.sage`. Log: `bin_exp011_diagonal_capstone.log`. |

### ALISO (38)

| EXP | Source | Finding |
|---|---|---|
| `EXP-ALISO-001` | `p1486_degree_first_hecke_probe` | TOY-EVIDENCE / MODEL-BOUND / ORACLE-ONLY |
| `EXP-ALISO-002` | `p1486_degree_first_hecke_verify` | PASS / NEGATIVE RESULT / TOY-EVIDENCE / MODEL-BOUND / ORACLE-ONLY |
| `EXP-ALISO-003` | `p1486_frobenius_midpoint_sweep` | Date: 2026-07-28 |
| `EXP-ALISO-004` | `p1486_frobenius_midpoint_sweep_verify` | Historical Autolab experiment with retained result artifacts. |
| `EXP-ALISO-005` | `p1486_frobenius_midpoint_verify` | Historical Autolab experiment with retained result artifacts. |
| `EXP-ALISO-006` | `p1486_hecke_degree_pair_support_probe` | Historical Autolab experiment with retained result artifacts. |
| `EXP-ALISO-007` | `p1486_hecke_degree_pair_support_verify` | Historical Autolab experiment with retained result artifacts. |
| `EXP-ALISO-008` | `p1486_hecke_krylov_probe` | Historical Autolab experiment with retained result artifacts. |
| `EXP-ALISO-009` | `p1486_hecke_support_cost_probe` | Historical Autolab experiment with retained result artifacts. |
| `EXP-ALISO-010` | `p1486_parity_center_smoothness_probe` | Historical Autolab experiment with retained result artifacts. |
| `EXP-ALISO-011` | `p1486_parity_center_smoothness_verify` | Historical Autolab experiment with retained result artifacts. |
| `EXP-ALISO-012` | `p1486_quantum_aggregate_oracle_probe` | Historical Autolab experiment with retained result artifacts. |
| `EXP-ALISO-013` | `p1486_quantum_cost_accounting_verify` | Historical Autolab experiment with retained result artifacts. |
| `EXP-ALISO-014` | `p1243_auxiliary_discriminant_search` | Date: 2026-07-29 |
| `EXP-ALISO-015` | `p1243_auxiliary_four_line_descent` | Date: 2026-07-29 |
| `EXP-ALISO-016` | `p1243_auxiliary_geometric_principalization` | Date: 2026-07-29 |
| `EXP-ALISO-017` | `p1243_auxiliary_lattice_kani` | Date: 2026-07-29 |
| `EXP-ALISO-018` | `p1243_auxiliary_orientation_eigenline` | Date: 2026-07-29 |
| `EXP-ALISO-019` | `p1243_auxiliary_principalization` | Date: 2026-07-29 |
| `EXP-ALISO-020` | `p1243_auxiliary_principalized_lattice` | Date: 2026-07-29 |
| `EXP-ALISO-021` | `p1243_auxiliary_target_branch` | Date: 2026-07-29 |
| `EXP-ALISO-022` | `p1243_ordinary_transverse_field_probe` | Historical Autolab experiment with retained result artifacts. |
| `EXP-ALISO-023` | `p1243_parity_repair_dominance` | Date: 2026-07-29 |
| `EXP-ALISO-024` | `p1243_parity_repair_phase_diagram` | Date: 2026-07-29 |
| `EXP-ALISO-025` | `p1243_parity_repaired_kani_probe` | Historical Autolab experiment with retained result artifacts. |
| `EXP-ALISO-026` | `p1243_repaired_kani_lattice` | Date: 2026-07-29 |
| `EXP-ALISO-027` | `p1243_transverse_auxiliary_probe` | Historical Autolab experiment with retained result artifacts. |
| `EXP-ALISO-028` | `iso_genus_filtered_crater_ancestor` | OBSERVATION / CURVE-LEVEL TOY-EVIDENCE / GENUS-FILTERED CANDIDATE REDUCTION |
| `EXP-ALISO-029` | `iso_genus_filtered_crater_sweep` | OBSERVATION / MULTI-DISCRIMINANT CURVE-LEVEL TOY-EVIDENCE |
| `EXP-ALISO-030` | `iso_ascending_prime_power_consensus_v10` | HYPOTHESIS |
| `EXP-ALISO-031` | `iso_ascending_prime_power_consensus_v11` | HYPOTHESIS |
| `EXP-ALISO-032` | `p1486_degree_first_hecke_probe_result_v2` | TOY-EVIDENCE / MODEL-BOUND / ORACLE-ONLY |
| `EXP-ALISO-033` | `p1486_degree_first_hecke_verify_result_v2` | PASS / NEGATIVE RESULT / TOY-EVIDENCE / MODEL-BOUND / ORACLE-ONLY |
| `EXP-ALISO-034` | `p1486_frobenius_midpoint_probe_result_v1` | Historical Autolab experiment with retained result artifacts. |
| `EXP-ALISO-035` | `p1486_frobenius_midpoint_probe_result_v2` | Historical Autolab experiment with retained result artifacts. |
| `EXP-ALISO-036` | `p1486_hecke_degree_pair_support_verify_result_v2` | Historical Autolab experiment with retained result artifacts. |
| `EXP-ALISO-037` | `p1486_hecke_degree_pair_support_verify_result_v3` | Historical Autolab experiment with retained result artifacts. |
| `EXP-ALISO-038` | `p1486_quantum_aggregate_oracle_probe_result_v1` | Historical Autolab experiment with retained result artifacts. |

### ALECF (3)

| EXP | Source | Finding |
|---|---|---|
| `EXP-ALECF-001` | `ecdsafail-challenge` | > **Goal.** Build the cheapest reversible quantum circuit that performs one |
| `EXP-ALECF-002` | `ecdsafail-frontier-jul23` | > **Goal.** Build the cheapest reversible quantum circuit that performs one |
| `EXP-ALECF-003` | `ecdsafail-q1141-old-jul24` | > **Goal.** Build the cheapest reversible quantum circuit that performs one |

## Deferred (inventoried, not EXP-packaged in this pass)

| Topic | Path / note | Why deferred |
|---|---|---|
| ECDLP index-calculus campaign monolith | `ecdlp_index_calculus_state/` | ~41k artifacts; needs curated trial extraction, not bulk EXP emission |
| ECDLP challenge notes corpus | `ecdlp-challenge/notes/` | ~1900 probe notes; select winners later |
| PO-transfer / PO96AB research program | `research/PO_transfer_* + .sage-po96ab-*` | Large theory+audit chain; many already in Autolab ledger narrative |
| SHA1-H001..H004 campaigns | `research/ + jobs/` | Custody/audit failures dominate; not clean EXP packages |
| Codex worktree 258d unique JSON dump | `/Users/adamburan/.codex/worktrees/258d/autolab` | Unique vs main; requires manual curation before harness IDs |
| ISO ascending prelaunch / intermediate versions | `experiments/ecdlp_isogeny/iso_ascending_*prelaunch*` | Intermediate negatives; finals ported preferentially |
| Root phase*.sage.py scripts without colocated results | `phase*.sage.py` | Scripts-only / historical; results live in negative_results narrative |
| ecc2k130 campaign state | `ecc2k130_campaign_state/` | Systems optimization state, not cryptanalytic EXP contract |

## Worktrees

Almost all `/Users/adamburan/.codex/worktrees/*/autolab` checkouts are sparse detached copies of `f1c783082` without unique `experiments/`. Exception:

- `258d`: ~550 unique root JSON/md probe dumps (P1553/torus/divisor ledgers) not present on Autolab main; inventoried as deferred curation, not auto-ported.

## How to extend

```bash
python3 tools/port_autolab_experiments.py
python3 tools/validate_ledger.py
```

