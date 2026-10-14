# Attempt-1 archive and replay

`run1.tar.zst` is the complete immutable run tree for the accepted fresh
replication. It contains all 160,000 raw solve rows, the two compiled solver
binaries, compiler logs, source/binary hashes, host receipt, exact shuffled
job plan, 392 per-job receipts, commands, and the completed session manifest.

Archive SHA-256:

```text
37d8abf2d12d51eed53ef013f05bbf8a17028ee51c60355cf1e2f2994fa63eb7  run1.tar.zst
```

The frozen analyzer treats each absolute output path as signed provenance.
Extract into the original empty root; extracting under a different path is
expected to fail the receipt-path check. Never overlay an existing directory.

```bash
RUN_ROOT=/tmp/isogeny-volcano-level-replication-20261013-run1
test ! -e "$RUN_ROOT"
mkdir "$RUN_ROOT"
tar --zstd -xf run1.tar.zst -C "$RUN_ROOT"
python3 analyze.py --run-root "$RUN_ROOT" --output-dir replay-output
```

The accepted analysis was run against that exact root before archiving. A
separate extraction under a temporary path was compared recursively with the
live tree and had no byte differences. The raw-tree hashes independently
reported by `results.json` are:

- `m=37`: `bae5bbe0f77da5c376a43f18a9641e27bc3d95488e8f1a86bb8c62cac64075f8`;
- `m=41`: `0096c753b7e96a5977318482c87455ee9d3166c381b46dcad9644e5f73b54226`.

The archive is outcome evidence for this bounded proxy experiment. It does
not add an isogeny map, price a transfer, or establish a weak curve.
