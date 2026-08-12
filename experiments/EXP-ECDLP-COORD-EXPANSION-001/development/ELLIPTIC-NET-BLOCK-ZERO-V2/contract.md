# Experiment Contract: Elliptic-Net Block-Zero V2

## Hypothesis

Affine-normalizing the exact five-addition locator before multiplying dyadic
block leaves removes projective gauge artifacts and exposes a shared,
low-order recurrence or sibling annihilator along the public progression
`P0+iD` for at least one ordinary prime-field coordinate family.

This is a diagnostic hypothesis about a possible implicit state. It is not a
claim that a recurrence automatically gives a sub-rho root finder.

## Null Hypothesis

The normalized locator sequences have the same linear complexity as matched
random progression sequences, no shared sibling recurrence, or no exact
held-out continuation. In that case affine normalization removes a display
artifact but does not produce a usable recursive compiler.

## Model And Parameters

- generated ordinary prime-order curves from the verified typed five-term
  input;
- curve sizes: the existing 10-, 12-, and 14-bit development curves;
- coordinate families: `random_x`, `source_prf_x`, `x_interval`, and
  `rational_union`;
- factor-base sizes and public progression inherited exactly from
  `TYPED-FIVE-EC-V1`;
- canonical four-term `R` tuples;
- progression length `L=8B`;
- normalized locator:
  `(x-x_Q)^2 - nu*(y-y_Q)^2` after affine conversion, with a fixed
  nonsquare `nu`; the infinity value is the nonzero sentinel `1`;
- the base V1 addition and tree code is reused, but the V2 wrapper and
  independent verifier are separately hashed.

## Metrics

- BM order and normalized BM order at every leaf and block level;
- train/held-out recurrence violations;
- exact Somos-4 fits and sibling connection sharing;
- zero counts and exact zero descent for planted and held-out targets;
- affine permutation invariance and normalized projective-rescaling
  invariance;
- source RCB calls, locator evaluations, tree field elements, field
  multiplications, peak memory, and wall time;
- promoted-family count and constructible-implicit-state gate.

## Positive Controls

- planted order-four linear sequences recover with exact held-out terms;
- elliptic divisibility sequences satisfy Ward and Somos-4 identities;
- every planted witness and every normalized zero set replays to the named
  affine target;
- all 24 permutations of four `R` inputs produce the same affine point and
  normalized locator value;
- nonzero projective rescalings produce the same normalized locator value.

## Negative Controls

- deterministic random sequences do not satisfy an exact Somos-4 recurrence;
- matched random `A` sets are analyzed under the same normalized locator and
  tree schedule;
- scalar progression remains diagnostic-only and is not eligible for attack
  promotion.

## Success Criterion

A provisional recurrence signal requires at least three of four coordinate
families to pass on every tested curve, with normalized progression BM order
at most `0.8` times the matched random order, exact held-out continuation,
at least half of sibling pairs sharing a connection, exact semantics, and
successful planted descent.

Even a signal is only an authorization for a separate implicit-state
construction experiment. It is not an ECDLP improvement.

## Falsification Criterion

Any affine or zero-set mismatch, failed control, failed independent replay,
surviving mutation, or absence of a family-wide recurrence signal falsifies
this normalized-recursion hypothesis for the tested schedule. Explicit tree
materialization remains a cost negative even if a recurrence signal appears.

## Reproduction Command

```bash
python3 experiments/EXP-ECDLP-COORD-EXPANSION-001/src/elliptic_net_block_zero_v2.py \
  experiments/EXP-ECDLP-COORD-EXPANSION-001/development/TYPED-FIVE-EC-V1/raw-result.json \
  --families random_x source_prf_x x_interval rational_union \
  --length-multiplier 8
```

Independent verification consumes the resulting raw JSON with
`verify_elliptic_net_block_zero_v2.py` and replays the producer through the
normalized wrapper.
