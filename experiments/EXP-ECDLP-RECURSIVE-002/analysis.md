# Analysis

The first independent pre-run audit returned `REVISE` at commit `96fcc1b`.
The arithmetic reconstruction survived, but command provenance, budget
enforcement, positive-control binding, order independence, and coordinate cost
accounting did not. No canonical v1 output exists.

Version 2 repairs those arithmetic/control defects and changes the curve seeds so the
nine curves use nine distinct field primes. Reduced smokes establish only
protocol execution, clean-curve selection, mandatory controls, exact
uniform-order reconstruction, charged-cost reconstruction, rho correctness,
and generator/verifier agreement. They do not execute the 31+31 null schedule
and are not evidence for or against the hypothesis.

The second independent audit returned `REVISE` at commit `878acef`. It found
that the plan could still be replaced, predecessor provenance could be forged,
descendant resources escaped, post-run mutations were unchecked, and same-inode
aliases were accepted. Execution protocol v3 addresses those findings with an
external approval lock, approved-plan-only execution, complete receipts and
Git transitions, post-run checks, same-inode rejection, isolated absolute
Python argv, and a no-descendant resource policy. A sampling-only fast-detach
repair attempt failed 12 of 12 adversarial trials and remains a scoped negative
artifact; canonical locked runs now forbid child creation instead.

No third-audit verdict or canonical 31+31 result exists yet.

The literature comparison also remains model-aware. The fixed-generator
`ST^2` advice bound is a restricted theorem for random generic encodings. The
2026 structured model has a `delta*T` escape term, but a unary coordinate
predicate does not itself instantiate `delta`. `SGCP-EMBED-001` is the next
theory experiment: produce a valid partial-operation embedding certificate or
the smallest unique-factorization/injectivity counterexample.
