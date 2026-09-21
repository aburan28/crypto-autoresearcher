# EXP-SGCP-EMBED-002 independent theory review v3

## Handoff: version-3 theory preflight

### Claim or task

Determine whether frozen commit
`2be45cd57bce4e23ad9996965999f906bb81dd4c` is ready to proceed to
design of a separate hash-complete canonical launch plan.

### Status

`NEGATIVE RESULT` for protocol readiness only; `RESTRICTED THEOREM`,
`TOY-EVIDENCE`, and `MODEL-BOUND` for the mathematical checks.

**Final recommendation: REVISE.** Do not begin canonical launch-plan design
yet. This does not reject the coordinate-predicate hypothesis.
`maximum_runs` remains exactly `0`.

### Assumptions

- Review was restricted to committed content at `2be45cd`; unrelated
  working-tree changes were ignored.
- No files or artifacts were created and no curve-family or canonical work was
  run.
- Dynamic checks used only abstract objects and the frozen p=19 curve.
- A conforming independent implementation must be derivable from the frozen
  protocol, not merely agree with an unstated convention shared by producer
  and verifier.
- A future GO would authorize plan design only, not execution or a budget
  change.

### Evidence so far

The central finite construction is coherent once the source ordering
conventions are assumed:

- An ordered factor base `F` supplies degree-two formal multisets.
- For every nonidentity point in `2F`, the compiler retains the
  lexicographically least formal witness.
- Pairs of those representatives induce degree-four maxima `m`, with fixed
  downward closures `I_m`.
- Individually injective maxima are vertices; two maxima conflict when
  evaluation is noninjective on the union of their ideals.
- For an independent set `S`, the optimizer maximizes final pair support
  `R(S)`, then minimizes constrained labels and public edges, maximizes retained
  maxima, and finally applies the lexical tie break.

`RESTRICTED THEOREM`: for these fixed ideals, graph independence is equivalent
to injectivity on their complete union. If a union collision exists, choose
ideals containing the two colliding formal objects. They cannot lie in one
ideal because every vertex is individually injective; therefore their two
ideals form a conflict edge. The converse is immediate. This proof does not
extend to an S-dependent closure that creates new triple- or multi-maximum
objects. The contract scopes the statement appropriately, and producer and
verifier implement it in `candidate_graph` and `reconstruct_graph`.

The exact optimizer requirements are internally consistent in
`optimize_coverage_graph`, `replay_density_search`, and
`independent_density_primary_optimum`. Exhaustion proves the primary and
secondary objective provided constrained-label and public-edge counts are
monotone under ideal enlargement and the clique-cover/pair-capacity bound is
admissible. Both properties hold for this fixed-union construction.

The six-pair gate implements exact middle-two null median, duplicate retention,
fixed `family x {1/2,3/4}` pairing, four strata, six comparisons per stratum,
threshold `max(1,ceil(q/20))`, and the `18/24` positive-comparison rule.

The source table is complete and independently reconstructed for the
code-defined labels. Its bytes are included in public and nested receipts.
Final-layer edge absence is correctly marked as a construction invariant, not
a discovery.

The committed source hashes match `development-test-log-v3.md`. Additional
commit-pinned checks found no counterexample across:

- 960 randomized abstract exact-objective cases;
- 143,632 exhaustive frozen-p=19, B=4 graph subsets over all three coordinate
  predicates and four hash controls;
- 28 frozen full-objective cap checks.

These are empirical implementation checks, not proofs or family evidence.

The structured-generic wording is otherwise appropriately bounded: compiler
dependence is explicit, final-edge absence is constructional, and relation
generation, rank, descent, rho improvement, scaling, and deployment relevance
are excluded.

### Failure modes

Exact blockers requiring `REVISE`:

1. **The representative compiler is not fully preregistered in prose.** The
   contract treats `F` as a set while choosing a lexicographically least
   indexed formal witness. The source silently indexes points by ascending
   `(x,y)`. Hash-ranking ties are resolved by `(digest,x)`, and source labels
   use `"O"` or `"x:y"`, without those conventions being frozen in the
   contract. Because representative choice changes the optimum, two
   implementations can currently follow the prose yet compile different
   objects.
2. **All-applicable-rejection wording contradicts code and test.** Producer and
   verifier short-circuit duplicate candidates to the exclusive list
   `["duplicate_candidate"]`. The test duplicates a singular curve and expects
   only that reason. Freeze duplicate-first exclusive semantics or change all
   three layers to record every mathematically applicable reason.
3. **Outcome taxonomy is contradictory.** Invalid axioms, optimizer
   disagreement, mismatched controls, and scalar leakage appear under
   hypothesis falsification, while contract and specification treat those
   events as invalidation and `INCONCLUSIVE`. Only a complete valid exact
   matrix may weaken or reject the mathematical hypothesis.

Model-escape routes remain open after repair: representative-invariant
compilers, closures that add genuinely multi-maximum objects, non-tree partial
operations, algorithmic source recovery rather than fixed advice, and
noncoordinate encodings. No model instantiated here addresses relation
generation, factor-base logarithms, matrix rank, target descent, online lookup
cost, or cryptographic-size scaling.

### Next concrete action

Commit a no-run amendment that freezes factor indexing, label encoding, and
hash tie rules; resolves duplicate-rejection semantics consistently across
prose, producer, verifier, and tests; and moves implementation/control failures
from hypothesis falsification to run invalidation. Rerun only focused unit,
abstract, and frozen-p=19 controls and request fresh read-only review. Preserve
`maximum_runs=0`.

### Artifact paths

- `experiments/EXP-SGCP-EMBED-002/contract.md`
- `experiments/EXP-SGCP-EMBED-002/hypothesis.json`
- `experiments/EXP-SGCP-EMBED-002/specification.json`
- `experiments/EXP-SGCP-EMBED-002/revision-response-v3.md`
- `experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py`
- `experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py`
- `tests/test_sgcp_embed_family.py`
