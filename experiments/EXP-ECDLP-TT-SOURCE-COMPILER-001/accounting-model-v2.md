# Exact TT compiler accounting model v2

Version 2 preserves v1 and replaces the one-slice Kronecker materialization
with an exact two-stage contraction through the separate operand bonds.

## Status

`REVIEW_REQUIRED`. This model derives implementation-independent shape and
traffic rules. It does not authorize source or fix aggregate operation
ceilings; those require the reviewed implementation schedule.

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
workspace is `B^6`, equal to 15,625 words at `B=5`; stage B writes at most one
`B^5=3,125`-word output slice before insertion into `M`.

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

Preprocessing retains only five source TTs. `X,Y,Z,XY`, factor certificates,
and gate traces are diagnostic storage. Target coefficient formation,
multiway direct sum, exact normalization, retained target TT, and disposal are
charged separately for each of 24 target cells.

## 8. Exact vectorized backend preflight

An optional producer backend may use NumPy `int64` only for dense integer
array allocation, the two sequential contractions, matrix products, and row updates. It may
not call floating linear algebra or use tolerances. Every result is reduced
modulo `p` after the declared operation.

For the largest mandatory field and contraction,

```text
p <= 3947,
dot length <= 150,
150*(p-1)^2 <= 2,335,637,400 < 2^63.
```

The length 150 comes from the largest six-way direct-sum bond; streamed
contractions sum across at most `B^2=25`, and factor-identity checks sum across
rank at most `B^3=125`. Individual row-update products are below `(p-1)^2`.
Therefore signed 64-bit
integer arithmetic cannot overflow under the frozen shapes. The source must
assert these bounds before every vectorized dot product and emit the maximum
observed accumulator bound. A different `p`, `B`, inner dimension, dtype,
library version, or unbounded fused operation invalidates the backend claim.

The verifier remains non-importing and uses Python arbitrary-precision integer
arithmetic. If NumPy is adopted, its exact version, BLAS/runtime metadata,
thread count, dtype, and no-overflow certificate become protocol inputs. The
current specification's standard-library-only dependency line must be amended
before source implementation; this section alone does not authorize NumPy.

## 9. Frozen hard stops

Before implementation-derived aggregate ceilings, the universal hard stops
remain:

```text
one local M or rank-factorization input <= 1,000,000 field words
one retained or temporary TT object     <= 1,000,000 field words
total peak RSS                          <= 2 GiB
wall time per run                       <= 3,600 seconds
aggregate CPU                           <= 12 hours.
```

Each allocation is predicted before execution. A refusal preserves the exact
cell, gate, operation, mode, operand ranks, requested shape, requested words,
and cumulative ledger. It is a scoped result for this schedule.

## Handoff: accounting preflight

### Claim or task

Make every exact TT compiler operation, temporary, and traffic term auditable.

### Status

`REVIEW_REQUIRED`

### Assumptions

- Dense core and matrix kernels follow the declared shapes.
- No full raw Hadamard TT or `B^5` value tensor is present in the producer.
- Exact ranks are restored after every addition, subtraction, or product.

### Evidence so far

- Ambient physical ranks give finite mandatory shape ceilings.
- The largest local product matrix is 78,125 words at `B=5`.
- The two-stage contraction replaces the 390,625-word v1 Kronecker slice by a
  15,625-word stage-A workspace.
- Exact `int64` vectorization has a large frozen no-overflow margin.

### Failure modes

- A vectorized library may allocate undeclared temporaries.
- Prefix ranks can exceed final exact ranks and must remain charged.
- Aggregate field work may still make `B=5` impractical despite small RSS.
- An implementation-specific optimization can invalidate these formulas.

### Next concrete action

Have the Benchmark Agent independently check every formula and choose the
producer backend before an execution matrix or source is approved.

### Artifact paths

- `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/accounting-model-v2.md`
