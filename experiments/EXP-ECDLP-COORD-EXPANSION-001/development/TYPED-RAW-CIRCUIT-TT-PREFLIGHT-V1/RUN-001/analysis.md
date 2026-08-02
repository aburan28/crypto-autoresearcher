# Typed Raw Circuit-TT Preflight V1 Result

## Status

`NEGATIVE RESULT`, scoped to the uncompressed direct-sum/Kronecker TT closure
of the frozen left-associated RCB circuit. The producer is non-enumerative in
source tuples, but the exact raw representation is unusably large before any
target specialization or zero localization.

## Exact Run

- input: immutable `TYPED-FIVE-EC-V1/raw-result.json`;
- curves: `q=953,3919,15583`;
- families: `random_x`, `source_prf_x`, `x_interval`, `rational_union`;
- rows: 12;
- source tuple enumeration: false;
- producer wall time: 0.0039 seconds;
- producer peak RSS: 25,182,208 bytes;
- independent shape replay, producer rerun, and all three mutations: valid.

The producer tracks exact representation sizes under two algebraic TT rules:
addition concatenates bonds, and pointwise multiplication takes Kronecker
products of bonds. No numerical truncation or finite-registry tensor rank is
being substituted for the raw construction.

## Raw Bond Growth

The bond ranks are identical across the registered families because this is a
circuit-shape construction. The maximum bond after each source stage is:

| source stage | maximum raw bond |
|---:|---:|
| 2 sources | `96` |
| 3 sources | `725,760` |
| 4 sources | `40,440,702,173,184` |
| 5 sources | `126,953,775,741,144,031,423,264,456,704` |

The first norm's raw core-entry count ranges from
`1.4128e+113` to `2.8256e+113` logical entries across the registered `B`
values. Relative to the materialized toy `B^5` source universe, the ratio
ranges from approximately `2.83e+114` to `4.52e+115`.

The closure performs 95 TT additions and 50 TT multiplications per row. The
constant-time shape calculation is cheap precisely because it does not
materialize the enormous cores; allocating those cores would fail the fixed-
curve advice and memory gates by many orders of magnitude.

## Interpretation

`NEGATIVE RESULT`: direct-sum/Kronecker closure is not a viable source-TT
compiler for this circuit. It does not establish a lower bound on minimal exact
TT ranks. Exact TT rounding, common polynomial bases, nonlinear quotient
states, and transposed operators remain open.

The result does establish a concrete requirement for any successor: it must
compress intermediate states during or before multiplication, and it must
charge the exact compression work, retained cores, normalization, and witness
path. Naming the raw circuit as a TT does not provide a relation compiler.

## Boundary and Next Action

This is a toy, model-bound construction preflight. It is not a zero finder,
relation generator, ECDLP solver, or exponent improvement. The next positive
track is an exact **rank-truncated or common-basis** source compiler on a small
registered curve, with independent tensor replay and explicit compression
traffic. A finite-rank win must still be compared against the materialized
typed D4 and rho baselines.
