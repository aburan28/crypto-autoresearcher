# Falsification review — TASK-20260730-073

## Verdict

**CONFIRM.** Snapshot `277db292` durably archives a Coordinator-authorized
write-scope symbolic F-union / operational-error composition ledger under
`DEC-20260730-022` / `EV-SSI-024`. Independent checks reproduce: all seven
recovery_spec constituents (`F_input`, `F_oracle`, `F_cleanup`, `F_stop`,
`F_recovery`, `F_tail`, `F_verify`) are members of an explicit symbolic union
`U = ⋃ F_*` with membership rules R1–R5 and set-theoretic operational-error
composition under common-event F; `composition_status=f_union_ledger_partial`;
F_sim retains `maps_to_F=false`; harness
`python3 -m composition_ledger_harness.run_harness` passes **7/7** tests with
`collimation_sieve_apis_invented: 0` and explicit rejection of invented
probabilities, numeric error bounds, security bits, and τ. Disposition
**`FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED`** is retained with QM-STOPPING
still open, QM-MEMORY-MAP `peak_liveset_partial`, and QM-ERROR
`f_union_ledger_partial` (`reconciled: false`, `clearance: false`);
CollimationSieve@`6f9188e4` remains `host_gap_certified` without API
invention; BATCH-020 `no_admissible_pin` retained for external hosts;
BATCH-014 is not equated; no numeric, breakthrough, PIN_COMPLETE, or
completion creep is present.

Inference: requested `review-xhigh`; resolved **Cursor Grok** with
`fallback_used: true` because review-xhigh was unavailable;
`independent_session: true` (this session did not originate
TASK-20260730-071).

## Durable snapshot

Git independently establishes that
`277db292fe55790b9eca5d8e8ce78b09aa3dde84` is an ancestor of review-bind
HEAD `ead812c232ed3b5b33ac0806be9e950e29d868bc`, and that HEAD equals the
declared bind commit. Parent of the archive commit is
`9e8eb5b474c282b0cdf5f9a2853310038f29bbba`, matching the receipt. The archive
commit changes exactly the eleven producer sources under
`tasks/TASK-20260730-071/` plus
`archives/TASK-20260730-072/snapshot-receipt.json` (twelve paths). No
undeclared extras; no CollimationSieve sources; no BATCH-022 scaffold edits;
no BATCH-021 freeze edits; no BATCH-024 inclusion edits; no ledger status
edits. Receipt `source_path_sha256` values recomputed from `git show` match
all eleven producer artifacts. The receipt still says `pending_post_commit`
with null `commit_sha`; ancestry, path scope, and hashes establish the
reviewed snapshot anyway. Producer `harness_receipt.json` was restored to the
committed hash after the independent harness re-run (which rewrites that
file).

## Attack surface results

| Attack | Result |
|---|---|
| Invented probabilities / numeric error bounds / security bits | **Not detected.** All constituents `probability_assigned: false`; composition is `symbolic_set_union_under_common_event_F`; harness flags `probabilities_invented` / `numeric_error_bounds_invented` / `security_bits_invented` = false; forbidden-claim key scan empty. |
| Illicit QUERY_MEMORY or QM-STOPPING clearance | **Not detected.** Disposition unreconciled; `QUERY_MEMORY.cleared=false`; QM-STOPPING open; BATCH-018 FAIL retained; no τ / joint finiteness. |
| Fake F-union completeness / PIN_COMPLETE | **Not detected.** Status is explicitly `f_union_ledger_partial`; `pin_complete: false`; probability composition and crypto Verify absent. |
| CollimationSieve API invention / BATCH-014 equation | **Not detected.** Negative control retained `host_gap_certified`; `apis_invented: 0`; `equated_to_batch014: false`; creep tokens appear only in negation. |
| Treating `f_union_ledger_partial` as clearance | **Not detected in producer fields.** QM-ERROR `clearance: false` / `reconciled: false`; residual risk is downstream ledger wording. |
| Illicit F_sim→F map | **Not detected.** `maps_to_F: false`; F_sim not a union member; illicit map refused. |
| Snapshot ancestry / undeclared extras | **Confirmed clean.** Ancestor relation holds; twelve-path scope only; hashes match. |

## Independent harness re-run

- **Working entrypoint:** from
  `.../BATCH-025/tasks/TASK-20260730-071`, run
  `python3 -m composition_ledger_harness.run_harness` → **7 tests OK**,
  all seven F_* in symbolic union, `composition_structure_ok=true`,
  `composition_status=f_union_ledger_partial`, F_sim `maps_to_F=false`,
  probabilities / numeric bounds / security bits / τ invented=false,
  `query_memory_cleared=false`, `qm_stopping_cleared=false`,
  `collimation_sieve_apis_invented: 0`.
- Producer receipt restored after re-run; committed SHA-256
  `d05e88d29fe0d29d631c8f53f5c179e7c479a96adf500b47235f12c761244b8f`
  unchanged; producer tree left clean (no permanent dirtying).
- AppleDouble `._*` created under BATCH-025 during review were removed.

## Independent composition checks (summary)

