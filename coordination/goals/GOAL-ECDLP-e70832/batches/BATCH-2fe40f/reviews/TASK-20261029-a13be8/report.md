# Independent delivery, isolation and metrics source review

TASK-20261029-a13be8 · BATCH-2fe40f · session /root/controlled_delivery_review · 2026-10-29.

**J-delivery and J-metrics break on this source snapshot. Actual runtime isolation remains unqualified.** The named custody-before-label gate rejects missing ACK, incomplete collection and nonquiescence in deterministic mocks. Several later integrity checks accept inconsistent inputs, and the report renderer loses required material. These are source-readiness findings, not scientific observations or a verdict on any algorithm, exponent, family, usefulness or scalar-ordering hypothesis. No new 48-curve study was frozen or launched.

The reviewed executable revision is C = 1b41962f1ae578b452319f1bf4b92f5388294093. Actual source_payload checks verified the five worker and thirteen host manifest entries against committed C blobs and live bytes. All 26 paths in the source snapshot receipt's archive_binding.path_sha256 match actual live SHA256 values; the receipt itself makes the 27th bound path. Its actual SHA256 is 2c37b1860bce933f63b4529fedba2e8cbf5748b54c8a0187babdce4e105b110f. Coordinator-supplied snapshot f28bac0066, source d9e9ce106cdfbbf32a16120f84b028c21529d258 and published-inputs 16ef166fde are dispatch provenance; this session did not independently qualify their abbreviated reachability. Exact source hashes and honest read depths are in read-attestation.yaml.

## Reproducible observations

checks.json contains the complete executed C1/C2 Python heredocs, exact combined stdout/stderr and shell return codes. Both harness commands returned 0 because they record each observed outcome, including accepted bad mutants. A harness return code is not a passing verdict for every guard. The missing-counter-family mutation produced a real jsonschema.ValidationError and was retained; no producer source was silently repaired.

Only disclosed software fixtures ran: F11 with p=11,a=1,b=6,r=13,P=(2,7),Q=(7,2),known k=7, and F23 with p=23,a=11,b=5,r=17,P=(5,22),known k=7. SHA256 reference streams used fixed all-zero 32-byte seeds. No fresh sampler/cohort/point draw, nonce, old-cohort analysis, actual SDK import/call, VM, network request, timing benchmark, credential use, canonical edit or Git mutation occurred. Temporary fixture trees were removed after their exact programs and outputs were captured. Repeated F11 display rows were rendering fixtures, not twenty observed curves.

| Check | Actual observation |
|---|---|
| Actual worker/host source_payload | Five/thirteen committed and live bindings accepted |
| Direct host.verify/reference import injected into worker source | Rejected by audit_closure |
| Missing ACK, false ACK, nonquiescence, incomplete collection | Rejected before custody capability |
| Missing one of seven raw files | Rejected |
| Producer transport/postrun regression suite | All 17 tests pass; complete/failed/partial fixture exports and source refusals retained |
| Corrupt supervisor archive | driver.check(supervisor root) rejects; postrun(supervisor root) calls sentinel host verifier once and returns complete |
| Worker protocol/source pins changed consistently to ff/ee vs controller/config00 | Real verify_bundle is called by postrun and returns checked; postrun complete, no errors |
| Remove retained single and also lower worker host-plan expectation/IDs | Real verify_bundle returns checked with singles=0 |
| Relabel F11 fixture as confirmation-A-16-0 with calibration arm/original-only trace | Real verify_bundle returns checked |
| Duplicate schema key in a single-point JSON row | Real verify_bundle returns checked |
| Remove final newline from sealed trace JSONL | Real verify_bundle returns checked; later analysis has its own stricter parser |
| Divergent manifest.yaml IDs/status and raw-result run/experiment IDs | driver.check returns transport_evidence_integrity=true, complete |
| Remove required trace counter families | Rejected by schema, correctly; retained exception is not reported as an accepted omission |
| Runtime fact mocks | Wrong UID/group, extra environment, inherited FD9 and writable parent rejected; expected mocked facts accepted |
| PDF with twenty F11-derived rows plus failure canary | Markdown keeps row19/error; extracted PDF omits both, calibration and reference canaries absent |
| No-draw job construction | 382464 distinct job IDs, 216 setups, 345600 singles, 24576 calibration traces, 12288 confirmation traces, 73728 cells, 1033728 physical predicate calls |

## Load-bearing findings and minimal repairs

