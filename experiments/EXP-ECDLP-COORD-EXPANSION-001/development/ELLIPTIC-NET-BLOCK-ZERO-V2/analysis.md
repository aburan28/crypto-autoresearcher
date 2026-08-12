# Elliptic-Net Block-Zero V2 Analysis

## Status

`NEGATIVE RESULT`, `TOY-EVIDENCE`, `MODEL-BOUND`.

This is a scoped negative for affine-normalized locator sequences, the four
tested coordinate families, the fixed left-associated RCB tree, and the
`L=8B` progression schedule. It is not a negative result for all elliptic
net constructions, alternate addition trees, target-parametric selectors,
batch decomposition, or prime-field ECDLP.

## Hypothesis

Removing projective scale before forming the zero locator would expose a
shared low-order recurrence or sibling annihilator along `P0+iD` for at least
one coordinate-defined factor base.

The normalized locator is

`(x-x_Q)^2 - nu*(y-y_Q)^2`

after affine conversion, with fixed nonsquare `nu`; the point at infinity is
mapped to the nonzero sentinel `1`.

## Exact Run

- source commit: `fda7219af4850eaddf2f3a9c4b020342858beaf9`;
- curves: three generated prime-order curves at 10, 12, and 14 bits;
- families: random-x, source-PRF-x, x-interval, rational-union;
- rows: 12;
- progression length: `L=8B`;
- exact canonical four-term `R` tuples;
- producer wall time/RSS: `22.48` seconds / `43,008,000` bytes;
- verifier wall time/RSS: `22.32` seconds / `43,892,736` bytes.

The producer launched from a clean committed tree. The verifier reran the
normalized wrapper against the untouched raw result.

## Controls And Verification

All controls pass:

- planted order-four linear recurrence with held-out continuation;
- elliptic divisibility Ward and Somos-4 identities;
- deterministic random sequence rejects exact Somos-4;
- every source zero set and planted descent replays exactly;
- all 24 permutations of the four `R` inputs agree in affine output and
  normalized locator value on each of the three curves;
- four nonzero projective rescalings agree in normalized locator value on each
  curve.

The independent verifier reports `valid=true`, exact normalized rerun digest
`7e99e50edf9a11a80c76c9fd3aceb04be7da9bc379201da5b28e35bdd5a6b7b8`, and
rejects all six registered mutations: protocol, base-generator hash,
normalization mode, normalization-control flag, promotion flag, and semantic
row.

## Candidate Result

No row has `recurrence_signal=true`, and no family is promoted. For every
family, progression and matched-random planted-root BM orders are identical
at the three tested sizes:

| Family | Progression root BM orders | Matched random root BM orders | Signal rows |
|---|---|---|---:|
| random-x | `20,32,40` | `20,32,40` | 0/3 |
| source-PRF-x | `20,32,40` | `20,32,40` | 0/3 |
| x-interval | `20,32,40` | `20,32,40` | 0/3 |
| rational-union | `20,32,40` | `20,32,40` | 0/3 |

The normalized recurrence gate is false. The largest explicit tree state is
approximately `362.8` field elements per `B^2.5` unit in the recorded rows;
the run remains an enumerative diagnostic and does not construct an implicit
state.

## Charged Work

For each of progression and matched-random variants, the producer records:

- `1,297,920` RCB calls;
- `648,960` locator evaluations;
- `1,303,488` materialized tree field elements;
- `647,488` block-product field multiplications.

The two variants use the same source volume. No advice structure, arbitrary
target query, relation matrix, or target descent compiler was produced.

## Strongest Valid Conclusion

Affine normalization removes the tested projective-scale dependence, but it
does not expose a shared low-order recurrence or sibling recurrence in the
four tested coordinate families on these three generated curves. The raw V1
gauge artifact was a real implementation concern; fixing it does not create
the desired implicit state.

## Next Positive Question

The remaining constructive directions are target-parametric rather than
single-sequence recurrence fitting: test a compact transposed operator or a
nonlinear composition-tower selector that shares state across many target
locators while charging construction, memory, witness descent, and relation
rank. Keep explicit tree materialization as the baseline and do not promote a
recurrence diagnostic into an ECDLP algorithm.
