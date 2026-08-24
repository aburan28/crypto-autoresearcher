# Falsification review — TASK-20260730-045

## Verdict

**CONFIRM.** Snapshot `b23b8a2c` durably archives a dedicated stopping-law /
joint Q·S·P·C control against pinned Peikert extraction (BATCH-011),
`CollimationSieve@6f9188e4`, `recovery_spec` type obligations, and ttm-v2
one-retry ideal-choice panel limits. An explicit Verify-relative τ pass rule
and joint additive-expectation obligations are defined; τ and jointly finite
`E[sum Q/S/P/C+H]` remain `not_instantiated`; C2 remains `NOT_REJECTED`;
`control_result` is **FAIL**. Disposition
`FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED` is supported with QM-STOPPING /
QM-MEMORY-MAP / QM-ERROR still open; ttm-v2 is not inflated to global τ and
is not equated to BATCH-014; no numeric, breakthrough, or completion creep
is present.

Inference: requested `review-xhigh`; resolved **Cursor Grok** with
`fallback_used: true` because review-xhigh was unavailable;
`independent_session: true` (this session did not originate
TASK-20260730-043).

## Durable snapshot

Git independently establishes that
`b23b8a2ca102978125b97cc243162597f48c3092` is an ancestor of review-bind
HEAD `d2ba5ab3b49f0b4d0ead07e5b0b0c1a297953815`, and that HEAD equals the
declared bind commit. The archive commit changes exactly:

- `stopping_law_artifact.md`
- `joint_qspc_ledger.yaml`
- `control_report.md`
- `mutation_status.yaml`
- `classification.yaml`
- `archives/TASK-20260730-044/snapshot-receipt.json`

No undeclared extras. Receipt `source_path_sha256` values recomputed from
`git show` match all five producer artifacts. The receipt still says
`pending_post_commit` with null `commit_sha`; ancestry, path scope, and
hashes establish the reviewed snapshot anyway.

## Attack surface results

| Attack | Result |
|---|---|
| Invented joint finiteness or PASS despite missing τ | **Not detected.** All joint expectations null; `finiteness_status: not_established`; `control_result: FAIL`. |
| Illicit QM-STOPPING clearance | **Not detected.** Artifact exists; `reconciled: false`; blocker remains open under FAIL. |
| ttm-v2 → global/history-uniform stopping inflation | **Not detected.** `usable_as_global_tau: false`; panel retained as finite ideal-choice only. |
| False QM-MEMORY-MAP / QM-ERROR clearance or invented Verify | **Not detected.** Both blockers open / out of clearance scope; Verify absent. |
| Mere residual-gap checklist without real stopping-law definition | **Falsified (attack fails).** §1 defines τ + joint-expectation pass rule; instantiation table scores obligations; result FAIL. Meets DEC-015 “not another residual-gap checklist alone.” |
| BATCH-014 equation; numeric / breakthrough / completion creep | **Not detected.** `equated_to_batch014: false`; claim boundaries forbid security/breakthrough/completion. |
| Snapshot ancestry / undeclared extras | **Confirmed clean.** Ancestor relation holds; six-path scope only; hashes match. |

## Why CONFIRM rather than REVISE

The package does what DEC-20260730-015 / EV-SSI-017 / RT-20260730-041
required: produce a separate stopping-law / joint Q·S·P·C control artifact
addressing QM-STOPPING, keep MEMORY/ERROR open, retain the ttm-v2 panel
without BATCH-014 equation, and record PASS/FAIL honestly. The control
**FAIL**s for the right reason (missing source-compatible τ and joint
finiteness). Residual issues are non-blocking wording qualifications
(receipt pending fields; do not compress “artifact produced” into “blocker
closed”), not defects in the producer claim boundary.

## Scope and disposition

No Pollard-rho, BSGS, or specialized-baseline resource comparison is
admissible. Peikert's CollimationSieve remains the closest specialized
baseline; a FAIL against per-run / typical estimates does not change its
accounting. KN-TECH-051 / KN-OPEN-014 remain the locus of CSIDH
quantum-security dispute; this package supplies no security number.

A dedicated stopping-law artifact that FAILS is not QM-STOPPING clearance,
not a durable negative cryptanalytic boundary, and not QUERY_MEMORY
clearance. recovery_spec Verify / `F_stop` types sharpen τ obligations but
do not instantiate them.

## Narrowest supported conclusion

Relative to pinned Peikert (BATCH-011), `CollimationSieve@6f9188e4`,
`recovery_spec`, and ttm-v2 panel scope, BATCH-018 defines and fails a
Verify-relative τ / joint Q·S·P·C control: τ and jointly finite expectations
are not source-instantiated; C2 remains live; QM-STOPPING stays open;
MEMORY/ERROR stay open; QUERY_MEMORY remains unreconciled; ttm-v2 stays
finite ideal-choice only and is not equated with BATCH-014; no broader
cryptanalytic or completion conclusion follows.

## Recommended Coordinator action

Ledger-archive CONFIRM: adopt the stopping-law FAIL artifacts, retain
`FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED` with QM-STOPPING / QM-MEMORY-MAP /
QM-ERROR open, state that artifact production under FAIL is not clearance,
keep the ttm-v2 panel without equating BATCH-014 or inflating to global τ,
and make no numeric-security, breakthrough, or GOAL-SSI-001 completion
claim. Next work should either source-instantiate Verify-relative τ with
joint finiteness or implement FC0 lifetimes / Verify for MEMORY/ERROR.
