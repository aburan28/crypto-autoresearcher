# Experiment Contract: Typed Raw Circuit-TT Preflight V1

## Hypothesis

Wrapping the frozen five-source RCB addition circuit in an exact TT using
direct-sum addition and Kronecker pointwise multiplication may provide a
non-enumerative source representation with manageable bond ranks.

This is a construction preflight. It measures the raw exact TT closure before
any rank truncation or basis compression; it does not claim that the raw
closure is minimal.

## Null Hypotheses

1. Direct-sum/Kronecker closure produces bond ranks that grow too quickly to
   support fixed-curve advice or target queries.
2. The raw TT wrapper only hides the same source-tensor bottleneck behind a
   larger representation.
3. Any useful successor must perform a nontrivial exact compression step whose
   cost is not represented by this raw closure.

## Parameters

- input: immutable `TYPED-FIVE-EC-V1/raw-result.json`;
- all three generated ordinary prime-field curves and four coordinate
  families;
- source modes `[A,R,R,R,R]` with the recorded `B=|R|`;
- four left-associated complete RCB additions;
- exact TT shape rules:
  - tensor addition uses direct-sum bonds;
  - pointwise multiplication uses Kronecker bonds;
  - scalar multiplication leaves bonds unchanged;
- first norm locator uses `h=e_X^2-nu*e_Y^2` and the same raw TT rules;
- no `B^5` tuple enumeration and no numerical rank truncation.

## Metrics

- TT bond ranks after each RCB stage and after the norm;
- exact raw core-entry counts and peak raw advice words;
- closure addition/multiplication counts;
- ratios to `B^5`, `sqrt(q)`, and the typed materialized-D4 payload;
- source/input/protocol hashes, wall time, and peak RSS.

## Positive Controls

- rank-one source coordinates remain rank-one under scalar operations;
- direct-sum and Kronecker shape laws satisfy their small synthetic tensor
  controls;
- the stage schedule is deterministic and independent of target labels;
- no enumerated source tuple is present in the producer path.

## Success Criterion

A raw-closure signal would require all registered rows to retain a maximum
bond and raw core-entry count below the fixed-curve advice frontier. This
preflight does not authorize an attack or a rank-truncation implementation.

## Falsification Criteria

- any shape/control or independent replay mismatch;
- raw bond ranks exceed a declared implementation ceiling;
- raw core entries exceed `B^5`-scale state or the fixed-curve advice target;
- the result depends on enumerating source tuples.

Failure is scoped to the direct-sum/Kronecker circuit closure. It does not
rule out exact TT rounding, common polynomial bases, nonlinear quotient states,
or implicit transposed operators.

## Reproduction Command

```bash
python3 src/typed_raw_circuit_tt_preflight.py \
  development/TYPED-FIVE-EC-V1/raw-result.json \
  --families random_x source_prf_x x_interval rational_union
```
