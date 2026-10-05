# RESULTS — EXP-BINSTD-4b846c

Hypothesis: H-BINSTD-07aa73
Approved by: DEC-20261003-7fbcb8
Predecessor: EXP-BINSTD-9b18fc / EV-BINSTD-90c856 (also cites EV-BINSTD-69cb29, EV-BINSTD-a99d47)
Package outcome (cell-scoped (17,4)): **O-FAIL-BAND**
Diagnostic (17,3) outcome: **O-INSTRUMENT-BOUNDARY-17-3**
Cell (17,4) continuity label: **O-CELL-FAIL-BAND-17-4**

Package cells: [(17, 4)]
Diagnostic cells: [(17, 3)]

Admission floors (package cells only): >=3 distinct dimVV, >=2 distinct N_var
Spearman band: >= 0.7
Stage-2 null authorized when (17,4) floors met.

## Panels

- `n17_l4` (package): floors_met=True, rho=0.17385016708940756, CI95=[-0.08375481163023511, 0.3461820100189872], distinct_dimVV=3, dimVV_values=[7, 9, 10], distinct_Nvar=2, in_band=False, twin_fail=False, band_reading_authorized=True, ci_entirely_below_band=True
- `n17_l3` (diagnostic): floors_met=False, rho=nan, CI95=[nan, nan], distinct_dimVV=2, dimVV_values=[5, 6], distinct_Nvar=2, in_band=False, twin_fail=False, band_reading_authorized=False, ci_entirely_below_band=False

## Claims

- break: false
- exponent_move: false
- amazon_bedrock: NOT_USED
- No n>=131 transfer.
- Not a re-run of EXP-BINSTD-9b18fc, EXP-BINSTD-16ee30, or EXP-BINSTD-5b2fd0 v1.
- catalog_seed=2026100340 (forbidden priors: [2026100317, 2026100320, 2026100330]).
- Stage-2 null: see stage2/ after stage=2 trial (if authorized).

## Stage-2 null

- null_outcome: **O-NULL-ALSO-BELOW-BAND**
- observed rho=0.17385016708940756 CI95=[-0.08375481163023511, 0.3461820100189872]
- permutation mean_rho=0.002897502784823461 ci95_hi=0.2332489741782888 reaches_band=False
- random_boolean mean_rho=-0.009892882465492662 ci95_hi=0.23647154446502733 reaches_band=False
- artifact: stage2/null-results.json
