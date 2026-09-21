# TASK-20260722-002 independent adversarial methodology review

## Verdict

**REVISE.** The archived producer package remains correctly classified
`FRONTIER_ONLY`, and its claim boundaries are appropriately conservative.
Neither proposal is ready for a frozen validation protocol.

- `frontier-A`: **REVISE**
- `frontier-B`: **REVISE**
- implementation or experiment authorization: **none**
- research evidence or finding produced by this review: **none**
- ECDLP attack-cost improvement established: **none**

The decisive defects are methodological. Frontier-A calls a bounded dynamic
trace a non-interference receipt and omits much of the trace cost. Frontier-B
misinterprets a lower confidence bound on yield as a lower bound on required
attempts and lacks a precommitted schedule against which attempt completeness
could be certified.

## Runtime, fallback, and independence receipt

- Requested policy: `review-xhigh`
- Requested reasoning effort: `xhigh`
- Resolved model: `gpt-5.6-sol-high`
- Available reasoning effort: `high`
- Fallback used: `true`
- Authorization: `DEC-20260722-001`
- Adapter version: `unavailable_not_exposed_by_cursor_runtime`
- Adapter version available: `false`
- Adapter/runtime availability: Cursor agent runtime was available; its adapter
  version value and provider session ID were not exposed.
- Independent session: `true`
- Session identity:
  `TASK-20260722-002-independent-review-20260722T093600-0700`
- Non-originating reviewer: `true`
- Reviewed artifacts originated by this reviewer: none
- Equivalence between `high` and requested `xhigh`: not claimed

This session is distinct from TASK-20260721-008 and originated none of its
artifacts, snapshot records, or authorization records.

## Snapshot and producer-fallback gate

The producer package was not read until its archive binding was reconstructed.
The snapshot gate passes:

- archive task: `TASK-20260721-009`
- commit: `03eea94f5ea4e1c98d5e0d6aea0e63dd1cff9e92`
- parent: `7885e51da107b25d91ed79dcc7374f7548f72dd3`
- reachable from review HEAD: yes
- exact changed paths: the receipt and four declared TASK-20260721-007/008
  producer artifacts, with no extra path
- full commit message: contains `TASK-20260721-009`,
  `TASK-20260721-007`, `TASK-20260721-008`, `GOAL-ECDLP-001`, `BATCH-001`,
  and `DEC-20260721-002`
- all five committed SHA-256 values: independently recomputed and equal to the
  completed archive task card
- current TASK-20260721-008 producer bytes: equal to the archived bytes

The receipt file's own `commit_sha` and `parent_sha` are null. That is the
documented self-reference convention, not an integrity gap: the completed
archive task card supplies those values and Git verifies them independently.

The producer fallback receipt also passes. Both producer artifacts record
`research-sol-max`, `gpt-5.6-sol-high`, `high`, `fallback_used: true`, the
unavailable-but-explicit adapter-version state, and `DEC-20260721-002`
consistently.

The review authorization is itself committed at
`ae6f5137d21baa9103a20c8e3da508826c2e3278`, parent
`03eea94f5ea4e1c98d5e0d6aea0e63dd1cff9e92`. Its decision and handoff hashes
match the current files. No metadata or snapshot mismatch required an early
stop.

## Adversarial reconstruction of frontier-A

### Narrow mechanism that survives

The useful core is a target-swap divergence gate:

1. Seal the declared setup boundary, inputs, environment, randomness, and
   outputs.
2. Run setup under independently changed public toy targets.
3. Compare setup-state digests and the observed dependency graph.
4. If a target-to-setup-state causal path exists, reject the claimed
   target-independent amortization and recharge the affected work.

That gate is absent from the current runner and ledger validator. It can change
a concrete decision for a candidate that claims reusable fixed-curve
preprocessing.

### Novelty challenge