- **F-union:** `U = F_input ∪ F_oracle ∪ F_cleanup ∪ F_stop ∪ F_recovery ∪ F_tail ∪ F_verify` with R1–R5; each constituent `member_of_symbolic_union=true`, `probability_assigned=false`; success exit requires Verify=true; F_sim ∉ U and `maps_to_F=false`.
- **Operational-error composition:** set-theoretic union under recovery_spec common-event F; checklist C1–C7 harness-passed; explicitly not probability sum / numeric union bound / security-bit reduction / Bernoulli product.
- **Common-F classification:** any non-Verify=true exit is ∈ F by definition; `union_subseteq_common_f` is a CONSTITUENTS-set checklist. Non-tautological content is the named-union ledger + rules + success exit + F_sim honesty — not a distributional inclusion proof.
- **C2 prior path justification:** harness assumes CONSTITUENTS are path-justified by default (documented dependency `batch024_path_justified_on_scaffold_prior`); does not re-import BATCH-024 executable paths. Honest dependency recording, not a silent re-proof.
- **Package identity:** write-scope `composition_ledger_harness` under TASK-20260730-071; BATCH-022–024 scaffolding / freeze read-only; BATCH-020 `no_admissible_pin` retained; CollimationSieve untouched.
- **Disposition consistency:** C2 remains live (STOPPING); C3 global status unresolved under `peak_liveset_partial`; error map remains live under `f_union_ledger_partial` with F_sim→F uninstantiated.

## Why CONFIRM rather than REVISE

The package does what DEC-20260730-022 / EV-SSI-024 required: construct a
checkable symbolic F-union / operational-error composition ledger from
BATCH-024 path-justified F_*, advancing QM-ERROR without inventing
probabilities or claiming QUERY_MEMORY clearance, without inventing
CollimationSieve APIs, and without claiming crypto end-to-end,
PIN_COMPLETE, or numeric widths. Honest `f_union_ledger_partial` with open
QM blockers is the supported reading. Residual issues are non-blocking
wording qualifications (receipt pending fields;
`classification.artifact_commit_reference` naming the CollimationSieve tip;
C2 assumed via CONSTITUENTS; keep `f_union_ledger_partial` distinct from
probability-composed closure and clearance), not defects in the producer
claim boundary.

## Scope and disposition

No Pollard-rho, BSGS, or specialized-baseline resource comparison is
admissible. Peikert's CollimationSieve remains the closest specialized
baseline; writing a symbolic F-union ledger against a separate in-repo freeze
package / BATCH-022–024 scaffolding does not change its accounting.
KN-TECH-051 / KN-OPEN-014 remain the locus of CSIDH quantum-security
dispute; this package supplies no security number.

Symbolic ledger deepening with open QM blockers is not QUERY_MEMORY
clearance, not QM-STOPPING / MEMORY / ERROR closure, not cryptographic
Verify, not probability-composed F_* ⊆ F, not PIN_COMPLETE, not a durable
negative cryptanalytic boundary for FC0 in general, and not lane closure
under inventor-protocol §4. Producer inventor-protocol fields correctly mark
`dominated_by: n/a` and `sota_delta: 0` with open next construction
directions.

## Narrowest supported conclusion

Relative to DEC-20260730-022, EV-SSI-024, BATCH-024 path justification,
BATCH-022 scaffolding, BATCH-021 freeze, BATCH-013/017/020/023 controls, and
snapshot `277db292`, BATCH-025 records honest `f_union_ledger_partial`
write-scope deepening of symbolic `U = ⋃ F_* ⊆ F` (set-theoretic /
checklist only) with honest local F_sim (`maps_to_F=false`) under
zero-compute honesty rules. CollimationSieve@`6f9188e4` remains
`host_gap_certified`. QUERY_MEMORY remains unreconciled; QM-STOPPING stays
open; QM-MEMORY-MAP stays `peak_liveset_partial`; QM-ERROR advances to
`f_union_ledger_partial` (not cleared); ttm-v2 stays finite ideal-choice only
and is not equated with BATCH-014; no broader cryptanalytic, impossibility,
completeness, or completion conclusion follows.

## Recommended Coordinator action

Ledger-archive CONFIRM: adopt the BATCH-025 symbolic F-union /
operational-error composition ledger artifacts, retain
`FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED` with QM-STOPPING open,
QM-MEMORY-MAP `peak_liveset_partial`, and QM-ERROR `f_union_ledger_partial`
(not cleared), state that `f_union_ledger_partial` ≠ clearance /
PIN_COMPLETE / QUERY_MEMORY success / probability-composed closure, and
F_sim `maps_to_F=false`, keep CollimationSieve as `host_gap_certified`
negative control without API invention, keep BATCH-020 `no_admissible_pin`
for external hosts, keep finite ideal-choice ttm-v2 without equating
BATCH-014, and introduce no numeric-security, breakthrough, or GOAL-SSI-001
completion claim. Next batch: probability-composed F_* ∪ ⊆ F,
crypto-or-host-integrated Verify, numeric widths / peak-byte accounting, or
source-instantiate Verify-relative τ with joint finiteness for QM-STOPPING —
without inventing APIs on CollimationSieve@`6f9188e4`.
