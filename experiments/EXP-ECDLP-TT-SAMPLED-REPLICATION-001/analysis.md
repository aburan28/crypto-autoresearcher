# Analysis: Two-Seed Fresh Sampled Locator Replication

## Status

`NEGATIVE RESULT`, `TOY-EVIDENCE`, `MODEL-BOUND`.

This package tests whether the p16267 sampled typed-TT locator signal survives
two fresh ordinary 14-bit prime-field fixtures. It does not test all possible
selectors, coordinate predicates, factor bases, or fixed-curve compilers.

## Result

The strict replication gate was not met on either fresh curve. For both
`recursive-toy-p15667-a10428-b3105-q15583` (seed `271828`) and
`recursive-toy-p15683-a13370-b621-q15749` (seed `161803`), every strict
sub-full budget failed at least one of projected support, held-out coverage, or
full quotient rank. The accepted sub-full budget map is empty for all four
families on both curves.

The full controls passed on both curves:

- full `B^2` replay was exact;
- full-budget witnesses verified directly;
- all matched toy Pollard-rho targets were solved and directly certified;
- the independent verifier regenerated both fixtures and passed every source,
  digest, support, witness, curve, and rho check.

The generator used 365.927 seconds wall time, 264.358 CPU seconds, and
1,271,349,248 bytes peak RSS. Matched rho used 211,901 group operations across
the two curves.

## Interpretation

This is a scoped negative result for the hash-ranked uniform suffix selector as
a reproducible strict relation gate. It weakens the claim that the p16267
signal is a generic fresh-curve effect. It does not rule out structured,
source-aware, target-independent selectors; non-enumerative circuit
contraction; fixed-curve advice with an explicit preprocessing/online tradeoff;
or a different coordinate relation compiler.

The p16267 positive receipt remains valuable as a positive control and a
fixture-specific signal. The correct next experiment is to compare a
structured selector against the same fresh-curve protocol, with full source
construction, retained advice, bandwidth, rank, descent, and rho costs charged.

## Implementation evidence

The first verifier attempts exposed nondeterministic runner timing fields inside
the generated fixture hash. Those failed receipts are retained as
`RUN-TT-REPLICATION-002` and `RUN-TT-REPLICATION-004`. The generator and
verifier now recursively remove `wall_seconds` and `total_wall_seconds` before
fixture serialization. `RUN-TT-REPLICATION-005` and its independent verifier
`RUN-TT-REPLICATION-006` are hash-stable and valid.

## Reproduction

The immutable generator and verifier commands are recorded in runs `005` and
`006`. The package test asserts their validity and the empty strict accepted
budget map:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m pytest -q \
  experiments/EXP-ECDLP-TT-SAMPLED-REPLICATION-001/tests
```

