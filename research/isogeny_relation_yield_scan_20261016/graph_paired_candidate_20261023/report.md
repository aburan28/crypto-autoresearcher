# Paired targetwise confirmation candidate

2026-10-22. This report describes implementation controls only. It makes no
scientific verdict about graph-wide relation yield or ECDLP cost.

## Scope and method

The candidate applies the selected P29/P37 vertex list from the frozen study
draft to each of the three native bases. It reads only fresh confirmation
collector outputs whose graph-attempt and supervisor receipts match the
preceding confirmation analysis. For each vertex it constructs the four cells
in [`paired_table.svg`](paired_table.svg), using the same target index and
coefficient stream in each arm. The difference between two bases is the
number useful only on the left minus the number useful only on the right,
divided by 32,768 targets. All cells and receipt references remain in the
write-once output. The selected vertex set is discovery-selected, so these
descriptive comparisons do not represent an unselected graph-wide average.

## Bounded controls

`python3 -m unittest research/isogeny_relation_yield_scan_20261016/graph_paired_candidate_20261023/test_paired.py -v`
passed three tests. They check a four-target 2-by-2 table, reject changed
collector digests/coefficient streams/order, and parse the existing bounded
P37 eight-target fixture in
[`graph_solve_candidate_20261023/controls/attempt-3`](../graph_solve_candidate_20261023/controls/attempt-3).
The parsed useful count equals that fixture's independent rank-verifier count
of 2/8. This exercises the format and count binding, not a paired comparison
over the full graph. No new scientific trial or performance benchmark ran.

## Limits and next checks

The candidate requires a Coordinator-approved plan binding both analysis
sources and all selected arm receipts. There are no such receipts in this
directory. The preceding analyzer supplies simultaneous marginal intervals;
this script supplies targetwise concordance and discordance. Curve-by-base
interaction can be read as the vector of paired differences across selected
vertices, but a population-level interaction test is not specified here.
No canonical scientific graph changed because there is no new curve evidence.
The subsequent stage measures complete same-point ECDLP and matched rho costs.
