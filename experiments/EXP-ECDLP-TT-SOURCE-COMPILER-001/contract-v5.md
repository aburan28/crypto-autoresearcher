# Experiment Contract: exact first-norm source-TT compiler v5

Version 5 preserves the v1-v4 review history and makes every factorization
count phase-scoped. It freezes the source subtotal, withheld target delta, and
harness-only campaign-total equations without exposing target schedule data to
the source process.

## Protocol status

`APPROVED_FOR_SOURCE_IMPLEMENTATION_ONLY`. Independent theory, accounting, and
red-team reviews have passed and are recorded in `theory-review-v2.md`,
`accounting-review-v2.md`, and `red-team-v4.md`. This state authorizes source
implementation and focused development tests after the protocol-only tree is
frozen in a clean Git commit. It does not authorize a baseline, mutation, or
registered experiment run; those require the separate post-implementation gate
defined in `implementation-authorization-v1.md`.

## Hypothesis

The literal five-source RCB circuit can be executed with exact finite-field TT
arithmetic to construct the five trace-zero source tensors without enumerating
the `B^5` source tuples.

## Null hypothesis

The literal gatewise compiler is semantically wrong, fails exact
recompression, hides tuple enumeration or uncharged state, or crosses a frozen
work or memory gate before completing the mandatory schedule.

## C1: claim boundary

Passing supports a restricted constructive result for the first norm on the
frozen toy schedule. It does not support a Fermat locator, witness recovery,
relation generation, an index-calculus complexity, target descent, or an
ECDLP improvement.

The target-blindness claim is `MODEL-BOUND` to the isolated staged process,
closed IR, transitive source/call-graph audit, withheld-literal audit, runtime
filesystem/environment trace, and registered mutations. It is not an
information-theoretic claim against arbitrarily obfuscated malicious source.

## C2: frozen inputs and schedule

The inherited selection source remains
`../EXP-ECDLP-TT-NORM-RANK-001/instance-manifest-v1.json`, but no source process
may read it. `source-instance-manifest-v1.json` is the complete target-redacted
source input and `source-execution-matrix-v2.json` is its target-free execution
contract. The full execution matrix and `target-instance-manifest-v1.json` are
withheld until the source advice and its receipt are frozen. Only these entries
are mandatory:

```text
C08: p=8-bit registry size B=3
C10: p=10-bit registry size B=4
C12: p=12-bit registry size B=5
```

For each curve, compile `random_unique` and `x_interval`. This gives six
source-compilation cells. The mode order is `(P1,P2,P3,P4,P5)`, all five modes
use the named registry, and the tree is
`Add(Add(Add(Add(P1,P2),P3),P4),P5)`.

Each cell emits exact TTs for `X,Y,Z,X2,XZ,Z2,XY,YZ,Y2`. The retained advice is
exactly `X2,XZ,Z2,YZ,Y2`; the other cores are diagnostic certificates.

One mandatory non-retained control recompiles `C08:random_unique` after scaling
the five projective input modes by `(2,3,4,5,6)`. With source multidegree
`(16,16,8,4,2)`, the frozen coordinate and quadratic scale factors are 124 and
80 modulo 239. It emits nine source tensors and one Q00 target tensor but no
retained advice.

Target specialization cells are:

```text
random_unique: Q00,Q01,IDENTITY,PLANTED
x_interval:    Q00,Q01
all six source cells: GENERAL_TRACE_Q00 control
```

This gives 18 original trace-zero target TTs, one rescaled trace-zero control,
and six general-basis controls, for 25 target TTs. The inherited targets and
extension constants are not selected or replaced. Each general-basis control
freezes `t=1,n_control=1`; the exact discriminants, Legendre checks, target
projective coordinates, and both coefficient vectors are in the target
manifest before source implementation, but are unavailable to that process.

## C3: phase-separated construction path

The source compiler must:

1. parse and hash only `source-instance-manifest-v1.json` and
   `source-execution-matrix-v2.json` as data inputs;
2. audit curve, registry, mode-order, tree, and RCB-gate provenance;
3. create coordinate inputs only as mode-local rank-one TTs;
4. execute the literal 40-gate RCB schedule four times per source cell;
5. use only exact TT direct sums, streamed Hadamard products, scalar
   multiplication, and exact finite-field recompression;
6. build the six quadratic source tensors and retain the five trace-zero
   sources;
7. evaluate only the preregistered constant-size diagnostic sample list;
8. emit canonical advice, cores, IR/gate traces, accounting, certificates, and
   provenance to stdout.

