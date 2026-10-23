# k11 bounded runner implementation check

Recorded 2026-10-17 UTC. This note covers implementation readiness for
`EXP-ICPERF-018b0c`, which remains `review_required` and execution unauthorized.
The complete input preparation and its independent point replay are in
`docs/reports/2026-10-17-icperf-k11-common-target-inputs.md`.

## Binary interface check

The pinned `/opt/homebrew/bin/cryptominisat5` SHA-256 is
`a3f85c3709b5e2a040bf82a4a604d1c7b9f10219bbf180a9e0f72319a2e892ac`;
its reported version is 5.14.7. The exact two-variable synthetic XCNF was
`p cnf 2 2\n1 0\nx1 2 0\n` (input SHA-256
`0acb3e1faca829108d13c843665d661cdd2f9adb2877a66f9ce84c9b38407aff`).
The specified `--verb 0 --threads 1 --maxsol 1 --random 20261017 --maxtime 2`
interface returned code 10, `s SATISFIABLE`, and complete model `v 1 -2 0`.
That model satisfies the CNF unit and native XOR row. The exact command,
stdout/stderr, binary version, and hashes are in
`implementation/solver_interface_receipt.json`; its temporary input path is
reconstructible from the embedded XCNF bytes.

## Runner and checker boundary

`implementation/execute.py` requires an adapter-created launch, a frozen and
approved experiment, an exact source-bound trial plan, and committed input
hashes. It first runs both separately planted positive formulas and gates the
eight-target, 64-formula natural panel on both full-point certificates. Each
call has a 300-second wall guard, 8-GiB sampled RSS guard, 64-primary-model
cap, fixed seed and single solver process. It preserves raw attempts and
records decompression, solver-process, point-filter, host-admission, and total
stage time separately. Censoring and unproved solver exhaustion retain their
own labels.

`implementation/verify_run.py` reads retained stdout and serialized XCNF,
rechecks complete Boolean models, reconstructs blocked formulas, and
independently recomputes GF(2^61) point sums and projected rows. The archived
planted models pass this checker in both base arms. Changing retained stdout
causes rejection; the targeted regression suite reports three passing tests.
These are correctness checks on known fixtures and synthetic solver input.
They measure no natural relation yield, degree of regularity, rank, linear
algebra, target solve, or end-to-end advantage.

The remaining approval work is to bind exact source hashes and trial commands
in a plan and runbook or record an implementation-tier reason, reconcile the
goal lanes and archive ancestry, and obtain the Coordinator's approval
decision only after `newest_experiments` reports `ready`. Scientific calls
must then enter through the repository's `run` path and its independent review.
