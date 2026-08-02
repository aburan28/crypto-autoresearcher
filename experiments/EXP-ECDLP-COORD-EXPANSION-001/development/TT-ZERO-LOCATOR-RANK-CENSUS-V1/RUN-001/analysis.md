# TT Zero-Locator Rank Census V1: RUN-001

## Result

`NEGATIVE RESULT`, scoped to the exact five-source affine norm-power
unfolding on the registered toy input.

The run covered 36 cells: three generated ordinary prime-field curves, four
coordinate families, and three targets per family. It enumerated 1,667,412
ordered tensor entries and charged 8,337,060 affine point-add calls,
6,668,802 field inversions, and 26,675,208 counted field multiplications.
The producer took 41.69 seconds and reported a peak RSS of 82,509,824 bytes
from `/usr/bin/time -l`.

The independent verifier replayed all 36 cells in 45.09 seconds, with a
peak RSS of 83,673,088 bytes. Replay after removing only timing fields was
exact. All required checks passed and all five mutations were rejected.

## Observed rank behavior

For every family and target, the norm stages `h`, `h2`, `h4`, and `h8` had
the same rank profile. The observed 2-versus-3 ranks were generally 30, 34,
35, 48, or 110, matching the tensor's near-full ambient limit for the
corresponding dimensions. The largest apparent reduction was a one-rank
ambient artifact, not the preregistered `<0.8` signal.

The final zero indicator often had very small rank, but its support was also
small or empty. Its ranks were therefore interpreted only against the
support-matched random binary tensor. This is the expected sparse-indicator
failure mode and does not identify a compact norm or selector operator.

The summary recorded six rows below the strict ambient-limit diagnostic
used by the producer, but none satisfied the contract's 0.8 threshold. The
producer's promotion and breakthrough flags remained false.

## Interpretation

The tested affine normalization and first norm/Hadamard power chain did not
show a cross-curve early unfolding signal strong enough to justify a compact
TT zero-locator construction. This is a negative result for this exact
representation and stage family. It does not rule out nonlinear composition
towers, target-parametric transposed operators, quotient constructions, or
other coordinate-specific relation compilers.

The next positive question is whether a target-parametric transposed
operator can exploit the addition circuit before the norm/indicator chain,
with explicit charged construction and application costs. The next negative
question is whether its middle rank reaches the same near-ambient profile
under an independently frozen operator census.

## Reproduction

```bash
python3 src/tt_zero_locator_rank_census.py \
  development/TYPED-FIVE-EC-V1/raw-result.json \
  --families random_x source_prf_x x_interval rational_union

python3 src/verify_tt_zero_locator_rank_census.py \
  development/TT-ZERO-LOCATOR-RANK-CENSUS-V1/RUN-001/raw-result.json
```

## Evidence hashes

- contract: `e2bdc1c42c46e2bdff788f00467f5226904e23ab1ad1013845c8aa8d6a2f238a`
- producer: `fb5c9ba0d122dcd3cc3220089d3f3863822cc28317a0aa278249e32afac5ad62`
- verifier: `ea1f6bf5d52f97836d5123a419fd32677214201759d2fde1029aadda905e6530`
- immutable input: `c7476f8aeff640ea2690c70218252186a8c657bf1d6db76baa01c55e2289fa3c`
- raw result: `0faeb069b15d32d2e3dc6c83ba64e3b71366a965861fd03e8cf16d39206bd9b1`
- verification: `f8042f43a35ac27fc58996913b49770847c084ee8e75d1c8e8e67ac362cbb799`
- producer stderr: `24d5bd310aa9fee998581244893643bd2c040962db192019cb7a389e170d3361`
- verifier stderr: `536c9553b86de57f231ec9f8ec6af34c31747e7f0775bb6d34ef701682beff9b`
