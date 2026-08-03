# BATCH-046 scope decision — RC-45 bounded toy Executor

Opening authority: `DEC-20260803-002`, implementing the durable
`GOAL-ECDLP-001.next_action` after BATCH-045.

This batch executes the frozen contract
`PA-IT-001-v3-rc45-repair-5` as a bounded toy Executor package against
reserved run IDs `RUN-IT-001-rc45-smoke` and (budget permitting)
`RUN-IT-001-rc45-measure`, using the exact frozen command strings.

## Hygiene vs immutability

- **RT-045-D2 (required for runtime binding):** implement `--amendment`,
  `--run-id`, `--mode`, `--seed`/`--seeds` on
  `experiments/EXP-IT-001/implementation/run_bounded_toy.py` so the frozen
  smoke/measure strings invoke successfully.
- **RT-045-D1 (deferred):** residual colon→dict acceptance/metrics items
  cannot be quoted without editing the frozen RC-45 blob or changing the
  frozen `--amendment` path (both would void the PASS snapshot /
  command-binding freeze). Recorded as deferred-by-immutability; not a
  pre-run gate for this batch.

## Claim ceiling

**Toy.** Observations only. No crypto-scale claim, no asymptotic support,
no H-IT-001 status change in the Executor task, no STR, no lane death, no
GOAL completion. All four asymptotic promotion gates remain OPEN.

## Forbid list

- Editing `PA-IT-001-v3-rc45-repair-5.yaml` or `specification.v3.yaml`
- Invoking any entrypoint other than the frozen binding entrypoint
- Touching prior run dirs `RUN-IT-001-bounded-toy`, `RUN-IT-001-rerun`
- Hypothesis status transitions outside the ledger archive
