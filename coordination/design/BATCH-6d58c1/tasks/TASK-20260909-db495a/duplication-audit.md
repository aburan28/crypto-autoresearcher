# Duplication audit: deferred-lane minimum-viable-batch cost gate

## Scope of this audit

This document records only the design task's duplication boundary. It did not
search the repository, inspect proposal inventories, inspect live lanes, read
literature, or compare cost models. Consequently it does not assert novelty,
non-duplication, dominance, or a state-of-the-art delta.

## Candidate mechanism

The candidate is a zero-run typed accounting gate. It requires an exact
source-bound cost, compatible baseline, range, count, ratio, calibration, and
consumer binding before a future record may be labeled `COMPARABLE`. Missing
inputs instead produce `UNESTIMABLE` or `NO_CONSUMER` and are prohibited from
changing research state.

## Known comparison status

| Candidate aspect | Search performed | Status | Reason |
| --- | --- | --- | --- |
| Deferred-lane cost templates in this repository | No | inconclusive | No repository inventory was read. |
| Cost-model research literature | No | inconclusive | No source was read or retained. |
| Existing calibration/accounting schemas | No | inconclusive | No live or historical schema was compared. |
| Existing consumer or priority contracts | No | inconclusive | The task was prohibited from inspecting them. |

## Pareto and dominance status

`dominated_by` is **inconclusive**. No rows of a time, memory, data, query, or
administrative-effect frontier were inspected. The draft must not be described
as lower-cost, stronger, less burdensome, or preferable to any existing method.

`sota_delta` is **unavailable**. No state-of-the-art reference was retrieved or
read.

## Future duplicate screen requirements

Before a canonical proposal could be considered, a source-bound duplicate
screen must compare at least:

1. the exact input identity and hash-binding rules;
2. the cost boundary and unit compatibility rules;
3. the range/count/ratio/calibration/consumer cross-bindings;
4. the `UNESTIMABLE`, `NO_CONSUMER`, and no-state-change semantics;
5. the affected outcome scope and any claimed administrative effect.

Each comparison needs retained sources, immutable locators, hashes, and an
independent review. Until then, this document is a record of uncertainty, not
evidence of novelty.
