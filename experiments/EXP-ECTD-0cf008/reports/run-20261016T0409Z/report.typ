#set page(paper: "a4", margin: 17mm)
#set text(size: 9.5pt)
= ECTD relation-yield run report
*Experiment:* `EXP-ECTD-0cf008`  *Hypothesis:* `H-ECTD-e88346`  *Goal:* `GOAL-ECTD-001`
*Session start:* 2026-10-16 04:09 UTC  *Run-record commit:* `3d57867407e9dc59899dbfcee1c53d1eb33c29be`

This is a descriptive run record. It assigns no evidential verdict or hypothesis status. Missing arms are missing data, not zero relation yield.

== Execution and custody
The frozen schedule requested 20 arms with 32,768 distinct nonidentity targets per arm. The supervisor created 16 run directories: 3 `output_validated` and 13 `infrastructure_error`. Four transported-base arms waited for their failed native reference arms and were not launched. The complete per-arm status, run path, timing, recorded values, and failure class are in `data.json`; all raw records are under `../../runs/RUN-ECTD-*/`.

The run used the published epoch-1 claim for `TASK-20261015-1222e4`, the immutable trial plan SHA-256 `cb09e4df4fbc684688c150edaa15eb68eb22c40e14a43c329d389669154b2ed9`, the prepared input manifests, and the public seed commitment at `../../preparation/seed-commitment.json`. Private seed values were not exposed in this run report. Each attempt records input, admission, binary and source hashes. The three sealed attempt receipts record macOS 26.6 arm64, Python 3.13.1, and psutil 7.2.2.

The command that produced the later five attempts was:
```sh
PATH=/Volumes/SSD990/llm/tmp/ectd_git_compat_20261015:$PATH \
PYTHONPATH=/Volumes/SSD990/llm/tmp/ectd_pydeps_20261015 \
python3 tools/experiment_execution.py run \
  --plan experiments/EXP-ECTD-0cf008/trial-plan.json \
  --owner executor-ectd-20261015 --epoch 1
```
The first 11 attempt directories came from the same supervisor invocation without `PYTHONPATH`; all stopped at the missing `psutil` import. Before any run directory existed, the supervisor also refused a sparse-checkout path, one shell selected a Homebrew Python missing PyYAML, and the sandbox refused its `.git` process lock. Those setup refusals produced no scientific trial receipt. The later command used the installed Homebrew Git 2.56.0 through `git-compat.sh` (SHA-256 `73d6eb79e772ad51e38afaaa97483ebdd7c82e5e4f49d9268911ca73ed3c77f4`), which maps the frozen `check-rules --stdin` call to Git’s default-stdin form. The shim passed all 20 intended run paths and rejected an unrelated path.

== Recorded measurements
The following three arms have `output_validated` supervisor receipts. Useful counts and exact finite-population endpoint intervals are copied from each `raw-result.json`. Rank values are copied at the frozen target prefixes 512, 2,048, 8,192, and 32,768. No primary crater/floor ratio can be formed from this partial panel.

- `P29-E2-native` / `RUN-ECTD-c769f1`: 2204 useful targets of 32,768; exact 99.75% endpoint interval for the population useful fraction [0.063148, 0.071545]; rank 37, 143, 256, 256. Phase wall seconds collector/count/verify/interval: 18.14, 16.25, 6.23, 11.57. Sampled CPU seconds: 9.18, 8.72, 3.59, 6.81. Peak sampled RSS bytes across phases: 58490880.
- `P29-E3-native` / `RUN-ECTD-f395a9`: 2191 useful targets of 32,768; exact 99.75% endpoint interval for the population useful fraction [0.062762, 0.071136]; rank 45, 140, 256, 256. Phase wall seconds collector/count/verify/interval: 16.16, 16.36, 6.90, 17.14. Sampled CPU seconds: 9.00, 8.75, 3.44, 6.69. Peak sampled RSS bytes across phases: 58703872.
- `P37-floor-u2-native` / `RUN-ECTD-26d06d`: 2178 useful targets of 32,768; exact 99.75% endpoint interval for the population useful fraction [0.062377, 0.070729]; rank 35, 163, 587, 1578. Phase wall seconds collector/count/verify/interval: 629.83, 186.54, 43.42, 32.19. Sampled CPU seconds: 0.00, 78.36, 0.00, 13.67. Peak sampled RSS bytes across phases: 289783808.

