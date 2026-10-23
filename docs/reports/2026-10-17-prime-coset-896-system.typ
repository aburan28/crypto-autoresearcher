#set page(paper: "a4", margin: 17mm)
#set text(size: 9pt)
#set heading(numbering: none)

= Exact m=2…8 inputs for the selected 896-coset base

*Frozen algebraic inputs and independent planted-equation replay, 2026-10-17
UTC.* The selected target-blind base has 475 points on the certified 63-bit
prime-order curve. The new record serializes direct and quadratic-lifted
chained-S3 systems for every m=2…8. These are correctness inputs, not
observed solver costs or natural relations.

#image("2026-10-17-prime-coset-896-system.svg", width: 100%)

At m=8 the d=896 lifted input has 103 variables, 104 equations and 294
monomial occurrences, versus 111, 112 and 310 for the prior d=788 input.
The new base has 475 rather than 380 columns. The d=896 square-and-multiply
chain uses 11 gates per x instead of 12; both lifted systems have maximum
input degree four. Base sizes differ, and input counts predict neither
Gröbner degree nor runtime.

== Independent check

SageMath 10.10.rc0 checked all seven known-point sums, 70 direct and 455
lifted equations, and an altered-auxiliary rejection at each arity. The
896-element coset has 421 x-values that do not lift to the curve; arbitrary
solver roots still need point and sign checks. Direct S8 addresses seven
summands plus target; eight summands need S9 or a chained construction.

== Remaining gate

Freeze equal-realized-size 475-point random and small-x controls, then run
bounded matched solver comparisons under an approved protocol. Natural
relations, useful rank, unseen target work, complete setup and memory
charges, and matched rho remain unmeasured. The companion Markdown report
links the exact systems and independent replay.
