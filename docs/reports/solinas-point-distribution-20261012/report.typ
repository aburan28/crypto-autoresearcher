#set page(paper: "a4", margin: 16mm, footer: context [#align(center)[#counter(page).display()]])
#set text(font: "DejaVu Sans", size: 10pt)
#set par(leading: .6em)
= Solinas primes and point distributions
2026-10-12 · point-distribution-20261012 · measured observations

None of the 24 primary intervals excludes zero. The study did not resolve a mean difference in these prespecified metrics at the stated simultaneous confidence level. This does not establish equality or exclude other patterns.

== What we are measuring
The field is integers modulo p; the curve is $y^2=x^3+A x+B$ over that field.
At each x, the right side is either a nonzero square (two points), zero (one
point) or a nonsquare (no points). x coverage and point mass are distinct.

With quadratic character $chi$ and $chi(0)=0$:
$ w(x)=1+chi(x^3+A x+B), quad N=1+sum_(x in F_p) w(x). $
The extra one is infinity. Trace $t=p+1-N$ satisfies $abs(t)<=2 sqrt(p)$.
If Z cubic roots lie in the field, liftable x count is $(N-1+Z)/2$.
Coverage should be close to one half. Local gaps and clustering require
separate measurements against matched controls.

For uniformly random nonsingular models, expected coverage is
$1/2+(p-1)/(2p^2)$ and expected $t^2/(4p)$ is $(1-1/p^2)/4$.
See THEORY.md for the derivation and exhaustive small-prime checks.

== Fixed wider design
20,480 complete curve censuses over 5,120 distinct small primes: 512 blocks
each at 18 and 20 bits, four curves per field. Each sparse-prime block has
two random and two mod-96 controls, matched within 5% and the same bit size.
Sparse means signed nonadjacent binary weight at most six.

3,328 whole-curve probe cases at P-192/P-224: 512 curves at each fixed
structured prime, with 144 random and 144 residue-matched fields per case,
four curves per control field. Their existing pools match within 1% and
mod 12. Counts are original exact PARI source inputs; x probes are new.

#image("workflow.svg", width: 100%)

Every curve has 4,096 uniform x probes and 2,048 adjacent coordinates.
All outcomes are retained; no outcome-driven stopping. No scalar search.

#pagebreak()
= Primary distribution comparisons
Three metrics: point-count spread $t^2/(4p)$, adjacent-coordinate
liftability correlation and weighted 32-bin x dispersion. Each is compared
with R (random) and C (residue-matched). Differences are S minus control.

#image("primary-comparisons.svg", width: 100%)

Bars: approximate Student/Welch intervals, nominal 99.9958333% each;
Bonferroni targets nominal 99.9% coverage jointly over 24 comparisons.
Toy units: 512 paired prime blocks, all curves in a field kept together.
Large-case units: 512 S curve draws at a fixed prime versus 144 control-field
means. No exact coverage or power guarantee. Source: analysis.json.

#pagebreak()
= Numerical comparisons and controls
All intervals use the frozen multiplicity correction. Trace², Lag 1 and
Bins refer to the three dimensionless metrics above.

#table(columns: (1.2fr, 1fr, .6fr, 1.2fr, 1.2fr, 1.2fr), inset: 3pt, [Case],
[Metric],
[Arm],
[Difference],
[Low],
[High],
[toy18],
[Trace²],
[R],
[-0.00468],
[-0.03189],
[0.02253],
[toy18],
[Trace²],
[C],
[-0.00346],
[-0.03179],
[0.02487],
[toy18],
[Lag 1],
[R],
[0.00101],
[-0.00142],
[0.00345],
[toy18],
[Lag 1],
[C],
[0.00067],
[-0.00172],
[0.00307],
[toy18],
[Bins],
[R],
[0.36843],
[-0.54458],
[1.28143],
[toy18],
[Bins],
[C],
[0.14520],
[-0.75731],
[1.04772],
[toy20],
[Trace²],
[R],
[-0.01501],
[-0.04321],
[0.01319],
[toy20],
[Trace²],
[C],
[-0.00810],
[-0.03574],
[0.01954],
[toy20],
[Lag 1],
[R],
[-0.00076],
[-0.00328],
[0.00177],
[toy20],
[Lag 1],
[C],
[-0.00098],
[-0.00335],
[0.00140],
[toy20],
[Bins],
[R],
[0.09504],
[-0.78333],
[0.97341],
[toy20],
[Bins],
[C],
[-0.09292],
[-1.04763],
[0.86180],
[P-192],
[Trace²],
[R],
[0.00947],
[-0.05426],
[0.07320],
[P-192],
[Trace²],
[C],
[0.00520],
[-0.05519],
[0.06560],
[P-192],
[Lag 1],
[R],
[-0.00028],
[-0.00552],
[0.00497],
[P-192],
[Lag 1],
[C],
[-0.00123],
[-0.00654],
[0.00408],
[P-192],
[Bins],
[R],
[0.05529],
[-1.87740],
[1.98798],
[P-192],
[Bins],
[C],
[-0.65363],
[-2.67717],
[1.36991],
[P-224],
[Trace²],
[R],
[0.01218],
[-0.05210],
[0.07646],
[P-224],
[Trace²],
[C],
[-0.00181],
[-0.06601],
[0.06239],
[P-224],
[Lag 1],
[R],
[0.00037],
[-0.00539],
[0.00614],
[P-224],
[Lag 1],
[C],
[0.00132],
[-0.00414],
[0.00677],
[P-224],
[Bins],
[R],
[0.48363],
[-1.49721],
[2.46447],
[P-224],
[Bins],
[C],
[0.20673],
[-1.77026],
[2.18372])


