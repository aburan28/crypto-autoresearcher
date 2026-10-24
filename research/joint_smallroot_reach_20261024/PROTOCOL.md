# Scope fixed before successor diagnostics

This is a software accounting audit of finite lattices, not an approved ECDLP
experiment or a hypothesis-state transition. No random trial, solve-rate fit,
performance advantage, or scientific promotion is authorized by this document.

Inputs: the historical calculator at main dcfdd16cdf7783a059ca1e6e4cc5efbf77434b7b;
S3 with integer coefficients a=2,b=3; for joint rows xQ=5. The coordinate order
is x1,x2,x3,x4,u,v. No subgroup instance or private target is involved.

Checks: reproduce the historical --validate/--m 4 output; construct exact t=1
integer coefficient matrices at p=101 with all scaling bounds 2; compare exact
determinants with the triangular formula; verify finite full-box counts directly;
check divisibility on a public toy elliptic addition fixture.

Successor diagnostics: single S3 at t=1,2,4,6,8,10; joint union-support family at
t=1,2,3; total-degree joint family at t=1,2,3,8,16 using exact combinatorial
counts. Record row count, modulus exponent, divisibility exponent, coordinate
exponent sums, determinant budget, equal-bound volume per equation, number of
dense matrix entries, and support-size bounds. These dimensions are structural
cost proxies, not measured root-extraction or complete IC costs.

For each joint column, choose the largest total polynomial power among products
of the three inputs whose monomial-shifted support remains in the declared
column set. Every row must have its assigned distinct monic pivot. This is an
explicit finite construction, not a globally optimal shift calculation.

Any arithmetic mismatch fails the corresponding software check. Preserve failed
attempts. No determinant-only result counts as root recovery, a relation-yield
measurement, or the user's requested pipeline improvement. Independent blind
review is prepared separately and remains unexecuted until its required input
publication is authorized; do not fabricate its report.
