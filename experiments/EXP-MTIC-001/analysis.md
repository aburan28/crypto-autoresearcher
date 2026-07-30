# EXP-MTIC-001 analysis (Executor, TASK-20260727-001, protocol v2)

Observations only. No claim about H-MTIC-001 being supported, weakened, rejected, or closed is made anywhere in this file; the decision matrix tabulates measured values and frozen-formula outcomes per accounting.

## 1 Observation

### 16-bit (N=17623, sqrt(N)=132.8)

- S_rel: 0.022336 s (censored partial: False); S_LA: 0.011281251907348633 s (mode true_rhs_maxrank_subsystem, entry status None)
- T_desc median 60.0 s over 25 attempted targets (capped 25, cancelled 25); IQR 0.0 s
- rho baseline median 1720.0 total group ops (0.0010618750238791108 s) per target
- [group_ops_rho] S=55204.8, T=9.85293e+07, K*=infinite, frontier ratio=3.04108e+16, regime: (i) K* infinite
- [group_ops_bsgs] S=10866.5, T=1.93945e+07, K*=infinite, frontier ratio=2.31934e+14, regime: (i) K* infinite
- [wall_seconds] S=0.0336173, T=60, K*=infinite, frontier ratio=3.04108e+16, regime: (i) K* infinite

### 20-bit (N=139753, sqrt(N)=373.8)

- S_rel: 0.06153 s (censored partial: False); S_LA: 0.09922385215759277 s (mode true_rhs_maxrank_subsystem, entry status None)
- T_desc median 60.0 s over 13 attempted targets (capped 13, cancelled 37); IQR 0.0 s
- rho baseline median 2893.0 total group ops (0.002031770534813404 s) per target
- [group_ops_rho] S=231980, T=8.65846e+07, K*=infinite, frontier ratio=1.24443e+16, regime: (i) K* infinite
- [group_ops_bsgs] S=228601, T=8.53232e+07, K*=infinite, frontier ratio=1.19083e+16, regime: (i) K* infinite
- [wall_seconds] S=0.160754, T=60, K*=infinite, frontier ratio=1.24443e+16, regime: (i) K* infinite

### 24-bit (N=11000719, sqrt(N)=3316.7)

- S_rel: 9.859178 s (censored partial: False); S_LA: 8.63622498512268 s (mode true_rhs_maxrank_subsystem, entry status None)
- T_desc median 60.0 s over 12 attempted targets (capped 12, cancelled 38); IQR 0.0 s
- rho baseline median 12244.0 total group ops (0.0096230624767486 s) per target
- [group_ops_rho] S=2.38658e+07, T=7.74219e+07, K*=infinite, frontier ratio=1.30042e+16, regime: (i) K* infinite
- [group_ops_bsgs] S=1.64404e+07, T=5.33333e+07, K*=infinite, frontier ratio=4.25097e+15, regime: (i) K* infinite
- [wall_seconds] S=18.4954, T=60, K*=infinite, frontier ratio=1.30042e+16, regime: (i) K* infinite

## 2 Comparison vs frozen formulas (measured values only)

