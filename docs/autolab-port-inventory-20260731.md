# Autolab → crypto-autoresearcher port inventory (2026-07-31)

Source: `/Volumes/Volume/autolab` @ `dca04ac33e9ffcfc51edb3ae7e7bd558b1962d95`
Port tag: `autolab-port-20260731`
Tool: `tools/port_autolab_experiments.py`

## Ported

Total EXP packages: **84**

### ALPF (32)

| EXP | Source | Finding |
|---|---|---|
| `EXP-ALPF-001` | `round001_exp1_firstfall` | d_ff(symmetric prime-field Semaev) stays bounded (flat) across >=3 sizes for fixed m, strictly below D_reg |
| `EXP-ALPF-002` | `round002_exp002_m3_firstfall` | **Seed:** 42 **Date:** 2026-05-30 20:14 **Verdict:** FAILED (NEGATIVE RESULT) |
| `EXP-ALPF-003` | `round002_exp003_multitarget` | **Category**: 8 AMORTIZATION — NOT an ECDLP exponent break |
| `EXP-ALPF-004` | `round003_exp003b_multitarget` | 8 AMORTIZATION (not an ECDLP exponent break) |
| `EXP-ALPF-005` | `round003_exp004_firstfall_reps` | **Experiment:** round003-exp004 **Seed:** 42 **Date:** 2026-05-30 21:21 **Verdict:** FAILED |
| `EXP-ALPF-006` | `round004_exp005_validated_firstfall` | **Experiment:** round004-exp005 **Seed:** 42 **Date:** 2026-05-30 21:47 **Verdict:** INCONCLUSIVE |
| `EXP-ALPF-007` | `round004_exp006_ratmap_pullback` | INCONCLUSIVE -- meter not validated; 'no early fall' results cannot be promoted to NEGATIVE (DEFECT-A unmet). |
| `EXP-ALPF-008` | `round004_exp007_vw_multitarget` | **Category**: 8 AMORTIZATION -- NOT an ECDLP exponent break |
| `EXP-ALPF-009` | `round005_exp008_fixeddeg_fb` | SCOPED_NEGATIVE -- d_FB fixed, D_reg fixed, BUT descent blocked |
| `EXP-ALPF-010` | `round005_exp009_crossbred` | POTENTIAL SURVIVOR -- crossbred field-op cost within 10x of rho on >=1 verified cell. FLAG: extrapolate size trend befor |
| `EXP-ALPF-011` | `round006_exp010_validated_resweep` | POSITIVE (SURVIVED) -- at least one PRIME-FIELD m=3 representation genuinely early-falls (d_ff < D_reg) under the valida |
| `EXP-ALPF-012` | `round006_exp011_binary_fppr` | Binary FPPR early fall reproduced: d_ff < D_reg. Meter calibrated at large-degree Semaev profile. PO-002 met. |
| `EXP-ALPF-013` | `round007_exp012_localization_gate` | Claim label: RESTRICTED THEOREM (gate is a correct, discriminating localization test |
| `EXP-ALPF-014` | `round007_exp013_posc_anchor` | **Experiment**: EXP-013 **Round**: 007 **Timestamp**: 2026-05-31 00:33:32 |
| `EXP-ALPF-015` | `round007_exp014_binary_fppr_corrected` | Binary FPPR gated meter fires: d_ff<D_reg AND gate passes (firing syzygy involves S3 leading form) in at least one cell  |
| `EXP-ALPF-016` | `round008_exp015_m4_semaev_gated` | Round 008. Seed 42. Timestamp 2026-05-31 00:54:53. |
| `EXP-ALPF-017` | `round008_exp016_efp_fixeddeg_fb` | NEGATIVE RESULT (SCOPED): No E(F_p)-native fixed-degree membership condition yields (i) d fixed + /FB/-independent, (ii) |
| `EXP-ALPF-018` | `round009_exp017_abelian_surface` | **Round** 9 **Role** Experiment-Engineer **Timestamp** 2026-05-31 |
| `EXP-ALPF-019` | `round009_exp018_vw_optimal_fleet` | **Category**: 8 AMORTIZATION (H11) + 9 CONSTANT-FACTOR (H09)  NOT an ECDLP exponent break |
| `EXP-ALPF-020` | `round010_exp020_crossbred_m4` | `meter_self_validated = True` |
| `EXP-ALPF-021` | `round011_exp021_crossbred_m4_ering` | Round 11. Semaev S5 (m=4) index-calculus decomposition system in |
| `EXP-ALPF-022` | `round011_exp022_solvegate_ic_vs_rho` | / bits / p / n_bits / /FB/ / #rel / P_rel / ops/attempt / IC_coll / IC_la / IC_desc / IC_total / rho / IC/rho / k_verifi |
| `EXP-ALPF-023` | `round012_exp028_theta_kummer_surface` | **The last un-probed H14 intrinsic representation** (round-10 high-risk direction). |
| `EXP-ALPF-024` | `round013_exp029b_bsmooth_psin_fb` | FB non-empty (escapes NR-021 cardinality barrier) but the subgroup-information barrier holds: n-torsion DLogs are all mu |
| `EXP-ALPF-025` | `round015_exp030b_theta_redo` | Round 15. Experiment-engineer. Bounded redo of the round-13 EXP-030 measurement |
| `EXP-ALPF-026` | `round015_exp031_torus_semaev` | Round 15. Last genuinely-novel algebra lever in the named queue. |
| `EXP-ALPF-027` | `round015_exp032_symbolic_s5_ering` | - POS-A: {'fires': False, 'gate_meaningful': False, 'd_ff': None, 'D_reg': 4, 'expect_fire': True, 'expect_gate_meaningf |
| `EXP-ALPF-028` | `round017_exp033_precomputed_dp_rho` | Status: OBSERVATION / TOY-EVIDENCE / HEURISTIC. |
| `EXP-ALPF-029` | `round018_T2_isogeny_gatedmeter` | No narrative finding recorded; source result artifact carries fields: partA_topform_invariant, partB_distinct_maxGBdeg,  |
| `EXP-ALPF-030` | `round019_PO009prime` | No narrative finding recorded; source result artifact carries fields: control_has_resolution, falsified, rows, same_orde |
| `EXP-ALPF-031` | `round019b_ering_sweep` | No narrative finding recorded; source result artifact carries fields: any_gate_meaningful, pos_control_fired, rows, star |
| `EXP-ALPF-032` | `round020_solvegate` | `round020_solvegate_contract.md`. Reproduction: `round020_solvegate_ic_vs_rho.sage` (+ `.log`, `_result.json`). |

### ALBIN (11)

| EXP | Source | Finding |
|---|---|---|
| `EXP-ALBIN-001` | `bin_exp001` | **Completion:** 5 of 6 planned cells completed; the 6th cell (n=11, m=3) was KILLED after ~16 min (expensive S₄ resultan |
| `EXP-ALBIN-002` | `bin_exp002` | / n / nvars / genuine maxdeg / genuine consistent / genuine #sols / control maxdeg / control #sols / DISCRIMINATES / rho |
| `EXP-ALBIN-003` | `bin_exp003` | - **m=3** (first non-degenerate arity — m=2 linearizes at degree ≤2 and cannot show the FPPR effect). |
| `EXP-ALBIN-004` | `bin_exp004` | / n / nvars / \/FB\/ / descended deg / genuine solving degree / consistent / real_sol_satisfies / GB secs / status / |
| `EXP-ALBIN-005` | `bin_exp005` | For each n, build an ordinary E/F_{2^n}, **measure the EXACT factor-base size** /FB/ = #{points with x-coordinate in an  |
| `EXP-ALBIN-006` | `bin_exp006` | BIN-NR-003 (capstone) identified the /FB/²≈2^{2n/3} sparse-linear-algebra stage as the obstruction for fixed m=3. The Pe |
| `EXP-ALBIN-007` | `bin_exp007` | A working, validated WDSat-style SAT harness for binary Semaev point decomposition: |
| `EXP-ALBIN-008` | `bin_exp008` | Per `research/proof_obligation_binary_solving_degree.md`, PO-BIN-001(a) asks: **at FIXED arity m, is the solving degree  |
| `EXP-ALBIN-009` | `bin_exp009` | m=4 D_solv was blocked in BIN-EXP-008 by the `S5.subs` symbolic-descent explosion (S₅ = degree 32, per-variable degree 8 |
| `EXP-ALBIN-010` | `bin_exp010` | Get the third diagonal point D_solv(m=5) to test the BIN-OBS-007 law D_solv ≈ m(m−1)+O(1) (predicting ≈20 at m=5). Enabl |
| `EXP-ALBIN-011` | `bin_exp011` | BIN-NR-003 measured the IC/rho cost gap at FIXED m=3 (gap grows ~n/6) — but BIN-OBS-009 showed that misrepresents the Pe |

### ALISO (38)

| EXP | Source | Finding |
|---|---|---|
| `EXP-ALISO-001` | `p1486_degree_first_hecke_probe` | TOY-EVIDENCE / MODEL-BOUND / ORACLE-ONLY |
| `EXP-ALISO-002` | `p1486_degree_first_hecke_verify` | PASS / NEGATIVE RESULT / TOY-EVIDENCE / MODEL-BOUND / ORACLE-ONLY |
| `EXP-ALISO-003` | `p1486_frobenius_midpoint_sweep` | RESTRICTED-THEOREM FAMILY EVIDENCE / TOY / MODEL-BOUND / NO GENERAL COMPLEXITY CLAIM |
| `EXP-ALISO-004` | `p1486_frobenius_midpoint_sweep_verify` | INDEPENDENTLY-REPLAYED THREE-FAMILY TOY EVIDENCE / MODEL-BOUND / NO GENERAL COMPLEXITY CLAIM |
| `EXP-ALISO-005` | `p1486_frobenius_midpoint_verify` | INDEPENDENTLY-REPLAYED TOY EVIDENCE / MODEL-BOUND / NO GENERAL COMPLEXITY CLAIM |
| `EXP-ALISO-006` | `p1486_hecke_degree_pair_support_probe` | TOY-EVIDENCE / EXACT SUPPORT ENUMERATION / MODEL-BOUND / SUPPORT-PRIMITIVE NOT IMPLEMENTED |
| `EXP-ALISO-007` | `p1486_hecke_degree_pair_support_verify` | TOY-EVIDENCE / EXACT SUPPORT ENUMERATION / MODEL-BOUND / INDEPENDENT VERIFICATION |
| `EXP-ALISO-008` | `p1486_hecke_krylov_probe` | TOY-EVIDENCE / FULL-GRAPH ORACLE / MODEL-BOUND / ALGORITHM FALSE |
| `EXP-ALISO-009` | `p1486_hecke_support_cost_probe` | ANALYTIC QUERY SIGNAL / STANDARD-CIRCUIT SCOPED NEGATIVE / TOY OPERATION PROXIES |
| `EXP-ALISO-010` | `p1486_parity_center_smoothness_probe` | HEURISTIC DISTRIBUTION EVIDENCE / TOY / MODEL-BOUND / NO GENERAL COMPLEXITY CLAIM |
| `EXP-ALISO-011` | `p1486_parity_center_smoothness_verify` | INDEPENDENTLY-VERIFIED EXACT POPULATIONS AND TOY DISTRIBUTIONAL EVIDENCE / REGISTERED TREND FAILS / MODEL-BOUND / NO GEN |
| `EXP-ALISO-012` | `p1486_quantum_aggregate_oracle_probe` | TOY ORACLE-REDUCTION EVIDENCE / NOT A QUANTUM SIMULATION / NO GATE-COMPLEXITY CLAIM |
| `EXP-ALISO-013` | `p1486_quantum_cost_accounting_verify` | No narrative finding recorded; source result artifact carries fields: all_pass, artifact_hashes, grid, identity_checks,  |
| `EXP-ALISO-014` | `p1243_auxiliary_discriminant_search` |     Mac OS X            	   2  �     �   |
| `EXP-ALISO-015` | `p1243_auxiliary_four_line_descent` |     Mac OS X            	   2  �     �   |
| `EXP-ALISO-016` | `p1243_auxiliary_geometric_principalization` |     Mac OS X            	   2  �     �   |
| `EXP-ALISO-017` | `p1243_auxiliary_lattice_kani` |     Mac OS X            	   2  �     �   |
| `EXP-ALISO-018` | `p1243_auxiliary_orientation_eigenline` |     Mac OS X            	   2  �     �   |
| `EXP-ALISO-019` | `p1243_auxiliary_principalization` |     Mac OS X            	   2  �     �   |
| `EXP-ALISO-020` | `p1243_auxiliary_principalized_lattice` |     Mac OS X            	   2  �     �   |
| `EXP-ALISO-021` | `p1243_auxiliary_target_branch` |     Mac OS X            	   2  �     �   |
| `EXP-ALISO-022` | `p1243_ordinary_transverse_field_probe` | ORDINARY TOY-EVIDENCE / FIELD-ACCOUNTING CONTROL / NO KANI RECONSTRUCTION |
| `EXP-ALISO-023` | `p1243_parity_repair_dominance` |     Mac OS X            	   2  �     �   |
| `EXP-ALISO-024` | `p1243_parity_repair_phase_diagram` |     Mac OS X            	   2  �     �   |
| `EXP-ALISO-025` | `p1243_parity_repaired_kani_probe` | ARITHMETIC LEMMA EVIDENCE / HEURISTIC SMOOTH SEARCH / NO KANI OR TRANSVERSE-ISOGENY IMPLEMENTATION |
| `EXP-ALISO-026` | `p1243_repaired_kani_lattice` |     Mac OS X            	   2  �     �   |
| `EXP-ALISO-027` | `p1243_transverse_auxiliary_probe` | TOY GEOMETRIC EVIDENCE / FULL RATIONAL TORSION / NO KANI RECONSTRUCTION |
| `EXP-ALISO-028` | `iso_genus_filtered_crater_ancestor` | OBSERVATION / CURVE-LEVEL TOY-EVIDENCE / GENUS-FILTERED CANDIDATE REDUCTION |
| `EXP-ALISO-029` | `iso_genus_filtered_crater_sweep` | OBSERVATION / MULTI-DISCRIMINANT CURVE-LEVEL TOY-EVIDENCE |
| `EXP-ALISO-030` | `iso_ascending_prime_power_consensus_v10` | HYPOTHESIS |
| `EXP-ALISO-031` | `iso_ascending_prime_power_consensus_v11` | HYPOTHESIS |
| `EXP-ALISO-032` | `p1486_degree_first_hecke_probe_result_v2` | TOY-EVIDENCE / MODEL-BOUND / ORACLE-ONLY |
| `EXP-ALISO-033` | `p1486_degree_first_hecke_verify_result_v2` | PASS / NEGATIVE RESULT / TOY-EVIDENCE / MODEL-BOUND / ORACLE-ONLY |
| `EXP-ALISO-034` | `p1486_frobenius_midpoint_probe_result_v1` | No narrative finding recorded in the source result artifacts. |
| `EXP-ALISO-035` | `p1486_frobenius_midpoint_probe_result_v2` | No narrative finding recorded in the source result artifacts. |
| `EXP-ALISO-036` | `p1486_hecke_degree_pair_support_verify_result_v2` | No narrative finding recorded in the source result artifacts. |
| `EXP-ALISO-037` | `p1486_hecke_degree_pair_support_verify_result_v3` | No narrative finding recorded in the source result artifacts. |
| `EXP-ALISO-038` | `p1486_quantum_aggregate_oracle_probe_result_v1` | No narrative finding recorded in the source result artifacts. |

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

## Verifying this port

Needs no Autolab checkout. Recomputes each package's artifact list, count
and per-file sha256 from the files it ships, and compares them against
`implementation.md`, `manifest.yaml`, `raw-result.json` and this manifest:

```bash
python3 tools/port_autolab_experiments.py --verify
```

`--verify --reconcile` rewrites those derived fields from the archive.
It never edits an archived source artifact.

## How to extend

Porting needs the source tree. `inputs/refs` is a documentation mirror and
holds no result artifacts, so point `AUTOLAB_ROOT` at a full checkout at the
pinned commit; the tool refuses to run against a partial source.

```bash
AUTOLAB_ROOT=/path/to/autolab python3 tools/port_autolab_experiments.py
python3 tools/port_autolab_experiments.py --verify
python3 tools/validate_ledger.py
```