The source verifier independently checks the seven source cells, canonicalizes
the five retained sources per primary cell into `frozen-source-advice.json`,
and separately canonicalizes the non-retained `XY` sources and modewise-
rescaled control sources into `frozen-source-control-certificates.json`. Its
receipt binds both SHA-256 digests while counting only the five-source primary
bundle as retained advice. The source compiler process then terminates. Only
after that receipt exists may a separate target-specialization process read
the target manifest and both frozen source artifacts. It derives and checks
target coefficients, executes 25 five- or six-source linear combinations, and
emits a separate ledger. Reversing target order must leave both frozen source
artifacts and digests unchanged.

Neither process may import prior generated tensors, rank tables, source tables,
verifier code, or the mutation manifest. The source process may not read the
inherited or target manifest. It must not enumerate the Cartesian source
product, construct an unfolding from tuple values, or use an affine group
oracle to assign a TT core.

The source-visible capability boundary is frozen in
`source-execution-matrix-v2.json`; the harness-only full boundary is frozen in
`execution-matrix-v4.json`.
Data inputs, the hashed local source closure, the pinned Python/NumPy package
closure, and operating-system loader reads are four separate categories. No
process may use dynamic imports or code, child processes, network access,
unbound helpers, five-dimensional arrays, or generic physical tuple iterators.
All dense arrays pass through audited allocation and free events; no producer
array may have more than three dimensions.

The compiler is an interpreter over the closed IR
`input_coordinate,scale,direct_sum,stage_a_contract,stage_b_contract,
rank_factor,absorb_left,absorb_right,emit,free`. Every allocation and output
must have one traced IR producer. Each primitive receives at most one physical
mode and one slice. A complete transitive AST/call-graph audit separately
rejects `B**5`, constant-folded equivalents, five radix decodes, five-source
products, nested physical loops, and untraced arithmetic or allocation paths.

Both source processes run from isolated staging roots containing only their
hash-bound local source closure, the two source-visible data files, and, for
verification, the source raw result. No repository `.git` metadata, inherited
manifest, full matrix, target file, mutation file, or prior artifact is staged.
Runtime auditing covers open/stat/listdir/scandir/glob/readlink/chdir events and
forbids directory enumeration outside the declared runtime/package closure.
Only the frozen deterministic/thread-control environment variables are
readable. Both processes emit JSON only to stdout; the harness writes the two
frozen source artifacts and receipt after verification.

## C4: exact TT semantics

All core entries are canonical integers in `[0,p)`. Core shapes must join,
boundaries must equal one, and every operation must preserve five physical
modes of size `B`.

The exact factorization routine uses finite-field elimination with frozen
lexicographic pivots. It emits both factors, pivot columns, rank, factor digest,
and operation/traffic counters. Final exact recompression uses two sweeps:

1. left to right, reshape each visited core as `(r_(j-1)*B) by r_j`, factor,
   retain the left factor, and contract the right factor into the next core;
2. right to left, reshape each visited core as `r_(j-1) by (B*r_j)`, factor,
   retain the right factor, and contract the left factor into the preceding
   core.

The first sweep makes prefix interfaces full column rank; the second makes
suffix interfaces full row rank and reduces every nonzero bond to the exact
unfolding rank. A rank-zero factorization returns a tagged canonical zero with
exact ranks `(0,0,0,0)`. Nonzero scalar multiplication changes the first core,
requires no sweep, and emits a rank-preservation certificate; scalar zero
returns the canonical zero. Addition, subtraction, and Hadamard product always
invoke both sweeps. Streamed prefix ranks and raw direct-sum or product ranks
are reported separately and never called exact ranks.

The streamed Hadamard routine may hold only operand cores, the incoming
transfer, one local matrix, its factorization workspace, the emitted prefix,
and accounting metadata. A full raw five-core product is prohibited.

The producer reshapes the transfer as `(s,la,lb)` and, for each physical slice,
contracts first over `la` with the A core and then over `lb` with the B core.
It may not materialize a Kronecker slice. At C12/B5, both the largest stage-A
workspace and largest stage-B output slice are 15,625 words; the latter occurs
at mode 3. The local factorization matrix and transfer maxima remain 78,125
words.

Exact dense kernels use the bound Python 3.13.1 executable and installed NumPy
2.4.0 closure in `execution-matrix-v4.json`, signed int64, C order, one thread,
and only its operation allowlist. The executable SHA-256, all 1,320 NumPy file
digests and closure digest, `_multiarray_umath` digest, architecture, loaded
extension paths, and OS loader paths are attested before work. The standard
library files actually read are hashed into the pre-run runtime receipt. A
matching version string with a different closure is rejected.

