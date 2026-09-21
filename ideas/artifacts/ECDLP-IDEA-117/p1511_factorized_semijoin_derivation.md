# P1511 Factorized Marked-Polynomial Semijoin Derivation

Status: `SCOPED_NEGATIVE_P1510_STYLE_PRODUCT_CIRCUIT_INPUT_IS_CUBIC`

This receipt resolves the sole P1511 continuation admitted after the FD-width
gate. It is a lower bound for the declared P1510-style product-circuit grammar,
not for arbitrary arithmetic circuits, sparse common-factor algorithms, or
generic prime-field ECDLP.

## Exact Product Circuit

For target x-coordinate `u_t`, selector roots `x_i`, and

```text
a_(t,i)(V) = S3(u_t,V,x_i),
b_j(V,W)   = S3(V,W,x_j),
```

the ordinary constant component of P1510 is

```text
J_t(W)
  = Res_V(product_i a_(t,i), product_j b_j)
  = product_(i,j) P_(t,i,j)(W),

P_(t,i,j)(W) = Res_V(a_(t,i),b_j).
```

The second equality is exact resultant multiplicativity. Every
`P_(t,i,j)` is a resultant of two quadratics and has bounded W-degree. P1510's
operation transcript independently confirms exactly `r^2` constant-size
quadratic-resultant leaves for every target.

Let `T` be `s=Theta(r)` public targets. The target-side batch circuit is

```text
A(W) = product_t J_t(W)
     = product_(t,i,j) P_(t,i,j)(W).
```

The three-factor side is partitioned by its first factor-base point:

```text
K(W) = product_k J_(P_k)(W)
     = product_(k,l,m) P_(k,l,m)(W).
```

The sign-complete x-coordinate convention means one canonical start per
factor-base x-coordinate covers both start signs. Common squarefree factors of
`A` and `K` are exactly the endpoint keys needed by the A2/A3 semijoin; P1509
and P1510 source jets can recover the two source pairs after such a key is
isolated.

## Circuit-Generation Bound

The declared input representation explicitly instantiates:

```text
target leaves = s*r^2 = Theta(r^3),
A3 leaves     = r*r^2 = Theta(r^3).
```

Each leaf has constant positive serialized size and needs its target/start and
two source labels. Therefore even an unevaluated provenance-preserving product
circuit has `Omega(r^3)` leaf nodes and source backpointers. This occurs before
polynomial multiplication, gcd, factorization, Hasse extraction, rank, or
descent.

On the frozen `q=Theta(r^5)` family, Pollard rho is `Theta(r^(5/2))`. The
ratio between this leaf count and rho is `Theta(r^(1/2))` and grows.

This does not claim that every circuit for the same mathematical semijoin has
cubic size. It proves that assembling one P1510 product circuit per target or
per factor start already misses the required exponent.

## Dense Batch-GCD Routes

The raw P1510 polynomial `J_t` has degree `Theta(r^2)`; its squarefree endpoint
support has degree `2r^2+1` on the frozen real fixtures. Consequently both
batch products have degree `Theta(r^3)`.

The standard exact routes retain that degree:

| Route | Mandatory charged object |
|---|---|
| expand then gcd | two dense degree-`Theta(r^3)` coefficient vectors |
| product/remainder tree | quasi-linear work in total input degree `Theta(r^3)` |
| quotient-module kernel | a module of dimension `Theta(r^3)` |
| one P1510 object per target | `Theta(r^3)` coefficient or leaf traffic |
| all target/start surface pairs | `Theta(r^2)` degree-`Theta(r^2)` gcd/resultant queries |

P1493 already independently verified the neighboring product/CRT fact: exact
pair-support membership has degree `r^2`, and batching `Theta(r)` supplied
queries moves soft-`Theta(r^3)` words. P1510 improves source provenance once an
endpoint surface is compiled; it does not lower that endpoint-support degree.

Batch-GCD product/remainder trees are quasi-linear in the total explicit input
size, not sublinear in it. Straight-line-program gcd/factorization closure is
also not the missing bound: the classical circuit algorithms are polynomial
in circuit size and total degree, while this declared circuit already has
cubic leaf size. See [Kaltofen's straight-line-program factorization
result](https://users.cs.duke.edu/~elk27/bibliography/89/Ka89_slpfac.pdf) and
the [polynomial SLP gcd result](https://www.cecm.sfu.ca/~pborwein/images/rand_imgs/l29n7f3l.pdf).

## Marker And Provenance Boundary

Let `g=deg(gcd(A,K))`. A determinant/resultant of marked perturbations of `A`
and `K` vanishes to order at least `g`, because the unperturbed Sylvester map
has corank at least `g`. A complete relation batch expects `g=Theta(r)` common
factors. Thus P1510's constant marker truncation cannot be applied once to the
whole batch and still expose all relation factors.

This is not itself fatal if the gcd factors have already been isolated: each
factor can then be evaluated against the existing P1510 jets and source trees.
The failure is earlier. None of the admitted routes isolates those factors
before paying the cubic circuit/input cost.

## Exact Synthetic Control

The executable gate uses two families of `r^3` public linear leaves over
`F_65537`, grouped as `r` surfaces of `r^2` leaves. Exactly one leaf pair per
surface shares a planted root, while every other root is distinct. This is the
most favorable constant-degree version of the P1510 product grammar.

For every frozen `r in {4,6,8,12,16,24,32}` it must verify:

- `r^3` leaves per side and exact target/source backpointers;
- dense batch-product degree `r^3` per side;
- squarefree gcd degree exactly `r`;
- exact recovery of all `r` planted source tuples;
- leaf-count/rho ratio `sqrt(r)`;
- product-tree coefficient traffic and peak state at least linear in `r^3`;
- a thin `r^2`-leaf control remains below the `r^(5/2)` boundary.

The planted common roots are correctness controls only. They cannot promote
relation density or ECDLP performance.

## Decision

Close `RUN-P1511-FACTORIZED-SEMIJOIN-DERIVATION` as a scoped negative if the
synthetic control and independent audit replay the exact cubic circuit floor.
Preserve P1510 as an independently verified single-target compiler positive.

Any successor must change the representation before P1510 leaf emission. In
particular, it must construct one target-uniform source-biconditional object
whose size is sub-`r^(5/2)` and whose common-factor atoms invert to exact five-
source rows. Repackaging the same leaves as a dense resultant, product tree,
remainder tree, quotient module, or source-annotated matrix is closed.
