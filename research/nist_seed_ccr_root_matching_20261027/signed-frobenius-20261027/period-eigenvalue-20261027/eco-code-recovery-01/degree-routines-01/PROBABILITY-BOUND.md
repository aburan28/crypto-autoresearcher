# Intended randomized degree routine: conditional per-call bound

This is a symbolic derivation from the recovered1997 source contract, not a measured frequency or probability assigned to the original deterministic RNG stream.

Assume a squarefree polynomial f of degree n>=2 over F_p, all its irreducible factors having the same degree d; h=X^p mod f; valid field arithmetic; and mutually independent uniform coefficient draws for the two random stages. If d=1 then h=X and the source returns1 immediately. Otherwise d>=2 and the number m of irreducible factors is n/d<=floor(n/2).

The source draws a uniform polynomial P1 of degree<n and sums its n Frobenius conjugates. CRT decomposes F_p[X]/(f) into m copies of F_(p^d). In each component the sum is (n/d) times the field trace. If p>n, this multiplier is nonzero; the m resulting trace values are independent uniform elements of F_p. The probability that any two coincide is at most m(m-1)/(2p).

Without a collision, the trace element's minimal polynomial has degree m. The source then calls its probabilistic min_poly routine with bound floor(n/2); the documented projection-error bound is floor(n/2)/p. A union bound therefore gives

P(any exceptional returned degree) <= [m(m-1)/2 + floor(n/2)]/p.

For the documented modular-polynomial range ell<800 and degree n=ell+1, n<=798, floor(n/2)<=399, and the numerator is at most399*398/2+399=79,800. Every frozen curve field satisfies p>2^191, hence this conditional per-call bound is less than2^-174.

This bound assumes intended valid inputs, independent uniform draws and correct arithmetic. It excludes neither RNG bias, a bad modulus/backend, wrong polynomial degree bound, malformed/non-squarefree or unequal-degree input, nor a different historical implementation. It supplies no bound on the actual probability of these reconstructed omissions. The missing historical caller and invocation remain material. The n=1 path is excluded from these assumptions and discussed separately in LINEAR-EDGE.md.
