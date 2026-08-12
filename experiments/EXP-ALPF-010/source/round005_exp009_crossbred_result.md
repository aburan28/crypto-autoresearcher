# EXP-009 Result: crossbred / XL-with-cutoff for m=3 prime-field Semaev

SEED=42  timestamp=2026-05-30 23:13:13  sage=SageMath version 10.9, Release Date: 2026-05-04

## Meter re-validation (round-005 kernel/nontrivial-syzygy meter)

| control | d_ff | D_reg | early_fall | role |
|---|---|---|---|---|
| POS-A 3 cubics shared quadratic factor | 4 | 7 | True | must fire |
| NEG-1 3 generic quadrics (regular CI) | 4 | 4 | False | must be quiet |
| NEG-2 3 generic cubics (regular) | 7 | 7 | False | must be quiet |

**METER VALIDATED: True**

## Cost table: crossbred(best d_1) vs F4 vs rho (FIELD-OP-EQUIVALENT)

rho field ops use 8 field-mults/group-op (conversion most favorable to rho);
F4 ops = ncols(D_solve)^2.37 proxy. cb ops = Macaulay build + exact RREF + guess.

| curve | |FB| | tr | D_reg | d_ff | early | best d_1 | cb ops | n_ver(cb) | F4 ops | n_ver(F4) | rho ops(8M) | cb<F4? | cb/rho | appr rho? |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| structured/13b | 3 | 0 | 7 | 7 | False | 3 | 2.59e+03 | 1 | 8.47e+04 | 1 | 323 | True | 8.02 | True |
| structured/13b | 3 | 1 | 7 | 7 | False | 3 | 2.59e+03 | 1 | 8.47e+04 | 1 | 323 | True | 8.02 | True |
| structured/13b | 4 | 0 | 10 | 10 | False | 4 | 5.43e+03 | 1 | 6.63e+05 | 1 | 323 | True | 16.8 | False |
| structured/13b | 4 | 1 | 10 | 10 | False | 4 | 5.43e+03 | 1 | 6.63e+05 | 1 | 323 | True | 16.8 | False |
| structured/13b | 5 | 0 | 12 | 12 | False | 5 | 9.8e+03 | 1 | 1.99e+06 | 1 | 323 | True | 30.3 | False |
| structured/13b | 5 | 1 | 12 | 12 | False | 5 | 9.8e+03 | 1 | 1.99e+06 | 1 | 323 | True | 30.3 | False |
| structured/15b | 3 | 0 | 7 | 7 | False | 3 | 2.59e+03 | 1 | 8.47e+04 | 1 | 638 | True | 4.06 | True |
| structured/15b | 3 | 1 | 7 | 7 | False | 3 | 2.59e+03 | 1 | 8.47e+04 | 1 | 638 | True | 4.06 | True |
| structured/15b | 4 | 0 | 10 | 10 | False | 4 | 5.43e+03 | 1 | 6.63e+05 | 1 | 638 | True | 8.52 | True |
| structured/15b | 4 | 1 | 10 | 10 | False | 4 | 5.43e+03 | 1 | 6.63e+05 | 1 | 638 | True | 8.52 | True |
| structured/15b | 5 | 0 | 12 | 12 | False | 5 | 9.8e+03 | 1 | 1.99e+06 | 1 | 638 | True | 15.4 | False |
| structured/15b | 5 | 1 | 12 | 12 | False | 5 | 9.8e+03 | 1 | 1.99e+06 | 1 | 638 | True | 15.4 | False |
| structured/17b | 3 | 0 | 7 | 7 | False | 3 | 2.59e+03 | 1 | 8.47e+04 | 1 | 1.29e+03 | True | 2.01 | True |
| structured/17b | 3 | 1 | 7 | 7 | False | 3 | 2.59e+03 | 1 | 8.47e+04 | 1 | 1.29e+03 | True | 2.01 | True |
| structured/17b | 4 | 0 | 10 | 10 | False | 4 | 5.43e+03 | 1 | 6.63e+05 | 1 | 1.29e+03 | True | 4.22 | True |
| structured/17b | 4 | 1 | 10 | 10 | False | 4 | 5.43e+03 | 1 | 6.63e+05 | 1 | 1.29e+03 | True | 4.22 | True |
| structured/17b | 5 | 0 | 12 | 12 | False | 5 | 9.8e+03 | 1 | 1.99e+06 | 1 | 1.29e+03 | True | 7.61 | True |
| structured/17b | 5 | 1 | 12 | 12 | False | 5 | 9.8e+03 | 1 | 1.99e+06 | 1 | 1.29e+03 | True | 7.61 | True |
| structured/19b | 3 | 0 | 7 | 7 | False | 3 | 2.59e+03 | 1 | 8.47e+04 | 1 | 2.57e+03 | True | 1.01 | True |
| structured/19b | 3 | 1 | 7 | 7 | False | 3 | 2.59e+03 | 1 | 8.47e+04 | 1 | 2.57e+03 | True | 1.01 | True |
| structured/19b | 4 | 0 | 10 | 10 | False | 4 | 5.43e+03 | 1 | 6.63e+05 | 1 | 2.57e+03 | True | 2.12 | True |
| structured/19b | 4 | 1 | 10 | 10 | False | 4 | 5.43e+03 | 1 | 6.63e+05 | 1 | 2.57e+03 | True | 2.12 | True |
| structured/19b | 5 | 0 | 12 | 12 | False | 5 | 9.8e+03 | 1 | 1.99e+06 | 1 | 2.57e+03 | True | 3.82 | True |
| structured/19b | 5 | 1 | 12 | 12 | False | 5 | 9.8e+03 | 1 | 1.99e+06 | 1 | 2.57e+03 | True | 3.82 | True |
| random/13b | 3 | 0 | 7 | 7 | False | 3 | 2.59e+03 | 1 | 8.47e+04 | 1 | 435 | True | 5.96 | True |
| random/13b | 3 | 1 | 7 | 7 | False | 3 | 2.59e+03 | 1 | 8.47e+04 | 1 | 435 | True | 5.96 | True |
| random/13b | 4 | 0 | 10 | 10 | False | 4 | 5.43e+03 | 1 | 6.63e+05 | 1 | 435 | True | 12.5 | False |
| random/13b | 4 | 1 | 10 | 10 | False | 4 | 5.43e+03 | 1 | 6.63e+05 | 1 | 435 | True | 12.5 | False |
| random/13b | 5 | 0 | 12 | 12 | False | 5 | 9.8e+03 | 1 | 1.99e+06 | 1 | 435 | True | 22.5 | False |
| random/13b | 5 | 1 | 12 | 12 | False | 5 | 9.8e+03 | 1 | 1.99e+06 | 1 | 435 | True | 22.5 | False |
| random/15b | 3 | 0 | 7 | 7 | False | 3 | 2.59e+03 | 1 | 8.47e+04 | 1 | 823 | True | 3.15 | True |
| random/15b | 3 | 1 | 7 | 7 | False | 3 | 2.59e+03 | 1 | 8.47e+04 | 1 | 823 | True | 3.15 | True |
| random/15b | 4 | 0 | 10 | 10 | False | 4 | 5.43e+03 | 1 | 6.63e+05 | 1 | 823 | True | 6.6 | True |
| random/15b | 4 | 1 | 10 | 10 | False | 4 | 5.43e+03 | 1 | 6.63e+05 | 1 | 823 | True | 6.6 | True |
| random/15b | 5 | 0 | 12 | 12 | False | 5 | 9.8e+03 | 1 | 1.99e+06 | 1 | 823 | True | 11.9 | False |
| random/15b | 5 | 1 | 12 | 12 | False | 5 | 9.8e+03 | 1 | 1.99e+06 | 1 | 823 | True | 11.9 | False |
| random/17b | 3 | 0 | 7 | 7 | False | 3 | 2.59e+03 | 1 | 8.47e+04 | 1 | 1.75e+03 | True | 1.48 | True |
| random/17b | 3 | 1 | 7 | 7 | False | 3 | 2.59e+03 | 1 | 8.47e+04 | 1 | 1.75e+03 | True | 1.48 | True |
| random/17b | 4 | 0 | 10 | 10 | False | 4 | 5.43e+03 | 1 | 6.63e+05 | 1 | 1.75e+03 | True | 3.1 | True |
| random/17b | 4 | 1 | 10 | 10 | False | 4 | 5.43e+03 | 1 | 6.63e+05 | 1 | 1.75e+03 | True | 3.1 | True |
| random/17b | 5 | 0 | 12 | 12 | False | 5 | 9.8e+03 | 1 | 1.99e+06 | 1 | 1.75e+03 | True | 5.59 | True |
| random/17b | 5 | 1 | 12 | 12 | False | 5 | 9.8e+03 | 1 | 1.99e+06 | 1 | 1.75e+03 | True | 5.59 | True |
| random/19b | 3 | 0 | 7 | 7 | False | 3 | 2.59e+03 | 1 | 8.47e+04 | 1 | 3.36e+03 | True | 0.773 | True |
| random/19b | 3 | 1 | 7 | 7 | False | 3 | 2.59e+03 | 1 | 8.47e+04 | 1 | 3.36e+03 | True | 0.773 | True |
| random/19b | 4 | 0 | 10 | 10 | False | 4 | 5.43e+03 | 1 | 6.63e+05 | 1 | 3.36e+03 | True | 1.62 | True |
| random/19b | 4 | 1 | 10 | 10 | False | 4 | 5.43e+03 | 1 | 6.63e+05 | 1 | 3.36e+03 | True | 1.62 | True |
| random/19b | 5 | 0 | 12 | 12 | False | 5 | 9.8e+03 | 1 | 1.99e+06 | 1 | 3.36e+03 | True | 2.92 | True |
| random/19b | 5 | 1 | 12 | 12 | False | 5 | 9.8e+03 | 1 | 1.99e+06 | 1 | 3.36e+03 | True | 2.92 | True |

