# EXP-SGCP-EMBED-002 revision response v2

## Disposition

Accept every finding in `development-red-team-v1.md`. Version 1 remains a
verified development artifact and cannot satisfy the family hypothesis.

## Objective repair

Version 2 replaces the unconstrained support-per-label ratio with the certified
frontier

```text
R*(C) = max R(S) subject to constrained_count(S) <= C.
```

Candidate and null are compared only at the same integer cap on the same curve
and B. The caps are `floor(q/4)`, `floor(q/2)`, `floor(3q/4)`, and `q`.

## Accounting repair

- Live capped-search frontier states become charged private artifacts.
- Shared precomputation and every cap cell receive separate operation receipts;
  their exact sum must equal the row total.
- Public, private, and per-cap serialized byte receipts are independently
  recomputed by the verifier.
- Balanced-raw final support and full 8F support receive distinct names.
- Formal-multiset and ordered-tuple energies receive distinct fields and source
  measures.
- Duplicate curve draws receive explicit rejection records.

## Evidence repair

The independent verifier must reconstruct every frontier state, candidate/null
cap, energy field, and bound. A nonzero-gap cell cannot enter a positive gate.

## Budget response

Version 1 consumed 17/18 development rows. Version 2 permits only unit tests and
frozen-fixture controls. It does not authorize another empirical sweep or any
canonical run.

## Remaining gate

Independent theory, accounting, and red-team review must issue GO on the frozen
version-2 source and execution plan before `maximum_runs` can move above zero.
