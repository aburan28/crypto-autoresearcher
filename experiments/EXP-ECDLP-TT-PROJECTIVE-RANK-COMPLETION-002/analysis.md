# Analysis: second 16-bit projective relation-batch rank completion

## Handoff: second fresh curve replication

### Claim or task
Replicate the `2B+1` expanded relation-batch signal on a second fresh 16-bit ordinary prime-order curve with the same support, rank, weighted-cost, memory, and rho gates.

### Status
MIXED POSITIVE SIGNAL, SCOPED NEGATIVE FOR FAMILY-INDEPENDENT RANK, TOY-EVIDENCE, MODEL-BOUND

### Assumptions
- The fixture is a fresh deterministic ordinary prime-order curve at 16 field bits with seed `86420`.
- `source_prf_x` is the candidate family and `random_x` is the predeclared negative control.
- The relation transcript contains 29 generated targets and up to four supported held-out targets, giving 33 target rows.
- Full rank `15` is the required relation-matrix gate for this fixture; rank completion is not an individual-log descent.
- The memory gate is the immutable harness limit of `6 * 1024^3` bytes peak RSS.

### Evidence so far
- Generator `RUN-TT-PROJECTIVE-RANK-COMPLETION-002` is `completed_valid`; raw-result SHA-256 is `97023b5b38aaee460f35dfe392464f1d68415cc6215d814637165900a07c7af3`.
- Independent verifier `RUN-TT-PROJECTIVE-RANK-COMPLETION-003` is `completed_valid`; raw-result SHA-256 is `0861a3c2d206e767e78c0ec478f52427f3d3e5b5d397d3b3854716efa4235611`. Every integrity, support, witness, homogeneous-scaling, weighted-comparator, target-batch, rho, and memory check passes; `rank_gate=false` is reported separately.
- The fresh curve is `recursive-toy-p62071-a30383-b11933-q62137`. Full `source_prf_x` rank is `15/15`; full `random_x` rank is `13/15`. Both families pass exact support, held-out witnesses, and matched rho. The rho control uses `156,937` group operations.
- Neither family accepts the strict `96` budget: `source_prf_x` loses held-out support there, while `random_x` is rank-deficient. Full mode passes held-out support for both families.
- Projective weighted cost is below both affine comparators in all `2` family cells and all four inversion weights. At weight `100`, projective versus naive-orbit versus original-affine costs are `149,711,818 / 2,063,701,208 / 2,918,567,392` for `source_prf_x`, and `173,812,264 / 2,063,745,794 / 2,918,549,820` for `random_x`.
- Full projective charged field multiplications are `148,917,518` and `173,003,064`, with `7,943` and `8,092` inversions for `source_prf_x` and `random_x`. The projective cache is approximately `140.65 MB` for both. The run took `847.9` wall seconds, `832.8` CPU seconds, and peaked at `6,184,501,248` bytes, below the `6,442,450,944` byte contract limit.

### Failure modes
- The first-curve rank completion does not replicate as a family-independent property: the predeclared `random_x` control remains at `13/15` on this second curve.
- The candidate family reaches full rank here and on the first curve, but the experiment is still only two ordinary 16-bit curves and does not establish asymptotic rank behavior.
- The extra target batch consumes nearly the full memory budget. Any larger-field escalation needs a memory reduction or a stricter resource design.
- Weighted cost counts field multiplications and inversions; physical bandwidth, sparse linear algebra, and individual-log descent remain separate open costs.
- No cryptographic-scale factor-base build, fixed-curve preprocessing tradeoff, or individual-log recovery is present.

### Next concrete action
Do not escalate the uncompressed `2B+1` scan. Preserve the repeated `source_prf_x` rank signal, but design a source-aware rank-preserving selector or compressed row-space construction that is tested against both families and lowers retained advice or peak memory. Require full rank, held-out support, sparse linear-algebra accounting, and matched rho on fresh curves.

### Artifact paths
- `experiments/EXP-ECDLP-TT-PROJECTIVE-RANK-COMPLETION-002/contract.md`
- `experiments/EXP-ECDLP-TT-PROJECTIVE-RANK-COMPLETION-002/specification.json`
- `experiments/EXP-ECDLP-TT-PROJECTIVE-RANK-COMPLETION-002/src/run_rank_completion_harness.py`
- `experiments/EXP-ECDLP-TT-PROJECTIVE-RANK-COMPLETION-002/src/verify_rank_completion_harness.py`
- `experiments/EXP-ECDLP-TT-PROJECTIVE-RANK-COMPLETION-002/runs/RUN-TT-PROJECTIVE-RANK-COMPLETION-002/`
- `experiments/EXP-ECDLP-TT-PROJECTIVE-RANK-COMPLETION-002/runs/RUN-TT-PROJECTIVE-RANK-COMPLETION-003/`

## Interpretation

The `2B+1` target batch preserves full rank for the declared `source_prf_x` family on both fresh 16-bit curves, but the random negative control loses rank on the second curve. The strongest supported conclusion is therefore a candidate-family signal plus a family-independent rank negative, not a generic relation compiler. The projective weighted arithmetic signal survives, but memory is close to the hard limit and the uncompressed batch should not be escalated unchanged.
