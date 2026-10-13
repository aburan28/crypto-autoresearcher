# Attempt-1 archive and replay

`run1.tar.zst` is the complete immutable scientific run tree for attempt 1. It
contains the 400 raw job outputs and receipts, all 25,600 planted-key solve
rows, the exact 35 selftest certificates, compiled solver and build receipt,
host and Git provenance, shuffled plan, normalized records, completed session,
and the 424-entry file seal. The archive itself is not part of the sealed run
tree.

Archive SHA-256 and size:

```text
eaad213c09f70c4c3cc330af20286328e51ab079545abaf5b80feba1b0027505  run1.tar.zst
2,581,190 bytes
```

The sealed run commitment and principal result hashes are:

```text
1318653f04d8c1a8b79d6cd646d0f1a410fe78c5e13c9db2d1700006b7a04d1d  MANIFEST.sha256
0f3099774d4530538763723a735e2244586ab40bfb8589dda9c32cc6413705f8  records.csv
9087c623b85ab0da7dc483deb7d3153eeae1ded8f87c5283b912d36c5e7feee6  analysis.json
```

Extract into a new empty directory, verify the seal, and replay the frozen
analysis. The analyzer supports relocation while still checking the absolute
paths recorded in receipts against the original run root in provenance.

```sh
study_dir=research/isogeny_volcano_m51_rho_20261013
replay_root=/tmp/isogeny-volcano-m51-rho-replay
replay_out=/tmp/isogeny-volcano-m51-analysis-replay
test ! -e "$replay_root"
test ! -e "$replay_out"
mkdir "$replay_root"
tar --zstd -xf "$study_dir/run1.tar.zst" -C "$replay_root"
(cd "$replay_root" && sha256sum --strict -c MANIFEST.sha256)
python3 "$study_dir/analyze.py" \
  --run-root "$replay_root" \
  --output-dir "$replay_out"
```

A clean-room extraction at `/tmp/m51-archive-audit-run1` compared recursively
byte-for-byte equal to the live run tree, contained no symlinks, and passed the
complete seal. Rebuilding the normalized tar/zstd archive produced the same
archive bytes and SHA-256. Analysis of that relocated extraction reproduced
all five CSV outputs byte-for-byte. Independent replay also reconstructed every raw row,
counter identity, scalar, stream, orbit assignment, job/core assignment,
receipt, fixed-orbit interval, hierarchical sensitivity interval, and summary
distribution without discrepancy.

This archive supports only the bounded collision-walk measurements in this
study. It does not establish a causal conductor effect, a usable transfer,
end-to-end ECDLP cost, NIST-scale behavior, or a weak curve.
