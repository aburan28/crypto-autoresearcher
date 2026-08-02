## Handoff: SGCP V6 exact-commit theory review

### Claim or task

Determine whether exact commit
`83023747e7477376d19efbc459f6293e40671c06` is ready for a separate
EXP-SGCP-EMBED-002 launch-plan design.

### Status

`NEGATIVE RESULT` for V6 protocol readiness and `RESTRICTED THEOREM` for
the fixed finite graph/ideal equivalence.

Decision: `REVISE` for launch-plan design only. Execution remains `NO-GO`.
The underlying claim remains `HYPOTHESIS`, `TOY-EVIDENCE`, `MODEL-BOUND`,
and `NOVELTY-UNVERIFIED`.

### Assumptions

- Only exact committed blobs at `8302374` were treated as evidence.
- A family row includes an in-memory complete density-row construction, not
  only a persisted JSON artifact.
- Exactness is limited to the registered finite curves, predicates, compiler,
  downward ideals, graph, objective, and gate.
- Resource reservations are combinatorial ceilings, not wall-time, RSS, I/O,
  or CPU authorization.

### Evidence so far

- All nine V6 development-log hashes match the committed blobs.
- The mathematical object, objective, source-table charging, gate arithmetic,
  and theorem boundary are internally consistent.
- The V5 input-snapshot, registered-B, source-owned replay-cap,
  legacy-routing, and gate-boundary defects are substantially repaired.
- Exact rational gate semantics agree in producer and verifier: persistence is
  at least `1/4`, medians retain multiplicity, positive counts do not splice
  across caps, and collapse is strict below `1/10` for every coordinate
  family.
- Ledger state remains `review_required`, with `runs=[]` and
  `maximum_runs=0`. No canonical matrix, runner, launch plan, or run artifact
  exists.

### Findings

1. `BLOCKER`: registered curve reconstruction occurs before row
   authentication and trusted reservation. `registered_row_envelope_errors`
   calls `frozen_curve_record` or `registered_curve_bundle` before the direct
   and document paths check the row digest. Document reservation is later
   still. A correctly signed document with bad row digests can therefore
   derive all registered curves before rejection while the phase receipt omits
   that work. See `src/verify_sgcp_embed_family.py:2644`, `:2664`, `:2839`,
   `:3624`, `:3630`, and `:3967` at the reviewed commit.
2. `BLOCKER`: the focused suite crossed the declared zero-family-row scope.
   `test_predicate_replicate_rules_and_mobius_transcript_are_enforced`
   generated the registered `(bits=6,seed=101)` curve, constructed a complete
   canonical-scope `B=4` Mobius density row, and verified it in memory. No row
   was persisted, but the committed log and revision response incorrectly
   stated that only the frozen p=19 row had been constructed. See
   `tests/test_sgcp_embed_family.py:754`, `contract.md:364`, and
   `development-test-log-v6.md:5`.
3. `HIGH`: the standalone B4 oracle computes complete candidate and eligible
   formal lists but returns only their counts and eligible indices. The final
   comparison therefore does not directly compare every candidate and
   eligible formal record. See `tests/test_sgcp_embed_family.py:326`, `:544`,
   and `:1092`.
4. `MEDIUM`: `verifier_source_sha256` reopens `SCRIPT_PATH` at report time. It
   is not an attestation of the bytes Python executed if the source path changes
   after module load. See `src/verify_sgcp_embed_family.py:360` and `:4077`.
5. `LOW`: `contract.md:68` and `contract.md:268` retain stale Version 5
   attribution in the V6 boundary.

### Restricted theorem

For the fixed representative compiler and downward ideals, graph independence
is equivalent to injectivity of EC evaluation on the union of selected ideals.
Each eligible maximum has an injective individual ideal. A graph edge is
exactly a collision in the union of two ideals. Conversely, a collision in the
global union lies within one ideal, contradicting eligibility, or across two
ideals, producing an edge.

This theorem does not cover non-downward partial operations, a different
representative compiler or factor base, algebraic coordinate attacks, relation
generation, matrix rank, or target descent. Those remain model-escape routes,
not refutations.

### Failure modes

- Curve derivation precedes digest authentication and reservation.
- The phase ledger does not expose that pre-reservation work.
- A generated canonical-scope density row was constructed despite the
  zero-row boundary.
- The standalone differential omits direct comparison of complete candidate
  and eligible formal lists.
- Runtime verifier-source hashing is not executed-code attestation.
- Canonical B6/B8 feasibility, artifact size, wall time, RSS, rank, descent,
  and rho comparison remain open.

### Next concrete action

Prepare one no-run V7 repair that authenticates rows before curve derivation,
reserves and phases source-owned curve work before deriving registered
transcripts, replaces the generated density-row test with factor-base-only
Mobius controls, and directly compares the standalone oracle's complete
candidate and eligible formal lists; then request fresh exact-commit review.

### Artifact paths

- `8302374:experiments/EXP-SGCP-EMBED-002/protocol-amendment-v6.json`
- `8302374:experiments/EXP-SGCP-EMBED-002/revision-response-v6.md`
- `8302374:experiments/EXP-SGCP-EMBED-002/development-test-log-v6.md`
- `8302374:experiments/EXP-SGCP-EMBED-002/source-self-review-v6.md`
- `8302374:experiments/EXP-SGCP-EMBED-002/contract.md`
- `8302374:experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py`
- `8302374:experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py`
- `8302374:tests/test_sgcp_embed_family.py`