The general mechanism is not externally novel. Public in-toto link attestations
already bind commands, hashed materials, hashed products, byproducts, and
environment. SLSA provenance records resolved dependencies and explicitly
treats completeness as best effort. ReproZip traces process and file activity
to package reproducible executions.

The only defensible novelty claim is therefore repository-local and
application-specific: combine established provenance and trace patterns with a
target swap and an ECDLP setup-versus-online cost decision. The producer should
not describe the underlying receipt or tracing method as new.

### Non-interference claim fails as written

Two target swaps and equal hashes do not prove semantic non-interference. They
show only that no divergence was observed for two values inside one observation
boundary. A hidden dependency may be untraced, dormant on those values, carried
through memory or an accelerator, or canceled before the final state hash.

Conversely, a changed hash is not automatically target leakage. Clock values,
temporary paths, process IDs, scheduling, unordered serialization, and
uncontrolled randomness can cause target-independent divergence. Unless the
receipt supplies a target-to-state causal path, the correct disposition is
`invalid_or_inconclusive_trace`, not immediate reclassification of all setup as
per-target work.

The passing claim must be narrowed to:

> No target-derived dependency was observed within the sealed deterministic toy
> trace boundary.

It must not say semantic non-interference, complete dependency coverage, or
cryptographic-scale reusable preprocessing.

### Cost and burden challenge

`O(A)` artifact hashing and `O(E)` retained event storage are incomplete. A
frozen estimate must separately charge:

- hermetic environment construction;
- syscall or equivalent event capture CPU and wall time;
- event ordering and normalization;
- repeated setup and target-swap replay;
- memory, subprocess, accelerator, network, and shared-service coverage;
- state snapshot bytes and hashing;
- receipt serialization and storage;
- independent receipt verification;
- false-divergence investigation.

This is high-burden instrumentation. It may save an unspent campaign budget
after detecting leakage, but no numeric saving and no ECDLP attack-cost
reduction exists yet.

### Required falsification controls

The proposed clean fixture and two planted leaks test basic sensitivity but are
insufficient. A future specification would also need identical-target reruns,
target-independent nondeterminism controls, a deliberately unobserved channel
to measure boundary failure, and a rule distinguishing a causal leak from an
unexplained divergence.

For those reasons frontier-A is **REVISE**, not PASS.

## Adversarial reconstruction of frontier-B

### Narrow mechanism that survives

The useful core is a conservation join:

1. Begin from a hash-bound schedule manifest created before execution.
2. Require a bijection from scheduled attempt IDs to terminal receipts.
3. Bind each accepted result to an independently checked relation certificate,
   canonical row, field and column schema, and exact rank before/after.
4. Retain consumed resource vectors for invalid, censored, duplicate,
   dependent, failed, and successful attempts.
5. Give rank credit only to a verified row that raises exact rank.

The corpus already demands these accounting concepts in prose. The additional
capability is machine-checkable schedule-to-receipt-to-rank conservation.

### Attempt completeness is not self-authenticating

Requiring every "scheduled attempt" exactly once is ineffective unless the
schedule is independently sealed before work begins. A producer can omit an
unfavorable attempt from both the schedule and receipts, or create IDs only
after seeing outcomes. Generated receipt IDs cannot reveal that omission.

The root artifact must therefore be a precommitted campaign manifest containing
attempt IDs, seeds, parent/retry policy, budgets, worker allocation, field,
column schema, and terminal-state vocabulary. The conservation check is a
bijection against that manifest, not merely a uniqueness check over observed
receipts.

### The confidence rule is mathematically misinterpreted

The package says the projected attempts required for `r` rank units are "at
least `ceil(r/p_L)`", where `p_L` is a lower confidence bound on incremental-rank
yield. Under the fixed IID Bernoulli model needed for that expression, if
`N_r` is the number of trials to obtain `r` successes, then:

```text
E[N_r] = r/p.
```

On the event `p >= p_L`:

```text
E[N_r] <= r/p_L.
```

