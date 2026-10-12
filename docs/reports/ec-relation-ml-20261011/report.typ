#set page(paper: "a4", margin: 17mm, footer: context [#align(center)[#counter(page).display()]])
#set text(font: "DejaVu Sans", size: 9.5pt)
#set par(leading: .5em)
= ML-assisted EC relation research flow
2026-10-11 · measured engineering pilots · source 3e02da06533b

The runnable bridge uses ML to choose an algebra solver, checks exact EC point
relations, removes dependent rows and verifies any uniquely identified scalar.
It implements a discovery/evaluation flow. It establishes no cryptographic-size
resistance result or new attack mechanism.

#table(columns: (1fr, 1.8fr, 1.5fr, 1.5fr), inset: 4pt, [Pilot],
[Fields / cases],
[Jobs / censored],
[Test new logs],
[quick],
[12 / 24],
[96 / 0],
[4 / 8],
[standard],
[48 / 192],
[768 / 0],
[11 / 48])

Every completed action agreed with separate exhaustive evaluation of the original
equations and exact point checks. All 864 jobs were retained;
the 13 mathematical/leakage tests and software replays passed. The standard test
has 48 targets in 12 unseen finite fields.

#table(columns: (1.8fr, 1.8fr, 1.9fr), inset: 4pt, [Selector],
[Process/PAR-2 mean (s)],
[Rank / total target logs],
[Fixed 0],
[0.510],
[56 / 18],
[Best fixed (training)],
[0.504],
[56 / 18],
[Random (seed 0)],
[0.527],
[56 / 18],
[Ridge],
[0.535],
[56 / 18],
[Bandit],
[0.521],
[56 / 18])

#image("solver-costs.svg", width: 100%)

All completed solvers deliver the same information: a sum of 56
per-target independent ranks and 18 total target logs,
including 7 already-known G/-G targets.
Only 11 are newly identified. ML found no
additional relations here. Exact BSGS recovered all 192 standard targets.
Warm-parent BSGS timing is not a paired process benchmark. Post-hoc shared-batch
accounting gives a sum of 39 joint per-curve ranks and 13 newly identified
test targets. These differ from per-target sums; all solvers supply the same pool.
No full batch-cost claim.

Timings include fresh process startup; dots are field means, not intervals.
These are one-run software observations, with no preregistered statistical
security inference. Sources: immutable pilot manifests, labels and evaluation JSON.

#pagebreak()
= Why rank is not recovery
Let $Q = q G$ and $P = u G$. On the checked toy curve
$E / F_17: y^2 = x^3 + 2x + 2$, subgroup order 19, cofactor 1, $G = (5,1)$,
take $P = 5G$ and $Q = 7G$. The point equation $2P-Q=3G$ gives
$2u-q=3$ modulo 19. Rank one with two unknowns leaves q undetermined.
Add $P=5G$: rank becomes two, and q=7 is unique and verifies against Q.

Unit rank counts number-field multiplicative units. Mordell–Weil rank counts
independent infinite-order EC points over that field. Modular relation rank
counts constraints between finite-subgroup logs. Predicting one of these ranks
does not recover a scalar. Extra seeds can add rank while leaving q unknown.

#image("workflow.svg", width: 100%)

Solid boxes are implemented. Dashed extensions/confirmation are proposed.
Training feedback uses training fields only. Scalar truth and post-solve outcomes
are excluded from features. S3 roots must lift to subgroup points with signs
that verify P1+P2=Q. Duplicate, negated and dependent information adds no rank.
Known maps need explicit transport to the original curve before their relations
can be counted there; map discovery is outside this pilot.

#pagebreak()
= Controls, costs and data independence
#image("relations-and-recovery.svg", width: 100%)

The archived number-field data have 104 cohorts from 24 source fields but only
six finite curves over three primes. The 1,664 nominal attempts reuse targets.
A simultaneous source-field and finite-curve holdout connects all 104 rows.
Random row splitting would test reuse. The archive is exploratory, not fresh
confirmation. Source: RUN-ECDLP-9e6cc1 and archived-data-audit.json.

