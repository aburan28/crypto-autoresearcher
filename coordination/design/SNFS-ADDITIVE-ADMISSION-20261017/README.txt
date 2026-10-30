Additive admission prototype and native readiness — preparation only
2026-10-17; branch research/snfs-remaining-leads-20261017

Outcome: 28 synthetic fixture tests pass. Production tools, frozen contracts,
claims, shared registries and official scientific statuses were not changed.
No scientific program or new inference session was executed. No new actual
DEC/TASK records, approval, model substitution, commit or push was created.

Files and evidence
- proposed_experiment_preapproval.py: isolated candidate copy of the current
  prospective probe, with an opt-in additive packet schema.
- additive_guards.py: additive identity, exact-byte, original-source closure,
  fresh retry identity, terminal predecessor receipt and narrow manifest
  transport checks. The ordinary packet path keeps its existing behavior.
- proposed-preapproval-extension.diff: focused integration illustration only;
  do not apply it automatically. Production needs separate review, integration,
  regression tests and an actual lawful approval/ownership lifecycle.
- test_additive_admission.py / fixture-tests.xml: four positive combinations
  (transport repair/retry, with/without schema transport) and 24 refusal cases.
  Synthetic Git repositories are created under pytest's temporary directory;
  the actual research checkout is never committed or ref-mutated by the tests.
- native_doctor_readiness.py / native-doctor-readiness.json: bounded actual
  network-enabled doctor, no inference or session probe, allowlisted status
  codes and safe argv only; stdout/stderr retained only as byte counts/hashes.
- production-source-fingerprints.json: binds the exact unchanged production
  source and policy used by this preparation to origin/main.

Test command (pytest installed only into /tmp/snfs-additive-admission-test-deps):
  PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/snfs-additive-admission-test-deps python3 -m pytest -q -p no:cacheprovider coordination/design/SNFS-ADDITIVE-ADMISSION-20261017/test_additive_admission.py
The sealed fixture drivers are never executed. Do not replay the one-shot doctor
writer over its existing receipt. Its saved successful return is the evidence.

Proposed exact packet interface
schema: crypto.autoresearch.additive_preapproval_packet.v1
original: canonical original trial_plan path, original plan SHA-256 and frozen
  specification SHA-256, all matching committed source_ref bytes.
specification: unchanged canonical specification path and exact original bytes.
trial_plan: NEW experiments/<EXP>/amendments/<correction>/... plan path.
amendment: NEW versioned amendment path; its exact SHA-256 is bound by the plan.
queue/handoff: NEW prospective queue/task namespace; old claims are not copied.
preview: exact final specification, amendment, plan, queue and handoff bytes.
approval_decision_id: fresh prospective correction decision identifier, never
  the existing scientific approval reused as new execution authority.
source_ref/lane_id/execution_route: existing published-source, open-lane,
  concurrency and implementation/runbook requirements remain enforced.

The prototype allows only transport_repair or retry. It retains original
experiment/hypothesis/goal/question identity, all scientific argv, trial IDs,
dependencies, trial counts, memory and watchdog values. Original source/input
bindings cannot be dropped or changed. Original output artifacts remain declared.
Every supervisor and trial artifact must have the existing archive coverage and
owner. Unsafe canonical paths, removed archive paths, zero-run handoffs and
insufficient handoff memory are refused. The return always explicitly says
execution_authorized:false; approvable:true is still only a read-only technical
prospective check, not a Coordinator decision or launch permission.

For old E3/D4 manifests, a versioned transport checker is still implementation
work: preserve original driver and science, forward the entire original checker
argv as an exact JSON argument, preserve producer-manifest.yaml, then create a
schema-complete provenance envelope from actual supervisor data. New source and
fixture-receipt bytes must be published and hash-bound. A fixture receipt does
not prove wrapper semantics; source review and actual schema-fixture checks are
separate obligations. Frozen input_bindings may be supplemented in the additive
amendment; the original specification must not be rewritten to add them.

For G1 retry, retain the original full-grid trial and exact scientific argv,
seeds, source hashes and protections; require a distinct RUN destination and a
hash-bound, published eligible terminal predecessor failure. The prior worker
must be confirmed inactive and its old claim reconciled/released at dispatch.
This prototype deliberately does not implement that runtime liveness/claim
attestation or authorize the previously prepared retry automatically.

