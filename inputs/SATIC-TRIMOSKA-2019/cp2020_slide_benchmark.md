# CP 2020 slide benchmark (Trimoska, Ionica, Dequen)

Source: "Parity (XOR) Reasoning for the Index Calculus Attack", CP 2020 slides,
https://mtrimoska.com/slides/CP_2020.pdf, fetched 2026-09-04. Text extracted with
`pdftotext -layout`. The same table was independently supplied by the repository
owner in conversation on 2026-09-04; the two agree exactly.

Slide caption: "Index calculus attack on binary elliptic curves — 51 variables, 52 equations."

Cross-reference: 51 variables / 52 equations is the `l = 6, n = 19` row of Table 1 of
ePrint 2019/313 (Grobner model column), so this slide is the l=6, n=19 instance family.

| Solving approach       | SAT runtime (s) | SAT #conflicts | UNSAT runtime (s) | UNSAT #conflicts |
| ---------------------- | --------------- | -------------- | ----------------- | ---------------- |
| Grobner bases          | 229.3           | N/A            | 229.4             | N/A              |
| MiniSat                | 239.7           | 1840190        | 517.0             | 3433304          |
| Glucose                | 189.2           | 1527158        | 274.8             | 2056575          |
| MapleLCMDistChronoBT   | 655.1           | 4035131        | 918.7             | 5378945          |
| CaDiCaL                | 43.6            | 254194         | 141.3             | 629869           |
| CryptoMiniSat          | 331.8           | 1791188        | 707.9             | 3416526          |
| WDSat                  | 0.6             | 48438          | 3.8               | 255698           |

## Solver architecture as stated on the slides

- WDSat is DPLL-based with three modules: **CNF**, **XORSET**, **XORGAUSS**.
- A preprocessing technique based on the **Minimal Vertex Cover** problem is used
  (this is the branching-order / core-variable selection step).
- Gaussian elimination is presented as the XOR-reasoning enhancement whose value is
  in question; the paper's Table 4 measures it and finds it NOT beneficial for this model.

## What this table does and does not say

- It is a single instance family (l = 6, n = 19) on binary Koblitz curves, S_4 (m = 3).
- Runtimes are from the authors' hardware (paper: 2.40GHz Intel Xeon E5-2640), not reproduced here.
- SAT and UNSAT are reported separately because the two cost profiles differ in opposite
  directions for SAT solvers versus Grobner bases (see ePrint 2019/313 Section 6).
- Nothing here is an end-to-end index-calculus cost: this is the point-decomposition
  (pdp) step only, with no relation-yield, linear-algebra, or matched-rho accounting.