**D1 — high: postrun bypasses supervisor evidence integrity.** In postrun/run_postrun.py::run the input is replaced by out/'modal' before driver.check(out). The checker therefore takes its inner check_transport route, bypassing raw-result.json, modal-evidence.tar.gz and the archive member manifest. In C1 the archive was replaced by the literal bytes CORRUPT-ARCHIVE. Direct driver.check on the supervisor root correctly raised “evidence archive hashes”; the same supplied root passed postrun far enough to call the host sentinel and return complete. The source-level defect occurs before the verifier injection branch; the sentinel demonstrates reachability without drawing host entropy or executing scientific work.

Keep the supervisor root, validate its complete envelope/archive first, and then descend into modal. If a standalone inner-tree mode remains useful, make it explicit and scope its integrity statement. Test the normal CLI path with corrupted archive, missing members, divergent duplicate controller receipts and failed/zero-data trees; require no host module import/seed draw or verifier call on a rejected supervisor envelope.

**D2 — high: host source/protocol provenance is compared with worker-produced metadata rather than the independent invocation pins.** The collected host-plan supplies provenance to verify_bundle, which checks agreement among plan, summary and completion. postrun never compares those protocol/source fingerprints with the controller plan/config/protocol snapshots. C2 changed the three worker-produced pin objects consistently to protocol ff… and source ee…, retained controller fingerprint00 and config protocol00, recomputed legitimate byte seals, and called the actual independent verifier through postrun's supplied-verifier test seam. Verification returned checked and postrun returned complete with no errors. This demonstrates the missing cross-boundary comparison; it does not claim the fixed source actually emitted forged data.

The production branch also reopens a current repository host manifest via config['inputs']['host_manifest']['path'] without first requiring its bytes/hash to equal the frozen copied binding, or recomputing and comparing the worker+host source fingerprint with the controller plan. source_payload proves each supplied manifest's committed/live contents, but does not make it the manifest used for this run. Already-imported postrun/controller/driver/analysis/renderer/export code also needs the executing-byte binding checked as part of the host route.

Before host label work, verify all copied static input hashes against the invocation config, protocol's static-input binding and controller plan; recompute source fingerprint from the copied manifests; match actual host executable bytes and the precise manifest revision/map; require host-plan provenance to equal those independently authenticated pins. Preserve wrong-pin failures. Add a test against the ordinary production branch with entropy patched to fail if reached before binding checks, in addition to the injected-verifier seam used here.

**D3 — high: the host does not independently reconstruct the frozen workload or public population law.** worker_runtime creates host-plan IDs from worker-generated jobs; verify_bundle compares rows with that same plan. The host does not derive the 48 stage/tier slots, 1800x8 calibration singles, 128x8 calibration traces, 64x8 confirmation traces, six cell IDs or public target mapping from the frozen static law independently. Its mathematics certifies valid curve/order/base/subgroup points, but not the production stage/tier/exclusion law. C2 removed the one fixture single and changed worker plan/summary/completion counts consistently; checked was returned with singles=0. Another C2 fixture substituted confirmation-A-16-0 for the F11 identifier while keeping r=13 and a calibration arm/original-only trace; checked was returned. These are fixed-fixture semantic mutants, not new sampled domains.

The producer job generator's no-draw counts themselves agree with the proposal. Independently, 24x1800x8=345600 singles; 24x128x8=24576 calibration traces; 24x64x8=12288 confirmation traces; 192+24=216 setups. Across three equal bit strata, mean L is 14: calibration queries344064, paired confirmation queries344064, hence total1033728. Six cells reuse each confirmation trace; they do not multiply predicate queries. Correct construction counts do not replace independent retained-ID validation.

Have the host build expected IDs/counts from independently implemented frozen stage/tier/arm/replicate rules and authenticated public cohort, then compare the worker plan as evidence rather than authority. Check exactly48 curve slots, actual r.bit_length(), unique (p,j) across stages and against the frozen exposed exclusions, exact public target counts/IDs, every paired designation and all six cell records. Keep a separately declared known-fixture law for these deterministic tests. Do not permit arbitrary specimen labels to silently opt out of production rules.

**D4 — medium: host raw parsing accepts ambiguous and partial records.** verify.py::iter_records uses plain json.loads on unbounded file iteration; completion/summary/cohort also use plain loads. Duplicate keys are overwritten before schema validation. C1 inserted an earlier wrong schema key in a single-point object, retaining the legitimate final schema key; the resealed bundle returned checked. Removing the final trace newline also returned checked. This conflicts with controller.read/analysis.rows, which reject duplicate keys or partial rows, respectively. The later analysis parser can reject the missing newline, but the independent verifier's checked receipt is still too permissive. No isolation violation is asserted merely because malformed later rows can be detected after an Oracle exists: the specified load-bearing ordering is collection/seal/quiescence/termination ACK before labels.

