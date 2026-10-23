# Exact membership encoding screen for two binary factor bases

**Scope and status.** This is a target-blind structural search on the certified
ordinary-binary GF(2^61) fixture with prime subgroup order
576460752557211763 and cofactor 4. Each archived k11 base has 316 projected
columns and 632 accepted raw torsion coordinates in the same 11-bit affine
block. The proposed encoding has not been serialized into an XCNF, passed to
a solver, or used to collect a relation. This record changes no experiment,
hypothesis, baseline, or speed claim.

## Question and inputs

Can the exact membership predicate for the target-blind weighted base be
represented with fewer Boolean clauses than the current forbidden-value
encoding, while keeping the same realized columns and a matched local-random
control? The two archived [base records](../icperf_binary_torsion_k11_weighted_20261017/base.json)
and [local-random record](../icperf_binary_torsion_k11_local_control_20261017/base.json)
are the source of the predicates. Their [weighted XCNF manifest](../icperf_binary_torsion_k11_xcnf_20261017/manifest.json)
and [control XCNF manifest](../icperf_binary_torsion_k11_local_control_xcnf_20261017/manifest.json)
are the reference for the existing clause counts. Provenance: `internal`, read
from exact file bytes; their SHA-256 values are in [result.json](result.json).

## Method and exact derived counts

[analyze.py](analyze.py) forms each 2,048-entry Boolean indicator, applies the
GF(2) Möbius transform to obtain its algebraic normal form (ANF), and checks
ANF evaluation on all 2,048 inputs. It constructs reduced ordered binary
decision diagrams (BDDs) in both low-bit-first and high-bit-first orders and
replays each diagram against the full truth table. For a prospective CNF it
counts one variable per BDD node, conditional equivalence clauses for each
edge, and one accepted-root unit. The eight input blocks use independent
copies. These are derived counts for a specified proposed encoding; no
XCNF emission or solver measurement occurred.

| Exact predicate / encoding | Weighted | Local random |
| --- | ---: | ---: |
| Accepted 11-bit values (exact truth-table checked) | 632 | 632 |
| ANF nonzero terms (derived) | 520 | 516 |
| ANF degree (derived) | 9 | 9 |
| Low-bit-first reduced BDD nodes per block (derived) | 188 | 212 |
| High-bit-first reduced BDD nodes per block (derived) | 193 | 216 |
| Archived forbidden-value clauses across eight blocks (`internal`) | 11,328 | 11,328 |
| Proposed low-bit-first BDD clauses across eight blocks (derived) | 5,640 | 6,424 |
| Proposed BDD variables added across eight blocks (derived) | 1,504 | 1,696 |

The [editable figure source](figure.py) and [SVG](figure.svg) show the
predicate path and clause counts. The reduction in a membership *clause
count* follows algebraically from this encoding definition; it says nothing
about a solver's search tree or the degree of regularity. Existing channel-0
formulas have 89,122 CNF clauses and 62,655 native XOR rows in both arms.
Replacing only the current 11,328 forbidden-value clauses would yield
83,434 and 84,218 CNF clauses respectively, conditional on the new encoder
preserving the rest of the circuit. It also adds the BDD variables above.
No such replacement formula has yet been built, and ANF degree 9 is **not**
the system's degree of regularity.

The first scratch output [result_initial.json](result_initial.json) recorded
its `started_at` timestamp after the calculation. The numerical predicates
and counts were unchanged. The corrected source and a fresh run produced
[result.json](result.json) with `started_at` taken before calculation; both
records are retained so the metadata correction is visible.

## Next discriminating test

Write an exact BDD XCNF encoder and an independent parser that checks all
2,048 values for each membership block, along with the existing planted
full-point controls. Freeze matched weighted and local-random formulas on the
same public target schedule with both forbidden-value and BDD encodings.
After a complete protocol, legal lane and executor admission, measure input
generation, full formula size, memory, solver conflicts and wall, rejected
models, independently certified rows, and censoring. A smaller serialized
formula with worse solver behavior redirects encoding choice; a genuine
per-call benefit still requires useful-rank, linear-algebra, target and
matched-rho accounting before any end-to-end statement.

## Visual and graph maintenance

[report.pdf](report.pdf) contains the graph and explanatory diagram. No
canonical ECDLP cost or curve graph changes because this search establishes
only predicate representation counts, not a relation or performance result.
