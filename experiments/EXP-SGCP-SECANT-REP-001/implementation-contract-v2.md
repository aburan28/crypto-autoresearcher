# Implementation Contract V2

## Status and composition

Status: `review_required`.

This contract incorporates `implementation-contract-v1.md` except where this
file or one of the v2 manifests is more specific. It closes the v1 theory and
accounting blockers. It does not authorize source implementation, development
execution, launch-plan design, registered seeds, or experiment execution.

The exact v2 design surface is:

- `implementation-contract-v1.md`;
- this file;
- `derivation-manifest-v2.json`;
- `control-manifest-v1.json`;
- `control-amendment-v2.json`;
- `mutation-manifest-v1.json`;
- `mutation-amendment-v2.json`;
- `accounting-schema-v1.json`;
- `process-accounting-v2.json`;
- `result-schema-v2.json`.

Unknown or conflicting requirements fail closed. V2 takes precedence over v1.

## Replacement derivation

The disabled inherited generated-curve and factor-base functions are not reused.
`derivation-manifest-v2.json` is the complete replacement derivation.

The producer and verifier separately implement that manifest. They may share
the manifest bytes, not Python logic. No generated transcript is valid unless
both implementations produce byte-identical attempt records and the exact
acceptance decision.

The pinned inherited producer may still be hash-checked and loaded for Curve
arithmetic, formal evaluation, graph construction, model metrics, pair-output
construction, and the optimizer. Its disabled sampling functions must never be
called.

## Closed document semantics

`result-schema-v2.json` is the closed record dictionary. Every object rejects
unknown keys. Exact types are checked recursively before arithmetic work.

The only `claim_status` value is:

```text
["HYPOTHESIS","MODEL-BOUND","TOY-EVIDENCE","NOVELTY-UNVERIFIED"]
```

The only terminal values are:

```text
INVALID
INCONCLUSIVE
SCOPED_NEGATIVE_VACUOUS
PASS_PROMOTE
SCOPED_NEGATIVE_CHART
SCOPED_NEGATIVE_MECHANISM
SCOPED_NEGATIVE_NO_SIGNAL
DEVELOPMENT_CONTROL_ONLY
```

Development controls require `DEVELOPMENT_CONTROL_ONLY`,
`scope=development_control`, `evidence_eligible=false`,
`breakthrough_claim=false`, `ecdlp_solved=false`, and
`rho_comparison=not_applicable`.

## Controls

`control-amendment-v2.json` adds:

- the exact `EXP-SGCP-EMBED-001` regression artifact hashes and objective rows;
- reverse and SHA-256 source-label permutation receipts;
- complete five-field synthetic objective vectors for the strict-rank positive
  control.

The synthetic positive tests derivation, strict-rank, and decision plumbing. It
is not an observed EC embedding advantage. The inherited regression tests the
unchanged optimizer/formal baseline only. Neither is hypothesis evidence.

## Process and accounting

`process-accounting-v2.json` freezes:

- the 10,416-child canonical process DAG;
- all 13 development child identities;
- zero-descendant development controls;
- attempt and optimizer conservation equations;
- parent-owned failure telemetry;
- observed and conservatively charged failed work;
- exact macOS RSS, disk I/O, and storage methods.

All canonical children are direct children of one future supervisor. The
supervisor is not included in the 10,416-child count but reports its own
resources separately. A child may not spawn descendants.

On abnormal termination, observed counters are lower bounds. Charged counters
use the full frozen per-attempt operation, node, wall, RSS, I/O, and storage
ceilings, so failed work cannot be undercharged. Observed and charged columns
are never combined.

## Source implementation boundary

If a later exact-commit review returns `GO`, source implementation may create
only the four paths frozen in v1. It must implement all v2 schemas and fail
closed where a platform measurement is unavailable.

No development child may run until a later post-implementation review freezes
source hashes, dependency closure, static tests, commands, and resource
containment. `maximum_runs=0` remains unchanged.

## Next concrete action

Hash-bind the v2 surface and obtain fresh theory, accounting, and red-team
reviews for source implementation only.
