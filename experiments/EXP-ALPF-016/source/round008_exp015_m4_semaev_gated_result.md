# EXP-015 Result: m=4 Semaev S5 in prime-field x-ring under the gated meter

Round 008. Seed 42. Timestamp 2026-05-31 00:54:53.

## Meter self-validation (mandatory)
- POS-A fires d_ff=4<7: **True**
- NEG-1 & NEG-2 quiet: **True**
- e-ring m=3 base-fires but NOT gate_meaningful (artifact): **True**
- POS-C Weil S_3 gate_meaningful (gate PASSES): **True**
- overall meter_self_validated: **True**

| control | d_ff | D_reg | fires | gate_passes | gate_meaningful | lf_degs |
|---|---|---|---|---|---|---|
| POS-A | 4 | None | False | False | False | [3, 3, 3] |
| NEG-1 | None | None | False | False | False | [2, 2, 2] |
| NEG-2 | None | None | False | False | False | [3, 3, 3] |
| e-ring m3 | 3 | 7 | True | False | False | [2, 2, 2, 4] |
| POS-C WeilS3 | 4 | 9 | True | True | True | [3, 3, 3, 3] |

## S5 correctness verification
- S5 total degree: 32 ; degree-per-variable: [8, 8, 8, 8, 8] ; #monomials: 54757
- S4 total degree: 12
- vanishes on REAL 5-tuples (P1+..+P5=O): 6/6 passed
- NEGATIVE control (random x-tuples, should be nonzero): 6/6 nonzero
- S5 verification ok: **True**

## Per-cell meter table (m=4 decomposition system [s5R, F(x1..x4)], sumpoly_indices=[0])

| bits | family | fbsize | s5R tdeg | s5R deg/var | lf_degs | d_ff | D_reg | fires | gate_passes | gate_meaningful | status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 13 | random_primeorder | 4 | 32 | [8, 8, 8, 8] | [32, 4, 4, 4, 4] | None | 13 | False | False | **False** | ok |
| 13 | random_primeorder | 5 | 32 | [8, 8, 8, 8] | [32, 5, 5, 5, 5] | None | 17 | False | False | **False** | ok |
| 13 | random_primeorder | 6 | 32 | [8, 8, 8, 8] | [32, 6, 6, 6, 6] | None | 21 | False | False | **False** | ok |
| 13 | solinas_a-3 | 4 | 32 | [8, 8, 8, 8] | [32, 4, 4, 4, 4] | None | 13 | False | False | **False** | ok |
| 13 | solinas_a-3 | 5 | 32 | [8, 8, 8, 8] | [32, 5, 5, 5, 5] | None | 17 | False | False | **False** | ok |
| 13 | solinas_a-3 | 6 | 32 | [8, 8, 8, 8] | [32, 6, 6, 6, 6] | None | 21 | False | False | **False** | ok |
| 15 | random_primeorder | 4 | 32 | [8, 8, 8, 8] | [32, 4, 4, 4, 4] | None | 13 | False | False | **False** | ok |
| 15 | random_primeorder | 5 | 32 | [8, 8, 8, 8] | [32, 5, 5, 5, 5] | None | 17 | False | False | **False** | ok |
| 15 | random_primeorder | 6 | 32 | [8, 8, 8, 8] | [32, 6, 6, 6, 6] | None | 21 | False | False | **False** | ok |
| 15 | solinas_a-3 | 4 | 32 | [8, 8, 8, 8] | [32, 4, 4, 4, 4] | None | 13 | False | False | **False** | ok |
| 15 | solinas_a-3 | 5 | 32 | [8, 8, 8, 8] | [32, 5, 5, 5, 5] | None | 17 | False | False | **False** | ok |
| 15 | solinas_a-3 | 6 | 32 | [8, 8, 8, 8] | [32, 6, 6, 6, 6] | None | 21 | False | False | **False** | ok |
| 17 | random_primeorder | 4 | 32 | [8, 8, 8, 8] | [32, 4, 4, 4, 4] | None | 13 | False | False | **False** | ok |
| 17 | random_primeorder | 5 | 32 | [8, 8, 8, 8] | [32, 5, 5, 5, 5] | None | 17 | False | False | **False** | ok |
| 17 | random_primeorder | 6 | 32 | [8, 8, 8, 8] | [32, 6, 6, 6, 6] | None | 21 | False | False | **False** | ok |
| 17 | solinas_a-3 | 4 | 32 | [8, 8, 8, 8] | [32, 4, 4, 4, 4] | None | 13 | False | False | **False** | ok |
| 17 | solinas_a-3 | 5 | 32 | [8, 8, 8, 8] | [32, 5, 5, 5, 5] | None | 17 | False | False | **False** | ok |
| 17 | solinas_a-3 | 6 | 32 | [8, 8, 8, 8] | [32, 6, 6, 6, 6] | None | 21 | False | False | **False** | ok |

## Verdict: **failed**

- meter_self_validated: True
- gate_meaningful_fire (any cell): False

### What this rules out
Under the hardened gated first-fall meter, the m=4 Semaev S5 decomposition system in prime-field x-ring coordinates with a degree-|FB| FB-membership constraint (|FB| in {4,5,6}, bits in {13,15,17}, random prime-order and Solinas/a=-3 curves) shows NO gate-meaningful early fall. This extends NR-018/NR-019 from m=3 to m=4: the same FB-row-confinement / D_reg-conservation behavior persists. NEGATIVE RESULT.

### What this does NOT rule out
- crossbred / XL / hybrid solvers (d_ff-governed, not D_reg-governed) at m=4;
- other FB shapes (trace/norm working DIRECTLY on E(F_p), Kummer subsets, rational-map roots) at m=4;
- m>=5 Semaev or asymmetric point-splitting (e.g. 1+3, 2+2 with distinct FBs);
- larger |FB| where the S-degree/FB-degree crossover differs;
- Weil/extension-field m=4 (out of prime-field scope here).

## Next structure to test
1. Conservative: m=4 S5 under a CROSSBRED/XL meter (d_ff-governed) at the same cells -- Yokoyama's D_reg bound does NOT cover crossbred, so a d_ff < D_reg with FB-confined syzygy could still help XL even if the gate is about IC-solver leverage.
2. Representation-changing: asymmetric m=4 split (2+2) with TWO distinct factor bases, or Kummer/Montgomery x-line FB working directly on E(F_p), re-metered with the gate.
3. High-risk: m=4 over a SMALL extension F_{p^2} with Weil restriction (POS-C is the only gate-passing fall) to test whether the m=4 Weil fall is stronger than m=3, then ask what prime-field structure could mimic it.