## Crossover-vs-size trend (cb/rho by bit size, where cb solved)

| bits | median cb/rho | n_cells |
|---|---|---|
| 13 | 16.8 | 12 |
| 15 | 8.52 | 12 |
| 17 | 4.22 | 12 |
| 19 | 2.12 | 12 |

Gap-to-rho trend: SHRINKING with size -> investigate

## Controls outcome

- Returned crossbred decompositions VERIFIED correct (FB-sum = +/- P): YES >=1 verified
- Crossbred beat F4 (field-op proxy) in >=1 cell: True
- Meter validated: True

## AUTO-VERDICT (raw, BEFORE red-team)

POTENTIAL SURVIVOR -- crossbred field-op cost within 10x of rho on >=1 verified cell.

## RED-TEAM CORRECTION -- the auto-verdict is a MEASUREMENT ARTIFACT (FAILED)

The "potential survivor" / "shrinking gap" signal is an APPLES-vs-ORANGES baseline
mismatch, NOT a real advantage. This is exactly the campaign's recurring integrity
trap (a control that cannot fail). Four independent tells, all visible in the table:

1. BASELINE MISMATCH (the killer). The crossbred field-op number is the cost of
   re-discovering ONE PLANTED decomposition of ONE point, where the FB-guess only
   searches |FB| in {3,4,5} values and the planted triple is GUARANTEED present.
   The number does NOT include: (a) generating ~|FB| INDEPENDENT relations to fill
   the relation matrix; (b) the relation-search FAILURE PROBABILITY -- a RANDOM
   point's x decomposes over a size-(3..5) FB with probability ~ |FB|^3/(3! * p)
   ~ 5^3/6/p ~ 2e-5 at p~10^6 and ->0 as p grows, so honest relation generation
   costs ~ p/|FB|^3 trials PER relation (this dominates and is p-dependent);
   (c) sparse linear algebra over the |FB| x |FB| relation matrix; (d) individual
   logarithm / target descent. rho's number solves the FULL DLP (sqrt(n)) and
   recovers the actual scalar k. The two costs are not comparable.

