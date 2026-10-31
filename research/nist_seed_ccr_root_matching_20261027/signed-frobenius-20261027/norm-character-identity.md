# Why the source resultant character can be reconstructed from an eigenvalue

This is an algebraic deduction under the stated kernel hypotheses, not a new
native execution of the source resultant routine.

Let `ell` be an odd prime different from the field characteristic, `P` have
order `ell`, and let its cyclic subgroup be stable under Frobenius with
eigenvalue `lambda`. Choose representatives `iP`, for `1<=i<=(ell-1)/2`, and
write `y_i=y(iP)`. None of these values is zero. For the monic kernel polynomial
`K(X)`, the resultant with the curve cubic is

`R = product_i y_i^2`.

Frobenius permutes these representatives up to signs. Consequently

`R^((p-1)/2) = product_i y_i^p / product_i y_i`

is the product of the signs incurred by multiplying the representative indices
by `lambda`. Gauss's lemma identifies that sign with `(lambda/ell)`. Hence
`(R/p) = (lambda/ell)`.

In the inspected source's `ell=1 mod4` refinement, the parity count includes
the Gauss counts for both `a` and `a^2`; the second character is one, so the
filter keeps precisely `(a/ell)=(lambda/ell)`. Since `(-1/ell)=1` there,
replacing the eigenvalue by its positive-half representative preserves this
test. This justifies the character reconstruction used in the frozen plan.
It does not establish the actual kernel order, resultant implementation,
degree mode, numerical limits or caller used in 1997.
