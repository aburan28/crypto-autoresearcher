# Derived F8 completeness and quotient-rank statements

This is a prospective algebraic derivation, not second-pass measurement or a
novelty claim. It assumes the published secp256k1 prime field and prime group
order/cofactor from SEC 2 section 2.4.1. The runner separately checks the
particular map and scalar witnesses on the standard generator and fixtures.

For a nontrivial cube root beta in Fp, the projective linear map
`(X:Y:Z)->(beta X:Y:Z)` preserves `Y^2 Z=X^3+7Z^3` and its identity.
It is an automorphism and hence preserves the elliptic group law. If its
scalar action on the prime-order generator is lambda, its action on every
group point is multiplication by lambda. The checks
`lambda^2+lambda+1=0`, `lambda!=1` and odd prime r show that the six scalars
`+/-lambda^j`, j=0,1,2, are distinct. Every nonzero point consequently has a
six-element signed orbit. This automorphism formula does not transfer to
P-256's nonzero coefficient a=-3: preserving that coefficient would require
`a beta=a` and hence beta=1.

Let C be the 48-by-8 compression matrix whose row for signed orbit point j
contains its certified scalar factor in the representative's column. The
eight canonical point rows are an identity matrix, so rank(C)=8. The forty
relations `e_j-factor_j e_canonical(j)` have an identity block on their
noncanonical columns. They are independent and span the row kernel of C.
Thus for any relation matrix R,

    rank([S;R]) - rank(S) = rank(RC).

Rows of RC equal to zero are known pure symmetry, not new representative-log
equations. The runner computes the four ranks using custom modular
elimination and a separate finite-field matrix implementation. The same C and
signed point set are available to the baseline; the six-element orbit size
does not grow with r and is no exponent improvement.

For a fixed target Q, every unordered three-point multiset has a unique
ordered index form `i<=j<=k`, including repeated indices. A pair table contains
every pair `i<=j`; querying `Q-P_k` and retaining `j<=k` therefore returns
exactly the complete multiset solution set. A separate projective enumeration
of all `i<=j<=k` supplies the finite-domain oracle. This covers the fixed point
set, not the whole field or a population success law.

The public hash-to-abscissa fixture generator does not provide scalar labels.
That statement is about the supplied data; it is not a mathematical theorem
that nobody knows a logarithm, a uniform-point theorem, or an RFC hash-to-curve
claim. The constructed positive target and historical labelled matrix fixture
remain controls. Empty ordinary target sets, if observed after release, would
concern only these fixed complete finite domains.
