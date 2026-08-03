# Falsification review — TASK-20260730-089

## Verdict

**CONFIRM.** Snapshot `8ed9ae0b` durably archives a Coordinator-authorized
write-scope symbolic Verify-relative success-exit and F_verify
obligation/charge-routing ledger under `DEC-20260730-026` / `EV-SSI-028`.
Independent checks reproduce: 7 success_exit + 6 f_verify_membership + 11
charge_routing items (24 total) with statuses `wired_symbolic=17`,
`checklist_only=1`, `deferred=1`, `not_supported=5`
(`ledger_status=verify_exit_partial`); lineage retains
`retry_cleanup_tail_partial`, `charge_incidence_partial`,
`resource_vector_partial`, `peak_liveset_partial`, and
`f_union_ledger_partial`; harness `python3 -m verify_exit_harness.run_harness`
passes **7/7** tests with `scaffold_mutated: false`,
`collimation_sieve_apis_invented: 0`, `crypto_verify_implemented: false`,
and explicit rejection of invented τ, numeric widths/charges, probabilities,
security bits, and clearance flags. Disposition
**`FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED`** is retained with QM-STOPPING
still open, QM-MEMORY-MAP `verify_exit_partial`, and QM-ERROR
`f_union_ledger_partial` (`reconciled: false`, `clearance: false`);
CollimationSieve@`6f9188e4` remains `host_gap_certified` without API
invention; BATCH-020 `no_admissible_pin` retained for external hosts;
BATCH-014 is not equated; no numeric, breakthrough, PIN_COMPLETE, crypto
Verify-completeness, or completion creep is present.

Inference: requested `review-xhigh`; resolved **Cursor Grok** with
`fallback_used: true` because review-xhigh was unavailable;
`independent_session: true` (this session did not originate
TASK-20260730-087).

## Durable snapshot

Git independently establishes that
`8ed9ae0bc38b0ca40a63dcb928ec075bfb62dd87` is an ancestor of review-bind
HEAD `0e33f7efb04839bf41fad0372d51d3f0e560a66f`, and that HEAD equals the
declared bind commit. Parent of the archive commit is
`df441b2c9c0b457a317ef1d1eca832c26794a06f`, matching the receipt. The archive
commit changes exactly the ten producer sources under
`tasks/TASK-20260730-087/` plus
`archives/TASK-20260730-088/snapshot-receipt.json` (eleven paths). No
undeclared extras; no CollimationSieve sources; no BATCH-022 scaffold edits;
no BATCH-021 freeze edits; no BATCH-023–028 source edits; no ledger status
edits. Receipt `source_path_sha256` values recomputed from `git show` match
all ten producer artifacts. The receipt still says `pending_post_commit` with
null `commit_sha`; ancestry, path scope, and hashes establish the reviewed
snapshot anyway. Producer `harness_receipt.json` was restored to the
committed hash after the independent harness re-run (which rewrites that
file).

## Attack surface results

| Attack | Result |
|---|---|
| Invented numeric widths / peak-byte bounds / probabilities / security bits | **Not detected.** H/C `numeric_charge=not_supported`; F_verify probability bounds `not_supported`; `joint_finiteness_established=false`; `peak_byte_bound=unresolved`; explicit `not_supported` for B_candidate numeric width and E under τ; deferred F_verify numeric probability charge; harness invented=false; forbidden-claim key scan empty. Item counts are ledger cardinalities only. |
| Illicit QUERY_MEMORY or QM-STOPPING clearance | **Not detected.** Disposition unreconciled; `QUERY_MEMORY.cleared=false`; QM-STOPPING open; BATCH-018 FAIL retained; `tau_invented=false`; joint finiteness false; `OBL-SE-tau_joint_finiteness_under_verify` / `ROUTE-VE-E_under_tau` are `not_supported`. |
| Illicit QM-MEMORY-MAP clearance / PIN_COMPLETE | **Not detected.** Status is explicitly `verify_exit_partial`; `pin_complete: false`; P/C/H remain `not_instantiated` in lineage; numeric charges absent. |
| Fake crypto Verify body completeness / end-to-end Verify | **Not detected.** `OBL-SE-crypto_verify_body` is `not_supported`; `crypto_verify_implemented=false`; BATCH-022 Verify is documented no-crypto token-accept; harness smoke exercises only those tokens. |
| Invented τ / joint finiteness via Verify-exit / M_tail language | **Not detected in producer fields.** τ-reject items carry `no_tau` / `no_qm_stopping_clearance`; `tau_invented=false`. |
| CollimationSieve API invention / BATCH-014 equation | **Not detected.** Negative control retained `host_gap_certified`; `apis_invented: false` / `0`; `equated_to_batch014: false`; archive path scope excludes CollimationSieve. |
| Treating `wired_symbolic` / `verify_exit_partial` as clearance | **Not detected in producer fields.** MEMORY-MAP `clearance: false` / `reconciled: false`; residual risk is downstream ledger wording. |
| Snapshot ancestry / undeclared extras | **Confirmed clean.** Ancestor relation holds; eleven-path scope only; hashes match. |

## Independent harness re-run

- **Working entrypoint:** from
  `.../BATCH-029/tasks/TASK-20260730-087`, run
  `python3 -m verify_exit_harness.run_harness` → **7 tests OK**,
  `ledger_status=verify_exit_partial`, item counts 7+6+11=24 with statuses
  17/1/1/5, disposition `FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED`, QM-STOPPING
  open, QM-ERROR `f_union_ledger_partial`, joint_finiteness / τ / numeric
  widths/charges invented=false, `crypto_verify_implemented=false`,
  `query_memory_cleared=false`, `qm_stopping_cleared=false`,
  `qm_memory_map_cleared=false`, `scaffold_mutated=false`,
  `collimation_sieve_apis_invented: 0`.
