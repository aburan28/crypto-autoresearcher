# Analysis EXP-SSIQ-c0a99a

Review task TASK-20261003-89b4c7. Hypothesis H-SSIQ-dfee7e. Approval DEC-20261003-f31aec. Evidence EV-SSIQ-ae9112. Decision DEC-20261003-090741.

## Observation

Two completed runs are on disk, each with `manifest.yaml`.

RUN-SSIQ-cddfc0 (Stage 0) has receipt status `output_validated`, `check.py` return 0, and stdout `{"outcome": "O-STAGE0-OK", "stage": 0}`. The raw result is `O-STAGE0-OK` with `fixtures_ok` true, `twin_ok` true, `k2_k` 2, `fourteen_k` 16378, `claims.break` false, and `claims.exponent_move` false. Certificate kind is `none`.

RUN-SSIQ-414b0f (Stage 1) has receipt status `output_validated`, `check.py` return 0, and stdout `{"outcome": "O-ARTIFACT", "stage": 1}`. The raw result is `O-ARTIFACT` with `artifact_flags` exactly `['k2_cover_not_rho_squared']`, `claims.break` false, and `claims.exponent_move` false. Certificate kind is `none`. Wall clock on the archived raw result is 590.467586517334 seconds. `RESULTS.md` names the same single `O-ARTIFACT` label and the same flag list.

Archived panel summaries, quoted only as figures the artifact label discards:

| cell | median_k | gstar | n_k | h1_maxdev |
| --- | --- | --- | --- | --- |
| sqisign_i_b20 | 14 | 1.7607032456627694 | 17911 | 0.28138957898383343 |
| sqisign_v_b20 | 180 | 5.9084187639572985 | 20000 | 0.31027036235027355 |
| regression_p40_b12 | 2 | 0.8026558465510883 | 400 | 0.29000000000000015 |

The sqisign_v_b20 median_k figure 180 and gstar figure about 5.908 meet the representation cuts median ≥ 80 and G* ≥ 4. The same cell's h1_maxdev is about 0.310, above both 0.02 and 0.1. The artifact label discards all three median_k figures. This package keeps no k-claim.

## Comparison

Blind evaluation, done before `implementation/` or `stage1/control-table.json` was opened. At k = 2 the cover formula `1-(1-ρ²)^{k/2}` equals ρ². On the frozen grid the six values are:

| ρ | ρ² |
| --- | --- |
| 0.02 | 0.0004 |
| 0.05 | 0.0025 |
| 0.1 | 0.01 |
| 0.2 | 0.04 |
| 0.4 | 0.16 |
| 0.8 | 0.64 |

The archived formula column matches that identity. Each stored formula equals the float64 evaluation of `1-(1-ρ²)^{1}`, and the absolute gap to ρ² is at most about 5×10⁻¹⁷.

On the six archived k = 2 rows, every `|p_a - formula|` and `|p_b - formula|` was computed. The maximum is `|0.215 - 0.16| = 0.055` on ρ = 0.4, path A (`p_a` 0.215; the IEEE subtraction against the stored formula is 0.054999999999999966, which is still above 0.05). The other eleven absolute deviations are at or below 0.05. The next largest is path B at ρ = 0.4, `|0.115 - 0.16| = 0.045`. The only excess is ρ 0.4 path A. The archived flag list is exactly `['k2_cover_not_rho_squared']`.

In `implementation/run.py`, `run_stage1` appends `k2_cover_not_rho_squared` when `max(k2_devs) > 0.05`, then assigns `outcome = "O-ARTIFACT"` whenever `artifact_flags` is nonempty. The median-band tests (`O-REPRESENTATION`, `O-NEGLIGIBLE`, `O-MIXED`) sit in the `else` of that test. A nonempty flag list, including this one flag, is decided before any median band is read. That branch cannot emit `O-REPRESENTATION` while the flag is set.

A Stage 1 replay was run from `/tmp/review-ssiq-c0a99a` after deleting that copy's `stage1/panels.json`, `stage1/control-table.json`, and `RESULTS.md`. Command: `python3 /tmp/review-ssiq-c0a99a/implementation/run.py --stage 1 --trial-plan /tmp/review-ssiq-c0a99a/trial-plan.json --run-dir /tmp/review-ssiq-c0a99a-rundir`. Exit 0. Outcome `O-ARTIFACT`. `artifact_flags` exactly `['k2_cover_not_rho_squared']`. Replay wall clock 590.9091436862946 seconds. Replay `panels_summary` equals the archived raw summary. The repository `RESULTS.md`, `stage1/panels.json`, and `stage1/control-table.json` were not rewritten.

## Inference

The package label is `O-ARTIFACT`. Direction is neutral. Strength is inconclusive. The median-k law is neither supported, weakened, nor rejected in scope. No exponent moves. Integer Arm I is the tested object. `O-ARTIFACT` keeps no k-claim, so the discarded median_k figures, including 180, are not an `O-REPRESENTATION` result.

Hypothesis H-SSIQ-dfee7e and experiment EXP-SSIQ-c0a99a move from `approved` to `analyzed` under DEC-20261003-090741. `analyzed` records the artifact label.

## Limitation

Scope is the frozen integer Arm I cells, the k = 2 nearby-object control, the dual-hash cover simulation, this solver, and these two runs. Deuring sampling and isogeny walks were not run. No `p^{1/4}` statement and no Wesolowski exponent move is in this package. Certificate kind is `none`. One coordinator task owned joints J1, J2, and J3 (addendum PD-1); a separate validator session and a red-team session were not run. The temp replay reproduces the archived label on the same seeds; it is not an independent replication and it is not a new `RUN-*` record. GOAL-SSIQ-001 was not edited.
