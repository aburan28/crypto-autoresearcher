#set page(paper: "a4", margin: 17mm)
#set text(size: 9pt)
#set heading(numbering: none)

= Target-blind 896-element prime coset search

*Exact input preparation and independent Sage replay, 2026-10-17 UTC.*
The 63-bit prime field admits a coset order 896. A frozen 16-seed scan retained
every point list and selected only by realized size. Its largest base has
475 points (seed 20261027), above the optimistic m=8 counting threshold of
441 columns. This does not prove target coverage or improve ECDLP cost.

#image("2026-10-17-prime-coset-896-search.svg", width: 100%)

Nine of 16 candidates cross the necessary count threshold. The selected
base has signed eight-term multiset upper count 16,944,744,476,780,007,525,
or 1.837153 times the subgroup order; collisions can still leave uncovered
targets. With seven summands on this same base, uniform-target coverage is
at most 1.535760%. Direct S8 therefore remains a seven-summand comparison.

== Independent replay and setup

SageMath 10.10.rc0 independently checked 14,336 coset x-values, each stored
point, the root orders, and the winner. The complete scan took 18.765831 s
wall and 0.829370 s process CPU on this host; constructor-call wall times
sum to 0.370852 s and exclude other scan work. Field selection, independent
replay, solver, relation, rank, target and rho costs are separate.

== Next gate

The prior generic quadratic-lift code locally derives 11 gates per x and a
103-variable, 104-equation, 294-monomial m=8 input for this base. Freeze and
independently check that system, then run a bounded direct/lifted comparison
against equal-realized-size random and small-x controls on the same targets.
Only complete charged relations, rank and unseen target work can establish
an end-to-end improvement. The companion Markdown report links all sources,
the full scan and the independent replay.