== Why coordinate controls matter
The map $(x,y) -> (u^2 x,u^3 y)$ yields $A'=u^4 A$ and $B'=u^6 B$.
It preserves the curve order while changing numerical positions. One
companion per field is checked; it is not an independent sampling unit.
Shuffled windows preserve counts and check the clustering statistics.
Synthetic clustered sequences test statistic sensitivity only.

#image("coverage-and-coordinates.svg", width: 94%)
Dots are descriptive means, without inferential intervals. Primary intervals
are on page 2. Full toy census bins isolate coordinate changes with N fixed.
Companion sampled-window differences also include fresh sampling; they do not
alone isolate a coordinate effect. See coordinate-checks.json.

#pagebreak()
= Retained data, checks and limits
#table(columns: (1.2fr, .6fr, 1fr, 1fr, 1.3fr, 1.2fr), inset: 3pt, [Case],
[Arm],
[Fields],
[Curves],
[Coverage],
[Lag 1],
[toy18],
[S],
[512],
[2048],
[0.499990],
[-0.00035],
[toy18],
[R],
[1024],
[4096],
[0.500098],
[-0.00136],
[toy18],
[C],
[1024],
[4096],
[0.499999],
[-0.00102],
[toy20],
[S],
[512],
[2048],
[0.499919],
[-0.00123],
[toy20],
[R],
[1024],
[4096],
[0.500092],
[-0.00048],
[toy20],
[C],
[1024],
[4096],
[0.500058],
[-0.00026],
[P-192],
[S],
[1],
[512],
[0.499911],
[-0.00044],
[P-192],
[R],
[144],
[576],
[0.499893],
[-0.00017],
[P-192],
[C],
[144],
[576],
[0.499863],
[0.00078],
[P-224],
[S],
[1],
[512],
[0.499766],
[-0.00023],
[P-224],
[R],
[144],
[576],
[0.500112],
[-0.00060],
[P-224],
[C],
[144],
[576],
[0.500305],
[-0.00154])


12 prelaunch tests passed. Post-run checks verify 5,698
field artifacts, 23,808 base curves and
380,928 independently calculated
character spot checks, point examples, census identities and checksums.
No failed field rows. This is same-session software verification, not an
independent scientific review.

Worker CPU: 4649.3 s; run wall time:
1566.7 s, three workers. Raw arrays:
1,981,842,986 bytes; full census masks, zero positions,
uniform probe inputs and weights, windows and companion controls retained.
Whole-curve URNs hash exact p,A,B; no subgroup generator is selected.

== Interpretation limits
The two large structured primes are fixed cases. Their old curve pools
are source data, not a fresh sample of a large-prime family. Probe windows
are not a whole-field census. Constrained prime matching and approximate
intervals limit coverage guarantees. No detected mean difference would
not establish equality or exclude higher-order patterns. Numeric clustering
alone establishes no group-invariant effect. This run makes no security
claim or official hypothesis transition.

== Sources and reproducibility
Source commit: #text(size: 8pt)[69cdec441c5aec84a18483c32bb7d22d0a387bba].
See report.md for links to protocol, config, inputs.json, environment.json,
receipt.json, analysis.json, verification.json and per-field outputs.
P-192/P-224 pools: EXP-ECDLP-5184f7 / RUN-ECDLP-d0e449 preparation/curves;
exact source hashes are frozen in inputs.json. Derived CSV files list all
comparisons and exact whole-curve identities. Full dataset archive checksums
are recorded separately. All sources are internal/retrieved local files.

Historical rank, point-supply, attack and ML graphs and frontier files were
inventoried. Their supported claims are unchanged; no canonical graph edge
is updated. See graph-inventory.json. The editable diagram and SVG figures
are kept with this Typst source and PDF.

Proposed next check: lock any newly interesting descriptor and evaluate it
on fresh fields and curves. ML may explore this dataset afterward.
