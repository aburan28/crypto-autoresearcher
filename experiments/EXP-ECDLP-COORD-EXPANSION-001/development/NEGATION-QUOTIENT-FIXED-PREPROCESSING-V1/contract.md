# Experiment Contract: Negation-Quotient Fixed Preprocessing V1

## Hypothesis

For a fixed curve and coordinate factor base, exact `D3` advice can be
quotiented by elliptic negation: store an x-coordinate and a one-bit sign
mask instead of a full affine point key. The resulting index should preserve
all `A+R+D3` witnesses while reducing logical advice words, with online work
reported separately from the stronger materialized `D4` baseline.

This is a concrete fixed-curve preprocessing improvement candidate. It is
not expected to change the asymptotic exponent by itself.

## Null Hypotheses

1. The x/sign quotient loses exact witnesses or changes target support.
2. Advice savings disappear once witness records and sign metadata are
   charged.
3. The online `A+R+D3` join remains above the intended one-target frontier.

## Parameters

- immutable input: `TYPED-FIVE-EC-V1/raw-result.json`;
- three generated ordinary prime-order curves, four coordinate families;
- exact nondecreasing D3 and D4 source tuples;
- target batch: planted, held-out, and shifted-control targets;
- candidate: x-coordinate plus deterministic elliptic-negation sign bit for
  D3 states;
- baselines: full point-keyed D3 and materialized point-keyed D4;
- all returned witnesses are canonicalized and replayed as four R indices.

## Metrics

- D3/D4 support, all witness records, state and witness digests;
- logical key field elements, sign bits, witness-index words, and total
  logical advice words;
- point additions, inversions, multiplications, lookups, candidate witnesses,
  successful targets, and exact hit sets;
- per-target `S*T^2/q` diagnostic, clearly separated from a theorem or attack
  claim;
- producer/verifier wall time, peak RSS, and exact hashes.

## Controls

- full point-keyed D3 lookup on the same states;
- materialized D4 lookup on the same curve and target batch;
- exact equality of full-point and x/sign hit sets;
- exact equality of both with materialized D4 hits;
- independent affine addition, quotient lookup, witness replay, and mutation
  rejection.

## Success Boundary

A valid practical signal requires all hit sets to agree, nonzero advice-word
savings after witness payloads, and a separately reported online cost. This
would be a fixed-curve negation-quotient improvement only.

Promotion toward a generic prime-field ECDLP result additionally requires a
constructive exponent improvement, fresh curves and seeds, relation rank,
individual descent, complete offline/online cost, peak memory, supported
target count, and comparison against optimized rho and same-advice generic
preprocessing.

## Falsification

- any witness or hit-set mismatch;
- advice savings vanish after charged witness/sign metadata;
- query work is not improved relative to the point-keyed baseline;
- all advantage is a constant-factor representation effect with no scalable
  successor.

Failure is scoped to this negation quotient and does not rule out other
fixed-curve preprocessing, nonlinear selectors, or target-batched operators.

## Reproduction

```bash
python3 src/negation_quotient_fixed_preprocessing.py \
  development/TYPED-FIVE-EC-V1/raw-result.json \
  --families random_x source_prf_x x_interval rational_union

python3 src/verify_negation_quotient_fixed_preprocessing.py \
  /path/to/raw-result.json
```
