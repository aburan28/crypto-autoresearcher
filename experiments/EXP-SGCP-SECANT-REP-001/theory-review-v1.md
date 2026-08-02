# Theory Review V1

## Handoff: Secant representative preflight

### Claim or task

Review preregistration commit
`cc5e93d356ca114b09e6eff4d8c2a89cd3b384ae` for implementation readiness.

### Status

`OBSERVATION`: `REVISE`. No implementation or execution is authorized.

### Evidence so far

- The secant and tangent formulas are correct under explicit branch rules.
- For a fixed nonidentity output `R`, the witness line also contains `-R`, so
  distinct valid unordered witness multisets cannot share the same line under
  the registered curve assumptions.
- V1 did not freeze field-element ordering, multiset encoding, the exact
  inherited optimizer objective, downstream-universe terminology, hash bytes,
  finite-rank ties, exhaustive outcomes, or a bound positive control.

### Failure modes

- Tangent witnesses could be collapsed by set rather than multiset semantics.
- Implementations could choose different field orderings, objectives,
  deduplication rules, quantiles, or hash encodings while appearing compliant.
- A one-of-three signal was neither a success nor a scoped negative.
- Conflict reduction was predicted but absent from the promotion gate.

### Next concrete action

Freeze exact encodings, one optimizer objective, common versus
compiler-specific universes, deterministic rank semantics, controls, and
exhaustive outcomes in v2.

### Artifact paths

- `experiments/EXP-SGCP-SECANT-REP-001/contract.md`
- `experiments/EXP-SGCP-SECANT-REP-001/hypothesis.json`
- `experiments/EXP-SGCP-SECANT-REP-001/specification.json`
