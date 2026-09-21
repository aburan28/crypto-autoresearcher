# Target-Parametric Norm Operator V1: RUN-001

## Result

`SCOPED NEGATIVE` for source-rank compression, with an exact batch
linearization observation.

The affine norm locator was reconstructed from five target-independent source
features: `1`, `x`, `y`, `x^2-nu*y^2`, and an infinity indicator. The three
target coefficients had exact rank 3 over every tested curve. All 36 target
specializations reconstructed the direct affine norm exactly, and all 12
weighted transpose identities matched entry by entry.

The run covered 12 cells over three generated ordinary prime-field curves and
four coordinate families. It enumerated 555,804 ordered source entries and
charged 2,779,020 point-add calls, 2,222,934 field inversions, and 8,891,736
counted field multiplications. Producer wall time was 12.66 seconds with
peak RSS 95,322,112 bytes. Independent verifier wall time was 12.78 seconds
with peak RSS 94,142,464 bytes.

## Rank behavior

The nonconstant finite-source features `x`, `y`, and `norm_source` had the
same central cut-2 ranks as the direct norm census on every row: 30, 34, 35,
48, or 110 according to the recorded dimensions. The constant feature had
rank one. The infinity indicator had rank zero on this source schedule
because no ordered five-source output was the identity.

Thus the target coefficient dimension is small, but the source-side feature
tensors do not show a new low-rank compression. The identity removes repeated
target-dependent field arithmetic after source outputs are already available;
it does not remove the `A+4R` source construction, exact zero testing, source
witness recovery, matrix rank, or target descent.

## Verification

The independent verifier reports `valid=true`, exact normalized replay, all
36 direct reconstructions true, all 12 transpose checks true, and five of five
mutations rejected. Infinity is handled by a separate target-independent
feature, so the affine sentinel is not silently folded into the finite
quadratic formula.

## Interpretation

This is a reusable constant-factor batch identity and a clean negative for
the hypothesis that target-parametric linearization alone creates a compact
source operator. It is not an ECDLP improvement, fixed-curve preprocessing
result, relation compiler, zero finder, or deployed-key result.

The next positive direction must change the object being compressed: a
nonlinear target selector, a quotient state with exact witness lift, or a
transposed operator that acts before source-tensor materialization. Any such
successor must charge construction, traffic, zero support, rank, and descent
against the same typed five-term baseline.

## Evidence hashes

- contract: `4f53ef0aa2ae3574cdb9a225f56473bc2218f23f8d2e5aa99a70484e77083cfe`
- producer: `2655f6b42fbb2950999d433efe798f5cd53e553d8ee1562f31786abef1adc0f1`
- verifier: `fa9fcd55dbd4b7d55a41addcade3c1407d9f50efe4e00da9d09db533bfe9804b`
- immutable input: `c7476f8aeff640ea2690c70218252186a8c657bf1d6db76baa01c55e2289fa3c`
- raw result: `0db430f4a7854921522d9d4cd3f5c147f4bf7b996dbf266fafa924e592558c45`
- verification: `e89d81cd45286b01d791c54c131d2a39d09a9b191a9f5943fc42964168740010`
- producer stderr: `9d147df2628d152c53d223579377e245d22f4b0dbde7c4e8d06295e7916add64`
- verifier stderr: `65b5ebcdafa516c077304c190d2c9a76b552e217f0324b1acf92790304d535b4`
