# Red-team falsification review — GOAL-SSI-001 BATCH-008

Task `TASK-20260729-007` · Snapshot
`5c8e1f65c32176fd973de0a173eeb73e52d1b98d`  
Verdict: **REVISE**

## Result

`CSIDH-COLLIMATION-FC0-R1` materially improves the FC0 accounting schema, but
O1-O5 were not all adequately repaired:

- **O1 — partial:** per-invocation charging is the right repair, but the exact
  equality between an aggregate query figure and a stochastic realized
  invocation multiset mixes expectation, trace, percentile, and stopping
  semantics.
- **O2 — adequate as a type repair:** the classical tail is removed from
  quantum query/T/depth/width and retained as explicit classical work and
  memory. Its values remain unresolved, as the producer states.
- **O3 — partial:** diamond distance gives the oracle a composable contract,
  but sieve, postprocessing, and tail error terms are not mapped into the same
  operational metric.
- **O4 — partial:** the global-liveness principle is correct, but the stage
  table is a checklist, not an instantiated register-liveness schedule with
  widths and allocation/deallocation boundaries.
- **O5 — provisional:** the `8L` cap can be a conservative Equation (4.1)
  bound only if it is source-proved to bound every charged phase vector. The
  committed snapshot does not contain primary-source text that lets this
  implication, factor `36`, or the other exact source semantics be checked.

The disposition **`FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED` is supported**.
No source-compatible end-to-end resource vector was instantiated, and the
expectation-versus-realized-trace defect is itself an unresolved query/recovery
semantic. This does not make query semantics the only blocker: the
uniform-oracle channel, coherent width, classical tail, and end-to-end error
remain unresolved too.

## Knowledge and scope checks

The `peikert_unconstrained_collimation_explicit_qracm` posture is conceptually
aligned with `KN-TECH-051`: it reports QRACM, imposes no exogenous memory cap,
and rejects importing a SQALE resource-constrained row. “Peikert
unconstrained” must remain a local convention label, however, because
`KN-TECH-051` and `KN-LIT-127` say the concrete Peikert details were not
primary-source verified.

No numeric-security, NIST-level, parameter, breakthrough, ECDLP, or
GOAL-completion claim was made. No closed lane was reopened. The generic
Pollard-rho and BSGS square-root comparators cannot be evaluated against R1
because R1 emits no complete attack time-memory-oracle point. The closest
specialized baseline remains the exact Peikert binary c-sieve row under the
same revision and memory posture.

## Cheapest falsification control

Let every top-level invocation cost `q` queries and `s` non-oracle work, with a
geometric invocation count `R`. The source aggregate may satisfy
`Q_tilde_total = E[R]q` while no ordinary realized trace has
`sum_i Q_i = Q_tilde_total`. R1 must either:

1. declare expectation semantics and also charge `E[R]s` plus the corresponding
   postprocessing, tail, memory, and error quantities; or
2. declare a percentile/worst-case budget and derive that budget for every
   resource.

A single source- or code-derived trace cannot reconcile an expected aggregate.

## Archival limit

The snapshot commit is reachable, changes exactly the three producer artifacts
and receipt, and all producer hashes match the receipt. The committed receipt
still records `commit_sha: null` and `verification.status:
pending_post_commit`; dispatcher post-commit acceptance must be durably
recorded before an official state transition.

## Next action

Archive exact primary-source excerpts and build one stochastic invocation
ledger that defines the stopping distribution and reconciles queries, repeated
sieve work, postprocessing, tail, memory, and errors under one declared
statistic. Keep `FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED` until that control
passes.
