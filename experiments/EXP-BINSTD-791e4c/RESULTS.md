# RESULTS — EXP-BINSTD-791e4c

Hypothesis: H-BINSTD-336a46
Approved by: DEC-20261003-c5aef5
Predecessor: EXP-BINSTD-dbca92 / EV-BINSTD-56c2bc / DEC-20261003-95d6b8 (parent EXP-BINSTD-871156 / EV-BINSTD-d3a6be)
Stage-1 outcome: **O-INCONCLUSIVE**

Stage-1 cells: [(19, 3), (19, 4), (23, 3), (23, 4)]

Spearman band (pre-registered): <= -0.7
Admission floors: distinct_rTr>=4, distinct_Nnl>=4, unique_pairs>=4
Catalog seed: 202610033364 (forbidden [202610038196, 202610038782, 202610039715, 202610034821])
Stage-2 shuffled-linear null: authorized when Stage-1 is O-SUPPORT.

## Panels

- `n19_l3`: rho=-0.8865567227404852, CI95=[-0.9795389508379349, -0.7554983781688576], distinct_rTr=4, distinct_Nnl=4, unique_pairs=7, floors_met=True, in_band=True, twin_fail=False
- `n19_l4`: rho=-0.9030616159415418, CI95=[-1.0000000000000002, -0.6831300510639733], distinct_rTr=3, distinct_Nnl=3, unique_pairs=4, floors_met=False, in_band=False, twin_fail=False
- `n23_l3`: rho=-0.5991480037243602, CI95=[-0.7868026053340385, -0.31160174480862873], distinct_rTr=4, distinct_Nnl=13, unique_pairs=20, floors_met=True, in_band=False, twin_fail=False
- `n23_l4`: rho=-0.5737260654466283, CI95=[-0.799714188940302, -0.32992184913208095], distinct_rTr=4, distinct_Nnl=11, unique_pairs=17, floors_met=True, in_band=False, twin_fail=False

## Claims

- break: false
- exponent_move: false
- amazon_bedrock: NOT_USED
- No n>=131 transfer.
- Not a re-run of EXP-BINSTD-dbca92 / 871156 / 6fd454 / 8196d7.
- Distinct from IDEA-20261001-febbe1 (dim(V·V)→N_var).
- No KN-FIND.
- Stage-2 null: see stage2/ after stage=2 trial (if authorized).
