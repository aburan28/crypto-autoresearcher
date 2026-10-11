# Coordinator design audit: SNFS-G4 rotation control

```yaml
task_id: TASK-20261010-30d9e5
idea_id: IDEA-20261009-354b14
goal_id: GOAL-ECDLP-001
disposition: proposed
approved: false
scientific_result: none
```

## Audit findings

This is a design audit, not an approval, dispatch, hypothesis edit, status
transition, or experiment result. The source provenance is internal repository
evidence: `AGENTS.md`, `agents/coordinator.md`,
`ledger/proposals/IDEA-20261009-354b14.yaml`,
`ledger/hypotheses/H-ECDLP-bd1572.yaml`, the SNFS-A1 proposal
(`IDEA-20261009-0f3a09`), the SNFS-A4 proposal
(`IDEA-20261009-443717`),
`coordination/intakes/20261009-snfs-ecdlp-ledger/source-addendum.yaml`, and
the associated intake audit. The reviewed repository tree also contains the
adjacent factor-base and Semaev-control records named by those proposals.

The exact duplicate check searched the reviewed repository for
`rotation-minimal`, `rotation_minimal`, `D_rot`, the SNFS-G4/A4 identifiers,
and the proposed Semaev/two-sum path. The only rotation-minimal predicate
references found were the G4 proposal and its source addendum; no existing
implementation of that predicate was found. Adjacent controls do exist,
notably SNFS-A1's prime-form algebra control, SNFS-A4's digit-prefix control,
and the internal small-coordinate factor-base records. This is a repository
scope finding, not a claim that no implementation exists elsewhere.

Two repairs are mandatory before any runnable contract is considered. First,
`D_rot` cardinality must be enumerated exactly in the selected subgroup; it
must not be assumed to be `p/2^m`, or even inferred from the ambient-field
density. Second, multiplication by 2 is only a coordinate predicate on the
chosen representation of `F_p`: the cyclic bit rotation does not define a
fixed-curve group action on `E(F_p)`. The model-scaling observation in the
proposal is an isomorphism between curve models whose inverse cancels; it is
not a point endomorphism and does not establish subgroup closure or a group-law
symmetry.

The current harness is not runnable as-is. The records say “reuse A1 / A4
harness” but do not identify a runnable experiment contract or an existing
rotation implementation. Missing work includes the predicate and unit tests,
exact subgroup/ordinary-curve fixture certification, exact cardinality and
identity handling, Semaev/direct-addition cross-checks, matched controls,
clustered statistical analysis with Holm correction, and raw-artifact/replay
receipt production. A future design session must implement and specify these
items without editing the immutable idea or adjacent proposal records.

## Proposed future measurement contract

The following is a proposed, not approved, bounded measurement. Its initial
core is `c in {13, 17, 19}` and `m in {1, 2, 4, 8}`, always subject to
`m < c`. Every cell requires a certified ordinary curve and a certified
selected subgroup `H = <G> <= E(F_p)` with known order and a checked generator;
the identity is excluded from factor bases because it has no x-coordinate.
`c in {31, 61}` is explicitly excluded from the initial runnable contract and
would require a later specification review.

For a non-identity `P in H`, encode `x(P)` as the specified c-bit word and
define

```text
rho(P) = min_{0 <= j < c} rot_c(x(P), j)
D_rot(H;c,m) = { P in H \ {O} : rho(P) < 2^(c-m) }.
```

The implementation must enumerate `H`, compute `d_rot = |D_rot|` exactly,
and publish the count and digest. It must not substitute `p/2^m`, `|H|/2^m`,
or a sampled estimate. The matched random-subset arm has exactly `d_rot`
members; the A4-prefix arm and the random-prime size-based arm also publish
their natural cardinalities and use an explicitly specified exact-size
matching procedure for any cross-arm comparison.

The exact closure statistic for a finite nonempty arm `A <= H` as a set of
points is

```text
C(A) = (1 / |A|^2) * sum_{P in A} sum_{Q in A} 1[P + Q in A],
```

with ordered pairs, multiplicity retained, the group operation performed in
`H`, and `O` treated according to the stated membership predicate. The
primary null is the same-group random-subset distribution at the exact size
`|A|`; `|A|/|H|` is a descriptive density only and is not declared to be the
exact closure expectation without a separate derivation. The exact two-sum
decomposition statistic for a declared target panel `T subseteq H` is

```text
N_A(R) = |{ (P,Q) in A x A : P + Q = R }|
F(A,T) = (1 / |T|) * sum_{R in T} 1[N_A(R) > 0].
```

The same ordered-pair convention, target panel, identity rule, and duplicate
handling must be used for rotation, matched random-subset, A4-prefix, and
random-prime arms. If S3 root counting is used, every reported root count is
cross-checked against direct group addition on the certified fixture; a root
count alone is not a decomposition certificate.

The fixed sample plan is three independent seed clusters per cell and arm,
with 1,000,000 uniformly generated ordered closure pairs and 100,000 uniformly
selected targets per cluster. Exact subgroup enumeration and exact arm
cardinalities occur before sampling. The primary uncertainty unit is the
cluster, not the individual pair: report per-cluster estimates, a cluster-level
95% interval (with the declared small-sample method), and the aggregate only as
secondary context. The planned family is fixed before data: two metrics
(`C` and `F`) x twelve cells x three contrasts (rotation versus matched
random-subset, A4-prefix, and random-prime), 72 tests. Report raw p-values and
Holm step-down adjusted p-values at family alpha 0.05; do not add or remove
tests after inspecting results.

Seeds are domain-separated and deterministic, for example
`SNFS-G4:TASK-20261010-30d9e5:<c>:<m>:<arm>:<metric>:<cluster>`. No seed,
target stream, or pair stream may be reused across arms or metrics. The run
stops only after all fixed cells, arms, clusters, and receipts are complete.
There is no optional stopping, replacement of an invalid fixture with a more
favorable one, or extension to c=31/61. A composite prime, non-ordinary or
uncertified curve, wrong subgroup order/generator, identity mishandling,
nonuniform sampler, seed collision, missing control, predicate mismatch, or
missing raw/replay artifact invalidates that cell or run. A timeout, crash, or
implementation failure is infrastructure and is not mathematical evidence.

## Required artifacts and claim ceiling

The future implementation must retain a frozen protocol and source manifest;
curve identifiers and equations; p and subgroup-order certificates; generator
checks; encoding and rotation-predicate tests; exact membership/cardinality
lists or lossless bitmaps with hashes; raw pair and target streams or an
equivalent replayable record; per-cluster raw machine-readable results;
statistics, confidence intervals, raw and Holm-adjusted tests; stdout/stderr;
exact command; source commit and dirty-tree state; environment and dependency
versions; timestamps and resource measurements; and a replay receipt that
recomputes the artifact hashes and all reported counts from the frozen seeds.

The claim ceiling is a finite control on the stated ordinary fixtures and
sampled scope: closure and two-sum decomposition comparisons only. It permits
no group action claim, asymptotic claim, algorithm claim, key or deployed-curve
claim, or ECDLP improvement. `dominated_by` is
`KR-IC-5931ee` plus the SNFS-A1 and SNFS-A4 control arms; `sota_delta` is
exactly `0` (only a reusable finite control table could be added).

No scientific conclusion is recorded here. In particular, this audit records
neither a positive nor negative ECDLP finding and makes no status transition.
The idea remains `proposed`; it is not approved or dispatched. Because this is
a design-only audit and the requested write scope is exactly this file, no run,
evidence-review graph, or PDF is generated.
