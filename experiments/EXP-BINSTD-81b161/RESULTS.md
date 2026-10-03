# RESULTS — EXP-BINSTD-81b161

Hypothesis: H-BINSTD-af1faf
Approved by: DEC-20261003-31801d
Predecessor: EXP-BINSTD-4b846c / EV-BINSTD-f1d8e2 / DEC-20261003-4bb57d
Stage-1 package outcome (enriched floors on (17,4)): **O-INCONCLUSIVE**
Diagnostic (17,3) outcome: **O-INSTRUMENT-BOUNDARY-17-3**
Cell (17,4) continuity label: **O-NOT-WEIL-UNIQUENESS**

Package cells: [(17, 4)]
Diagnostic cells: [(17, 3)]

Admission floors (package cells only): >=5 distinct dimVV, >=4 distinct N_var
Legacy Spearman band (NULL reachability target, not Weil uniqueness): >= 0.7
Stage-2 null authorized when (17,4) floors met.

## Panels

- `n17_l4` (package): floors_met=False, rho_disclosed=nan, CI95_disclosed=[nan, nan], distinct_dimVV=3, dimVV_values=[7, 9, 10], distinct_Nvar=2, twin_fail=False, band_reading_authorized_for_null=False, Nvar_values=2
- `n17_l3` (diagnostic): floors_met=False, rho_disclosed=nan, CI95_disclosed=[nan, nan], distinct_dimVV=2, dimVV_values=[5, 6], distinct_Nvar=3, twin_fail=False, band_reading_authorized_for_null=False, Nvar_values=3

## Claims

- break: false
- exponent_move: false
- amazon_bedrock: NOT_USED
- No n>=131 transfer.
- Not a re-run of EXP-BINSTD-4b846c, EXP-BINSTD-9b18fc, EXP-BINSTD-16ee30, EXP-BINSTD-5b2fd0.
- catalog_seed=2026100350 (forbidden priors: [2026100317, 2026100320, 2026100330, 2026100340]).
- Stage-2 null: see stage2/ after stage=2 trial (if authorized).

## Stage-2 null (package HEUR)

- Stage-2 launcher invoked: `RUN-BINSTD-7e503a`.
- Gate: (17,4) floors unmet (`distinct_dimVV=3` `< 5`, `distinct_Nvar=2` `< 4`); twin_fail=False.
- Stage-2 outcome: **O-IMPEDIMENT** (`reason: Stage-2 gate failed: (17,4) floors unmet or twin_fail`).
- No permutation / random-Boolean Spearman was computed; no `stage2/null-results.json`.
- Not a Weil uniqueness re-test; not a re-run of 4b846c/9b18fc/16ee30/5b2fd0 v1.
