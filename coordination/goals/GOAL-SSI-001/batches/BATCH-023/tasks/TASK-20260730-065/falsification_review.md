# Falsification review — TASK-20260730-065

## Verdict

**CONFIRM.** Snapshot `e6044cbf` durably archives a Coordinator-authorized
write-scope F_* composition and peak live-set deepening package under
`DEC-20260730-020` / `EV-SSI-022`. Independent checks reproduce: all seven
recovery_spec constituents (`F_input`, `F_oracle`, `F_cleanup`, `F_stop`,
`F_recovery`, `F_tail`, `F_verify`) are `scaffold_channel_wired` with
`justified_by_implemented_end_to_end_path: false` and inclusion
`checklist_only_not_justified` (`composition_status=fstar_composition_partial`);
stage membership walks pass against BATCH-022 `StageLiveSetTracker` with
**peak = max = 5** symbolic object slots (mistaken sum 19 rejected; no
numeric widths / peak-byte bound; `peak_liveset_status=peak_liveset_partial`);
harness `python3 -m composition_harness.run_harness` passes **4/4** tests with
`collimation_sieve_apis_invented: 0` and explicit rejection of τ /
numeric-width invention. Disposition
**`FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED`** is retained with QM-STOPPING
still open and QM-MEMORY-MAP / QM-ERROR `peak_liveset_partial` /
`fstar_composition_partial` (`reconciled: false`, `clearance: false`);
CollimationSieve@`6f9188e4` remains `host_gap_certified` without API
invention; BATCH-020 `no_admissible_pin` retained for external hosts;
BATCH-014 is not equated; no numeric, breakthrough, PIN_COMPLETE, or
completion creep is present.

Inference: requested `review-xhigh`; resolved **Cursor Grok** with
`fallback_used: true` because review-xhigh was unavailable;
`independent_session: true` (this session did not originate
TASK-20260730-063).

## Durable snapshot

Git independently establishes that
`e6044cbf9141ed7ff6591d5769015e51fd22364a` is an ancestor of review-bind
HEAD `8e702b03b22554fdc715f018d89cd531ca012146`, and that HEAD equals the
declared bind commit. Parent of the archive commit is
`ce83d8f067894c482748e2cbe90f9bba3e3cdb0d`, matching the receipt. The archive
commit changes exactly the twelve producer sources under
`tasks/TASK-20260730-063/` plus
`archives/TASK-20260730-064/snapshot-receipt.json` (thirteen paths). No
undeclared extras; no CollimationSieve sources; no BATCH-022 scaffold edits;
no BATCH-021 freeze edits; no ledger status edits. Receipt
`source_path_sha256` values recomputed from `git show` match all twelve
producer artifacts. The receipt still says `pending_post_commit` with null
`commit_sha`; ancestry, path scope, and hashes establish the reviewed
snapshot anyway. Producer `harness_receipt.json` was restored to the
committed hash after the independent harness re-run (which rewrites that
file).

## Attack surface results

| Attack | Result |
|---|---|
| CollimationSieve@6f9188e4 API invention | **Not detected.** Negative control retained as `host_gap_certified`; composition harness read-only imports BATCH-022 scaffold; coverage reports `collimation_sieve_apis_invented: 0`; archive commit does not touch CollimationSieve sources. |
| Fake F_* inclusion (`justified_by_implemented_end_to_end_path: true` on stubs) | **Not detected.** All seven constituents have `justified_by_implemented_end_to_end_path: false` and inclusion `checklist_only_not_justified`; harness summary `any_inclusion_into_common_F_justified: false`. |
| Invented τ or numeric peak-byte widths | **Not detected.** Scaffold rejects `invents_tau=true` and `numeric_width` on `M_tail`; peak_byte_bound unresolved; peak=5 is symbolic object-count max only. |
| Illicit QUERY_MEMORY clearance or QM-STOPPING closure | **Not detected.** Disposition unreconciled; `QUERY_MEMORY.cleared: false`; QM-STOPPING open; BATCH-018 FAIL retained. |
| Equating BATCH-014 with ttm-v2 panel | **Not detected.** `equated_to_batch014: false`; ttm-v2 retained as finite ideal-choice only. |
| Numeric security / breakthrough / completion creep | **Not detected.** Claim boundaries and non-claims forbid security bits, breakthrough, and goal completion; creep-token hits appear only in negation or rejection tests. |
| Treating `fstar_composition_partial` / `peak_liveset_partial` as MEMORY/ERROR clearance | **Not detected in producer fields.** Structured fields set `reconciled: false` and `clearance: false` for both blockers; reports state “not clearance.” Residual risk is downstream ledger wording. |
| Snapshot ancestry / undeclared extras | **Confirmed clean.** Ancestor relation holds; thirteen-path scope only; hashes match. |

## Independent harness re-run

- **Working entrypoint:** from
  `.../BATCH-023/tasks/TASK-20260730-063`, run
  `python3 -m composition_harness.run_harness` → **4 tests OK**,
  all seven F_* channel-wired, inclusion unjustified, peak=5 with sum-19
  rejected, τ / numeric-width invention rejected, `collimation_sieve_apis_invented: 0`.
