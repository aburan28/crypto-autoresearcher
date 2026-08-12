# Exact TT compiler accounting model v3

Version 3 preserves v1 and v2, corrects the stage-B slice certificate, binds
the installed integer backend, separates source compilation from target
specialization, and defines componentwise campaign accounting.

## Status

`REVIEW_REQUIRED`. This model derives implementation-independent shape,
operation, traffic, phase, and backend rules. It does not authorize source.

## 1. Field-word convention

One field word is one canonical residue in `[0,p)`. Its canonical byte width is

```text
w_p = ceil(log2(p)/8).
```

Python or NumPy object storage is not substituted for field words. Peak RSS,
allocator temporaries, Python metadata, array headers, pivot indices, JSON,
and digest state are reported separately.

For a TT with five physical modes of size `B` and bonds
`(r1,r2,r3,r4)`, core storage is

```text
W_TT = B(r1+r1*r2+r2*r3+r3*r4+r4).
```

For every order-five tensor, exact ranks satisfy the physical ambient bounds

```text
(r1,r2,r3,r4) <= (B,B^2,B^2,B).
```

Hence one normalized nonzero TT uses at most

```text
W_exact(B) = 2B^2+2B^4+B^5.
```

At `B=5`, this is 4,425 field words.

## 2. Direct sum

For a dense `k`-way direct sum of normalized TTs at the ambient ranks, raw
bonds are at most `(kB,kB^2,kB^2,kB)`, and dense core storage is bounded by

```text
W_sum(k,B) = 2kB^2+2k^2B^4+k^2B^5.
```

Frozen maxima at `B=5` are:

```text
binary circuit addition: W_sum(2,5) = 17,600
five-source target sum:  W_sum(5,5) = 109,625
six-source control sum:  W_sum(6,5) = 157,800.
```

Dense allocation charges every zero-filled block word as a write and every
copied nonzero source word as one read plus one write. Coefficient scaling of a
first core charges one multiplication and reduction per scaled word. A zero
coefficient omits that source only if the omission and avoided allocation are
reported; the frozen target census is unchanged.

## 3. Rank factorization

For `A in F_p^(m x n)`, the frozen candidate algorithm copies `A`, uses
lexicographic finite-field RREF, records pivot columns, and returns
`A=C F`, with shapes `(m,r)` and `(r,n)`.

Worst-case field operations for observed rank `r` are bounded by:

```text
inversions      <= r
multiplications <= r*m*n
subtractions    <= r*(m-1)*n
comparisons     <= m*n+r*(m-1)
reductions      <= multiplications+subtractions+inversions.
```

The implementation emits exact observed counts; these are ceilings, not
substitutes.

With input `A` retained, peak factorization field words are bounded by

```text
W_RF_peak = 2mn+mr+rn+n,
```

where the final `n` is one row-update temporary. Pivot and row-permutation
metadata are non-field bytes.

Logical field-word traffic, including factor digesting, is bounded by

```text
T_RF <= 4mn+5rn+3mr+r(m-1)+3r(m-1)n.
```

This includes input-to-workspace copy, monotone pivot search, pivot-row
normalization, elimination, extraction of `C,F`, and digest reads. If the
implementation uses a block update or any additional array temporary, its
complete allocation and traffic are added rather than hidden under this bound.

## 4. Neighbor contraction

For a factor `(u x v)` contracted with a neighboring core `(v,B,w)`, output
shape is `(u,B,w)`. Dense work is

```text
products     = u*v*B*w
additions    = u*B*w*max(v-1,0)
output words = u*B*w
traffic      = 2*products+output_words
```

under register accumulation. If partial sums are materialized, their traffic
is additional.

Left-sweep and right-sweep factorizations and contractions use separate
ledgers. A tensor reaching rank zero emits a tagged zero; it does not allocate
positive-rank placeholder cores and call them exact ranks.

## 5. Streamed Hadamard product

At mode `j`, let operand core shapes be `(la,B,ra)` and `(lb,B,rb)`, and
reshape the incoming prefix transfer as

```text
V in F_p^(s x la x lb).
```

For one physical slice, contract in the frozen order

```text
T[alpha,bl,ar] = sum_al V[alpha,al,bl] A[al,i,ar]
O[alpha,ar,br] = sum_bl T[alpha,bl,ar] B[bl,i,br].
```

