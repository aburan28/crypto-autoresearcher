# EXP-SGCP-EMBED-002 source self-review v3

## Handoff: coordinator pre-independent audit

### Claim or task

Check whether the V3 source and tests implement the no-run amendment closely
enough to justify fresh independent review.

### Status

`OBSERVATION`, `TOY-EVIDENCE`, `MODEL-BOUND`, and `review_required`.

### Assumptions

- Review is against the hashes in `development-test-log-v3.md`.
- Dynamic evidence is restricted to abstract, provenance, factor-base, and
  frozen p=19 controls.
- This is a coordinator self-review, not independent GO.

### Evidence so far

#### Provenance and schema

- Producer and verifier use separate hash and EC implementations.
- The verifier replays all generated curve draws and all applicable rejection
  reasons, including duplicates.
- Factor-base records are closed and independently bound to row family,
  replicate, B, Mobius derivation, roots, poles, polynomial, and points.
- V3 document and row envelopes are closed. Nested public edges, source rows,
  representative rows, frontier states, graph rejections, conflicts,
  optimizers, retention, expansion, structural work, and byte receipts have
  closed key sets.
- A recursive forbidden-key scan rejects builder-visible scalar, discrete-log,
  dlog, log-table, and secret material.

#### Mathematical binding

- The representative compiler is named, emitted, hashed, and independently
  reconstructed.
- Eligible candidates, rejection first collisions, eligible universe indices,
  conflict first collisions, and graph metrics are independently reconstructed.
- Every public source-table row maps one constrained coordinate label to one
  formal source and is independently rederived.
- The public operation contains no final retained-4F by retained-4F edge by
  construction; V3 does not present this as an empirical discovery.
- All degree-expansion and energy fields are independently recounted.

#### Optimization and gate

- Objective order and bound method are frozen.
- A canonical cell must be completely exhausted, exact in primary and
  secondary objectives, and match both deterministic replay and an alternate
  depth-first primary proof.
- The producer validates exact ordered row keys, curve consistency,
  cross-seed uniqueness, and canonical node caps before constructing a
  canonical envelope.
- The verifier repeats those checks and independently computes the family gate.
- Exact median, duplicate-null policy, same fixed family-cap pair, thresholds,
  strata, and 18/24 sign denominator are literal source constants.
- Both gate implementations refuse unresolved cells before computing a result.

#### Accounting

- Each cap receives a fresh model cache.
- Emitted structural counts are deterministic and independently reconstructible.
- Operation totals, retained-object size, and peak-memory labels were removed
  from V3 rows.
- Canonical-JSON byte measures are recomputed exactly and labeled nested and
  nonadditive.
- Row and cap wall times are only checked for finite nonnegative nesting.

### Failure modes

1. The alternate depth-first proof shares the same factor-base, candidate, and
   constrained-count mathematical model; it is algorithmically distinct but
   not an independent formal proof of that model.
2. The producer has no enabled canonical CLI or approved execution plan. This
   is intentional while the budget is zero, but a later launch adapter must be
   separately hashed and reviewed.
3. The verifier currently restricts written reports to `development/`; a future
   canonical run path must be introduced only in the approved launch adapter or
   a reviewed verifier amendment.
4. Exact closure of all 672 cells may be infeasible under the proposed node and
   role budgets. No generated family row was spent to estimate this.
5. The deterministic sampler is not a proof of random-curve representativeness.
6. The tested effect may depend entirely on the frozen representative compiler.
7. Structural cells omit real interpreter, allocation, sorting, hashing,
   serialization, field, memory-traffic, and verifier costs.
8. No relation compiler, linear algebra, individual logarithm, or rho baseline
   is connected to this experiment.

### Next concrete action

Freeze this snapshot in Git and request fresh read-only theory, accounting, and
red-team `GO` or `REVISE` decisions. Do not prepare or launch a canonical run
unless all three approve the evidence boundary.

### Artifact paths

- `experiments/EXP-SGCP-EMBED-002/protocol-amendment-v3.json`
- `experiments/EXP-SGCP-EMBED-002/revision-response-v3.md`
- `experiments/EXP-SGCP-EMBED-002/development-test-log-v3.md`
- `experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py`
- `experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py`
- `tests/test_sgcp_embed_family.py`
