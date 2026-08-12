# Result Red Team

## Handoff: Coordinate Stage-A interpretation

### Claim or task

Determine whether V3 supports the scoped Stage-A negative result.

### Status

NEGATIVE RESULT

### Decision

`REVISE`, with no arithmetic rerun required for the narrow `D2` conclusion.

### Assumptions

- One generated curve at each of 10, 12, and 14 bits.
- One seed, `271828`.
- Prime-order, cofactor-one curves restricted to `p mod 4 = 3`.
- Frozen constructors and occupancy schedule only.
- Point-support geometry, not relations, rank, descent, or attack advantage.

### Evidence so far

- All committed tests pass.
- The independent verifier validates all 582 configurations and bound hashes.
- V2 and V3 arithmetic projections are equal.
- No candidate source record contains subgroup scalars.
- Seventeen of eighteen candidate cells have collision-free canonical `D2`;
  the remaining cell has support `104/105`.
- Candidate/null `D2` ratios are `0.990-1.000`, far above the `0.8` gate.
- `D3` is also null-like at `0.946-1.071`.
- The scalar-progression control compresses `D2/D3` while collapsing
  `D5_new`, showing that the profiler detects the intended tradeoff.

### Failure modes

- The pooled partial-order dominance count is not a calibrated p-value.
- Sampled scan-order spread differs from exact all-target spread.
- Formal occupancy ranges from `0.511` to `1.240` after size rounding.
- Audit wall time and temporary memory are not fully itemized.
- Compiler/audit separation is an API boundary in one process, not process
  isolation.
- One seed and three tiny `p mod 4 = 3` curves are a narrow schedule.

### Strongest valid statement

Under the frozen one-seed, three-curve development schedule, x intervals,
square-map images, and the square/Mobius union have essentially maximal `D2`
and null-like `D3`. No tested candidate achieved the intermediate-support
compression required for Stage-B promotion.

### What has not been ruled out

- Layered or heterogeneous factor bases.
- Succinct functional representations of a large `D2`.
- Other coordinate charts, field congruence classes, occupancies, or curves.
- Relation-rank and descent mechanisms not captured by support shrinkage.

### Next concrete action

Run an exact unrestricted small-cyclic-group Pareto census across multiple
occupancies, then test layered constructions or compact representations if
the joint support target is feasible.

### Artifact paths

- `contract.md`
- `src/coordinate_expansion.py`
- `src/verify_coordinate_expansion.py`
- `development/DEV-COORD-EXPANSION-V3/raw-result.json`
- `development/DEV-COORD-EXPANSION-V3/analysis.md`
