# P1512 Source-Labelled Linear-Chow Cycle-Length Gate

Status: `SCOPED_NEGATIVE_LINEAR_CHOW_ATOMIZER_REQUIRES_FULL_CYCLE_LENGTH`

This theorem gate closes scalar-linear determinant, standard determinant-of-
cohomology, and direct exterior-compound realizations of the complete labelled
five-factor incidence. It does not lower-bound arbitrary nonlinear arithmetic
circuits, target-specialized iterative algorithms, or representations whose
atoms are not independent kernel or cokernel basis elements.

## Frozen Incidence

Let the oriented public factor deck be

```text
D = {P_1,...,P_B},  B=2r,
```

and let `E` be embedded as a smooth plane cubic. The ordered universal graph is

```text
Gamma = {(i1,...,i5,R): R=P_i1+...+P_i5} subset D^5 x E.
```

It has length `B^5`, because projection to `D^5` is an isomorphism of finite
schemes when the complete addition graph and exceptional charts are retained.
Even after the most favorable permutation quotient, the canonical multiset
cycle has length

```text
L(r) = binomial(B+4,5) = binomial(2r+4,5) = Theta(r^5).
```

Repeated factors remain represented in this quotient. Using `L(r)` therefore
gives a conservative lower bound for any source convention at least as
informative as an unordered signed five-factor row.

For each rational target `R`, let `nu_R` be the number of canonical source
multisets summing to `R`, counted with scheme multiplicity. Then

```text
sum_R nu_R = L(r).
```

No relation-density assumption is used.

## Single Linear Matrix Theorem

Suppose `M(X,Y,Z)` is an `m x m` matrix of homogeneous linear forms in the
plane target coordinates. Require:

1. `M` is generically invertible on `E`;
2. at every target `R`, its normalized kernel or cokernel basis has at least
   `nu_R` independent atoms;
3. every atom publicly inverts to a distinct exact source multiset; and
4. no source table or post-hoc nonlinear splitter is used.

The determinant restricts to a nonzero section of `O_E(m)`. Since the plane
cubic has `deg O_E(1)=3`, its zero divisor has degree exactly `3m`.

At a target `R`, put the specialized matrix over the local discrete valuation
ring into Smith normal form. If the residue-field corank is `c_R`, at least
`c_R` diagonal invariant factors have positive valuation. Therefore

```text
ord_R(det M) >= c_R >= nu_R.
```

Summing over all target points gives

```text
3m = degree(div_0(det M))
   >= sum_R ord_R(det M)
   >= sum_R nu_R
    = L(r).
```

Hence

```text
m >= ceil(binomial(2r+4,5)/3) = Omega(r^5).
```

On the frozen `q=Theta(r^5)` family, this is `Omega(q)`, not below Pollard rho
`Theta(q^(1/2))=Theta(r^(5/2))`.

If `det M` vanishes identically, generic invertibility fails and every generic
target has a spurious kernel, contradicting the biconditional.

## Degree, Charts, And Complexes

After clearing denominators, let entries of block `M_c` be sections of
`O_E(d_c)`. Its determinant zero divisor has degree at most `3m_c d_c`.
Assigning every source atom to at least one complete chart gives

```text
sum_c m_c d_c >= L(r)/3.
```

Thus moving the payload into entry degree, exceptional charts, or block sums
does not pass the gate. The scalar-linear case has every `d_c=1`.

The same accounting applies to a generically exact finite Chow or Tate complex
whose finite target support is detected by its determinant of cohomology. Its
local torsion length is at least the number of independent source atoms, while
the determinant line degree is bounded by three times the total charged
rank-twist payload. Therefore a standard scalar-linear complex has total
charged linear rank `Omega(L(r))` even if alternating determinants cancel
away from the incidence support.

This statement does not cover a nonlinear target-specialized circuit that
does not materialize independent kernel atoms. Such a successor must charge
its entry circuits and a complete source splitter separately.

## Standard Controls

For the P1511 favorable batch polynomial of degree `N=r^3`:

| Construction | Charged scalar-linear dimension |
|---|---:|
| companion or Bezout matrix | at least `N` |
| Sylvester matrix for two degree-`N` inputs | `2N` |
| subresultant matrix retaining gcd degree `g` | at least `2N-2g` |
| `g`th exterior compound of a `2N` map | `binomial(2N,g)` |

These are controls for the already-closed P1510 product grammar. The stronger
cycle-length theorem above applies directly to a source-labelled universal
linear-Chow atomizer, before choosing that grammar.

Two exact positive controls prevent an overbroad interpretation:

- the `3 x 3` circulant linear matrix has determinant
  `X^3+Y^3+Z^3-3XYZ`, exactly matching a plane cubic;
- the diagonal matrix `diag(T-a_1,...,T-a_n)` has one labelled kernel basis
  atom at each distinct root and dimension exactly `n`; repeated roots require
  the matching repeated diagonal blocks and determinant multiplicity.

Linear determinantal representations therefore work. They simply pay the
degree and independent-atom length they represent.

## Literature Boundary

Eisenbud and Schreyer construct canonical Chow complexes and identify the
Chow form with the determinant of the complex for suitable sheaves. Their
construction changes the presentation of resultants; it does not assert a
sub-degree source-labelled kernel. Buchweitz and Pavlov give Moore-matrix
determinantal representations and Ulrich bundles for plane cubics, supplying a
valid small determinantal control but not a five-factor source atomizer.

- https://arxiv.org/abs/math/0111040
- https://arxiv.org/abs/1511.05502
- https://eprint.iacr.org/2004/031.pdf

## Decision

Close P1512's declared source-labelled scalar-linear Chow/Tate/exterior-
syzygy atomizer. Its exact source-biconditional requirement forces total
linear rank-twist payload at least the full canonical cycle length
`Theta(r^5)`, already above rho before kernel computation, factor-log rank, or
blind descent.

Preserve the open exception for a target-specialized nonlinear representation
that avoids a universal determinant and does not enumerate independent atoms
until after a public target is supplied. Such a successor is not an Ulrich-
Chow atomizer and needs a new contract.
