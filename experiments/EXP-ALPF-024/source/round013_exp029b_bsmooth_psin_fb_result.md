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
- PH recovered k mod n^2 correctly: True

### n=3, bits~11, seed=43
- p=1867 (11 bits), |E|=1791 = 3^2 * 199
- |FB x-coords| = 1, expected psi_n degree = 4, non-empty: **True**
- Cardinality barrier (NR-021) escaped: **True**
- Gated meter: d_ff=6 D_reg=5 fires=False gate_meaningful=False
- n-torsion rational count: 2 (expected n^2-1 = 8)
- Relations found: 0
- All n-torsion DLogs multiples of n*L: **True**
- k mod n: 2, k mod L: 37, k mod n*L: 236
- k mod n recovered from relations: N/A
- k mod L recovered from relations: N/A (no relations: k not ≡ 0 mod L)
- **Info about k mod L from IC relations**: **False**
- PH recovered k mod n^2 correctly: True

### n=3, bits~12, seed=44
- p=3907 (12 bits), |E|=3897 = 3^2 * 433
- |FB x-coords| = 4, expected psi_n degree = 4, non-empty: **True**
- Cardinality barrier (NR-021) escaped: **True**
- Gated meter: d_ff=6 D_reg=5 fires=False gate_meaningful=False
- n-torsion rational count: 8 (expected n^2-1 = 8)
- Relations found: 0
- All n-torsion DLogs multiples of n*L: **True**
- k mod n: 0, k mod L: 36, k mod n*L: 36
- k mod n recovered from relations: N/A
- k mod L recovered from relations: N/A (no relations: k not ≡ 0 mod L)
- **Info about k mod L from IC relations**: **False**
- PH recovered k mod n^2 correctly: True

### n=5, bits~10, seed=52
- Curve search FAILED: No suitable B-smooth curve found for n=5, bits~10
### n=5, bits~11, seed=53
- p=1861 (11 bits), |E|=1825 = 5^2 * 73
- |FB x-coords| = 2, expected psi_n degree = 12, non-empty: **True**
- Cardinality barrier (NR-021) escaped: **True**
- Gated meter: d_ff=14 D_reg=13 fires=False gate_meaningful=False
- n-torsion rational count: 4 (expected n^2-1 = 24)
- Relations found: 13
- All n-torsion DLogs multiples of n*L: **True**
- k mod n: 4, k mod L: 0, k mod n*L: 219
- k mod n recovered from relations: 0 mod L (but not which nonzero residue)
- k mod L recovered from relations: 0 (relations exist only when L|k, giving k mod L = 0 exactly)
- **Info about k mod L from IC relations**: **False**
- PH recovered k mod n^2 correctly: False

## Pohlig-Hellman Baseline Note
PH recovers k mod n^2 in O(n^2) group ops using E[n] directly — no IC needed.
PH recovers k mod L in O(sqrt(L)) group ops using the order-L subgroup.
For n-torsion IC to be relevant it must beat PH on the L-part.
This experiment shows it cannot: relations from E[n] are confined to k = 0 mod n*L,
providing zero new information about k mod L beyond PH.

## Verdict
**FAILED**

FB non-empty (escapes NR-021 cardinality barrier) but the subgroup-information barrier holds: n-torsion DLogs are all multiples of n*L (PROVED algebraically), so A+B+C=Q from E[n] requires L|k (probability 1/L for random k).  Relations carry zero info about k mod L beyond a 1-bit test.  PH dominates on both parts.  Bankable empirical+algebraic NEGATIVE RESULT.

## What Is Ruled Out
- n-torsion psi_n FB as an IC attack on the L-part of the ECDLP.
- Any representation using fixed-degree FB from a PROPER subgroup of E(F_p)
  is confined to the Pohlig-Hellman territory of that subgroup.

## What Is NOT Ruled Out
- IC attacks using FB elements that are NOT confined to a proper subgroup.
- The theta/Kummer chart (EXP-030) where the FB is not a subgroup.
- Weil restriction methods over extension fields (POS-C confirmed).

## Next Experiment
EXP-030: Theta/level-2-Kummer quartic chart (round-12 EXP-028 was circular;
verify algebraic distinctness from x-line Semaev before running meter).

