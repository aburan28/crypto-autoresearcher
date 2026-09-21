# Independent review of SOURCE-LOCATOR-OPEN admission

## Result

**Verdict:** `NO_ADMISSIBLE_OPERATION`  
**Upholds producer:** `yes`  
**First failed requirement:**
`requirement_1_explicit_semantically_distinct_operation`  
**Breakthrough claimed:** `false`

This verdict applies only to the checked, Coordinator-committed snapshot. It
does not assert that a source locator is impossible, that the checked corpus is
literature-exhaustive, or that any unrestricted non-generic ECDLP lower bound
has been proved.

## Snapshot check

The dispatch queue identifies snapshot commit
`502f084b5b42a3d6041cbfab3570c7cab2893529`, parent
`2e8682d6c16ca61ab64bc7f971c8e4c23489c778`. The commit is reachable from
`HEAD`; it changes exactly the two TASK-20260723-601 artifacts and the
TASK-20260723-602 receipt. Their SHA-256 values match the post-push dispatch
record:

- `admission_report.yaml`:
  `325280d59fcc4e350565a986cd22cd25d6a4328c0f80ff57a7be560e3d38a418`
- `source_locator_admission.md`:
  `aaaf92797659c0f3e866964725a49211978978b7fa0111f7144f43d7df2234e3`
- `snapshot-receipt.json`:
  `5370507eb2e11494deccf3135d8820163aca6f72975d9629ac151ee8cd3d4d2e`

The receipt inside the snapshot still says `pending_post_commit` and has null
commit fields. That is the immutable pre-commit template. The later
Coordinator dispatch record supplies the verified commit, parent, path set,
and hashes; it is the authority used for this review.

## Independent recomputation

With \(B=N^{1/5}\),

\[
B^{5/4}=N^{0.25},\qquad
B^{9/4}=N^{0.45},\qquad
B^{5/2}=N^{0.50},\qquad
B^3=N^{0.60}.
\]

The campaign gate is inclusive: \(\lambda,\mu\leq0.45\). Pollard rho's
\(0.50\) work exponent is a comparison baseline, not a relaxed admission
gate. Thus an exponent in \((0.45,0.50]\) still fails.

The named source-labelled six-list control materializes two triple spaces for
a \(3+3\) match and has complete work \(B^{3+o(1)}=N^{0.60+o(1)}\). Its
direct materialized state is also \(B^3\). For one fresh five-factor target, a
\(2+3\) split can reuse \(B^2=N^{0.40}\) pair state but still enumerates
\(B^3=N^{0.60}\) work. These costs exceed the campaign gate and the stated
\(N^{0.25}\) complete fresh-query gate.

One wording guard is necessary: \(N^{0.60}\) is the cost of this named direct
control, not a proved lower bound on all source-faithful algorithms. The
producer verdict remains valid because no alternative explicit operation is
supplied; it must not be recast as a universal \(0.60\) lower bound.

## Mechanism, representation, and source recovery

No checked object has all of:

1. typed public inputs and outputs;
2. target-independent preprocessing and advice provenance;
3. admitted-stratum and subset-restriction semantics;
4. exact colour, sign, and occurrence-label output; and
5. an inlined cost path through every backend.

The determinant, pair-wedge, and endpoint predicates verify supplied tuples or
endpoints. They do not recover which occurrences produced an endpoint.
Supplying a residue, scalar, source tuple, source dictionary, or \(B^3\)
provenance assumes the missing inverse. Renaming a compact-factor routine,
zero-minor locator, hyperplane-signature resolver, or target-fitted coefficient
builder does not instantiate it. This confirms requirement 1 as the first
failure.

Duplicate endpoints are decisive for the representation contract. Two equal
public points with different occurrence labels must remain distinguishable.
An endpoint-only transcript, canonicalized dictionary, or deduplicated subset
cannot support exact signed occurrence replay.

## Mandatory \(O(1)\)-overhead GGM exclusion

The required comparison is transcript-level. A relation transcript must
contain the target occurrence and five signed source occurrences; a fresh
transcript must contain the scalar-blind masked target tag and five signed
source occurrences. Public group equality then verifies the tuple.

