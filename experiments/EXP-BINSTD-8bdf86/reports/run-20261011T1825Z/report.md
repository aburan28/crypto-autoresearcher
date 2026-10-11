# Run report — EXP-BINSTD-8bdf86

This is an observations-only report for the two trials executed in this run session. It does not promote, weaken, or review the hypothesis. Both trials completed under the frozen Stages 0–1 protocol in a Linux container, and both independent checker invocations returned zero.

## Identity and custody

- Experiment: `EXP-BINSTD-8bdf86`
- Hypothesis: `H-BINSTD-5a212b`
- Goal: `GOAL-ECDLP2M-001`
- Approval: `DEC-20261003-555f72`
- Additive dispatch correction: `CORR-20261011-cd4279`
- Successor task: `TASK-20261011-98ecf7`
- Successor plan SHA-256: `4aada724b476b9b8792637d28948f7811abba918a325b8649cb612d404f0e729`
- Execution commit recorded by the supervisor: `9169922cf5462927f36632b33648705642c0aaa8`
- Host: Linux, Python `3.11.17`, inside the local `crypto-ci-python:20261008` Docker image
- Container boundary: 1 CPU, 1 GiB RAM, swap capped at 1 GiB, 64 PIDs, network disabled
- Working tree state: tracked inputs were at the recorded commit; pre-existing untracked session files were not part of the declared inputs
- The supervisor applied the plan’s 512 MiB per-process `RLIMIT_AS` ceiling to both trials.

The exact supervisor commands and hash-bound inputs are in each run directory: [`RUN-BINSTD-969bcc`](../../runs/RUN-BINSTD-969bcc/) and [`RUN-BINSTD-6a482f`](../../runs/RUN-BINSTD-6a482f/).

## Trial accounting

| Stage | Run ID | Recorded start | Recorded finish | Derived wall time | Supervisor status | Checker |
|---|---|---:|---:|---:|---|---|
| 0 protocol freeze | `RUN-BINSTD-969bcc` | 18:25:20.475599Z | 18:25:20.659547Z | 0.183948 s | `output_validated` | exit 0 |
| 1 admissibility and yield gate | `RUN-BINSTD-6a482f` | 18:25:27.009172Z | 18:25:27.212941Z | 0.203769 s | `output_validated` | exit 0 |

The wall times above are derived only by subtracting the supervisor’s recorded timestamps. CPU time, peak RSS, and a per-cell rate spread were not recorded by this supervisor and are therefore missing. No rate sample was produced because both cells stopped at the structural admissibility gate.

## Frozen inputs and controls

Stage 0 recorded the following frozen parameters:

- `n = 17`, `ell = {3, 4}`, target count `40`, seed `9049049433885666`
- band threshold `1.25`
- solver pin `exhaustive_fb_sum_m3_stdlib_gf2`
- controls `ctl_matched_dim_open_V`, `ctl_matched_random_targets`, `ctl_shared_solver_pin`, `ctl_no_posthoc_band_edit`, and `ctl_admissible_phi_dims_certified`
- Stage 2 (`n ∈ {23,31}` plus the Boolean null) was not authorized and was not run.

The stage-0 artifacts are [`freeze.json`](../../stage0/freeze.json), [`preregistered-predictions.json`](../../stage0/preregistered-predictions.json), and [`solver-pin.json`](../../stage0/solver-pin.json). The stage-0 observation was `S0-FREEZE-OK`.

## Recorded observations

The factorization artifact records irreducible degrees `[1, 8, 8]` for `x^17 − 1` over `F₂`. The derived subset-sum dimension set is `[0, 1, 8, 9, 16, 17]`.

The stage-1 artifact records two structural cells:

| Frozen cell | Label | Status | Ratio |
|---|---|---|---|
| `ell = 3` | `E-NO-TAU-CLOSED-AT-ELL` | structural | missing; `3` is not admissible |
| `ell = 4` | `E-NO-TAU-CLOSED-AT-ELL` | structural | missing; `4` is not admissible |

These are the implementation’s recorded cell labels, not a comparison of measured yield rates. The complete machine-readable result is [`raw-result.json`](../../runs/RUN-BINSTD-6a482f/raw-result.json), and the checker output is [`check.stdout.log`](../../runs/RUN-BINSTD-6a482f/check.stdout.log).

The visual record is [`graph.svg`](graph.svg), with its editable data in [`graph-data.json`](graph-data.json). It shows the executed pipeline and the structural gate because no pair of admissible arms produced comparable rate values.

## Scope and missing data

- No exhaustive factor-base-sum rate was evaluated for either frozen cell.
- No ratio, uncertainty interval, spread, or sample distribution exists for this run.
- The result is scoped to the finite `n=17`, `ell={3,4}` protocol and its declared implementation.
- This run does not establish a conclusion outside the approved experiment scope.

## Supporting artifacts

- Stage 0 run: `experiments/EXP-BINSTD-8bdf86/runs/RUN-BINSTD-969bcc/`
- Stage 1 run: `experiments/EXP-BINSTD-8bdf86/runs/RUN-BINSTD-6a482f/`
- Stage 1 admissibility artifact: `experiments/EXP-BINSTD-8bdf86/stage1/admissible-phi-dims.json`
- Stage 1 yield matrix: `experiments/EXP-BINSTD-8bdf86/stage1/yield-matrix.json`
- Human-readable result: `experiments/EXP-BINSTD-8bdf86/RESULTS.md`
