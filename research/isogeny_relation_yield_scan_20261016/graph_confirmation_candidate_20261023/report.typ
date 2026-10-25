#set page(paper: "a4", margin: 20mm)
#set text(font: "Helvetica", size: 10pt)
= Held-out confirmation candidate and interval tooling control

2026-10-22. Implementation and tooling observations only; no scientific
verdict about graph relation yield or ECDLP cost.

#image("confirmation_flow.svg", width: 100%)

The candidate verifies every selected arm's supervisor and graph-attempt
receipts, fresh paired coefficient stream, 32,768-target quota and fixed rank
prefixes. It calculates integer-inverted hypergeometric intervals with a
Bonferroni family correction and nominates at most six finalists per stratum.
No confirmation receipts were available for analysis.

Four pure controls passed: small-population exact boundaries, zero-count
ratios, finalist ties, and cache replay/tamper rejection. These controls do
not exercise complete P29/P37 confirmation trials.

One tooling calculation on an Apple M4 Pro with Python 3.13.1 and macOS 26.6
took 44.834188750 seconds of measured wall time. Parameters were population
81,640,511,860, draws 32,768, illustrative count 2,048, and tail threshold
1/58,800. Exact bounds were 4,661,659,633 and 5,569,195,061. Source and
command are bound in `benchmark-interval.json`. The count was a calculation
input, not a measured relation yield. There is one timing and no spread.

Next: freeze the source with a Coordinator-approved plan after complete
discovery; collect every fresh confirmation receipt; implement paired
targetwise and curve-by-base secondary summaries; then run complete same-point
ECDLP and matched rho measurements on the nominated finalists.
