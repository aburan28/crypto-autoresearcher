# J2 blind mathematical derivation

This document was written before reading the review plan, input manifest, producer
proofs, targets, reports, PR body, git history, or any sibling review. Its sole
external mathematical input is `../../blind-statements.json`. The companion
standard-library Python script implements polynomial arithmetic and binary linear
algebra from scratch. These are deterministic exact calculations, not timing or
performance experiments. All arithmetic below is over F2 unless specified.

## Product and irreducibility

Let a = X^8 + X^5 + X^4 + X^3 + 1 and
b = X^8 + X^7 + X^6 + X^4 + X^2 + X + 1. Carryless convolution gives

    a b = 1 + X + X^2 + ... + X^16,
    (X + 1) a b = X^17 + 1 = X^17 - 1.

The bitmasks are a=313, b=471, ab=131071, and full product=131073.
For either monic degree-eight factor f, the Rabin criterion is

    X^(2^8) = X mod f, and gcd(f, X^(2^4) - X) = 1.

Why this suffices: X^(2^8)-X is the product of all monic irreducible
polynomials whose degrees divide 8, each once. The gcd removes degrees 1, 2,
and 4, leaving degree 8. This uses the finite-field factorization theorem;
the independent exhaustive trial-division check below does not need that theorem.

For a, X^16 mod a has bitmask 156 and X^256 mod a has bitmask 2;
gcd(a, 156 xor 2)=1. For b these numbers are 235, 2, and
gcd(b, 235 xor 2)=1. An independent second method divides each factor by every
monic polynomial of degrees 1 through 4, exactly 30 candidates. Neither factor
has any such divisor. A reducible degree-eight polynomial has a nonconstant
factor of degree at most four, so this exhaustively proves irreducibility.

## Canonical field Frobenius

Let K be any field with exactly 2^17 elements, including a canonical GF(2^17).
Let F: K -> K send z to z^2, viewed as an F2-linear map. Additivity follows
from characteristic two, and scalar compatibility follows because the scalars
are 0 and 1. Every nonzero element has order dividing 2^17-1 by Lagrange's
theorem in K's multiplicative group; zero separately satisfies the same
F^17(z)=z equality. Thus F^17=I.

F is not the identity: if z^2=z for every z, the nonzero polynomial Z^2-Z
would have 2^17 roots, contradicting the degree bound on the number of roots
of a polynomial over a field. Since 17 is prime, F has exact order 17.

Exact order alone is insufficient to identify the minimal polynomial.
For the needed additional step, suppose a nonzero polynomial
q(T)=sum(i=0..d) c_i T^i of degree d<17 annihilates F. Then the nonzero
ordinary polynomial L(Z)=sum(i=0..d) c_i Z^(2^i) vanishes on every element
of K. Distinct exponents prevent coefficient cancellation; its degree is
2^d <= 65536 < 131072. The root bound is contradicted. Therefore the
minimal polynomial has degree at least 17. Since T^17-1 annihilates F,

    minpoly(F) = T^17-1 = T^17+1.

This proof uses characteristic-two squaring, Lagrange's theorem, the root
bound, and the definition/divisibility property of the minimal polynomial.
It requires no normal-basis theorem, empirical sample, or choice of polynomial
basis. Since dim_F2 K=17, Cayley-Hamilton also gives charpoly(F)=T^17+1.

The product is squarefree: its derivative is T^16, coprime to T^17+1.
The distinct coprime irreducible factors are (T+1), a(T), b(T). The standard
primary-decomposition/Chinese-remainder theorem for a finite-dimensional
F2[T]-module therefore decomposes K into ker(F+I), ker(a(F)), ker(b(F)).
Characteristic-polynomial factor multiplicities, each one, give dimensions
1, 8, 8. This is an abstract mathematical corollary, not a statement that any
runner has selected or implemented these kernels. The fixed kernel is F2.

## Archived modulus and independently constructed matrix

The supplied mask 131081 means m(X)=X^17+X^3+1 under the conventional
least-significant-bit-is-constant encoding. The script finds
X^(2^17) mod m = X and gcd(m, X^2-X)=1. Since 17 is prime, these are the
Rabin checks. Independently, all 510 monic candidates of degrees 1 through 8
fail to divide m. Reducibility would yield such a divisor; m is irreducible.
Thus R=F2[X]/(m) is a field of cardinality 2^17.

In the ordered basis 1,x,...,x^16, the independently defined square map has
the following columns, encoded as coefficient bitmasks:

    [1, 4, 16, 64, 256, 1024, 4096, 16384, 65536,
     18, 72, 288, 1152, 4608, 18432, 73728, 32786].

Full binary matrix arithmetic gives rank 17, F^17=I, F!=I, and no linear
dependence among I,F,...,F^16. The first dependence is F^17+I=0, establishing
the same minimal polynomial independently of the canonical proof above.
The x orbit has rank 16 and trace zero. The (x+1) orbit has rank 17 and
trace one, furnishing an explicit normal basis in this quotient. Raw orbit
values, rows and columns, and elimination results are in `blind-output.json`.
The computed polynomial kernels have dimensions 1,8,8; their basis union
has rank 17; applying F to each listed basis vector remains in its kernel.

An abstract transport to canonical K exists: m divides Z^(2^17)-Z; that
polynomial splits into distinct linear factors in K, so choose a root alpha
of m in K and evaluate x at alpha. Irreducibility gives an injective field
map R -> K, and equal cardinality makes it an isomorphism. It fixes F2 and
commutes with squaring. Hence it conjugates these mathematical Frobenius maps.

This still does not identify an archived runner with R. That requires a
precise encoding agreement, correctness of its carryless multiplication and
reduction modulo the same m, correctness of its squaring/Frobenius routine,
and correctness of its matrix/basis conversion. To identify archived
invariant subspaces or membership/rank outputs, additionally prove their
chosen vectors, bases, equations, or predicates represent the relevant
polynomial kernels under that encoding, and preserve dimensions and ranks.
Finite-field uniqueness alone cannot certify executable code or a selected
subspace implementation. No runner source has been read at this blind stage.

## Negative controls and failures expected by the control design

The nearby degree-eight polynomial c=X^8+1 equals (X+1)^8. Its X^256
residue is 1, not X, and gcd(c,X^16-X)=X+1 (mask 3), not 1.
Both irreducibility tests reject it. Trial division reports proper monic
divisors with masks 3,5,15,17. Squaring in the nonfield quotient has rank 4
and minimal polynomial T^4+T^3 (mask 24), and F^17 != I. In epsilon=x+1
coordinates this is expected: epsilon^8=0 and each squaring doubles the
epsilon exponent, so F^3 kills the nilpotent part and F^4=F^3.

For GF(2), concretely F2[X]/(X), Frobenius is I. It satisfies F^17=I but
has exact order 1 and minimal polynomial T+1. The expected degree-17 claim
is false. This specifically checks that the argument must use cardinality
or dimension, and cannot infer a degree-17 minimal polynomial from F^17=I.

No mathematical check failed unexpectedly. A filesystem-path relocation
was needed before sealing; an attempted patch while that move was still
running failed to find the destination. The move completed, the patch was
applied, and the complete calculation reran successfully at the assigned
path. This operational failure is not a negative-control observation.
