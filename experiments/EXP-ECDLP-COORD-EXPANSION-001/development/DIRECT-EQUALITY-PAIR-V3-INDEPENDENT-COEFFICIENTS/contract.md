# Experiment Contract: Direct Equality Pair V3 Independent Coefficients

## Hypothesis

The V1 suffix coordinate factors at cuts 2 and 3 can be reconstructed by a
second polynomial implementation modulo

`X^3=Y^2 Z-a X Z^2-b Z^3`,

with exact authenticated coefficient chunks, ambient ranks 24/12, and planted
residual-zero witnesses.

This certifies the coefficient-level leaf object only. It is not a
simultaneous-zero index or ECDLP improvement.

## Null Hypotheses

1. Independently reduced suffix coordinates differ from the V1 coefficient
   chunks.
2. The stated homogeneous degree or 24/12 basis is incomplete.
3. Independent evaluation disagrees with affine `A+4R` semantics.
4. Planted witnesses do not give simultaneous zero at both cuts.
5. A coefficient or target mutation is not detected.
6. Independently reduced suffix or specialized residual matrices do not
   reproduce the recorded ranks.

## Parameters

- immutable `TYPED-FIVE-EC-V1/raw-result.json`;
- immutable `DIRECT-EQUALITY-PAIR-V1/raw-result.json`;
- immutable
  `DIRECT-EQUALITY-PAIR-V2-INDEPENDENT-CROSS-TREE/raw-result.json`;
- curves `q=953,3919,15583`;
- random-x, source-PRF-x, x-interval, rational-union;
- every ordered suffix tuple at cuts 2 and 3;
- chunk size 64 suffix tuples;
- degree-8/4 coordinate-ring bases of dimensions 24/12;
- both V1 targets and every V2 first witness.

## Producer

The producer exports:

- the ordered basis;
- per-chunk digests for all three suffix coordinate vectors;
- whole-matrix and target-specialized residual digests;
- coordinate and specialized residual ranks;
- authenticated first/middle/last vector samples;
- planted and held-out first-witness evaluations.

The producer may reuse V1 algebra because its role is evidence export.

## Independent Verifier

The verifier must not import the producer, V1 factor implementation, RCB
implementation, or rank implementation. It supplies its own:

- sparse polynomial arithmetic;
- cubic normal-form reduction;
- complete-addition polynomial circuit;
- coefficient-vector conversion;
- modular Gaussian elimination;
- affine group law and polynomial evaluation.

## Metrics

- suffix tuples and chunks;
- coefficient field elements and nonzeros;
- polynomial additions, multiplications, reductions, and generated terms;
- coordinate and residual ranks;
- chunk, matrix, target, sample, and witness digests;
- planted/held-out zero outcomes;
- coefficient-mutation and target-mutation detection;
- wall time, peak RSS, and artifact bytes.

## Positive Controls

- independent basis dimensions are exactly 24/12;
- every polynomial is homogeneous of degree 8/4 and reduced to `X` degree at
  most 2;
- all independent chunk and whole-matrix digests match;
- V2 planted first witnesses are simultaneous zeros at both cuts;
- evaluated projective coordinates map to the independent affine sum.

## Negative Controls

- changing one authenticated coefficient changes its chunk digest and at
  least one evaluation;
- mutating the planted target destroys the planted simultaneous zero;
- an unreduced `X^3` monomial is rejected by the basis encoder.

## Success Criterion

Every chunk, matrix, specialization, rank, sample, witness, and semantic check
matches under the independent verifier; all positive and negative controls
pass.

Passing certifies the frozen coefficient factors as a development leaf only.

## Falsification Criterion

Any mismatch falsifies coefficient-level certification until explained.
Passing does not prove minimal rank, compression, sub-rho work, relation
yield, or asymptotic behavior.

## Reproduction Command

```bash
python3 src/export_direct_equality_pair_coefficients.py \
  development/TYPED-FIVE-EC-V1/raw-result.json \
  development/DIRECT-EQUALITY-PAIR-V1/raw-result.json \
  development/DIRECT-EQUALITY-PAIR-V2-INDEPENDENT-CROSS-TREE/raw-result.json \
  --families random_x source_prf_x x_interval rational_union \
  --chunk-size 64
```
