# BUILD.md — TASK-20260901-92672b

Round count is parameterized at a single macro point in
`src/rc8probe_feistel_rk.c` (the ONLY structural edit vs the archived RC-D
source, see `src/diff_vs_archived.txt`):

```c
#ifndef FEISTEL_ROUNDS
#define FEISTEL_ROUNDS 16
#endif
```

Compiler on this host: `cc`, `gcc`, and `clang` are all Apple clang 17.0.0
(clang-1700.0.13.5, arm64-apple-darwin25.6.0). Flags match BATCH-014's
archived build line (`gcc -O3 -pthread`, per the archived source header).
All commands run from the worktree root with
`T = coordination/goals/GOAL-AES-003/batches/BATCH-7939d0/tasks/TASK-20260901-92672b`.

| r | exact build command |
|---|---|
| 4 | `gcc -O3 -pthread -DFEISTEL_ROUNDS=4 -o $T/src/rc8probe_feistel_r4 $T/src/rc8probe_feistel_rk.c` |
| 8 | `gcc -O3 -pthread -DFEISTEL_ROUNDS=8 -o $T/src/rc8probe_feistel_r8 $T/src/rc8probe_feistel_rk.c` |
| 16 | `gcc -O3 -pthread -DFEISTEL_ROUNDS=16 -o $T/src/rc8probe_feistel_r16 $T/src/rc8probe_feistel_rk.c` |
| 32 | `gcc -O3 -pthread -DFEISTEL_ROUNDS=32 -o $T/src/rc8probe_feistel_r32 $T/src/rc8probe_feistel_rk.c` |
| verbatim RC-D control (no -D; archived file compiled in place) | `gcc -O3 -pthread -o $T/src/rc8probe_feistel_verbatim coordination/goals/GOAL-AES-003/batches/BATCH-014/tasks/TASK-20260805-b95720/src/rc8probe_feistel.c` |
| AES arm instrument (BATCH-015's archived source, compiled in place) | `gcc -O3 -pthread -o $T/src/rc8probe_freshfeistel coordination/goals/GOAL-AES-003/batches/BATCH-015/tasks/TASK-20260805-d408ac/src/rc8probe_freshfeistel.c -lm` |

CLI semantics (unchanged from RC-D):
`./rc8probe_feistel_r<r> detcheck <seed>` and
`./rc8probe_feistel_r<r> arm <name> <rounds_ignored> <amask> <smask> <log2N> <seed> <armid> <threads>`.
The `<rounds_ignored>` argv field stays ignored (reported as
`rounds_field_ignored_input`); the actual round count is the compile-time
`FEISTEL_ROUNDS`, reported in every arm JSON as `feistel_rounds_actual`.

Note: the `-DFEISTEL_ROUNDS=16` variant and the verbatim control differ only
in how the same value 16 is supplied; their outputs are required to be
byte-identical (PREREGISTRATION.md §2 binding parity gate).
