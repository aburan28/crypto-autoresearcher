## Handoff: EXP-SGCP-EMBED-002 V6 independent accounting review

### Claim or task

Independently audit exact commit
`83023747e7477376d19efbc459f6293e40671c06` for cost integrity and readiness
for launch-plan design only.

### Status

`OBSERVATION`; the underlying claim remains `HYPOTHESIS`, `TOY-EVIDENCE`,
`MODEL-BOUND`, and `NOVELTY-UNVERIFIED`.

Decision: `REVISE` for launch-plan design only. Execution remains `NO-GO`.

### Assumptions

- Only exact committed blobs were used for substantive review.
- No family row, canonical matrix, runner, launch plan, or experiment run was
  created by the reviewer.
- Structural cells, CPU, field operations, RSS, disk, I/O, and memory
  bandwidth are distinct resources.
- Resource exhaustion or verifier failure remains `INCONCLUSIVE`.

### Evidence so far

- All nine V6 development-log hashes match commit `8302374`.
- Python AST, JSON syntax, diff whitespace, and the 41-test inventory passed
  bounded static checks.
- Ledger state is V6 `review_required`, with `runs=[]`.
- The declared combinatorial budget formulas recompute exactly.
- No relevant ECDLP baseline is beaten or end-to-end comparable.

### Findings

1. `BLOCKER`: file admission is not total or strictly size-first. The verifier
   opens with blocking `O_RDONLY` before checking regular-file type, so an
   unwritten FIFO can block indefinitely. Initial `st_size` is not rejected
   before reading, and the loop can read one additional MiB before enforcing
   the 256-MiB ceiling. See `src/verify_sgcp_embed_family.py:390-404` and
   `tests/test_sgcp_embed_family.py:1697` at the reviewed commit.
2. `BLOCKER`: canonical curve generation precedes trusted reservation.
   Static preflight invokes `registered_curve_bundle`, which may perform up to
   100,000 draws per registered key, before resource reservation exists. A
   bounded provenance-only recomputation found 112 actual draws, 336 hashes,
   and 218 point enumerations across the eight fixed keys per deriving role;
   the source ceiling is 800,000 draws. Actual receipts expose only curve-cache
   entries. See `src/verify_sgcp_embed_family.py:608`, `:2664`, `:3937`,
   `:3967`, and `:4103`.
3. `BLOCKER`: invalid optimizer payloads can trigger unreserved work. Mask
   strings may be eight MiB and are converted to arbitrary-size integers
   without a B-derived length bound. Frozen exact-empty frontier requirements
   are absent from static preflight. Later gate errors do not stop replay,
   retained-model work, or primary proof. See
   `src/verify_sgcp_embed_family.py:2733`, `:3045`, `:3065`, and `:3233`.
4. `HIGH`: producer metric and full-model caches have no enforced entry or byte
   ceiling. Verifier reservation counts aggregate entries, not bytes or peak
   simultaneous occupancy. Actual receipts expose replay-cache occupancy but
   only an upper bound for primary caches and no actual retained-model calls or
   cells. See `src/sgcp_embed_family.py:836`, `:1119`, `:1425`, and
   `src/verify_sgcp_embed_family.py:3675`, `:4110`.
5. `MEDIUM`: expansion, graph, and retained-model cells are valid declared
   combinatorial units but omit weighted field operations, Python-object work,
   sorting, hashing, serialization, CPU, RSS, and bandwidth.
6. `MEDIUM`: JSON parser materialization, joined snapshot bytes, diagnostic
   accumulation, verifier-output size, and disk use remain external immutable-
   runner obligations. A 256-MiB file ceiling is not evidence that a future
   four-GiB role envelope will hold.

### Accounting recomputation

| B | Rows | Expansion cells/row | Expansion EC adds/row | Candidate max | Graph cells/row | Retained cells/call |
|---:|---:|---:|---:|---:|---:|---:|
| 4 | 56 | 214 | 1,484 | 35 | 1,855 | 2,485 |
| 6 | 56 | 1,440 | 10,848 | 126 | 23,877 | 22,155 |
| 8 | 56 | 6,809 | 52,880 | 330 | 163,515 | 122,760 |

Canonical aggregate ceilings are 1,344,000,000 producer optimizer nodes,
1,344,000,000 verifier replay nodes, 3,360,000,000 verifier primary nodes,
6,048,000,000 combined nominal nodes, 473,928 expansion cells per role,
3,651,872 expansion EC additions per role, 10,597,832 graph cells per role,
9,464,535,808 aggregate verifier cache-entry units, 4,732,268,576 retained-
model calls, and 234,199,407,524,320 retained-model cells. These are ceilings,
not predictions or peak-memory bounds.

### Baseline and scaling boundary

- Pollard rho and BSGS operate below roughly 15 group steps/table entries on
  the tiny registered orders before constants; SGCP does not solve a DLP and
  is not compared end to end.
- No van Oorschot-Wiener parallelism, MOV/Frey-Ruck special-case baseline,
  index-calculus relation path, linear algebra, or target descent is executed.
- Degree-eight expansion is `Theta(B^8)`, candidate count is `Theta(B^4)`,
  pair/graph storage is `Theta(B^8)`, current graph scans can reach
  `Theta(B^12)`, and exact subset optimization remains
  `2^Theta(B^4)` before caps.

### Failure modes

- FIFO or device opening may block before rejection.
- Oversized files are not rejected from initial metadata.
- Invalid transcripts can trigger curve work before reservation.
- Invalid frontier or mask payloads can reach replay or proof.
- Producer caches and verifier cache bytes lack closed peak-memory accounting.
- Receipts omit curve draws, retained calls/cells, exact primary-cache
  occupancy, and complete field operations.
- B6/B8 feasibility, artifact size, rank, and descent remain unmeasured.

### Next concrete action

Create a no-run V7 accounting repair that uses nonblocking admission and
pre-read size rejection; performs cheap type, digest, exact-empty-frontier, and
B-derived mask checks before curve work; constructs and receipts source-owned
reservation before registered-curve derivation; stops on invalid preflight;
and adds FIFO, oversized-file, pre-reservation-curve, nonempty-frontier, and
oversized-mask regressions.

### Artifact paths

- `8302374:experiments/EXP-SGCP-EMBED-002/protocol-amendment-v6.json`
- `8302374:experiments/EXP-SGCP-EMBED-002/development-test-log-v6.md`
- `8302374:experiments/EXP-SGCP-EMBED-002/contract.md`
- `8302374:experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py`
- `8302374:experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py`
- `8302374:tests/test_sgcp_embed_family.py`
