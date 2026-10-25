#set page(paper:"a4",margin:19mm)
#set text(font:"Helvetica",size:10pt)
#set par(leading:0.5em)
= ECPP cohort implementation: V9
2026-10-25 UTC · TASK-20261024-4f1bf4 · GOAL-NISTSEED-ab8949

*Named cohort orders executed: 0. Legacy programs executed: 0.*

The final guarded static/mock suite passes: syntax exit 0, nine methods, zero failures and zero errors. The retained log reports 30.673 seconds on Python 3.12.8 / macOS 26.6 arm64. The guard records zero attempts to call original legacy functions or subprocesses. All output in these tests comes from injected fake artifacts.

#figure(image("status.svg",width:100%,height:54mm,fit:"contain"),caption:[Engineering custody and prospective next steps. Dashed edges are unmeasured.])

== What passed
The nine methods cover complete admitted output, consistent censored envelopes and corrupted-censor refusal; exact producer/checker mappings for all 21 curve identities; mutation refusal at independent semantic checks; manifest, supervisor, status, started-record and raw-inventory checks; A/A semantics; trace/catalog/raw-byte offsets; and the actual supervisor complete_manifest function on mock data.

All 18 frozen task inputs still match their original hashes. Published P-224 matches the existing certificate with its exact coefficient under side=other. The current four source/schema digests equal the V9 receipt. The reports-only V10 patch changes none of those files. A synthetic certificate exercises the bounded software interface; it is not a mathematical proof.

== Retained captures
#table(columns:(0.6fr,0.8fr,0.8fr,0.8fr,2.6fr),inset:4pt,
 [Capture],[Methods],[Failures],[Errors],[Recorded obstruction],
 [V1],[4],[1],[0],[Trace-expression assertion],
 [V2],[5],[1],[1],[Provenance and path handling],
 [V3],[5],[0],[2],[Actual container/catalog contracts],
 [V4],[7],[0],[23],[Cascading exact P-224 join errors],
 [V6],[9],[0],[29],[Cascading JSON bytes errors],
 [V8],[9],[1],[4],[Censored status / mutation metadata],
 [V9],[9],[0],[0],[Final guarded suite passes],
)
V5 was a metadata-only diagnostic and incomplete test proposal; V7 was a source patch. Neither is a full-suite capture. Error counts can cascade from one early gate. They are not independent curve observations or replications. Every prior failure is retained.

#pagebreak()
== Reproducibility and delivery
The exact observed command is in report.md and IMPLEMENTATION_REPORT.md. The V9 receipt retains source digests, platform, Python, timestamps and guard status. Source-bindings.json binds that receipt, the per-method log, the operator guard and the partial-clone fixture. The complete 18-input table and four source/schema hashes are in the implementation report.

A separate two-case regression fixture reproduced the artifact-check lookup error in a blobless Git clone. Full object IDs permit fetching the 1,024-byte data fixture; the unchanged policy still rejects the 1,100,000-byte data fixture. The workflow caller now requests 40-character object IDs. No storage limit or required gate was disabled.

Main was merged at f61b6e66d471c09feab45a0610853e646e208fb1. A read-only source comparison confirms that the mock-tested supervisor complete_manifest function remains byte-identical. Changes elsewhere in upstream plan admission do not change that function. No redundant mock rerun was performed after reports-only edits.

The official canonical-store migration was refused at S3 HeadObject with HTTP 403. Artifact-store-push-v1.json retains the command/error and verifies all five pre-existing local runtime/PDF hashes unchanged. No upload or manifest success is asserted. The V6 mock log is retained losslessly as .log.gz with a round-trip receipt. This delivery-access obstruction changes no cohort observation.

== Scientific question still open
The prospective study asks whether the recovered period primality software treats eleven reconstructed omitted orders differently from ten published controls. This report contains no ECPP label, catalog traversal, certificate outcome or runtime for those named inputs. A measured software difference would still need original-caller evidence before historical attribution.

The implementation snapshot, separate frozen specification and plan, actual preapproval, committed approval and ready-state verification precede a future run. The original caller and keep/skip trace remain absent. The broader search for a shared hidden weakness remains open.

== Graph and evidence custody
The canonical admission.dot and admission.svg were updated together to reflect the passing implementation tests. Weakness, isogeny and ECDLP frontier graphs remain unchanged because this round establishes engineering behavior only. All references below are internal, retrieved evidence.

*Raw evidence:* coordination/goals/GOAL-NISTSEED-ab8949/batches/BATCH-08d006/ contains versioned V1–V9 receipts and logs, source proposals, patches and guard wrappers. Source-bindings.json beside this PDF gives exact selected paths and SHA-256 values. The original code and 18 input bindings are under experiments/EXP-NISTSEED-6886da/implementation/ and the canonical task handoff.

*Limits:* fake artifacts do not validate the scientific execution path on real orders. The passing tests alone authorize no scientific run or research-state transition. Historical selection and mathematical weakness are separate unresolved questions.
