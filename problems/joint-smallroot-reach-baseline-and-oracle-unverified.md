# Joint small-root baseline and executable decomposition remain unverified

- **Status:** investigating
- **Kind:** historical instrument accounting discrepancy; optimized-oracle implementation and proof gaps; admission and CI gates
- **Affected work:** [small-root lead](../knowledge/leads/ecdlp/ic-prime/LEAD-ICP-coppersmith-smallroot-semaev.yaml); [audit](../research/joint_smallroot_reach_20261024/report.md); the user's reach-cost and verified prime-field IC improvement objective
- **Next action owner:** Coordinator designs a bounded finite clipped-certificate pack/checker specification for existing J-r2-mu1-joint_A; exact domain, kernel/minor, native-span and integer-index/height witnesses remain required before construction/evaluation, separate from runtime/scientific approval
- **Last updated:** 2026-10-30

## Problem

We cannot establish a verified improvement of prime-field IC from the proposed
joint small-root method because its historical numerical baseline needs
reconciliation and no independently validated optimized-shift/root-extraction
oracle has been integrated and compared with a frozen IC pipeline.

The exact diagnostic objects are integer S3 with a=2,b=3, its joint four-leaf
tree with xQ=5, and finite triangular shifts. They are not subgroup instances,
random-target trials, or complete DLP solves. The original objective remains
the complete reach-cost tradeoff and a verified improvement over the current
prime-field IC baseline; software checks alone do not meet it.

## Evidence and uncertainty

- **Observed:** the historical `--validate --m 4` command reproduces its 0.8408
  constant and passes its seven univariate calibrations. Its ten tests pass.
  The successor software tests include independent symbolic expansion, exact
  coefficient-matrix determinants, finite row-power enumeration, joint row
  construction, and root-divisibility controls. See the linked report and raw
  diagnostic files for exact revisions and commands.
- **Derived:** N triangular rows with modulus exponent sum q and column
  exponents s_i have determinant p^q times product(X_i^s_i). Divisibility p^t
  gives the determinant-level budget t*N-q. The legacy code uses q. At t=1
  for the 13-column S3 fixture these are 1 and 12 respectively. This is a
  scoped arithmetic/software finding with a completed independent mathematical
  derivation and separate parent implementation comparison, not a closure of
  any attack family.
- **Missing capability:** an applicable external optimized-shift theorem or
  implementation for the actual joint system; root extraction and its success
  measurements; random-target relation yield/rank; fully charged matched IC
  and rho measurements. The inspected external AsymptoticBounds package
  requires SageMath; its applicability to this joint system is not established
  by reading its README and two source files. The Ryan artifact page returned
  HTTP 403 in this environment; that failure is an access observation only.
