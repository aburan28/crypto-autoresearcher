# TT source compiler implementation development checkpoint v1

## Status

`OBSERVATION`, `TOY-EVIDENCE`, `MODEL-BOUND`, `NOVELTY-UNVERIFIED`.

This checkpoint records a development implementation and a non-freezing
verification pass. It is not an authorized experiment run, a source-advice
freeze, a locator, a relation algorithm, an index-calculus exponent, a target
descent, a Pollard-rho improvement, or an ECDLP breakthrough.

## Implemented boundary

- The source compiler interprets the frozen 40-gate RCB circuit using exact
  order-five TT primitives and never enumerates a producer-side `B^5` table.
- Direct sums use exact left-to-right then right-to-left normalization.
- Hadamard products use the frozen two-stage streamed contraction and allocate
  each local matrix only after all immutable physical-slice outputs exist.
- Exact rank factorization uses lexicographic finite-field elimination.
- Every dense allocation has one immutable IR producer, one digest, and one
  allocation/free transition.
- The C08 random-unique cell carries a complete allocation-ID transcript. The
  independent verifier replays every payload using separate arbitrary-precision
  arithmetic, TT evaluation, rank factorization, and RCB code.
- The static closure auditor checks disjoint producer/verifier closures and the
  frozen phase-firewall policy.

## Development evidence

The pinned Python 3.13.1 and NumPy 2.4.0 run completed all seven source cells.
The canonical raw result was 132 MiB and remained below the 256 MiB raw-result
gate.

| Measure | Observed |
|---|---:|
| source cells | 7 |
| tensor records | 63 |
| exhaustive verifier tuples | 9,027 |
| exhaustive tensor-value checks | 81,243 |
| IR events | 65,347 |
| allocation/free events | 136,442 |
| independently replayed C08 nodes | 8,641 |
| normalization calls | 1,022 |
| streamed-prefix factorizations | 1,512 |
| two-sweep factorizations | 8,176 |
| total rank factorizations | 9,688 |
| maximum local matrix | 10,800 field words |
| maximum TT object | 6,150 field words |
| peak live storage | 49,580 field words |
| producer peak RSS | 632,750,080 bytes |
| verifier peak RSS | 1,286,717,440 bytes |

The development verifier reconciled the complete producer operation vector,
traffic buckets, liveness transitions, allocation ledger, and peak live count.
It independently checked every C08 arithmetic count in
`adds,subs,muls,squares,inversions,reductions,comparisons`.

Development-only digests from this checkpoint are:

- raw result:
  `771ad7833846068a0354abf8e246b131b494a6b85d07e65675de42873bcb51d3`
- implementation-audit report:
  `443e16f127e34199c97303754b7aed9e1bda544e2c131bfa24baa0f90381966d`
- static closure-audit report:
  `42a344884c7a3804f9e8ffba514a5e9f6d7f5c276ced0d61fbadfc3c3e031dda`

These digests are not frozen run artifacts and may change when the external
runner, reviews, or implementation repairs change the source closure.

## Remaining gates

The producer conservatively reports the following external facts as false:

- filesystem audit passed;
- deterministic environment audit passed;
- AST/call-graph audit passed;
- isolated staging root;
- absence of repository, target, mutation, and prior-artifact files.

The development verifier therefore sets
`artifact_freeze_authorized=false` and emits no source artifact. A harness-side
runner must enforce and attest those facts. Independent implementation
accounting and red-team reviews are also required before implementation freeze
or run authorization.

## Failure modes still open

- The runtime audit may reveal filesystem or loader accesses outside the frozen
  closure.
- Isolated staging may require a versioned receipt interface repair.
- The target specializer and target verifier are not yet implemented.
- The source compiler may pass all toy gates while target specialization or
  mutation testing fails.
- Even a fully accepted experiment would establish only a toy coordinate-circuit
  measurement, not a sub-rho attack.

## Next concrete action

Implement and test the isolated source-partition runner that emits a
hash-bound `runner-receipt.json` and leaves target-bearing records unavailable
until independent source verification has frozen the advice receipt.
