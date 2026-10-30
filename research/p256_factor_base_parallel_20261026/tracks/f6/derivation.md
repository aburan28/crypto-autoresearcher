# Derived F6 staircase identities and extraction boundary

This is a prospective algebraic derivation, not a measured second-pass result.
The field and group parameters are published P-256 parameters. Write the
balanced integer lift of `f3(c1+u,c2+v,xQ)` as `f(u,v)`. Translating and
balancing nonleading coefficients preserves its modular zeros and its leading
monomial `u^2 v^2`, of coefficient one. It has individual degrees at most two
and total degree at most four.

Fix `m in {1,2,3}`, `t in {0,1,2,3}`, `D=4m+t`, and all exponent pairs
`alpha=(i,j)` with `i+j<=D`. Set `k=min(m,floor(i/2),floor(j/2))` and

    g_alpha = p^(m-k) u^(i-2k) v^(j-2k) f^k.

Each modular root of `f` makes every `g_alpha` divisible by `p^m`.
In graded-lex monomial order every row's leading monomial is `u^i v^j`
with coefficient `p^(m-k)`. All other monomials precede it and stay in the
same total-degree staircase. Scaling a column `(i,j)` by `B^(i+j)` gives
a square full-rank triangular lattice with

    n = binomial(D+2,2)
    K = sum_{k=1}^m binomial(D-4k+2,2)
    w = 2 binomial(D+2,3)
    det(L) = p^(mn-K) B^w.

The sum for K follows by counting the exponent pairs for which the selected
power is at least k. The column-weight sum is w. These are exact identities,
not volume estimates. The code independently reconstructs polynomial rows and
checks triangularity; it additionally checks two fixed determinants directly.

For a polynomial represented by row vector z and `0<=u,v<=B`,
`|h(u,v)| <= sqrt(n) ||z||_2`. Therefore the actual strict integer test
`n ||z||_2^2 < p^(2m)` lifts divisibility to an integer zero. Combining
the determinant with Galbraith chapter 17 Theorem 17.2.12(5) gives only the
following sufficient first-vector guarantee:

    n^(2n) 2^(n(n-1)) B^(4w) < p^(4K).

A failed inequality leaves the actual reduction/extraction question open.
Even a qualifying vector is not automatically a zero-dimensional ideal. The
runner separately records the ideal, its dimension status, elimination and
integer-root candidates, with the complete finite-box point oracle as a
reference. The known-root positive is not an ordinary input.

This f3 relation concerns **two summands**. An interval of B+1 abscissas
has at most `2(B+1)` signed points. Its number of unordered two-summand
multisets is at most `binomial(2(B+1)+1,2)`, so half coverage of uniform
nonzero targets necessarily requires

    2 binomial(2(B+1)+1,2) >= r-1.

The declared width screen only reaches `B=2^84`; it is below that
two-summand capacity scale. No arity-three threshold is substituted. Neither
this necessary counting condition nor the sufficient lattice condition gives
a success law, total attack cost, or a general impossibility theorem.
