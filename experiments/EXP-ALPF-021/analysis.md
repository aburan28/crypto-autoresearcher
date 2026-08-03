# Analysis — Autolab prime-field: round011_exp021_crossbred_m4_ering

## Observation
{'experiment': 'EXP-021 crossbred/XL m=4 e-ring admissibility', 'm': '4', 'seed': '42', 'd_S_symbolic_2^(m-1)': 8, 'd_S_ladder_ering_surrogate': ['3', '4', '5', '6', '8'], 'meter_self_validated': True, 'any_admissible_below_Dreg_ering': True, 'any_gate_meaningful_admissible': False, 'any_IC_beats_rho_end_to_end': False, 'candidate': False, 'verdict': 'failed', 'nr025_xring_baseline': 'NO admissible (D,k) with D<D_reg in x-ring (reduced surrogate)'}

Source excerpt / raw summary:

```
# EXP-021 - crossbred/XL admissible-(D,k) at m=4 in the E-RING

Round 11. Semaev S5 (m=4) index-calculus decomposition system in
elementary-symmetric (e-ring) coordinates over prime-field ECDLP toy families.
Seed 42. Extends NR-025 (x-ring crossbred negative) to the e-ring.

## Degree model (LABELED)

- Symbolic S5 per-variable x-degree: 2^(m-1) = 8 (the true object).
- E-ring surrogate top-form degree ladder d_S in [3, 4, 5, 6, 8] (reduced-surrogate, same
  approach as NR-025; lower d_S = optimistic e-ring packing = BEST chance for a
  crossbred D<D_reg cut to open). d_S=8 reproduces the symbolic degree.

## Meter self-validation (inline, mandatory)

meter_self_validated = **True**

| case | d_ff | D_reg | fires | gate_passes | gate_meaningful | ok |
|---|---|---|---|---|---|---|
| POS_A | 4 | None | False | - | - | True |
| NEG_1 | None | None | False | - | - | True |
| NEG_2 | None | None | False | - | - | True |
| ERING_m3 | 3 | 7 | True | False | False | True |
| POS_C | 4 | 9 | True | True | True | True |

## Admissibility frontier (e-ring) vs NR-025 (x-ring)

NR-025 x-ring baseline: NO admissible (D,k) with D<D_reg in x-ring (reduced surrogate)

| kind | bits | |FB| | d_S | n_vars | degs | D_reg | d_ff | adm<D_reg? | min_adm_D | adm_gate_meaningful |
|---|---|---|---|---|---|---|---|---|---|---|
| solinas_a-3 | 13 | 3 | 3 | 4 | [3, 2, 2, 2] | 6 | 3 | True | 3 | False |
| solinas_a-3 | 13 | 3 | 4 | 4 | [4, 2, 2, 2] | 7 | 3 | True | 3 | False |
| solinas_a-3 | 13 | 3 | 5 | 4 | [5, 2, 2, 2] | 8 | 3 | True | 3 | False |
| solinas_a-3 | 13 | 3 | 6 | 4 | [6, 2, 2, 2] | 9 | 3 | True | 3 | False |
| solinas_a-3 | 13 | 3 | 8 | 4 | [8, 2, 2, 2] | 11 | 3 | True | 3 | False |
| solinas_a-3 | 13 | 4 | 3 | 4 | [3, 2, 2, 2, 2] | 4 | 3 | True | 3 | False |
| solinas_a-3 | 13 | 4 | 4 | 4 | [4, 2, 2, 2, 2] | 4 | 3 | True | 3 | False |
| solinas_a-3 | 13 | 4 | 5 | 4 | [5, 2, 2, 2, 2] | 5 | 3 | True | 3 | False |
| solinas_a-3 | 13 | 4 | 6 | 4 | [6, 2, 2, 2, 2] | 5 | 3 | True | 3 | False |
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
