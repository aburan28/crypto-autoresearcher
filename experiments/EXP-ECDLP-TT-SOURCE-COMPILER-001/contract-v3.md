# Experiment Contract: exact first-norm source-TT compiler v3

Version 3 preserves the v1 and v2 review history. It binds the exact two-stage
Hadamard contraction, NumPy `2.4.0` int64 backend, producer capability boundary,
numeric campaign ceilings, allocation events, full C08 gate transcript,
modewise projective-rescaling cell, strengthened synthetic controls, corrected
literature, and 25-entry live-source mutation schedule.

## Protocol status

`REVIEW_REQUIRED`. No source implementation or run is authorized until
independent theory, accounting, and red-team reviews pass, all repairs are
versioned, the canonical specification is approved, and protocol hashes are
frozen in a clean Git commit.

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

## C2: frozen inputs and schedule

The authoritative instance source is
`../EXP-ECDLP-TT-NORM-RANK-001/instance-manifest-v1.json`. Only these entries
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
and six general-basis controls, for 25 target TTs. The inherited targets and trace-zero extensions
are not selected or replaced. Each general-basis control freezes `t=1` and the
least positive `n_control` for which `t^2-4n_control` is a quadratic nonresidue
modulo `p`; exact values and Legendre checks must appear in the execution
matrix before source implementation.

## C3: producer construction path

The producer must:

1. parse and hash the inherited manifest;
2. audit curve, registry, target, mode-order, tree, and RCB-gate provenance;
3. create coordinate inputs only as mode-local rank-one TTs;
4. execute the literal 40-gate RCB schedule four times;
5. use exact TT direct sums, streamed Hadamard products, scalar
   multiplication, and exact finite-field recompression;
6. build the six quadratic source tensors and retain the five trace-zero
   sources;
7. specialize every trace-zero target by one five-term linear combination;
8. specialize the general-basis control by one six-term linear combination;
9. evaluate only the preregistered constant-size diagnostic sample list;
10. emit cores, gate traces, accounting, certificates, and provenance.

It must not import prior generated tensors, rank tables, source tables, or
verifier code. It must not enumerate the Cartesian source product, construct
an unfolding from tuple values, or use an affine group oracle to assign a TT
core.

The complete producer capability boundary is frozen in
`execution-matrix-v2.json`. The producer is one hashed local source closure and
may read only the inherited manifest, execution matrix, and mutation manifest.
It may not use dynamic imports or code, child processes, network access,
verifier source, prior run artifacts, five-dimensional arrays, generic tuple
iterators, or unbound helpers. All dense arrays pass through audited allocation
and free events; no producer array may have more than three dimensions.

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
It may not materialize a Kronecker slice. Exact dense kernels use NumPy 2.4.0,
signed int64, C order, one thread, and only the operation allowlist in the
execution matrix. Before every kernel it asserts canonical residues and the
actual dot-product overflow bound; after every kernel it reduces modulo `p`.
`kron`, `einsum`, `tensordot`, NumPy index-grid helpers, object dtype,
floating conversion, and `np.linalg` are prohibited.

## C5: independent verifier

The verifier must not import producer modules or reuse its TT evaluator,
finite-field elimination, RCB routine, tuple iterator, target coefficient
routine, or accounting calculator.

For every source-compilation cell it independently enumerates all `B^5`
tuples in a different traversal and computes the frozen left-associated sum by
an independently transcribed RCB evaluator. It checks all nine TT values.
For every target cell it computes the applicable trace-zero or frozen
general-basis norm formula directly and checks the target TT value. It
independently unfolds every nonzero emitted tensor and checks all four exact
ranks.

Verifier enumeration, rank work, traffic, memory, and time are reported in a
separate ledger and may never be reclassified as source preprocessing.

For `C08:random_unique`, the producer additionally emits the complete operand,
raw-shape, transfer, factor, sweep, output-core, allocation, and free transcript
for every live primitive. The verifier independently replays each local
operation and recomputes its shape, field work, traffic, and liveness. Other
cells retain complete event shapes/digests plus final exhaustive semantics and
ranks.

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

`mutation-manifest-v2.json` freezes 25 mutations before source. M01-M13 cover
circuit, core, transfer, reshape, normalizer, target coefficient, accounting,
and provenance errors. M14-M25 patch live source or live records to exercise
product/radix/NumPy enumeration, prior-table reads, raw-then-recompress,
post-rank accounting, late peak sampling, unreduced int64 input, wrong dtype,
cumulative reset, affine inputs, and shared verifier aliases.

Capability mutants must be refused before the forbidden action. Semantic
mutants execute only the frozen C08 random scope. The verifier emits reason
codes before comparing them with manifest expectations; expected detector
labels are not inputs to its decision. A missing, surviving, replaced, or unexecuted
mutation invalidates the mutation partition.

## C7: accounting

Every field ledger separates addition, subtraction, multiplication, squaring,
inversion, comparison, and modular reduction. Every traffic ledger separates:

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

`accounting-model-v2.md` and `execution-matrix-v2.json` are authoritative for
all shape, operation, traffic, liveness, canonical-byte, RSS, and artifact
ceilings. Cumulative counters never reset at a gate or cell boundary. The
campaign separately reconciles each partition and the whole-run totals.

The producer must report:

```text
full_tuple_enumerations = 0
full_tuple_values_read  = 0
maximum_live_mode_indices <= 1 outside TT contraction kernels
diagnostic_sample_count = frozen O(1) count
maximum_ndarray_dimensions <= 3
prior_artifact_reads = 0
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

The execution matrix additionally caps baseline-generator multiplications and
additions/subtractions at 20 billion each, inversions at 2 million, logical
traffic at 200 billion words, and whole-campaign field work and traffic at 52
billion operations and 300 billion words. These are preimplementation hard
ceilings; the implementation must derive tighter predicted and observed
ledgers before canonical approval. Crossing a predicted or
observed hard boundary stops the cell before allocation and preserves the
first named gate, operation, mode, matrix shape, and rank state. Resource
refusal is an implementation result, not evidence against the mathematical
existence of some other compiler.

## C9: success and falsification

Success requires:

- all six primary source cells, one rescaled source control, and 25 target
  cells complete;
- zero producer full-tuple enumerations and no source-audit violation;
- zero independent semantic mismatches;
- every nonzero core bond equals the independent exact unfolding rank;
- all 25 live-source or live-record mutations are rejected;
- the C08 full gate transcript and every strengthened synthetic control pass;
- the capability audit, file-read allowlist, source-closure hash, dtype,
  canonical-range, overflow, allocation, and cumulative-counter gates pass;
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
- `operation-ledger.json`
- `gate-rank-ledger.json`
- `gate-transcript.json`
- `allocation-event-ledger.json`
- `advice-ledger.json`
- `capability-audit.json`
- `mutation-report.json`
- `analysis.md`

## Reproduction command

Canonical harness commands are intentionally absent from v2. They will be
hash-frozen only after the reviews, implementation-derived ceilings, source
audit, and focused tests pass.
