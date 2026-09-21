# Red-team review: 16-bit projective relation-batch rank completion

## Scope

This review checks whether expanded target batching supports a rank-completion claim or only a one-curve toy observation.

## Checks

- **Independent verification:** `RUN-TT-PROJECTIVE-RANK-COMPLETION-006` is valid. It regenerates the fixture, checks support and witnesses, verifies source hashes, reconstructs projective states, checks homogeneous zero-equivalence, validates weighted comparator rows, checks the expanded target count, and confirms the rank gate.
- **Rank:** both `source_prf_x` and `random_x` reach `15/15` on the fresh curve. This is consistent with the hypothesis that the earlier `11-13/15` ranks were partly a target-batch artifact, but one curve cannot distinguish a batch-size explanation from a favorable transcript.
- **Support and held-out targets:** full mode passes exact support and held-out witnesses for both families. At budget `96`, `random_x` passes the strict held-out acceptance list while `source_prf_x` does not; this prevents a stronger sub-full claim.
- **Arithmetic accounting:** projective weighted cost beats both affine comparators in all two family cells and all four registered inversion weights. Point additions and cache bytes remain separate costs, and the expanded batch peaks at `5.56 GB` RSS.
- **Controls:** `random_x` uses the same target transcript and was not selected after observing rank. Matched rho solves all targets. The experiment does not claim that the candidate family uniquely causes the rank or arithmetic behavior.
- **Receipt boundary:** the generator is valid but records `dirty=true` because an earlier failed wrapper run was present at launch. The independent verifier is clean; no claim depends on the generator's dirty flag being clean.

## Verdict

Retain as a positive, model-bound toy signal for target-batch rank completion and projective weighted arithmetic. Do not promote it to an index-calculus improvement, a fixed-curve preprocessing win, or an ECDLP break. The memory cost and one-curve replication boundary are material.

## Required successor controls

1. Repeat the `2B+1` target batch on a second fresh 16-bit curve.
2. Keep `random_x`, full support, held-out witnesses, rank `15`, and matched rho as mandatory controls.
3. Reject escalation if peak memory exceeds `6 GB` or if the weighted advantage disappears after relation-matrix and bandwidth accounting.
4. Add an explicit sparse linear-algebra and target-descent cost before making any preprocessing or online claim.
