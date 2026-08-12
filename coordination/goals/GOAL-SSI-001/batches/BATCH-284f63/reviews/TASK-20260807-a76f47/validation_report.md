# Independent Validator re-derivation — RUN-SSI-9b542d-001

**Task:** TASK-20260807-a76f47 (independent session, role: validator)
**Target:** experiments/EXP-SSI-9b542d/runs/RUN-SSI-9b542d-001
**Instruction, verbatim from GOAL-SSI-001.next_action:** "independent Validator
re-derivation of BCG-1/BCG-2 and RG-1..5 from the run's raw output, not from
the specification's printed tables."
**Constraint honored:** read-only for the entire task; no file touched, edited,
or moved; no git command run. All recomputation performed from raw JSON/first
principles against the frozen `specification.yaml` formulas and `crossover.py`
where a formula was only implicit in code.

## Method

Recomputed every re-derivable check directly from the run's raw artifacts
under `experiments/EXP-SSI-9b542d/runs/RUN-SSI-9b542d-001/`
(`execution_report.yaml`, `raw-result.json`, `boundary_condition_gate.json`,
`reproduction_gate.json`, `monotonicity.json`, `p_star_table.json`,
`sensitivity.json`, `cross_check_secondary.json`, `input_hashes.json`,
`environment.json`, `command.txt`, `stdout.txt`/`stderr.txt`), never from the
specification's printed summary tables, the commit message's headline
figures, or `crossover.py`'s self-reported pass/fail flags where an
independent recomputation was possible instead. BCG-2 was treated
adversarially per its own stated purpose in the specification ("this
campaign's first control... independently confirmed capable of failing") — the
task was to try to break the archived PASS, not confirm it.

## Results

| check | archived | independently recomputed | agrees |
|---|---|---|---|
| RG-1 | PASS | {L1:118.461337, L2:118.517922, L3:118.568995, L4:118.524756} ⊂ [118.25,118.75] | yes |
| RG-2 | PASS | S=3.0 shift ⊂ [121.25,121.75] | yes |
| RG-3 | PASS | A=1.584963 bands ⊂ [119.9,120.4]/[122.9,123.4] | yes |
| RG-4 | PASS | bracket [118.461337,123.153958], mixed units correctly disclosed | yes |
| RG-5 | PASS | full 4-law×2-S×4-A grid at c=0: min gap 2.524114, max gap 11.275629, span ⊇ [6,11] | yes |
| BCG-1 | PASS | algebraic identity confirmed (penalty term exactly 0 at w=L_mem(P)) | yes |
| BCG-2 | PASS | superseded-formula residual hand-derived to 0.5·L_mem(P); 36 raw `tail_checks.bcg1_interpolated_check` entries spot-checked directly, all residual 0.0; confirmed genuine, non-vacuous negative control | yes |
| MONO-1 | PASS | n_checks=300, n_pass=300, max_error≈1.4e-15 — consistent with genuine finite-difference measurement | yes (not cell-by-cell reconstructed — see limitations) |
| MONO-2 | PASS | kink locations 92.5/138.6 for P=256/384 match T2's L_mem values exactly | yes |
| MONO-3 | FAIL (non-blocking finding) | p_star_log2 = 295.263566 (log2_w=80) → 370.685590 (log2_w=92.5), L1/L2, MC_P13_CORRECTED, S=A=c=0 — pulled directly from `p_star_table.json.main_grid`; w=80 root independently confirmed by direct substitution into the margin formula (residual ≈8.7e-10) | yes — reversal is real, shape now characterized: occurs exactly at w=L_mem(256)=92.5, confined to L1/L2 under MC_P13_CORRECTED; MC_VOW arms correctly reported NOT_EVALUABLE(n=0), not silently zeroed |
| MONO-4 | PASS | max difference 136.1 bits, consistent with independently-confirmed BCG-2 magnitude at P=768 | yes (not cell-by-cell reconstructed — see limitations) |
| MONO-5 | PASS | L_paper(P)-P/3 and L_mem(P)-P/3 monotonicity hand-verified from all five T2 rows | yes |
| XCHK-1 (cross-check) | PASS | recomputed via the "direct summation" path independently; agrees with archived `general_evaluator`/`direct_summation` pair, diff 0.0 | yes (self-limited: same expression, second code path, per the spec's own caveat) |
| NULL-OBJECT | PASS | D_null0/D_null1 recomputed directly from E(P); band [11.9,14.2] satisfied; D_null1 < D_null0 holds algebraically wherever E(P) > 9.8 | yes, non-vacuous |

## Findings, non-blocking, both independently re-confirmed by the Coordinator's own separate check (see EV-SSI-0c529c)

1. **Commit-identity inconsistency.** `manifest.yaml.git_commit` = `5266050b4b710f093d252a9cb479a658021e68bc`; `execution_report.yaml.implementation_commit` = `f7944f98c2d881fe1ac28e8575b9fca4190d53da`. Both distinct, both real, both reachable; both files self-report a dirty working tree at execution time. The durable receipt (Coordinator snapshot `a21c1976b`) is clean and content-complete, so this does not put the archived result in doubt — but the run's own provenance fields disagree with each other.
2. **XCHK-2 conformance gap.** `environment.json` shows numpy present, but `cross_check_secondary.json` reports `XCHK-2: "NOT_IMPLEMENTED"` rather than either running the Dickman-rho cross-check (the spec's expected path when numpy is available) or using the defined absence path (`NOT_RUN` + `ImportError` text, which only applies when numpy is genuinely absent). Non-blocking per the frozen contract; undisclosed as a deviation by the archived run.

## Reproducibility

Input file hashes (`cost_measurements.json`, `paper_fulltext.md`,
`cost_model.py`) recomputed and confirmed byte-exact against
`input_hashes.json`, independently by both this task and by the Coordinator's
own separate `sha256sum` pass (see EV-SSI-0c529c). Cell counts
(`n_main_cells=4480`, `n_null_cells=2240`, `n_l5_cells=1120`) confirmed to
match the actual grid lengths in `p_star_table.json` and the categorical
counts in `raw-result.json.tail_checks`.

## Overall verdict

**PASS.** RUN-SSI-9b542d-001's "all mandatory gates PASS" self-report survives
independent re-derivation from raw data. Every check re-derivable from raw
JSON reproduces to matching precision; no check disagreed with its archived
verdict; MONO-3's finding is real, non-blocking, and now precisely
characterized rather than left as a bare flag.

## Limitations, stated rather than smoothed over

- MONO-1 and MONO-4 were accepted on internal-consistency plausibility
  grounds (magnitude and structure), not full independent cell-by-cell
  reconstruction of their underlying grids, due to grid size.
- XCHK-1 is self-limited by construction (the spec itself notes it would
  inherit the same anchor bug as the primary path, being a second code path
  over the same expression).
- The commit-identity discrepancy is recorded, not explained — which commit
  was actually live during execution cannot be determined from the artifacts
  alone.
