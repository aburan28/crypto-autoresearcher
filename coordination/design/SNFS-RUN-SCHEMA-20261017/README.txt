G2 additive run-schema/accounting correction, 2026-10-17

Original: experiments/EXP-ECDLP-8cc60d/runs/RUN-ECDLP-2ac930/
Published original archive: fba584bdc8540f2f552e4ec86e221f99dd191dc6
Actual execution source commit: 37315eaa955d97dfe4609e76e846d3f94c92de96
Correction: CORR-20261017-b17a35

The original producer and execution-time checker both returned 0. The supervisor
returned invalid_output because the producer's flat manifest has no top-level
run mapping. All original run files, receipt, status and hashes remain intact.
No new trial, result review, approval, claim, commit or push occurred here.

RUN-ECDLP-2ac930.manifest.schema-v2.yaml is an additive schema-readable envelope
of the already archived observations. It preserves invalid_output, explicitly
records output_validated:false and scientific_review_verified:false, and carries
certificate.kind:none. Its source commit and argv come literally from launch,
environment and receipt; producer timing remains the producer's literal rounded
value, with supervisor timestamps separately identified. The archive commit is
not falsely presented as the execution commit. No performance or mathematical
claim is made by this correction.

The original flat manifest contains neither id nor run_id. The proposed registry
fragment explicitly uses the existing superseded_id_null:true mechanism for
that absent identity; its provenance states the field was absent rather than
claiming the original contained an explicit null. Hash-pinned launch and receipt
both identify RUN-ECDLP-2ac930, matching the original directory name. The actual
check_run_supersessions implementation accepts that explicit opt-in. Omitting
it fails the recorded negative control; ordinary unregistered identity recovery
has not been changed or generalized.

Only the proposed one-record fragment was loaded. check_run_supersessions and
check_run pass with zero errors. Verification also rejects altered original and
successor digests, an omitted identity opt-in and wrong run identity, and checks
all three source/input bindings at the actual execution commit. No broad ledger
validation was run in the sparse checkout.

Primary's publication steps:
1. Review the correction/provenance and complete packet as metadata only.
2. Stage/commit this new directory alongside an exact merge of the single entry
   in run-supersession-registry.fragment.yaml into tools/run_supersession_registry.yaml.
   The preparer did not edit that shared registry. Do not overwrite, regenerate,
   amend or delete anything in the original run folder.
3. Re-run this directory's verify.py and the focused fragment checks. If the
   successor bytes change, generate an additive corrected record and corresponding
   final digest; do not leave registry hashes stale.
4. Publish the archive and refresh PR #2382. Registry registration changes schema
   routing only; the original supervisor receipt remains invalid_output.
5. Required independent scientific review and any future official decisions are
   separate tasks. No output_validated promotion or rerun is implied.

No Coordinator approval is required by the existing additive_schema_completion
registry parser/checks, and none is asserted here. Actual preparing runtime:
Codex; system-reported family GPT-6; exact serving identifier unavailable. The
unverified anthropic Coordinator adapter binding was not impersonated/probed.
