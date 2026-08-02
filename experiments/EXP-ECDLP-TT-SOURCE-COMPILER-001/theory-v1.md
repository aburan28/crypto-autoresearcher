# Exact first-norm source-TT compiler v1

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
  canonically and never used to claim a minimal positive bond rank.

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

For a core `G_j` in a right-to-left sweep, reshape it as

```text
A in F_p^(r_(j-1) x (B r_j)).
```

Replace `G_j` by `F`, reshaped as `(rank(A),B,r_j)`, and contract `C`
into the right bond of `G_(j-1)`. Starting at the last core, the processed
suffix interface has full row rank. Induction therefore makes each visited
nonzero bond equal to the exact unfolding rank. A merely left-to-right local
factorization would control prefix rank but could miss dependencies in the
unprocessed suffix; it is not accepted as exact final recompression. The
producer records the right-sweep invariant, and the verifier checks every
final bond from independently unfolded toy values.

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
right-to-left exact recompression sweep removes suffix-dependent redundancy.
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

Every scalar addition and multiplication is a TT operation followed by exact
recompression. Scalar multiplication by curve constants is charged. Build

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
    + X_Q^2 Z2
    - 2 n Y_Q Z_Q YZ
    + n Z_Q^2 Y2.
```

This formula is homogeneous quadratic in the target and matches the source
span proved in `EXP-ECDLP-TT-NORM-RANK-001/theory-v2.md`.

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

It does not establish source ranks independent of `B`, an efficient
`h^(p-1)` compiler, a zero locator, a decomposition algorithm, relation yield,
linear-algebra cost, target descent, or a rho improvement.

## 7. Proof and disproof tracks

Proof track:

- prove the rank-factorization and streamed-product invariants;
- replay every emitted core against direct RCB values;
- verify every final bond against independent exact unfolding rank;
- show target specialization equals the prior norm formula.

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
- Recompression may be semantically correct but fail to attain minimal bonds.
- A producer/verifier shared helper could make replay circular.

### Next concrete action

Obtain independent theory, accounting, and red-team reviews of this protocol
before implementing producer source.

### Artifact paths

- `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/research-question.json`
- `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/hypothesis.json`
- `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/theory-v1.md`
- `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/contract-v1.md`
- `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/specification.json`
