# Result Theory Review

## Handoff: Coordinate expansion arithmetic review

### Claim or task

Verify signed canonical accounting, `D5_new`, split hits, `T_perm`, and the
strongest scoped conclusion.

### Status

NEGATIVE RESULT

### Decision

`REVISE` for evidence packaging and protocol precision. The arithmetic and
scoped conclusion are accepted.

### Assumptions

- Three toy prime-order curves at 10, 12, and 14 bits.
- One seed and 31 draws per null family.
- Frozen coordinate constructors and sign policies.
- Fields restricted to `p mod 4 = 3`.
- No rank, descent, asymptotic, or generic ECDLP inference.

### Evidence so far

- All 582 configurations were independently recomputed with zero arithmetic
  discrepancies.
- Sign-complete canonical class totals match at every depth:
  - `B=10`: `10, 51, 180, 501, 1182`;
  - `B=12`: `12, 73, 304, 985, 2668`;
  - `B=16`: `16, 129, 704, 2945, 10128`.
- Every `D5_new`, canonical defect, energy, and maximum multiplicity matches.
- Every split census has support exactly `D5`; redundancy, hit counts, and
  both `T_perm` directions match.
- Every candidate instance fails both compression gates: 18/18 `D2` misses
  and 18/18 `D3` misses.
- V2/V3 arithmetic projections match; V2 supersession was reporting-only.

### Failure modes

- The original pooled dominance statistic was not precisely defined in the
  contract and is not a calibrated p-value.
- The first verifier did not durably recompute canonical counts, defects,
  energies, or maxima.
- V3 lacked a contemporaneous timestamp, dependency, and dirty-state receipt.
- The restricted schedule cannot support a family-wide conclusion.

### Strongest valid statement

No useful intermediate point-support compression was found for the frozen
x-interval, square-map, and square/Mobius-union representations under this
Stage-A development schedule.

### Restricted theorem target

Let `F` be a subset of `Z/qZ`, with prime `q` and `5|F|-4<q`. If
`|2F|=2|F|-1`, Vosper's theorem makes `F` an arithmetic progression, so
`|5F|=5|F|-4`. For `|F|=Theta(q^(1/5))`, fivefold coverage is `o(q)`.

This covers maximal compression only. The `0.8x` Stage-A threshold is well
outside the exact Vosper regime.

### Next concrete action

Classify affine-equivalence classes on the exact small-cyclic Pareto frontier,
including progressions, unions, inverse-symmetric sets, Sidon-like sets, and
perturbed progressions. Search for moderately compressed non-progressions
that retain constant-fraction `D5_new`.

### Artifact paths

- `contract.md`
- `development/DEV-COORD-EXPANSION-V3/raw-result.json`
- `development/DEV-COORD-EXPANSION-V3/analysis.md`
- `src/verify_coordinate_expansion.py`