Write `O` into the `i` block of

```text
M in F_p^((sB) x (ra*rb)).
```

This is algebraically identical to `V kron(A_i,B_i)` but never materializes
the Kronecker slice or sums across the combined `la*lb` bond.

Dense operation ceilings are:

```text
stage-A multiplications = B*s*lb*ra*la
stage-A additions       = B*s*lb*ra*max(la-1,0)
stage-B multiplications = B*s*ra*rb*lb
stage-B additions       = B*s*ra*rb*max(lb-1,0).
```

The local words are:

```text
stage-A T     = s*lb*ra
stage-B O     = s*ra*rb
M             = s*B*ra*rb
incoming V    = s*la*lb
factor copy   = M
emitted core  = s*B*rank(M)
outgoing V    = rank(M)*ra*rb.
```

Operands, prior provisional cores, the full factor pair, row temporary, and
all other live circuit tensors are added to peak state.

For normalized inputs at ambient ranks, the five local `M` sizes are bounded
by

```text
(B^3,B^6,B^7,B^6,B^3).
```

Thus the mandatory maximum is `B^7`, equal to 78,125 field words at `B=5`.
The outgoing transfer is also at most 78,125 words. The largest stage-A
workspace is `B^6`, equal to 15,625 words at `B=5`. The largest stage-B output
slice is also `B^6=15,625` words, attained at mode 3 where
`s*r_a*r_b=B^6`. This repairs v2's false `B^5` stage-B certificate.

Across the five modes, dense two-stage product construction is bounded by

```text
stage-A multiplications <= B^2+B^6+B^9+B^9+B^5
stage-B multiplications <= B^3+B^7+B^9+B^8+B^4.
```

At `B=5`, this totals 6,347,650 multiplications before streamed
factorizations, compared with 61,097,250 for v1's Kronecker-plus-matrix path.
Both are exact; v2 is the frozen preferred order.

The provisional streamed output uses at most

```text
W_streamed <= 2B^6+B^4+B^3+B^2 = 32,025 words at B=5.
```

The prohibited complete raw Hadamard TT would use

```text
W_raw_product = B^9+2B^7+2B^3 = 2,109,625 words at B=5.
```

It exceeds the one-object gate and may not be materialized.

## 6. Two-sweep normalization

The left sweep factors matrices

```text
(r_(j-1)B) x r_j, j=1,...,4,
```

and contracts the right factors forward. The right sweep factors

```text
r_(j-1) x (B r_j), j=5,...,2,
```

and contracts left factors backward. Every factorization uses Sections 3 and
4, with distinct phase identifiers. Input cores remain live until their
replacement and neighbor contraction are committed.

## 7. Circuit and target ledgers

One RCB call charges 12 streamed Hadamard gates, five curve-scalar gates, 17
additions, six subtractions, and one `b3=3b` formation. Four calls are executed
per source cell. Six quadratic source products follow. Every operation record
contains:

- cell, RCB stage, gate number, destination, and operation kind;
- operand exact ranks and words;
- raw or streamed-prefix ranks, explicitly labeled nonminimal;
- every local shape and predicted allocation before allocation;
- exact final ranks after both sweeps;
- operations, logical reads/writes, canonical bytes, elapsed time, and peak
  live words;
- stopping reason and first refused object if a gate fails.

Preprocessing retains only five source TTs per primary source cell. `X,Y,Z,XY`,
factor certificates, and gate traces are diagnostic storage. Source advice is
serialized and hashed before the target manifest becomes readable. Target
coefficient formation, multiway direct sum, exact normalization, retained
target TT, and disposal are charged separately for each of 25 target cells in
a different process.

## 8. Bound exact integer backend

The source compiler and target specializer require the following local backend
identity. A version string alone is not an identity certificate.

```text
Python executable:
  /Library/Frameworks/Python.framework/Versions/3.13/bin/python3
Python executable SHA-256:
  20c9c2144a9f5202177620417e67643fb551aa31586e5d3c1361627b920cadb0
Python version:
  3.13.1 (v3.13.1:06714517797, Dec 3 2024, 14:00:22), Clang 15.0.0
platform/machine:
  macOS-15.6-arm64-arm-64bit-Mach-O / arm64
NumPy version:
  2.4.0
installed NumPy file count:
  1320
installed NumPy closure SHA-256:
  8a802a5be64dbec34c009c0fb7b76c3b2da97c2b92ec1ee9e66796ad6dcace94
_multiarray_umath SHA-256:
  aa5ff97ea536db1e8ffba077c980842f501dc7567a2c290d7500d4c7383172e5
architecture:
  arm64
```