Use one strict bounded parser contract for every host JSON/JSONL input: duplicate-key rejection, finite numbers, complete newline-delimited records and the frozen maximum line bytes. Add duplicate-key and partial-row tests directly to verify_bundle, with all hashes valid, so a byte-integrity test cannot hide a semantic parser gap.

**D5 — medium: supervisor IDs and run manifest are not checked, and the exporter substitutes a run identity.** driver.check verifies raw-result/inner receipt/archive bytes, but never reads manifest.yaml or compares its run/experiment identity/status with raw-result. C2 changed manifest to RUN-WRONG/EXP-WRONG/failed and raw-result IDs to RUN-OTHER/EXP-OTHER; check still returned complete. make_export then synthesizes protocol_id+'.supervisor' instead of carrying the allocated supervisor RUN-* identity. The postrun export file list is built from inner modal JSON/collected data and postrun outputs; it does not bind the parent supervisor envelope/archive. The source inspection, rather than a newly frozen protocol experiment, establishes the exporter identity mismatch.

Require agreement among allocated run ID, protocol experiment ID, manifest, raw-result, controller receipt and unified export row. Link/hash the complete supervisor evidence in the export as well as raw candidate records. Check these without rewriting historical records. The deliberate skeletal fixture protocol remains unqualified; its actual checker findings must stay present.

**D6 — medium: the rendered report drops failures and most required output.** render_report.py puts only report[:24] on PDF page1, regardless of row count. With twenty display rows the extracted two-page PDF included rows0–13 but omitted row19 and the failure canary, while Markdown retained them. The renderer never reads calibration.json or references.json, so neither format presents calibration/error histograms, BSGS/uniform/null outcomes, cost vectors or cold/warm scope. The plot combines all retained outcome counts and indexes fractions without named A/B panel summaries; it is insufficient as the full standalone observation report. export validation is also computed after rendering, so those findings cannot appear in the current report.

Paginate all required rows and operational/export failures; present separate calibration and confirmation-A/B sections, six-cell outcomes, unique targets and paired discordants, retained reference/null eligibility/support/duplicates/ties, and complete cost-scope summaries with links/digests. Render after export findings are known, avoiding a circular self-hash design. Include the backend, counter-replay and clock limits explicitly. Verify first/last rows and failure/reference canaries by PDF text readback and inspect the final rendered pages. This session performed PDF text readback only; no independent visual-appearance qualification is claimed.

## Isolation and cost boundaries that survive this review

The exact worker manifest is five files. Actual current source has no host/BSGS/reference import; constructor/engine use public coordinates and arithmetic, and source_payload enforces committed/live bytes. BOOTSTRAP makes /work plus source/stage parents root-owned, clears the environment, uses UID/GID1000 with cleared groups/no-new-privileges, closes descriptors/stdin, observes remaining UID1000 processes, seals outputs, streams/readbacks files and waits for provider termination before custody is eligible. OS-fact mocks exercise the UID/environment/FD/parent-write checks. These establish source branches only, not actual VM access denial, process isolation, complete root-bootstrap behavior or provider observation.

Static primary inspection of installed Modal1.6.2 confirms terminate(wait=True) awaits wait(raise_on_termination=False) and returns the sandbox exit code; it need not return zero. The controller correctly retains the provider return code. create accepts the named VM runtime, cpu/memory tuples, blocked network, workdir and identity-token option; its network source sets BLOCKED. No actual SDK was imported or called.

A separate defense-in-depth gap remains: audit_closure accepts importlib.import_module("host.verify") because importlib is standard library and only Name calls to __import__/eval/exec are prohibited. C1 proves that AST acceptance without importing the injected module. This payload is absent from the reviewed worker; it is not evidence of current contamination. Either restrict dynamic-loading capabilities/stdlib usage and test aliases, or narrow the audit's documented promise to a static-import screen supported by exact source review and runtime filesystem denials. An injected sixth host file is already denied by the exact worker manifest/runtime closure contract.

custody_for alone accepted duplicate raw manifest entries and omission of host-plan; the ordinary postrun driver.check layer validates duplicate entries, and later plan access would fail. These local helper observations are retained, but are not promoted into a demonstrated end-to-end duplicate-path bypass. Keep capability construction self-contained if it will be called elsewhere.

