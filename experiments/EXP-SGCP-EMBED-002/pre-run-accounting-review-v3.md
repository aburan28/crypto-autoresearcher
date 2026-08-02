# EXP-SGCP-EMBED-002 independent accounting review v3

## Handoff: version-3 accounting boundary

### Claim or task

Determine whether frozen commit
`2be45cd57bce4e23ad9996965999f906bb81dd4c` honestly closes the V2
accounting boundary well enough to design a separate hash-complete canonical
launch plan.

### Status

`OBSERVATION`, `TOY-EVIDENCE`, and `MODEL-BOUND`.

**Final recommendation: GO.**

GO authorizes plan design only. It does not authorize execution, curve-family
rows, canonical artifacts, or a budget change. `maximum_runs=0` must remain
unchanged.

### Assumptions

- Review used committed Git objects at `2be45cd` only; unrelated working-tree
  changes were ignored.
- No curve-family sweep or canonical work was performed.
- One permitted frozen `p=19,a=2,b=9,q=23,B=4` check was executed entirely in
  memory from Git blobs.
- The possible result is a predicate-plus-representative-compiler density
  signal, not an ECDLP algorithm or preprocessing result.

### Evidence so far

The committed producer, verifier, tests, hypothesis, specification, and
contract hashes exactly match the V3 test-log hashes.

#### Accounting audit

| Emitted quantity | What it really measures | Audit result |
|---|---|---|
| `degree_multiset_evaluations` | Number of formal multisets enumerated by the degree-1/2/4/8 expansion only | Reconstructible, but not all multiset evaluations and not degree-weighted EC work |
| `balanced_*`, candidate, conflict, pair-output cells | Deterministic combinatorial cardinalities | Correctly reconstructed; not instructions, field operations, or wall cost |
| `explored_nodes` / `optimizer_nodes` | Expanded live branch-and-bound nodes | Correct, but excludes greedy initialization, queue operations, model-cache construction, sorting, hashing, and serialization |
| `optimizer_bound_calls` | Calls to the bound routine | Correct and independently replayed |
| Per-cap structural fields | Selected maxima, final unordered pairs, public edge records, and source-table entries | Exact counts, not materialization or lookup cost |
| JSON byte receipts | ASCII canonical-JSON length of precisely named nested objects | Exact, verifier-recomputed, and correctly labeled nonadditive |
| Row/cap `wall_time_seconds` | Producer-observed core-construction intervals | Observational only; excludes some surrounding work and is not an independent cost receipt |
| Peak memory | Nothing | Correctly absent |
| Verifier cost | Independent-proof node count only in the report | Not total verifier work; the documents correctly require external role accounting |

The per-cap model cache is created inside the cap loop in `build_density_row`,
so semantic and structural receipts are cap-local. Reversing cap order in the
frozen in-memory check produced identical public objects, optimizer receipts,
and structural fields at all four caps; only observational times changed.

The verifier independently recomputes both structural cells and all nested
byte receipts. It also verifies finite, nonnegative cap times whose sum does
not exceed the row timer.

The byte labels are honest but intentionally incomplete. They omit the
accounting object, row digest, document envelope/digest, newline, manifests,
logs, and verifier report. The contract delegates complete serialized-output
measurement to a future trusted runner.

The public representative and label-to-formal source tables are included in
the public model and nested cap bytes, so neither is free advice.

#### Baseline table

| Baseline | Correct resource boundary | V3 comparison |
|---|---|---|
| Four hash-ranked x-fiber controls | Same curve, B, absolute cap, optimizer budget; exact four-value median | Correct strongest baseline for the claimed coordinate-family signal |
| Pollard rho with negation and any available cheap endomorphism | Approximately square-root group work, constant worker memory | Not measured; no rho claim is possible |
| van Oorschot-Wiener parallel collision search | Total collision work, wall-time scaling, distinguished-point storage, processors | Not measured |
| BSGS/MITM | Square-root group work and square-root memory | Not measured |
| Index calculus / Groebner / SAT / crossbred | Relation generation, decomposition, solver work, rank, linear algebra, and target descent | No corresponding pipeline exists |
| MOV/Frey-Ruck, Smart, Cheon, twist/fault/HNP cases | Special-instance preconditions and full attack cost | Out of scope; toy-curve specialness remains a caveat |

