# Portfolio hold — EXP-BINSTD-b7344f Stage 2

Decision orientation: **DO-1**

## Stage-0 arithmetic (modeled)

- V(β) ≤ 0 for all ρ ≥ 1 on the Stage-0 grid: `True`
- Product-law FREE-oracle floors exceed rho at m ∈ {2,3}: `True`
- Therefore a concurrent IC∪rho portfolio cannot improve expectation at m ≤ 3
  under the concentrated-IC / exponential-rho model (HOLD-U).

## Stage-1 controlled null (measured)

- Unsat CV: `0.01114683604798408`
- Sat CV: `0.010443595978207395`
- HEUR-H1 (CV < 0.1) on both: `True`

W4 cost-shape is a **controlled null** only. IMP-no-cdcl remains: absence of
WDSat / CryptoMiniSat / CaDiCaL / Macaulay2 is infrastructure, not thin-tail
evidence about CDCL search.

## Claims refused

- No break, no exponent move, no deployed V(β*)>0, no CDCL heavy-tail claim,
  no positive portfolio authorization. m ≥ 4 remains an arity/oracle question,
  not a portfolio question.

## certificate.kind

Stage-2 artifacts use `certificate.kind: none`.
