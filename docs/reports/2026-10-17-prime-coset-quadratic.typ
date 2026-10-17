#set page(paper: "a4", margin: 17mm)
#set text(size: 9pt)
#set heading(numbering: none)

= Quadratic lift of a 63-bit prime coset input

*Exact formulation and planted-input check, 2026-10-17 UTC.* A target-blind
380-point factor base lies in a 788-element multiplicative coset. Replacing
each x^788 = g^788 equation with a twelve-gate square-and-multiply chain
reduces maximum input degree from 788 to 4, including the retained S3 chain.
The new variables and equations may make solving harder; no degree-of-regularity
or runtime result has been obtained.

#image("2026-10-17-prime-coset-quadratic.svg", width: 100%)

At m=8, the direct system has 15 variables, 16 equations and 118 monomial
occurrences. The lifted system has 111 variables, 112 equations and 310
monomial occurrences. These counts are serialized input sizes, not Gröbner
matrix sizes. The formulation is a chained-S3 system with eight summands;
it is not a direct S8 computation.

For this 380-column base, signed multisets bound uniform-target coverage by
binomial(760+m−1, m)/r. At m=7 the ceiling is 0.323848%; at m=8 it is
31.048916%. Collisions can only lower these values. Extra target shifts,
bases, or another complete-target method need explicit cost accounting. The
optimistic m=8 count reaches subgroup order only at B=441 or more; the archived
base has B=380, and counting alone never guarantees coverage.

== Independent check

The archived planted point sum satisfies all 16 direct and 112 lifted
equations in an independent SageMath 10.10.rc0 evaluator. Changing one
auxiliary value violates two equations. Of 788 coset x-values, only 380 lift
to points on the chosen curve, so roots require point checking. A separate
two-variable Gröbner diagnostic worked over the 63-bit field; it says nothing
about whether the m=8 system is tractable.

== Required next comparison

A frozen trial should compare direct and lifted inputs on the same base and
targets, with equal-realized-size random and small-x controls, bounded
solver time and memory, root certificates, useful rank, complete setup,
linear algebra, unseen target recovery, and matched rho. Censored solver
attempts remain censored. The companion Markdown report links the exact
system JSON, source, independent replay, and raw capability output.