Before every kernel the process asserts canonical residues and the actual
dot-product overflow bound; after every kernel it reduces modulo `p`. `kron`,
`einsum`, `tensordot`, NumPy index-grid helpers, object dtype, floating
conversion, and `np.linalg` are prohibited.

## C5: independent verifiers

The source and target verifiers must not import producer modules or reuse a
producer TT evaluator, finite-field elimination, RCB routine, tuple iterator,
target coefficient routine, IR interpreter, or accounting calculator.

For every source-compilation cell it independently enumerates all `B^5`
tuples in a different traversal and computes the frozen left-associated sum by
an independently transcribed RCB evaluator. It checks all nine TT values.
After the source receipt is frozen, the target verifier independently derives
every trace-zero and general-basis coefficient vector from the projective
target and extension constants, checks it against the target manifest, and
checks the target TT value. It independently unfolds every nonzero emitted
tensor and checks all four exact ranks.

Verifier enumeration, rank work, traffic, memory, and time are reported in
their own partition ledgers and may never be reclassified as source
preprocessing or online specialization.

For `C08:random_unique`, the producer additionally emits the complete operand,
raw-shape, transfer, factor, sweep, output-core, allocation, and free transcript
for every live primitive. The verifier independently replays each local
operation and recomputes its shape, field work, traffic, and liveness. Other
cells retain complete event shapes/digests plus final exhaustive semantics and
ranks.

The two source processes cannot read the full execution matrix because it
binds target-bearing records. Before launch, the harness derives all target
IDs, coordinates, coefficients, labels, planted tuples, and target-bearing
digests from withheld files and rejects any occurrence in the complete source
closure. Producer diagnostic samples use a source-only SHA-256 rule and do not
include the planted tuples.

## C6: controls and mutations

Positive controls:

- mode-local rank-one coordinate TTs;
- rank-one separable addition and Hadamard products;
- an asymmetric synthetic TT with preregistered ranks `(1,2,3,4)`;
- `A+(-A)` and a common-prefix/independent-suffix direct sum whose exact rank
  drops only under the complete two-sweep normalizer;
- identity and planted targets;
- one nonzero-trace six-source `GENERAL_TRACE_Q00` target per source cell;
- `A+(-A)+S`, preserving a nonzero low-rank result while charging the complete
  direct sum;
- a streamed product with large provisional bonds and rank-one final tensor;
- tagged zero followed by every supported TT operation;
- a nontrivial gauge-equivalent TT;
- the C08 modewise projective-rescaling compiler cell;
- a `B=17` low-rank synthetic tripwire where hidden `B^5` work is conspicuous;
- cumulative resource refusal without an individual object refusal;
- source-advice digest invariance under reversed target order;
- exact agreement with the prior first-norm source formula.

`control-manifest-v1.json` freezes each synthetic field, deterministic tensor
or explicit core list, expected exact ranks, value digest where applicable,
and expected IR transcript before source. Controls may not be regenerated from
observed compiler output.

`mutation-manifest-v4.json` freezes 29 mutations before source. M01-M17 cover
circuit, core, transfer, reshape, shared normalizer, target coefficient,
accounting, provenance, product/radix/NumPy enumeration, and prior-table reads.
M18A attempts the prohibited full raw C12/B5 Hadamard allocation; M18B performs
flattened B5 traversal without an oversized object. M19-M25 attack raw-cost
accounting, liveness, int64 range/dtype, cumulative vectors, projective inputs,
and shared verifier aliases. M26 freezes the corrected mode-3 stage-B slice,
M27 attacks the target-redacted phase firewall, and M28 changes backend closure
identity while preserving the NumPy version string.

Capability mutants must be refused before the forbidden action. M18A also
requires independent allocator or pre-allocation evidence, while M18B must be
rejected without relying on an object-size limit. Semantic mutants execute only
their frozen scopes. The verifier emits reason codes before comparing them with
manifest expectations; expected detector labels are not inputs to its
decision. A missing, surviving, replaced, or unexecuted mutation invalidates
the mutation partition.

## C7: accounting

Every event emits the componentwise vector
`(adds,subs,muls,squares,inversions,reductions,comparisons,hash_bytes,
copied_words)`. Squares are not duplicated as multiplications, and unused
capacity in one component cannot offset another. Every traffic ledger
separates:

- registry coordinate input reads;
- direct-sum allocation and copies;
- local Hadamard matrix construction;
- streamed-prefix, left-sweep, and right-sweep factorization copies, pivot
  search, row normalization, and elimination in separate buckets;
- transfer propagation;
- emitted cores, provisional prefixes, neighboring-core contractions, and
  complete-normalizer workspaces;
- retained five-source advice;
- diagnostic certificate cores;
- target coefficient formation;
- target linear combination and recompression;
- digesting, serialization, and replay.

