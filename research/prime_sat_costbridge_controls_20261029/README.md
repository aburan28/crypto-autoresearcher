# Fixed checker controls and prefix coverage

This additive package exercises the previously source-audited complementary-point
reference and checker. It preserves their original source, tests and receipts.
The prospective contract is
`coordination/prime_sat_costbridge_controls_20261029/software-contract.json`.
The actual fixed software outcomes are captured in `producer-results.json`;
they are not scientific samples or performance measurements.

The controls isolate a false nonroot certificate with an empty output domain,
four malformed inputs with matching recomputed hashes, two on-curve wrong-sum
witnesses, an order-three target's exceptional root, and the general square-root
path over F17. Deliberately weakened checker copies exist only in memory and
are labeled mutants; they demonstrate why the named guards matter. The original
checker is used for every acceptance or rejection result.

`prefix_cover.py` adds an iterative sparse-prefix coverage utility. Variable 0
is the first, least-significant bit. A `(depth,prefix)` pair denotes the entire
cylinder of assignments with those low bits. A terminal trie node closes that
subtree. For an auxiliary range `bits >> projected_bits < aux_bound`, setting
unassigned bits to zero gives the minimum auxiliary value; a missing child is
therefore either an invalid-domain subtree or an explicit uncovered assignment.
These two observations justify the traversal. Duplicates and overlapping
cylinders are idempotent, the zero-bit cube contains one assignment, and a zero
auxiliary bound denotes an empty domain.

There are at most `1 + sum(depth)` allocated nodes. Input validation also costs
one visit per supplied entry; integer shifts, comparisons, input and output
bit costs are additional. A transcript containing exponentially many prefixes
remains expensive. This is a source-level bound, with no timing comparison.

The utility always returns `arithmetic_verified=False`. It does not check a
polynomial refutation or validate a returned model. Coverage of unproved
cylinders establishes no UNSAT claim. The utility is not yet integrated into
the frozen SAT transcript checker; that requires separately validating every
algebraic clause, each projected-model fiber, and the auxiliary-domain encoding.
An uncovered assignment is a combinatorial gap, not necessarily a curve model.

Run the admitted fixed suite and captured original regressions with:

```sh
/home/ec2-user/prime-sat-research-venv/bin/python -B research/prime_sat_costbridge_controls_20261029/test_controls.py --receipt research/prime_sat_costbridge_controls_20261029/producer-results.json
```

The source review retains RFC 9380 Appendix I for square-root conventions and
the prior cost-bridge review for the exact target algorithm. The current SAT
implementation's `encoding.py::verify_search` provides the inspected exhaustive
coverage check. The proposed future partial-assignment interface is documented
by [PySAT IPASIR-UP](https://pysathq.github.io/docs/html/api/engines.html).
[Saccomani et al., Sections III-IV](https://hanielbarbosa.com/papers/2026fmcad-ffproofs.pdf)
separately justify algebraic identities and branch completeness; neither that
solver nor its proofs were run here. No novelty, solving-degree, scalar-recovery
or general ECDLP advantage is claimed by this software package.
