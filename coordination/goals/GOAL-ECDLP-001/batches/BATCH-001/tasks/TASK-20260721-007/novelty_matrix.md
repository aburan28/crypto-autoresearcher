# TASK-20260721-007 operation-level novelty and complete-cost matrix

Terminal verdict: `FRONTIER_ONLY`.

This is proposal/frontier analysis only. It is not evidence, a validated
improvement, or a breakthrough. No experiment, solver, relation campaign,
factor-log solve, blind target attack, or live-system action was run.

## Runtime metadata

- `requested_policy: research-sol-max`
- `resolved_model_id: gpt-5.6-sol-high`
- `reasoning_effort: high`
- `fallback_used: true`
- `adapter_version: unavailable_not_exposed_by_cursor_runtime`
- `adapter_version_available: false`
- `authorization: DEC-20260721-002`

The adapter version is recorded as unavailable because the Cursor runtime did
not expose an adapter version to this session. No version was inferred or
fabricated.

## Inspected boundary

- Repository: `/Volumes/Volume/crypto-autoresearcher`
- Branch: `main`
- Commit: `7885e51da107b25d91ed79dcc7374f7548f72dd3`
- Cutoff: `2026-07-22T03:16:40Z`
- Required roots: `AGENTS.md`, `agents/idea-generator.md`, `ledger/`,
  `experiments/`, `knowledge/`, `ideas/`, `focus/`,
  `coordination/dispatch_queue.json`, and
  `ledger/decisions/DEC-20260721-002.yaml`.
- Inventories screened: 125 ledger files, 942 experiment files, 44 knowledge
  files, 116 focus files, and the complete idea corpus plus the concurrent
  dirty delta.
- The pre-`20260721-c` 894-file idea-tree content manifest is
  `82d9fe9e8c224470e3d12c1688355a8910aa3758f9c3200779d7508d46b3ba78`.
- The corrected `20260721-c` 15-file package manifest is
  `979e9a2c1a8ed9b7dec68d8b38d023b1af06a3de1f43f8b4a1ba2418b60497e1`.
- The concurrent `20260721-d` twelve records and three retired contract
  snapshots were read and are bound individually in `mechanism_frontier.yaml`.
- The exact dirty path groups, modified-file blobs, decisive-input blobs, and
  all `20260721-d` blobs are recorded in `mechanism_frontier.yaml`. Every dirty
  path is under `ideas/`; none was edited by this task.

The most recent independent content review at the cutoff is
`ideas/reviews/REDTEAM-20260721T172536-0700.md`. It upheld the `20260721-c`
no-survivor dispositions but remained non-durable because the package had no
preceding Coordinator snapshot commit. The later `20260721-d` delta had no
DEDUP/REDTEAM review at the cutoff and is therefore treated only as unreviewed
preallocation evidence.

## Matched controls and cost convention

Let the prime subgroup have order `N` and set `B=N^(1/5)`.

- Pollard rho: expected total work `N^(1/2+o(1))`; parallel processors reduce
  wall time but not matched total work.
- BSGS: time and memory `N^(1/2+o(1))`.
- Generic fixed-curve preprocessing: `S*T^2=Omega_tilde(epsilon*N)`.
  Therefore setup `S<=N^0.45` and fresh query `T<=N^0.25` cannot be credited
  with constant success as a generic method; such an interface must prove a
  non-generic, non-simulable information source.
- A relation route must charge preprocessing, relation density, collection,
  independent rank, factor-log linear algebra, fresh scalar-blind descent,
  output, ambiguity, verification, bit complexity, memory, and total parallel
  work.

The frozen complete gates are

```text
lambda = max(a, beta+delta+q-r+o, ell,
             delta_t+q+o+u, beta)

mu = max(a_m, q_m, beta+o, ell_m, u)

beta = 1/5; promotion requires lambda,mu <= 0.45.
```

## Operation-level matrix

### 1. Generic collision and preprocessing

- Mathematical object: opaque encodings in a prime-order group.
- Operation: collision search, generic table lookup, or advice/query tradeoff.
- Information source: group-operation and equality oracles only.
- Output: the scalar discrete logarithm.
- Nearest semantic predecessors: `KN-TECH-001`, `KN-TECH-005`,
  `KN-LIT-011`, and `KN-LIT-013`.
