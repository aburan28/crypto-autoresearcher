# Experiment Contract: Target-Parametric Norm Operator V1

## Hypothesis

The affine norm locator can be linearized in a fixed, target-independent
source feature basis:

`h_T(Q) = (x(Q)-x(T))^2 - nu (y(Q)-y(T))^2`

`= c_0(T) * 1 + c_1(T) * x(Q) + c_2(T) * y(Q) + c_3(T) * (x(Q)^2 - nu y(Q)^2) + 1_{Q=O}`.

If the four source feature tensors have a materially smaller exact unfolding
rank than the direct locator and the target coefficient batch remains small,
this may identify a target-parametric transposed operator worth compiling.

The identity alone is expected algebra. It is not expected to locate zeros or
solve an ECDLP; those costs are explicit promotion obligations.

## Null Hypotheses

1. The source feature tensors retain the same near-ambient central ranks as
   the direct norm locator on ordinary generated curves.
2. The four-feature representation only removes target-dependent point
   arithmetic and does not reduce source construction, zero-finding, witness
   lift, rank, or target-descent costs.
3. Any apparent gain is a constant-factor batch reuse or a sparse-indicator
   artifact, not a sub-rho relation compiler.

## Parameters

- immutable input: `TYPED-FIVE-EC-V1/raw-result.json`;
- three generated ordinary prime-field curves with `q=953,3919,15583`;
- families: `random_x`, `source_prf_x`, `x_interval`, `rational_union`;
- ordered tensor dimensions `[|A|,B,B,B,B]`;
- target batch: `planted`, `held_out`, `shifted_control`;
- field nonsquare `nu` selected deterministically from `F_p`;
- exact source features: `1`, `x`, `y`, `x^2-nu*y^2`, and an infinity indicator;
- exact modular row rank at cuts 1 through 4;
- deterministic transpose weights `[1,2,3]`.

## Metrics

- rank and digest of each source feature tensor;
- rank of the three-by-four target coefficient matrix;
- exact zero counts and digests for each target specialization;
- weighted transpose identity and digest;
- point additions, field inversions, field multiplications, tensor entries,
  target specializations, wall time, and peak RSS.

## Positive Controls

- affine norm reconstruction agrees with direct target specialization;
- weighted transpose equals direct weighted target evaluation entry by entry;
- the all-one feature has rank one at every cut;
- producer and independent verifier use separate affine addition and rank
  implementations;
- verifier mutations fail closed.

## Promotion Gate

No promotion is authorized by this experiment. A future operator successor
would additionally need a constructible source representation, target query
work and traffic below the matched generic baseline, exact zero recovery,
witness descent, relation rank, and all fixed-curve offline advice charged.

## Falsification Criteria

- any reconstruction, transpose, source accounting, or replay mismatch;
- all nonconstant source feature ranks remain near their ambient limits;
- the only reduction is the expected four-dimensional target coefficient
  identity;
- no representation of exact zero support or witnesses is produced.

Failure is scoped to this affine feature linearization. It does not rule out
nonlinear target operators, alternate addition trees, quotient states, or
source-parametric selectors.

## Reproduction Commands

```bash
python3 src/target_parametric_norm_operator.py \
  development/TYPED-FIVE-EC-V1/raw-result.json \
  --families random_x source_prf_x x_interval rational_union

python3 src/verify_target_parametric_norm_operator.py \
  /path/to/raw-result.json
```
