# Analysis: shared-sign source-state operator

## Handoff: paired affine source-state arithmetic

### Claim or task
Test whether the two members of each source negation orbit, `P+S` and `P-S`, can be evaluated with one shared denominator inversion without changing the exact lifted relation support.

### Status
POSITIVE SIGNAL, TOY-EVIDENCE, MODEL-BOUND

### Assumptions
- The experiment uses two fresh deterministic ordinary prime-field curves of approximately 14 bits.
- The source orbit is keyed by `x(R2+R3)` and the target predicate is unchanged.
- Affine field-operation counts are the declared cost model; memory, point additions, lift, rank, held-out coverage, and matched rho are reported separately.
- The source orbit cache is fixed-curve advice and is charged as retained bytes.

### Evidence so far
- Generator `RUN-TT-SHARED-SIGN-OPERATOR-002` is `completed_valid`, bound to commit `0a0cc257263db86e02adec8ea872fbaed7f4a79d`, with raw-result SHA-256 `492fa1703934388c2e30f211bd6f4f5dab14789500d2b39cabf1a32514c4ece9`.
- Independent verifier `RUN-TT-SHARED-SIGN-OPERATOR-003` is `completed_valid`, clean, bound to the same code commit, with raw-result SHA-256 `e1b952062ff1f4bb5c83efe7a447f47a22c0851cfaef2396bcfb1f645998d5f1`.
- Every full budget has exact support, valid lifted witnesses, and a solved matched rho certificate. Total matched rho work is `211,901` group operations.
- The strict sub-full `source_prf_x` gate accepts budgets `32` and `44` on `p=15667`, and budget `44` on `p=15683`. The other families fail the strict gate, and `p=15683/source_prf_x` fails at budget `32`; this is a mixed signal, not a universal selector result.
- Full source caches contain `60,500` or `66,000` paired calls and retain approximately `22.9` or `24.8` MB. Shared source inversions are approximately `60.5k-66.0k`, compared with `124.3k-136.2k` for the naive orbit quotient and `112.6k-123.3k` for the original full predicate.
- Charged field multiplications are approximately `101.095M-110.211M` for the paired operator, `101.216M-110.343M` for the naive quotient, and `141.115M-153.949M` for the original full predicate. Point-add calls remain essentially the naive quotient count and exceed the original predicate count, so the aggregate vector is not a broad end-to-end win.

### Failure modes
- The shared denominator only reduces the source-state inversion component; it does not remove the two affine point reconstructions.
- Exceptional equal-x and identity cases require exact fallbacks and are explicitly counted.
- The sub-full gate is not stable across both curves and all coordinate families.
- These are toy fixed-curve relation-locator measurements. They do not include a cryptographic-scale factor-base build, sparse linear algebra, individual-log descent, or a comparison against a full rho attack at the target security level.

### Next concrete action
Implement a projective or differential shared-sign source operator, then repeat `source_prf_x` on at least one additional fresh curve with the same exact-support, rank, memory, and charged-cost gates. Preserve the affine operator as the baseline and do not promote this result to an exponent claim.

### Artifact paths
- `experiments/EXP-ECDLP-TT-SHARED-SIGN-OPERATOR-001/contract.md`
- `experiments/EXP-ECDLP-TT-SHARED-SIGN-OPERATOR-001/specification.json`
- `experiments/EXP-ECDLP-TT-SHARED-SIGN-OPERATOR-001/src/shared_sign_locator.py`
- `experiments/EXP-ECDLP-TT-SHARED-SIGN-OPERATOR-001/runs/RUN-TT-SHARED-SIGN-OPERATOR-002/`
- `experiments/EXP-ECDLP-TT-SHARED-SIGN-OPERATOR-001/runs/RUN-TT-SHARED-SIGN-OPERATOR-003/`

## Interpretation

The result supports a narrow practical hypothesis: source-state arithmetic can share an inversion across the two signs of an elliptic negation orbit while preserving exact witnesses. The clearest improvement is in the inversion component, not in total charged work. The one strict sub-full signal on both curves is encouraging enough to justify a differential/projective successor, but it is not evidence of a generic-prime-field ECDLP improvement or a faster-than-rho algorithm.