- Full-cost result: rho and BSGS already attain exponent `0.50`; generic
  preprocessing is constrained by `S*T^2`. Online-only savings are not an
  end-to-end or multi-target gain after advice, state, success, and
  amortization are matched.
- Disposition: no candidate.

### 2. Endomorphism, isogeny, and representation transfer

- Mathematical object: an endomorphism, isogeny, cover, jet, elliptic net,
  pairing target, trace-zero representation, or global lift.
- Operation: split an orbit or transfer the DLP, then return an oriented scalar
  or exact source.
- Information source: public curve structure excluded by the generic model.
- Output: a scalar or verified source relation after return.
- Nearest semantic predecessors: `ECDLP-IDEA-002`, `004`, `006`, `008`,
  `009`, `160`, and the P1540-P1548 audits.
- Full-cost result: fixed degree changes constants, not the square-root
  exponent. Growing degree restores construction/state; pairing targets need
  another DLP; tested jets and net identities were simulable, universal, or
  k-unspecific in their audited scopes. Exact scalar-blind return remains
  missing.
- Disposition: no candidate.

### 3. Relation collection and blind descent

- Mathematical object: five signed factor decks and the six-list
  Abel-Jacobi/Semaev relation fibre.
- Operation: exact subset-stable target existence followed by one signed
  occurrence replay.
- Information source: a public endpoint-derived algebraic reporter, not a
  supplied source catalogue.
- Output: a verified relation row and a fresh masked-target decomposition.
- Nearest semantic predecessors: `ECDLP-IDEA-012`, `121`, `156`, `195`,
  `199`, `266`, P1513, P1551, P1516, and P1553 R4.
- Full-cost result: determinant, wedge, trace, norm, Fitting-ideal, tensor, and
  coefficient identities are local predicates or aggregates. Standard
  constructions restore `B^3` pair-plus-singleton traffic, `B^4` pair-pair
  traffic, or a `B^5` source algebra. No exact reporter/update/source inverse
  is constructed.
- Disposition: frontier only.

### 4. Structured linear algebra and solver substitutions

- Mathematical object: a represented sparse relation matrix or source
  transition operator.
- Operation: Wiedemann, block Krylov, displacement solving, Arnoldi,
  reordering, or projection.
- Information source: relation rows or operator nonzeros that already encode
  source incidence.
- Output: factor logs, a kernel vector, Ritz data, or an aggregate
  certificate.
- Nearest semantic predecessors: `ECDLP-IDEA-056`, `KN-TECH-008`,
  `KN-OPEN-006`, `EXP-STR-001`, and preallocation records
  `20260721-d-L06/L12`.
- Full-cost result: this changes a backend after relation supply. In
  `EXP-STR-001`, the AP restriction had displacement rank proportional to `B`
  and a growing supply penalty; collection dominated any solve saving.
  Arnoldi likewise requires the missing exact operator and source lift.
- Disposition: no candidate.

### 5. Special-curve attacks

- Mathematical object: anomalous, pairing-friendly, low-embedding-degree, or
  otherwise exceptional curves.
- Operation: exploit a family-specific map or representation defect.
- Information source: exceptional public curve parameters.
- Output: the scalar on that restricted family.
- Nearest semantic predecessors: `KN-TECH-005`, `KN-OPEN-001`,
  `ECDLP-IDEA-005`, and `ECDLP-IDEA-009`.
- Full-cost result: these constructions do not apply to the declared generic
  ordinary prime-field prime-order setting. Restricting the input family is a
  scope change, not a generic ECDLP improvement.
- Disposition: no candidate for this task.

### 6. Multi-target and fixed-curve amortization

- Mathematical object: target-independent advice shared across public targets.
- Operation: preprocess once, then answer scalar or descent queries.
- Information source: retained fixed-curve advice.
- Output: one or many logarithms.
- Nearest semantic predecessors: `KN-LIT-013`, `KN-TECH-005`, and P1553 R4.
- Full-cost result: the generic preprocessing tradeoff rules out an uncharged
  generic gain. No non-generic advice constructor with exact source replay,
  factor logs, fresh blind descent, memory, and matched target count survived.