- Producer receipt restored after re-run; committed SHA-256
  `2553865e72ef09c5cf42bc55f7288025983bc26967783a07a5295ec7f65d88f7`
  unchanged; producer tree left clean (no permanent dirtying).

## Independent composition checks (summary)

- **F_*:** each recovery_spec constituent is exercisable on BATCH-022
  FailureChannel stubs (malformed input → `F_input`; cleanup / destroy
  discipline → `F_oracle` / `F_cleanup`; stopping breach + τ rejection →
  `F_stop`; recovery precondition → `F_recovery`; tail exhaustion + width
  forbidden → `F_tail`; no-crypto Verify false/fault → `F_verify`). Union
  ⊆ F remains checklist-only. `F_sim→F` absent.
- **Peak:** stage checklist matches recovery_spec / BATCH-017 / BATCH-021;
  membership APIs `live_subset_of_stage` / `required_members_present`
  supported; counts 4/5/5/5; peak = max = 5; sum 19 rejected; widths not
  invented.
- **Package identity:** write-scope `composition_harness` under
  TASK-20260730-063; BATCH-022 scaffold read-only; BATCH-021 freeze
  unchanged; BATCH-020 `no_admissible_pin` retained; CollimationSieve
  untouched.
- **Disposition consistency:** C2 remains live (STOPPING); C3 global status
  unresolved under `peak_liveset_partial`; error map remains live under
  `fstar_composition_partial` with `F_sim→F` uninstantiated.

## Why CONFIRM rather than REVISE

The package does what DEC-20260730-020 / EV-SSI-022 required: deepen F_*
composition and peak-stage live-set accounting against FC0-EXT-PKG-SSI-001
scaffolding with checkable probes, without inventing CollimationSieve APIs,
without clearing QUERY_MEMORY, and without claiming justified F_* ⊆ F,
PIN_COMPLETE, or numeric widths. Honest `fstar_composition_partial` /
`peak_liveset_partial` with open QM blockers is the supported reading.
Residual issues are non-blocking wording qualifications (receipt pending
fields; `classification.artifact_commit_reference` naming the
CollimationSieve tip; keep `fstar_composition_partial` /
`peak_liveset_partial` / `scaffold_channel_wired` / peak=5 distinct from
clearance, justified inclusion, and peak-byte bounds), not defects in the
producer claim boundary.

## Scope and disposition

No Pollard-rho, BSGS, or specialized-baseline resource comparison is
admissible. Peikert's CollimationSieve remains the closest specialized
baseline; composing against a separate in-repo freeze package / BATCH-022
scaffold does not change its accounting. KN-TECH-051 / KN-OPEN-014 remain
the locus of CSIDH quantum-security dispute; this package supplies no
security number.

Partial composition with open QM blockers is not QUERY_MEMORY clearance,
not QM-STOPPING / MEMORY / ERROR closure, not cryptographic Verify, not
justified F_* ⊆ F, not PIN_COMPLETE, not a durable negative cryptanalytic
boundary for FC0 in general, and not lane closure under inventor-protocol
§4. Producer inventor-protocol fields correctly mark `dominated_by: n/a`
and `sota_delta: 0` with open next construction directions.

## Narrowest supported conclusion

Relative to DEC-20260730-020, EV-SSI-022, BATCH-022 scaffolding, BATCH-021
freeze, BATCH-013/017/020 controls, and snapshot `e6044cbf`, BATCH-023
records honest `fstar_composition_partial` / `peak_liveset_partial`
write-scope deepening of F_* channel wiring and symbolic peak-as-max
accounting under zero-compute honesty rules. CollimationSieve@`6f9188e4`
remains `host_gap_certified`. QUERY_MEMORY remains unreconciled;
QM-STOPPING stays open; QM-MEMORY-MAP / QM-ERROR stay open under
`peak_liveset_partial` / `fstar_composition_partial`; ttm-v2 stays finite
ideal-choice only and is not equated with BATCH-014; no broader
cryptanalytic, impossibility, completeness, or completion conclusion
follows.

## Recommended Coordinator action

Ledger-archive CONFIRM: adopt the BATCH-023 F_* / peak live-set composition
artifacts, retain `FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED` with QM-STOPPING
open and QM-MEMORY-MAP / QM-ERROR `peak_liveset_partial` /
`fstar_composition_partial` (not cleared), state that
`scaffold_channel_wired` ≠ justified F_* ⊆ F, peak=5 ≠ peak-byte bound, and
fstar/peak_partial ≠ clearance / PIN_COMPLETE / QUERY_MEMORY success, keep
CollimationSieve as `host_gap_certified` negative control without API
invention, keep BATCH-020 `no_admissible_pin` for external hosts, keep the
ttm-v2 panel without equating BATCH-014, and make no numeric-security,
breakthrough, or GOAL-SSI-001 completion claim. Next work should
crypto-or-host-integrate Verify and/or numeric widths / peak-byte
accounting, justify F_* ⊆ F with probability composition, or
source-instantiate Verify-relative τ with joint finiteness for QM-STOPPING
— without inventing APIs on `CollimationSieve@6f9188e4`.
