# Implementation Contract V5

## Status

Status: `review_required`.

No source writing, importing, compiling, testing, child invocation, registered
seed access, canonical execution, or experiment run is authorized.

## Normative composition

The V5 source-design review surface is:

1. protocol v6 (`contract.md`, `specification.json`, and
   `protocol-consistency-v6.json`);
2. implementation contracts V3-V5 and source schemas V3-V5;
3. `source-authorization-amendment-v5.json`;
4. derivation, control, process-accounting, and mutation manifests through
   mutation amendment V5;
5. implementation-design consistency receipts through V5.

V5 is a narrow amendment and takes precedence over conflicting source-stage
statements. Exact bytes are bound by the V5 consistency receipt.

## Closed V5 semantics

- The specification's zero-run implementation rule is amended only through a
  separate Coordinator transition. Reviewer GO is advisory, not authorization.
- Canonical values have exact JSON types, literals, ranges, encodings, and
  digest preimages.
- Stream, fixture, compiler, cell, attempt, verification, missing-cause, and
  decision records have explicit foreign-key and recomputation rules.
- Compiler index zero is the candidate; indices 1-31 are hash controls 0-30.
- Complete cells require fourteen literal-true checks bound to an independent
  verifier receipt.
- Six controls must pass and all 65 mutations must be rejected.
- Partial artifacts require a nonempty derivation prefix and a charged,
  resolvable cause for every missing cell.
- The verifier may have no repository-local transitive dependency. A fourth,
  non-executing auditor source performs path, origin, AST, loaded-module,
  opened-path, and normalized-function checks.
- Counter vectors are nested closed objects with exactly 121 qualified work
  leaves. Child and supervisor failure vectors are total and deterministic.
- Supervisor process ceilings, campaign limits, half-open intervals, peak
  metrics, and additive metrics are distinct.

## Authority transition

After three fresh exact-commit `GO` recommendations, the Coordinator may create
one closed `AUTHORIZE_SOURCE_ONLY` decision. That decision may authorize writing
only:

- `src/sgcp_secant_producer.py`;
- `src/sgcp_secant_optimizer_worker.py`;
- `src/verify_sgcp_secant.py`;
- `src/audit_sgcp_secant_independence.py`;
- `tests/test_sgcp_secant_source.py`.

It does not authorize importing, compiling, executing, or testing those files.
A later exact-source review is required before any such action. Registered
execution remains `maximum_runs=0`; D01-D13 remain unauthorized.

## Claim boundary

This is source-protocol engineering for a toy, model-bound structural
hypothesis. It provides no relation-generation result, no rank result, no
target descent, no exponent estimate, and no rho comparison.

## Next concrete action

Validate and commit the V5 design, then obtain fresh exact-commit theory,
accounting, and red-team review.
