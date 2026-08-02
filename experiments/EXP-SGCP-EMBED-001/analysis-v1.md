# SGCP Embedding Canonical Five-Bit Analysis V1

## Status and claim boundary

Status: `OBSERVATION`, `TOY-EVIDENCE`, `MODEL-BOUND`.

The frozen five-bit implementation preflight completed valid. It constructs and
independently verifies a coordinate-compatible injective formal order ideal for
one generated elliptic curve and three factor-base sizes. This is not a scaling
result, a conventional-coordinate lower bound, a relation generator, an index
calculus algorithm, an ECDLP solution, or evidence of an exponent below rho.

## Immutable evidence

- approval commit: `2e01d5bc7385bc3ab135b3a750d0e8ee916e2176`;
- external approval-lock SHA-256:
  `97a2cbf6475229f45a48064a25161402c4f897537d653be4df776784feb7bcbe`;
- generator run: `RUN-SGCP-EMBED-001`, committed at
  `e5a4b9be40c6d700db3fd9f3af2fa6c7690217a9`;
- generator raw-result SHA-256:
  `03e02b7d05db14bd8250b203226d3e336f9eed7933ed8688d0637bcd5d7faf88`;
- verifier run: `RUN-SGCP-EMBED-002`, committed at
  `df256ef`;
- verifier raw-result SHA-256:
  `839a585d6c486a1a800df0dbd313506ba88d5eab20ebff6ab9692b60308d91a3`.

Both runs report `completed_valid`, empty stderr, a clean launch tree, unchanged
protocol and approval bytes, no descendants, and valid runner receipts. The
verifier receipt binds the exact committed generator manifest, runner receipt,
and raw-result hash.

## Canonical result

The curve is `y^2 = x^3 + 2x + 9` over `F_19`; its prime-order group has
`q=23`. The source set is coordinate-defined by the emitted polynomial `L` and
its roots. `P2` is the exact balanced-universe optimizer under forced degree-two
closure.

| B | constrained labels / q | selected degree-4 witnesses | star edges | retained final support / q | public bytes | charged private bytes |
|---:|---:|---:|---:|---:|---:|---:|
| 4 | 20/23 | 5 | 26 | 13/23 | 3,606 | 58,696 |
| 6 | 17/23 | 4 | 20 | 7/23 | 3,402 | 74,293 |
| 8 | 14/23 | 4 | 21 | 7/23 | 3,435 | 106,696 |

Raw four-witness support is `23/23` in every row. The reduction in final
support is therefore caused by the injectivity, associativity, factorization,
acyclicity, source, and final-edge constraints, not by absence of EC sums.

The builder charged, respectively:

| B | field multiplications | point additions | optimizer nodes |
|---:|---:|---:|---:|
| 4 | 549,670 | 261,596 | 4,096 |
| 6 | 35,149 | 17,745 | 256 |
| 8 | 2,619,468 | 1,332,354 | 16,384 |

The nonmonotone work is explained by the exact valid-candidate subset counts;
it cannot support an exponent fit.

## Independent reconstruction

The verifier:

- accepted all 12 registered positive and negative controls;
- independently reconstructed all three coordinate rows with zero errors;
- independently reconstructed the scalar-index optimizer outcomes for all
  three rows;
- matched candidate/valid/conflict/subset counts of
  `31/12/20/4096`, `68/8/4/256`, and `124/14/53/16384`;
- confirmed exact scalar compatibility for `P0` and `P2` where defined;
- did not import or execute the builder and did not share its scalar table;
- made 41,472 exhaustive valid-subset comparisons and 24 scalar ground-truth
  calls.

The verifier explicitly does not claim covert-channel exclusion. Named scalar
fields are absent and diagnostic integers are bounded, but an in-range channel
could still encode information.

## Baseline interpretation

`P0-BALANCED-ONLY` retains `23/23` final support, but fails associativity,
unique factorization, acyclicity, and direct-final-edge exclusion in every row.
It is not a valid structured-group embedding.

`P1-CANONICAL-CLOSURE` retains raw support but does not define an embedding for
any row. Canonical witness selection is therefore not a repair on this fixture.

`P2-BALANCED-UNIVERSE-OPTIMUM` defines a valid coordinate-compatible embedding
with nonzero density and final support. On this curve, validity requires a
substantial support sacrifice. This is a concrete finite-model observation,
not evidence that the sacrifice persists asymptotically or for other coordinate
predicates.

## Decision

The implementation preflight is `GO` for its frozen five-bit scope. The result
supports a fresh family-level experiment, not promotion of the hypothesis.

The next useful test is a separately reviewed multi-curve successor that:

1. samples ordinary prime-order curves and frozen coordinate predicates across
   at least three bit sizes and seeds;
2. proves optimizer optimality or reports an explicit optimality gap;
3. measures conflict-graph expansion, constrained density, absolute retained
   support, and public/private accounting together;
4. compares interval, random-x, rational-map, and matched random constructions;
5. keeps relation generation, matrix rank, target descent, and rho accounting
   as separate gates before any cryptanalytic interpretation.

No larger row is authorized by this analysis.