- Disposition: no candidate.

## Narrowest unresolved mechanism

The only checkable residual is an oracle-free, gauge-invariant,
restriction-aware elliptic unit-product constructor.

Its mathematical operation would be:

1. take public complete-chart source-labelled pair-divisor trees;
2. construct, rather than receive, the mixed target/source elliptic-net or
   division-polynomial terms needed for `r_R mod g_I`, or equivalent exact
   dyadic unit products;
3. decide exact restricted Query2P1 existence for a fresh target; and
4. replay one signed occurrence with `O(log B)` restriction calls.

This would be operation-level distinct from:

- evaluating a recurrence after mixed terms are supplied;
- computing a fast gcd after `r_R mod g_I` is represented;
- applying a solver to a supplied source graph, matrix, text, or distribution;
- naming a determinant, norm, coefficient, or existence oracle without
  constructing it.

The only admissible new information source is a proved gauge-invariant
normalization and recurrence derived from public complete elliptic
addition/division-polynomial coefficients. Hidden scalar characters, pairing
target logarithms, source tuples, mixed-resultant oracles, target-trained
branches, and `B^3` provenance are forbidden inputs.

## Complete conditional route and cost

If the missing constructor existed and all remaining assumptions held:

1. Build five signed coloured factor decks of size `B`.
2. Build two source-labelled dyadic pair-divisor indexes in
   `B^(2+o(1))=N^(0.40+o(1))` state/work.
3. Answer one exact fresh target in
   `B^(5/4+o(1))=N^(0.25+o(1))`.
4. Replay and verify one occurrence with `O(log B)` restrictions.
5. Query `B` known-log targets; total query work is
   `B*B^(5/4)=B^(9/4)=N^0.45`.
6. Require `Theta(B)` independent verified rows and full factor-base rank.
7. Solve every factor log with a charged `B^(2+o(1))=N^0.40` baseline.
8. Reuse unchanged state on `Q+[t]P`, recover a signed decomposition, compute
   the scalar, and verify by scalar multiplication.

The resulting gate arithmetic is conditionally `lambda=0.45` and `mu=0.40`.
Those numbers are not an achieved complexity bound. They assume the missing
constructor, exact exceptional-stratum behavior, useful density, independent
rank, factor-log completion, and identical scalar-blind descent.

## Cheapest decisive test and falsifiers

The cheapest decisive test is theorem-only: enumerate every recurrence index,
seed, coefficient source, gauge action, dependency edge, represented
dimension, target update, and dyadic restriction update. Expand the first mixed
term that is not derived from public pair-tree data.

The route is falsified if any of the following occurs:

- a mixed net, norm, resultant, or recurrence term is supplied;
- gauge rescaling changes the gcd, unit product, or existence decision;
- an admitted zero, pole, tangent, vertical, identity, infinity,
  repeated-label, collision, or nonreduced stratum is answered incorrectly or
  cannot replay an occurrence;
- one target/restriction restores `B^3` traffic or exceeds `B^(5/4)`;
- setup/state/campaign exceeds `B^(9/4)`;
- density, rank, factor logs, blind descent, output, bit cost, memory, or
  parallel work makes `lambda` or `mu` exceed `0.45`; or
- the augmented interface is generically simulable with constant overhead.

Important confounders are supplied recurrence terms, known-scalar target
orientation, incomplete affine charts, sparse toy decks with poor generic
coverage, output-sensitive gcd degree without source backpointers, and
parallel wall-time claims that hide unchanged total work.

## Exactly one next target

Prove or refute an oracle-free, gauge-invariant elliptic-net or
division-polynomial constructor for `r_R mod g_I`, or equivalent exact dyadic
unit products, with `B^(9/4+o(1))` total setup/campaign,
`B^(5/4+o(1))` fresh-target work/workspace, exact all-strata restricted
existence, and `O(log B)` signed source replay; if construction fails, identify
the first required mixed seed or represented state that exceeds a cap.

No candidate survives until that theorem target is met and the complete path
is independently reviewed.
