# Experiment Contract: exact first-norm source-TT compiler v1

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

Target specialization cells are:

```text
random_unique: Q00,Q01,IDENTITY,PLANTED
x_interval:    Q00,Q01
```

This gives 18 target TTs. The target and extension data are inherited without
selection or replacement.

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
7. specialize every frozen target by one five-term linear combination;
8. evaluate only the preregistered constant-size diagnostic sample list;
9. emit cores, gate traces, accounting, certificates, and provenance.

It must not import prior generated tensors, rank tables, source tables, or
verifier code. It must not enumerate the Cartesian source product, construct
an unfolding from tuple values, or use an affine group oracle to assign a TT
core.

## C4: exact TT semantics

All core entries are canonical integers in `[0,p)`. Core shapes must join,
boundaries must equal one, and every operation must preserve five physical
modes of size `B`.

The exact factorization routine uses finite-field elimination. It emits pivot
columns, rank, a digest of the factor pair, and operation/traffic counters.
Final exact recompression is a right-to-left sweep: each core is reshaped as
`r_(j-1) by (B*r_j)`, factored, and its left factor is contracted into the
preceding core. Every nonzero post-recompression bond is claimed minimal and
must equal the independent unfolding rank. Streamed prefix ranks and raw
direct-sum or product ranks are reported separately and never called exact
ranks.

The streamed Hadamard routine may hold only operand cores, the incoming
transfer, one local matrix, its factorization workspace, the emitted prefix,
and accounting metadata. A full raw five-core product is prohibited.

## C5: independent verifier

The verifier must not import producer modules or reuse its TT evaluator,
finite-field elimination, RCB routine, tuple iterator, target coefficient
routine, or accounting calculator.

For every source-compilation cell it independently enumerates all `B^5`
tuples in a different traversal and computes the frozen left-associated sum by
an independently transcribed RCB evaluator. It checks all nine TT values.
For every target cell it computes the trace-zero norm formula directly and
checks the target TT value. It independently unfolds every nonzero emitted
tensor and checks all four exact ranks.

Verifier enumeration, rank work, traffic, memory, and time are reported in a
separate ledger and may never be reclassified as source preprocessing.

## C6: controls and mutations

Positive controls:

- mode-local rank-one coordinate TTs;
- rank-one separable addition and Hadamard products;
- an asymmetric synthetic TT with preregistered ranks `(1,2,3,4)`;
- identity and planted targets;
- exact agreement with the prior first-norm source formula.

Negative controls and mandatory mutations are frozen before implementation:

```text
M01 wrong b3 coefficient
M02 gate 37 subtraction changed to addition
M03 physical modes P2 and P3 exchanged
M04 one retained source core coefficient incremented modulo p
M05 one Hadamard transfer entry deleted
M06 product reshape orientation transposed
M07 exact recompression skipped at one named multiplication
M08 c2 target coefficient sign flipped
M09 c5 target coefficient omits extension norm n
M10 retained-advice word count reduced by one
M11 peak local-matrix word count reduced by one
M12 producer provenance falsely declares a full tuple iterator absent
```

Mutation generation emits isolated artifacts. The verifier must reject all 12
with their declared detector. A missing, surviving, replaced, or unexecuted
mutation invalidates the mutation partition.

## C7: accounting

Every field ledger separates addition, subtraction, multiplication, squaring,
inversion, comparison, and modular reduction. Every traffic ledger separates:

- registry coordinate input reads;
- direct-sum allocation and copies;
- local Hadamard matrix construction;
- factorization copy, pivot search, row normalization, and elimination;
- transfer propagation;
- emitted cores and temporary prefixes;
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

The producer must report:

```text
full_tuple_enumerations = 0
full_tuple_values_read  = 0
maximum_live_mode_indices <= 1 outside TT contraction kernels
diagnostic_sample_count = frozen O(1) count
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
```

The exact implementation-derived traffic and operation ceilings must be added
in a reviewed v2 execution matrix before approval. Crossing a predicted or
observed hard boundary stops the cell before allocation and preserves the
first named gate, operation, mode, matrix shape, and rank state. Resource
refusal is an implementation result, not evidence against the mathematical
existence of some other compiler.

## C9: success and falsification

Success requires:

- all six source cells and 18 target cells complete;
- zero producer full-tuple enumerations and no source-audit violation;
- zero independent semantic mismatches;
- every nonzero core bond equals the independent exact unfolding rank;
- all 12 mutations are rejected;
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
- `advice-ledger.json`
- `mutation-report.json`
- `analysis.md`

## Reproduction command

Canonical harness commands are intentionally absent from v1. They will be
hash-frozen only after the reviews, implementation-derived ceilings, source
audit, and focused tests pass.
