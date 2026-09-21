# Revision history v4

## Preserved status

- V1 received theory `REVISE` for the missing `nY_Q^2` target term and
  one-sweep normalizer.
- V2 received theory `GO` but red-team `REVISE` for capability, aggregate
  accounting, backend, mutation, control, and literature gaps.
- V3 received red-team `REVISE` for one false workspace certificate, target
  visibility during preprocessing, insufficient operation/dataflow binding,
  ambiguous aggregate accounting, incomplete backend identity, and weak
  mutations.
- No producer, specializer, or verifier source has been written and no run
  exists.

## V4 repairs

1. Corrected the mode-3 stage-B output slice from `B^5=3,125` to
   `B^6=15,625` words. The maximum local matrix and transfer remain 78,125
   words.
2. Split the inherited data into a target-redacted
   `source-instance-manifest-v1.json` and withheld
   `target-instance-manifest-v1.json`, plus a target-free
   `source-execution-matrix-v1.json`. Source advice is independently checked,
   canonicalized, and hashed before a separate target process starts. The
   source-only diagnostic samples are target-independent and exclude all
   planted tuples.
3. Removed inherited and mutation manifests from the source process data-read
   allowlist. Mutation expectations are available only to the mutation harness
   and verifier.
4. Separated four capability categories: data inputs, transitive local source,
   pinned Python/package runtime, and OS loader reads.
5. Bound the Python executable SHA-256, Python version and architecture, all
   1,320 installed NumPy distribution files and closure digest, the core NumPy
   extension digest, dtype, order, thread count, and loader paths.
6. Added a closed operation IR and required complete runtime IR plus transitive
   AST/call-graph audits. No node accepts a linear `B^5` table index, five
   physical indices, or radix decoding.
7. Replaced ambiguous total field work with the non-resetting componentwise
   vector `(adds,subs,muls,squares,inversions,reductions,comparisons,
   hash_bytes,copied_words)` for every event, six partitions, and the campaign.
8. Froze traffic buckets, per-partition traffic caps, source/target phase order,
   and six run partitions.
9. Added `control-manifest-v1.json` with exact fields, explicit or deterministic
   TT inputs, expected ranks, a value digest, and expected IR transcripts.
10. Replaced the raw-product mutant with independent C12/B5 raw-allocation and
    flattened-enumeration mutants; added stage-B, target-conditioned-advice,
    and same-version/different-build mutants. The frozen total is 29.
11. Retargeted the mode swap to the asymmetric modewise-rescaled cell and the
    one-sweep mutant to the shared production normalizer.

## Unchanged claim boundary

Passing would be `TOY-EVIDENCE` and a `RESTRICTED IMPLEMENTATION RESULT` for
constructing the frozen first-norm source advice. It would not be a Fermat
locator, relation algorithm, asymptotic index-calculus result, target descent,
sub-rho algorithm, or ECDLP improvement.

## Execution effect

The experiment remains `REVIEW_REQUIRED`. The existing mathematical theory
`GO` remains applicable because the tensor identities are unchanged. Fresh
accounting and red-team reviews must both return `GO` before source
implementation.

## Handoff: v4 review bundle

### Claim or task

Audit the target-blind, operation-bound, componentwise-accounted v4 protocol.

### Status

`OPEN`

### Assumptions

- The v2 mathematical TT and first-norm identities remain unchanged.
- The local runtime identity remains exactly the frozen closure.

### Evidence so far

- All v3 blockers have corresponding versioned repairs.
- Source and target data are now disjoint files with frozen schedules.
- No implementation or empirical output can influence these records.

### Failure modes

- A phase or package closure may still contain an unbound read.
- An aggregate or traffic term may still be double-counted or omitted.
- The control transcript may fail to exercise a live production primitive.

### Next concrete action

Run the independent v4 accounting and red-team reviews.

### Artifact paths

- `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/contract-v4.md`
- `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/accounting-model-v3.md`
- `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/execution-matrix-v3.json`
- `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/source-execution-matrix-v1.json`
- `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/mutation-manifest-v3.json`
