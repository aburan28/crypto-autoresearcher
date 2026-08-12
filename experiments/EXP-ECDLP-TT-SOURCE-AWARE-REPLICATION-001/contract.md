# Experiment Contract: EXP-ECDLP-TT-SOURCE-AWARE-REPLICATION-001

## Hypothesis

A target-independent suffix schedule ranked by the affine x-coordinate of the
source-only pair sum `R_j + R_k` preserves the typed five-term relation gate at
the 64/100 budget on two fresh ordinary 14-bit prime-field curves.

## Null hypothesis

The p16267 sampled signal is not explained by source-only suffix geometry: the
fixed pair-sum-x schedule fails exact support, held-out coverage, or quotient
rank on at least one fresh curve, or its selector construction cost removes
the measured reduction.

## Parameters

- seeds: `271828`, `161803`;
- field size: 14 bits, one fresh curve per seed;
- families: `random_x`, `source_prf_x`, `x_interval`, `rational_union`;
- budgets: `32`, `64`, `full` suffix columns out of `B^2`;
- primary selector: ascending affine x-coordinate of `R_j + R_k`, with
  infinity last and `(x,y,index)` tie breaking;
- controls: full exact replay and the committed hash-ranked fresh replication
  `EXP-ECDLP-TT-SAMPLED-REPLICATION-001`;
- baseline: materialized typed D4 support, held-out targets, quotient rank, and
  matched toy Pollard-rho certificates.

## Source-only boundary

The selector may inspect only the public curve, factor-base points, and the
source-only suffix pair sums. It may not inspect target coordinates, target
scalars, relation transcripts, support sets, or held-out labels. Pair-sum
construction is charged separately, even though the locator later rebuilds the
same suffix table as part of its advice.

## Success criterion

The primary selector has at least one strict sub-full budget passing exact
projected support, held-out coverage, valid witnesses, and full quotient rank on
both fresh curves, with reduced predicted entries after selector construction
and all declared source/reconstruction costs are reported.

## Falsification criterion

Either full control fails, or the primary selector has no accepted strict
sub-full budget on either fresh curve, or the selector's charged source-only
construction eliminates the claimed reduction.

## Boundary

This is toy-scale, fixed-curve representation evidence. It does not claim a
generic ECDLP break, an exponent improvement, deployed-key recovery, or
superiority to Pollard rho at cryptographic sizes.

