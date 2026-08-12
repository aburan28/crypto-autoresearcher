# Pre-run red-team review v1

## Handoff: implementation, accounting, and launch controls

### Claim or task

Determine whether the reviewed implementation and accounting support the exact
noncanonical development launch.

### Status

`NEGATIVE RESULT`: `REVISE / NO-GO` for the reviewed launch snapshot.

This is a readiness result, not a negative result for the translator
hypothesis. The repaired sign, identity, workspace, matching, projection, and
conjunctive-aggregation controls are credited. All prospective results remain
`TOY-EVIDENCE`, `MODEL-BOUND`, and novelty-unverified.

### Evidence so far

- Focused suite at review: `43 passed, 12 subtests passed`.
- Reduced integration replay passed.
- The exact development schedule could not complete because its first two
  seeds produced repeated field moduli at 8 and 10 bits.

### Launch-blocking findings

1. The configured six-curve schedule produced moduli `251,251` at 8 bits,
   `991,991` at 10 bits, and `4079,3823` at 12 bits. The generator correctly
   rejects repeats, so the reproduction command deterministically aborted.
2. Source binding omitted theory v2/v3 and the red-team record, was computed
   only after expensive work, and did not reject start/end source drift.
3. Supported `16B` schedules could be clamped to smaller cardinalities and
   still enter conjunctive practical-signal groups.
4. Wall times and all timing-derived global signals could be coherently forged
   because volatile timing fields were intentionally excluded from replay.
   D2-major timing also included an affine audit that target-major timing did
   not.
5. The advertised direct quadratic-resultant comparator actually evaluated an
   already-built symbolic sparse `f4`; it did not count a direct scalar
   quadratic-resultant computation per tuple.
6. Source extraction occurred outside preprocessing timing. Executable advice
   retained roots that logical accounting omitted, while unused polynomial
   coefficients were charged. Required RSS language exceeded what was measured.
7. The verifier did not independently derive candidate total vectors, weighted
   work, ratios, crossovers, and continuation gates.
8. The contract named exceptional MOV exclusions without a quantitative or
   enforced embedding-degree test. All planned fields also came from the
   inherited `p mod 4 = 3` policy, which was not prominent in interpretation.
9. The reproduction command emitted only raw JSON rather than a prelog,
   stdout/stderr, environment/resource record, source-boundary hashes, verifier
   receipt, and final manifest.

### Required controls

- Preflight all curves, exclusions, unique moduli, and target cardinalities.
- Force a support-short `16B` case and prove it cannot become a signal.
- Remove unattested wall time from verified promotion semantics.
- Compare direct scalar resultants with symbolic `f4` on identical tuples.
- Independently derive every cost vector and gate used for continuation.
- Either add same-map nulls or mark non-identity-map comparisons confounded and
  ineligible for coordinate-specific continuation.
- Record the `p mod 4 = 3` restriction and test a quantitative MOV threshold.
- Launch only through an immutable run wrapper.

### Failure modes

- Mistaking an infrastructure abort for hypothesis evidence.
- Labeling a shortened batch as `16B`.
- Letting forged timings create a global signal.
- Letting same-code replay certify a coherent accounting defect.
- Letting missing memory data or a restricted field family manufacture a toy
  advantage.

### Next concrete action

Repair all findings, bind this review and a later theory `GO`, and request a
second red-team review against a source-stable snapshot before launch.

### Artifact paths

- `contract.md`
- `pre-run-theory-review-v2.md`
- `src/exact_floor.py`
- `src/polynomial_engine.py`
- `src/outer_translator.py`
- `src/verify_outer_translator.py`
- `tests/test_outer_translator.py`

## Coordinator response

The v1 `NO-GO` is preserved. No evidence run was started. Every listed issue is
treated as a repair or explicit de-scoping obligation, followed by a distinct
theory and red-team decision.
