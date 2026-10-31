#set page(paper: "a4", margin: (x: 18mm, y: 17mm))
#set text(font: "DejaVu Sans", size: 10pt)
#set par(justify: true)
#let rank = math.op("rank")
#let span = math.op("span")
#set heading(numbering: "1.")
#set page(footer: context [#text(size: 8pt)[T-1107 · Blind derivation · 2026-10-31] #h(1fr) #counter(page).display()])
#align(center)[#text(size: 18pt, weight: "bold")[Last fall degree and finite degree profiles]]
#align(center)[Independent mathematical review · T-1107 · 2026-10-31]

*Derived result:* with finite $d_F$ and at least one strict fall,
$ d_F = max { d_f : f in (F), d_f > deg f }. $
An exact finite profile certifies its covered fall indices. Its largest observed fall needs a completion argument before it identifies the global value. All controls below are exact derivations over every field, rather than sampled measurements.

= Definitions and consequences
Write $I=(F)$ and $V_i=V_(F,i)$ for the smallest vector space in the task's definition. Indices are nonnegative integers. The zero polynomial lies in every such space and is treated separately from nonzero degree calculations.

The subspace $I inter R_(<=i)$ satisfies the defining containment and multiplication conditions, so $V_i subset.eq I inter R_(<=i)$. If $i<=j$, the space $V_j$ is admissible for the cap-$i$ definition; therefore $V_i subset.eq V_j$.

Every $h in I$ is a finite sum $sum_j a_j f_j$. A cap at least all $deg a_j + deg f_j$ admits every product and their sum. Hence each nonzero ideal element has a first membership index $d_h >= deg h$, and $h in V_i$ if and only if $d_h <= i$. This remains valid for an infinite generating set.

= Independent proof
Put $d=d_F$ and let $S$ be the nonempty set of first-membership indices of strict falls. For each strict fall $h$, the global property gives
$ d_h <= max(d, deg h). $
Since $deg h < d_h$, this implies $d_h<=d$. Thus $S$ is a nonempty bounded subset of the nonnegative integers and has a greatest element $M<=d$.

For an arbitrary nonzero $h in I$, a strict fall has $d_h<=M$, and a nonfall has $d_h<=deg h$. In either case $d_h<=max(M,deg h)$, so monotonicity implies $h in V_(max(M,deg h))$. Zero also belongs to this space. Thus $M$ satisfies the global defining property, and the minimality of $d$ gives $d<=M$. Therefore $d=M$.

*Attainment check.* A strict fall implies $d>=1$. Minimality of $d$ provides some $h in I$ outside $V_(max(d-1,deg h))$. The defining property at $d$ forces $deg h<=d-1$; otherwise the two caps would coincide. Hence $h in.not V_(d-1)$ and $h in V_d$. This supplies an actual fall with $d_h=d$, independently checking attainment.

#pagebreak()
= Exact finite-profile content
For $i>=1$, form
$ Q_i = (V_i inter R_(<=i-1)) / V_(i-1). $
Its denominator lies in its numerator. A nonzero quotient class is represented by a polynomial of degree below $i$ lying in $V_i$ but outside $V_(i-1)$. Consequently
$ Q_i != 0 <==> exists h in I: d_h=i > deg h. $
An exact profile through $B$ determines all fall indices at most $B$. If at least one occurs, their maximum $M_B$ satisfies $M_B<=d_F$. If none occurs, it certifies absence only in that covered range.

Let $pi_i$ take the homogeneous component of degree $i$. The required quotient dimension is
$ dim Q_i = dim V_i - rank(pi_i|_(V_i)) - dim V_(i-1). $
Thus total row rank alone is not the fall statistic. The top-degree projection, or equivalent intersection information, is needed. For example, $F={x}$ has $dim V_i=i$ for $i>=1$ and no strict falls at all.

== Required bridges for a measurement
+ Bind the exact input, field, variables, total-degree rule, and degree caps.
+ Prove the computed row space equals $V_i$, including multiplication of newly found lower-degree combinations within the same cap.
+ Justify exact rank, membership, and nonmembership over the specified field. Finding a polynomial at cap $i$ proves $d_h<=i$, rather than equality.
+ Compute the quotient statistic above, or give equivalent fall witnesses.
+ Prove the cutoff complete before identifying the observed maximum with $d_F$.

A known bound $d_F<=B$ combined with the exact profile through $B$ is sufficient under the nonempty-fall assumption. An independently verified invariant establishing the global property at $M_B$ is also sufficient. A stretch of degrees without observed falls supplies neither certificate by itself.

No actual measured matrix, execution trace, field instance, or cutoff certificate was supplied to this blind reviewer. The bridge for a particular existing measurement is therefore *inconclusive* in this task.

