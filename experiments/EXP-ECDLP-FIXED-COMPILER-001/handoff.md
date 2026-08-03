## Handoff: fixed-curve five-term compiler specification

### Claim or task

Implement and independently verify a fixed-curve `4+1` compiler that reaches from exact coordinate sumsets through relation rank and individual target descent with complete cost accounting.

### Status

HYPOTHESIS

### Assumptions

- `UNTESTED`: coordinate families can improve support per advice bit over matched random-x.
- `MODEL-BOUND`: the generic `S*T^2` frontier is a comparison diagnostic, not a theorem about concrete coordinates.
- `TOY-EVIDENCE`: complete support and scalar verification are restricted to tiny generated groups.

### Evidence so far

- Prior recursive experiments provide exact support construction, clean-curve selection, matched controls, rho instrumentation, and independent affine arithmetic.
- `EXP-SGCP-EMBED-001` closes part of the structured-model translation but explicitly leaves relation collection, rank, linear algebra, and descent outside its scope.
- The literature map identifies fixed-curve preprocessing and batch point decomposition as open coordinate-specific targets.

### Failure modes

- Four-sum advice scales like an uncompressed random set.
- A single functional witness per sum produces a rank-deficient relation matrix.
- More witnesses restore rank only by erasing any storage advantage.
- Descent support or randomization cost dominates rho.
- Scalar metadata leaks into the solver path.

### Next concrete action

Specify `EXP-ECDLP-COMPRESSED-JOIN-001`, retaining the verified relation/rank/descent surface while replacing materialized `D4` advice with a representation that can plausibly approach `q^0.6` advice and beat same-advice BSGS online.

### Artifact paths

- `experiments/EXP-ECDLP-FIXED-COMPILER-001/contract.md`
- `experiments/EXP-ECDLP-FIXED-COMPILER-001/hypothesis.json`
- `experiments/EXP-ECDLP-FIXED-COMPILER-001/candidate-checklist.md`
- `notes/structured_group_coordinate_predicates_literature_20260717.md`
- `experiments/EXP-ECDLP-FIXED-COMPILER-001/development-result-v1.md`
- `experiments/EXP-ECDLP-FIXED-COMPILER-001/development/DEV-FIXED-COMPILER-001/verification.json`
