# Analysis — Autolab prime-field: round010_exp020_crossbred_m4

## Observation
{'meter_self_validated': True, 'meter_detail': {'POS_A': {'d_ff': 4, 'D_reg': None, 'fires': False}, 'NEG_1': {'fires': False}, 'NEG_2': {'fires': False}, 'ering_m3': {'fires': True, 'gate_passes': False, 'gate_meaningful': False}, 'POSC_weil': {'fires': True, 'gate_passes': True, 'gate_meaningful': True}, 'criterion': 'POS-A d_ff=4; NEGs quiet; e-ring fires-but-not-meaningful; POS-C gate_meaningful'}, 'any_admissible_below_Dreg': False, 'any_crossbred_beats_rho_end2end': False, 'verdict': 'fail

Source excerpt / raw summary:

```
# EXP-020 - Crossbred/XL admissible (D,k) frontier, m=4 Semaev S5 x-ring

Seed: 42.  m=4, n=4 free unknowns (x4 = x(R) constant).  Reduced surrogate Semaev degree d_S_reduced=2 for EXACT Macaulay algebra; symbolic Semaev per-var degree = 2^(m-1) = 8.

## Meter self-validation (MANDATORY)

`meter_self_validated = True`

```json
{
  "POS_A": {
    "d_ff": 4,
    "D_reg": null,
    "fires": false
  },
  "NEG_1": {
    "fires": false
  },
  "NEG_2": {
    "fires": false
  },
  "ering_m3": {
    "fires": true,
    "gate_passes": false,
    "gate_meaningful": false
  },
  "POSC_weil": {
    "fires": true,
    "gate_passes": true,
    "gate_meaningful": true
  },
  "criterion": "POS-A d_ff=4; NEGs quiet; e-ring fires-but-not-meaningful; POS-C gate_meaningful"
}
```

## Field-op conversion (stated)

- **rho**: 0.886*sqrt(p)*C_grp, C_grp=12 field-mults/group-op
- **crossbred_per_solve**: Ncols(D)^omega, omega=2.807 (Strassen)
- **crossbred_enum**: FB-enum d_FB^(n-k) [primary]; p^(n-k) [pessimistic]
```

## Comparison
Compared against Autolab's stated baseline (typically Pollard rho / VW / Wesolowski-class
isogeny cost, depending on topic). This import does not recompute those baselines inside
crypto-autoresearcher.

## Inference
`OBSERVATION` / `TOY-EVIDENCE` (or Autolab's original label if stronger, still not upgraded):
the Autolab package is now citeable as `EXP`+`RUN` evidence under the harness. Scientific
content remains bounded by Autolab's original scope and caveats.

## Limitation
- Not independently re-executed in this repository.
- Certificates were not re-verified; do not promote discrete-log / decomposition claims.
- Claim tier remains `toy` unless a later harness experiment re-runs with certificates.
