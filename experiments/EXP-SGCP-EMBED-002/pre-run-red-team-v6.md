## Handoff: EXP-SGCP-EMBED-002 V6 exact-commit adversarial review

### Claim or task

Determine whether exact commit
`83023747e7477376d19efbc459f6293e40671c06` is ready for launch-plan design
without authorizing execution.

### Status

`OBSERVATION`; the underlying claim remains `HYPOTHESIS`, `TOY-EVIDENCE`,
`MODEL-BOUND`, and `NOVELTY-UNVERIFIED`.

Decision: `REVISE` for launch-plan design only. Execution remains unauthorized,
and `maximum_runs=0` remains in force.

### Assumptions

- Only exact committed SGCP blobs were interpreted.
- Unrelated pre-existing worktree dirt was ignored.
- Probes were bounded and created no repository artifacts.
- No family row, canonical matrix, runner, launch plan, or experiment run was
  created by the reviewer.

### Evidence so far

- HEAD and the requested commit both resolved to full commit
  `83023747e7477376d19efbc459f6293e40671c06`.
- All nine V6 development-log hashes matched the committed blobs.
- All 41 focused tests passed in the reviewer at 2.091 seconds.
- Hypothesis and experiment records validate; the ledger remains
  `review_required`, V6, with `runs=[]`.
- Exact-type rejection, V1-V5 rejection, registered grid/caps, input-byte
  snapshotting, frozen B4 semantics, and gate arithmetic survived.
- The producer CLI remains disabled.

### Findings

1. `BLOCKER`: late-invalid and exception receipts do not describe actual work.
   An objective mismatch is recorded, but the verifier continues through all
   replay and primary-proof calls. Replay/proof phases are appended only after
   every row succeeds. The exception boundary discards completed row reports
   and an already-passed reservation, so the final receipt can report zero
   work after material replay and proof work. A signed wrong-objective probe
   executed four replays and four proofs while listing neither phase. A
   second-cap exception probe executed two of each but returned zero rows,
   zero actual work, and no reservation. See
   `src/verify_sgcp_embed_family.py:3025`, `:3088`, `:3233`, `:3977-4002`,
   and `:4219-4238` at the reviewed commit.
2. `HIGH`: digest and ordering fail-fast still derive registered curves first.
   A bad-digest frozen row invoked `frozen_curve_record` before rejection.
   The committed test patched only later provenance verification and missed
   this path. See `src/verify_sgcp_embed_family.py:3624`, `:3630-3642`, and
   `tests/test_sgcp_embed_family.py:1602-1622`.
3. `HIGH`: nonregular-file handling is not total. Blocking open precedes
   `fstat`, so an unwritten FIFO can prevent any receipt. `O_NOFOLLOW` applies
   only to the final path component; parent-component symlink policy is not
   stated. See `src/verify_sgcp_embed_family.py:388-400`.
4. `HIGH`: `verifier_source_sha256` is not bound to the executed source bytes.
   The report reopens `SCRIPT_PATH` after module load and can receipt bytes B
   after executing bytes A. See `src/verify_sgcp_embed_family.py:360-365` and
   `:4077-4081`.
5. `MEDIUM`: parser and diagnostic ceilings are amplification bounds, not
   containment. Node/depth/string checks occur after `json.loads`; unexpected
   keys are sorted and serialized into an uncapped diagnostic. A 10,000-key
   probe produced one 150,236-byte error. Accepted combinatorial ceilings are
   not wall-time, RSS, byte-traffic, or cache-memory enforcement.
6. `MEDIUM`: canonical full-objective independence is weaker than claimed.
   The verifier replay closely mirrors producer search. The separate DFS proves
   retained-support optimality only, not the complete constrained-count,
   public-edge, retained-maxima, and lexical tie-break objective. A structurally
   independent full-objective oracle exists only for frozen B4.
7. `MEDIUM`: the gate compares three coordinate families with four fixed hash
   controls on eight tiny deterministic curves. Low embedding-degree examples
   occur in the registry. A future PASS could be a tiny-curve or weak-null-bank
   artifact and would not establish statistical persistence.
8. `LOW`: two contract passages retain stale V5 wording.

### Overclaim corrections

- Snapshot-bound currently means parsed input bytes, not executed verifier
  source.
- The actual phase ledger is valid only for success and early rejection.
- Resource reservation is combinatorial accounting, not OS-enforced time or
  memory.
- Canonical secondary-objective exactness is replay-confirmed, not independently
  DFS-proved.
- A future PASS would be only a toy win over four controls on eight curves. It
  would not establish relation yield, rank, descent, preprocessing crossover,
  rho improvement, or an ECDLP attack.

### Failure modes

- Invalid authenticated inputs can consume replay/proof work omitted from the
  receipt.
- An exception can report zero work after material work occurred.
- A FIFO can prevent any receipt.
- Parser and diagnostic amplification can exceed practical role limits.
- Shared optimizer structure can preserve the same secondary-objective error
  outside frozen B4.
- Four nulls and eight tiny curves can produce a toy-specific signal.

### Next concrete action

Create one no-run V7 revision that moves row authentication before curve work;
stops before replay/proof when any earlier error exists; records replay/proof at
their call sites; preserves reservation and partial lower-bound counters through
exceptions with `actual_work_complete=false`; uses nonblocking size-first file
admission; states parent-symlink policy; caps diagnostic count and bytes; and
binds executed code through a future immutable-runner commit receipt.

Required controls are signed wrong-objective, mask/index, frontier, graph, and
accounting mutations with zero unnecessary replay/proof; second-cap exception
injection with preserved partial work; an unwritten FIFO; source replacement
after module load; diagnostic-amplification boundaries; and structurally
different full-objective abstract fixtures.

### Artifact paths

- `8302374:experiments/EXP-SGCP-EMBED-002/decision-v5.json`
- `8302374:experiments/EXP-SGCP-EMBED-002/protocol-amendment-v6.json`
- `8302374:experiments/EXP-SGCP-EMBED-002/revision-response-v6.md`
- `8302374:experiments/EXP-SGCP-EMBED-002/development-test-log-v6.md`
- `8302374:experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py`
- `8302374:experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py`
- `8302374:tests/test_sgcp_embed_family.py`