For every operation and gate, report operand ranks, raw candidate ranks,
local matrix shapes, exact output ranks, current live field words, cumulative
logical reads and writes, and wall time. Canonical storage uses
`ceil(log2(p)/8)` bytes per field word. Peak RSS is normalized with the same
Darwin/Linux rule as `EXP-ECDLP-TT-NORM-RANK-001`.

`accounting-model-v4.md` and `execution-matrix-v4.json` are authoritative for
all shape, operation, traffic, liveness, canonical-byte, RSS, and artifact
ceilings. Cumulative vectors never reset at a gate, cell, or partition
boundary. The campaign reconciles all named traffic buckets, each of six
partitions, and the componentwise whole-campaign totals.

The target-free source matrix labels only its source subtotal:

```text
normalizations: 1,022
prefix factorizations: 1,512
two-sweep factorizations: 8,176
total rank factorizations: 9,688.
```

The harness-only full matrix adds the withheld 25-target delta
`(25,0,200,200)`, producing campaign upper bounds
`(1,047,1,512,8,376,9,888)`. No source process sees the target delta.

The producer must report:

```text
full_tuple_enumerations = 0
full_tuple_values_read  = 0
maximum_live_mode_indices <= 1 outside TT contraction kernels
diagnostic_sample_count = frozen O(1) count
maximum_ndarray_dimensions <= 3
prior_artifact_reads = 0
target_manifest_reads_in_source_phase = 0
mutation_manifest_reads_in_source_or_target_phase = 0
dynamic_code_events = 0
child_processes = 0
network_events = 0
```

These counters are necessary but not sufficient; source and provenance audits
are also mandatory.

## C8: budgets and stopping rules

Mandatory per-process limits:

```text
wall clock                         <= 3600 seconds
aggregate CPU                      <= 12 hours
peak RSS                           <= 2 GiB
one local factorization matrix     <= 1000000 F_p words
one retained or temporary TT object <= 1000000 F_p words
predicted peak live state            <= 500000 F_p words
raw result per partition             <= 256 MiB
whole campaign artifacts             <= 1 GiB
```

The execution matrix gives exact integer caps for every component and for each
of `source_generator,source_verifier,target_generator,target_verifier,
mutation_generator,mutation_verifier`, plus the whole campaign. Its traffic
caps are 200, 50, 50, 50, 50, and 20 billion field words respectively, with a
420 billion campaign cap. These are preimplementation hard ceilings; the
implementation must derive tighter predicted and observed vectors before run
approval. Crossing any predicted or observed component stops before the next
operation or allocation and preserves the first named cell, gate, operation,
mode, matrix shape, rank state, and cumulative vector. Resource refusal is an
implementation result, not evidence against another compiler.

## C9: success and falsification

Success requires:

- all six primary source cells, one rescaled source control, and 25 target
  cells complete;
- the source process sees no target-bearing input, terminates after independent
  advice freeze, and the target process consumes exactly that frozen digest;
- zero producer full-tuple enumerations and no source-audit violation;
- zero independent semantic mismatches;
- every nonzero core bond equals the independent exact unfolding rank;
- all 29 live-source or live-record mutations are rejected;
- the C08 full gate transcript and every strengthened synthetic control pass;
- the capability audit, phase-specific data-read allowlist, local-source hash,
  pinned runtime/package closure, OS-loader record, dtype, canonical-range,
  overflow, IR/AST, allocation, and cumulative-vector gates pass;
- all mandatory accounting and provenance fields are present;
- every observed allocation, traffic term, RSS value, and time lies below its
  frozen reviewed ceiling.

Any semantic mismatch rejects the corresponding implementation claim. A
rank-minimality mismatch rejects exact recompression but may preserve semantic
correctness. A resource stop weakens only the literal gatewise schedule. No
toy rank trend may be fitted as an asymptotic exponent.

## C10: required artifacts

- `raw-result.json`
- `verification.json`
- `run-manifest.json`
- `runner-receipt.json`
- `source-advice-receipt.json`
- `frozen-source-advice.json`
- `frozen-source-control-certificates.json`
- `source-verification.json`
- `target-verification.json`
- `backend-attestation.json`
- `ir-event-ledger.json`
- `operation-ledger.json`
- `gate-rank-ledger.json`
- `gate-transcript.json`
- `allocation-event-ledger.json`
- `advice-ledger.json`
- `capability-audit.json`
- `mutation-report.json`
- `analysis.md`

## Reproduction command

Canonical harness commands are intentionally absent from v5. They will be
hash-frozen only after the reviews, implementation-derived ceilings, source
audit, and focused tests pass.