- **Publication:** automatic approval review refused the GitHub push as an
  external publication without explicit authorization. No workaround was
  attempted. Local work continued. The repository's independent-dispatch
  rule requires published inputs, so the prepared blind review was not run.
  The user subsequently authorized publication; the branch is now in
  [PR #2547](https://github.com/aburan28/crypto-autoresearcher/pull/2547), and the
  prepared blind review has been dispatched. Auto-merge was separately refused
  as outside the publication authorization; the PR remains open.
- **Independent derivation:** [TASK-20261024-da3810](../research/joint_smallroot_reach_20261024/independent-review.md)
  independently derives K=tN-q, the full-box equal-beta determinant limit, and
  the exact 13-column S3 determinant. It did not inspect the producer code or
  artifacts and therefore returns inconclusive on implementation compatibility.
  The [parent addendum](../research/joint_smallroot_reach_20261024/review-20261024/report.md)
  compares the matching finite fixture and keeps this separate from a global
  implementation, optimized-shift, root-extraction or pipeline validation.
- **What this does not establish:** optimality of the tested shift families,
  impossibility of better decomposition, a validated replacement for 0.8408,
  a root-recovery rate, or an IC speedup. Equal-bound finite volume is not a
  certificate for arbitrary weighted bounds. Dense matrix entry counts are
  structural proxies; they are not actual peak memory or total solver cost.

## What would unblock it

- [x] Authorize publication of the concrete local branch and publish the snapshot.
- [x] Perform the prepared independent mathematical derivation; no scientific-state promotion is made.
- [x] Independently derive the finite determinant budget, exact fixture and LLL/norm correction.
- [ ] Reconcile the optimized joint weighted-bound normalization, applicable
  shift family, charged threshold and root-extraction assumptions.
- [ ] Produce a real optimized joint construction, and test its bounds and
  verified root recovery on planted public synthetic instances under a frozen
  executable protocol; state the lattice reduction and memory costs.
- [ ] Integrate the candidate and compare complete cold IC cost on matched
  random-target subgroup instances with a frozen verified IC baseline and the
  matched rho reference. Include misses, duplicates, rank, linear algebra,
  verification, setup, failures, and independent replay.

Meeting the accounting conditions permits a sound experiment; it does not
guarantee an improvement. The last condition is necessary to satisfy the user's
full objective. A stage gain remains scoped to that stage until end-to-end cost
moves.

## Next discriminating step

- **Action:** use the completed blind determinant derivation in TASK-20261024-da3810
  to bind a theorem-backed optimized joint shift construction to this same budget
  convention before selecting a root-recovery panel.
- **Inputs and controls:** exact t=1 S3 coefficient matrix; univariate finite
  and asymptotic controls; historical frozen outputs; three-equation candidate
  matrices; generic-support and actual-coefficient distinctions.
- **Limits:** this session computed finite union-support candidates at t=1..3
  and combinatorial total-degree counts at t=1,2,3,8,16. These are diagnostic
  scope limits, not campaign spending caps. No scientific trial was launched.
- **Outcomes:** agreement qualifies the software accounting; disagreement
  requires an additive correction before any benchmark. A feasible optimized
  construction motivates a frozen recovery test. An unavailable theorem or
  tool remains an implementation/access gap, not negative mathematical evidence.
- **Recheck trigger:** completion and verified archival of the published zero-run
  design task TASK-20261025-b7e32e; a checked applicable weighted joint shift
  construction/root-extraction implementation; owner-first shared artifact-tool
  parity and completion of current-head hosted merge checks.

## Resolution and history

2026-10-24: additive audit and candidate finite accounting prepared locally;
historical code and closure outputs retained. Independent review and the original
pipeline-improvement requirement remain unresolved.

2026-10-24 publication continuation: user authorization received; exact branch
history pushed and PR #2547 opened. Prepared independent review dispatched against
published inputs. Auto-merge remains approval-blocked; this is separate from the
mathematical and implementation obligations.

2026-10-24 review continuation: independent mathematical derivation and exact
arithmetic fixture returned. Parent source comparison is recorded separately in
the addendum. No optimized-shift certificate, joint root extraction, scientific
state transition, or verified IC improvement is established.

2026-10-25 readiness continuation: the user explicitly authorized merge, so
the previous approval impediment is resolved. Artifact-policy and draft-tier
CI defects were repaired without weakening enforcement; the artifact workflow
passes and the other applicable checks remain pending. No merge has occurred.
The [new report](../research/joint_smallroot_reach_20261024/readiness-20261025/report.md)
and [PDF](../research/joint_smallroot_reach_20261024/readiness-20261025/report-compact.pdf)
derive the weighted conditional cost model from the archived finite counts.
These three certificate regions do not meet that model's sub-rho condition;
this is not an impossibility claim about improved shifts. The pinned cuso
implementation runs its documented univariate calibration at delta*=1/3.
Its optimal-shift implementation uses Gröbner preprocessing, so bypassing all
such costs has not been established. No joint solver trial was launched.
Two host-goal lanes are already open and an independent Coordinator runtime
receipt remains unavailable in this session. Full-ledger validation reports
106 errors outside the audit's changed paths; no historical records or
validation baselines were altered. The optimized joint oracle and matched
complete IC comparison remain the scientific gaps.
The direct authenticated Codex readiness check exits before initialization
with a read-only filesystem error, as recorded in the
[operational follow-up](../research/joint_smallroot_reach_20261024/readiness-20261025/operational-followup.md).
Two newly inherited main workflows also needed the existing draft-tier guards;
the local checker now reports zero uncovered workflows.

2026-10-25 coordination correction: the failed nested CLI did not establish
that the authenticated managed native Coordinator was unavailable. The
repository's documented native runtime alternative is now in use, with actual
model selection and authentication provenance recorded without claiming an API
catalog probe or an unrelated CLI receipt. Two open lanes also did not establish
two active workers: the inspected producer claims have completed releases.
After full history and historical blobs were fetched, targeted health reports
the old PFDR archive task ready; its earlier missing-artifact report was not
proved queue corruption. No existing lane was closed or taken over.

The new disjoint zero-run design lane BATCH-3cfef2 is registered and
TASK-20261025-b7e32e is published and claimed in
[PR #2557](https://github.com/aburan28/crypto-autoresearcher/pull/2557), under
DEC-20261025-fe4f22. It specifies the first joint workload and applicability
obligations prospectively. It does not approve a scientific trial or resolve the
optimized oracle and matched IC comparison gaps. The audit PR additionally
needs the artifact-tool fix to land in its owning `crypto` repository and mirror
consistently; the exact patch is prepared, but the owner workflow's Conductor
tool is absent here and no owner code was edited. See the
[operational correction](../coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-3cfef2/setup/additive-operational-correction.md).

2026-10-25 implementation compatibility continuation: the zero-run design and
snapshot archive are complete and verified. Completing `coordinate` is not a
permanent restriction on advancing the original goal through its implementation
workflow. The actual owner requirements are more specific: `crypto/AGENTS.md`
prohibits Python research execution and compiled wrappers that delegate to it,
and requires a Conductor task/check before code changes. The Sage/cuso adapter
preview therefore needs an explicit native implementation path, not a wrapper.
Native Singular 4.4.1 and a C++ compiler are present, but the complete shift,
polytope, echelon and normalization path has not been ported or validated.
The required Conductor check exits127 because the command is unavailable; no
owner code was edited and no ownership approval was fabricated. The
[compatibility assessment](../coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-3cfef2/setup/owner-native-implementation-gates.md)
names the source policies, exact observations, native implementation obligations
and checkable exit condition. This is an owner-workflow and implementation gap,
not a mathematical negative result or a request to reapprove the research.

2026-10-25 setup follow-up: the missing local Conductor installation is resolved.
The documented, checksum-verified release is installed, PostgreSQL17.11 and an
isolated loopback control plane are running, and the local native-directory
check returns exit0 with outcome allow. This is workspace-local readiness,
not a global reservation or scientific approval. Owner code remains unchanged.
The external publication gate has changed: Git push returns403 and the connected
GitHub tool returns404 for existing PR2557, despite the plugin being enabled.
The correction is committed locally; its publication and a new admitted
implementation handoff await restored repository access. Existing user research
and merge authorization persist. The native port, independent review, runnable
preapproval and matched complete IC improvement remain uncompleted obligations.

2026-10-26 repository transfer follow-up: connected repository discovery identifies
`isogeny-labs/crypto` and `isogeny-labs/crypto-autoresearcher`. Both remotes now
use these paths, authenticated fetch succeeds, and the PR connector reads both
PRs. PR #2557 merged into the audit branch; #2547 remains open. The two local
operational follow-up commits are preserved alongside the newer hosted changes.
Current main is merged without rewriting archived records. The earlier HTTP
observations stay historical; repository access is no longer the next-action
blocker. The owner artifact checker now contains full-object-ID handling, and
this checkout passes its current shared-code lock; full sibling byte parity is
not asserted. See the [transfer receipt](../coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-3cfef2/setup/repository-transfer-followup-20261026.json).
The next concrete step is the native implementation handoff and owner reservation.
No joint scientific calculation, root-extraction validation, or matched IC
improvement has occurred.

2026-10-26 hosted-check follow-up: push to audit PR #2547 succeeds at
`c62bcf577851492f4865ad1940e32b6ac1727938`. GitHub reports failure before job
steps begin: “The job was not started because recent account payments have
failed or your spending limit needs to be increased.” The same annotation is
present on progress-fidelity and artifact checks. Their [exact annotations](../coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-3cfef2/setup/hosted-check-followup-20261026.json)
are retained. This is a hosted account-availability gate. No billing settings,
permissions, checks or validation baselines were changed. Local focused tests
pass27/27, hygiene/artifact/local-lock checks pass, and the full ledger retains
100 unsuppressed errors outside this follow-up's changed records. Merge waits
for applicable hosted verification after account availability is restored;
native handoff preparation can continue.

2026-10-26 native-source and review continuation: published owner snapshot
`1d47988261c4d13f7a8549d70f53571163246c77` in
[crypto PR #2642](https://github.com/isogeny-labs/crypto/pull/2642) implements
the prospective C++/GMP/Singular construction. All 77 bound source blobs and
the eleven-path programme snapshot `0baa7b0901230b23dce945adc55695abd3e48249`
verify against Git. Native warnings-as-errors and sealed structural/guard-codec
checks pass. The later integrated owner library run passes 4862 tests with 0
failed and 121 inherited ignores; its separately retained earlier 18 missing
sparse-fixture failures were repaired by restoring tracked inputs unchanged.
These are software checks, not reach-cost or IC evidence.

The normalization/domain/order review is bounded to static source semantics;
full-cell executed parity is unestablished. The independent specialization/
extraction/cost review is inconclusive for theorem applicability and attack
readiness. Both reviewers read the complete 52-page Ryan primary paper, resolving
the earlier retrieval gap without resolving applicability. The actual review
independence checker fails with two retained attestation/phase-list issues;
no perfect mechanical pass or source-equivalence certificate is asserted.
See the source and review packet in
[PR #2594](https://github.com/isogeny-labs/crypto-autoresearcher/pull/2594).

All 24 symbolic-bound cases and the proposed four additional control constructions
remain unrun. The current host mounts cgroupfs read-only and cannot install
the frozen 8 GiB process-tree guard. A writable delegated cgroup host and actual
guard qualification are required; no RSS fallback or unguarded run is allowed.
Execution-proof/authoritative receipt integration, literal failure semantics,
finite-specialization/group/extraction checks and matched complete IC costs
remain unresolved. Hosted owner migrate/review and lab checks also report
account payment/spending-limit failures before starting. The active owner
ruleset lacks required-status-check rules, so auto-merge is held to preserve
the repository's stronger all-applicable-checks contract; no financial or
branch-protection setting was changed. The original goal remains active and
unfulfilled; no verified IC improvement or mathematical impossibility follows.

2026-10-26 CPU-accounting and runtime continuation: the published source-only
continuation DEC-20261026-45aec1 fixes CPU receipt units/coverage under a fresh
Executor/snapshot/Reviewer/Coordinator chain, preserving the completed queue and
checkpoint. No scientific case is authorized by it. Owner head27fca7749 currently
fails Rust library compilation in an unchanged upstream file; the exact retained
[attempt7 log](../coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-ee839d/continuations/DEC-20261026-45aec1/operations/upstream-cargo-attempt7.log) is not relabelled a pass.

The managed local Docker daemon provides a candidate route around the outer
read-only cgroup mount: an ephemeral private privileged container successfully
created a delegated subtree and wrote/read the exact8GiB child memory limit.
The ordinary container remained read-only despite a misleading test-w result.
The [runtime observation](../coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-ee839d/continuations/DEC-20261026-45aec1/operations/docker-cgroup-readiness.json)
records both outcomes. This resolves neither guard qualification nor scientific
readiness: actual stopped-child placement, full-tree cleanup, the unchanged1800s
watchdog, serial admission, OOM enforcement, failure retention, native runtime
compatibility and effective ancestor headroom remain to be tested prospectively.
No additional external host is assumed necessary until this supported local
runtime is assessed. Existing research authorization persists; there is still
no reach-cost measurement or verified IC gain.


## 2026-10-27: original guard observations and current owner validation

The original fixed qualification at owner C1
`204735c3f6f3144911df58a6ece7699c0e74d4ad` retained all five outcomes:
Q1 placement, Q2 escaped-tree cleanup and both Q5 negative cases passed their
fixture assertions; Q3 failed because generic orphan cleanup consumed the
competitor before its dedicated `wait4` receipt, leaving ECHILD; Q4 was
`infrastructure_not_started` at measured enclosing headroom 12,439,695,360
bytes, below the unchanged 12,884,901,888-byte gate. No Q4 allocator ran.
Q3 retained genuine production censoring after 1800.071693757 seconds, serial
rejection and cleanup evidence; its receipt failure is not a mathematical or
production-enforcement failure verdict. Full qualification is not established.
The [original snapshot receipt](../coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-ee839d/continuations/DEC-20261026-2a1490/archives/TASK-20261026-a3ab76/snapshot-receipt.json)
binds the five programme outputs and published C1 records.

The original T-3 lease expired after credential expiry stalled heartbeats;
a live wrapper process did not prove a live lease. The published
[not-admitted receipt](../coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-ee839d/continuations/DEC-20261026-2a1490/amendments/DEC-20261026-b83007/archives/TASK-20261026-a4dde2/repair-admission.json)
preserves that refusal. Normal daemon outage recovery later extended T-3's
lease, permitting ordinary release without declaring its work merged/done.
Fresh Conductor T-4 and programme TASK-20261026-1525ac were acquired separately;
no continuous-ownership claim bridges the earlier loss. The
[published limited successor admission](../coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-ee839d/continuations/DEC-20261026-2a1490/successors/DEC-20261026-7a93a8/archives/TASK-20261026-a4dde2/successor-admission.json)
permits the scoped helper repair, builds and one presealed native software
regression. That regression passed once, preserving old-order ECHILD and
correct-order exact-child exit status and actual usage. Source stage
`6b3ed020228586f60ab4ae56edf68fed2a853ef5`, parent60e694, is now published;
its 87 paths include the 86-member source/check manifest, with all five
external binary hashes verified. The one-pass cache-preparation admission is
published at `446773e283ba386cb19a052b0c542c08204fc3cf`. The sole advice pass
accepted all 375 sealed files, with zero exclusions/failures and every return
code zero with stable metadata. Its success did not establish enough headroom:
post-pass H was **9,264,652,288 bytes**, below the unchanged **12,884,901,888**
gate by 3,620,249,600 bytes. The limiting observed outer group had
memory.max17,179,869,184 and memory.current7,915,216,896; the empty 8 GiB worker
was excluded from that minimum. Its raw swap.max was `max`, while the observed
container parent's zero cap established effective zero swap. Hidden ancestors
remain unobserved. The empty-group probe and preparation containers exited and
were removed; no allocator or worker ran. The separately recorded Q4 follow-up
is `infrastructure_not_started`; its
[not-admitted receipt](../coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-ee839d/continuations/DEC-20261026-2a1490/successors/DEC-20261026-7a93a8/archives/TASK-20261026-a4dde2/q4-execution-admission.json)
binds 317 raw phase files. No extra advice, retry or threshold change is
authorized. The Q4 refusal is published at
`3d369f1f451e290c22b8e9d06b185f795179ebcb`. Q3's separate admission is
published at `57f3427d8019a29bd88ec6da0aa4fd366460f1bc`. Parent serial checks
recorded no remaining task-owned containers, the repaired helper hash and
then-live T-4/goal claim; the sole Q3 follow-up started at container timestamp
2026-10-27T01:03:08.619938647Z in `jsr-1525ac-q3-followup-1`. Its actual
terminal observation is now retained separately below; the earlier approximate
01:33:09 completion window was a scheduling estimate, not evidence.
Q4 success is not a Q3 prerequisite.
The 375-file inventory had excluded 23 of 398 original candidates; its
631,361,269 bytes were never a promise of reclamation or adequate headroom.

Owner integration `60e6943d31dc57ab509b37a5f62cba2f134d8b74` contains C1 and
has identical native-directory bytes before the new eight-line Q3-only helper
repair. Protected production source remains pinned to
`86ddd19f67e08160c22a0d8ba9a32a92321d18ad`. The earlier attempt7 syntax failure
belongs to an older head and is not a current-head compile result. Current
attempt8 instead failed compilation because a tracked bitop/v2 fixture was
absent from this sparse worktree; it was materialized byte-for-byte, without
changing tracked source. Attempt9 then compiled and ran the complete library
suite: **4,888 passed, 6 failed, 121 ignored**, exit101, in 1290.51 seconds of
test execution. This is a failed full run, not Rust PASS.

The six terminal failures were:

- `weighted_comparison_prices_verified_pairs_and_records_weight_identity`:
  `zero.legacy_comparison_id.is_none()` failed at `compare.rs:2448`.
- Three `hyper_ic` tests: method resolution rejected the `branches` parameter
  at `hyper_ic.rs:1126` or `:1203`.
- `fixture_records_reprice_to_their_committed_blocks`: tracked
  `tests/fixtures/ecbench/work-v1/records.jsonl` was absent at `work.rs:2067`.
- `pqc::hawk::tests::naive_forgery_fails`: verification assertion failed at
  `hawk.rs:328`.

The raw attempt9 log is retained locally as
`/workspace/smallroot-session/native-owner-current-cargo-attempt9-60e694.log`,
SHA-256 `b37a4217610b6d40aa72004ef36b170bac669545f389b6bc218f7f6c2cd38636`;
its durable raw-log publication is pending. Exact tracked work/v1 fixture
materialization restored the original fixture bytes, and its one same-binary
replay passed. Weighted comparison and all three hyperelliptic parameter
failures reproduced with exit101; the one HAWK replay passed. That single HAWK
pass does not repair or erase its original failure, and the full-suite result
remains 4,888 passed, 6 failed, 121 ignored. The six bounded replays and their
logs/hashes are recorded in local metadata
`native-owner-current-library-validation-60e694.json`, SHA-256
`4473057570356d17ab4f6f673f04630ccaf3b025b25c16c949c9a47405333d35`;
its raw/metadata durable publication is also pending. An ancillary upload
attempt through the normal configured AWS CLI failed at STS with exit255,
`Unable to locate credentials`; no credential/configuration change, alternate
identity or artifact-store bypass was attempted. The 431,104-byte full log
exceeds the64KiB data-file threshold and remains locally retained, not in
canonical durable custody. A separate18-file bounded validation package
(17members plus manifest), under owner checks
`parent-library-validation-60e694/`, has manifest SHA-256
`b782e9677ba9b7e99d99728fe04b7ba249cba216ce47d2ca0d3aa78fcd4b70ba`.
Its member hashes were independently checked. It preserves attempt8 raw/meta,
the actual attempt9 result metadata, all six replay logs/exits and the exact
2,850-byte failure excerpt beginning at full-log byte offset428254, with an
explicit `full_run_log_canonical_custody_complete:false` limitation. This
partial package is prepared for the final owner manifest; it neither replaces
the full log nor establishes Rust PASS. Recheck the normal artifact-store
credential chain when available, retaining original bytes in the meantime.
Guard raw records remain separate from this ancillary library-log limitation.
Source and test trees at
60e694 and base `8eef1252714097e0b8279c0bf55b82ed9e49943d` are identical
(`src` tree `6f82e102c66eda913a81a1e20c29a79366b0c597`, `tests` tree
`d2aa1e178ab14f5881081e2bbcb7c8ec628bdd37`); Cargo.toml/lock also have no
base-to-head changes. These parity checks support an untouched-service scope
assessment; they do not preclassify the remaining runtime failures or excuse
failed merge checks. The scoped C++ task does not authorize unrelated Rust
bug fixes. Owner AGENTS requires failures caused by the change to be repaired
and unrelated base/service failures to be reported with evidence on the PR.

Hosted owner checks at head60e694 also retain the actual
[account billing annotation](https://api.github.com/repos/isogeny-labs/crypto/check-runs/121910719417/annotations):
the job did not start because account payments failed or its spending limit
requires attention. Applicable failed checks are not a pass or an invitation
to bypass merge gates. The source stage is published with honest untouched-service failure evidence;
applicable merge checks remain unsatisfied. Subsequent guard observations still
require their separately admitted phases. All 24 scientific cases remain unrun; applicability,
extraction, complete cost and a verified improvement over a frozen current
prime-field IC baseline remain unresolved. The goal remains active.

## 2026-10-27: terminal successor observations and independent review

The sole Q3 follow-up completed once at
2026-10-27T01:33:08.853118452Z. The container, launcher, wait CLI and removal
all returned exit 0. Production watchdog time was 1,800,064,885,794 ns and
independent elapsed time was 1,800,065,709,473 ns; the supervisor retained
`censored=true` and wait status 9. The repaired helper retained the dedicated
competitor PID 7 receipt before generic cleanup: errno 0, reaped true, exit 0,
user 1,018 microseconds and system 0 microseconds, both available. Serial
admission rejected the competitor and launched no competing worker. Retained
cleanup shows the escaping child changing R to Z and cgroup populated changing
1 to 0; the owned group was removed, its lock released, and exact container
absence checked. The external 1,950-second fail-safe did not fire. These are
bounded software observations; original Q3 remains failed with ECHILD and
its original raw receipt is unchanged.

Final owner evidence is published at
`76a3e4eb67e818354da7575dad4b834467a97e5c`, parent
`608f7198db59fc431123de2c4d928e4e3466d6da`, in
[owner PR #2642](https://github.com/isogeny-labs/crypto/pull/2642).
The exact 284-path final stage contains the terminal Q3 records, current
681-member record index with seven shards, all 18 bounded Rust-package files
and the appended daily log. The protected production source remains identical
to 86ddd19f67. Historical phase manifests bind their own published commit trees;
the current index binds final appended-log bytes. No historical log hash is
asserted equal to the final appended log. The actual cached diff check exits 2
for eight retained blank-at-EOF diagnostics in two raw CPU-info and six raw
Rust replay logs; those bytes were preserved, not relabelled a clean check.

The original Q1/Q2/Q5 outcomes belong to the C1 helper; the sole Q3 follow-up
belongs to its repaired receipt-order helper. Those other classes did not rerun.
Independent TASK-20261026-5bedd5 checked the exact source/runtime/custody and
publication bindings. Its full-joint verdict is **breaks** because actual Q4
OOM enforcement is absent; narrower recorded observations hold. It supports
transfer of Q1/Q2/Q5 only to the same protected supervisor and fixture because
the sole helper change is Q3-specific after the supervisor returns. Successor
programme snapshot `c90b8b1a12bc6323ece604a965bb96bad823c166` binds all five
final outputs. The preparation-stage
publication occurred after Q3 launch; this timing is retained and is not
represented as a prelaunch publication. Separately published execution seals
and Q3 admission preceded the authorized Q3 invocation. Independent review
finds the pre-action source/admission gates hold: the later preparation archive
preserves already-completed preparation records and is not itself a prelaunch
gate.

Neither Q4 admission launched an OOM allocator. The follow-up's observed
H = 9,264,652,288 bytes remains below the unchanged 12,884,901,888-byte threshold;
the exact 8 GiB empty-cap readback does not establish OOM enforcement. Current
one-pass/no-retry authority is exhausted, so another preparation pass or Q4
attempt would need a prospective scoped admission rather than an automatic
retry. Full guard qualification remains false after review. A lawful actual
OOM qualification with sufficient measured
enclosing headroom would address this resource-enforcement gap only; theorem
applicability, scientific execution, extraction and the matched complete IC
comparison would remain separate requirements. All 24 scientific cases remain
unrun, no verified IC gain is established, and the goal stays active.

The canonical current-round independence checker exits 0 with one owned-joint
attestation, blindness respected and controls declared. This is a genuine
fresh `openai/gpt-5.6-sol`, `review-adversarial/xhigh`, `fork:none` review with
zero guard, regression, stress or scientific executions. Its source/raw review
does not claim a regression replay. Current mechanical PASS does not repair
the original mathematical round's two retained attestation/phase-list issues,
and the earlier independent CPU-only acceptance remains separate. The
[composition](../coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-ee839d/continuations/DEC-20261026-2a1490/tasks/TASK-20261026-94c1e6/report.md)
and [DEC-20261026-3380c9](../ledger/decisions/DEC-20261026-3380c9.yaml)
record partial software observations only and require root's exact isolated
ledger archive verification/publication before official effect. Its two-page
Typst PDF was rendered and every final page inspected. No scientific graph,
goal status or immutable original batch checkpoint changed.

Owner head 76a3 currently retains 16 failed checks and one skip in the root
observation. The inspected current-head
[review annotation](https://api.github.com/repos/isogeny-labs/crypto/check-runs/121956938857/annotations)
again states that account payment/spending-limit availability prevented job
start. This is separate from the failed full Rust run and its incomplete
canonical full-log custody. Applicable checks remain unsatisfied; no merge
bypass is authorized. Recheck actual OOM admission only when the stated
headroom/runtime/ownership packet exists, and recheck normal artifact-store
custody and hosted verification when their configured services are available.

The exact ten-file review/composition archive is now published at
`c0618e50c6b26758e479592b01397041f37c2c9b`, parent
`6b8d69f0504fb1d6d731ec6afa5e7526d6d99c00`. Its actual parent, exact path
set, required record IDs and all ten hashes were verified. The completed
review and composition releases report observations only; all six tasks in
this guard queue are terminal and formal dispatch reports zero ready and zero
deferred tasks. Source reservation T-4 was ordinarily released after final
owner/snapshot publication; subsequent observation shows its lease inactive
and task cancelled, with the authorized wrapper and watcher stopped. This is
an unmerged reservation release, not owner work landed/done or a goal status.
Final branch hygiene passes; full-ledger validation still reports the exact
same ordered 100 preexisting errors and no new record error. No error
suppression, failed-check bypass, new research chain or immutable checkpoint
edit occurred. Authorized software coordination is complete; the scientific
goal remains active and impeded by the requirements stated above.


## 2026-10-27 02:56 UTC: informational host-status recheck

A read-only continuation assessment at 2026-10-27T02:56:36.173000+00:00
recorded the whitelisted host/cgroup status below. It read system metadata
only: no container, helper, Docker inner probe, memory-advice pass, allocator,
qualification case or scientific case was launched. This is informational
prospective-route orientation, not a new admission, qualification attempt,
retry or rescoring of either historical Q4 row.

The measured visible cgroup has memory.max 17,179,869,184 bytes and
memory.current 7,881,801,728 bytes. Its derived finite headroom is
`17,179,869,184 - 7,881,801,728 = 9,298,067,456` bytes, below the unchanged
12,884,901,888-byte requirement by the derived 3,586,834,432 bytes. Host
MemAvailable 17,882,804,224 bytes is not the limiting recorded value. The
visible cgroup mount is read-only, its raw swap maximum is `max`, and current
swap usage and host swap totals are 0. No new inner-runtime effective swap cap
or writable delegation was measured; hidden ancestors remain unobserved.
This snapshot therefore establishes no eligible current candidate route and
confirms the present visible-headroom impediment. It does not establish OOM
behavior, invalidate the historical software observations, or provide a
mathematical negative result.

The complete whitelisted status JSON is retained inline, rather than relying
on an unpublished scratch pointer. Its source bytes have SHA-256
`4957c3b72931531a6a5bdfd10bf4c18ec7917b12e6be219e004abccfa7630223`.

```json
{
  "schema": "informational-host-status-v1",
  "recorded_at": "2026-10-27T02:56:36.173000+00:00",
  "purpose": "Read-only prospective-route orientation; not admission, qualification, retry, or rescoring of historical Q4 rows.",
  "operations": [
    "Read /proc/meminfo and own cgroup/mount mappings",
    "Read visible cgroup memory and swap status"
  ],
  "containers_helpers_allocators_advice_launched": 0,
  "host_meminfo": {
    "MemTotal_bytes": 18882674688,
    "MemAvailable_bytes": 17882804224,
    "SwapTotal_bytes": 0,
    "SwapFree_bytes": 0
  },
  "own_cgroup_mapping": "0::/",
  "visible_cgroup_mounts": [
    {
      "root": "/..",
      "mount_point": "/sys/fs/cgroup",
      "options": "ro,nosuid,nodev,noexec,relatime"
    }
  ],
  "visible_levels": [
    {
      "visible_path": "/sys/fs/cgroup",
      "raw": {
        "memory.max": "17179869184",
        "memory.current": "7881801728",
        "memory.swap.max": "max",
        "memory.swap.current": "0"
      },
      "finite_headroom_bytes": 9298067456
    }
  ],
  "informational_visible_minimum_headroom_bytes": 9298067456,
  "fixed_required_headroom_bytes": 12884901888,
  "hidden_ancestors": "unobserved",
  "execution_authorized": false
}
```

Root's concurrent read-only PR/status observation retains owner PR #2642 open
and unmerged at 76a3e4eb67e818354da7575dad4b834467a97e5c and programme PR #2594
open and unmerged at unchanged head 5fdacf2d; eight current owner workflow runs
are completed failures. No workflow rerun or merge bypass occurred in this
recheck. These workflow-run counts are separate from the earlier per-check
counts and do not relabel any failed verification as successful.

Standing Coordinator authority still permits justified prospective design;
the completed cards' one-pass/no-retry authority does not permit another
case. This below-threshold observation supplies no viable fresh executable
host route and creates no packet or execution authority. The exact existing
recheck remains a host/admission packet demonstrating measured enclosing
H at least 12,884,901,888 bytes with the unchanged 8 GiB payload/runtime and
production watchdog, serial admission, kernel-event/victim/peak/parent-
survival/cleanup receipts, and fresh maintained ownership. Recheck when that
condition changes, without automatically repeating preparation or Q4 under
the completed cards. Both Q4 rows and all completed task states remain
unchanged; all 24 scientific cases remain unrun, no IC gain is established,
and the goal remains active.


## 2026-10-29: one fresh advice pass, Q4 refused, review gate unresolved

The [partial composition](../coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-ee839d/continuations/DEC-20261029-03e304/tasks/TASK-20261029-947247/report.md), [PDF](../coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-ee839d/continuations/DEC-20261029-03e304/tasks/TASK-20261029-947247/report.pdf), and DEC-20261029-7ce9bf preserve the terminal fresh-host scope. Published prep66ea/86f4 sealed80owned files; additive source correctione946 pins observed own-PID membership in visibleinit under inherited mountroot/.., then capturesinit→visibleparent. OriginalTask30/protectedproduction bytes are unchanged. The corrected Q4 launcher is implemented/syntax-checked but unexecuted; no newOOM/runtime qualification follows.

Under published advice-only327869 authority, the sole native --advise exited0:80accepted,0excluded/failed,4,557,159,684accepted bytes. This capacity is not reclaimed-byte proof. Immediatepost raw H=min(hostMemAvailable,allfinitevisiblemax-current)=min(17,974,874,112,17,179,869,184−4,471,181,312)=**12,708,687,872bytes**, **176,214,016below** unchanged12,884,901,888. PreH8,154,775,552. The immediatepost snapshot was captured first after helper return before advised-file/library/Git rewarming; sequential snapshots have no reported uncertainty/error bars. Hidden ancestors remain unobserved. Refusal a204291 retains infrastructure_not_started/refused_Q4: **zero Q4 containers/drivers/workers/allocators/scientific calls** and no further advice/case, even if later memory changes. Raw owner0bcdc1a8 and exact programme snapshotcc367e96 retain the evidence. Outer max/swap/events/peaks are not absent-worker enforcement measurements.

The fresh [independent report](../coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-ee839d/continuations/DEC-20261029-03e304/tasks/TASK-20261029-e276d7/report.md) verified96prep/26case paths and derived the same H. Its joint verdict is **breaks for missing coverage**, with coherent bounded source/advice/refusal facts; this is not a cap stress failure or mathematical negative. The canonical independence checker nevertheless returns**exit1**: original review-plan blindness.lifted_for contains DEC3380/49e identifiers rather than validTASKowners. The current attestation joints_owned is correct. Original plan/checker/reviewer bytes and actual failure are preserved; no retrospective correction/waiver, completed-round assertion or accepted qualification is made. Reviewer initially wrote4outputs at the wrongcwd before moving exactbytes; departure retained. One pack-fa66 historicalmtime changed from1793053277390270427 to fresh1793056768668436294, causeunknown:79/80allhistoricalmetadata match, all80freshmetadata/content/seal/advice stable. Do not read old_metadata_matches as all-field historical equality.

The owner normalmerge8217 resolved the journal-only conflict preserving parent blocks; deferred log append then completed. Ownrawstage diffcheck0/artifactPASS do not erase mergedcached check128 with3inherited patchtrailing warnings/promisor503. Frozen reviewer snapshots still report pending current validation. New root17:53 terminal metadata records current8217(equalRust/Cargo0bcdc) **5261passed/0failed/123ignored/0filtered of5384,exit0,1427.58s**; this is ancillary currentlibraryPASS, not Q4qualification. Attempt1missingtrackedpencilpackage was restored exactly without source/test/workload change. Current467436Bfullraw SHA256625799c468d07e4534f9795cb4e9057d15f282dd0fb2128cb4c918495d5efc01 stays localonly/canonicalfalse; no configuredAWSCLI/runtimebinding/defaultfiles observed, no uploadattempt or accessdenial claimed. Historical12c5198/8/123 full failure plus8samebinarypasses and fullrawcustody gap remain separate from guard qualification. PriorCPU17/17 and oldQ1/Q2/repairedQ3/Q5 scopes, older mathematical independence/quorum gaps and originalQ3failure are unchanged. No goal/checkpoint/otherlane/scientificstatus changes; all24scientificcells remain0run and jointreach–cost/verifiedcompleteprimefieldICgain unknown.

**Recheck:** currentunitjob is nowterminal; after this exact negative/partial archive, rank read-only metadata of first-use currentbuildbinary/object artifacts as possibly distinct freshowned candidates from exhausted80; require exactownership/immutability/capacity/H and complete newprospectiveauthority if justified. This authorizes no newcard/seal/advice/case or oldcardretry. A largerhost is another candidate, not proved the only route. Before any future independent round, author a schema-valid plan prospectively; do not repair this round retrospectively. FutureQ4 still needs unchanged12GiBH/exact8GiBworker/16GiBparent/effectiveswap0/1800stimer and actualOOM/victim/peak/survival/cleanup plus freshownership/source/admission. The original research additionally needs applicablejointtheory/parity/extraction/random-target/fullmatchedICcomparison; no singleblockleadclosure transfers to the jointlattice.


## 2026-10-30: conditional joint layers reduce the next gap to a finite clipped packet

The [new composition](../coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-ee839d/continuations/DEC-20261030-553ef2/tasks/TASK-20261030-685c7c/report.md), [three-page PDF](../coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-ee839d/continuations/DEC-20261030-553ef2/tasks/TASK-20261030-685c7c/report.pdf) and DEC-20261030-5d1573 compose the exact producer94c29 snapshot and two fresh independent reports. This is manual/source derivation, no numerical ideal/rank/domain/lattice/crypto computation. All24scientific cells remain unrun.

For the exact three-equation Semaev object I=(F1,F2,F3), N independent formal modulus, fixed finite M and d=|M|, the supported formal module has q_N=mu*d−sum_j dim(I^j intersect span(M)). This whole-joint identity was independently rederived without newproducer access. The producer's auxiliary monic top monomials are pairwise coprime, giving global ideal-power saturation for integral specializations; adversarial review checked the product-basis proof. This does not establish clipping. Actual T_j and a common adapted B/Binverse with T_j B=[0,C_j], L_j C_j=Id, plus p-unit localization/minor data, are still missing. Conditional on that finite clipped certificate and N0=p, the complete supported integer lattice has index p^q_N; a returned sublattice may have extra integer index/height cost even when its p-local span is full. No rank, Delta, trace, native span, reach or root was evaluated.

Blind0cd7c6 is inconclusive for actual finite/growing-family applicability; adversarial4c1898 holds for the conditional manual interface. Canonical checker on original plan+both original attestations actually passes exit0. This consistency check does not prove every read/mathematical statement or erase prior exit1/oldphase issues. Current reviewer bytes are unchanged. Both filename-inventory departures are retained (no current siblingcontent reported), as is adversarial's missing-path127 before metadata writer and managedPython3.12.14 versus documented3.12.8 metadata-only use. No procedural departure is waived or relabeled full compliance.

The controls distinguish generic unit from finite unit ((N,cx),c(p)=p); global monicity from clipped base change (x+c*y clipped to span x); p-local span from real integer determinant (p versus p(p+1)); and support/x-zeros from roots/signed group relations. The quantifiers remain forall fixed(mu,M), exists finitecertificate/Delta, forall good specializations. No uniform changing-multiplicity/parameter success, useful short vectors, extraction or IC improvement follows. Ryan's Heuristics1–2, suitability/proportional specialization/strict margin/growth hypotheses and final-recovery exclusion remain explicit. PrincipalS3/S4/S5 ceilings remain principal and do not close the joint family.

**Ranked next target:** design the finite proof-of-certificate pack and independent checker specification for existing **J-r2-mu1-joint_A**, a=2,b=3,q=5, centers(11,13,17,19,23,29), original Wp weights(1000,50,50,50,50,100,100). Bind M1 as every integer point in the convex hull of0 plus the exact fixed nonzero supports, not a rawsupport/box/genericdomain. Require remainder identities/T1, nestedflag B/Binverse/tailleftinverse/rank/minor/Delta, actualnative order/trace and both span directions, then a prospectively declared prime's units/branches, actualinteger lifts/index/saturation andheight ledger. Construction/evaluation remains unapproved until a complete conformance protocol and lawful route are recorded. A pass qualifies that finite interface only; a failure identifies an exact witness/fiber condition. JOINT-UNIFORM-HEIGHT-6394ed is later or restrict to fixedpacket. Extraction/group/yield/rank/fullmatchedIC costs stay separate. No new task, run, host or retry is created by this entry.

Ancillary latest root scope: tested914f source equals published9b44297b4779f9fc77ed4737fccc04f6331d0523 in Rust/Cargo/crates/native, whole5551 result5428/0/123 exit0,1395.81s. Full486662Braw SHA f0148955bed287bc652d5291915570adf06374fb4d9390156d6132f6ba890439 remains local/canonicalfalse. T7 cancelled/unmerged normally, no jobs perroot; laterbd4 lines/journalconflict unintegrated/untested. Main.cpp postlaunch-status finding remains open; oldCPU17fixtures do not supply broaderqualification. BothPRs remain unmerged/gated, parent payment/spending-limit jobs notstarted are nottestfailures. Oldraw/guard/refusal andfailedreviewrecords stayimmutable; goal/checkpoint/otherlanes/hypotheses unchanged.
