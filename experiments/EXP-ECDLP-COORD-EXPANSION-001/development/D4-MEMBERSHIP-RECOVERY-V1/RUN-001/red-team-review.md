# Red-Team Review: D4 Membership With Deferred Recovery V1 RUN-001

## Findings

1. **Advice reduction is genuine but partial.** D4 witness records are
   removed, while D2 state and witness advice remains. The route is not a
   zero-advice membership oracle.
2. **Recovery is fully charged.** Every support hit scans all D2 states and
   expands/replays all matching witness products. No recovery work is hidden
   in the membership metric.
3. **The support-hit rate is low on this toy batch.** That helps the route's
   online cost, but the resulting frontier still loses to materialized D4 on
   average and has no asymptotic evidence.
4. **The exactness claim is narrow.** It covers generated toy curves, four
   coordinate families, and three target labels per row. It does not establish
   relation yield, matrix rank, descent, or a generic ECDLP improvement.

## Disposition

`SCOPED NEGATIVE` for support-only D4 membership with recursive D2 recovery.
Preserve it as a fixed-curve many-target baseline. A successor should batch
recovery certificates or replace D2 scanning with an algebraically grouped
operator before expanding the parameter sweep.