= Requested one-variable controls
For $D>=2$, let $F_D={x^D,x^D+x}$. The ideal is $(x)$. No generator is admitted below cap $D$. At cap $D$, subtraction produces $x$, and closure produces every $x^j$ through the cap. Hence
$ V_(F_D,i) = cases(0 & i<D, span_(k) (x,x^2,dots,x^i) & i>=D). $
Every nonzero $h in (x)$ has $d_h=max(D,deg h)$, and $d_(F_D)=D$. Replacing $D$ by $D+1$ gives $d_(F_(D+1))=D+1$. The two profiles agree through $D-1$ and first differ at $D$; claiming agreement through $D$ would be an indexing error.

#pagebreak()
= A visible early fall does not complete the profile
Fix $B>=2$ and $N>B$ in $k[x,y]$:
$ G_N={x^2,x^2+x,x^N,x^N+x}, $
$ H_N={x^2,x^2+x,y^N,y^N+y}. $
Both systems have four distinct generators with degrees $2,2,N,N$. Their exact spaces agree at every observed cap $i<=B$. Below cap 2 both spaces vanish. From cap 2 onward, $V_(G_N,i)=(x) inter R_(<=i)$. For $H_N$ this same formula holds at $2<=i<N$, while at $i>=N$ it becomes $(x,y) inter R_(<=i)$.

The shared difference $x$ first occurs at cap 2. The difference $y$ first occurs for $H_N$ at cap $N$, when its high-degree generators become admitted. Closure yields all monomials of the respective ideals through each cap. Thus
$ d_(G_N)=2, quad d_(H_N)=N. $
Both profiles have the same visible fall at 2, followed by no new fall through $B$. Nevertheless their global values differ. The gap can be arbitrarily large. Equal generator-degree multisets do not remove the ambiguity.

#image("profile-control.svg", width: 100%)
#text(size: 8pt)[Derived illustration: B = 4 and N = 6. The dimensions follow from the exact spaces: dim ((x) intersect R at cap i) = i(i+1)/2; dim ((x,y) intersect R at cap i) = (i+1)(i+2)/2 - 1. These are algebraic values, not experimental observations.]

== A fall above all generator degrees
Take $K={x^2,x y-1}$. At cap 2 its span has no nonzero polynomial of degree below 2. At cap 3,
$ y x^2 - x(x y-1)=x. $
Closure then gives $x y$, and subtraction of $x y-1$ gives 1. Thus $V_3=R_(<=3)$ and $V_i=R_(<=i)$ for larger caps. The constant 1 first occurs at 3, and $d_K=3$, exceeding the maximum generator degree 2. That degree alone is not a generally valid stopping bound.

#pagebreak()
= Controls on the matrix-to-space bridge
At cap $D$, one-pass bounded monomial multiples of the original generators of $F_D$ have row span
$ span_(k) (x^D,x^D+x)=span_(k) (x^D,x). $
For $D>=3$ this has dimension 2, while the true $V_D$ has dimension $D$. Multiplication of the newly obtained $x$ within the same cap supplies the missing powers. Thus this one-pass span is not generally the defined space.

Likewise, for $K$ at cap 3 the one-pass span has rows
$ x^2, x^3, x^2 y, x y-1, x^2 y-x, x y^2-y. $
It contains $x$ but not 1: its only row with a constant term also carries $x y$, which no other row can cancel. The actual $V_3$ contains 1 after the additional closure step.

The empty-fall boundary also matters. For $F={x}$, every nonzero ideal element satisfies $d_h=deg h$, and the global property holds at 0. The fall set is empty and has no greatest element. A convention that defines its maximum as zero is a different formulation.

= Verdicts and next obligation
#table(columns: (1fr, 24mm), inset: 6pt,
  table.header([Claim reviewed], [Verdict]),
  [Finite last fall degree plus a nonempty fall set implies the stated greatest-element equality.], [holds],
  [Exact spaces through B identify all fall indices at most B.], [holds],
  [An arbitrary finite profile's largest observed fall is the global value without a completion argument.], [breaks],
  [Maximum generator degree always supplies a valid cutoff.], [breaks],
  [One-pass bounded generator multiples always span the defined spaces.], [breaks],
  [A particular existing measured profile establishes the global value.], [inconclusive],
)

The next obligation for a measured result is exact space/rank evidence and a cutoff certificate for the same system. The coordinator can compare them against the explicit bridge conditions without changing the independent mathematical proof.

= Independence and provenance
Scientific input: only the supplied mathematical definitions and requested example families. No producer code, target YAML, research note, historical receipt, review plan, sibling report, memory file, or external mathematical source was read. General operational skills, repository AGENTS.md, Git metadata, and command help were consulted. The companion attestation enumerates these reads.

Archival parent: #text(size: 8pt)[2b0cfe1401831c9493cfe047a515955f38d037b8]. The plan content at that revision was not read. The isolated sparse worktree materializes only root AGENTS.md and this report directory. No Lean build, scientific experiment, statistical measurement, or canonical-graph inspection was performed. The full report and exact derivations are in report.md; the coordinator owns the final packet and any shared graph reconciliation.
