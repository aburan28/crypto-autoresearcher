# Negation-Quotient Fixed Preprocessing V1: RUN-001

## Result

`SCOPED NEGATIVE` for an asymptotic fixed-curve improvement, with exact
negation-quotient correctness.

The candidate stores exact `D3` states by x-coordinate plus a one-bit
elliptic-negation sign mask. It was compared with full point-keyed `D3`
advice and materialized point-keyed `D4` advice across 12 curve/family cells
and 36 target queries. All three hit sets agreed on every target, all 36
quotient and D4 checks passed, and 17 of the 36 target queries had nonempty
support in every representation.

The independent verifier replayed all 12 cells exactly and rejected all five
mutations. The producer charged witness replay additions consistently with
the verifier.

## Fixed-curve accounting

After charging witness-index words, x/sign advice saved between 0 and 10
logical words per cell, 24 words total across 12 cells. Five cells had any
positive saving. The online work ratio was exactly `1.0` for x/sign versus
full point-keyed `D3` on every query: the quotient changes representation,
not the complement computation or witness replay.

The materialized `D4` baseline used more advice but had lower online work on
this toy batch. Its tradeoff is reported separately and is not compared as a
generic-group theorem.

Producer accounting:

- D3 build point additions: 4,500;
- D4 build point additions: 17,840;
- 36 target queries;
- producer wall time: 0.60 seconds;
- producer peak RSS: 27,246,592 bytes.

Verifier wall time was 0.10 seconds with peak RSS 28,246,016 bytes.

## Interpretation

The x/sign quotient is an exact fixed-curve representation optimization, but
its savings disappear once witness payloads are charged and it does not
reduce online query work. It is therefore not a breakthrough and does not
establish a faster-than-rho algorithm.

This result is scoped to the negation quotient and the tested D3/D4 advice
surfaces. It does not rule out other fixed-curve preprocessing, nonlinear
target selectors, batch-specific operators, or coordinate-specific relation
compilers.

The next useful direction is a target-conditioned nonlinear complement
operator that changes query work or state exponent, not merely the point-key
encoding.

## Evidence hashes

- contract: `df9238789742202df4130690e834a3c1f7c915fe32f226858572864ff10693e6`
- producer: `53559cbde85cd46413bf1977035bfefe3aaac046cd7e2237322651cc0fc508f9`
- verifier: `3f371a595dbec94465e0064894068c46b7025a17aaf600d2a60a3cf8fc133694`
- immutable input: `c7476f8aeff640ea2690c70218252186a8c657bf1d6db76baa01c55e2289fa3c`
- raw result: `58c0a79bb7ec1b43f6bef1d9584445a094fd55d3fde43d03b4518ddb68fac8bb`
- verification: `2a407090cd1033f549bd68cbab9c89823cda45c61bba851879f866d7b77e27c8`
- producer stderr: `3d8959215a402c7e66b0f27d4553999f8eaf57d36049b74f26f1459b6c3bb59d`
- verifier stderr: `b950d70cc5f52a30d7a0e3e6fb936818e4f94228ac4822e62aaf07e278f2e85a`
