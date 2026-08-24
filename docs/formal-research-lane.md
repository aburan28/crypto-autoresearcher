# Formal Research Lane: Lean-backed machine verification

**Status:** Producer + verifier wired; advisory frontier integration

The producer half — turning a claim into candidate Lean with the MathCode
engine — is documented in `docs/mathcode-integration.md`. This file covers the
lane's contracts; that one covers installing and driving the engine.

## Purpose

Add a formal-methods lane to Research Loop v2 so important mathematical claims can be promoted from model-generated reasoning to machine-checkable evidence without weakening Coordinator authority or independent review.

The design follows the verification discipline demonstrated by `Mira-acc/cvp`: pin a reproducible Lean environment, keep executable theorem sources, run a separate axiom audit, and treat the generated proof artifact as inspectable evidence.

## Architecture

```text
hypothesis / claim
       |
       +--> experiment worker ----+
       |                          |
       +--> formal proof worker --+--> independent review --> Coordinator --> ledger / KB
                    |             |
                    |             +--> proof-gap diagnosis --> successor frontier candidates
                    |
                    +-- MathCodeFormalizer (produce candidate Lean, untrusted)
                    +-- pre-stage scan     (unfinished/smuggled candidates never enter the workspace)
                    +-- LeanWorker         (lake build + axiom audit: the only machine evidence)
```

The formal worker never writes authoritative state. It returns a `FormalProofResult` that must pass both machine verification and semantic-fidelity review.

`orchestration.formal.pipeline.formalize_and_verify` is the whole join: generate, screen, verify. `orchestration.formal.cli` (`autoresearch formal`) runs one task from the shell and prints the proof artifact.

A task is frozen as a `crypto.autoresearch.formal_task.v1` spec under `formal/targets/`, which both the CLI (`--task-file`) and `tools/formal_task.py` consume — so what the Coordinator queues and what the executor runs are the same text. A formal task is an ordinary `executor` stanza in the existing dispatch queue: it needs no new role, and giving it one would hand the lane authority it does not have.

## Frontier task kinds

- `formalize_claim`: encode a human claim as a precise theorem statement and attempt a proof.
- `find_proof_gap`: formalize until the smallest unresolved lemma is isolated; turn that lemma into successor work.
- `formal_counterexample`: attempt to refute a proposed intermediate statement or produce a finite counterexample artifact.
- `proof_generalization`: lift a benchmark-specific theorem toward a structural statement and expose newly required assumptions.

`orchestration.formal.integration` maps these task kinds into deterministic Research Loop route features and typed `SuccessorContract` requirements. The bridge is advisory only: it cannot admit, dispatch, archive, or transition a campaign.

## Evidence states

- `machine_verified`: Lean build and axiom audit passed, with no forbidden constructs. This still requires semantic review.
- `formalization_blocked`: proof or audit failed; the blocking lemma/reason seeds typed successor candidates.
- `formally_refuted`: checked contradictory evidence; it requires independent review before the claim is refined or rejected.
- `invalid`: the proof source used forbidden constructs or otherwise violated the formal lane contract.

## Generation contract

`MathCodeFormalizer` invokes the MathCode engine once, under a wall-clock
budget, in a per-attempt directory *outside* the Lean workspace, and screens the
result before staging it:

- only the file declaring the requested theorem is considered; output that
  answers a different question is rejected rather than staged;
- a candidate whose only forbidden constructs are `sorry`/`admit` is an
  incomplete formalization — held back, its open obligations reported as
  `sorry:<line>`, outcome `formalization_blocked`;
- a candidate declaring a custom `axiom` or `unsafe` is `invalid`;
- a missing engine, timeout, non-zero exit, or empty output yields **no**
  `FormalProofResult` — it is an infrastructure failure, and rule 3 forbids
  reading it as evidence about the claim.

Staging is gated because `LeanWorker` scans the *whole* workspace: an unfinished
candidate left in `formal/` would mark every later task in that workspace
`INVALID`.

## Verification contract

`LeanWorker` checks a repository-local workspace, scans Lean files for `sorry`, `admit`, custom `axiom`, and `unsafe`, runs `lake build`, then runs `lake env lean AxiomAudit.lean`.

