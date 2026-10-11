#set page(paper: "a4", margin: 16mm)
#set text(font: "DejaVu Sans", size: 10pt)
#set par(justify: false, leading: .65em)
#set heading(numbering: none)
#set page(footer: align(right)[Solinas rank follow-up · #counter(page).display()])
= Solinas rank measurements
2026-10-11 UTC · EXP-ECDLP-4c6a09 · Observations, with unresolved cases retained

*First cubic case: rank 1 over Q, rank 3 over K — two added independent directions.*
The curve is $y^2=x^3-3x+3$ and $K=QQ(alpha)$, with $alpha^3-alpha-1=0$.
Certified descent lower and upper bounds agree. This is a computation using
standard 2-descent, not an independently reviewed research-state transition.

#figure(image("rank-construction.svg", width: 100%), caption: [Measured cubic
example. Reduction can identify points; a higher characteristic-zero rank alone
does not recover an unknown finite-field scalar.])

== What rank counts
The free part of E(K) is $ZZ^r$: rank counts independent directions. P, −P,
and 2P count as one direction. The experiment measures the added rank
$r_K-r_Q$, using a rational baseline for each curve.

2-descent supplies a lower bound and a Selmer upper bound. Subtract rational
2-torsion from the raw Selmer dimension. Equal bounds determine rank;
different bounds leave an interval. Both automatic Sha-square/parity lower
bound increases in the inherited code were disabled.

== Actual input coverage
*335 distinct rational curves, all exact:* rank 0: 108; rank 1: 181;
rank 2: 45; rank 3: 1. The follow-up contains *157 distinct number-field/curve
pairs*, including all *88 Solinas pairs* and all original cubic controls.
Higher-degree random/pure-field controls are outside this scope. There are
*51 certified exact NF ranks* and *34 certified positive
rank gains* across the distinct follow-up pairs.

Source: #link("../../runs/RUN-ECDLP-7cfef7/raw-result.json")[RUN-ECDLP-7cfef7],
#link("../../runs/RUN-ECDLP-280de8/raw-result.json")[RUN-ECDLP-280de8],
#link("../../runs/RUN-ECDLP-959b32/raw-result.json")[RUN-ECDLP-959b32], and
#link("../../runs/RUN-ECDLP-aba670/raw-result.json")[RUN-ECDLP-aba670].

#pagebreak()
= Results, including what remains unresolved
#figure(image("cubic-rank-gain.svg", width: 100%), caption: [Cubic rank gain
above each curve's rational baseline. Labels count distinct pairs; gray means
no completed NF bound. Arm membership can overlap. No independence or
statistical-significance claim is made.])

#figure(image("solinas-rank-status.svg", width: 100%), caption: [All 88 distinct
Solinas cases. GRH-conditional data remain distinct from certified ranks.])

#table(columns: (1.35fr, .7fr, .8fr, 1fr, 1.2fr), inset: 5pt,
  [Solinas shape], [Pairs], [Certified exact], [GRH conditional], [Interval / unresolved],
  [P-192],
[43],
[22],
[0],
[21],
[P-224],
[15],
[0],
[15],
[0],
[P-256],
[15],
[0],
[9],
[6],
[P-384],
[15],
[0],
[4],
[11])

GRH means the generalized Riemann hypothesis. Higher-degree auxiliary
class/unit data were not all verified with bnfcertify. Those rank bounds keep
that assumption, including when the two bounds agree. A missing NF upper bound,
tool error or watchdog does not mean rank zero. Higher-degree curves can gain
rank even when the earlier point-search run found no new points.

#pagebreak()
= Reproduction and interpretation
== The concrete cubic example
Descent found representatives $(1,1)$,
$(1-2alpha,-2alpha^2+2alpha-1)$ and
$((6alpha^2+7alpha-27)/25,(-121alpha^2-162alpha+182)/125)$.
All equations were checked exactly. Three independent mod-2 classes and
an upper rank bound of three determine rank three. A saturated basis was
not computed or claimed.

The field relation supplies a concrete point: for
$x=1-2alpha$ and $y=-2alpha^2+2alpha-1$,
$y^2-(x^3-3x+3)=4alpha(alpha^3-alpha-1)=0$.
Descent then certifies its role among independent directions.

== Tool repairs and exact scope
The first batch measured all rational ranks, then exposed an output-format
incompatibility and an enormous residue-field allocation. It was stopped and
retained. The follow-up reuses 8 error-free exact
NF results and completes the remaining cubic instances. A separate run measures
candidate-group upper bounds for all 45 higher-degree pairs, before local
conditions and quartic searches. This is an upper bound, not an asserted
exact Selmer dimension. Modified Simon
code normalizes projective output and caps explicit residue enumeration.
Large-prime local search must produce an exactly checked square witness;
an unresolved search throws rather than inferring an obstruction.

PARI 2.17.2; pinned Sage source commit
#text(size: 8pt)[46a9468cf7fccca63c6b873cb52b73ea141da068].
At most four GP workers; 4 GiB address space each; 128 MiB initial stack,
2 GB maximum stack; seed 1; 80-digit real precision; 120 s process watchdog.
Cubic LIMTRIV=2 then 4, LIM1=LIM3=2. Larger-degree initial searches use
zero limits and supplied rational points. All class/unit data are certified
for cubic calculations; larger auxiliary data retain explicit GRH labels.

== Limits on the interpretation
Rank depends on K and the characteristic-zero curve model, so repeated
reduction primes do not add independent rank measurements. Random draws can
include the Solinas polynomial itself; different defining polynomials can
give isomorphic fields. These data do not establish a special Solinas rank
advantage. No unknown finite-field scalar was recovered and no ECDLP cost
bound was measured. Standard Simon/PARI 2-descent is the method being used.

== Sources and immutable evidence
#link("report.md")[Full report and concrete positive cases] ·
#link("ranks.csv")[All 157 bounds and curve/field identities] ·
#link("summary.json")[Summary and consistency checks].

#link("../../runs/RUN-ECDLP-7cfef7/plan.json")[Frozen input plan] ·
#link("../../runs/RUN-ECDLP-7cfef7/source/provenance.json")[Exact source patches and hashes] ·
#link("https://github.com/sagemath/sage/blob/46a9468cf7fccca63c6b873cb52b73ea141da068/src/sage/schemes/elliptic_curves/ell_number_field.py")[Sage rank-bounds wrapper] ·
#link("https://github.com/sagemath/sage/tree/46a9468cf7fccca63c6b873cb52b73ea141da068/src/sage/ext_data/pari/simon")[Simon GP source].

Raw follow-up SHA256: #text(size: 7pt)[f3d0af7c3c88cdbda3576fe8f20c02a5fa80f5167f872629a5642eb2a6f7df1f].
The original coverage report and raw JSON remain unchanged. No canonical
ECDLP frontier graph or scientific status was promoted. Sources are retrieved
or internal; algebraic explanations are derived; ranks/bounds are measured.