2. CROSSBRED COST IS INDEPENDENT OF p. cb ops = 2592 / 5433 / 9798 for |FB| =
   3 / 4 / 5 at EVERY bit size (13..19). A genuine ECDLP attack's cost MUST grow
   with p. A cost that is flat in p is the signature of solving a p-independent
   toy (find a known triple among |FB| options), not the DLP.

3. THE "SHRINKING GAP" IS MECHANICAL. cb/rho = const / sqrt(p), so it shrinks by
   construction as p grows -- and would "cross" rho at large p purely because the
   numerator is fixed. Extrapolating it is meaningless: it measures "constant
   beats sqrt(p)", which is true of any p-independent constant, including 1.

4. d_ff = D_reg ON EVERY SEMAEV CELL (early_fall=False, 48/48). With the NOW-
   VALIDATED kernel/nontrivial-syzygy meter (POS-A fires d_ff=4<7, negatives
   quiet), the prime-field m=3 Semaev+FB system shows NO early fall: d_ff equals
   the semiregular D_reg (7/10/12 for |FB|=3/4/5). So there is NO first-fall
   loophole for crossbred to exploit here -- the very quantity that would let
   crossbred beat Yokoyama's D_reg is absent. The crossbred "win" came entirely
   from the FB-guess shortcut on a planted instance, not from any algebraic fall.

