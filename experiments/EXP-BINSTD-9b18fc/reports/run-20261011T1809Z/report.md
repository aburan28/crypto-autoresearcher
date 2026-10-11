# EXP-BINSTD-9b18fc — run observation report

This is an observations-only execution report. The corrected supervisor entered the frozen two-stage sequence and stopped before Stage 0’s producer process began; Stage 1 therefore remained dependency-gated. No catalog, panel, or scientific result was produced and no research state changed.

## Bound execution

- Goal: `GOAL-ECDLP2M-001`
- Experiment: `EXP-BINSTD-9b18fc`
- Successor plan: `experiments/EXP-BINSTD-9b18fc/trial-plan-v2.json`
- Successor plan SHA-256: `b6f5786eaa9c665fb62f20971274f4213f5fb4bc2e8aad15037c70432d3b4e66`
- Dispatch correction: `CORR-20261011-dace28`
- Approved by: `DEC-20261003-6e578e`
- Executor task: `TASK-20261011-903edd`, claim epoch 1
- Stage 0 run: `RUN-BINSTD-54a677`
- Stage 1 run: `RUN-BINSTD-6e9fde` (not started; dependency waiting)
- Code commit recorded by the supervisor: `2fe6da2d78bf423f982b4a871f8688bcb35e76e3`
- Host: Darwin, Python 3.12.8
- Started: `2026-10-11T18:09:10.972020+00:00`
- Finished: `2026-10-11T18:09:10.986604+00:00`

## Exact command and stage boundary

Stage 0 producer:

```text
python3 experiments/EXP-BINSTD-9b18fc/implementation/run.py --stage 0 --trial-plan experiments/EXP-BINSTD-9b18fc/trial-plan-v1.json --run-dir experiments/EXP-BINSTD-9b18fc/runs/RUN-BINSTD-54a677
```

The Stage 0 checker was bound to the same run directory. The receipt records `status = infrastructure_error`, `detail = Exception occurred in preexec_fn.`, and null producer/checker return codes. All logs are empty. `manifest.yaml` and `raw-result.json` were not created.

Stage 1 was not attempted: its frozen dependency is `stage0-enhanced-diversity-catalog-freeze`, whose state is `needs_reconciliation` after the infrastructure stop. No `stage0/`, `stage1/`, or `RESULTS.md` output was created.

## Controls and limitations

The frozen trial-plan-v1 input, Stages 0-1 command lines, seed, admission floors, twin-meter requirements, scoped `(17,4)` rule, and preferred run identities were preserved in the successor plan. The Stage 0 catalog and twin probe were not reached, so no admission or correlation quantity was measured. This operational receipt is not evidence for or against the BINSTD hypothesis.

## Visual record

There are no comparable measured values. The accompanying diagram records the sequence boundary: Stage 0 requested → pre-execution infrastructure stop → Stage 1 dependency waiting. It is derived from the sealed Stage 0 receipt and the frozen plan dependency.

- [Run directory](../../runs/RUN-BINSTD-54a677/)
- [Execution receipt](../../runs/RUN-BINSTD-54a677/execution-receipt.json)
- [Rendered PDF](report.pdf)
