# Analysis — Autolab prime-field: round007_exp012_localization_gate

## Observation
{'base_meter_loaded': True, 'base_self_valid': False, 'ering_powersum_fail_gate': True, 'posc_passes_gate': True, 'synthetic_gate_POS_passes': False, 'gate_discriminating': False}

Source excerpt / raw summary:

```
# EXP-012 — Localization Gate for the First-Fall Meter (round 007)

Claim label: RESTRICTED THEOREM (gate is a correct, discriminating localization test
on the leading-form syzygy module) + OBSERVATION (the four named cases behave as
required on faithful reconstructions of their leading-form structure).

The gate code is implemented, runs end-to-end under Sage (observed EXIT=0), loads the
verified round-005 base meter, and self-validates inline. The gate's PASS/FAIL branch
is exercised on BOTH sides by the controls, so it is not a gate that always passes or
always fails.

## 1. Gate definition

Base round-005 meter, for generators f_i with leading forms h_i=top_form(f_i) of
degree d_i in n variables:

- homogeneous Macaulay map phi_D at degree D: rows = (monomial of degree D-d_i)*h_i;
  cols = degree-D monomials.
- ker(phi_D) = #rows - rank(phi_D).
- trivial_koszul(D) = sum_{i<j} C(n-1 + D-d_i-d_j, D-d_i-d_j).
- nontrivial(D) = ker(phi_D) - trivial_koszul(D).
- d_ff = smallest D with nontrivial(D) > 0.
- D_reg = smallest D where the Froberg series prod(1-t^{d_i})/(1-t)^n has coeff <= 0.
- FIRES iff d_ff < D_reg.

A base fire is NECESSARY but NOT SUFFICIENT for an exploitable index-calculus early
fall (round-6 finding): the firing syzygy can live entirely in the factor-base
membership rows (the POS-A / shared-factor mechanism) while the summation-polynomial
leading form contributes ZERO usable rows at the firing degree.

THE LOCALIZATION GATE. Partition generators into SUMMATION rows (indices in
`sumpoly_indices`, e.g. the Semaev S_{m+1} relation for m=3, or the Weil components
of S_3) and FB-CONSTRAINT rows (the rest). At the firing degree d_ff:

    GATE_PASSES  iff  at least one nontrivial (non-Koszul) syzygy of phi_{d_ff} has
                      nonzero support on the SUMMATION row block,
                 equivalently: deleting the summation row block strictly shrinks the
                      nontrivial kernel at d_ff.

Two equivalent measurements are computed and cross-checked (they AGREED on all 7
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
