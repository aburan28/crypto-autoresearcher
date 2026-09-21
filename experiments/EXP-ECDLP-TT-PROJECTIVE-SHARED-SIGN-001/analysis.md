# Analysis: projective shared-sign source-state operator

## Handoff: homogeneous zero-locator arithmetic

### Claim or task
Test whether a shared-Z Jacobian computation of `P+S` and `P-S` removes generic source inversions while preserving the exact zero support used by the typed relation locator.

### Status
POSITIVE SIGNAL, TOY-EVIDENCE, MODEL-BOUND

### Assumptions
- The three fixtures are fresh deterministic ordinary prime-order curves at approximately 14 bits.
- The locator uses only zero support and row-space reconstruction, not the affine predicate value itself.
- The source state is fixed before targets are evaluated, and every generic source state has nonzero `Z`.
- Field multiplication, inversion, point-addition, cache, lift, rank, and rho counters are reported separately.

### Evidence so far
- Generator `RUN-TT-PROJECTIVE-SHARED-SIGN-001` is `completed_valid`, bound to clean commit `31c65cd95d07d22889bb17bb64c823e948da37cd`; raw-result SHA-256 is `784a30ccac5cae97e8cbc51553776ecfcf6c4cd91c3a25c2a81008febef76dd0`.
- Independent verifier `RUN-TT-PROJECTIVE-SHARED-SIGN-002` is `completed_valid`, bound to clean commit `cda67d9c1991332a63115dbda6e97559355f48b1`; raw-result SHA-256 is `8f4d3c76945e5c4e25ba67145a351f95cb505d8bfca3781031faa84ca3580e2d`.
- All three full budgets have exact support, valid lifted witnesses, and solved matched rho certificates. Total matched rho work is `316,633` group operations.
- The predeclared `source_prf_x` family accepts budget `44` on all three curves; p15667 also accepts budget `32`. Other families and the remaining sub-full budgets are retained as failures.
- The projective identity is exact: each cleared branch predicate is its affine value times `Z^6`, so the paired product is the affine orbit predicate times the source-only nonzero factor `Z^12`. The independent verifier regenerated source states and found no reconstruction, zero-equivalence, or target-dependent-scale mismatch.
- Across the 12 full-budget family/curve cells, charged projective field multiplications range from `17.98M` to `38.28M`, compared with `101.22M-110.35M` for the naive affine orbit quotient and `141.11M-153.95M` for the original affine predicate. Charged projective inversions range from `3,070` to `4,060`, compared with `124,266-136,257` and `112,605-123,239`, respectively.
- Projective point-add calls remain approximately equal to the naive quotient (`123,636-135,216` versus `123,628-135,192`) and are about 10% above the original predicate's `112,300` or `122,500` calls. Projective source-cache memory is `29.85-32.33 MB`, larger than the affine orbit cache because each cached state retains Jacobian coordinates and shared powers.

### Failure modes
- The homogeneous predicate is not numerically equal to the affine predicate. It is equal only up to a source-state column scale, which is safe for zero support and row-space rank but unsafe if later code consumes absolute predicate values.
- Projective predicate multiplication and cache costs are substantial; physical memory bandwidth is not yet measured independently of retained bytes and logical reads.
- The point-add count does not improve, and the projective path does not include a cryptographic-scale factor-base build, sparse linear algebra, individual-log descent, or a full target-cost comparison against rho.
- A stable `source_prf_x` sub-full signal is encouraging but is not a universal coordinate-family result.

### Next concrete action
Run a preregistered weighted cost sensitivity and a larger fresh sweep, starting at 16-bit curves, with source-cache bandwidth and sparse relation-matrix/descent costs included. Preserve the homogeneous locator only if the `source_prf_x` signal survives without using affine predicate values or target-dependent selector tuning.

### Artifact paths
- `experiments/EXP-ECDLP-TT-PROJECTIVE-SHARED-SIGN-001/contract.md`
- `experiments/EXP-ECDLP-TT-PROJECTIVE-SHARED-SIGN-001/specification.json`
- `experiments/EXP-ECDLP-TT-PROJECTIVE-SHARED-SIGN-001/src/projective_shared_sign_locator.py`
- `experiments/EXP-ECDLP-TT-PROJECTIVE-SHARED-SIGN-001/runs/RUN-TT-PROJECTIVE-SHARED-SIGN-001/`
- `experiments/EXP-ECDLP-TT-PROJECTIVE-SHARED-SIGN-001/runs/RUN-TT-PROJECTIVE-SHARED-SIGN-002/`

## Interpretation

This is the strongest result in the shared-sign line so far: the source operator generalizes from two to three fresh curves, preserves the exact zero-locator protocol under independent arithmetic checks, and reduces the reported field-multiplication and inversion components against both affine comparators. It remains a fixed-curve toy relation-locator improvement, not an ECDLP algorithmic exponent result. The next gate is whether the advantage survives larger dimensions and full downstream accounting.
