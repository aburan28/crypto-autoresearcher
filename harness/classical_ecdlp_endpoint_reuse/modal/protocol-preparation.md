# Prospective Modal admission for EXP-ECDLP-2b4ff1

This is one provider and transport correction of the existing experiment.
The original `experiments/EXP-ECDLP-2b4ff1/protocol.json` and existing handoffs
remain intact. The successor is
`experiments/EXP-ECDLP-2b4ff1/protocol.modal-vm.v1.json` (protocol version 2).
Preparing these files grants no execution authority.

The six native arms, 64 curves × two replicates × 64 ordered targets,
768 child executions, cost and memory accounting, seed laws, private-label
custody, arena cap, prefixes, controls, analysis, stopping, scientific
3600-second global/child watchdogs and one-attempt/no-restore policy are
preserved. Native source A is
`fe01ccd832832488c58abeef17548b0a8db6035f`. The Modal adapter has a separate
source-B commit and per-file source provenance. The analysis remains the
original source-A file, SHA-256
`9e1293af171167065d966366cbc41d29457a9bd3b4be95e166870ddc44293abf`.

The official schema already supports `execution.backend="modal"`.
`execution.placement` and `extensions.modal_vm_route` carry the VM and
provider identities. Actual `ap-*`, `im-*` and post-create `sb-*` values are
Modal object IDs. `instrument.image_digest` stays null. No OCI registry
digest, L2, dedicated physical host or physical-core pinning is asserted.
The retained L2 field is the unachieved timing threshold. Every wall/CPU
clock stays `wall_valid:false`, including uninterrupted children; counts
and observed RSS are the registered measurements.

The route requests and limits two physical CPU cores (four vCPU equivalent)
and 12288 MiB, one native child at a time, UID/GID 1000, VM runtime and blocked
workload networking. No Secrets, OIDC identity or account volumes enter the
workload. Lifecycle watchdogs are 5400 seconds for the Sandbox, 600 for
staging, 4200 for its engine command and 600 for collection. The supervisor
permits 5700 seconds to retain and seal its local evidence after the
5400-second provider lifecycle. These are machine protection limits and
change no scientific count, stopping rule or campaign budget.

## Pin, freeze, draw, then admit

1. Finalize and commit every Modal source before building, including the
   engine, controller, exporter, admission driver and preparation builders.
   Keep source-A native/cohort/verifier/analysis bytes identical. Build from
   committed allowlisted blobs only. Retain actual App/Image IDs, build-info,
   native executable SHA-256, compiler executable hashes, A/B source-tree and
   adapter/context manifest hashes, and code-only software-probe receipts.
2. Run `modal/build_protocol.py --image-receipt ACTUAL_RECEIPT --build-info
   ACTUAL_BUILD_INFO --out FRESH_PREVIEW`. Its optional binding-path arguments
   name the eventual repository receipt paths. It refuses missing real pins,
   source-A replacement, a data-bearing image, changed analysis, an altered
   predecessor or existing output. It produces a draft, never a freeze.
   `--draft` is explicitly unpinned and cannot establish readiness.
3. Put the actual receipt/build-info and successor protocol at their chosen
   canonical paths. Validate the successor with
   `python3 tools/experiment_protocol.py validate PATH`. Set up and perform
   the real official freeze, commit it and retain its exact canonical/file
   hashes. No target inputs belong in this hash dependency chain.
4. Use the existing cohort custodian's committed source/protocol lock with
   source commit B, which contains the byte-identical source-A cohort files.
   Retain the separate native source-A pin. Commit the lock; only afterward
   draw the external nonce/private entropy and generate the single registered
   cohort through `cohort/prepare.py`. Its README and built-in chronology
   checks remain binding. Do not reveal private labels before actual output
   seal. Package only the sealed `public/` tree with the existing public-input
   bundler; do not regenerate or replace any sampled instance.
5. Create three JSON objects: `source-pins.json` is a nonempty mapping of
   repository-relative source paths to exact SHA-256; `input-pins.json` maps
   exact source-bound public files/receipt files and any external public
   bundle to SHA-256; `bindings.json` maps `image_receipt`, `build_info`,
   `public_bundle`, `inputs_manifest` to their exact paths. Input pins must
   also include the canonical successor protocol. All source paths must be
   committed and pushed at the selected `origin/...` ref. The admission
   builder enforces the complete allowlisted native-A and current adapter
   source closure. Relative input paths likewise need committed exact bytes;
   external absolute files are checked by digest by the official probe.
