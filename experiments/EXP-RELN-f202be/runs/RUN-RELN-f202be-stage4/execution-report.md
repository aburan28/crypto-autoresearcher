# Execution report -- RUN-RELN-f202be-stage4 (analysis)

Consumes RUN-RELN-f202be-{stage0,stage1,N14,N16,N18,N20} artifacts.

## HEADLINE: forced-negation-gap trap control (BLOCKING) fails on 23/72 object cells

Measured deviation is always NEGATIVE (measured < B^3/(4M)) and shrinks monotonically in relative size as B grows across rungs (~-10% mean at rung14, ~-6% at rung16, ~-3% at rung18, ~-2% at rung20), consistent in sign, scale and trend with the specification's own acknowledged O(m/B) correction to INV-2pp (m=3; 3/B = 6.25% at B=48 vs 1.6% at B=186). This pattern is consistent with a genuine finite-size correction rather than an implementation bug, but the pre-committed ABSOLUTE tolerance of 0.1 is exceeded on 23 of 72 object cells (mostly rung14 and rung16, B2 convention especially), which is a BLOCKING control miss under the contract's own stopping_rules and invalidation_rules, applied mechanically here regardless of the plausible explanation.

Rungs with at least one failing cell: [14, 16]. Rungs 18 and 20 pass this control cleanly on every cell (see per-cell measured-vs-expected values in control-verdicts.json / accounting.json of each rung run).

Per the contract's stopping_rules, this is a BLOCKING control failure: "Stop the run's object-arm reading if ... the forced-negation gap is off by more than 0.1 on any negation-closed arm; complete and record the null and control arms, mark the run instrument_failed, and report no scientific verdict." Applied mechanically here.

## Mechanical classification
- complete_run_set: True
- all_blocking_controls_pass: False
- all_object_cells_in_null_a_band (measured, NOT a verdict given the control failure above): True
- growth_slope_contains_zero_all_geometries (measured, NOT a verdict): False
- slope_status_per_geometry (measured, NOT a verdict): {'x_interval_low': 'excludes_zero_negative', 'x_interval_mid': 'excludes_zero_negative', 'qr_class': 'excludes_zero_negative'}
- mechanical_classification: INSTRUMENT_FAILURE_NO_VERDICT

### Reason
A blocking control failed its pre-committed value: the forced-negation-gap trap control (forced_gap_within_0.1) misses its pre-committed 0.1 absolute tolerance on 23 of 72 object cells, concentrated at rungs [14, 16] (see control-verdicts.json for the exact cells and the measured-vs-expected values; the deviation is small, negative, and shrinks with B in a pattern consistent with the specification's own acknowledged O(m/B) correction to INV-2pp -- but the contract's stopping_rules mandate this classification mechanically regardless of that plausible explanation: 'Stop the run's object-arm reading if ... the forced-negation gap is off by more than 0.1 on any negation-closed arm ... mark the run instrument_failed, and report no scientific verdict.' The null and control arm measurements (NULL-A/NULL-B bands, ZN-interval, Bose-Chowla, q-decay, spectral cross-check, growth fit) are still recorded in full in metrics.json/bands.json as required, but the object-arm M6 NULL/ALIVE verdict is NOT read from this run set.

## Measured (not verdict) growth fits (log excess vs log N, B1 reduced, 4 rungs)
Recorded per the contract's requirement to preserve all null/control-arm measurements even when an instrument failure blocks the object-arm verdict; NOT read as evidence for or against NULL/ALIVE given the control failure above.
- x_interval_low: slope=-0.4800 CI=[-0.6315,-0.3437] n_rungs=4 rungs_used=[14, 16, 18, 20]
- x_interval_mid: slope=-0.4524 CI=[-0.6967,-0.2158] n_rungs=4 rungs_used=[14, 16, 18, 20]
- qr_class: slope=-0.4830 CI=[-0.5270,-0.3921] n_rungs=4 rungs_used=[14, 16, 18, 20]

## Other control summary (ZN interval, Bose-Chowla, q-decay -- all pass)
See control-verdicts.json 'detail' key; ZN_interval/Bose-Chowla/q_decay all pass their own pre-committed values at every rung/curve (Bose-Chowla skipped, not failed, at rung16 -- see implementation.md #1).

## Predicate lifts / Holm correction
See predicate-lifts.json. Also NOT a verdict given the forced-gap control failure above. Additionally carries its own separate DEVIATION (see implementation.md #3): computed under the ANALYTIC (INV-3, i.i.d.-uniform) null for ALL object cells including negation-closed arms, NOT the contract-specified NULL-A Monte Carlo null for negation-closed arms.
