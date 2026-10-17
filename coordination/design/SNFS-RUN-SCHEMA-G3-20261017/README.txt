G3 additive run-schema/accounting correction, 2026-10-17

Run: RUN-ECDLP-e89532 / EXP-ECDLP-4c6a09 / original trial ID full-grid
Correction: CORR-20261017-504324
Original archive: 233991be24b83777c94fb76bc2e821407b9a8404
Execution source: aefcb291f54dd1cb1e59487a70c11b910ec28b06
Producer end-of-run repository HEAD: 74180d9aa1b30d56699152d7a80add600dd4903f

The three commits have different meanings. The source commit is literal from
supervisor launch/environment/receipt. The Rust producer sampled a later HEAD
while unrelated control-plane publication occurred. Scientific source/input
hashes are verified at the execution source commit; the intervening changed
paths do not intersect that frozen closure. The producer's observed HEAD and
literal direct binary command are retained separately from supervisor cargo
argv. The archive commit is not falsely presented as execution provenance.

Producer rc0, execution-time checker rc0, 1395 raw cells. Supervisor status was
invalid_output because the original flat manifest has no top-level run. Every
original run file is preserved and matches the published archive byte for byte.
No rerun, approval, scientific transition, independent scientific review, git
mutation or shared-registry edit occurred in this delegated task.

The successor manifest preserves invalid_output, output_validated:false,
scientific_review_verified:false and certificate.kind:none. Original timing
literals, cell timings, actual Rust/rustc/platform/gp metadata, all frozen
parameters and controls are retained with source pointers. Supervisor Python
metadata describes the supervisor/checker runtime, not the Rust producer.

Rank arm is explicitly skipped in every raw cell. Distinct point counts do not
certify independence or rank gain. This schema/accounting envelope does not
certify rank, turn checker witnesses into an attack certificate, validate an
exponent, promote scientific status or establish any ECDLP advantage.

The flat original omits both id and run_id. The proposed one-entry registry
fragment uses the existing superseded_id_null:true opt-in, with explicit
provenance naming hash-pinned launch and receipt identities and agreeing run
directory basename; it does not pretend id:null appeared in the old file.
Both check_run_supersessions and check_run pass on this fragment and source
alone. Four negative controls reject changed original/successor digests, missing
identity opt-in and wrong run identity. Verification checks all 13 frozen
source/input bindings at execution commit and exact original argv/trial ID.
No repository-wide ledger validation was run in the sparse checkout.

Primary owns reviewing and publishing this correction. Merge only the proposed
entry in run-supersession-registry.fragment.yaml into the shared registry;
archive this new directory; re-run verify.py; commit/push and refresh PR #2382.
The original receipt and run folder remain immutable. Registering schema
routing does not change invalid_output or constitute independent result review.
No approval is required by the existing schema-completion parser/checks, and no
Coordinator decision or substitution approval is fabricated by this packet.
Actual preparing runtime: Codex, system-reported family GPT-6; exact serving
identifier unavailable. The unverified anthropic adapter was not impersonated.
