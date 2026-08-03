# TASK-20260730-063 composition report

**Goal:** GOAL-SSI-001 / BATCH-023  
**Decision / evidence:** DEC-20260730-020 / EV-SSI-022  
**Package:** FC0-EXT-PKG-SSI-001 (frozen; BATCH-021)  
**Scaffold (read-only):** BATCH-022 / TASK-20260730-059  
**Revision:** `c66042444d434091c2f0a91e1c931976d5ffe8a3`  
**Runs:** 1 / `maximum_runs: 1`  
**Compute:** zero curve / isogeny / quantum-circuit

## Objective (executed)

Deepen F_* composition and peak-stage live-set accounting against
FC0-EXT-PKG-SSI-001 scaffolding without numeric widths, τ invention, or
QUERY_MEMORY clearance.

## Method

1. Read-only import of BATCH-022 `scaffold` via write-scope
   `composition_harness` (path insert; BATCH-022 tree not modified).
2. Exercise every recovery_spec `F_*` FailureChannel stub; record
   `scaffold_channel_wired` vs `inclusion_into_common_F:
   checklist_only_not_justified`.
3. Walk stages `preparation`, `sieve_attempt`, `recovery`,
   `tail_verification` with `StageLiveSetTracker` membership checks.
4. Peak = max over stage symbolic object counts (not sum; not bytes).
5. Harness: `python3 -m composition_harness.run_harness` from this task
   directory → 4/4 tests OK (`composition_harness/harness_receipt.json`).

## F_* composition outcomes

| Constituent | BATCH-017 | BATCH-023 scaffold | Inclusion into common F |
|---|---|---|---|
| F_input | specified_not_instantiated | scaffold_channel_wired | checklist_only_not_justified |
| F_oracle | specified_not_instantiated | scaffold_channel_wired | checklist_only_not_justified |
| F_cleanup | specified_not_instantiated | scaffold_channel_wired | checklist_only_not_justified |
| F_stop | specified_not_instantiated | scaffold_channel_wired (τ rejected) | checklist_only_not_justified |
| F_recovery | specified_not_instantiated | scaffold_channel_wired | checklist_only_not_justified |
| F_tail | specified_not_instantiated | scaffold_channel_wired | checklist_only_not_justified |
| F_verify | specified_not_instantiated | scaffold_channel_wired (no-crypto) | checklist_only_not_justified |

- Union checklist `F_* ⊆ F`: still **scaffold_channels_wired_inclusion_still_checklist_only**.
- **F_sim → F:** absent (`maps_to_F: false`); F_sim not in scaffold enum.
- **composition_status:** `fstar_composition_partial` (not clearance).

## Peak live-set outcomes

- Checklist members match recovery_spec / BATCH-017 / BATCH-021.
- Symbolic membership APIs supported: `live_subset_of_stage`,
  `required_members_present`.
- Stage object counts: preparation 4; sieve_attempt / recovery /
  tail_verification 5 each.
- **Peak = max = 5** (stages: sieve_attempt, recovery, tail_verification).
- Mistaken sum 19 **rejected** as peak.
- Numeric widths: **not invented**; peak-byte bound: **unresolved**.
- **peak_liveset_status:** `peak_liveset_partial` (not clearance).

## Disposition and blockers

- **Disposition:** `FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED`
- **QM-STOPPING:** open (no τ / joint finiteness)
- **QM-MEMORY-MAP:** `peak_liveset_partial` (not clearance)
- **QM-ERROR:** `fstar_composition_partial` (not clearance)
- BATCH-020 `no_admissible_pin` retained; CollimationSieve@6f9188e4
  untouched; ttm-v2 retained; BATCH-014 not equated.
- Explicitly **not** `FC0_PIN_COMPLETE_FOR_LATER_NUMERIC_REVIEW`.

## Extra write-scope files (beyond declared artifact_paths)

Coordinator may expand `artifact_paths` before snapshot:

- `composition_harness/__init__.py`
- `composition_harness/scaffold_import.py`
- `composition_harness/f_star_probe.py`
- `composition_harness/peak_live_set_probe.py`
- `composition_harness/test_composition.py`
- `composition_harness/run_harness.py`
- `composition_harness/harness_receipt.json`

## Non-claims

No CollimationSieve API invention; no numeric security; no breakthrough;
no goal completion; no PIN_COMPLETE; closed IDEA-20260725-001/002/003
not reopened. No git commit by Executor.
