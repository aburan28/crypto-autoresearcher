# Larger solver validation: compiler-stopped attempt

This report records an operational attempt, not a solver comparison or scientific verdict. The admitted build stopped before any confirmation measurement ran. Larger-cohort recovery and runtime comparison remain unmeasured by this attempt.

- Experiment `EXP-ECDLP-381959`; run `RUN-ECDLP-9f18c9`; goal `GOAL-ECDLP-8be063`; hypothesis `H-ECDLP-15dc5f`.
- Actual source/claim commit: `af72d170c751d4210eec09d6670af43cd4b2743d`.
- Raw records published before this report: `c395a3c6ae40c6647a16a4c1ec4b4541b0bb9a92`.
- Status: `infrastructure_error`, return code 2; no output-checker invocation.
- Supervisor interval: 25 October 2026, 19:06:32.953559–19:07:20.789667 UTC; measured wall envelope 47.836108 seconds.
- Workload requested: 48 fresh curves at 12/14/16/18 subgroup bits and 768 public targets, with a nested 192-target core. None entered the measurement stage.
- Compiler: `g++ (Debian 14.2.0-19) 14.2.0`.
- Custody: all 2,612 receipt-listed artifact hashes checked; 2,613 actual files including the receipt. There are 2,883 required artifact paths; 270 unstarted checker/verification-stage artifacts are absent. No missing file was fabricated.

[Report PDF](report.pdf) · [Observed stages](observations.md) · [Recorded metadata](data/failed-attempt.json) · [Editable timeline](execution.svg).

All report pages and the timeline PDF were visually inspected. `./build.sh` rebuilds only the document and graph from this recorded metadata; it executes no experiment. This is same-session reporting, not an independent scientific review.
