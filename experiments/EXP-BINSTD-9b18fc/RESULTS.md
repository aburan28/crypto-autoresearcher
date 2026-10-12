# RESULTS — EXP-BINSTD-9b18fc

Hypothesis: H-BINSTD-73ea03
Approved by: DEC-20261003-6e578e
Predecessor: EXP-BINSTD-16ee30 / EV-BINSTD-69cb29 (also cites EV-BINSTD-a99d47)
Package outcome: **O-INCONCLUSIVE**
Scoped (17,4) outcome: **O-CELL-FAIL-BAND-17-4**

Stage-1 cells: [(17, 3), (17, 4)]

Admission floors (package FORALL): >=3 distinct dimVV, >=2 distinct N_var
Spearman band (pre-registered; package read only after FORALL floors): >= 0.7
Scoped (17,4) fail-band replication authorized when that cell meets floors (independent of (17,3) floors).

## Panels

- `n17_l3`: floors_met=False, rho=nan, CI95=[nan, nan], distinct_dimVV=2, distinct_Nvar=3, in_band=False, twin_fail=False, band_reading_authorized=False, ci_entirely_below_band=False
- `n17_l4`: floors_met=True, rho=0.10991777135396452, CI95=[-0.13887576443373953, 0.29612168143997897], distinct_dimVV=3, distinct_Nvar=2, in_band=False, twin_fail=False, band_reading_authorized=True, ci_entirely_below_band=True

## Claims

- break: false
- exponent_move: false
- amazon_bedrock: NOT_USED
- No n>=131 transfer.
- Not a re-run of EXP-BINSTD-16ee30 or EXP-BINSTD-5b2fd0 v1.
- catalog_seed=2026100330 (forbidden priors: [2026100317, 2026100320]).
