## Handoff: SGCP V9 exact-commit red-team review

### Claim or task

Adversarially test whether exact commit
`224189ce2acc054c4e319597940f34bb0edee619` is ready for design of a separate
hash-complete launch plan.

### Status

`NEGATIVE RESULT`; decision `REVISE` before launch-plan design. This grants no
execution authority. `maximum_runs=0` remains binding, with no generated row,
matrix, runner, plan, or run authorized.

### Assumptions

- Exact committed blobs were reviewed read-only.
- Direct Python imports are in the adversarial API model.
- Reflective mutation of Python globals is outside the attack model except as
  bounded fault-injection instrumentation.
- Frozen B4 and external-resource claim boundaries remain unchanged.

### Evidence so far

Finding:

1. `MEDIUM`: the direct-producer boundary remains bypassable through public
   `build_legacy_row`. V9 gates `generated_curve` and exact-association-checks
   `build_density_row`, but `build_legacy_row` enters factor-base, expansion,
   graph, pair-output, optimizer, and retained-model work without a frozen or
   zero-budget guard. Existing focused controls call it for B4/B6/B8, while the
   V9 producer-gate test covers only the other two callables.

A direct importer can instantiate a non-frozen curve using public `Curve` and
`enumerate_points` and pass it to `build_legacy_row` without reflective
mutation. A bounded probe confirmed that the association reaches
`factor_base` instead of failing at the producer boundary.

This cannot create accepted V9 evidence because the legacy result lacks the V9
density schema and path verification rejects unregistered associations. It is
an unauthorized row-work capability that a future launcher could inherit.

The V9 statement that generated controls remain private and factor-base-only is
therefore too broad. V9 gates the current generated-curve and density-row entry
points but not the legacy row-production pipeline.

Independent controls also established:

- All nine V9 test-log hashes match the exact commit blobs.
- The exact-blob focused suite passes 58/58.
- V1-V8 schema labels reject with zero row and graph work.
- A V8 protocol under the V9 schema rejects before row work.
- An 8,388,609-character invalid-budget path returns a bounded 2,166-byte
  invalid receipt.
- No generated density row, matrix, runner, plan, or run was created.

No other medium-or-higher false-valid, path-amplification, phase-suppression,
schema-downgrade, or stale-identity defect was found.

### Failure modes

- A future launcher could call the public legacy builder and consume
  unauthorized row work.
- B6/B8 secondary fields remain replay confirmations, not standalone complete
  five-field proofs.
- Canonical feasibility, output size, CPU, RSS, parser/allocator behavior,
  cache occupancy, I/O, and bandwidth remain unmeasured.
- The verifier source digest remains diagnostic, not executed-commit attestation.
- No relation generation, rank, linear algebra, descent, preprocessing
  crossover, rho improvement, exponent, or ECDLP result is established.

### Next concrete action

Prepare one no-run V10 repair that disables or exact-association-gates
`build_legacy_row` before `factor_base`, and add one parameterized control
proving every row-producing callable rejects a concrete non-frozen association
before row mathematics; retain `maximum_runs=0` and request fresh review.

### Artifact paths

- `git:224189ce2acc054c4e319597940f34bb0edee619`
- `experiments/EXP-SGCP-EMBED-002/contract.md`
- `experiments/EXP-SGCP-EMBED-002/development-test-log-v9.md`
- `experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py`
- `tests/test_sgcp_embed_family.py`
