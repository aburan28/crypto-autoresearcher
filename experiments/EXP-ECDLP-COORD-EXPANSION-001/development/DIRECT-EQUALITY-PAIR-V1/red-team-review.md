# Independent Red-Team Review

## Handoff: Independent red-team of DIRECT-EQUALITY-PAIR-V1

### Claim or task

Audit the equality-pair theorem, residual-zero semantics, 24/12 dimensions,
invariance, ranks, planted controls, verifier, and state accounting.

### Status

- algebraic core: `RESTRICTED THEOREM`;
- sweep: `OBSERVATION`, `TOY-EVIDENCE`, `MODEL-BOUND`;
- explicit materialization: scoped `NEGATIVE RESULT`;
- overall: `REVISE INTERPRETATION`.

### Assumptions

- smooth short-Weierstrass curves over odd prime fields;
- valid nonzero projective outputs and affine targets;
- frozen left-associated circuit and cuts 2/3;
- one seed and materialized ordered suffix tuples;
- `B=Theta(q^0.2)` only as an asymptotic design assumption.

### Evidence so far

- The residual identity, norm reconstruction, degree doubling, cubic
  normal-form dimensions 24/12, and simultaneous-zero equivalence are
  algebraically correct under the assumptions.
- The artifact reports 2,223,216 pair evaluations and 865,072
  target-labeled suffix-permutation classes with zero shared-code mismatch.
- A separate read-only affine audit found 316 planted ordered witnesses, 84
  incidental held-out witnesses, 36 infinity outputs, and zero affine
  alternate-tree mismatch across 555,804 five-tuples. These checks are not
  preserved in the official artifact.
- An independent Gaussian reducer reproduced sampled suffix ranks
  `(24,24,48)` and `(12,12,24)` from vectors regenerated through the
  producer's polynomial path.

### Failure modes

1. Permutations are only internal to the suffix with fixed prefix, cut, and
   left-associated tree.
2. Canonical residual direction is non-injective and cannot substitute for
   direct point equality.
3. The verifier imports and reruns the producer; coefficient matrices and
   witnesses are not emitted.
4. The raw residual vector scales; only projective class and zero status are
   gauge-invariant.
5. Affine-section checks skip infinity, and target infinity/rescaling are
   untested.
6. Planted witness counts are absent from the official gate.
7. Dimensions 24/12 are ambient frozen-circuit dimensions, not
   representation-independent minima.
8. Concatenated row rank is not intrinsic predicate rank, relation rank,
   memory lower bound, or descent evidence.
9. Logical payload omits prefix state, live residency, validation arrays,
   traffic, compilation, rank work, and exhaustive replay.
10. Dependency versions, dirty-state receipt, operations, and a formal
    experiment-state transition are absent.

### Next concrete action

Run `DIRECT-EQUALITY-PAIR-V2-INDEPENDENT-CROSS-TREE`:

- independent affine/projective addition and cubic normal forms;
- authenticated coefficient chunks and independently recomputed ranks;
- planted indices, counts, nonzero-output checks, and witnesses;
- full `S4`, cross-cut allocations, all 14 trees, and random rescalings;
- infinity, doubling, inverse-pair, repeated-point, and mutation controls;
- separate compilation, specialization, validation, rank, residency,
  traffic, and payload ledgers;
- at least three seeds per size.

Preserve the explicit-state negative unless a witness-returning
simultaneous-zero index avoids `B^3` materialization and passes relation-rank,
memory, and descent accounting.

### Artifact paths

- `development/DIRECT-EQUALITY-PAIR-V1/contract.md`
- `development/DIRECT-EQUALITY-PAIR-V1/raw-result.json`
- `development/DIRECT-EQUALITY-PAIR-V1/verification.json`
- `src/direct_equality_pair.py`
- `src/verify_direct_equality_pair.py`
