# Archive and integrity record

`run1.tar.zst` is a deterministic archive of the complete sealed run tree
`/tmp/m51-deep-scan-run-d2dd22d7`. It includes the frozen inputs, 256 shard
receipts and outputs, controls, aggregate output, all 42 endpoint certificates,
selection, commands, host/runtime records, and nested manifests.

## Bound identities

| Object | Bytes | SHA-256 |
| --- | ---: | --- |
| `run1.tar.zst` | 2,445,167 | `ca2e0a60feb67a78ce215f3d88935d385d3812e34a7c3f059bd42560fc622096` |
| sealed root `MANIFEST.sha256` | 161,068 | `86c70ebda1c76f138a00a7b1e27d876222b29d9b9885c1f50f62e609c72ec5ed` |
| frozen input `FROZEN.sha256` | 1,313 | `b5967a1d1ee994e8973259de951297acd2bd623b55cf14230d9422f3a4a14bb4` |
| aggregate `hits.csv` | 3,240 | `79e3e6fadbd6ea50d9ef2f64363962a447293cb3739158685271ddc149df9862` |
| final `selection.json` | 49,179 | `c22aa51a7aaa911f936cf6843ada0bb248a83174551282739891c27674b97b7a` |
| `pairs.jsonl` | 23,951 | `ee1c3470454e3c934d7a07dfe33104d74dd10e03841998336cfb0461d28f3471` |
| `records.jsonl` | 22,392 | `e2f06f30857c5e611200cdbc533950a0917b004520ad9f7b0c52d47b9e0387c3` |
| exact GP executable | recorded in sealed host/runtime evidence | `35b1fc1911407f5e893f5ab6b683ac660d164d5d84223b1d38645ebc96d43379` |

The extracted archive was compared byte-for-byte with the sealed source tree.
Both copies contain 1,665 entries bound by the root manifest, and every entry
passed `sha256sum -c MANIFEST.sha256`.

## Local verification

From this directory:

```sh
sha256sum run1.tar.zst
mkdir -p /tmp/m51-deep-scan-verify
tar --zstd -xf run1.tar.zst -C /tmp/m51-deep-scan-verify
cd /tmp/m51-deep-scan-verify
sha256sum -c MANIFEST.sha256
```

The browser-friendly files under `results/` are exact copies from the sealed
tree except `selected-pairs.csv`, which is a deterministic projection of the
32 selected records in `results/selection.json`. Their hashes are collected in
`RESULTS.sha256` after rendering.

Archive verification establishes byte identity and internal consistency. It
does not by itself establish map evaluation, transfer, ECDLP cost, or weakness.