A successful result sets `needs_semantic_review=true`. `verification_outcome_from_formal_result` therefore reports a mechanically successful proof as `INCONCLUSIVE` until a separate reviewer confirms semantic fidelity. The reviewer must compare the Lean proposition with the original `claim` and reject vacuous statements, weakened quantifiers, hidden assumptions, or claims proved only from impossible premises.

A valid `formally_refuted` result is not classified as infrastructure or verifier failure. It is recorded as contradictory evidence requiring review, preserving the Research Loop v2 invariant that scientific falsification and broken execution are distinct outcomes.

## Successor generation

`successors_from_formal_result` deterministically converts formal outcomes into advisory successor candidates:

- `formalization_blocked` -> isolate the proof obligation, attempt a formal counterexample, and weaken/refine the claim;
- `formally_refuted` -> refine the hypothesis and characterize the boundary where a restricted theorem may survive;
- `machine_verified` -> perform semantic-fidelity review and attempt proof generalization;
- `invalid` -> repair/reproduce the formal attempt before drawing research conclusions.

The task/result IDs must match before successors are generated. A worker completion therefore cannot silently terminate a campaign simply because a proof attempt stopped.

## Coordinator integration

Implemented:

0. a formalization producer (MathCode) feeding the verifier, with provenance;
1. deterministic route features for all four formal task kinds;
2. typed successor contracts for formal frontier work;
3. translation of formal results into existing `VerificationOutcome` contracts;
4. semantic-review gating for machine-verified proofs;
5. distinct handling of blocked, refuted, invalid, and verified outcomes;
6. deterministic successor proposal generation from proof failures and successes.

Still reserved for the canonical controller:

1. admission of proposals into the durable ranked frontier;
2. dispatch to a formal-capable worker after KB retrieval;
3. archival of the emitted proof artifact — theorem source, build/audit logs, toolchain/manifest hashes, and source commit;
4. invocation and identity enforcement for an independent semantic reviewer;
5. promotion of reviewed proof evidence into claim/ledger state;
6. indexing theorem metadata and proof status in the KB.

## Proof artifact schema

Emitted by `FormalRunRecord.as_proof_artifact`; printed by
`autoresearch formal formalize`. Fields that could not be computed are `null`,
never a placeholder.

```yaml
schema: crypto.autoresearch.formal_proof.v1
proof_id: FP-ECDLP-00017
claim_id: CL-ECDLP-0041
hypothesis_ids: [H-ECDLP-017]
system: lean4
task:
  task_id: TASK-20260817-a1b2c3
  kind: formalize_claim
  claim: "..."                     # the human claim the theorem must capture
  workspace: formal
theorem:
  file: CryptoResearch/ECDLP/GenericLowerBound.lean
  name: CryptoResearch.ECDLP.genericLowerBound
formalizer:                        # who wrote the Lean, and from what
  schema: crypto.autoresearch.formalization_attempt.v1
  engine: mathcode
  engine_version: "..."            # null if the engine reports none
  engine_env: {MATHCODE_LEAN_REPL: "1", ...}
  staged: true
  prompt_sha256: "..."
  source_sha256: "..."
  attempt_dir: .formal-attempts/TASK-20260817-a1b2c3
  unproved_sites: []               # e.g. ["sorry:42"] on a blocked attempt
  exit_code: 0
  duration_seconds: 611.2
  failure: null
  infrastructure_failure: false
verification:
  status: machine_verified
  build: PASS
  axiom_audit: PASS
  forbidden_constructs: []
  blocking_reason: null
  infrastructure_failure: false
semantic_review:
  required: true
  status: pending
provenance:
  source_commit: "..."
  lean_toolchain_sha256: "..."
  lake_manifest_sha256: "..."
```

## Security and reproducibility

Production execution should run the *verifier* in a network-disabled, resource-bounded container with a pinned Lean toolchain and dependency manifest. The generator cannot be network-disabled — it calls an inference backend — which is one more reason the evidence is the verification and not the generation. The Python worker and integration bridge deliberately contain no ledger or Coordinator mutation API. Compilation is evidence of formal validity, not scientific importance or semantic fidelity.

## Scope

The stacked formal-lane PR establishes the Lean worker and contracts. This integration phase connects formal outcomes to Research Loop v2's existing advisory routing and verification contracts, and attaches a producer so a task can start from a claim rather than from hand-written Lean, while leaving durable frontier mutation and official state transitions solely to the canonical Coordinator.
