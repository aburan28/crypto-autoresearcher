# Implementation

Status: development implementation complete; canonical source review and approval pending.

The generator will use the already audited affine arithmetic only as a hash-bound dependency. It will independently enforce the clean-curve policy introduced after the anomalous recursive-expansion result.

For `B` factor-base points, it first computes all unordered pair sums. It then enumerates every unordered four-index multiset exactly once, combines the canonical first and second pair sums, and retains every distinct four-sum key with at most the configured number of lexicographically earliest source witnesses. Enumeration work is charged even when a witness is discarded by the cap.

The relation collector chooses known target multiples from one deterministic permutation shared by all factor-base families on a curve. It scans the factor base for each target, emits at most the frozen number of distinct five-term rows, removes duplicate coefficient vectors, records rank growth, and stops only after full rank or the target budget is exhausted.

Full rank triggers modular Gaussian elimination. The resulting factor-base logarithms are verified point by point with scalar multiplication. Individual-log challenges then use charged additive randomization and first-witness queries; challenge scalars are private verification data and are not inputs to the solver path.

The independent verifier must reconstruct curves and factor bases through the prior independent arithmetic implementation, rebuild four- and five-term supports, verify every retained witness and relation, recompute rank and solutions, replay descent, and reject coefficient, right-hand-side, metric, source-hash, or configuration mutations.

The development implementation now also executes fixed-base BSGS on the identical target challenges under the candidate's full advice-bit budget. Both sampled-average and deterministic-worst-case online comparisons are mandatory routing gates. The attack-path cost vector reports group operations, charged `F_p` multiplications and inversions, mod-`q` linear operations, logical preprocessing writes, and online reads; exhaustive and witness-replay checks remain separately charged audit work.