For a supplied constant-size tuple, the named determinant or pair-wedge zero
bit is equivalent on the admitted stratum to checking a constant-size group
sum. A generic simulator can reproduce that bit with \(O(1)\) group
operations and equality testing. Coordinate syntax that disappears after
encoding erasure is not, by itself, simulator separation.

There is no candidate locator, output distribution, or complete transcript
for which non-reproducibility could be proved. Therefore no non-generic
advantage receives credit. This is not a lower bound against an unspecified
future locator; it is an exclusion of the named supplied-tuple predicates and
of operations that hide the source inverse behind an oracle.

## Replay and rank charging

The producer's replay count is conditionally sound. For an exact
occurrence-labelled rectangular existence operation, split occurrence-label
intervals in a frozen depth-first binary tree. If \(s\) positive singleton
leaves are emitted and a leaf has depth

\[
D_k=\sum_{h=1}^{k}\lceil\log_2 |S_h|\rceil=O(\log B),
\]

querying both children of every positive internal node requires at most
\(1+2sD_k\) calls. The bound includes empty siblings and preserves duplicate
occurrences. Polylogarithmic depth does not make calls free: every restriction
rebuild, target translation, miss, output, and group-equality verification
inherits the underlying call cost. Cached restrictions, source sidecars,
ambiguity lists, and traversal frontiers remain live memory.

This is only a reduction from exact restricted existence to replay. No checked
operation implements the restricted call, so replay cannot be credited.

The relation matrix needs rank \(\Theta(B)\) over the actual factor columns.
An expected \(\Theta(B)\) incidence or row count does not imply independent
rank. A pass requires either deterministic rank or a tail bound for the frozen
deck and target distribution. Under a probabilistic bound, every deficient
batch pays relation location, replay, misses, verification, rank computation,
discarded storage, rebuilds, and retry traffic.

Neither a deterministic guarantee nor a tail bound is present. Consequently
positive rank credit is unavailable and the rank-retry exponent is unknown,
not zero. For a future candidate, the unit called a “batch” must be frozen so
the same rank gain is not counted through both the per-batch rank parameter
and the full-rank acceptance parameter.

## Cheapest discriminating mutation

Use a zero-compute duplicate-occurrence relabel and backend-erasure control:

1. duplicate one public endpoint under two occurrence labels;
2. independently permute occurrence labels and signs;
3. freeze all preprocessing before revealing a fresh scalar-blind target; and
4. replace every unnamed locator backend by its declared public transcript.

The operation must emit the correspondingly permuted signed occurrences at
the same fully charged asymptotic cost. Endpoint output cannot distinguish the
duplicate labels. Dependence on original labels, fitted coefficients, a hidden
dictionary, or an undeclared resolver exposes leakage. A supplied-tuple
equality bit remains \(O(1)\)-GGM-simulable. Only an inlined, equivariant
locator with a complete relation-to-rank-to-fresh-target path survives.

## Baselines and narrow conclusion

- Pollard rho: \(N^{1/2+o(1)}\) expected work and \(N^{o(1)}\) serial memory.
- Baby-step/giant-step: \(N^{1/2+o(1)}\) work and memory.
- Closest specialized control: source-labelled six-list \(3+3\) matching,
  with \(N^{0.60+o(1)}\) complete campaign and fresh-target work.

The checked specialized control is worse than Pollard rho in work and misses
the \(0.45\) gate. Speculative \(N^{0.40}\) streaming state cannot repair its
stated \(N^{0.60}\) work, absent rank yield, missing source recovery, or
missing fresh-target descent.

The narrow supported statement is therefore: the committed
TASK-20260723-601 snapshot supplies no explicit operation that reaches the
repaired admission stage. Requirement 1 fails first; simulator exclusion,
subset-stable replay, rank/retry accounting, backend provenance, fresh-target
descent, and complete \(\lambda,\mu\) certification also remain unsatisfied.

## Coordinator handoff

The one next action is for Coordinator TASK-20260723-604 to ledger-archive
this scoped upheld verdict and both TASK-20260723-603 artifacts without
enlarging it into a lower bound or changing official state outside Coordinator
authority.
