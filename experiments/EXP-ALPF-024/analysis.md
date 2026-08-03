# Analysis — Autolab prime-field: round013_exp029b_bsmooth_psin_fb

## Observation
failed

Source excerpt / raw summary:

```
# EXP-029b: B-smooth psi_n Torsion Factor Base — Result

**Experiment**: EXP-029b  |  **Round**: 13  |  **Timestamp**: 2026-05-31 11:45:12

## Hypothesis
On a curve E/F_p with B-smooth order (n^2 | |E(F_p)|), the n-torsion FB is non-empty
(escaping NR-021 cardinality barrier), but relations confined to E[n] carry zero
information about k mod L (the large prime factor). IC provides no advantage over PH.

## Null Hypothesis
Relations from the n-torsion FB pin k mod L with non-trivial probability (> 1/L).

## Meter Self-Validation
All 4 fixtures: **PASS**
- POS_A: PASS (expect: fires=True, d_ff=4, D_reg=7 (3-var ring))
- NEG_1: PASS (expect: fires=False)
- ERING: PASS (expect: fires=True, gate_meaningful=False)
- POS_C: PASS (expect: fires=True, gate_meaningful=True)

## Anti-Circularity Check
N/A: this experiment tests the subgroup-information barrier on the n-torsion FB,
NOT a new polynomial representation.  The psi_n membership constraint is
algebraically distinct from the x-line Semaev FB (psi_n cuts E[n] by degree, not x-interval).
No comparison to previously-tested polynomial systems is needed because the
decisive test is information-theoretic (DLog mod n vs mod L), not degree-of-regularity.

## Results by Case

### n=3, bits~10, seed=42
- p=827 (10 bits), |E|=801 = 3^2 * 89
- |FB x-coords| = 1, expected psi_n degree = 4, non-empty: **True**
- Cardinality barrier (NR-021) escaped: **True**
- Gated meter: d_ff=6 D_reg=5 fires=False gate_meaningful=False
- n-torsion rational count: 2 (expected n^2-1 = 8)
- Relations found: 0
- All n-torsion DLogs multiples of n*L: **True**
- k mod n: 1, k mod L: 5, k mod n*L: 94
- k mod n recovered from relations: N/A
- k mod L recovered from relations: N/A (no relations: k not ≡ 0 mod L)
- **Info about k mod L from IC relations**: **False**
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
