# BATCH-bd36fe v9 control-plane provenance repair

This is a superseding, design-only repair after the independent v8 review
`TASK-20260809-19d88f` returned `REVISE`. The v4-v8 records remain immutable.
v9 does not implement ECDLP, define a frozen experiment, authorize an
Executor, execute a run, create evidence, or change research status.

## Residual findings repaired

| v8 review finding | v9 closure |
|---|---|
| Actual argv spelling was not bound | The validator compares the actual `sys.argv[0:]` spelling, before argument parsing or input loading, with the canonical accepted argv after the `python3` token. The declared self-test changes `--repo-root .` to an absolute spelling and must fail; an actual absolute-root subprocess is also a required review probe. |
| v8 predecessor-root metadata was descriptive | The v9 contract and manifest carry the exact archived v8 root, validator, contract, manifest, snapshot commit/parent, and seven-artifact SHA-256 map. The validator compares every pointer with the actual `--v8-root` and verifies every predecessor byte before the v8 predecessor validator runs. |
| Accepted-case paths could escape the fixture root | Each accepted-case path must be non-absolute, traversal-free, exactly `<fixture_id>.json`, and resolve directly beneath the canonical v6 fixture root. The strict mutation changes a canonical path to an absolute path and must fail before file loading. |

## Predecessor and execution boundary

The v9 validator first runs the exact archived v8 fixture-only validator. The
v8 validator in turn runs the v7 and v6 predecessor suites. v9 then checks the
actual invocation, exact v8 predecessor paths and bytes, case authority, v9
metadata, source bindings, and the inherited 400-arm binding. It applies four
v9 in-memory strict mutations: actual argv spelling, manifest predecessor-root
relabelling, contract predecessor-root relabelling, and absolute accepted-case
path escape. All must fail.

The package is a synthetic control fixture. A successful `VALIDATION_PASS`
means only that the declared predecessor suite and v9 provenance mutations
behave as declared. It is not an ECDLP observation, performance result,
security claim, asymptotic result, cryptographic-scale validation, experiment
specification, approval, Executor admission, run, evidence, or status
transition. A fresh independent `review-adversarial` freeze review of the
archived v9 bytes is required before any specification gate.

## Claim ceiling

The only supported interpretation of this package, if its validator and
independent review pass, is that the named synthetic control and provenance
checks reject the tested mutations. It does not show that any mathematical
mechanism works, that an ECDLP avenue is promising, or that a future experiment
is approved or runnable.
