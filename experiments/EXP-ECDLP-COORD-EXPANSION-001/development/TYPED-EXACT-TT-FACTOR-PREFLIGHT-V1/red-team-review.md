# Red-Team Review: TYPED-EXACT-TT-FACTOR-PREFLIGHT-V1

## Verdict

Accept as a scoped toy observation. Do not promote it to an algorithmic improvement or ECDLP result.

## Objections and responses

1. **The raw baseline is a deliberately unrounded upper bound.** The comparison is useful only as a diagnostic that direct-sum/Kronecker closure loses cancellation. It does not show that a practical compiler can obtain the exact ranks.

2. **The exact factorization enumerates every tensor entry.** Its 15.1-second sweep and elimination counts are charged evidence for a diagnostic, not an online or offline attack cost. Any future compiler must include the cost of obtaining the same information without enumeration.

3. **The exact ranks are close to ambient at the important cuts.** The B=10 ranks `[11,110,55,10]` leave little evidence of an additional low-rank miracle after exact rounding. The promising signal is removal of the absurd raw closure rank, not a sub-square-root relation mechanism.

4. **The verifier reruns the producer and therefore is not an independently implemented elliptic/tensor evaluator.** It does independently check protocol, input hash, enumerative boundary, row count, promotion gates, and exact rerun digest. A future acceptance receipt should add a second arithmetic implementation or a cross-check against the existing independent rank-census implementation.

5. **The experiment uses one target per family and no batch.** It says nothing about target amortization, factor-base construction, rank across many target locators, or sparse matrix behavior.

6. **The factorized cores are not yet a reusable common basis.** Each row has its own exact factorization. Shared-core discovery across targets and factor-base families remains open.

## Required follow-up

Implement a sampling or circuit-contraction compiler with no full source-tuple enumeration, test it first on rank-one and planted low-rank controls, then verify all entries on the frozen toy cells. Report the exact rank gap, sampling/contraction cost, core traffic, supported target count, and failure probability.