Uniform references correctly use distinct nonzero scalars and min(M,r-1): fixed F11 M0/1/12/22 yields effective0/1/12/12 with exact denominators12; F23 M0/1/16/26 yields0/1/16/16 with denominator16. Saturated lists contain every nonzero scalar once and succeed on known k7. M=0 has no public equations and a retained false success. Candidate M determination remains excluded from this conditional reference and must be paid in a standalone interpretation.

Working BSGS solves known k7 on both fixtures, retaining separate setup and online vectors, table payload, cold_includes_setup=true and warm_setup_increment=0. Consumers must add setup once per actual object and not sum its repeated disclosure across targets. Exact full-mask null controls retain1023 with-replacement draws: F11 support32/unique32/duplicates991 and F23 support128/unique128/duplicates895; multiplicities sum1023, repeated bank/start duplicates are retained, tie counts each total1023, inferential_p_value remains null. These controls use deterministic disclosed fixtures and an all-defined diagnostic mask, not a new candidate population or significance test.

analysis correctly associates decoder cells through trace_id because actual cell schemas lack curve_id. It retains six-cell outcomes, caps/undefined/empty/rejected/zero successes, null denominators for zero-success cost ratios, and stores original/incremental physical trace vectors once rather than six times. Decoder ratios remain component-only; setup/common and host reference vectors are separate. Raw singles/sampler/RNG/proposal vectors remain data rather than a qualified complete end-to-end advantage. Host and worker backends differ; public-equation checks and nonnegative schema checks do not replay worker counters. The rejected missing-counter-family test shows that this particular schema guard exists. The negative-counter test used an incomplete family object, so its observed rejection establishes the family-schema guard, not an independently isolated negative-leaf test.

No clock qualification, independent worker counter execution replay, RSS/native memory or Python interpreter/I/O/integer-cost qualification exists. wall_valid=false and counter_replay_qualified=false survive the outputs inspected. Preserve those limits through any repaired report. Additional A/A/reset/reordering/isomorphism/perfect-half/wrong-root/clustered-error controls still need exact implemented IDs/counts or explicit prospective excuses in a separately frozen lawful protocol. Optional FFT/SFT/Gray work was omitted and is not qualified here.

## Provenance, scope and handoff

The handoff and prewritten review-plan were read first. agents/reviewer.md was absent; the actual Validator and Red Team contracts were then read. Named older decoder/controls/review notes supplied literature and observation context. The locally installed SDK implementation was read as primary API source without import. No external primary papers were fetched under this no-network card; no literature completeness or novelty inference rests on those internal reports. No current sibling TASK-20261029-182d42 report or source-review-package content was read. Requested review-adversarial/xhigh is recorded as requested; serving model/backend/usage/probe remain null because no actual receipt was observed.

An initial metadata-hashing command failed with KeyError('archive') because the reviewer looked up the wrong receipt key. The corrected reader used archive_binding and verified all26 actual hashes; both command records are retained. Initial absent outside-package/reviewer-file lookups and truncated combined reads are disclosed in the attestation. A first combined final-file write command was rejected before process creation because its argument list was too long; delivery was split into individual file writes. These are reviewer retrieval failures, not producer source corrections.

Root owns canonical application, archive TASK-20261029-332f28, claims/releases/publication and any readiness decision. Return D1–D6 as one explicit repair packet, preserve this snapshot and these failed controls, then independently recheck the changed joints with source-bound deterministic regressions. No producer file was edited by this reviewer. No canonical scientific graph changed; the diagram below records only this audited source handoff. The assigned three-file scope leaves any PDF/graph rendering of this review to the Coordinator.

~~~mermaid
flowchart LR
  A[Frozen static protocol and manifests] --> B[Candidate-only worker]
  B --> C[Root seal and complete collection]
  C --> D[Quiescence and provider termination ACK]
  D --> E[Host verification and references]
  A -. missing independent pin and schedule comparisons .-> E
  F[Supervisor envelope and archive] -. postrun bypasses check .-> E
  E --> G[Retained analysis and export]
  G -. PDF truncation and omitted outputs .-> H[Standalone report]
~~~

## review_attestation

- joints_owned: J-isolation, J-delivery, J-metrics.
- sources_read: exact actual paths/hashes/read depths in read-attestation.yaml, including hash-only distinctions.
- read_sibling_reports: false.
- verdict: breaks on J-delivery/J-metrics; actual runtime isolation inconclusive; named ACK/custody negative controls hold.

