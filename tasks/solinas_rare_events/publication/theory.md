# Elementary sampling facts and rare-event limits

These are derived group/counting identities, not new cryptanalytic mechanisms
or measured attack-cost results. They explain the interpretation of the frozen
point-distribution experiment. No external literature novelty claim is made.

## Marginal point coverage is independent of the generator

Let E(F_p) have prime order N and let H be any nonzero point. Then H generates
E(F_p), and k -> [k]H is a bijection from Z/NZ to E(F_p). A full orbit has the
same point set for every generator; generator selection changes its ordering.
If Q is uniform over the full group, Q+[j]H is uniform for any fixed j.

The experiment samples Q uniformly from nonzero points, and fails visibly if
any subsequent point is infinity. For a fixed position, excluding one group
point changes the full-group marginal by total variation1/N. The probability
that a256-point window intersects infinity is at most256/(N-1). These tiny
finite-domain conventions do not justify treating adjacent bits as independent.

For any subset S of affine x coordinates, write f(x)=x^3+Ax+B and let chi be
the quadratic character with chi(0)=0. Exactly1+chi(f(x)) affine points lie
above x. Therefore a uniform affine point satisfies

    Pr[x in S] = (|S| + sum_{x in S} chi(f(x))) / (N-1).

This formula contains the field and curve coefficients, but no generator.
A generator-specific effect must involve ordering, a restricted start
population, representation, or another joint/conditional quantity.

## Sign reversal cannot change these full-domain event rates

For a256-point H walk starting at Q, its reversed sequence is the -H walk
starting at Q+[255]H. Translation is bijective, so uniform-start full-domain
event probabilities agree for H and -H whenever the event is invariant under
sequence reversal. The same statement is exact on the finite-window domain
that excludes every start whose window would contain infinity: reversing a
finite window maps that domain bijectively onto the corresponding -H domain.

All three frozen descriptors are reversal invariant: longest equal-bit run
does not change; the three-bit parity-sign sum reverses its term order; and
four-bit motif counts are permuted by bit-string reversal, preserving their
sum of squares. Thus choosing the smaller y root versus its negative cannot
create a global uniform-start rate difference for these descriptors. This
does not equate unrelated lifted points on different fields, or imply that
arbitrary different generators have identical joint distributions.

## Uniform sampling can miss a real localized exception

If an exceptional event occupies M admissible starting points, its prevalence
is q=M/(N-1), up to the stated infinity convention. With n independent starts,
the probability of seeing at least one is1-(1-q)^n, approximately1-exp(-nq).
About3/q samples give95% detection probability when q is small. Estimating a
rare rate relatively precisely is harder: the usual rare-binomial relative
standard error is approximately1/sqrt(nq).

The exact previously observed prefix can always be reproduced deliberately.
Its existence alone says nothing about M. If only a handful of starting
windows exhibit it, even millions of random starts in a~2^192 or~2^224 group
will almost surely miss it. If it changes a descriptor's global frequency near
1e-4 or1e-5, a powered million-window study can measure that. These are
different scientific questions; neither erases the other.

The script's power plan states event prevalence, rate ratio and test alpha
explicitly. Its fixed samples are independent-start windows, not individual
walk points or a fixed percentage of the field. Its conclusions remain
conditional on the measured bit, event definitions, start populations and
fixed curve/point models.
