# Conversion-cost note — EXP-BINSTD-38e4ad Stage 0 (HOLD-S)

Polynomial-basis ↔ normal-basis conversion for F_{2^n} is charged **O(n²) bit
operations once** (build the change-of-basis matrix once; apply as needed).

HOLD-S correction:
- This cost is a rounding error against any decomposition / relation-search
  budget at the scales considered in this lane.
- It is **recorded here once** and **dropped from the title and priority
  argument** of H-BINSTD-c3d68f / EXP-BINSTD-38e4ad.
- On ECC2K-130 the challenge is already in a type-II ONB (KN-LIT-661e97 prior
  pointer); access cost is zero there — cited as prior only, not re-derived.

`conversion_cost_note_present: true`
`label: DOCUMENTATION`
`no_priority_use: true`
