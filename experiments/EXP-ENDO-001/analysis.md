# EXP-ENDO-001 analysis (executor observations only)

Protocol: experiments/EXP-ENDO-001/specification.yaml (frozen v1). 12 planned runs executed under TASK-20260727-002. This document reports measurements and comparisons against the frozen thresholds only; it makes no support/refute claim about H-ENDO-001 (that transition belongs to the Coordinator).

## 1 Observation

### Displacement rank alpha per instance/arm (over F_n, exact GE)

| cell | arm | R | B | alpha | alpha/min(R,B) | residual ||M Phi-Phi M||_0 |
|---|---|---|---|---|---|---|
| j0-16:phi_invariant | structured | 231 | 231 | 0 | 0.0000 | 0 |
| j0-16:random_baseline | random | 231 | 231 | 229 | 0.9913 | - |
| j0-20:phi_invariant | structured | 915 | 915 | 0 | 0.0000 | 0 |
| j0-20:random_baseline | random | 915 | 915 | 908 | 0.9923 | - |
| j0-24:phi_invariant | structured | 1659 | 1659 | 0 | 0.0000 | 0 |
| j0-24:random_baseline | random | 1659 | 1659 | 1652 | 0.9958 | - |
| j1728-16:phi_invariant | structured | 164 | 164 | 0 | 0.0000 | 0 |
| j1728-16:random_baseline | random | 164 | 164 | 161 | 0.9817 | - |
| j1728-20:phi_invariant | structured | 648 | 648 | 0 | 0.0000 | 0 |
| j1728-20:random_baseline | random | 648 | 648 | 647 | 0.9985 | - |
| j1728-24:phi_invariant | structured | 1660 | 1660 | 0 | 0.0000 | 0 |
| j1728-24:random_baseline | random | 1660 | 1660 | 1657 | 0.9982 | - |
| generic-16:negation_orbit_generic | structured | 134 | 134 | 0 | 0.0000 | 0 |
| generic-16:random_baseline | random | 134 | 134 | 133 | 0.9925 | - |
| generic-20:negation_orbit_generic | structured | 374 | 374 | 0 | 0.0000 | 0 |
| generic-20:random_baseline | random | 374 | 374 | 373 | 0.9973 | - |
| generic-24:negation_orbit_generic | structured | 3318 | 3318 | 0 | 0.0000 | 0 |
| generic-24:random_baseline | random | 3318 | 3318 | 3310 | 0.9976 | - |
| j0-16:phi_invariant (ablated) | phi-matrix, random shift | 231 | 231 | 227 | 0.9827 | - |
| j0-20:phi_invariant (ablated) | phi-matrix, random shift | 915 | 915 | 903 | 0.9869 | - |
| j0-24:phi_invariant (ablated) | phi-matrix, random shift | 1659 | 1659 | 1655 | 0.9976 | - |
| j1728-16:phi_invariant (ablated) | phi-matrix, random shift | 164 | 164 | 161 | 0.9817 | - |
| j1728-20:phi_invariant (ablated) | phi-matrix, random shift | 648 | 648 | 647 | 0.9985 | - |
| j1728-24:phi_invariant (ablated) | phi-matrix, random shift | 1660 | 1660 | 1655 | 0.9970 | - |
| j0-20:ap_benchmark | AP (EV-STR-001 protocol) | - | 914 | 717 | 0.7845 | - |
| j1728-20:ap_benchmark | AP (EV-STR-001 protocol) | - | 648 | 504 | 0.7778 | - |
| generic-20:ap_benchmark | AP (EV-STR-001 protocol) | - | 374 | 296 | 0.7914 | - |

### Hit rates and relation-density penalty (200 decomposition tests/arm/cell)

