# Continuation allocation after the 2026-10-05 container restart

Written 2026-10-05 before 13:23:40Z by the continuation executor session, BEFORE any continuation run
started and before any Stage-2 outcome other than the completed RUN-SEMBIN-24e9d9 (30,2,2,15)
and the four partial records of the interrupted RUN-SEMBIN-633f0c existed. It adds to
`schedule-allocation.md` and does not revise it. No item depends on an observed SOLV4 outcome.

## Run inventory at restart (13:18Z)

| run | content | state |
|---|---|---|
| RUN-SEMBIN-a0d778 | Stage-1 engine gate (SR-2) | completed_valid, manifest present |
| RUN-SEMBIN-745bf5 | Stage-1 builder check | completed_valid, manifest present |
| RUN-SEMBIN-5cf90a | Stage-1 smoke, first attempt | aborted_infrastructure by the earlier executor (sols.c defect, dev-log D18), manifest present; terminal, superseded by 814631 |
| RUN-SEMBIN-814631 | Stage-1 (40,2,2,20) smoke | completed_valid, manifest present |
| RUN-SEMBIN-24e9d9 | Stage-2 (30,2,2,15) | completed_valid, manifest present |
| RUN-SEMBIN-633f0c | Stage-2 (40,2,2,20) | INTERRUPTED by the container restart: no manifest, no raw-result; note `runs/RUN-SEMBIN-633f0c.INFRA-INTERRUPTION.yaml` |

## Continuation (implementation/run_schedule_continue.sh)

| order | run id (new) | cell | args as in run_schedule.sh | note |
|---|---|---|---|---|
| 2 | RUN-SEMBIN-cfd1a7 | (40,2,2,20) | 6.5 h, primary 0.55, null T=2 | re-execution superseding 633f0c; full allocation again (the 0.32 h spent in 633f0c is counted as spent session time below, not deducted from the cell) |
| 3 | RUN-SEMBIN-20fdd9 | (21,3,3,7) | 2.0 h | null: zero allocation |
| 4 | RUN-SEMBIN-5bea99 | (45,2,2,23) | 3.5 h | null O-CENSORED by OP-NULL (N = 46) |
| 7 | RUN-SEMBIN-9d540c | (40,2,2,21) | 2.0 h | stage3 off-diagonal |
| 8 | RUN-SEMBIN-bb6ee8 | (40,2,2,22) | 2.5 h | stage3 off-diagonal |
| extra | RUN-SEMBIN-32150f | (50,2,2,25) | 1 SAT + 1 UNSAT | only if session time remains |
| extra | RUN-SEMBIN-b666d2 | (25,3,3,9) | 1 SAT + 1 UNSAT | only if session time remains after 32150f |

The ids in `run_schedule.sh` for items 3-8 (RUN-SEMBIN-2fa33f, -ccbf15, -8d8b15, -8c9c1a) were
never instantiated (no directory). They are not used; every continuation id was minted fresh
with `tools/allocate_id.py --next run --area SEMBIN` and confirmed with `--check`.

## "Wall time remains" (extras rule) -- interpretation, declared now

`schedule-allocation.md` gives the extras only "if wall time remains after item 8" and does not
say how session time is counted. Reading fixed here, before any continuation outcome:
remaining = 86,400 s (handoff budget) - 12,083 s (executor run wall from the first Stage-1 run
start 06:12:28Z to the interruption 09:33:51Z) - continuation wall elapsed. The host outage
(09:33Z-13:17Z) and the time before the first Stage-1 run (Stage 0 and development) are not
counted. Expected remaining after item 8 is about 86,400 - 12,083 - 59,400 = ~14,900 s, so the
extras are expected to start. The extra cell's allocation is the remaining time. The
deadline only stops new instances from starting, and per-process caps (8 GiB, 28,800 CPU-s)
still apply. This reading is a protocol interpretation (implementation.md D-14) and is
submitted to the Coordinator with the others.

## Restart resilience

Each instance record is appended to `runs/<RUN>/instances.jsonl` when it completes, and
classifications go to `classify.jsonl`. If the container restarts again, the continuation
script refuses to resume a run directory that has no manifest (exit 4). The next session leaves
that directory as found, writes an interruption note beside it, and re-executes under a new
run id, as was done for 633f0c. Progress is logged to `implementation/schedule-continue.log`.
