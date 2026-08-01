# Partition-control attempt log

The deterministic positive control in `partition_control.py` had two
non-evidentiary failed attempts before its completed result.  They are retained
here rather than silently discarded.

1. The sandboxed Sage invocation failed while Sage tried to create a lazy-import
   cache temporary file under `/Users/adamburan/.sage/cache/`.  This was an
   infrastructure permission failure; no matrix case ran.
2. The approved-cache invocation reached the harness but failed before ranking
   because `Matrix.set_column(..., 0)` requires a vector-like value.  The
   harness was corrected to use `[0] * nrows`.  This was an implementation
   failure and has no bearing on the block-rank invariant.
3. The corrected invocation completed.  `partition-control.json` contains 18
   exact equalities: three deterministic matrices, three column-block widths,
   and both unsplit and split-carrier modes.  In every case the accumulated
   carrier rank equals the monolithic M4RI rank.

Canonical successful command:

```text
/usr/local/bin/sage -python experiments/EXP-DREG-001/partition_control.py > experiments/EXP-DREG-001/partition-control.json
```

The exact successful v1 source is retained as `partition_control_v1.py`.

## Version 2

Version 2 added an explicitly row-rank-deficient matrix and an all-zero matrix.
Its first invocation failed during Sage import with system-volume ENOSPC; no
case ran, and the zero-byte redirected output is retained as
`partition-control-v2-enospc.empty`.  After the precanonical DREG scratch data
was moved intact from `/private/tmp` to the external experiment volume, the
same command completed to `partition-control-v2.json`: 24/24 partition checks
matched monolithic ranks `17`, `35`, `64`, and `0`.

```text
partition_control_v1.py             fe64e44d75dd98f428d9c59a51d5fc989daba7d79cf87d1dfdc8ea638979dfad
partition-control.json              e834301f903bb6d1fcbaf34a1c6d41adad8b00c0502f706bd66890ce8c1fea66
partition_control.py (version 2)    f8544bf93e726d76adb227ffec3a8bc0acfb8027343df4982a5c105c41bd2a84
partition-control-v2.json           ce96889d01fa394427566fe6cf2f1b937225c128c30c040b292fbf705687bc52
partition-control-v2-enospc.empty   e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```
