# Sorted witness scope correction, 2026-10-19

This PR review correction qualifies the unrestricted witness-preservation
statement in `H-ICPERF-3982eb` and the original specification archived at
`ed2de007d759452458683e5163d449b1fe76b804`. It changes no official hypothesis
state and authorizes no solver call. The original hypothesis, design report,
snapshot receipts and historical source commits remain unchanged.

The [retained counterexample](20261019-sorted-exception.json) uses eight signed
points from the weighted membership set, including a point and its inverse.
Its unsorted tuple has representable intermediate points, satisfies every
clause and XOR of an independently evaluated original-encoder formula, and
passes full-point certification. Its raw target is
`(27643812986663646, 1204997118723717215)`.

Stable coordinate sorting puts the inverse pair first. Their sum is infinity,
so the first intermediate phi value is undefined and `primary_for` rejects
the sorted tuple with `exceptional intermediate point`. Group commutativity
preserves the final point; it does not preserve representability in this
affine seven-S3 chain. The certificate establishes a counterexample to the
stated stable-permutation construction. It does not prove that the same target
has no other sorted relation or that the sorted formula is unsatisfiable.

The counterexample has a different target from the two predeclared positive
controls. Both existing controls still pass their original/sorted CNF, XOR,
point and mutation checks. The current unfrozen specification now explicitly
restricts witness preservation to tuples whose original and sorted prefixes
of lengths two through seven remain affine with x outside `{0, gamma}`.
Unrestricted preservation is false; full representation equivalence and
completeness remain unresolved. The two-control diagnostic provides no
natural-yield or timing result from this static review.

Reproduce the retained counterexample, without a solver, from repository root:

```sh
python3 -m unittest discover -s experiments/EXP-ICPERF-554db4/implementation -p test_sorted_exception.py -v
```

The regression rebuilds the original formula for the recorded target, checks
the complete unsorted model and point certificate, compares the final sums,
then verifies the sorted exceptional intermediate. No scientific run or
blind target-schedule derivation is performed. In particular this review is
not a J0 or J1 attestation.

The mutable trial preview binds the corrected specification and regression
source. The archived blind-review plan in `BATCH-8f7bd6` binds the earlier
specification hash `9078440def11b8b826367e50b4bd172f05b43f3360faa840f631078ae3c25348`.
Its write-once plan and handoffs remain historical records. A Coordinator must
supersede or explicitly rebind that plan before dispatch, retaining the
independent-session and backend gates. The experiment stays unapproved.
