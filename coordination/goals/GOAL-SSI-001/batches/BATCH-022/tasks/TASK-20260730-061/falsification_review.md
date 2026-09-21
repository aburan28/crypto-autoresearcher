# Falsification review — TASK-20260730-061

## Verdict

**CONFIRM.** Snapshot `96e90851` durably archives a Coordinator-authorized
write-scope FC0-EXT-PKG-SSI-001 Verify/lifetime implementation spike under
`DEC-20260730-019` / `EV-SSI-021`. Independent checks reproduce:
`impl_status=implemented_partial`; typed no-crypto `Verify(x, k_prime) -> bool`
scaffolding; all twelve lifetime hooks (`W_label`, `R_label`, `W_sieve`,
`R_sieve`, `B_input`, `B_attempt`, `B_sieve`, `accepted_transcript`, `B_post`,
`B_recovery`, `M_tail`, `B_candidate`) each exposing birth / last_use /
cleanup / destroy methods (48 total); harness `python3 -m scaffold.run_harness`
passes **11/11** tests with `collimation_sieve_apis_invented: 0` and explicit
rejection of numeric widths / τ invention. Disposition
**`FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED`** is retained with QM-STOPPING
still open and QM-MEMORY-MAP / QM-ERROR
`scaffolding_partial_implementation_pending` (`reconciled: false`,
`clearance: false`); CollimationSieve@`6f9188e4` remains
`host_gap_certified` without API invention; BATCH-020 `no_admissible_pin`
retained for external hosts; BATCH-014 is not equated; no numeric,
breakthrough, PIN_COMPLETE, `implemented_complete`, or completion creep is
present.

Inference: requested `review-xhigh`; resolved **Cursor Grok** with
`fallback_used: true` because review-xhigh was unavailable;
`independent_session: true` (this session did not originate
TASK-20260730-059).

## Durable snapshot

Git independently establishes that
`96e908512cba165b593cab97ce3ae1a2e1d58116` is an ancestor of review-bind
HEAD `a9e52bec74af7b47eb7fd511010d71385a5ea0c2`, and that HEAD equals the
declared bind commit. Parent of the archive commit is
`64ebf8d845616303b81a34a68d095c82b6112f7f`, matching the receipt. The archive
commit changes exactly the thirteen producer sources under
`tasks/TASK-20260730-059/` plus
`archives/TASK-20260730-060/snapshot-receipt.json` (fourteen paths). No
undeclared extras; no CollimationSieve sources; no BATCH-021 freeze edits;
no ledger status edits. Receipt `source_path_sha256` values recomputed from
`git show` match all thirteen producer artifacts. The receipt still says
`pending_post_commit` with null `commit_sha`; ancestry, path scope, and
hashes establish the reviewed snapshot anyway. Producer `harness_receipt.json`
was restored to the committed hash after the independent harness re-run
(which rewrites that file).

## Attack surface results

