# Analysis: source-aware compressed projective locator

## Corrected result

Status: `NEGATIVE RESULT`, `TOY-EVIDENCE`, `MODEL-BOUND` for the first-half
source-prefix selector.

The selector evaluates the first half of the public source-derived diagonal
prefix order and leaves the target and relation transcripts untouched. The
corrected 8-bit smoke on `p=239,q=227` selected `32/64` prefixes and missed
one supported `source_prf_x` relation. The corrected 16-bit run on the fresh
curve `p=62071,q=62137` selected `1372/2744` prefixes and missed four or five
supported relations per family. Full-budget support was therefore not exact:

| family | 8-bit recall | 16-bit recall | 16-bit rank |
|---|---:|---:|---:|
| `source_prf_x` | `0.6765` | `0.4468` | `15/15` |
| `random_x` | `0.5882` | `0.2128` | `13/15` |

The selector retained valid witnesses for every hit and kept the projective
arithmetic counters live. It reduced the candidate's full-budget predicted
entries from the uncompressed `13,541,640` to `6,770,820` at 16 bits and
reduced projective predicate multiplications from `176,041,320` to
`89,893,440`. The weighted arithmetic comparator still won in `2/2` family
cells, but that is a sub-cost result. It does not compensate for missed
relations or establish a relation compiler.

The corrected 16-bit run took `1,978.963` seconds wall time and
`1,480.965` CPU seconds, peaked at `4,426,481,664` bytes RSS, and solved the
matched rho control in `223,916` group operations. The independent verifier
reproduced the negative outcome with `valid=true`, `rank_gate=false`, and
`weighted_gate=true`.

## Receipts

- Corrected 8-bit generator: `RUN-TT-PROJECTIVE-COMPRESSED-LOCATOR-014`, raw
  SHA-256 `2ef6f28204ed5eff8c478b621daa96a8d4e5488e10a775d8d960b06e4f2cf943`.
- Corrected 16-bit generator: `RUN-TT-PROJECTIVE-COMPRESSED-LOCATOR-015`, raw
  SHA-256 `ae7dc67375782cf0c341ac23c375f6d4a8c03e2b6efa6a9041cf83a9063e0e7d`.
- Independent negative verifier: `RUN-TT-PROJECTIVE-COMPRESSED-LOCATOR-017`,
  raw SHA-256 `5e4aa9dd1b5e3018c300fc7966df3de097d42c4cee667a4dafab034a87b63f83`.

## Audit boundary

Runs `009`, `010`, `011`, and `013` are preserved implementation-audit
receipts, not selector evidence. Their first version patched the wrapper
module but not the nested delegated runner, so the actual scan remained
full-prefix despite the half-prefix metadata. Run `012` exposed a verifier
alias defect. The nested binding and the negative-verifier semantics were
fixed before runs `014` through `017`.

## Interpretation

This experiment rules out only the first-half diagonal prefix truncation under
the stated curves and budgets. It does not rule out a stratified, hash-ranked,
or source-geometry-aware selector. The result also shows why rank alone is an
insufficient gate: `source_prf_x` retained rank `15/15` at 16 bits while
losing almost half of the supported relation targets.

## Next positive search

Test target-independent stratified prefix schedules at the same query budget:
interleaved diagonal prefixes, source-hash-ranked prefixes, and a balanced
permutation across the three prefix indices. Each must be compared against the
full oracle on fresh 8-, 12-, and 16-bit curves, with exact support, held-out
coverage, rank, memory, bandwidth, matrix, descent, and rho all charged.

## Claim boundary

No generic prime-field ECDLP break, asymptotic improvement, fixed-curve
preprocessing frontier improvement, or deployed-key recovery is claimed.
