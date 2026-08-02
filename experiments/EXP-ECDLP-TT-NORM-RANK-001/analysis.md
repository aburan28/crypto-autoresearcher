# TT first-norm rank analysis

## Classification

- Evidence type: `TOY-EVIDENCE`, exact arithmetic, six generated prime-order
  curves over 8-17 bit prime fields.
- Result status: `OBSERVATION` plus independently replayed instances of the
  restricted first-norm theorem.
- Interpretation: `SANITY_ONLY`.
- ECDLP status: no compiler, locator, relation generator, descent, exponent
  estimate, or improvement over rho was produced.

All four frozen development partitions completed valid from clean Git
revisions. These are noncanonical development runs; the draft protocol did not
and could not emit a locked runner receipt.

## Registered runs

| Run | Role | Launch commit | Wall seconds | Peak RSS bytes | Status |
|---|---|---|---:|---:|---|
| `RUN-ECDLP-TT-NORM-GEN-001` | baseline producer | `8cfa9f2` | 16.3073 | 194,674,688 | `completed_valid` |
| `RUN-ECDLP-TT-NORM-VERIFY-001` | independent baseline verifier | `2e5cbc9` | 12.9449 | 189,628,416 | `completed_valid` |
| `RUN-ECDLP-TT-NORM-MUT-GEN-001` | mutation producer | `2db2e78` | 0.3796 | 34,504,704 | `completed_valid` |
| `RUN-ECDLP-TT-NORM-MUT-VERIFY-001` | mutation verifier | `d9c76f3` | 0.2549 | 38,060,032 | `completed_valid` |

The baseline producer emitted 24 source tables, 615,868 source tuples,
2,463,472 RCB calls, 60 semantic cells, 1,539,670 residual/norm evaluations,
288 exact rank jobs, 12 sampled-cohort span jobs, and 18 D2/D3 comparator
jobs. Every frozen schedule check passed and every mismatch counter was zero.
The independent verifier replayed all six curves, all 60 cells, all 288 rank
jobs, and all six controls with zero semantic mismatches or Hilbert violations.

## Exact rank observations

For the `random_unique:Q00` cells, ranks are listed in cut order 1/2/3/4.

| B | `h` | `h^2` | `h^4` | `h^8` |
|---:|---|---|---|---|
| 3 | 3/6/9/3 | 3/6/9/3 | 3/6/9/3 | 3/6/9/3 |
| 4 | 4/10/16/4 | 4/10/16/4 | 4/10/16/4 | 4/10/16/4 |
| 5 | 5/15/24/5 | 5/15/25/5 | 5/15/25/5 | 5/15/25/5 |
| 7 | 7/28/24/7 | 7/28/48/7 | 7/28/49/7 | 7/28/49/7 |
| 8 | 8/36/24/8 | 8/36/48/8 | 8/36/64/8 | 8/36/64/8 |
| 10 | 10/48/24/10 | 10/55/48/10 | 10/55/96/10 | 10/55/100/10 |

The exact `g` and `h` cut ranks agreed on every scheduled Q00 cell. Every
`h` rank was below the ambient-capped Hilbert bound. Projective rescaling
changed homogeneous values but preserved the zero set and ranks exactly.

This is a useful positive signal for the first norm: at the third cut, the
observed `h` rank stabilizes at 24 from `B=5` onward. It is also an immediate
warning for the locator chain: on `B=10`, pure powers grow `24 -> 48 -> 96 ->
100`, reaching the ambient `B^2` ceiling by `h^8`. These toy values neither
prove the asymptotic Hilbert ceilings are tight nor determine mixed
addition-chain ranks.

Every one of the 12 sampled primary target cohorts had span dimension three,
equal to the number of frozen targets. This checks consistency but does not
measure the full target-family dimension. The at-most-five trace-zero source
coefficient statement remains an algebraic theorem, not an empirical
inference from three targets.

## Accounting

Observed rank traffic was 299,838,977 `F_p` words plus 18,262,674 `F_p2`
words. Charging two base-field words per extension coefficient gives
336,364,325 base-field-word equivalents, below the frozen 587,622,372
ceiling. The verifier checked every materialization, pivot-scan, elimination,
normalization, certificate, and extension-conversion identity.

The producer also charged 206,680,675 `F_p` multiplications, 7,108,461
`F_p2` multiplications, and 4,930,604 group additions across all diagnostic
paths. Full `B^5` enumeration is labeled diagnostic and retained as zero bytes
of advice. Online specialization and compiler preprocessing are explicitly
`not_executed`.

There were 720 zero witnesses and 1,538,950 no-hit evaluations. Most witnesses
come from planted permutation controls; this deterministic census is not a
success-probability estimate. The comparator performed 3,612 candidate
additions under its 7,002 upper bound, but no attack-level timing comparison
is authorized.

## Adversarial verification

All 15 frozen mutations were rejected, including wrong RCB constants/gates,
affine substitution, invalid projective output, wrong Frobenius/norm,
rank-field and cut-order changes, target postselection, duplicate factor-base
points, shared verifier code, omitted enumeration/memory accounting, and an
asymptotic breakthrough label.

One nonblocking artifact issue remains: the mutation verifier's
`c08_replay_digest` includes volatile replay accounting and is therefore not a
cross-run reproducibility digest. Mutation detection and every semantic/rank
comparison are unaffected. The digest must be normalized before reuse as a
certificate in a successor protocol.

## Decision

`WEAKEN`: the runs support the degree-preserving first norm, source-span
identity, projective invariance, and frozen rank caps. They do not execute the
hypothesis's constructive source-advice or online-specialization clause.

The immediate obstruction has moved. Existence of a bounded first-norm tensor
is no longer the question; construction of exact source/common-basis TT cores
without dense `B^5` enumeration is now the gate. Even a successful first-norm
compiler would still leave the growing `h^(p-1)` locator chain open.

## Next concrete action

Create a fresh successor contract for an exact coefficient-space/source-TT
compiler for the five nonzero trace-zero source tensors, requiring construction
without `B^5` enumeration, complete work/traffic/advice accounting, exact
replay against this run, and no claim about the Fermat locator.