6. Run `modal/prepare_admission.py --protocol FROZEN_PROTOCOL --source-pins
   SOURCE_PINS --input-pins INPUT_PINS --bindings BINDINGS --prospective
   --out NEW_OUTSIDE_CHECKOUT`. This creates only preview files. The projected
   approved/frozen fields are exactly the hypothetical states the official
   read-only preapproval tool requires; `authority.json` states that no
   approval, live claim or execution authority was created. The default mode
   instead leaves review-required/unapproved drafts and is expected to fail
   official preapproval.
7. Register and push a lawful open lane for its exact queue, within the
   goal's `max_concurrent:1`. The newly allocated candidate lane is
   `BATCH-b1c6e1`; verify existing ref-visible lanes before opening it:
   `python3 tools/goal_lanes.py lanes GOAL-ECDLP-e70832 --json`.
   `goal_lanes.py open-lane --help` gives the required owner/session arguments.
   The lane's `dispatch_queue_path`, packet `lane_id` and queue path must
   agree. Commit/push the unchanged canonical review-required specification,
   goal concurrency record and actual lane before the probe.
8. Run `python3 tools/experiment_preapproval.py --packet PREVIEW_PACKET`.
   Preserve the complete report. Only `approvable:true` for these exact bytes
   permits the Coordinator's separate approval decision and exact-path
   design snapshot/archive. The probe alone never authorizes a run. The
   archive covers the actual frozen successor, version-2 specification, trial
   plan, queue, new executor/archive handoffs, source/input bindings, image
   receipts, correction/approval decisions, lane and source/protocol lock.
   Use an actual `content_at_commit` receipt if binding files whose future
   state can change; never invent a future commit or path hash.
9. Publish the actual approval/archive and require
   `python3 tools/newest_experiments.py --experiment EXP-ECDLP-2b4ff1 --json`
   to report `execution_state:"ready"`. Only then publish a real owner/epoch
   claim for the new executor task and invoke the existing supervisor through
   `/run`. The implementation-tier handoff is intentional; no linted
   mechanical runbook is asserted. Missing external model API credentials
   do not automatically invalidate an interactive Codex session.

The trial's literal command is `python3 modal/admission_driver.py run` with
the pinned image receipt, frozen protocol, sealed public bundle/manifest hash,
reserved run ID and supervisor `{run_dir}`. The checker is the same source
with `check --out {run_dir}`. The generated plan uses full repository paths.
The controller creates one real VM and launches the engine once; ambiguous
submissions are reconciled against that same observed Sandbox. Collection
may be resumed for the existing Sandbox without launching another engine.

## Archive and observation scope

The controller records the actual sealed remote parent output archive hash,
part hashes, member manifest, returned-byte hashes and readback result before
termination. Future output hashes are recorded after execution, never filled
with guessed pre-registration values. The driver seals the full controller
tree, including raw native children and failed/partial records, into
`modal-evidence.tar.gz` plus a member manifest. The trial archive covers these
four driver outputs **and every supervisor artifact**: manifest, raw result,
evidence archive/member manifest, launch/execution receipt, literal command,
environment and stdout/stderr/check logs. Large bytes follow the existing
authorized artifact-store path; an external receipt must preserve the same
exact content identity and readback.

The driver's checker verifies transport evidence integrity only. A successful
copy is not native correctness, independent public witness/causal verification,
passing controls, qualified statistics or a scientific promotion. Use the
unchanged public verifier and analysis and the new source-B Modal exporter
after the actual run; preserve all 768 planned child outcomes and 8192 public
IDs. Export and independent review keep their usual separate scopes.

## Sources checked before implementation

The repository's `AGENTS.md`, literature-first and observation-first rules,
`coordinate`, `design-experiment`, `experiment-protocol`,
`docs/experiment-protocol.md`, `docs/confound-control.md`, official protocol
schema/checker, official preapproval/supervisor/queue/lane tools, original
builder/protocol/specification/handoffs, cohort README/source lock, and source-A
image-build/worker were read. These fix immutable records, prospective pinning,
controls, custody, count/clock separation and the actual admission boundaries.

The prior mechanism audit and literature/source pointers embedded in the
original protocol are retained; this correction asserts no mathematical
novelty or new scientific result. Relevant official Modal primary sources were
read from the retrieved 2026-10-27 source copies and retrieval hashes in
`/workspace/classical-ecdlp-endpoint-reuse/modal-route-feasibility/`: Sandbox,
Image, resources, networking/security and filesystem APIs. Those establish
the documented VM boundary, CPU units, blocked-network option and explicit
file transport, while leaving physical-host exclusivity and L2 unestablished.
The actual software-only VM probe is an operational observation, with zero
ECDLP targets; it is not a receipt for the future scientific Sandbox.

No new literature search about the endpoint-reuse mechanism was needed to
alter only the provider/transport; no novelty or transfer claim is made.
