## Handoff: Null-calibrated recursive coverage

### Claim or task

Implement the frozen successor that tests whether the verified eight-term coordinate signal is exceptional against paired null distributions on clean curves.

### Status

HYPOTHESIS

### Assumptions

- Thirty-one replicates per null family are a toy percentile screen.
- Exact support and order-seeded scans are reproducible measurements, not an attack.
- The p mod 4 restriction remains explicit.

### Evidence so far

- EXP-ECDLP-RECURSIVE-001 independently replayed 216 configurations.
- Its passing rows had maximal four-term support and no advice compression.
- Its two one-draw null controls differed by 0.5705x to 1.4155x.
- One curve was anomalous, requiring generator/verifier repair.
- The successor generator rejects trace 0 or 1, special j, composite order,
  and nonmonotone schedules, and its nine-curve reduced smoke stayed clean.
- The independent verifier passed 14 self-tests and exactly replayed an
  externally generated reduced document.

### Failure modes

- Runtime exceeds budget with 62 nulls per curve.
- Support-order scans dominate or expose unstable first-witness costs.
- Empirical percentiles remain too coarse at toy sizes.
- A positive coverage signal fails later rank or descent gates.

### Next concrete action

Obtain an independent pre-run audit of the final source hashes and frozen gate;
launch no canonical run unless that audit returns `GO`.

### Artifact paths

- `experiments/EXP-ECDLP-RECURSIVE-002/specification.json`
- `experiments/EXP-ECDLP-RECURSIVE-002/contract.md`
- `experiments/EXP-ECDLP-RECURSIVE-001/result-red-team.md`
- `experiments/EXP-ECDLP-RECURSIVE-001/evidence.json`
- `experiments/EXP-ECDLP-RECURSIVE-002/src/null_calibrated_coverage.py`
- `experiments/EXP-ECDLP-RECURSIVE-002/src/verify_null_calibrated_coverage.py`
- `tests/test_null_calibrated_coverage.py`
