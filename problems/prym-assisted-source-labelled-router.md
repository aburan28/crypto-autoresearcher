# Prym-assisted relations lack a source-labelled router

- **Status:** `open`
- **Kind:** missing construction, implementation and comparative measurement;
  a scoped prior algebraic argument is linked, not a universal obstruction
- **Affected work:** [issue #2414](https://github.com/aburan28/crypto-autoresearcher/issues/2414),
  [IDEA-20260909-4c5ee9](../ledger/proposals/IDEA-20260909-4c5ee9.yaml),
  [ECDLP-IDEA-002](../ideas/ECDLP-IDEA-002_split_jacobian_projected_smoothness_hypothesis.md),
  [the follow-up](../research/prym_relation_followup_20261019/README.md),
  RQ-ECDLP-002, GOAL-ECDLP-001 and GOAL-ICEX-001 (existing goal states unchanged;
  design-only work is recorded under BATCH-c406ea)
- **Next action owner:** Coordinator, for mechanism selection and runnable design
- **Last updated:** 2026-10-25

## Problem

The owner-requested Prym-assisted prime-field ECDLP follow-up cannot yet
establish a useful relation-generation improvement because no explicit public
source-labelled router outside the recorded fixed-branch scope, or matched
current IC baseline, is supplied.

For ordinary E/F_p, prime-order G=<P> and Q=[k]P, the intended route keeps G in
J(D) and uses auxiliary Prym constraints to locate relations. It is distinct
from direct algebraic transfer E->Prym: the latter has Frobenius-compatibility
and nonzero-image gates, while the natural anti-invariant projector kills the
conorm image. That fact does not reject auxiliary relation search.

## Evidence and uncertainty

**Completed finite census, 2026-10-25:** [EXP-ECDLP-d6d8e8](../experiments/EXP-ECDLP-d6d8e8/specification.yaml) / [RUN-ECDLP-ea49a6](../experiments/EXP-ECDLP-d6d8e8/reports/run-20261025T0327Z/report.md) executed exactly 1,867,776 descriptors. Native outputs and the independent checker passed. Sampling recorded 97 rows; exhaustive coverage recorded 4,160. The F431 ranks changed from 2/4 and 1/3 to 4/4 and 3/3. Both F4099 cases produced zero rows, rank 0 and U=7 even under complete 3,584-branch support. F101 cells have U=0 and are public calibrations. These observations describe limited sampled support and zero-row behavior on this exact finite stream. They establish no general rank obstruction or attack-cost improvement.

Canonical storage access and fresh Put/Get/hash verification succeeded through a temporary authorized process. The earlier access impediment is no longer current. Old W2 files were preserved while additional digest-tied copies were uploaded. Snapshot `a6fe1b4716daef145c710a686e411f4d84998aaa` binds all 19 logical outputs. The completed-release helper used its documented authoritative-receipt route for two compacted logical names, retaining all 19 hashes. Raw data, run seals and native receipts were preserved. See the [release/custody record](../coordination/goals/GOAL-ECDLP-001/batches/BATCH-61781b/final/release-custody-check.json).

The independent [review](../experiments/EXP-ECDLP-d6d8e8/reviews/TASK-20261025-5145ac/report.json), archived at `6042d89a68d3e89f3e3c3e9fe26fbc6238db1447`, reproduced all 4,257 source equations, 16 matrices and complete attempted support. It checked 144 principal/E2 witnesses and 11 negative controls. Its assigned arithmetic/custody findings hold within those scopes.

**Formal independence bookkeeping remains open.** The actual generic checker exits 1 on six phase-2 reads because it unions the complete read history rather than representing the predeclared sealed-then-unblind phases. Phase 1 was sealed at 03:44:38.004075Z with hash `0751c0c2771e291a363d92c99d5b16cdce27a2a340abe6080e150394b418db84`. First unblinding occurred before 03:48:10.196002Z, but its exact time was not separately captured. Exact UID serialization was checked in phase 2; remote GET and operation counters were not independently remeasured. All disclosures and the actual checker finding remain in the record. No all-gate pass, exception or scientific promotion is claimed.

**Checkable procedural exit:** test a proper prospective phase-aware validator that accepts a valid sealed-then-unblind transcript and rejects pre-seal result reads, missing read disclosures, changed seals/hashes, and false or late time controls. Resolve timing/provenance obligations before claiming formal independence or promotion. This is a workflow/provenance gap. Current PR #2560 also requires final-head CI/review; PR #2415 is merged history.

The dated prospective statements below are preserved as earlier states. The current observations supersede their execution/access status only; goal and hypothesis states remain unchanged.

**2026-10-25 prospective rank-census update:** [EXP-ECDLP-d6d8e8](../experiments/EXP-ECDLP-d6d8e8/specification.yaml) now specifies a nested comparison on eight fresh A=2 toy curves: the same public sources1..64 and eight-atom base in both arms, with64 sampled branches versus all3,584 tuple/sign branches per source. The finite end is1,867,776 attempts; full rank never stops collection. Public-anchor projection, exact rank/kernel certificates and an independent complete-stream replay are implemented. Only public fixture construction and deliberately planted software controls have run; fresh-panel relation labels have not been observed. The canonical experiment remains `review_required`, with no execution approval or new scientific run.

Required artifact publication is currently an infrastructure impediment: this managed environment reports no configured storage credentials/outbound identities, and the ordinary AWS route returned `Unable to locate credentials`. The current repository contract requires large data in `s3://setec-astronomy-artifacts` with digest manifests. Admission must bind a working writer/readback route and preserve raw-output custody before this census can run. This access failure says nothing about matrix rank or the Prym mechanism. Checkable exit: configured approved runtime identity, successful normal bucket write/readback through `tools/artifacts/artifacts.py`, digest-verified manifest custody, then exact native preapproval/approval/archive/ordinary-ready/live-claim gates. Complete weighted costs, worker isolation and blind recovery remain separate later requirements.

The native prospective-byte probe now returns `approvable:true` with no static blockers, and the Director recorded an implementation-tier route plus missing mechanical-wrapper fields. These administrative checks grant no execution authority: canonical EXP-ECDLP-d6d8e8 remains `review_required`, no approval decision exists, and no fresh scientific stream ran. Source snapshot f69f179631622d84f53ff92049c9bc6dbfd308e5 and admission-disposition snapshot e599d644b3b2f962db21112aba90129a4457453c preserve those bytes. The ordinary experiment selector correctly returns an empty list while the contract is unapproved.

The current PR also has a concrete storage migration gate: `tools/artifacts/artifacts.py check origin/main HEAD` selects the earlier immutable W2 `events.jsonl` (27,079,956 bytes) and `raw-result.json` (1,363,130 bytes). The new census package fits the policy. Existing run immutability still binds: preserve historical bytes and digests, use the canonical artifact tool and a compatible digest-custody migration, and verify both the storage and native custody checks before merge. No remote write followed the missing-credential observation. Required/applicable final-head CI and review also remain due. These are publication gates, not matrix-rank evidence.

See [admission diagnostics](../experiments/EXP-ECDLP-d6d8e8/packaging/diagnostics.json) and the [current checkpoint](../coordination/goals/GOAL-ECDLP-001/batches/BATCH-a00184/CHECKPOINT.json).

**2026-10-21 execution update:** [implementation and recorded results](../research/prym_experiment_design_20261019/implementation/README.md) now supersede the original design-only status statements below. Native G (RUN-ECDLP-dad803) and schema-only W2 (RUN-ECDLP-d25f6a, EXP-ECDLP-cded08) completed with passed independent checkers. W2 verified public source/principal-divisor witnesses but reached nontrivial full rank in only six of 24 cells; six cells were already fully public, and twelve had insufficient rank. The fixed source/tuple stream, not the entire Prym direction, is bounded by this result. No current-IC or complete-cost gain was measured.

Conditional S/E prototypes, independent census/final checkers, eight fresh S inputs and forty public E inputs now exist. Remaining impediments include the unmet rank/S-benefit gates, unavailable worker isolation (Landlock ENOSYS; bubblewrap UID map read-only), complete orbit/cost and native-package audits, current-best matched IC/complete S and reference bindings. Workers refuse without isolation; no S/E scientific trial ran. A distinct prospectively frozen constructor/repair and enforceable runtime isolation, followed by matched independent checks, are the next discriminating steps. Native approval applies only to the two completed finite audits.

- **Observed:** the existing proposal already includes residual/nonlinear
  Prym companion cancellation. The [P1546 record](../ideas/artifacts/ECDLP-IDEA-002/p1546_projected_smoothness_counting_gate.md)
  supplies a scoped bounded-branch counting argument and names compact
  growing-degree/adaptive routing as an unresolved operation. The
  [PO-transfer-003 record](../inputs/refs/experiments/ecdlp_isogeny/po_transfer_003_result.md)
  reports earlier toy relation/recovery observations. These are retrieved
  historical records, not fresh execution or an independent review here.
- **Derived or proved:** the follow-up states the standard push-pull and
  anti-invariant identities as interface constraints, not a new certified
  result. P1546's theorem labels are attributed to its frozen record. No
  universal lower bound or absence of other Prym algorithms is established.
- **Suspected explanation:** branch enumeration, duplicate projected images,
  unknown tuple-first source logs, or post-hoc kernel residuals may erase a
  proposed gain. Which applies to a future router remains to be tested.
- **Missing capability:** explicit target-local construction, independently
  checkable source witnesses, admitted fixtures/collector, frozen matched
  baseline and complete costs. These are design/implementation gaps.
- **What this evidence does not establish:** novelty, a new performance
  advantage, below-rho recovery, a weak deployed curve, or impossibility.
  The unsourced count of 32 covers and chat-only F_43 example are not native
  experiment evidence. No new scientific run is cited or authorized.

## What would unblock it

- [ ] Specify one public router/batched constructor, its representation,
  exact source-return interface, degree/genus/field costs and applicability.
  Explain its precise distinction from P1546's fixed-branch/dither scope.
- [ ] Independently check maps, exceptions, norm witnesses, order-r retention,
  unique projected columns and useful rank; prevent hidden-log/target leakage.
- [ ] Bind the current verified IC baseline and freeze a runnable controlled
  successor through existing approval, admission and archive routes.
- [ ] Measure complete S, memory and blind recovery on matched instances,
  retaining all failures, and obtain independent review. A verified reduction
  against the current IC baseline is progress; rho is a separately reported gap.

The first item unblocks design, not a performance claim. The later items are
required for empirical advancement; crossing rho is not a prerequisite for
recording an incremental improvement. No acceptance checkbox changes a
scientific status without the existing Coordinator decision.

## Next discriminating step

**Next proposed experiment, not executed here:** after the current observation review is archived and its procedural limits are treated explicitly, draft a NEW contract testing factor-base size m=8 versus m=16 on the same two p=4099, a=2 curves with constants b=13 and b=16. Preserve P/EC1 and the first eight atoms/lifts; append the next eight eligible distinct norm classes in the same lexicographic rational-point order. Freeze public scalars 1..64, source order independent of base UID, and the same cubic/residual/chart/alias law. Full `C(m,3) × 4^3` support gives 3,584 versus 35,840 branches per source. Re-enumerating both arms on two curves would prescribe a derived 5,046,272 attempts. This work has not run.

Measure the changed U, affine/augmented rank, nullity, accepted/rejected/alias counts and all setup, construction, normalization, matrix, checker and storage costs. Include old-eight-atom witness embedding and transported-encoding controls. Add no anchors, early stopping, large-prime repair or different constructor. Disclose that the m=8 zero-row outcomes motivated case selection, while m=16 acceptance labels remain unseen. The new contract must freeze inputs, controls, metrics and stopping rules before approval. Phase-aware independence/tooling acceptance remains an explicit requirement before formal promotion.

The earlier design-intake discussion below is historical context.

The immediate step is the fixed paired census above, after its publication/admission gates. Report accepted rows, U, rank modulo r and costs together. If complete support remains deficient, retain its finite nullspace and prospectively change one constructor or factor-base ingredient. These data do not decide a structural impossibility claim. The older design-intake items below remain historical context.

- **Bounded engineering tests:** the [four-stage experiment programme](../research/prym_experiment_design_20261019/README.md)
  now specifies geometry checks, public-source/rank controls, a concrete PO003
  companion-bucket selector and blind complete-cost comparison. Arithmetic and
  selector components exist; generator/canonicalizer/checker integration,
  current baseline and native execution admission remain due. This selector
  tests a fixed generator within its existing scope; it does not resolve the
  compact-router problem below.
- **Action or proof obligation:** write the concrete router interface and
  scope comparison described in [the design step](../research/prym_relation_followup_20261019/README.md#next-discriminating-design-step).
- **Inputs and controls:** the pinned existing proposal/P1546 record, direct
  elliptic and split-product controls, known-false source labels and a
  proposed frozen atom base. Actual fixtures are not yet admitted.
- **Execution limits and stop condition:** this is design intake, not a
  runnable trial. Scientific execution requires a separately complete,
  admitted protocol with samples, seeds, machine limits and stopping rules.
  No campaign spending cap or production-target run is introduced.
- **Outcomes and next actions:** a distinct explicit construction proceeds
  to runnable design; a duplicate records its exact scope and missing
  operation; a proof gap remains open; tool/access failure is infrastructure
  evidence only. Never restart IDEA-002 merely because this issue exists.
- **Recheck trigger:** a concrete router/correspondence, source-witness
  implementation, comparative baseline or relevant scoped proof update.

## Resolution and history

2026-10-19: owner-requested follow-up recorded in issue #2414 and the
machine-readable companion. Existing goals, hypotheses, protocols and queues
remain unchanged. The missing operation is unresolved; filing or merging this
record does not establish an algorithmic result.

2026-10-19 follow-up: four proposed hypotheses and review_required experiment
designs added, together with prospective arithmetic/selector components and
software checks. No scientific trial or measured advantage. Existing
scientific records were preserved; a separate design queue tracks this work.
