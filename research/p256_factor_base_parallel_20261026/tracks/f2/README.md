# F2 second pass: prepared source, execution gated

Task TASK-20261026-e8fd72. This directory is the exclusive second-pass F2
scope. No first-pass input is edited. Phase A creates source and a draft
protocol; it does not collect the next panel or assert its results.

Read literature.md and derivation.md for the exact assumptions. The full
generic fibre has degree 65,536. Finite relation queries use the frozen
matched M=26 and M=121 domains in the three first-pass families.

One wrapper invocation contains two actual implementation traversals:
producer and reference oracle. Each is one exported row at instance 0,
replicate 0, seed 2026102602. This is not two independent samples. All
internal fixed cases are retained in the shared raw package. Arm clocks
are absent; joint wrapper resource diagnostics have wall_valid=false.

Root must first commit and push the source/locks, pin the actual interpreter
binary and source commit in a fresh protocol.json, freeze and commit it,
complete the real S3 checkpoint gate, and create an explicit release bound
to that frozen protocol. The root-owned runtime/checkpoint_gate.py helper
enforces and serializes that actual gate. A pending question is not approval.

After root Phase B release, from the repository root, with a fresh attempt:

    /workspace/dickson-solver/.venv/bin/python research/p256_factor_base_parallel_20261026/tracks/f2/run.py --out research/p256_factor_base_parallel_20261026/tracks/f2/runs/run-01 --seed 2026102602 --protocol research/p256_factor_base_parallel_20261026/tracks/f2/protocol.json --release research/p256_factor_base_parallel_20261026/tracks/f2/phase-b-release.json

    python3 research/p256_factor_base_parallel_20261026/tracks/f2/analysis.py --run research/p256_factor_base_parallel_20261026/tracks/f2/runs/run-01 --out research/p256_factor_base_parallel_20261026/tracks/f2/reports/run-01 --protocol research/p256_factor_base_parallel_20261026/tracks/f2/protocol.json

    python3 research/p256_factor_base_parallel_20261026/tracks/f2/export.py --run research/p256_factor_base_parallel_20261026/tracks/f2/runs/run-01 --analysis research/p256_factor_base_parallel_20261026/tracks/f2/reports/run-01 --protocol research/p256_factor_base_parallel_20261026/tracks/f2/protocol.json --out research/p256_factor_base_parallel_20261026/tracks/f2/exports/run-01/export.json

    python3 tools/experiment_protocol.py check-export research/p256_factor_base_parallel_20261026/tracks/f2/exports/run-01/export.json --protocol research/p256_factor_base_parallel_20261026/tracks/f2/protocol.json --verify-files

    python3 tools/experiment_protocol.py flow research/p256_factor_base_parallel_20261026/tracks/f2/exports/run-01/export.json

The runner refuses a nonfresh output directory, draft/unpinned source,
changed locks, wrong interpreter, wrong seed, absent/wrong release or failed
checkpoint gate before creating observation output. Mathematical imports
occur only after those guards. The panel has a 115-second internal watchdog
and five seconds of the card's 120-second envelope reserved for sealing,
one process and 2 GiB address-space limit. A watchdog leaves an unknown
incomplete panel, not an empty solution set. Every later attempt needs new
paths and prospective protocol treatment when its scientific bytes change.

The generated raw manifest is sealed. Analysis and exports live beside it;
never add files inside the sealed raw directory. Root renders and inspects
the fresh report PDF, checkpoints completed output, and snapshots before
fresh independent review. Neither schema validation nor successful
execution claims canonical scientific admission or official promotion.
