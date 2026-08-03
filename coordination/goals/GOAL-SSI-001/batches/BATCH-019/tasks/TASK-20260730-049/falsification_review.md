# Falsification review — TASK-20260730-049

## Verdict

**CONFIRM.** Snapshot `ee3ff810` durably archives a bounded FC0 lifetime /
Verify(x,k') implementation spike against pinned
`CollimationSieve@6f9188e4`. Independent re-verification matches pin blob
SHAs, confirms a three-module `src/` tree, finds no Verify / recovery /
QRACM / `M_tail` / uncompute symbols, and confirms `main` ends in a LaTeX
statistics report. Status **`host_gap_certified`** is supported;
disposition **`FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED`** is retained with
QM-STOPPING still open and QM-MEMORY-MAP / QM-ERROR
`open_host_gap_certified` (not cleared); BATCH-014 is not equated; no
numeric, breakthrough, or completion creep is present.

Inference: requested `review-xhigh`; resolved **Cursor Grok** with
`fallback_used: true` because review-xhigh was unavailable;
`independent_session: true` (this session did not originate
TASK-20260730-047).

## Durable snapshot

Git independently establishes that
`ee3ff810a891ff3e86258fab1ba51399e93a0f2d` is an ancestor of review-bind
HEAD `c983950fba352fcacd50a064df994bb3f3cbd60c`, and that HEAD equals the
declared bind commit. The archive commit changes exactly:

- `spike_report.md`
- `host_gap_or_impl_status.yaml`
- `lifetime_verify_attempt.yaml`
- `mutation_status.yaml`
- `classification.yaml`
- `archives/TASK-20260730-048/snapshot-receipt.json`

No undeclared extras. Receipt `source_path_sha256` values recomputed from
`git show` match all five producer artifacts. The receipt still says
`pending_post_commit` with null `commit_sha`; ancestry, path scope, and
hashes establish the reviewed snapshot anyway.

## Attack surface results

| Attack | Result |
|---|---|
| Fake implementation claims or invented Verify / lifetime APIs | **Not detected.** `pretend_apis_invented: false`; `host_patched: false`; all FC0/Verify outcomes absent or ambient-only; stub `blocked_host_gap`. |
| Weak host-gap certificate (no checkable pin/symbols/absences) | **Falsified (attack fails).** Pin blob SHAs, tree inventory, symbol search, and report-only control flow independently re-verified against `CollimationSieve@6f9188e4` / `artifact_pin.yaml`. |
| Illicit QUERY_MEMORY clearance or QM-STOPPING closure | **Not detected.** Disposition unreconciled; `QUERY_MEMORY.cleared: false`; QM-STOPPING open; BATCH-018 FAIL retained; no τ / joint finiteness invented. |
| Treating host_gap as mathematical impossibility of FC0 | **Not detected in producer boundary.** Claims stay pin-scoped; excluded-claim lists forbid clearance / completion; interpretation_limit states host-gap ≠ security / completion / implemented lifetimes. |
| BATCH-014 equation; numeric / breakthrough / completion creep | **Not detected.** `equated_to_batch014: false`; claim boundaries forbid security/breakthrough/completion. |
| Snapshot ancestry / undeclared extras | **Confirmed clean.** Ancestor relation holds; six-path scope only; hashes match. |

## Why CONFIRM rather than REVISE

The spike does what DEC-20260730-016 / EV-SSI-018 required: attempt the
narrowest in-repo MEMORY/ERROR advance against the pinned host, or emit an
explicit host-gap certificate. Producers chose the certificate for the
right reason (no pin-native APIs; inventing stubs forbidden). Residual
issues are non-blocking wording qualifications (receipt pending fields;
do not compress “host gap certified” into “blocker closed”; keep
pin-scope vs FC0-impossibility distinct; minor `printf` vs
`putStrLn`/`showFFloat` citation), not defects in the producer claim
boundary.

## Scope and disposition

No Pollard-rho, BSGS, or specialized-baseline resource comparison is
admissible. Peikert's CollimationSieve remains the closest specialized
baseline; certifying that this pin is report-only does not change its
accounting. KN-TECH-051 / KN-OPEN-014 remain the locus of CSIDH
quantum-security dispute; this package supplies no security number.

A pin-scoped `host_gap_certified` result is not QUERY_MEMORY clearance,
not QM-STOPPING / MEMORY / ERROR closure, not a durable negative
cryptanalytic boundary for FC0 in general, and not lane closure under
inventor-protocol §4.

## Independent pin checks (summary)

- Blob SHA-1s for `Main.hs`, `Random.hs`, `Phase.hs`, `README.md`,
  `test/Spec.hs` match `artifact_pin.yaml`.
- Recursive tree at `6f9188e4` has only `src/{Main,Phase,Random}.hs` plus
  packaging/docs.
- Case-insensitive search for verify / recover / QRACM / `M_tail` /
  uncompute: zero hits in pinned sources.
- `module Main (main)` only; exit is LaTeX statistics emission.

## Narrowest supported conclusion

Relative to pinned `CollimationSieve@6f9188e4`, BATCH-012 process
extraction, BATCH-013 `recovery_spec`, and BATCH-017 lifetime/error maps,
BATCH-019 certifies a structural host gap: Verify and FC0 W/R/B/M_tail
lifetimes are absent and cannot be hosted in-repo on this pin without
invention. QUERY_MEMORY remains unreconciled; QM-STOPPING stays open;
QM-MEMORY-MAP / QM-ERROR stay open under the host-gap certificate;
ttm-v2 stays finite ideal-choice only and is not equated with BATCH-014;
no broader cryptanalytic, impossibility, or completion conclusion follows.

## Recommended Coordinator action

Ledger-archive CONFIRM: adopt the host-gap spike artifacts, retain
`FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED` with QM-STOPPING open and
QM-MEMORY-MAP / QM-ERROR `open_host_gap_certified`, state that host-gap
certification is pin-scoped (not FC0 impossibility and not blocker
clearance), keep the ttm-v2 panel without equating BATCH-014, and make no
numeric-security, breakthrough, or GOAL-SSI-001 completion claim. Next
work should either pin a successor host / extension protocol capable of
FC0 lifetimes and Verify, or source-instantiate Verify-relative τ with
joint finiteness for QM-STOPPING — without inventing APIs on
`CollimationSieve@6f9188e4`.
