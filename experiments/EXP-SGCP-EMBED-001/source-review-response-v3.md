## Handoff: SGCP source-review repair v3

### Claim or task

Repair every remaining implementation finding in `source-red-team-v2.md`
without changing the version-3a mathematical hypothesis or executing a
canonical run.

### Status

HYPOTHESIS, source repair v3 in review. Canonical execution is unauthorized:
`specification.json` remains `review_required` with `approved_by: null`.

### Assumptions

- The five-bit fixture is implementation-only toy evidence.
- The locked repository runner, not either child, attests Git state, runtime,
  budgets, process-group quiescence, and predecessor transitions.
- The scalar-index oracle is verifier-only private material. Its scalar table
  is never copied into the builder certificate or verification report.
- Self-reported builder wall time and object-graph memory remain diagnostics;
  the runner separately enforces process limits.

### Evidence so far

| v2 finding | v3 repair |
|---|---|
| Generator/verifier did not compose with the locked runner | Both roles now have exact `--runner-json` modes, require `-I -S -B`, emit one stdout JSON object, spawn no descendants, and perform no child Git query. The verifier consumes the predecessor `raw-result.json`, checks its runner manifest/receipt, and reports the exact predecessor hash required by the runner. |
| Private audit omitted target association, identity witnesses, and final charged costs | Rows now preserve raw/retained target-to-witness-count maps, every degree-two identity witness, exact per-row operation deltas, and a fixed-point canonical private-audit byte count that includes its own size field. |
| Candidate density was mislabeled as raw witness density | Accounting now reports distinct balanced candidates and raw balanced parent pairs as separate exact ratios per constrained label. |
| Scalar-material non-emission claim was overbroad | The report claims only a syntactic forbidden-field/source-name gate and bounded diagnostic integers, explicitly sets `covert_scalar_encoding_excluded=false`, and carries no general information-flow attestation. An oversized diagnostic encoding is a rejecting regression. |
| Existing index differential shared verifier constructors and omitted retention/accounting | `verify_sgcp_scalar_index.py` is a separately structured standard-library implementation. It imports neither existing SGCP program, works in scalar indices after coordinate factor-base attestation, and independently recomputes candidates, invalid vertices, conflicts, every subset outcome, winners, target retention, and density accounting. The main verifier executes it in-process, exact-compares its frozen artifact, and gates every row on the differential. |

The proposed execution graph is hash-bound in `specification.json`: one locked
generator run followed by one locked verifier run. It passed protocol-hash
validation and an isolated `RLIMIT_NPROC=0` generator-to-verifier composition
test. This validates source composition only; it is not a canonical evidence
run.

### Failure modes

- A third reviewer may find a remaining provenance or common-mode weakness.
- The fixed scalar-index fixture checks optimizer implementation, not scaling,
  relation yield, matrix rank, linear algebra, or target descent.
- High retained final support would be an SGCP structure signal only. It would
  not establish a faster-than-rho ECDLP algorithm or even a viable end-to-end
  index-calculus algorithm.
- No execution lock may be issued until the reviewed source commit and all
  protocol hashes are final.

### Next concrete action

Run the final focused and repository suites, obtain a fresh read-only source
red-team decision, and freeze the reviewed commit only if the decision is GO.
Then request explicit approval before launching `RUN-SGCP-EMBED-001`.

### Artifact paths

- `experiments/EXP-SGCP-EMBED-001/source-red-team-v2.md`
- `experiments/EXP-SGCP-EMBED-001/src/sgcp_embed.py`
- `experiments/EXP-SGCP-EMBED-001/src/verify_sgcp_embed.py`
- `experiments/EXP-SGCP-EMBED-001/src/verify_sgcp_scalar_index.py`
- `experiments/EXP-SGCP-EMBED-001/oracles/scalar-index-oracle-v1.json`
- `experiments/EXP-SGCP-EMBED-001/specification.json`
- `tests/test_sgcp_embed.py`
