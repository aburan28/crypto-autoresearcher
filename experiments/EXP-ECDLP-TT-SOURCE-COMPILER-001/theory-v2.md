# Exact first-norm source-TT compiler v2

Version 2 preserves the reviewed v1 draft and repairs two theory errors before
implementation: target coefficient `c3` now includes `n Y_Q^2`, and universal
exact recompression is a left-to-right sweep followed by a right-to-left sweep.

## Handoff: constructive source advice

### Claim or task

Construct the five fixed trace-zero first-norm source tensors from the frozen
five-source RCB circuit without evaluating the full Cartesian input tensor.

### Status

- `RESTRICTED THEOREM`: exact TT addition, scalar multiplication, streamed
  Hadamard multiplication, and finite-field rank factorization preserve the
  represented tensor.
- `HYPOTHESIS`, `TOY-EVIDENCE REQUIRED`: the literal gatewise schedule remains
  below the frozen work and memory gates for `B in {3,4,5}`.
- `OPEN`: useful asymptotic source ranks, the Fermat zero indicator, witness
  localization, relation generation, and any ECDLP improvement.

### Assumptions

- The curve, factor base, RCB circuit, mode order, and addition tree are the
  exact frozen objects from `EXP-ECDLP-TT-NORM-RANK-001`.
- All arithmetic is exact in `F_p`.
- Every primary emitted tensor is nonzero. A zero intermediate is represented
  by a tagged canonical zero with exact cut ranks `(0,0,0,0)` and is never used
  to claim a minimal positive storage bond.

## 1. TT semantics

An order-five tensor train has cores

```text
G_j in F_p^(r_(j-1) x B x r_j),  r_0=r_5=1,
```

and value

```text
T(i_1,...,i_5)=G_1[:,i_1,:] ... G_5[:,i_5,:].
```

The exact minimal bond at cut `j` is the matrix rank of the unfolding with
row index `(i_1,...,i_j)` and column index `(i_(j+1),...,i_5)`.

For input point coordinate `C` in source mode `j`, use a rank-one TT whose
`j`th core contains the registry vector `C(P_i)` and whose other cores are
all ones. This construction performs `O(B)` reads and never visits a tuple of
five source indices.

## 2. Exact primitive operations

### Addition and linear combination

The sum of two TTs is represented by concatenating the first cores, taking
block diagonals in the middle cores, and vertically concatenating the last
cores. A finite linear combination of the five retained source TTs is built
as one multiway direct sum before exact recompression. Raw sum bonds and every
allocated block are charged.

### Exact rank factorization

For `A in F_p^(m x n)`, exact row reduction gives pivot columns `J` and RREF
`R`. Let `C=A[:,J]` and let `F` be the nonzero rows of `R`. Then

```text
A=C F,
```

with inner dimension `rank(A)`. No floating threshold or randomized sketch is
present.

One directional sweep is not universally sufficient for an arbitrary input
TT. The exact normalizer uses both directions.

First sweep left to right. For `j=1,...,4`, reshape

```text
A in F_p^((r_(j-1) B) x r_j),
```

factor `A=C F`, replace `G_j` by `C`, and contract `F` into the left
bond of `G_(j+1)`. This makes every prefix interface full column rank.

Then sweep right to left. For `j=5,...,2`, reshape

```text
A in F_p^(r_(j-1) x (B r_j)).
```

Replace `G_j` by `F`, reshaped as `(rank(A),B,r_j)`, and contract `C`
into the right bond of `G_(j-1)`. At each cut, the prefix is full column
rank and the processed suffix becomes full row rank, so the new bond equals
the exact unfolding rank. If either sweep finds rank zero, the whole tensor is
replaced by the tagged canonical zero and the stopping gate is recorded.

The counterexample to a right-only claim is a direct sum of `u tensor v` and
`u tensor w` with nonzero `u` and independent `v,w`: the last core can have row
rank two even though `u tensor (v+w)` has exact cut rank one. Broadcasting
rank-one cores embeds this example in five modes. The producer records both
sweep invariants; the verifier checks every final bond from independently
unfolded toy values.

A nonzero scalar is applied to the first core and preserves exact ranks without
a normalization sweep; it emits a rank-preservation certificate. Scalar zero
returns the tagged canonical zero. Addition, subtraction, and Hadamard product
always invoke the complete two-sweep normalizer.

### Streamed Hadamard product

The ordinary Hadamard construction would form bond products
`r_j^A r_j^B` in all five cores at once. The frozen compiler instead carries
one transfer matrix. At mode `j`, with incoming transfer

```text
V in F_p^(s_(j-1) x (r_(j-1)^A r_(j-1)^B)),
```

it forms only the local matrix

```text
M[(alpha,i),(a_j,b_j)]
  = sum_(a_(j-1),b_(j-1))
      V[alpha,(a_(j-1),b_(j-1))]
      A_j[a_(j-1),i,a_j]
      B_j[b_(j-1),i,b_j].
```

Exact factorization `M=C F` emits the next product core `C` and carries `F`
to the following mode. At the last mode the right product rank is one and the
remaining matrix is reshaped directly. Induction on the contracted prefix
proves exact Hadamard semantics, but these streamed prefix ranks are not
automatically minimal TT ranks. After the product is complete, the mandatory
left-then-right exact normalizer removes prefix- and suffix-dependent
redundancy.
The largest local `M`, its factorization copy, transfer, provisional output
cores, recompression workspace, and operand cores are all part of peak live
state.

This routine avoids a full raw five-core Kronecker train, but it is not free:
its local dimensions and elimination work can still grow to an ambient
boundary. The experiment must preserve the first failing gate if that happens.

## 3. Bound circuit and source tensors