| cell | structured rate [Wilson95] | random rate [Wilson95] | penalty rand/phi | B/alpha threshold |
|---|---|---|---|---|
| j0-16 | 1.0000 [0.9811539940816791, 1.0] | 1.0000 [0.9811539940816791, 1.0] | 1.0000 | infinite (alpha=0) |
| j0-20 | 1.0000 [0.9811539940816791, 1.0] | 1.0000 [0.9811539940816791, 1.0] | 1.0000 | infinite (alpha=0) |
| j0-24 | 1.0000 [0.9811539940816791, 1.0] | 1.0000 [0.9811539940816791, 1.0] | 1.0000 | infinite (alpha=0) |
| j1728-16 | 1.0000 [0.9811539940816791, 1.0] | 1.0000 [0.9811539940816791, 1.0] | 1.0000 | infinite (alpha=0) |
| j1728-20 | 1.0000 [0.9811539940816791, 1.0] | 1.0000 [0.9811539940816791, 1.0] | 1.0000 | infinite (alpha=0) |
| j1728-24 | 1.0000 [0.9811539940816791, 1.0] | 1.0000 [0.9811539940816791, 1.0] | 1.0000 | infinite (alpha=0) |
| generic-16 | 1.0000 [0.9811539940816791, 1.0] | 1.0000 [0.9811539940816791, 1.0] | 1.0000 | infinite (alpha=0) |
| generic-20 | 1.0000 [0.9811539940816791, 1.0] | 1.0000 [0.9811539940816791, 1.0] | 1.0000 | infinite (alpha=0) |
| generic-24 | 1.0000 [0.9811539940816791, 1.0] | 1.0000 [0.9811539940816791, 1.0] | 1.0000 | infinite (alpha=0) |

### AP benchmark (20-bit cells, EV-STR-001 protocol)

- j0-20: AP supply 14935 (supply/B 16.34), yield penalty C(B,3)/supply 8492.9, x-wise hit rate 0.1600 vs random 1.0000 (gap 6.2x)
- j1728-20: AP supply 9928 (supply/B 15.32), yield penalty C(B,3)/supply 4546.7, x-wise hit rate 0.1100 vs random 1.0000 (gap 9.1x)
- generic-20: AP supply 5849 (supply/B 15.64), yield penalty C(B,3)/supply 1478.7, x-wise hit rate 0.0550 vs random 1.0000 (gap 18.2x)

### Wiedemann calibration (largest B per family, verified solves)

- j0-24:phi_invariant: B=1659, converged=True, measured/model (matvec ops)=1.404, (total ops)=2.474, structured/Wiedemann model ratio=0, calibrated=0
- j1728-24:phi_invariant: B=1660, converged=True, measured/model (matvec ops)=1.396, (total ops)=2.458, structured/Wiedemann model ratio=0, calibrated=0
- generic-24:negation_orbit_generic: B=3318, converged=True, measured/model (matvec ops)=1.387, (total ops)=2.440, structured/Wiedemann model ratio=0, calibrated=0

### Fully-charged totals vs measured rho (group-operation equivalents)

- j0-16 structured: total 1.25e+05 group-ops vs rho median 2231 (ratio 55.8)
- j0-16 random_baseline: total 1.25e+05 group-ops vs rho median 2231 (ratio 55.8)
- j0-20 structured: total 1.39e+06 group-ops vs rho median 4716 (ratio 296)
- j0-20 random_baseline: total 1.39e+06 group-ops vs rho median 4716 (ratio 296)
- j0-24 structured: total 4.32e+06 group-ops vs rho median 6532 (ratio 662)
- j0-24 random_baseline: total 4.32e+06 group-ops vs rho median 6532 (ratio 662)
- j1728-16 structured: total 7.31e+04 group-ops vs rho median 1886 (ratio 38.7)
- j1728-16 random_baseline: total 7.31e+04 group-ops vs rho median 1886 (ratio 38.7)
- j1728-20 structured: total 7.4e+05 group-ops vs rho median 3855 (ratio 192)
- j1728-20 random_baseline: total 7.4e+05 group-ops vs rho median 3855 (ratio 192)
- j1728-24 structured: total 4.33e+06 group-ops vs rho median 6741 (ratio 642)
- j1728-24 random_baseline: total 4.33e+06 group-ops vs rho median 6741 (ratio 642)
- generic-16 structured: total 6.05e+04 group-ops vs rho median 1720 (ratio 35.2)
- generic-16 random_baseline: total 6.05e+04 group-ops vs rho median 1720 (ratio 35.2)
- generic-20 structured: total 3.2e+05 group-ops vs rho median 2824 (ratio 113)
- generic-20 random_baseline: total 3.2e+05 group-ops vs rho median 2824 (ratio 113)
- generic-24 structured: total 1.66e+07 group-ops vs rho median 11738 (ratio 1.41e+03)
- generic-24 random_baseline: total 1.66e+07 group-ops vs rho median 11738 (ratio 1.41e+03)

