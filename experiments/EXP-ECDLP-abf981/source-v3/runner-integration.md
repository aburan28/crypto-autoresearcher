# EXP-ECDLP-abf981 source-v3 integration

This is a source-v3 engineering candidate under DEC-20260909-7db063 and
TASK-20260909-743734. It preserves execution_approval format_version 1 with
a local ID-compatible schema. It does not claim that the unmodified legacy
numeric-ID approval schema or standalone runner-receipt schema accepts these
records. No standalone receipt or sixth companion is emitted.

The entry uses only standard-library imports and requires --launch-context-fd.
Missing context exits 2 before loading the adapter, benign worker or scientific
kernel. The parent adapter verifies the published authority immediately before
Popen and applies the existing non-root POSIX resource limiter. The child cannot
spawn Git under RLIMIT_NPROC=0. It independently rereads/hash/identity-checks the
published authority, approval, sidecar, current claim/native receipt, pinned
source/dependency files and exact configuration against the parent-verified
snapshot on its anonymous read-only descriptor before selecting the one fixed
benign worker. The descriptor is a capability within the trusted parent process
boundary. It is not a signature or protection against a malicious process with
the same user privileges and ability to replace trusted source/OS state.

The scientific kernels remain inert source inputs. This version cannot create a
scientific capability or admit scientific_execution_authorized:true. The sentinel
receives canonical_lock_verified, claim_verified and source_snapshot_verified
from actual admission; scientific_authority_verified and semantic_gate_verified
remain false. No arbitrary callable/module path or caller boolean selects a
kernel. Future scientific activation must have a separately published decision,
accepted source/semantic reviews, actual execution/claim/runtime ownership and
complete output/archive scope. The frozen models sequence is read_frozen_spec,
finite_payload with a caller-owned partial payload, scientific_artifact_data and
emit_scientific_artifacts, preserving payload.status/scoring_status and partial
failure data. The frozen incidence sequence is exact config_checked semantics
before import, then run_case(config, directory, manifest_context) after all six
gates are established from that future evidence; instrument_valid and
comparison_eligible remain distinct. These are prospective integration duties,
not scientific execution coverage or a current activation implementation.

The adjacent planned-execution.json is an intentionally non-runnable template.
Future executable/version/dependency pins, environment, effective UID, fixture
authority and repaired source snapshot are null. The actual input base commit
must never be substituted for the repaired source snapshot. At QA preparation,
the Coordinator materializes a separate raw JSON sidecar, replaces all nulls with
observations, and hashes this source template as an ordinary snapshot file.
The sidecar does not contain its own hash. Approval and external authority bind
its raw bytes independently; an external authority does not hash itself either.

Parent preparation and bootstrap
-------------------------------

The parent owns all fixture/capsule/claim/Git artifacts. The Executor does not
create a private Git repository or claim, overwrite a historical record, or
populate a real reserved RUN directory. A QA fixture copy must physically live
under coordination/pending-ideas/BATCH-e9d1c7/repair/qa/scratch in the parent
checkout. It has a genuine clean fixture commit descending from the separately
archived repaired source snapshot. Only one actual fixture-outputs/<case>/output
path is excluded from its postflight tree check; there is no broad dirty-tree
exception. Diagnostic directories and barrier endpoints are prepared by the
parent. Barriers use explicitly bound FIFO identities outside the clean fixture
copy, within parent QA scratch, so they do not invent ignored Git state.

The outer CLI is:

    <trusted-python> -B harness/finite_yaml_locked_v2.py \
      --lock <fixture-lock> --expected-sha256 <parent-published-sha256> \
      --run-id <exact-reservation> --authority <parent-reference-capsule>

