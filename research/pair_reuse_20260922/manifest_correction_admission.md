# Manifest schema-correction admission — P9 scientific snapshot prerequisite

**Decision:** prospectively approve one additive schema correction for
`RUN-KIC-ba86d9` and registration of its frozen supersession entry. This is
metadata/custody work under queued scientific snapshot `TASK-20260922-546d42`.
It is independent of hypothesis disposition, timing interpretation, review, or
any scientific claim.

## Immutable original and exact correction

The original generated manifest remains untouched at its original path and hash:

```text
SHA-256 5526c489d1158d98efbf9466f62bd07c2cf21ef20e048aae239db56a37bd4fee
```

It contains certificate kind `finite point decomposition replay`, which is not
in the schema enum `discrete_log | decomposition | none`. The additive
`manifest_v2.yaml`, SHA-256
`91b2fc619c75ab9f66e1f7ef0934dee991793654e8c56e0d2bf21175dbb835a8`, may
change only that value to `decomposition` and add explicit
`run.supersedes { path, sha256, relation }` plus `supersession_note`.

Every measured value, source/input/command/outcome field, receipt binding, and
run result must remain byte-equivalent to the original other than these declared
schema/supersession fields. The correction authorizes no rerun, remeasurement,
source edit, result substitution, or scientific reinterpretation.

## Registry admission

`research/pair_reuse_20260922/run_supersession_entry.json` is the frozen
archived artifact binding both manifest hashes and the additive schema
completion. Root may append exactly the corresponding single entry to mutable
`tools/run_supersession_registry.yaml`, after scope-checking the entry,
companions, and reverse binding. No unrelated registry entry or control-plane
field may change. The frozen entry JSON, v2 manifest, original manifest, and
registry entry must cross-reference consistently in the scientific snapshot.

## Native installation receipt

The prelaunch copied native binary mode correction `0644` to `0755` is accepted
as an installation metadata repair only when
`native_installation_receipt.json` and `install_native.py` record identical
binary bytes `ab068745...`. It changed no source or scientific process and does
not alter any result or custody hash of the executable bytes.

This admission is owned by `TASK-20260922-546d42`; it does not append to or
rebind the completed protocol/archive. It carries zero runs, 2 GiB memory, null
wall-clock budget, no fallback or Bedrock, and standing authorization. Root owns
Git, registry mutation, scope checks, and snapshot creation.

**Citation provenance:** all metadata and installation facts are `internal`.
