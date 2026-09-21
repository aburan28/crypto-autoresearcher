# Experiment Contract: TYPED-TT-CROSS-PREFLIGHT-V1

## Hypothesis

Given an exact-rank budget from the sealed toy factorization oracle, adaptive cross-unfolding queries can recover exact low-rank skeletons of the recursive locator tensor without enumerating all `B^5` source tuples.

## Null hypothesis

The sampled cross columns do not span the requested unfolding ranks, or holdout reconstruction fails often enough that the sampled skeleton is not a useful exact compiler primitive.

## Parameters

- field/curve family: the three frozen ordinary prime-field curves from `TYPED-FIVE-EC-V1`;
- factor-base families: `random_x`, `source_prf_x`, `x_interval`, and `rational_union`;
- rank budget: the exact TT ranks recorded by `TYPED-EXACT-TT-FACTOR-PREFLIGHT-V1`, treated as an explicit pilot input;
- query oracle: direct affine five-source addition and quadratic norm locator, evaluated only at requested index tuples;
- cross method: deterministic seeded random suffix columns, adaptive independent-prefix rows, exact modular skeleton solve;
- holdouts: 64 deterministic unseen matrix entries per cut;
- source tuple enumeration: forbidden; every oracle query is counted and cached.

## Metrics

- unique oracle queries and cache hits;
- affine group operations and field operations;
- cross trials and selected row/column indices;
- exact modular elimination and inversion counts;
- holdout reconstruction mismatches;
- sampled skeleton payload and query-to-full-tensor ratio;
- peak memory and wall time.

## Positive control

Rank-one synthetic tensors must be recovered from one cross column and reconstruct all holdouts exactly.

## Negative control

A requested rank above the true unfolding rank must be rejected by the cross-rank test.

## Success criterion

All 12 rows and all four cuts find the pilot rank budget and pass every holdout with zero mismatches while using fewer unique oracle queries than full tensor entries.

## Falsification criterion

Any rank failure or holdout mismatch falsifies this exact sampled-cross hypothesis for that cell. A pass does not establish a reusable common basis, a non-enumerative TT core chain, a relation generator, or an ECDLP improvement.

## Reproduction command

```bash
PYTHONDONTWRITEBYTECODE=1 python3 src/typed_tt_cross_preflight.py \
  development/TYPED-FIVE-EC-V1/raw-result.json \
  development/TYPED-EXACT-TT-FACTOR-PREFLIGHT-V1/RUN-001/raw-result.json \
  --families random_x source_prf_x x_interval rational_union
```

## Claim boundary

This is a pilot-guided `TOY-EVIDENCE` and `MODEL-BOUND` experiment. The rank oracle is not free in a real attack and is charged as prior diagnostic evidence, not folded into an asymptotic claim.
