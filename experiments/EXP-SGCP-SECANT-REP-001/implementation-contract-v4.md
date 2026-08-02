# Implementation Contract V4

## Status

Status: `review_required`.

No source implementation or execution is authorized.

## Normative composition

The source-stage contract is:

1. `implementation-contract-v3.md`;
2. `source-schema-v3.json`;
3. `source-schema-v4.json`;
4. `derivation-manifest-v2.json` narrowed by
   `derivation-amendment-v3.json`;
5. the control and mutation manifests through mutation amendment V4.

V4 files take precedence. Every incorporated file is hash-bound by the V4
consistency receipt.

## Closed V4 repairs

- Canonical complete and partial payloads are closed tagged unions.
- Completed cells contain the fourteen required embedding checks.
- The full mutation surface is result-bound.
- All six controls are mandatory in exact order.
- Attempt-cap exhaustion exists only at stream level.
- Verifier dependencies, AST imports, and loaded modules are audited.
- Fully qualified counter paths prevent optimizer/verifier aliases.
- Additive, peak, concurrency, and failure-charge equations are distinct.
- Development children and registered experiment runs are separate budgets.

## Authority

The current source authority remains `CONTROLS_ONLY_ZERO_RUN_V3`.
`maximum_runs=0`; registered seeds and canonical mode are rejected before
argument parsing. A source-implementation `GO` would authorize writing source
and focused static tests only. It would not authorize D01-D13 or any experiment
run.

## Next concrete action

Obtain fresh exact-commit theory, accounting, and red-team review for source
implementation only.
