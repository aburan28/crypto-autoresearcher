# Red-team review v2: protocol v3

## Handoff: v3 adversarial review

### Claim or task

Determine whether the v3 source-TT compiler protocol is sufficiently bound to
authorize source implementation.

### Status

`REVISE`

### Assumptions

- The two-stage Hadamard contraction follows `theory-v2.md`.
- All frozen counts were recomputed independently from the v3 schedule.
- No producer source existed during this review.

### Evidence so far

- The two-stage contraction is algebraically sound.
- Its frozen `B=5` multiplication count, 6,347,650 before factorization, is
  correct.
- The census of seven source cells, 63 source tensors, 25 target tensors, and
  352 final rank jobs is internally consistent.
- The modewise rescaling constants and the general-trace control constants are
  correct.
- The signed-int64 bound is mathematically sufficient under the frozen shape,
  canonical-residue, reduction, and kernel assumptions.
- The claim boundary correctly excludes a locator, relation algorithm,
  asymptotic result, and ECDLP improvement.

### Blocking findings

1. The stage-B workspace certificate is false at mode 3. The output slice has
   `s*r_a*r_b=B^6=15,625` words, not `B^5=3,125`. The overall local-workspace
   maximum remains 15,625 words, but the certificate must be repaired.
2. `accounting-model-v2.md` retains stale v2 language: 24 targets rather than
   25, optional NumPy despite the v3 binding, an already-satisfied amendment
   request, and a statement that aggregate ceilings are unavailable.
3. Limiting arrays to three dimensions does not exclude flattened
   `range(B**5)` traversal or five radix decodes. The accepted operation and
   dataflow model must be frozen and audited.
4. The raw-then-recompress mutant is too weak at the default C08 scope. One
   mutant must attempt the prohibited C12/B5 raw Hadamard allocation, while a
   second must traverse flattened `range(B**5)` without an oversized object.
5. Source preprocessing is not target blind because the producer may read the
   inherited manifest containing all targets. Compile from a target-redacted
   manifest, freeze and hash advice, then reveal targets to a separate
   specialization process.
6. The producer may read the mutation manifest. Mutation expectations must be
   harness/verifier input only.
7. The capability boundary conflates data reads, hashed local source, pinned
   package/runtime files, and unavoidable operating-system loader reads.
8. A NumPy version string does not identify the installed build. Bind the
   executable, architecture, installed package closure, and loaded extension
   objects, or change backend.
9. Aggregate work is underdefined. Freeze a componentwise operation vector and
   per-partition traffic ceilings instead of an ambiguous scalar field-work
   total.
10. Synthetic controls require frozen fields, tensors or deterministic core
    records, expected exact ranks, and expected operation transcripts.
11. M03 should attack the asymmetric modewise-rescaled cell. M07 must patch the
    shared normalizer used by live code, not a control-only route.

### Required mutations

- M18A: materialize the raw C12/B5 Hadamard TT and require pre-allocation or
  external-allocation rejection.
- M18B: traverse flattened `range(B**5)` with radix decoding and no oversized
  object.
- M26: report the wrong mode-3 stage-B slice, 3,125 rather than 15,625.
- M27: condition source advice on a target digest; the target-redacted phase
  split must reject it.
- M28: preserve NumPy's version string while changing its build/closure
  identity; backend attestation must reject it.

### Failure modes

- A producer can claim a valid IR trace while executing an untraced side path
  unless the transitive source closure and primitive call graph are audited.
- A target-blind API is not target blind if the process can read target-bearing
  files through an unbound helper or operating-system path.
- Componentwise campaign counters can still be misleading if copies, hashes,
  and serialization bytes are omitted.

### Next concrete action

Create a v4 bundle with target-redacted source input, a separate specialization
partition, corrected workspace and accounting records, exact backend closure,
frozen synthetic controls, and 29 live mutations; then obtain fresh accounting
and red-team reviews.

### Artifact paths

- `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/contract-v3.md`
- `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/accounting-model-v2.md`
- `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/execution-matrix-v2.json`
- `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/mutation-manifest-v2.json`
- `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/red-team-v2.md`