The reference capsule is strict JSON with exactly authority_repository,
authority_path, authority_sha256, publication_commit, publication_ref, case_id,
and git:{path,sha256}. authority_path is exactly
coordination/pending-ideas/BATCH-e9d1c7/repair/qa-admission/fixture-authority.json.
The only bootstrap executable is the OS-trusted /usr/bin/git; a capsule cannot
select a different executable. The repository must be the implementation
checkout or a physical ancestor checkout of a QA copy. The ref must be that
checkout's refs/remotes/origin/<current-branch>. The full commit must be reachable
from that fetched remote ref, and its authority blob must equal current bytes
and the capsule digest. The deployment trust root is parent-controlled source,
interpreter, checkout and OS tools. Capsule hashes alone do not create authority.
Network publication/fetch is the parent's duty; this adapter only reads local
Git state and never contacts a provider.

The published authority record has schema
crypto.autoresearch.finite_yaml_fixture_authority.v1, approved_by:coordinator,
decision_id:DEC-20260909-7db063, scientific_execution_authorized:false,
source_snapshot, approved_base_commit, tools (git and ps path/SHA pins),
owned_run_ids, claim (path/sha256/record), native_receipt (path/sha256/record),
claim_overlay_sha256 and cases. The overlay digest is canonical JSON of the
sorted {path,added_commit,sha256} observations from all immutable claim/release
additions for the task across git log --all. This matches the actual ordinary
branch claim transport; it does not invent a refs/claims namespace. The adapter
also checks live claim/release files, exact owner/task/epoch/branch/parent-session,
actual acquisition/expiry, and current output ownership.

Each case binds case_id, fixture_root, fixture_commit, experiment_id, run_id,
lock:{path,sha256}, plan:{path,sha256}, approval_document_sha256 (canonical parsed
approval JSON), run_object_sha256, claim and fixture_authorization. Optional
prelaunch_mutation is a fully specified target/before SHA/after UTF-8 mutation
of a disposable copy. fixture_authorization binds case_id,
scientific_execution_authorized:false, simulated_reservation, output_directory,
terminal_diagnostic, worker:{path,sha256}, worker_input:{path,sha256},
worker_input_document_sha256 and optional barriers. The worker path is fixed to
tests/fixtures/finite_yaml_locked_v2/worker.py. No unknown serving/runtime values
may be substituted with historical producer values.

Every native receipt carries actual thread_id/turn_id/parent_thread_id,
requested_policy/model/effort and configured model/effort, provider/resolved
model/served effort, model_verified, adapter_probe_performed, fallback/degradation
fields and metadata_source. Unprobed/unexposed serving fields remain null. A
verified claim needs a separately hash-bound matching probe record. Literal ultra
and a fresh QA thread are required. The claim's session is the parent control
plane and is compared to parent_thread_id, never relabeled as the QA child.

Dependency and environment closure
----------------------------------

The sidecar pins python:{executable,version,sha256}; complete source_closure and
protocol_hashes; and dependency_closure with python, stdlib, distributions,
loaded_images and module_origins. stdlib names its actual sysconfig root and all
.py/.so/.dylib/.zip files excluding site-packages, dist-packages and __pycache__.
Each named distribution carries actual version and all installed regular files
except bytecode, including metadata. PyYAML and complete JSON Schema runtime
distributions are mandatory. Actual imported module names/origins must exactly
match the separate outer/child maps and every origin must be in the bound file
closure. The existing core runner/records/research_budget modules are source
pinned before import. No scientific import is used to discover dependencies.

Loaded-image identity is observed separately for outer and isolated child. On
macOS it is the mapped Mach-O LC_UUID plus SHA256 of the actual load commands;
this is explicitly not a file-byte hash of an inaccessible dyld shared-cache
image. On Linux it is the mapped executable-library file SHA256. Missing support
refuses. The external parent must observe these exact identities; examples with
null or invented values cannot launch. JSON Schema is a complete Draft 2020-12
implementation, not the legacy subset validator.

The outer is launched with an explicit environment matching environment_policy.
outer exactly. PATH resolves the pinned Git/ps binaries. The child receives only
inner; absent_test_keys records deliberate benign canaries. Loader/startup
injection and credential-variable names are refused, and no broad environment
snapshot is archived. The fixed worker examines only FINITE_YAML_QA_CANARY.

Output and status boundary
--------------------------