Held-out finite fields under a fixed lift and wholly unseen lift templates are
separate generalization questions. P-192 and P-224 are fixed fields: recognizing
their constants or sparse binary encodings is not evidence about their logs.

Controls: fixed action, best training fixed action, uniform policy, shuffled
action labels, planted learnable and constant-reward cases; exact original-root
and signed-point checks; point aliases, false relations and field/curve leakage;
exact generic BSGS on the same targets. There is no speedup acceptance gate.

The pilots took 465.3 seconds in total. Standard acquisition cost
was 396.44 seconds;
fit and selection took 0.083 seconds.
Full overhead and memory are retained in the manifests. A one-off attack must
charge acquisition and fitting, not just a chosen solve. Subgroups here are
3–8 bits; grid root extraction does not scale.
Quick timing overlapped Git reads/checkout. One 1.620-second process spent only
0.0294 seconds in its timed solver. No such timing difference is a security finding.

Next scientific confirmation (proposed): fresh evaluator-held challenges,
checkpoint/predictions locked before truth release, matched random-prime and
random-number-field/seed controls, identical-target BSGS/rho, and full cost.
Target at least 512 independent eligible matched blocks per size stratum with
four curves and four controls of each type where available. Fixed P fields use
new curve/control pairings. Estimate power and freeze final counts before
opening confirmation labels. More reused target rows do not create new fields.

For three primary families, reserve 99.9667% intervals each for 99.9% joint
nominal coverage; additional primary tests require more correction. Resample
independent matched blocks, predeclare missingness/stopping/amortization, and
seek an independently reviewed mechanism. Higher confidence alone widens intervals.

#pagebreak()
= Prior evidence and limits
The earlier generic-resistance results remain unchanged:

#table(columns: (1.8fr, 1fr, 2.5fr), inset: 4pt, [Prior scope],
[Ratio],
[Marginal 99.9% interval],
[Solinas toy family],
[0.9952],
[\[0.9725, 1.0185\]],
[P-192],
[0.9834],
[\[0.9174, 1.0581\]],
[P-224],
[0.9875],
[\[0.9261, 1.0520\]])

Source runs: RUN-ECDLP-07aad1 (Solinas toy fields) and RUN-ECDLP-d0e449
(full P-192/P-224 fields, 16–20-bit subgroups). The intervals are conditional
on their frozen sampling/matching. These comparisons did not detect greater
generic resistance in those scopes. Cryptographic-size ECDLP remains unresolved;
localized or different structural mechanisms require different tests.

RUN-ECDLP-6d910b measured rank gains for selected lifts but no advantage over
its declared BSGS comparison. Exact lift preprocessing was excluded from its
primary group-call totals. New learned candidates must charge that work.

All exact benchmark curve/subgroup/generator/target identities are in
curve-identities.csv and the public cases.json files. Primary source:
tasks/ec\_relation\_ml/PROTOCOL.md and immutable examples/standard-20261011.
Software verification replays exact roots, signed relations, ranks, recovery,
fits and controls. It does not independently authenticate timings or constitute
independent scientific review. No sealed bound or official status changes.

Prior-art records were read from the repository because the knowledge MCP was
unavailable. KN-LIT-001/KR-IC-5a43e5 describe established summation-polynomial
decomposition. KN-LIT-d8e1b9/KR-IC-5931ee relay a negative result for naive
prime-field index calculus under statistical assumptions. KN-LIT-1940 is an
abstract-level pointer about twist-class redundancy. Primary papers were not
read in this round; no novelty or new impossibility follows from these pointers.
Unchanged record snapshots and hashes are in source-records/ and source-records.json.

The historical report diagrams and canonical frontier records were checked;
graph-inventory.json explains why no supported graph/frontier changes. The new
diagram is an engineering workflow, not a proven mathematical mechanism.

Artifacts: report.md; workflow.dot/svg; solver-costs.svg;
relations-and-recovery.svg; pilot-summary.json; archived-data-audit.json;
curve-identities.csv; source-bindings.json; both software verification receipts.
Publication is tracked separately and requires authenticated GitHub access.
