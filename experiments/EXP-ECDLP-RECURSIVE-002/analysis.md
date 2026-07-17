# Analysis

The first independent pre-run audit returned `REVISE` at commit `96fcc1b`.
The arithmetic reconstruction survived, but command provenance, budget
enforcement, positive-control binding, order independence, and coordinate cost
accounting did not. No canonical v1 output exists.

Version 2 repairs those protocol defects and changes the curve seeds so the
nine curves use nine distinct field primes. Reduced smokes establish only
protocol execution, clean-curve selection, mandatory controls, exact
uniform-order reconstruction, charged-cost reconstruction, rho correctness,
and generator/verifier agreement. They do not execute the 31+31 null schedule
and are not evidence for or against the hypothesis.

The literature comparison also remains model-aware. The fixed-generator
`ST^2` advice bound is a restricted theorem for random generic encodings. The
2026 structured model has a `delta*T` escape term, but a unary coordinate
predicate does not itself instantiate `delta`. `SGCP-EMBED-001` is the next
theory experiment: produce a valid partial-operation embedding certificate or
the smallest unique-factorization/injectivity counterexample.