The parent creates the output directory and captures/command/environment files
exclusively, with descriptor-relative no-follow checks. stdout.txt/stderr.txt
remain the original captures in both profiles; stdout.log/stderr.log are separate
byte-identical regular copies. Every ordinary nonmanifest profile/companion file
has a SHA256/byte-count entry. Identity, nlink, missing/extra membership and every
hash are checked before the manifest's exclusive creation. Manifest and directory
are fsynced last, with no self-hash. Collisions preserve existing bytes and create
only the separately owned terminal-diagnostic.json; missing canonical manifests
stay missing. No placeholder scientific output is created by the adapter.

The run envelope targets the unmodified run-manifest.schema.json and current
applicable ledger check_run. code.commit is the actual fixture launch commit;
source snapshot, authority publication, fixture and later archive commits are
separate. Inputs include fixture_only:true and simulated reservation. Certificate
is none with verified/verifier null. Exact argv and quoted command, raw child
cause, real native/claim provenance and all seven protocol checks plus additional
checks are retained. No standalone runner-receipt format is emitted.

Resource and implementation causes survive independent postflight failure.
Unquiesced/unsupported monitoring is infrastructure failure. A clean exit 0 needs
all authority/integrity/output checks for operational completed_valid. Sampled
RSS zero is observed_zero_with_sampling_limit; poll sleep is 0.01 s but ps work
increases spacing, sample count is unavailable, and brief peaks can be missed.
CPU is measured; the default research CPU cap remains null. Actual timeout,
allocator and fork-refusal tests remain deferred until parent admission.

Validation and resumption
-------------------------

Run preliminary checks with Python -B and task-owned TMPDIR:

    python3 -B tests/test_finite_yaml_locked_v2.py --evidence <new-scratch-json>

The command records all 154 cases as executed/deferred/failed. Pure helper checks
are explicitly distinguished from normal-admission coverage. It additionally
checks seven exact configurations and boolean-version refusals as metadata only.
For a complete QA suite the parent provides --admitted-index, mapping each case
to its actual capsule_path, lock_path, expected_sha256, run_id,
expected_predicate, expected_status, evidence_paths and prelaunch_mutation.
The test program never supplies its own authority. It requires clean child-success
and both profile baselines before relying on negative validity comparisons.
Full fixture bytes, outputs, identities and errors are retained by content hash.

The 154 recipes are frozen in tests/fixtures/finite_yaml_locked_v2/cases.json and
repair-disposition.json: 86 original regression questions plus 68 additions.
The Executor's preliminary report is not independent QA. After the parent creates
the exact TASK-20260909-ef0b82 source snapshot, fresh TASK-20260909-0bc778 QA
must establish actual full-path results, including barriers, aliases, resource
limits, independent schema/ledger validation and target-specific drift predicates.
Any missing or failed control remains unmet. Scientific execution remains zero.

The models profile contains 15 filenames: ten original names including both text
logs, plus exactly command.txt, environment.json, stdout.log, stderr.log and
raw-result.json. raw-results.json is the separate frozen instrument output. Its
two rows are p11/RUN-ECDLP-56d8aa and p23/RUN-ECDLP-591253. All constants come
from the raw hash-pinned specification; caller overrides are rejected.

Conservative checkpoint limitations
----------------------------------

The raw-result launch_receipt.wrapper_postprocessing mirror is explicitly null:
its required elapsed boundary includes hashing raw-result itself, which happens
after those immutable bytes are written. The actual measurement is recorded in
run.resources.wrapper_postprocessing after core-artifact hashing. This is an
UNMET frozen mirror requirement, requiring additive Coordinator clarification.
The adapter records receipt_wrapper_timing_mirror_complete:false and cannot emit
completed_valid in this checkpoint; it does not silently relax acceptance.

Actual canonical claims/native receipts remain protected. No claim/native mirror
API was added in this checkpoint. The declared disposable-copy drift controls
remain DEFERRED/UNMET: a future additive implementation must bind initially
byte-identical named mirrors in addition to genuine originals, recheck both, and
label mirror-integrity observations separately from real expiry/release/epoch
or runtime-provenance events. This gap is not evidence about either hypothesis.
