## Handoff: SGCP source-review repair v4

### Claim or task

Repair every source-freeze finding in `source-red-team-v3.md` without changing
the version-3a mathematical hypothesis or authorizing execution.

### Status

HYPOTHESIS, source repair v4 awaiting read-only review. Canonical execution
remains unauthorized; `approved_by` is null and no run output exists.

### Assumptions

- Exact runner argv provenance includes the invocation token as supplied by the
  frozen execution plan; resolving to the same file is insufficient for receipt
  equality.
- Target witness maps are private charged audit material, not public star
  advice.
- Diagnostic integers are bounded but remain unauthenticated semantic channels.

### Evidence so far

| v3 finding | v4 repair |
|---|---|
| Frozen relative argv differed from builder self-report | Runner mode now preserves `sys.argv[0]` exactly. The composition test loads both argv arrays directly from `specification.json`, runs under `-I -S -B` and `RLIMIT_NPROC=0`, and exact-compares the emitted builder argv with the plan and receipt. |
| Synthetic test used friendlier absolute paths | The test now uses the frozen relative source, contract, literature, and predecessor tokens. A mutated receipt with an absolute builder token is rejected by external provenance comparison. |
| Target audit retained only counts | Builder rows now emit literal raw and retained target-to-unordered-input-pair maps as point labels. The main coordinate verifier reconstructs them independently, while the scalar-index oracle translates scalar pairs to canonical point-pair order and exact-compares every map. Counts and histograms remain separate. |
| Public scalar wording was overbroad | `ABSENT_BY_DESIGN` was replaced by a structured attestation: forbidden named fields are absent by construction, while `covert_encoding_excluded` is exact false. |
| Covert-channel control covered only oversized integers | A valid in-range wall-time value carrying arbitrary information is accepted after receipt recomputation, and the report still declares that covert encoding is not excluded. Oversized integers remain rejected by bounds. |
| v3 response overstated composition | This repair supersedes that statement: frozen-plan composition is established only by the exact development fixture, not by a canonical runner launch. |

Focused v4 tests pass `22/22`; all 16 protocol hashes and the experiment schema
validate. These are development checks only.

### Failure modes

- The runner-shaped fixture uses synthetic manifest and receipt records; only a
  later approved runner launch can produce canonical provenance.
- Literal target maps increase private audit bytes and do not make the final
  join free.
- The scalar-index oracle remains a five-bit optimizer differential, not a
  scaling or cryptanalytic result.
- Another reviewer may still identify a source or plan mismatch.

### Next concrete action

Obtain a fresh read-only source-freeze decision on v4. Freeze a Git commit only
if it returns GO; request explicit approval separately before any run.

### Artifact paths

- `experiments/EXP-SGCP-EMBED-001/source-red-team-v3.md`
- `experiments/EXP-SGCP-EMBED-001/src/sgcp_embed.py`
- `experiments/EXP-SGCP-EMBED-001/src/verify_sgcp_embed.py`
- `experiments/EXP-SGCP-EMBED-001/specification.json`
- `tests/test_sgcp_embed.py`
