# Experiment Contract: EXP-ECDLP-TT-SOURCE-ORBIT-REPLICATION-001

## Hypothesis

Suffix pairs whose source-only sums share a large elliptic-negation orbit are
more useful for typed five-term relation localization than uniformly ranked
suffix pairs. A fixed orbit-multiplicity order should preserve the strict
64/100 relation gate on two fresh ordinary 14-bit prime-field curves.

## Null hypothesis

Source pair-sum orbit multiplicity is not predictive of typed relation support:
the fixed order fails exact support, held-out coverage, or quotient rank on at
least one fresh curve, or its charged construction cost removes the reduction.

## Parameters

- seeds: `271828`, `161803`;
- field size: 14 bits, one fresh curve per seed;
- families: `random_x`, `source_prf_x`, `x_interval`, `rational_union`;
- budgets: `32`, `64`, `full` suffix columns out of `B^2`;
- primary selector: descending multiplicity of the affine x-coordinate among
  source pair sums, then diagonal pairs first, then index distance, x, y, and
  original index;
- controls: full exact replay, matched rho, and the committed uniform and
  pair-sum-x fresh replications;
- baseline: materialized typed D4 support, held-out targets, quotient rank, and
  direct witness certificates.

## Source-only boundary

The selector sees only the public curve, factor-base points, and source-only
pair sums. It does not inspect target coordinates, target scalars, relation
transcripts, support sets, or held-out labels. Pair-sum construction is charged
separately.

## Success criterion

The fixed orbit-multiplicity selector has an accepted strict sub-full budget on
both fresh curves, with exact support, held-out coverage, valid witnesses, full
quotient rank, and declared selector/source/reconstruction costs recorded.

## Falsification criterion

Either full control fails, or the primary selector has no accepted strict
sub-full budget on either fresh curve, or charged selector construction removes
the claimed reduction.

## Boundary

This is toy-scale fixed-curve representation evidence. It does not claim a
generic ECDLP break, an exponent improvement, deployed-key recovery, or
superiority to Pollard rho at cryptographic sizes.

