# Red-Team Review: D4 Membership Recovery Batch V1 RUN-001

## Findings

1. **Advice sharing is charged once per batch.** The route does not receive a
   hidden per-target advice discount or repeated fixed-curve construction.
2. **Recovery is not accidentally amortized.** Every per-target predecessor
   record is retained and summed; supported targets visibly pay a fresh D2
   recovery scan.
3. **The supported schedule is a control, not evidence of target solvability.**
   Its targets are constructed from public `A_i` and public D4 points to make
   success probability explicit.
4. **Translated controls expose success dilution.** Epsilon is included in
   the diagnostic, so a low-success batch cannot masquerade as a speedup.
5. **The verifier boundary is explicit.** Batch aggregation and target
   digests are independently checked; exact route semantics are authenticated
   by the predecessor verifier receipt and its hash.

## Disposition

`SCOPED NEGATIVE` for advice-only batching of D4 membership with recursive D2
recovery. Preserve the result as a many-target baseline. Do not run a larger
batch sweep until a successor supplies a genuinely shared recovery operator.
