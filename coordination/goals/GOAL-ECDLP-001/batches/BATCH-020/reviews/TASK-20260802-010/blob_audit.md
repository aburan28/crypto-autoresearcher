# TASK-20260802-010 blob audit

**Verdict: PASS** — the prospective rebind is correctly committed and bound;
the historical path/hash mismatch remains explicitly recorded as a failure of
the old receipt, not silently repaired.

## Committed-byte replay

- `2c171760355d6f1eabe5fc6eb6ef34c9fd535959` has parent
  `2bdec2f9e8b2eb8e1591d68048bb2ae2175d1df7` and exactly the five declared
  added paths. Their SHA-256 values match the snapshot receipt for its four
  source artifacts; the receipt blob itself hashes to
  `61f15b3073389708e9628cb418d56caa12ab80b2f3d7da9c04127028ec0f1432`.
- `71564cc364de0847b825248a95cfb9cede9da255` has `2c171760` as parent and
  explicitly binds that snapshot. Its only later changes are BATCH-020 queue
  renderings; it changes no scientific artifact.
- At `cac4d8b459a44f1561d3f47835562824f7767765`, Git adds
  `ledger/decisions/DEC-20260731-010.yaml` (blob
  `a90164014f9df5e00e7ec51e1651d89f499369ae`, SHA-256
  `b76b7f915cf5625ada84e9e933bfd9919c592e9cd2eb1ec0f4d563820097189e`)
  and does not contain `DEC-20260731-019.yaml`. The remapped current
  `DEC-019` SHA-256 is
  `4253da998f53a39aa8f1d1e407c4c0b41a02767fb950a037a420da7adb625068`.
  Thus exact historical path/hash receipt verification remains `FAIL`.

## Semantic replay and frozen scope

The historical 3,870-byte `DEC-010` becomes byte-identical to the current
3,870-byte `DEC-019` after only these occurring substitutions:
`009→018` (four occurrences), `010→019` (one), and `011→020` (one).
`012→021` has zero occurrences in the historical blob.

The committed diffs for `CTRL-RT025-UNPLANTED.yaml` and
`v2_ctrl_unplanted.yaml` contain decision-reference remaps only. No scientific
parameter or status changes were found. The prospective snapshot did not alter
any immutable prior receipt, review, or scientific-control artifact.

`experiments/EXP-DS-001/runs/RUN-DS-001-ctrl-unplanted-b` does not exist.
No run occurred and this review grants no execution authorization. This audit
is integrity evidence only; it is not mathematical evidence or an experiment
result.
