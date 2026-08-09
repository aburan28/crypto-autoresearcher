# Formal Research Lane: Lean-backed machine verification

**Status:** Initial implementation + advisory frontier integration

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
                                  |
                                  +--> proof-gap diagnosis --> successor frontier candidates
```

The formal worker never writes authoritative state. It returns a `FormalProofResult` that must pass both machine verification and semantic-fidelity review.

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

Implemented in this phase:

1. deterministic route features for all four formal task kinds;
2. typed successor contracts for formal frontier work;
3. translation of formal results into existing `VerificationOutcome` contracts;
4. semantic-review gating for machine-verified proofs;
5. distinct handling of blocked, refuted, invalid, and verified outcomes;
6. deterministic successor proposal generation from proof failures and successes.

Still reserved for the canonical controller:

1. admission of proposals into the durable ranked frontier;
2. dispatch to a formal-capable worker after KB retrieval;
3. archival of theorem source, build/audit logs, toolchain/manifest hashes, and source commit;
4. invocation and identity enforcement for an independent semantic reviewer;
5. promotion of reviewed proof evidence into claim/ledger state;
6. indexing theorem metadata and proof status in the KB.

## Suggested proof artifact schema

```yaml
schema: crypto.autoresearch.formal_proof.v1
proof_id: FP-ECDLP-00017
claim_id: CL-ECDLP-0041
hypothesis_ids: [H-ECDLP-017]
system: lean4
theorem:
  file: CryptoResearch/ECDLP/GenericLowerBound.lean
  name: CryptoResearch.ECDLP.genericLowerBound
verification:
  build: PASS
  axiom_audit: PASS
  forbidden_constructs: []
semantic_review:
  required: true
  status: pending
provenance:
  source_commit: "..."
  lean_toolchain_sha256: "..."
  lake_manifest_sha256: "..."
```

## Security and reproducibility

Production execution should run the worker in a network-disabled, resource-bounded container with a pinned Lean toolchain and dependency manifest. The Python worker and integration bridge deliberately contain no ledger or Coordinator mutation API. Compilation is evidence of formal validity, not scientific importance or semantic fidelity.

## Scope

The stacked formal-lane PR establishes the Lean worker and contracts. This integration phase connects formal outcomes to Research Loop v2's existing advisory routing and verification contracts, while leaving durable frontier mutation and official state transitions solely to the canonical Coordinator.