The closure digest is computed by sorting
`importlib.metadata.distribution("numpy").files` by relative path and hashing,
for every regular file, the UTF-8 relative path, one NUL byte, and the 32 raw
bytes of that file's SHA-256 digest. The source records every member digest and
refuses a closure mismatch. The executable, NumPy closure, loaded NumPy
extension paths and hashes, dtype, C order, and thread environment are
pinned-runtime inputs.

Operating-system loader reads are not data inputs. The attested loader closure
for `_multiarray_umath` is exactly Accelerate, `libc++.1.dylib`, and
`libSystem.B.dylib` at their system paths. Their resolved paths and Mach-O
identities are recorded at run time; they are separate from the data-read
allowlist and from the local source closure.

NumPy signed `int64` may be used only for audited dense integer allocation,
the two sequential contractions, matrix products, and row updates. Floating
linear algebra, tolerances, and approximate rank are forbidden. Every result
is reduced modulo `p` at the declared boundary.

For the largest mandatory field and contraction,

```text
p <= 3947,
dot length <= 150,
150*(p-1)^2 <= 2,335,637,400 < 2^63.
```

The length 150 comes from the largest six-way direct-sum bond; streamed
contractions sum across at most `B^2=25`, and factor-identity checks sum across
rank at most `B^3=125`. Individual row-update products are below `(p-1)^2`.
The source asserts the actual canonical-value bound before every vectorized dot
product and emits the maximum observed bound. Any changed field, shape, inner
dimension, dtype, closure digest, or unbounded fused operation invalidates the
backend claim.

The independent verifiers use only Python arbitrary-precision integer
arithmetic for field semantics and ranks. They may inspect backend attestation
records but may not import producer or specializer code.

## 9. Accepted operation and dataflow model

The source compiler is an interpreter over this closed operation IR:

```text
input_coordinate, scale, direct_sum,
stage_a_contract, stage_b_contract, rank_factor,
absorb_left, absorb_right, emit, free.
```

Every allocation is the output of one IR node with input object digests,
shapes, field, predicted words, observed words, operation vector, traffic
vector, and liveness transition. Each emitted object has exactly one producing
node. The only physical-index arguments to any primitive are one mode and one
slice. No IR node accepts a five-index tuple, a linear physical-table index, or
a radix-decoding operation.

The harness parses the complete transitive local source closure and rejects:

- `product(..., repeat=5)` or an equivalent five-source product helper;
- `range(B**5)`, a constant-folded equivalent, or five radix decodes;
- five nested physical-index loops or comprehensions across helper calls;
- an array or memory view with five physical axes;
- a value table, unfolding, or prior-run tensor as an IR input;
- arithmetic or allocation output absent from the IR event stream.

The runtime trace and AST/call-graph audit are both required. Neither is
accepted alone as evidence of non-enumeration.

## 10. Componentwise operation equation

Every event emits the vector

```text
W = (adds, subs, muls, squares, inversions, reductions,
     comparisons, hash_bytes, copied_words).
```

For partition `P`, cell `c`, operation `g`, and event `e`, aggregation is
componentwise integer addition with no reset:

```text
W_P = sum_c sum_g sum_e W[P,c,g,e]
W_campaign = sum_P W_P.
```

`squares` are not also counted as `muls`. `reductions` count each explicit
canonical modular reduction boundary, including one per inversion result.
`hash_bytes` are bytes supplied to digest functions. `copied_words` count every
field word read or written by a copy, reshape-copy, serialization,
deserialization, zero initialization, or factor extraction; a view-only
reshape contributes zero copied words. Allocation metadata, JSON bytes, and OS
reads are reported separately and cannot be converted into field words.

The caps below apply independently to every component; spare capacity in one
component cannot offset an excess in another. The machine-readable execution
matrix stores the exact integers represented here in decimal shorthand.

