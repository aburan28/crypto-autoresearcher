# Red-Team Review: Implicit Pair-State Index V1 RUN-001

## Findings

1. **Deferred lift is real.** Pair records contain only two D2 state IDs;
   four-source witness tuples are generated at query time from the retained
   D2 witness lists.
2. **The state-pair count is still quadratic.** The record count is exactly
   `N2*(N2+1)/2` for each row, so removing witness payload does not remove
   pair-state enumeration.
3. **Exact state-ID indexing is not a materialized-D4 quotient.** Distinct
   state pairs with the same point sum remain distinct records, whereas D4
   collapses them by sum point and retains witnesses under that point.
4. **Fingerprint collisions are charged.** Widths 1, 2, and 4 recompute the
   candidate state sum and reject collisions before witness lift; those
   additions appear in the online metric.
5. **No cryptanalytic claim is supported.** The campaign uses three generated
   toy curves, four factor-base families, and no relation rank, individual-log
   descent, rho comparison at cryptographic scale, or asymptotic proof.

## Disposition

`SCOPED NEGATIVE` for explicit state-ID pair tables with deferred witness
lift. Preserve the implementation as an accounting baseline. A successor is
worth running only if its grouping object is algebraically smaller than the
quadratic state-pair table before witness materialization.
