# Formal Research Lane: Lean-backed machine verification

**Status:** Initial implementation

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
                                  +--> proof-gap diagnosis --> successor frontier nodes
```

The formal worker never writes authoritative state. It returns a `FormalProofResult` that must pass both machine verification and semantic-fidelity review.

## New frontier task kinds

- `formalize_claim`: encode a human claim as a precise theorem statement and attempt a proof.
- `find_proof_gap`: formalize until the smallest unresolved lemma is isolated; turn that lemma into successor work.
- `formal_counterexample`: attempt to refute a proposed intermediate statement or produce a finite counterexample artifact.
- `proof_generalization`: lift a benchmark-specific theorem toward a structural statement and expose newly required assumptions.

## Evidence states

- `machine_verified`: Lean build and axiom audit passed, with no forbidden constructs. This still requires semantic review.
- `formalization_blocked`: proof or audit failed; the blocking lemma/reason should seed successor tasks.
- `formally_refuted`: reserved for a future counterexample adapter that emits a checked refutation artifact.
- `invalid`: the proof source used forbidden constructs or otherwise violated the formal lane contract.

## Verification contract

`LeanWorker` checks a repository-local workspace, scans Lean files for `sorry`, `admit`, custom `axiom`, and `unsafe`, runs `lake build`, then runs `lake env lean AxiomAudit.lean`.

A successful result sets `needs_semantic_review=true`. A separate reviewer must compare the Lean proposition with the original `claim` and reject vacuous statements, weakened quantifiers, hidden assumptions, or claims proved only from impossible premises.

## Coordinator integration

A future controller phase should:

1. admit the four formal task kinds into `FrontierNode.kind`;
2. route them to a formal-capable worker after KB retrieval;
3. archive the immutable theorem source, build log, audit log, toolchain/manifest hashes, and source commit;
4. invoke an independent semantic reviewer;
5. only after both checks pass allow the Coordinator to attach `MACHINE_VERIFIED` evidence to the claim;
6. map blocked proofs into typed successors rather than generic task failure;
7. index theorem statements, assumptions, dependencies, axioms, claim IDs, and proof status in the KB.

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

Production execution should run the worker in a network-disabled, resource-bounded container with a pinned Lean toolchain and dependency manifest. The Python worker deliberately contains no ledger or Coordinator mutation API. Compilation is evidence of formal validity, not scientific importance or semantic fidelity.

## Initial scope

This PR establishes contracts, a bounded Lean verification worker, tests, and the workspace/documentation contract. It intentionally does not vendor CVP-specific lattice code or make Lean a mandatory dependency of the base autoresearcher install.
