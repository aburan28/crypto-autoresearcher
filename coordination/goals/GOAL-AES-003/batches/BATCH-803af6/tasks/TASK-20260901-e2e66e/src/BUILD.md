# BUILD.md -- TASK-20260901-e2e66e B4 exclusion-toggle audit builds

Base instrument: `coordination/goals/GOAL-AES-003/batches/BATCH-015/tasks/TASK-20260805-d408ac/src/rc8probe_freshfeistel.c`
(copied verbatim into this task's src/ as the derivation base; that file's header documents
its own lineage: harness machinery incl. the trivial-swap exclusion from rc8probe.c
BATCH-007/TASK-20260803-e55757; live-AES arm code from the same; digest formula from
yoyo_sbox_v4.c BATCH-009).

## Sources

| file | EXCLUDE_TRIVIAL | meaning |
|---|---|---|
| src/rc8probe_b4_on.c  | 1 | standard campaign build, trivial-trial exclusion ENABLED |
| src/rc8probe_b4_off.c | 0 | audit build, exclusion deliberately DISABLED |

`src/rc8probe_b4_off.c` was produced from `src/rc8probe_b4_on.c` by a script that performs
exactly one string replacement (`#define EXCLUDE_TRIVIAL 1` -> `#define EXCLUDE_TRIVIAL 0`),
verified by `diff` to change exactly that one line (src/INDEPENDENCE_AUDIT.md).

Changes relative to the base instrument (see PREREGISTRATION.md section 3):
1. the EXCLUDE_TRIVIAL toggle at the two exclusion sites in worker();
2. receipt augmentation identical in both builds (trivial-trial index log with computed W;
   hit-log entries carrying W; fields exclude_trivial_build, build, task_id,
   trivial_trials, trivial_trials_logged, trivial_log_overflow, trivial_log_cap_per_thread;
   hit_trials_logged corrected to sum across threads -- the base instrument printed only
   thread 0's count while its hit_trials array covered all threads; the corrected field is
   receipt-side only and cannot change any counting).

## Build commands (this task, Apple clang version 17.0.0 (clang-1700.0.13.5), arm64, macOS)

```
cc -O3 -pthread -o src/rc8probe_b4_on  src/rc8probe_b4_on.c  -lm
cc -O3 -pthread -o src/rc8probe_b4_off src/rc8probe_b4_off.c -lm
```

Both compiled clean (no diagnostics) at 2026-09-01T17:24:19Z. Binary sizes identical
(51152 bytes each).

## Run command shape

```
./src/rc8probe_b4_{on,off} arm <name> <oracle=aes|freshfeistel> <rounds> <amask> <smask> <log2N> <seed> <armid> <threads>
```

B4 arms (frozen campaign-standard spec of this seat, per PREREGISTRATION.md section 4):
`<rounds>=5 (aes) / 0 ignored (freshfeistel)`, `amask=1 smask=1 log2N=30 seed=531001 armid=1 threads=2`.