| Attack | Result |
|---|---|
| CollimationSieve@6f9188e4 API invention | **Not detected.** Negative control retained as `host_gap_certified`; scaffold is a separate in-repo write-scope surface; coverage reports `collimation_sieve_apis_invented: 0`; archive commit does not touch CollimationSieve sources. |
| Fake scaffolding (tests don't run / hooks missing vs freeze) | **Not detected.** Module harness passes 11/11; AST inventory shows all 48 required methods; stage live sets match BATCH-021 freeze. |
| Overclaiming `implemented_complete` / PIN_COMPLETE | **Not detected.** `impl_status=implemented_partial`; `pin_complete: false`; excluded-claim lists forbid both. |
| Illicit QUERY_MEMORY clearance or QM-STOPPING closure | **Not detected.** Disposition unreconciled; `QUERY_MEMORY.cleared: false`; QM-STOPPING open; BATCH-018 FAIL retained; scaffold rejects `invents_tau=true`. |
| Equating BATCH-014 with ttm-v2 panel | **Not detected.** `equated_to_batch014: false`; ttm-v2 retained as finite ideal-choice only. |
| Numeric security / breakthrough / completion creep | **Not detected.** Claim boundaries and non-claims forbid security bits, breakthrough, and goal completion; creep-token hits appear only in negation. |
| Treating `scaffolding_partial_implementation_pending` as MEMORY/ERROR clearance | **Not detected.** Structured fields set `reconciled: false` and `clearance: false` for both blockers; spike report states “not clearance.” |
| Snapshot ancestry / undeclared extras | **Confirmed clean.** Ancestor relation holds; fourteen-path scope only; hashes match. |

## Independent harness re-run

- **Working entrypoint:** from
  `.../BATCH-022/tasks/TASK-20260730-059`, run
  `python3 -m scaffold.run_harness` → **11 tests OK**,
  `implemented_method_count: 48`, τ / numeric-width invention tests pass by
  rejection.
- **Script-path footgun (non-blocking):**
  `python3 scaffold/run_harness.py` fails on this host because
  `scaffold/types.py` shadows stdlib `types` when the script directory is
  prepended to `sys.path`. This is packaging docs debt, not missing
  implementation. Prefer the module entrypoint; `unittest discover -s scaffold`
  remains fragile for relative imports (as the task card warned).
- Producer receipt restored after re-run; committed SHA-256 unchanged.

## Independent freeze-alignment checks (summary)

- **Verify:** signature `Verify(x, k_prime) -> bool`; total deterministic
  no-crypto token predicate; malformed inputs → `VerificationFault` /
  `F_verify`; synthetic accept path for unit tests only; crypto body absent.
- **Lifetimes:** twelve hooks match freeze / recovery_spec object classes;
  stage live sets match freeze; peak-accounting note explicitly refuses
  numeric widths; `M_tail` rejects `numeric_width` and `invents_tau=true`.
- **Package identity:** separate in-repo scaffold under TASK-20260730-059
  write scope; not an external successor pin and not a CollimationSieve
  patch; BATCH-020 `no_admissible_pin` retained; BATCH-021 freeze unreadably
  unchanged by the archive commit.
- **Disposition consistency:** C2 remains live (STOPPING); C3 global status
  unresolved under scaffolding-partial; error map remains live with
  `F_sim→F` uninstantiated.

## Why CONFIRM rather than REVISE

The spike does what DEC-20260730-019 / EV-SSI-021 required: bounded
write-scope scaffolding of Verify + W/R/B/`M_tail` against frozen
FC0-EXT-PKG-SSI-001 with checkable tests, without inventing CollimationSieve
APIs, without clearing QUERY_MEMORY, and without claiming
`implemented_complete` or PIN_COMPLETE. Honest `implemented_partial` with
open QM blockers is the supported reading. Residual issues are non-blocking
wording/packaging qualifications (receipt pending fields;
`classification.artifact_commit_reference` naming the CollimationSieve tip;
document `python3 -m scaffold.run_harness`; keep
`scaffolding_partial_implementation_pending` distinct from clearance), not
defects in the producer claim boundary.

## Scope and disposition

No Pollard-rho, BSGS, or specialized-baseline resource comparison is
admissible. Peikert's CollimationSieve remains the closest specialized
baseline; scaffolding a separate in-repo freeze package does not change its
accounting. KN-TECH-051 / KN-OPEN-014 remain the locus of CSIDH
quantum-security dispute; this package supplies no security number.

Partial scaffolding with open QM blockers is not QUERY_MEMORY clearance,
not QM-STOPPING / MEMORY / ERROR closure, not cryptographic Verify, not
PIN_COMPLETE, not a durable negative cryptanalytic boundary for FC0 in
general, and not lane closure under inventor-protocol §4. Producer
inventor-protocol fields correctly mark `dominated_by: n/a` and
`sota_delta: 0` with open next construction directions.

## Narrowest supported conclusion

Relative to DEC-20260730-019, EV-SSI-021, BATCH-021 freeze, BATCH-013/017/020
controls, and snapshot `96e90851`, BATCH-022 records honest
`implemented_partial` write-scope scaffolding of Verify and twelve lifetime
hooks under zero-compute honesty rules. CollimationSieve@`6f9188e4` remains
`host_gap_certified`. QUERY_MEMORY remains unreconciled; QM-STOPPING stays
open; QM-MEMORY-MAP / QM-ERROR stay open under
`scaffolding_partial_implementation_pending`; ttm-v2 stays finite
ideal-choice only and is not equated with BATCH-014; no broader
cryptanalytic, impossibility, completeness, or completion conclusion
follows.

## Recommended Coordinator action

Ledger-archive CONFIRM: adopt the FC0-EXT-PKG-SSI-001 scaffolding spike
artifacts, retain `FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED` with QM-STOPPING
open and QM-MEMORY-MAP / QM-ERROR
`scaffolding_partial_implementation_pending` (not cleared), state that
scaffolding ≠ crypto Verify / PIN_COMPLETE / `implemented_complete` /
blocker clearance, keep CollimationSieve as `host_gap_certified` negative
control without API invention, keep BATCH-020 `no_admissible_pin` for
external hosts, keep the ttm-v2 panel without equating BATCH-014, and make
no numeric-security, breakthrough, or GOAL-SSI-001 completion claim. Next
work should crypto-or-host-integrate Verify and/or numeric widths against
FC0-EXT-PKG-SSI-001, or source-instantiate Verify-relative τ with joint
finiteness for QM-STOPPING — without inventing APIs on
`CollimationSieve@6f9188e4`.
