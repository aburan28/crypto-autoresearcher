# Analysis: 16-bit projective relation-batch rank completion

## Handoff: expanded target batch

### Claim or task
Test whether increasing the registered relation batch from `B+1` to `2B+1` restores the 16-bit projective locator's missing relation rank without losing its weighted arithmetic advantage.

### Status
POSITIVE SIGNAL, TOY-EVIDENCE, MODEL-BOUND

### Assumptions
- The fixture is one fresh deterministic ordinary prime-order curve at 16 field bits.
- `source_prf_x` is the candidate family and `random_x` is the predeclared negative control.
- The relation transcript contains 29 generated targets and up to four supported held-out targets, giving 33 target rows.
- Weighted cost is field multiplications plus `w` times field inversions for `w` in `{10,50,100,200}`; point additions, cache bytes, and wall time remain separately charged.
- Full rank `15` is the required relation-matrix gate for this fixture; rank completion is not an individual-log descent.

### Evidence so far
- Generator `RUN-TT-PROJECTIVE-RANK-COMPLETION-003` is `completed_valid`; raw-result SHA-256 is `c41977b1cf6be8fe9b8c2604374d4c90295828840086a22639941118231e56c7`.
- Independent verifier `RUN-TT-PROJECTIVE-RANK-COMPLETION-006` is `completed_valid`; raw-result SHA-256 is `e6f05e6ba651e5fd5841fe91af4a60e2154b116c0f3118ac28e751c5b6c9c160`, with a clean verifier receipt and `rank_gate=true`.
- The fresh curve is `recursive-toy-p64283-a36250-b28647-q64171`; both families reach rank `15/15` with exact full support and valid witnesses. The matched rho control solves all targets using `155,938` group operations.
- The `96` class budget has exact support and rank for both families, but only `random_x` passes the stricter held-out-support acceptance list. Full mode passes held-out support for both families.
- Projective weighted cost is below both comparators in all `2` family cells and all four inversion weights. At weight `100`, projective versus naive-orbit versus original-affine costs are `173,798,028 / 2,063,688,328 / 2,918,541,200` for `source_prf_x`, and `224,251,622 / 2,063,766,878 / 2,918,609,246` for `random_x`.
- Full projective charged field multiplications are `173,009,328` and `223,394,422`, with `7,887` and `8,572` inversions for `source_prf_x` and `random_x`; the projective cache is approximately `140.67 MB` for both. The expanded run took `935.9` wall seconds, `898.9` CPU seconds, and peaked at `5.56 GB` RSS.

### Failure modes
- The rank result is one curve and one target-batch multiplier; it does not establish cross-curve persistence.
- The extra targets materially increase resource use. Peak RSS is close to the registered `6 GB` limit, and source-prf-x does not pass the strict held-out-support acceptance list at budget `96`.
- The weighted comparator excludes physical memory bandwidth and does not establish a wall-clock win or a fixed-curve preprocessing frontier win.
- No sparse linear-algebra solve, individual-log descent, cryptographic-size factor-base build, or target recovery is present.
- The generator receipt was launched while prior failed implementation artifacts were present, so its harness metadata records `dirty=true`; the independent verifier itself is clean and rechecks the relevant source hashes and invariants.

### Next concrete action
Repeat the `2B+1` batch on a second fresh 16-bit curve with the same controls, while explicitly charging peak memory and relation-matrix work. Escalate field size only if full rank, held-out support, and the weighted advantage persist without exceeding the memory budget.

### Artifact paths
- `experiments/EXP-ECDLP-TT-PROJECTIVE-RANK-COMPLETION-001/contract.md`
- `experiments/EXP-ECDLP-TT-PROJECTIVE-RANK-COMPLETION-001/specification.json`
- `experiments/EXP-ECDLP-TT-PROJECTIVE-RANK-COMPLETION-001/src/run_rank_completion_harness.py`
- `experiments/EXP-ECDLP-TT-PROJECTIVE-RANK-COMPLETION-001/src/verify_rank_completion_harness.py`
- `experiments/EXP-ECDLP-TT-PROJECTIVE-RANK-COMPLETION-001/runs/RUN-TT-PROJECTIVE-RANK-COMPLETION-003/`
- `experiments/EXP-ECDLP-TT-PROJECTIVE-RANK-COMPLETION-001/runs/RUN-TT-PROJECTIVE-RANK-COMPLETION-006/`

## Interpretation

The expanded target batch explains the earlier 16-bit rank deficit on this one fresh curve: rank reaches `15/15` while the projective arithmetic advantage survives every registered weighted comparison. This is a useful relation-batch and accounting signal, not an index-calculus breakthrough. The next gate is replication under the same memory and held-out-support requirements.
