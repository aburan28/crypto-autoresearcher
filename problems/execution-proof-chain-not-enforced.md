# Prescribed execution is not yet enforced through the proof chain

- **Status:** open
- **Kind:** implementation gap; proving-cost uncertainty
- **Affected work:** [Cairn integration](../docs/cairn-integration-plan.md),
  [required execution-proof chain](../docs/execution-proof-chain.md), and the
  [fabricated-measurement threat](../docs/subversion-resistance-20261010.md)
- **Next action owner:** Coordinator for the implementation handoff; Executor
  for the scoped backend/bridge work; independent Validator/Reviewer for release
- **Last updated:** 2026-10-16 (runbook seam added; still open)

## Problem

We cannot yet establish prescribed-computation integrity end to end because
no execution-proof backend connects the frozen experiment to the raw results,
metric checks, evidence promotion and Cairn settlement/audit.

The adversary controls the executor and its result artifacts. A deterministic
driver can fabricate counts, and a checker that only recalculates summaries
does not establish their provenance. The existing solution certificates check
their algebraic witnesses; Cairn's orbit certificate does not establish that
its endpoint came from the prescribed branch rule. The owner requires the
execution proof to be an integral link, with no silent downgrade.

## Evidence and uncertainty

- **Observed in source:** `tools/experiment_execution.py` captures frozen
  source/plan hashes and output receipts; it does not verify an execution
  proof. `tools/cairn_bridge.py` rechecks discrete-log/decomposition witnesses.
  `tools/exp_to_objective.py` renders the existing certificate/replay paths.
  The current Cairn registry has no execution-proof verifier. These statements
  describe inspected source, not a run or a deployed-node assessment.
- **Source baseline:** crypto-autoresearcher
  `1d5f6552e3b24c8257896bbc222b0c4ad664ec2a`; Cairn
  `4b8cafbd0e94abf87ebaf72828e907e05b007b85`.
- **Derived or proved:** no end-to-end prescribed-execution guarantee is
  established by the existing hashes or endpoint certificate alone.
- **Suspected explanation:** no unknown runtime fault is asserted; the
  required cryptographic path has not been implemented.
- **Missing capability:** versioned execution statement and schemas, real
  proof-producing guest, bounded independent receipt verification, complete
  coverage checks, result binding and all downstream enforcement.
- **Limits:** proving economics on the actual arithmetic workloads are not
  measured. This gap says nothing about ECDLP hardness or any hypothesis.
- **Added 2026-10-16, runbook seam (`docs/runbook-execution.md`):**
  `tools/runbook.py` now binds the statement components a guest journal must
  commit to (runbook, plan and source digests, the frozen argv with its seeds,
  and a per-unit statement), and an `execution_proof` step verifies each unit's
  receipt with a verifier pinned by digest. It requires `dev_mode: false`, the
  pinned image id, the receipt digest, and a journal committing to the unit's
  raw-result bytes. It refuses `RISC0_DEV_MODE`, unpinned verifiers, a wrong
  image and a wrong result (`tests/test_runbook.py`, against a fake verifier).
  Nonce-sampled replay audits now bound fabrication at a stated miss
  probability. None of this is an execution proof, and no item below is
  checked by it: there is still no guest and no real verifier. In the Claude
  Code cloud container the RISC Zero toolchain could not be installed (GitHub
  release downloads refused by the network proxy; a guest build exceeds the
  session disk allowance). That is an access limit of that environment, not
  of the design.

## What would unblock it

- [ ] Freeze cross-language statement/journal vectors that bind the approved
  protocol, executable, complete input/seed/coverage and raw output.
- [ ] Produce real non-development proofs for the small prescribed orbit walk
  and complete seeded count pilot, with independent arithmetic agreement.
- [ ] Reject the endpoint-valid alternative walk and all substitution,
  omission, incomplete aggregation and fake-receipt controls.
- [ ] Both Cairn implementations independently audit a settled pilot log
  offline, with every required proof byte available.
- [ ] Every covered run/reconciliation/bridge/evidence/progress-fidelity/archive
  path refuses missing or mismatched proof; valid execution with failed
  controls still cannot release dependent inference.
- [ ] Publish the scoped cost/adversarial report and independently review the
  exact release before enabling newly funded proof-required objectives.

These are necessary integration gates. Passing them establishes the declared
execution relation at the tested scale under the named proof assumptions; it
does not establish external-input truth, elapsed time, novelty, general
hardness, scientific interpretation or production-scale economics.

## Next discriminating step

- **Action:** prepare the first implementation handoff from milestones 1-2 in
  [the execution-proof contract](../docs/execution-proof-chain.md).
- **Inputs and controls:** the existing Cairn `ecc2k-23` job, its prescribed
  walker and independent arithmetic, an endpoint-valid alternative walk, and
  a complete seeded count workload including zero-hit/failed-control cells.
- **Execution limits and stop condition:** freeze the exact geometric workload
  ladder, resources, required artifacts and correctness targets in that
  handoff before measurement; do not infer a campaign spending cap here.
- **Outcomes:** valid proofs and failed forgery controls advance to the node
  and research bridge; a correctness disagreement blocks that release;
  excessive cost changes backend/workload strategy without weakening the
  proof requirement; infrastructure failure stays unverified and is retained.
- **Recheck trigger:** committed implementation and actual proof artifacts,
  a changed backend/advisory, or a measured feasibility result.

## Resolution and history

Unresolved. On 2026-10-16 the owner's requirement was incorporated into both
repositories' proof-chain plans and release gates. Neither this record nor
merging the documentation supplies the missing implementation or proves a
research result.
