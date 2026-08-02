# Handoff: EXP-SGCP-SECANT-REP-001 V4 accounting review

## Claim or task

Audit exact commit `c05dabbf4cddae8e196448de174e6daab7eba0d7`
for source-stage accounting and artifact closure.

## Status

`OPEN` - **REVISE**

No source implementation or execution is authorized.

## Assumptions

- V4 overrides conflicting V3 statements.
- Registered execution and all thirteen development children remain locked.
- This was a read-only static audit.

## Evidence so far

- Commit, tree, and every consistency-receipt hash matched.
- Mutation closure was exactly `24+12+8+8=52`.
- The distinction between development children and registered runs passed.

## Failure modes

1. V3 requires a flat counter vector while V4 requires qualified paths, but the
   serialized 121-path representation is not fixed.
2. Failure charging is not a total role-by-field function.
3. Supervisor ceilings have ambiguous process/campaign scope and no overhead.
4. Start-before-end tie ordering can report concurrency two for serial work.
5. Verification values, fixture completeness, and attempt foreign keys are not
   closed.
6. The independent-audit receipt has no retained path or whole-receipt binding;
   V4 contract and consistency hashes are absent from result bindings.

## Next concrete action

Define a nested counter vector, total failure-charge map, half-open intervals,
referential closure, and retained whole-receipt audit binding in V5.

## Artifact paths

- `experiments/EXP-SGCP-SECANT-REP-001/source-schema-v3.json`
- `experiments/EXP-SGCP-SECANT-REP-001/source-schema-v4.json`
- `experiments/EXP-SGCP-SECANT-REP-001/process-accounting-v2.json`
