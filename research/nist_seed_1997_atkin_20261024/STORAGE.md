# Lossless storage correction for the new PR artifact

24 October 2026 UTC. The PR's `repo_size` check rejected the newly added 3.6 MiB uncompressed `runs/scan-v1/raw.json`. The canonical `tools/artifact_store.py compact --no-offload` operation now stores that logical artifact as [raw.json.gz](runs/scan-v1/raw.json.gz). No source, protocol, arithmetic value, receipt or existing verification record changes.

The content SHA-256 remains `c01df39dc5706706834c2f91a4ac0df5c6cf7266c3225b47b672b7019d4e0e7d`. [storage-20261024.json](storage-20261024.json) records the exact command, stored/content digests and sizes, byte-for-byte round trip and agreement with both original receipt and completed verification. The restored data still has nineteen rows and 3,173 real cells. The canonical reader is:

```sh
python3 tools/artifact_store.py cat research/nist_seed_1997_atkin_20261024/runs/scan-v1/raw.json
python3 tools/artifact_store.py verify research/nist_seed_1997_atkin_20261024/runs/scan-v1/raw.json
```

The producer, verifier and renderer are frozen and still read the physical raw filename. For a verifier replay, copy the `scan-v1` directory to a fresh scratch directory and run `gzip -d` on the copied `raw.json.gz`; then pass that materialized run directory and a fresh output directory to the unchanged `verify.py`. For rendering, use a scratch checkout, decompress the stored file there and run the unchanged `render.py`. Decompression removes the compressed form only in that scratch copy. Do not commit the materialized large artifact or keep two stored forms in the archived tree.

The existing cutoff graph, inference diagram and report PDF were checked and stay unchanged because the decompressed bytes are identical. This is a storage correction to satisfy the PR gate, not new experimental evidence, a mathematical rerun or a scientific-status transition.