```text
partition              adds  subs  muls squares inversions reductions comparisons hash_bytes copied_words
source_generator       20e9  20e9  20e9    1e9       2e6      45e9       10e9        1e9       200e9
source_verifier         5e9   5e9   5e9    1e9       1e6      15e9        5e9        1e9        50e9
target_generator        5e9   5e9   5e9    1e9       5e5      12e9        3e9      512e6        50e9
target_verifier         5e9   5e9   5e9    1e9       5e5      12e9        3e9      512e6        50e9
mutation_generator      5e9   5e9   5e9    1e9       5e5      12e9        3e9      512e6        50e9
mutation_verifier       2e9   2e9   2e9    1e9       5e5       6e9        2e9      512e6        20e9
whole campaign         42e9  42e9  42e9    6e9       5e6     102e9       26e9      4.048e9       420e9
```

A weighted scalar may be reported diagnostically, but it is not a gate.

## 11. Logical traffic equation

Each event reports field-word reads and writes in these disjoint buckets:

```text
registry_input, coefficient_input, allocation_zero_fill, direct_sum_copy,
stage_a_input, stage_a_output, stage_b_input, stage_b_output,
factor_input_copy, pivot_scan, row_normalization, elimination,
factor_output, transfer_propagation, sweep_absorption,
core_emit, advice_serialize, advice_deserialize, target_emit,
digest_read, verifier_materialization, artifact_serialize.
```

For each partition, total logical traffic is the sum of all bucket reads and
writes. It must equal `copied_words` plus the non-copy arithmetic reads and
writes reported by the same events. Partition caps are 200, 50, 50, 50, 50,
and 20 billion field words in run-partition order; the campaign cap is 420
billion. Each partition additionally reports peak live field words, allocator
bytes, peak RSS, bytes read by data path, source path, package path, and OS
loader path, and serialized artifact bytes.

## 12. Frozen hard stops and phase order

```text
one local M or rank-factorization input <= 1,000,000 field words
one retained or temporary TT object     <= 1,000,000 field words
predicted peak live state               <= 500,000 field words
total peak RSS                          <= 2 GiB
wall time per process                   <= 3,600 seconds
aggregate CPU                           <= 12 hours
raw result per partition                <= 256 MiB
whole campaign artifacts                <= 1 GiB.
```

Each allocation is predicted before execution. A refusal preserves the exact
cell, gate, operation, mode, operand ranks, requested shape, requested words,
and cumulative ledger. It is a scoped result for this schedule.

There are exactly six process partitions:

```text
source_generator, source_verifier,
target_generator, target_verifier,
mutation_generator, mutation_verifier.
```

The source generator and source verifier read only the target-redacted source
manifest and target-free source execution matrix. The source verifier freezes
canonical retained-advice bytes
and, separately, canonical non-retained `XY` and rescaled-control certificate
bytes. Its receipt binds both SHA-256 digests and counts only the five primary
trace-zero sources as retained advice. Only after that receipt exists may the
target generator read the target manifest and both frozen source artifacts.
Mutation input is available only to the mutation harness and mutation verifier.

## Handoff: accounting preflight v3

### Claim or task

Make every exact TT compiler operation, temporary, phase, and traffic term
auditable.

### Status

`REVIEW_REQUIRED`

### Assumptions

- Dense core and matrix kernels follow the declared shapes.
- No full raw Hadamard TT or `B^5` value tensor is present in the producer.
- Exact ranks are restored after every addition, subtraction, or product.
- Runtime, package, source, and data-input closures remain distinct.

### Evidence so far

- Ambient physical ranks give finite mandatory shape ceilings.
- The largest local product matrix is 78,125 words at `B=5`.
- Both stage-A and stage-B local workspaces peak at 15,625 words.
- Exact `int64` vectorization has a large frozen no-overflow margin under the
  attested package closure.
- Six partitions enforce target-blind source compilation and separately charge
  online specialization.
- Work and traffic gates are componentwise and never reset.

### Failure modes

- A vectorized library or OS framework may allocate undeclared temporaries.
- Prefix ranks can exceed final exact ranks and must remain charged.
- Aggregate field work may still make `B=5` impractical despite small RSS.
- An implementation-specific optimization can invalidate these formulas.
- AST and IR checks can share a blind spot unless live mutations exercise both.

### Next concrete action

Have the Benchmark Agent independently check every formula, backend binding,
partition cap, and traffic reconciliation before source is approved.

### Artifact paths

- `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/accounting-model-v3.md`