## 2 Comparison vs frozen thresholds (measured values only)

```json
{
 "C1_clauses": {
  "alpha_phi<=r on >=4/6 GLV instances": {
   "measured": "6/6",
   "threshold": ">=4/6"
  },
  "at least one instance of each family with alpha<=r": {
   "measured": {
    "j0": true,
    "j1728": true
   },
   "threshold": "both families"
  },
  "complete separation alpha<=r<0.5*min(R,B)<=alpha_rand on those instances": {
   "measured": "6/6",
   "threshold": ">=4/6"
  },
  "zero unexplained commutation residuals": {
   "measured": 0,
   "threshold": 0
  },
  "generic arm alpha_neg<=2": {
   "measured": {
    "generic-16:negation_orbit_generic": 0,
    "generic-20:negation_orbit_generic": 0,
    "generic-24:negation_orbit_generic": 0
   },
   "threshold": "<=2 (prediction, not a gate)"
  }
 },
 "C2_clauses": {
  "median GLV penalty < B/alpha": {
   "measured": 1.0,
   "per_cell": {
    "j0-16": {
     "penalty": 1.0,
     "B_over_alpha": null,
     "below": true
    },
    "j0-20": {
     "penalty": 1.0,
     "B_over_alpha": null,
     "below": true
    },
    "j0-24": {
     "penalty": 1.0,
     "B_over_alpha": null,
     "below": true
    },
    "j1728-16": {
     "penalty": 1.0,
     "B_over_alpha": null,
     "below": true
    },
    "j1728-20": {
     "penalty": 1.0,
     "B_over_alpha": null,
     "below": true
    },
    "j1728-24": {
     "penalty": 1.0,
     "B_over_alpha": null,
     "below": true
    }
   },
   "threshold": "penalty < B/alpha per cell"
  },
  "calibrated model ratio <= 0.5 at largest B on >=4/6 GLV": {
   "measured": {
    "j0-24:phi_invariant": 0.0,
    "j1728-24:phi_invariant": 0.0
   },
   "threshold": "<=0.5"
  }
 },
 "control_gates": {
  "CTRL-RANDOM-BASELINE median alpha_rand/min(R,B)>=0.5": {
   "measured": 0.9957805907172996
  },
  "CTRL-PHI-ABLATION median ablated/min>=0.5": {
   "measured": 0.9919365988544342
  },
  "CTRL-AP-BENCHMARK alpha_AP>=0.5*min + supply-side penalty": {
   "measured": {
    "j0-20:ap_benchmark": {
     "alpha_over_min": 0.7844638949671773,
     "yield_penalty": 8492.886776029462
    },
    "j1728-20:ap_benchmark": {
     "alpha_over_min": 0.7777777777777778,
     "yield_penalty": 4546.726027397261
    },
    "generic-20:ap_benchmark": {
     "alpha_over_min": 0.7914438502673797,
     "yield_penalty": 1478.7355103436485
    }
   }
  },
  "CTRL-NON-GLV-ARM executed and comparable": {
   "measured": {
    "generic-16:negation_orbit_generic": 0,
    "generic-20:negation_orbit_generic": 0,
    "generic-24:negation_orbit_generic": 0
   }
  },
  "CTRL-WIEDEMANN-CALIBRATION median in [0.5,2]": {
   "measured": 1.3957831325301204
  },
  "CTRL-MATCHED-RHO-BSGS measured": {
   "measured": "rho/BSGS medians recorded per cell (see RUN-ENDO-011)"
  }
 }
}
```

## 3 Limitation

- Toy scale only (16-24-bit prime fields, B <= ~4100, GLV families j=0/j=1728 + one generic arm). No statement above claim_tier toy; nothing is implied for crypto-scale or generic curves.
- The structured-solve advantage is model-evaluated (alpha^2*B*ceil(log2 B)) with the Wiedemann side calibrated by verified solves; it is not a measured superfast solve.
- Relation matrices are assembled from enumeration-harvested relations with orbit closure by construction; the displacement measurement verifies the invariance exactly (it does not by itself prove the mechanism at other scales).
- Hit rates near 1.0 on both structured and random arms at these sizes make the penalty measurement a near-census of the tested distribution; wider-aperture regimes are untested.