CORRECTED VERDICT: FAILED. Crossbred/XL with FB-restricted guessing does NOT
provide a rho-competitive prime-field attack. The apparent advantage is a
planted-relation + wrong-baseline artifact; the real bottleneck (relation
generation probability ~|FB|^3/p, plus linear algebra and descent) was not
measured and is p-dependent and prohibitive. The honest algebraic finding is the
NEGATIVE one: with a validated meter, m=3 prime-field Semaev has d_ff = D_reg (no
early fall), so the crossbred/XL loophole over Yokoyama is CLOSED at these
parameters for this representation.

## What this rules out / does not rule out

- Rules out (scoped, toy 13-19 bit, m=3, x-ring FB): an EARLY FALL (d_ff < D_reg)
  in the prime-field Semaev+FB system under the VALIDATED kernel/nontrivial-syzygy
  meter -- 48/48 cells show d_ff = D_reg. Since crossbred/XL's only advantage over
  F4/Yokoyama is a first fall, this closes the crossbred loophole FOR THIS
  REPRESENTATION at these sizes. (Independent of Yokoyama: measured, not derived.)
- Rules out (scoped): the naive "crossbred beats rho" reading -- shown to be a
  planted-relation + apples-vs-oranges artifact (cost flat in p).
- Does NOT rule out: (a) an early fall in a DIFFERENT representation -- e-ring /
  power-sum / rational-map pullback / trace-norm-subfield FB -- run each through
  the validated meter; the binary FPPR/Petit-Quisquater setting DOES early-fall
  (POS-C Weil-S3 fired d_ff=5<6), so the question is whether any PRIME-field
  re-coordinatization can too; (b) m>=4 where the FB is larger; (c) a HONEST
  end-to-end IC cost (relation gen at true probability + sparse LA + descent)
  being below rho -- not measured here and expected far above rho.

## Next

1. Conservative (fix the baseline): re-instrument so the crossbred "cost" includes
   honest relation generation (random points, true decomposition probability
   ~|FB|^3/p, count trials-to-relation) + ~|FB| relations + sparse linear algebra
   + target descent; compare THAT end-to-end cost to rho. Prediction: dominated by
   relation gen, far above rho, GROWING with p (the artifact disappears).
2. Representation-changing: run the validated meter on e-ring / power-sum /
   rational-map-pullback / trace-norm-subfield Semaev systems to hunt a PRIME-field
   d_ff < D_reg (the only thing that would give crossbred a real edge).
3. High-risk: build the binary FPPR positive at l>=3 (where POS-C-style falls are
   documented) and test whether the fall mechanism can be transported to a prime
   field via Weil restriction of a quadratic-twist / subfield structure.