- Producer receipt restored after re-run; committed SHA-256
  `135ec07dba6e7c2dcec5218e5c81d63d1a61d77d9094d78f5a93f97a492c00f0`
  unchanged; producer tree left clean (no permanent dirtying).
- AppleDouble `._*` and `__pycache__` created under BATCH-029/TASK-087 during
  review were removed.

## Independent Verify-exit checks (summary)

- **Items:** 7 success_exit + 6 f_verify_membership + 11 charge_routing = 24;
  statuses only in `{wired_symbolic, checklist_only, not_supported, deferred}`;
  declared counts match.
- **Fields/channels:** H/C and F_verify/success_exit have
  `wired_symbolic` routes with `numeric_charge=not_supported` /
  `crypto_body=false`; Q/S/P routes intentionally retained in BATCH-028
  lineage (not re-derived).
- **Scaffold cross-check:** BATCH-022 `Verify` is a total deterministic
  no-crypto token predicate; `classify_verify_outcome` maps True →
  `success_exit` and False/fault → `F_verify`; `LifetimeRegistry` exposes
  B_candidate birth/last_use/cleanup/destroy; `STAGE_LIVE_SETS.tail_verification`
  includes `B_candidate`; no charge-meter API; `scaffold_mutated=false`.
- **Honest absences:** `OBL-SE-crypto_verify_body`,
  `OBL-SE-tau_joint_finiteness_under_verify`, `ROUTE-VE-E_under_tau`, and
  `ROUTE-VE-numeric_width_B_candidate` are `not_supported`;
  `ROUTE-VE-F_verify-numeric_probability_charge` is `deferred`.
- **Cross-links:** BATCH-023 `peak_liveset_partial` (peak symbolic object
  count 5, max-not-sum checklist only), BATCH-024 path-justified F_verify,
  BATCH-025 `f_union_ledger_partial` / F_sim `maps_to_F=false`, BATCH-026
  `resource_vector_partial`, BATCH-027 `charge_incidence_partial`, and
  BATCH-028 `retry_cleanup_tail_partial` retained without inventing widths,
  charges, probabilities, or τ.
- **Harness nature:** YAML schema/status consistency against hardcoded
  `EXPECTED_COUNTS` and absence of forbidden clearance booleans, plus
  no-crypto scaffold smoke — not a derivation of charges, widths,
  expectations, or cryptographic Verify. Some receipt honesty flags
  (`probabilities_invented`, `security_bits_invented`,
  `collimation_sieve_apis_invented`) are hardcoded literals; YAML/Git/scaffold
  checks independently support those conclusions for this snapshot.
- **Package identity:** write-scope `verify_exit_harness` under
  TASK-20260730-087; BATCH-022–028 scaffolding / freeze read-only;
  BATCH-020 `no_admissible_pin` retained; CollimationSieve untouched.
- **Disposition consistency:** C2 remains live (STOPPING; BATCH-018 FAIL);
  C3 global status unresolved under `verify_exit_partial`; error map remains
  live under `f_union_ledger_partial`.

## Why CONFIRM rather than REVISE

The package does what DEC-20260730-026 / EV-SSI-028 required: construct a
checkable symbolic Verify-relative success-exit and F_verify
obligation/charge-routing ledger against recovery_spec / F_union /
retry_cleanup_tail lineage, advancing QM-MEMORY-MAP without inventing
numeric widths/charges or claiming QUERY_MEMORY clearance, without inventing
CollimationSieve APIs, and without claiming τ / joint finiteness,
PIN_COMPLETE, or crypto Verify completeness. Honest `verify_exit_partial`
with open QM blockers is the supported reading. Residual issues are
non-blocking wording / harness qualifications (receipt pending fields;
`classification.artifact_commit_reference` naming the CollimationSieve tip;
hardcoded receipt honesty flags; keep `verify_exit_partial` distinct from
clearance, scaffold Verify smoke distinct from crypto Verify, `wired_symbolic`
distinct from numeric metering, and schema-pass distinct from mathematical
Verify completeness), not defects in the producer claim boundary.

## Scope and disposition

No Pollard-rho, BSGS, or specialized-baseline resource comparison is
admissible. Peikert's CollimationSieve remains the closest specialized
baseline and is unchanged by this write-scope ledger. Producer
`dominated_by` / `sota_delta` correctly mark n/a and 0 (no complexity claim).
Supported official reading: retain
`FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED` with QM-STOPPING open,
QM-MEMORY-MAP `verify_exit_partial`, QM-ERROR `f_union_ledger_partial`;
do not promote to PIN_COMPLETE, QUERY_MEMORY clearance, breakthrough, or
GOAL-SSI-001 completion.

## Next concrete action

Coordinator should ledger-archive a CONFIRM decision adopting the BATCH-029
Verify-exit / F_verify obligation ledger artifacts under the narrowest
supported statement in `red_team_report.yaml`, then gate the next batch on
numeric widths/charges/peak-byte accounting / measured Verify-failure
charges, Verify-relative τ with joint finiteness, or probability-composed
ERROR / crypto-or-host Verify — without CollimationSieve API invention and
without numeric-security claims.
