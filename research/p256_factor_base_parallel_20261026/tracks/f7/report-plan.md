# F7 second-pass preparation

26 October 2026. Task TASK-20261026-59f4c9 is prepared for balanced genus-two
arithmetic and norm checks. **No second-pass arithmetic panel or pilot has
run.** Root must release the exact source, frozen protocol and real S3 gate
before observation collection.

The proposed panel constructs sixteen fixed rational C points and eight
Frobenius-stable nonsplit degree-two supports, retaining every rejected draw.
It executes sixteen rational add/subtract/double/cancel cases, eight nonsplit
additions, eight associativity checks, and seven prior source pullbacks with
balanced class addition. Principal-divisor, infinity-difference, corruption
and missing-conjugate controls cover exceptions.

The candidate implements full split-model balanced triples `(u,v,n)` with
infinity counterweights. The actual reference reconstructs supports in Fp[i]
and sums their elliptic images. The reference checks norms, and cannot prove
class equality in the norm kernel. The nonzero infinity-difference class with
zero norm is an explicit control against that invalid inference.

See `derivation.md` for the balance convention and root-free norm, and
`literature.md` for primary sources actually read. The existing Sage10.6
even-degree pair arithmetic is not used as an oracle. No plane-quartic
Jacobian arithmetic, component-specific relation solver or advantage claim
is supplied.

Future commands, sequential with F5 in this worker, after root's release:

```text
python3 -B research/p256_factor_base_parallel_20261026/tracks/f7/run.py --out research/p256_factor_base_parallel_20261026/tracks/f7/runs/run-01 --seed 2026102607 --release research/p256_factor_base_parallel_20261026/runtime/releases/TASK-20261026-59f4c9.json
python3 -B research/p256_factor_base_parallel_20261026/tracks/f7/export.py research/p256_factor_base_parallel_20261026/tracks/f7/runs/run-01 --out research/p256_factor_base_parallel_20261026/tracks/f7/export-run-01.json
python3 tools/experiment_protocol.py check-export research/p256_factor_base_parallel_20261026/tracks/f7/export-run-01.json --protocol research/p256_factor_base_parallel_20261026/tracks/f7/protocol.json --verify-files
```

Each fresh run directory retains raw cases, traces, checks, rows, identities,
resource diagnostics and failures. Process clocks are diagnostic, with
`wall_valid=false`. There is no observation export or result before execution;
root will render and inspect the new report PDFs from actual recorded data.