Execute the literal RCB circuit four times in the frozen tree

```text
S12    = Add(P1,P2)
S123   = Add(S12,P3)
S1234  = Add(S123,P4)
S      = Add(S1234,P5) = (X:Y:Z).
```

Every addition, subtraction, and Hadamard multiplication is followed by the
complete exact normalizer. Scalar multiplication follows the frozen
nonzero/zero rule above and is charged. One RCB call contains 12 Hadamard
gates, five curve-scalar gates, 17 additions, and six subtractions, plus charged
formation of `b3=3b`. Build

```text
X2=X*X, XZ=X*Z, Z2=Z*Z, XY=X*Y, YZ=Y*Z, Y2=Y*Y.
```

For the trace-zero extension basis, retain exactly

```text
X2, XZ, Z2, YZ, Y2.
```

`XY` is emitted only as the general-basis control. For target
`Q=(X_Q:Y_Q:Z_Q)` and extension norm `n`, specialize

```text
h_Q = Z_Q^2 X2
    - 2 X_Q Z_Q XZ
    + (X_Q^2 + n Y_Q^2) Z2
    - 2 n Y_Q Z_Q YZ
    + n Z_Q^2 Y2.
```

This formula is homogeneous quadratic in the target and matches the source
span proved in `EXP-ECDLP-TT-NORM-RANK-001/theory-v2.md`. In particular,
`Q=(0:1:0)` gives `h_Q=n Z2`, not zero.

The general-basis control chooses a frozen nonzero trace `t` and compatible
norm `n_control` and specializes all six terms with coefficients

```text
c1 = Z_Q^2
c2 = -Z_Q(2X_Q+tY_Q)
c3 = X_Q^2+tX_QY_Q+n_control Y_Q^2
c4 = tZ_Q^2
c5 = -Z_Q(tX_Q+2n_control Y_Q)
c6 = n_control Z_Q^2.
```

This control tests `XY`; it is never retained as trace-zero primary advice.

## 4. Constructiveness and non-enumeration invariant

The producer is constructive only if all of the following hold:

1. Registry coordinate vectors are the only `B`-dependent input arrays.
2. No producer loop has one live index from each of the five physical modes.
3. No prior source table, unfolding, or `B^5` value vector is read.
4. Every exact factorization matrix is generated from TT cores and the one
   declared transfer, not from tuple evaluations.
5. Producer semantic checks use only a frozen constant-size sample list.
6. The verifier's exhaustive oracle is in a separate non-importing process
   and ledger.

A source audit, runtime counters, provenance hashes, and mutations enforce
these conditions. Merely reporting zero tuple evaluations is insufficient.

## 5. Cost model

For a materialized core `(l,B,r)`, charge `l B r` field words. For direct sum,
charge every copied and zero-filled word. For a local product matrix with
dimensions `m=s_(j-1)B` and `n=r_j^A r_j^B`, charge:

```text
local matrix words       = m n
factorization copy words = m n
transfer words           = rank(M) n
emitted core words       = m rank(M).
```

For each left-sweep matrix `((l B) x r)` and right-sweep matrix
`(l x (B r))`, charge the input view, factorization copy, pivot metadata,
both factors, contraction workspace, and updated neighboring core. Prefix
streaming factorizations and final normalization factorizations have separate
ledgers.

The implementation records actual additions, subtractions, multiplications,
inversions, comparisons, modular reductions, logical reads, and logical
writes. It separately reports:

- fixed-curve source preprocessing;
- retained five-source advice;
- diagnostic coordinate and `XY` certificates;
- per-target coefficient formation;
- per-target direct-sum construction and recompression;
- verifier-only enumeration and independent rank work.

Canonical bytes use `ceil(log2(p)/8)` per field word. Python object overhead
is additionally represented by normalized peak RSS.

## 6. Claim boundary

A complete valid run supports only:

> On the frozen toy curves, registries, mode order, and literal gate schedule,
> the five first-norm source tensors were constructed exactly from mode-local
> inputs without five-fold enumeration, under the reported finite work,
> traffic, advice, and memory costs.

The prior Hilbert theorem gives `B`-independent upper bounds on final source
ranks, but this run does not establish useful constants or cheap intermediate
construction beyond its frozen cells. It does not establish an efficient
`h^(p-1)` compiler, a zero locator, a decomposition algorithm, relation yield,
linear-algebra cost, target descent, or a rho improvement.

## 7. Proof and disproof tracks

Proof track:

- prove the rank-factorization, two-sweep, zero, scalar, and streamed-product
  invariants;
- replay every emitted core against direct RCB values;
- verify every final bond against independent exact unfolding rank;
- show the corrected target specialization equals the prior norm formula;
- replay the synthetic nonzero-trace six-source control.

Disproof track:

- identify any semantic or rank mismatch;
- identify the first gate whose local matrix crosses a frozen resource gate;
- test whether raw product bonds or elimination work saturate ambient powers;
- detect any hidden tuple table, uncharged transfer, or verifier leakage.

### Evidence so far

- `EXP-ECDLP-TT-NORM-RANK-001` supplies the exact source identity and frozen
  baseline values.
- No constructive source cores have yet been generated.

### Failure modes

- Intermediate product ranks can dominate even when final source ranks are
  small.
- Exact row reduction can cost more than direct toy enumeration.
- A one-sweep recompressor may be semantically correct but fail to attain
  minimal bonds.
- A producer/verifier shared helper could make replay circular.

### Next concrete action

Return the repaired v2 theorem, contract, and specification to theory review.

### Artifact paths

- `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/research-question.json`
- `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/hypothesis.json`
- `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/theory-v2.md`
- `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/contract-v2.md`
- `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/specification.json`