Thus V3 can only beat its matched-null density control. It cannot beat or even
be normalized against an ECDLP solver.

#### Scaling estimate

For factor-base size `B`, the emitted expansion cell count is

```text
sum_{d in {1,2,4,8}} binomial(B+d-1,d),
```

giving 214, 1,440, and 6,809 cells for `B=4,6,8`. Across 56 canonical
rows per B, that is 473,928 formal expansion cells. This understates actual EC
work because an evaluated degree-d multiset performs d additions.

The degree-four candidate count is at most `binomial(B+3,4)`: 35, 126,
and 330. Conflict and pair-output construction can therefore reach
quadratic-in-candidate work, asymptotically `O(B^8)`. Exact independent-set
optimization remains exponential in the eligible-candidate count.

The frozen protocol permits up to 2,000,000 producer nodes per each of 672
cells: 1.344 billion expanded-node slots. Verification replays that search and
adds a separate DFS proof whose current default is 5,000,000 nodes per cell.
If retained, the combined ceilings exceed six billion node expansions before
uncounted model construction and artifact handling. These are workload
envelopes, not an attack exponent.

### Failure modes

Residual risks accompanying GO:

1. `model_cache` stores complete model objects, including edge and source
   tables, for visited masks. Fresh-per-cap locality removes order
   contamination but not a potentially dominant peak-memory blowup.
2. `degree_multiset_evaluations` and `optimizer_nodes` are narrower than their
   names may suggest. They must never be summed or presented as total group,
   field, CPU, or preprocessing work.
3. Row timing begins inside `build_density_row` and ends before accounting
   serialization and the row digest; it also excludes curve generation, output
   I/O, and verification. Only external role timing may support a cost
   statement.
4. A future plan must freeze the verifier proof-node limit; it is currently a
   CLI parameter rather than a canonical protocol constant.
5. No canonical producer CLI exists, and verifier output is restricted to
   `development/`. Any adapter or verifier amendment needs its own hash and
   review.
6. The verifier still accepts clearly labeled legacy development schemas. A
   canonical manifest must bind V3 schema and `scope="canonical"` exclusively
   and exclude the committed V1 development artifacts.
7. Parallelism, aggregate RSS, total CPU, retry policy, process isolation,
   memory-traffic instrumentation, and complete producer/verifier artifact
   sizes remain unspecified. Data-dependent retries or budget increases must
   be forbidden.
8. Deterministic replay shares substantial model logic with the producer; the
   alternate DFS proves only the primary optimum. Shared model or
   secondary-objective errors remain possible.
9. Exact B=8 closure may be infeasible. Any unresolved cell invalidates the
   entire matrix and yields `INCONCLUSIVE`, preventing exact-only selection
   bias.
10. The focused V3 suite is green, but the repository-wide suite is honestly
    recorded as failed due to an immutable-run collision. Canonical work needs
    an isolated frozen environment.
11. Rank, relation collection, factor-base logarithms, target descent, memory
    crossover, and optimized rho comparison remain wholly absent. No
    family-gate outcome can be called a preprocessing or ECDLP win.

None of these residual risks can create a valid positive V3 gate under the
required verifier. They can make execution infeasible, force `INCONCLUSIVE`,
or enable a later overclaim if the launch plan omits its accounting obligations.

### Next concrete action

Draft, but do not execute, a hash-complete canonical launch plan binding commit
and adapter hashes, V3-only schemas, exact commands, producer and verifier node
limits, isolated role processes, full artifact manifests, external
wall/CPU/peak-RSS/memory-traffic/output-byte receipts, fixed parallelism and
retry rules, and `INCONCLUSIVE` on any resource or verification failure.
Preserve `maximum_runs=0` pending separate review and Coordinator approval.

### Artifact paths

- `experiments/EXP-SGCP-EMBED-002/contract.md`
- `experiments/EXP-SGCP-EMBED-002/hypothesis.json`
- `experiments/EXP-SGCP-EMBED-002/specification.json`
- `experiments/EXP-SGCP-EMBED-002/protocol-amendment-v3.json`
- `experiments/EXP-SGCP-EMBED-002/revision-response-v3.md`
- `experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py`
- `experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py`
- `tests/test_sgcp_embed_family.py`