```json
{
 "16": {
  "sqrt_n": 132.75164782404775,
  "N": 17623,
  "s_rel_seconds": 0.022336,
  "s_rel_censored": {
   "eval_cap_hit": false,
   "time_cap_hit": false
  },
  "s_rel_censored_partial": false,
  "s_la_seconds": 0.011281251907348633,
  "s_la_mode": "true_rhs_maxrank_subsystem",
  "s_la_entry_status": null,
  "t_desc_seconds_median": 60.0,
  "t_desc_n_attempted": 25,
  "t_desc_n_capped": 25,
  "t_desc_n_cancelled": 25,
  "t_desc_iqr_seconds": 0.0,
  "iqr_leq_median_uncensored": null,
  "n_uncensored_solves": 0,
  "iqr_note": "frozen decisiveness note requires IQR <= median among UNCENSORED solves; None when there are no uncensored solves (vacuous), in which case the capped-at-full-cap median is itself the bound per the frozen censoring rule",
  "rho_median_ops": 1720.0,
  "rho_median_seconds": 0.0010618750238791108,
  "bsgs": {
   "table_entries": 133,
   "table_memory_bytes_estimate": 15860,
   "group_operations": 223,
   "adds": 173,
   "lookups": 29,
   "memory_note": "estimate: sys.getsizeof(dict) + entries * (sizeof 2-tuple + sizeof int); labeled estimate, not exact",
   "solved": true,
   "k": 3830,
   "verified": true
  },
  "ctrl_single_target": {
   "entry_status": "measured",
   "components": {
    "s_rel_seconds": 0.022336,
    "s_la_seconds": 0.011281251907348633,
    "t_desc_median_seconds": 60.0
   },
   "group_ops_rho": {
    "ic_K1": 98584541.63289402,
    "rho_median": 1720.0,
    "ic_exceeds_rho": true
   },
   "group_ops_bsgs": {
    "ic_K1": 19405317.24554209,
    "rho_median": 1720.0,
    "ic_exceeds_rho": true
   },
   "wall_seconds": {
    "ic_K1": 60.0336190438884,
    "rho_median": 0.0010618750238791108,
    "ic_exceeds_rho": true
   },
   "holds_all_accountings": true
  },
  "accountings": {
   "group_ops_rho": {
    "S": 55204.757285992906,
    "T_desc": 98529333.87560803,
    "T_verify": 3,
    "T": 98529336.87560803,
    "sqrt_n": 132.75164782404775,
    "denominator": -98529204.1239602,
    "K_star_infinite": true,
    "K_star": "infinite",
    "frontier_product_ratio": 3.041079568202497e+16,
    "regime_i_t_desc_geq_sqrt_n": true,
    "below_frontier": false,
    "K_star_equals_one": false
   },
   "group_ops_bsgs": {
    "S": 10866.467276098101,
    "T_desc": 19394447.778265994,
    "T_verify": 3,
    "T": 19394450.778265994,
    "sqrt_n": 132.75164782404775,
    "denominator": -19394318.02661817,
    "K_star_infinite": true,
    "K_star": "infinite",
    "frontier_product_ratio": 231933513120422.97,
    "regime_i_t_desc_geq_sqrt_n": true,
    "below_frontier": false,
    "K_star_equals_one": false
   },
   "wall_seconds": {
    "S": 0.033617251907348634,
    "T_desc": 60.0,
    "T_verify": 1.7919810488820076e-06,
    "T": 60.00000179198105,
    "sqrt_n": 8.083987332644201e-05,
    "denominator": -59.99992095210772,
    "K_star_infinite": true,
    "K_star": "infinite",
    "frontier_product_ratio": 3.0410795646661204e+16,
    "regime_i_t_desc_geq_sqrt_n": true,
    "below_frontier": false,
    "K_star_equals_one": false
   },
   "calibration_rates": {
    "rho_walk_rate": 1642155.5645934672,
    "bsgs_construction_rate": 323240.79630443326
   },
   "algebraic_identity_disclosed": "wall_seconds frontier ratio equals the group_ops_rho ratio up to the T_verify conversion (3 ops native vs measured seconds; relative difference ~1e-8 at these measurements); the non-trivial audit is rho-walk vs bsgs-construction calibration constants"
  },
  "regime_per_accounting": {
   "group_ops_rho": "(i) K* infinite",
   "group_ops_bsgs": "(i) K* infinite",
   "wall_seconds": "(i) K* infinite"
  },
  "regime_stable_across_accountings": true,
  "below_frontier_observed_any_accounting": false
 },
 "20": {
  "sqrt_n": 373.8355253316624,
  "N": 139753,
  "s_rel_seconds": 0.06153,
  "s_rel_censored": {
   "eval_cap_hit": false,
   "time_cap_hit": false
  },
  "s_rel_censored_partial": false,
  "s_la_seconds": 0.09922385215759277,
  "s_la_mode": "true_rhs_maxrank_subsystem",
  "s_la_entry_status": null,
  "t_desc_seconds_median": 60.0,
  "t_desc_n_attempted": 13,
  "t_desc_n_capped": 13,
  "t_desc_n_cancelled": 37,
  "t_desc_iqr_seconds": 0.0,
  "iqr_leq_median_uncensored": null,
  "n_uncensored_solves": 0,
  "iqr_note": "frozen decisiveness note requires IQR <= median among UNCENSORED solves; None when there are no uncensored solves (vacuous), in which case the capped-at-full-cap median is itself the bound per the frozen censoring rule",
  "rho_median_ops": 2893.0,
  "rho_median_seconds": 0.002031770534813404,
  "bsgs": {
   "table_entries": 374,
   "table_memory_bytes_estimate": 49928,
   "group_operations": 588,
   "adds": 478,
   "lookups": 89,
   "memory_note": "estimate: sys.getsizeof(dict) + entries * (sizeof 2-tuple + sizeof int); labeled estimate, not exact",
   "solved": true,
   "k": 32984,
   "verified": true
  },
  "ctrl_single_target": {
   "entry_status": "measured",
   "components": {
    "s_rel_seconds": 0.06153,
    "s_la_seconds": 0.09922385215759277,
    "t_desc_median_seconds": 60.0
   },
   "group_ops_rho": {
    "ic_K1": 86816539.8795419,
    "rho_median": 2893.0,
    "ic_exceeds_rho": true
   },
   "group_ops_bsgs": {
    "ic_K1": 85551808.72480023,
    "rho_median": 2893.0,
    "ic_exceeds_rho": true
   },
   "wall_seconds": {
    "ic_K1": 60.16075589315101,
    "rho_median": 0.002031770534813404,
    "ic_exceeds_rho": true
   },
   "holds_all_accountings": true
  },
  "accountings": {
   "group_ops_rho": {
    "S": 231980.0175487256,
    "T_desc": 86584556.86199318,
    "T_verify": 3,
    "T": 86584559.86199318,
    "sqrt_n": 373.8355253316624,
    "denominator": -86584186.02646784,
    "K_star_infinite": true,
    "K_star": "infinite",
    "frontier_product_ratio": 1.2444296346751226e+16,
    "regime_i_t_desc_geq_sqrt_n": true,
    "below_frontier": false,
    "K_star_equals_one": false
   },
   "group_ops_bsgs": {
    "S": 228600.56513082416,
    "T_desc": 85323205.1596694,
    "T_verify": 3,
    "T": 85323208.1596694,
    "sqrt_n": 373.8355253316624,
    "denominator": -85322834.32414407,
    "K_star_infinite": true,
    "K_star": "infinite",
    "frontier_product_ratio": 1.1908320465686272e+16,
    "regime_i_t_desc_geq_sqrt_n": true,
    "below_frontier": false,
    "K_star_equals_one": false
   },
   "wall_seconds": {
    "S": 0.16075385215759277,
    "T_desc": 60.0,
    "T_verify": 2.040993422269821e-06,
    "T": 60.00000204099342,
    "sqrt_n": 0.00025905464360868706,
    "denominator": -59.999742986349816,
    "K_star_infinite": true,
    "K_star": "infinite",
    "frontier_product_ratio": 1.2444296331030246e+16,
    "regime_i_t_desc_geq_sqrt_n": true,
    "below_frontier": false,
    "K_star_equals_one": false
   },
   "calibration_rates": {
    "rho_walk_rate": 1443075.9476998863,
    "bsgs_construction_rate": 1422053.4193278232
   },
   "algebraic_identity_disclosed": "wall_seconds frontier ratio equals the group_ops_rho ratio up to the T_verify conversion (3 ops native vs measured seconds; relative difference ~1e-8 at these measurements); the non-trivial audit is rho-walk vs bsgs-construction calibration constants"
  },
  "regime_per_accounting": {
   "group_ops_rho": "(i) K* infinite",
   "group_ops_bsgs": "(i) K* infinite",
   "wall_seconds": "(i) K* infinite"
  },
  "regime_stable_across_accountings": true,
  "below_frontier_observed_any_accounting": false
 },
 "24": {
  "sqrt_n": 3316.733181912588,
  "N": 11000719,
  "s_rel_seconds": 9.859178,
  "s_rel_censored": {
   "eval_cap_hit": false,
   "time_cap_hit": false
  },
  "s_rel_censored_partial": false,
  "s_la_seconds": 8.63622498512268,
  "s_la_mode": "true_rhs_maxrank_subsystem",
  "s_la_entry_status": null,
  "t_desc_seconds_median": 60.0,
  "t_desc_n_attempted": 12,
  "t_desc_n_capped": 12,
  "t_desc_n_cancelled": 38,
  "t_desc_iqr_seconds": 0.0,
  "iqr_leq_median_uncensored": null,
  "n_uncensored_solves": 0,
  "iqr_note": "frozen decisiveness note requires IQR <= median among UNCENSORED solves; None when there are no uncensored solves (vacuous), in which case the capped-at-full-cap median is itself the bound per the frozen censoring rule",
  "rho_median_ops": 12244.0,
  "rho_median_seconds": 0.0096230624767486,
  "bsgs": {
   "table_entries": 3317,
   "table_memory_bytes_estimate": 426172,
   "group_operations": 9349,
   "adds": 6324,
   "lookups": 2987,
   "memory_note": "estimate: sys.getsizeof(dict) + entries * (sizeof 2-tuple + sizeof int); labeled estimate, not exact",
   "solved": true,
   "k": 9906125,
   "verified": true
  },
  "ctrl_single_target": {
   "entry_status": "measured",
   "components": {
    "s_rel_seconds": 9.859178,
    "s_la_seconds": 8.63622498512268,
    "t_desc_median_seconds": 60.0
   },
   "group_ops_rho": {
    "ic_K1": 101287654.56295614,
    "rho_median": 12244.0,
    "ic_exceeds_rho": true
   },
   "group_ops_bsgs": {
    "ic_K1": 69773693.82808639,
    "rho_median": 12244.0,
    "ic_exceeds_rho": true
   },
   "wall_seconds": {
    "ic_K1": 78.4954053186387,
    "rho_median": 0.0096230624767486,
    "ic_exceeds_rho": true
   },
   "holds_all_accountings": true
  },
  "accountings": {
   "group_ops_rho": {
    "S": 23865804.388935033,
    "T_desc": 77421847.17402111,
    "T_verify": 3,
    "T": 77421850.17402111,
    "sqrt_n": 3316.733181912588,
    "denominator": -77418533.4408392,
    "K_star_infinite": true,
    "K_star": "infinite",
    "frontier_product_ratio": 1.3004153779190902e+16,
    "regime_i_t_desc_geq_sqrt_n": true,
    "below_frontier": false,
    "K_star_equals_one": false
   },
   "group_ops_bsgs": {
    "S": 16440358.040704682,
    "T_desc": 53333332.78738171,
    "T_verify": 3,
    "T": 53333335.78738171,
    "sqrt_n": 3316.733181912588,
    "denominator": -53330019.05419979,
    "K_star_infinite": true,
    "K_star": "infinite",
    "frontier_product_ratio": 4250966632005875.0,
    "regime_i_t_desc_geq_sqrt_n": true,
    "below_frontier": false,
    "K_star_equals_one": false
   },
   "wall_seconds": {
    "S": 18.49540298512268,
    "T_desc": 60.0,
    "T_verify": 2.3335160221904516e-06,
    "T": 60.00000233351602,
    "sqrt_n": 0.002570385468425391,
    "denominator": -59.9974319480476,
    "K_star_infinite": true,
    "K_star": "infinite",
    "frontier_product_ratio": 1.3004153782914804e+16,
    "regime_i_t_desc_geq_sqrt_n": true,
    "below_frontier": false,
    "K_star_equals_one": false
   },
   "calibration_rates": {
    "rho_walk_rate": 1290364.1195670185,
    "bsgs_construction_rate": 888888.8797896951
   },
   "algebraic_identity_disclosed": "wall_seconds frontier ratio equals the group_ops_rho ratio up to the T_verify conversion (3 ops native vs measured seconds; relative difference ~1e-8 at these measurements); the non-trivial audit is rho-walk vs bsgs-construction calibration constants"
  },
  "regime_per_accounting": {
   "group_ops_rho": "(i) K* infinite",
   "group_ops_bsgs": "(i) K* infinite",
   "wall_seconds": "(i) K* infinite"
  },
  "regime_stable_across_accountings": true,
  "below_frontier_observed_any_accounting": false
 }
}
```

## 3 Ablation at 20 bits

- ablation_cbrt (B=52): T_desc median 60.0 s over 13 targets (capped 13); S_rel 0.017705 s (23296 evals); S_LA 0.0021848678588867188 s (true_rhs_full_rank); accountings recorded in run raw.json
- ablation_2_5 (B=115): T_desc median 60.0 s over 12 targets (capped 12); S_rel 0.013633 s (21735 evals); S_LA 0.009191751480102539 s (true_rhs_maxrank_subsystem); accountings recorded in run raw.json

## 4 Limitation

- Toy scale only (16-24-bit prime fields, B <= ~3400). No statement above claim_tier toy; nothing is implied for crypto-scale behavior.
- All Groebner costs are implementation-bound (sympy Buchberger proxies: wall time, basis size, max total degree; no degree-of-regularity observable). A different solver shifts absolute numbers.
- Capped solves are charged at the full 60 s cap per the frozen censoring rule; cancelled targets are recorded with the measured prefix retained.
- The wall-clock and group_ops_rho frontier ratios are identical by construction (disclosed); the non-trivial calibration audit is between the rho-walk and BSGS-construction rates.