Thus `r/p_L` is a conservative upper bound on the conditional expected number
of trials, not a lower bound on required trials. It is also not a finite-budget
completion guarantee. For a declared miss probability `alpha`, a valid fixed
IID budget gate instead chooses the least `n` satisfying:

```text
Pr[Binomial(n, p_L) >= r] >= 1 - alpha,
```

equivalently a negative-binomial tail condition. If `p_L=0`, no finite
guarantee follows.

Even this repair does not apply automatically. Incremental-rank yield usually
changes with current rank, matrix occupancy, retries, source adaptation, and
candidate selection. Near full rank, dependence can become more likely. A
single pilot estimate is invalid without prespecified state strata,
exchangeability assumptions, or a justified sequential confidence method.

This error makes the current complete-cost decision rule **FAIL** even though
the underlying conservation artifact remains repairable.

### Resource comparison is vector-valued

CPU seconds, wall seconds, group operations, bytes transferred, and peak memory
cannot be summed into one scalar without a frozen conversion or constrained
dominance rule. Peak memory is not additive, overlapping wall intervals must
not be summed as elapsed time, and shared preprocessing requires explicit
ownership. Candidate and matched rho/BSGS controls must report the same resource
vector before a "below both" decision is meaningful.

### Required falsification controls

The proposed valid, duplicate, dependent, invalid, censored, and overlapping
toy rows are useful. A decisive fixture must additionally plant:

- one scheduled attempt missing from receipts;
- one duplicate attempt ID;
- a retry-parent cycle or undeclared retry;
- a field or column-schema mismatch;
- shared work claimed by two workers and shared work claimed by neither;
- a relation whose certificate passes but whose canonical row does not match;
- a rank result reconstructed under the wrong field.

These controls test the actual conservation boundary rather than only the rank
arithmetic.

The passing claim must be limited to conservation of one sealed toy campaign
under one frozen schema. It is not an ECDLP relation-cost lower bound or an
attack-cost reduction.

For those reasons frontier-B is **REVISE**, with its current confidence/cost
subclaim marked FAIL.

## Decision and claim boundary

The review upholds `FRONTIER_ONLY`. Both proposals may have methodology value,
but neither supplies a validated tool, run, certificate improvement, lower
bound, empirical effect, or cryptanalytic result. Passing snapshot and metadata
checks establish provenance only. A future toy pass would remain toy
methodology evidence and would not establish P-256 behavior or a better-than-rho
attack.

Exactly one next action:

> Commission one versioned, review-only amendment of frontier-B that seals the
> attempt schedule and field/schema, freezes resource ownership as a vector,
> and replaces `ceil(r/p_L)` with a declared-alpha negative-binomial tail gate;
> defer frontier-A and authorize no implementation or run until that amendment
> passes another independent review.

## Public documentation boundary

Accessed 2026-07-22 for methodology comparison only:

- <https://slsa.dev/spec/v1.1/provenance>
- <https://github.com/in-toto/attestation/blob/main/spec/predicates/link.md>
- <https://docs.reprozip.org/en/latest/index.html>
- <https://docs.reprozip.org/en/latest/packing.html>
- <https://www.boost.org/doc/libs/1_46_0/libs/math/doc/sf_and_dist/html/math_toolkit/dist/dist_ref/dists/negative_binomial_dist.html>

No live key, deployed system, operational attack, unapproved experiment, or tool
implementation was involved.

## SHA-256 reviewed-input manifest

Both this report and `review_report.yaml` bind the verified snapshot and every
repository file directly relied upon:

