# Analysis: 16-bit projective shared-sign sweep

## Handoff: scale and rank gate

### Claim or task
Test whether the three-curve 14-bit projective shared-sign signal survives two fresh 16-bit curves under weighted arithmetic and downstream relation accounting.

### Status
MIXED POSITIVE SIGNAL, SCOPED NEGATIVE FOR SUB-FULL/RANK GATE, TOY-EVIDENCE, MODEL-BOUND

### Assumptions
- The two fixtures are fresh deterministic ordinary prime-order curves at 16 field bits.
- `source_prf_x` is the predeclared candidate family and `random_x` is the negative control.
- Weighted arithmetic is `field_multiplications + w * field_inversions` for `w` in `{10,50,100,200}`; point-add calls and memory are reported separately.
- Relation/rank accounting is downstream evidence, not an individual-log descent.

### Evidence so far
- Generator `RUN-TT-PROJECTIVE-16BIT-001` is `completed_valid`, bound to clean commit `464550b73a1d595e50c615b5dec5ea06a5557755`; raw-result SHA-256 is `2c2b757722f8748241527205f0406ccbb822a5db218c3574c9f23fb9a2835259`.
- Independent verifier `RUN-TT-PROJECTIVE-16BIT-002` is `completed_valid`, bound to clean commit `7a1cd896fe9350fc2cbc45a29d0866c84039a969`; raw-result SHA-256 is `679576d053466d3401c6f63d3e41b5eef3078187b49ea2f585b899623d5050a2`. It reports 64 checks with no failures.
- Both fresh curves pass full exact support, valid witnesses, and matched rho. Total matched rho work is `178,388` group operations.
- Neither curve accepts budgets `64` or `96` for either family. Full relation ranks are `11-13` while the target matrix dimension is `15`; the full scan therefore preserves correctness but does not preserve the required full rank at this scale.
- Projective weighted arithmetic is below both affine comparators in all 4 curve/family cells for every registered inversion weight. At the raw counter level, projective field multiplications are `89.97M-132.86M` and inversions `7,034-7,269`, versus `1.158B` and `583.8k-584.0k` for the naive orbit quotient and `1.650B` and `544.1k-544.3k` for the original affine predicate.
- Projective point additions are `582,528-582,746`, essentially equal to the naive quotient and about 7% above the original affine path. Projective source-cache memory is approximately `140.65 MB`, versus `107.34 MB` for naive orbit and `124.11 MB` for the original comparator.
- The full run took `1,220.4` wall seconds, `1,146.4` CPU seconds, and reached `3.40 GB` peak RSS. This resource growth is part of the scale result.

### Failure modes
- The homogeneous arithmetic advantage does not by itself reduce the class scan enough to pass a sub-full budget.
- Relation rank is deficient at full class support on both curves, so the result cannot support a complete relation-matrix or individual-log claim.
- Memory and point-add costs grow with the projective cache; the weighted table omits physical bandwidth and treats point-add calls as a separate structural counter.
- The candidate remains two-family and two-curve medium-toy evidence, with no cryptographic-scale factor-base build or individual-log descent.

### Next concrete action
Preserve the projective arithmetic as a reusable source-state primitive, but move the next attack effort to a rank-preserving selector: test source-aware class ordering or a compressed row-space basis at 16 bits while requiring full rank `15`, held-out support, and the same weighted/memory gates. Do not spend more budget on an uncompressed full scan at this scale until the rank bottleneck is addressed.

### Artifact paths
- `experiments/EXP-ECDLP-TT-PROJECTIVE-16BIT-001/contract.md`
- `experiments/EXP-ECDLP-TT-PROJECTIVE-16BIT-001/specification.json`
- `experiments/EXP-ECDLP-TT-PROJECTIVE-16BIT-001/src/run_projective_16bit_harness.py`
- `experiments/EXP-ECDLP-TT-PROJECTIVE-16BIT-001/runs/RUN-TT-PROJECTIVE-16BIT-001/`
- `experiments/EXP-ECDLP-TT-PROJECTIVE-16BIT-001/runs/RUN-TT-PROJECTIVE-16BIT-002/`

## Interpretation

The projective shared-sign arithmetic generalizes to the next scale as a weighted field/inversion improvement, but the relation compiler does not. The useful research lesson is now narrower and sharper: projective homogeneous evaluation is a viable primitive for a future rank-preserving selector, not a standalone index-calculus breakthrough.
