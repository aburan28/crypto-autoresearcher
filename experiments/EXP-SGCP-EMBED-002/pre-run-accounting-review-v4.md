## Handoff: SGCP V4 exact-commit accounting audit

### Claim or task

Audit commit `188b6f12cd50fb18a4304c126c23c27d99c56738` for
cost-model honesty, immutable evidence, budget enforcement, and readiness for
a separate canonical launch-plan design.

### Status

`OBSERVATION`; the underlying claim remains `HYPOTHESIS`, `TOY-EVIDENCE`,
`MODEL-BOUND`, and `NOVELTY-UNVERIFIED`.

Recommendation: `GO` for launch-plan design only. Execution, runner
construction, family rows, canonical matrices, and budget changes remain
prohibited.

### Assumptions

- Only the exact committed snapshot was reviewed.
- Structural cells are combinatorial accounting units, not CPU instructions or
  elliptic-curve operation totals.
- Nested JSON byte measures are nonadditive and omit enclosing artifacts,
  manifests, logs, and in-memory objects.
- The four hash controls are precommitted deterministic controls, not samples
  from a calibrated random-null distribution.

### Evidence so far

- All nine recorded SHA-256 values matched, the focused suite passed 25/25,
  hypothesis and specification validation passed, and `ledger.json` retained
  `runs: []`.
- Both producer CLI modes rejected execution and no V4 `runs/` directory
  exists.
- `maximum_runs=0`, `canonical_runs=0`, and `launch_plan=false` remain the
  operative budget boundary.
- V4 closes the exact-type, provenance, ordering, exhaustion, and canonical
  envelope defects assigned by the V3 decision.
- Per-row expansion grows sharply: B=4 uses 214 expansion cells and 1,484
  curve additions; B=6 uses 1,440 and 10,848; B=8 uses 6,809 and 52,880.
- Across the proposed 56 rows per B, the static expansion subtotal is 473,928
  cells and 3,651,872 curve additions before graph construction, exact search,
  verification, serialization, or process overhead.
- Candidate-pair construction can scale as O(B^8), and exact independent-set
  optimization is exponential in as many as Theta(B^4) eligible candidates.
- The proposed producer, replay, and independent-DFS ceilings can total more
  than six billion search nodes before setup and artifact handling.

### Failure modes

- A literal win over four deterministic controls is not a calibrated
  statistical win and has no global false-positive rate.
- No rho, van Oorschot-Wiener, BSGS, index-calculus, relation-generation,
  matrix-rank, or target-descent comparison is present.
- Model caches and memory bandwidth may dominate while remaining unmeasured.
- Row and cap times omit curve generation, output I/O, verifier time, and other
  end-to-end work.
- Proposed 900-second and 4-GB values are neither authorized nor mechanically
  enforced.

### Next concrete action

After theory and red-team decisions, draft but do not execute a hash-complete
canonical launch-plan design that freezes commands, hashes, node limits,
parallelism, retries, wall/CPU/RSS/traffic/I/O/full-byte receipts, output
ceilings, isolation, environment, manifests, and `INCONCLUSIVE` handling.

### Artifact paths

- `experiments/EXP-SGCP-EMBED-002/contract.md`
- `experiments/EXP-SGCP-EMBED-002/specification.json`
- `experiments/EXP-SGCP-EMBED-002/development-test-log-v4.md`
- `experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py`
- `experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py`
- `tests/test_sgcp_embed_family.py`

Final recommendation: **GO for launch-plan DESIGN only. Execution remains
NO-GO.**
