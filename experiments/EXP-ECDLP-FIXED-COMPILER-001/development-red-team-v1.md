# Development red-team v1

## Handoff: materialized D4 compiler review

### Claim or task

Determine whether the development implementation supports promotion of the fixed-curve coordinate compiler or only a scoped functional result.

### Status

NEGATIVE RESULT

### Assumptions

- `TOY-EVIDENCE`: one seed at 12, 14, and 16 bits.
- `HEURISTIC`: fitted slopes across three tiny instances are routing diagnostics only.
- `MODEL-BOUND`: generic preprocessing comparisons use disclosed advice bits and group-operation bounds.

### Evidence so far

- An independently structured verifier reconstructs all 36 rows and rejects mutations to relation RHS values, witnesses, rank, advice size, source hashes, descent outputs, and BSGS capacity.
- All 30 non-control rows pass the complete toy relation/rank/descent path.
- No candidate reaches the `0.8` dual-null score threshold.
- Every candidate loses both sampled-average and deterministic-worst-case online work to fixed-base BSGS at no larger advice.
- Builder-only witness replay, exact-support enumeration, recovered-log checks, challenge generation, and verifier work are separately labeled as audit costs.

### Failure modes

- A single draw from each null constructor is not a finite-null significance test.
- Python deep bytes and logical traffic are accounting proxies, not hardware measurements.
- The three-point slopes cannot support asymptotic extrapolation.
- Fixed-base BSGS is not the tightest generic preprocessing baseline, so merely approaching it would still be insufficient for a frontier claim.
- Independent sub-agent review could not be scheduled in this cycle; canonical source freeze remains prohibited.

### Next concrete action

Preserve this development artifact as a functional baseline and specify a compressed-join successor with a mechanical same-advice generic-baseline gate before requesting any canonical execution.

### Artifact paths

- `experiments/EXP-ECDLP-FIXED-COMPILER-001/development/DEV-FIXED-COMPILER-001/raw-result.json`
- `experiments/EXP-ECDLP-FIXED-COMPILER-001/development/DEV-FIXED-COMPILER-001/verification.json`
- `experiments/EXP-ECDLP-FIXED-COMPILER-001/development-result-v1.md`
- `tests/test_fixed_curve_compiler.py`
