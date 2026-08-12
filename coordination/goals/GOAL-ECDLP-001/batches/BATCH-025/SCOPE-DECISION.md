# BATCH-025 scope decision

**Selected:** Re-author executable `CTRL-NULL-OBJECT-STRUCTURE-DIRECTION-R2` under
`PA-DS-001-v2-ctrl-structure-null-r2` discharging **RT079-B3 / RT070-B3**.

**Why not pivot:** SG-ECDLP-002 / IDEA-20260731-008 is **dominated_by** finishing
this residual. BATCH-024 RC-24 non-execution (DEC-022) failed because the admitted
snapshot archived `abandoned_before_archive` stubs — an integrity/authoring
failure, not scientific discharge of RT079-B3. `R_null≪1` on EV-DS-007 cell
16/128/4/102 still blocks any structure reading of H-DS-001. Pivoting leaves that
blocking uncertainty open. Concurrent uncommitted EXP-IT-001 / H-IT-001 WIP is
**not official** and is not a substitute freeze.

**Does not edit:** Abandoned BATCH-024 stub blobs at `32165e30`
(`v2_ctrl_structure_null.yaml` / `CTRL-NULL-OBJECT-STRUCTURE-DIRECTION.yaml`
with `abandoned_before_archive`). Fresh `-r2` paths only.

**Deferred:** CTRL-RT025-CI-IDENTITY, CTRL-RT025-SPARSE-P-SUCCESS.

**Claim ceiling:** toy. No STR. H-IC-001 / H-STR-002 untouched. Quarantine stands.