Sampled CPU time in the P37 collector and verifier receipts is recorded as zero; this is a telemetry limitation, not an assertion that those phases used no CPU. The independent ordered-count comparison and reported-triple group-law checks passed for the three validated arms. Transported-base equality against native references was unavailable because the reference arms did not validate.

#image("yield.svg", width: 100%)

The graph plots only the three recorded useful-target counts. P29 E2 and E3 are same-conductor floor checks; the P37 bar uses a rebuilt native base on the u2 coordinate presentation. The bars are descriptive and do not estimate a conductor effect. Graph input is `data.json`; the editable generator is `draw.py`.

== Failures and incomplete coverage
Eleven arm receipts report `infrastructure_error` after `ModuleNotFoundError: No module named psutil`; they have no collector result. Two further arm receipts report `infrastructure_error` after `cannot read resident memory for process` during verifier-phase RSS sampling. Their raw collector/count files and event logs remain in their own directories, but no sealed attempt receipt exists for those two arms. The failed attempts were not overwritten or imputed.

The four `u2-transport` arms remained `waiting_on_dependencies` because their native reference arms lack validated outputs. The 20-arm panel therefore remains incomplete. The next execution requires a separately frozen additive recovery plan with new run IDs for failed arms and the original failed directories retained.

== Run directory index
Every item below is relative to `../../runs/`. The full machine-readable status and exact path appear in `data.json`.

- `P29-crater-native` → `RUN-ECTD-5a22e4/`: `infrastructure_error` (psutil_import_missing).
- `P29-crater-random` → `RUN-ECTD-fd922d/`: `infrastructure_error` (psutil_import_missing).
- `P29-crater-u2-native` → `RUN-ECTD-26c17c/`: `infrastructure_error` (psutil_import_missing).
- `P29-floor-native` → `RUN-ECTD-8231ef/`: `infrastructure_error` (psutil_import_missing).
- `P29-floor-random` → `RUN-ECTD-bf5901/`: `infrastructure_error` (psutil_import_missing).
- `P29-floor-u2-native` → `RUN-ECTD-69b263/`: `infrastructure_error` (psutil_import_missing).
- `P37-crater-native` → `RUN-ECTD-509251/`: `infrastructure_error` (psutil_import_missing).
- `P37-crater-random` → `RUN-ECTD-84a499/`: `infrastructure_error` (psutil_import_missing).
- `P37-crater-u2-native` → `RUN-ECTD-426674/`: `infrastructure_error` (psutil_import_missing).
- `P37-floor-native` → `RUN-ECTD-375652/`: `infrastructure_error` (psutil_import_missing).
- `P37-floor-random` → `RUN-ECTD-4cdc0a/`: `infrastructure_error` (psutil_import_missing).
- `P37-floor-u2-native` → `RUN-ECTD-26d06d/`: `output_validated`.
- `P29-E2-native` → `RUN-ECTD-c769f1/`: `output_validated`.
- `P29-E2-random` → `RUN-ECTD-d14263/`: `infrastructure_error` (rss_sampling_failure).
- `P29-E3-native` → `RUN-ECTD-f395a9/`: `output_validated`.
- `P29-E3-random` → `RUN-ECTD-45ca41/`: `infrastructure_error` (rss_sampling_failure).

The four unlaunched trial IDs are `P29-crater-u2-transport`, `P29-floor-u2-transport`, `P37-crater-u2-transport`, and `P37-floor-u2-transport`. Raw stdout, stderr, process events, receipts, and hashes are preserved in the listed run directories. This report is not an independent evidence review.
