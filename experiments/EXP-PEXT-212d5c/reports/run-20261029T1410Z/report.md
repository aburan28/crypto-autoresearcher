# EXP-PEXT-212d5c run report, 2026-10-29T14:10Z

Executor task TASK-20261024-672126 (lane BATCH-21339c, claim epoch 2, owner
executor-run-pext-20261029). Frozen trial plan experiments/EXP-PEXT-212d5c/trial-plan.json
(plan sha256 9e47c884...1417). Launched with:
  python3 tools/experiment_execution.py run --plan experiments/EXP-PEXT-212d5c/trial-plan.json
          --owner executor-run-pext-20261029 --epoch 2
Host: cloud container, 4 CPUs, 15 GB RAM; CPython 3.13.17 (/usr/bin/python3); rustc present;
no Lean toolchain (lake/elan absent). Seed 20261012 (plan defaults).

## What ran
- regression, RUN-PEXT-fccfb9: 14:10:07Z to 14:16:38Z, driver exit 0.
  Supervisor status invalid_output, published false. check.py not run.
- lean, RUN-PEXT-af1b2a: 14:16:43Z to 14:16:44Z, driver exit 0.
  Supervisor status invalid_output, published false. check.py not run.
- construct, char2, census, analyze: not launched (they depend on regression).

## Why the supervisor refused both
Each refusal detail reads: driver manifest run.code.command =
'/usr/bin/python3 experiments/EXP-PEXT-212d5c/implementation/run.py trial ...'
contradicts the launched argv ["python3", "experiments/EXP-PEXT-212d5c/implementation/run.py", ...].
run.py line 288 writes the command as " ".join([sys.executable, *sys.argv]); the frozen
argv starts with "python3". This is the supervisor's envelope check, not a check.py result.

## Driver-reported values (not validated by the supervisor or check.py)
- RUN-PEXT-fccfb9 raw-result.json /summary: checks 10, failed [], regression_pass true.
- RUN-PEXT-af1b2a raw-result.json /summary: status toolchain_unavailable, built false
  (lean-build.log: "lake not found on PATH or in ~/.elan/bin; Lean lemmas not built").
These are what the driver wrote; because both envelopes were refused they are not
output-validated run results.

## Files not in git
RUN-PEXT-fccfb9/R-n3-q5.jsonl (138,537 B), R-n3-q7.jsonl (355,662 B) and
R-n5-q3.jsonl (265,629 B) exceed the 64 KiB in-git limit for data files and the
artifact store was not reachable from this session. Their sha256 equal the
receipt's artifact_sha256:
  6e4434c7...f7ad17  R-n3-q5.jsonl
  be632ad3...934830  R-n3-q7.jsonl
  1a192b6d...429077  R-n5-q3.jsonl
Copies: s3://setec-astronomy-artifacts/checkpoints/crypto-autoresearcher/
run__20261029-unqualified/20261029T142147Z-ea7687b8c6b8/ (resume checkpoint).

## Records
Run commit b236c88a78 and claim release e2ba05c3ba on branch run/20261029-unqualified.
An earlier attempt (epoch 1, codex-run-20261026-01a179ee) was refused before launch
on a Lean source-hash mismatch and wrote no run records; all hashes matched this time.

## Outstanding
Running again needs run.py's command field to match the launched argv (a versioned
amendment of the frozen implementation) or a supervisor change. The run ids in the
plan are already used by these two directories. Nothing here is evidence about
H-PEXT-d536a1; a refused run is not a mathematical result.