Required production integration, separately reviewed
1. Add a supported additive-preapproval branch/helper with regression tests;
   keep ordinary preapproval behavior and exact-byte artifact protections.
2. Add explicit additive-plan selection/routing. newest_experiments currently
   starts from canonical trial-plan.json; successful prototype fixtures do not
   create a selector-ready plan. Do not edit frozen old plans as a shortcut.
3. Before launching an additive plan, require its exact amendment and a lawful,
   committed and published Coordinator approval binding experiment, original
   plan digest, new plan/amendment digests, new queue and executor identity.
   Existing load_plan alone ignores the extra amendment field; it is NOT a
   sufficient new approval gate. Keep source/hash checks, archive owner,
   resource checks, original run immutability and live published owner/epoch.
4. For retry, independently confirm no prior worker remains active; never reuse
   an attempted run directory or count a retry as a fresh replication. Reconcile
   dependent review/archive tasks without altering their historical records.
5. Require the final exact production probe, postapproval selection, publication,
   fresh ownership and existing unchanged supervisor gates before /run.

Native runtime provenance: new concrete readiness evidence
The installed CLI is 0.159.2. It accepts --strict-config sqlite_home=... and
log_dir=... under this new directory. A bounded doctor with supported network
permission returned 0: inherited auth, config, state and HTTP reachability
checks passed; WebSocket remained a warning. Cloud API-secret absence therefore
does not establish that native inherited auth is unavailable. No raw auth,
config, environment, response body, transcript or unrelated thread was copied.

The repository already has a privacy-preserving probe-codex-session route.
That route verifies exactly one new thread against its SQLite row and rollout
and check_runtime_bindings. It requires an existing DB before launch, accepts
no CLI configuration forwarding, and resolves rollout files relative to the
DB parent. The current runtime's CODEX_HOME is read-only with no available DB;
our scoped sqlite directory has no genuine session DB/rollout. sqlite_home
relocates the DB, not an established supported rollout/complete-metadata route.
No supported complete relocation was established from exec help, generated
protocol or the retrieved public config schema. This is a missing supported
integration, not a proof that native verification is impossible.

Do not create fake rows, repurpose HOME/CODEX_HOME, copy auth, silently substitute
models, or replace exact metadata checks with doctor success. Future integration
must forward allowlisted scoped config options, allow a genuine CLI-created DB
without fabricating one, and verify exact session metadata for the actual CLI
persistence format. If that format uses paginated storage rather than the
probe's expected rollout file, it needs a separately reviewed exact-session
reader. All persistence must use allowed workspace/tmp paths with inherited auth.
Only after that route is established is a bounded new-session inference probe
appropriate. Its receipt would attest only that new session, not this parent or
delegated session retroactively; actual approval/review must occur in the exact
receipt-bound session as required by docs/inference-backends.md.

Default adapter resolution remains unverified anthropic:claude-opus-5-5/high.
Explicit existing openai Coordinator resolution selects gpt-5.6-terra/high.
This delegated session is Codex, system-reported GPT-6 family, exact serving
model/effort identifier unavailable to this session. It did not pretend to be
either configured model. No native model verification or substitution approval
is asserted, so no new official approval is produced here.

Parent-owned concurrent engineering/search scopes, without canonical changes:
- research/snfs_ecdlp_ledger_20261017/continuation-20261017/e3-projective/
  Projective coefficient encoder/verifier, monic denominator charts, affine/O
  specialization, infinity primitivity, optional Bezout saturation and fixed
  D/chi fixtures. D is encoding/intersection degree under model hypotheses,
  not an asserted canonical height. Parent reports 13 deterministic fixtures.
- research/snfs_ecdlp_ledger_20261017/continuation-20261017/d1-inputs/
  Read-only rank-campaign dependency reconciliation and bounded public-source
  input checking. Parent reports 61 exact rational on-curve checks for candidate
  rank-30/31 inputs and rank-31 cross-source equality. This is not independence
  certification, Gram recomputation or a certified regulator interval. Archived
  validator/red-team numerical limitations and corrected discrepancy remain.
Those parent results are provenance pointers only; this delegated packet did
not independently verify or promote their mathematical conclusions.