```text
f21afaab25ac6f2c74a7a36cb67b76bde313be14ac78077e72abc76031dc493b  AGENTS.md
33f3c8084fa67a76e74fd016195ab1225601053e0b025c715cfdc7c6f9259dcb  CLAUDE.md
7931c399c5a6030b7cd29540073a9e9b740a8a9e458f2dc06fc05aa901c13440  ledger/handoffs/TASK-20260722-002.yaml
07c0d5e2d3d307a8f758c3e5cc0f4499fc52cce92ccb0ed506bc54e8224b8c4a  ledger/decisions/DEC-20260722-001.yaml
c4fa4079b1c49a735a6b723f1585943168f30b228f13a1ddf4b069e3063333d2  ledger/handoffs/TASK-20260721-008.yaml
997befa5ce24f3f1b25c1fe98eb0abfb35256db7c5abe34cc72d3a900a1bb068  ledger/decisions/DEC-20260721-002.yaml
0025826e758db9d2e175a85f130d5545c6573b9e0b0ebcf07c32f173da146bdd  orchestration/model-policies.yaml
e184c6a307c8f1127399356b1f7483fc05a58974e6968a04b1ac7072c4814490  docs/task-lifecycle.md
37cdc5d7ff60c45465e8ef88e1a800f3d9df06f7035fc9ea1f1552e7bf1ebf9a  docs/dynamic-subagent-dispatch.md
37fd8d21d97fdcb429c19b7d29c72dfca7d893f608a9f66f5cc0eb53d5c20d29  docs/claims-and-verification.md
2b03510a53fa97b5079fabf109aaf8af3d440e18b53324c48b91684c4dc4c43d  docs/evidence-and-reproducibility.md
8ba64525354917ab0cf9995955e87d11d86bbf42b147b28b36ae7a43b0c2347e  docs/focused-autoresearch-loop.md
a390605329527d92a3bc97d2cd9e73cd63a626fdb6d7a588df3d6c9e28a578dc  templates/research-records.md
03c41440421a58af2cdec435b0f54378126a000d52a668bea546358558372f73  coordination/goals/GOAL-ECDLP-001/batches/BATCH-001/archives/TASK-20260721-009/snapshot_commit_receipt.json
ed49ca9bc9c01f4f6a02a611a3059e67b339617f45e438597cd26f3500df572b  coordination/goals/GOAL-ECDLP-001/batches/BATCH-001/dispatch_queue.v3.json
e1b9d86c2fc556d77479cc61f6945e817cbb2fc2557e4e149a0906e8b3312415  coordination/goals/GOAL-ECDLP-001/batches/BATCH-001/tasks/TASK-20260721-008/methodology_frontier.yaml
a81e28c53c8802c3240dc09d8401e8fd323b738bab06a29a978c2ad2f013b2a2  coordination/goals/GOAL-ECDLP-001/batches/BATCH-001/tasks/TASK-20260721-008/cost_audit.md
7c8fa3f33ebba021a3c4caca6207378c5c88cac585b5d665bdc0692c75ab5d0e  harness/runner.py
a0699ac3564bd20f96e283027484b4eca2b100ed5f0109087ed7dcd7bb9efffc  tools/validate_ledger.py
0cb9a2f037896e947497c5362abc5b402d801bbcd836826d4488ac8f54d9f0a9  knowledge/techniques/KN-TECH-005.md
a92953c89ecb671d7264416b075631263cb9d4ce0cb0240f1395a04265d8e080  knowledge/techniques/KN-TECH-006.md
c68ff8d6fccce5dad969e4e6b0c42d60ae1d9c30f1c846edd3953b9a677e57a9  knowledge/literature/KN-LIT-013.md
7b9458592f777da4a50df4388997e72e7cd9bd265e9df16c4b21fd1c4a9840b3  experiments/EXP-ICI-001/analysis.md
8cf15364c2da6830255216f3766a5d016b847d4bd012df92fd86c462ee6a9bc1  ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md
da42d4ec1ce90a6338d89e84d9248e4044c694b91a229ecb9cdf703c4592d9fa  ideas/reviews/DEDUP-20260721T171454-0700.md
6b0c023f5960e6f06c8b919e0608b351f88a9c10ec046808d4ef75863788a94c  ideas/reviews/REDTEAM-20260721T172536-0700.md
```
