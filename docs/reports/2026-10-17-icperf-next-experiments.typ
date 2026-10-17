#set page(width: 8.5in, height: 11in, margin: (x: 0.73in, y: 0.65in))
#set text(font: "Helvetica Neue", size: 8.5pt)
#set par(leading: 0.25em)

= Next factor-base experiment gates at subgroup order $2^50$–$2^63$

#text(size: 8pt)[Search record · 2026-10-17 UTC · source: 2026-10-17-icperf-next-experiments.md]

This round ranked prepared factor-base and solver interfaces for ordinary binary, prime, and Koblitz curves across $m=2 dots 8$. It used the frozen input and independent-replay records listed below. No scientific solver trial was run in this round; no end-to-end cost improvement follows from the prepared systems.

== Ranked gates

#table(
  columns: (0.5in, 1.0in, 2.22in, 2.85in),
  inset: 4pt,
  stroke: (bottom: 0.5pt + gray),
  [*Rank*], [*Family*], [*Prepared input*], [*Next discriminating gate*],
  [1], [Ordinary binary], [GF($2^61$), prime subgroup $r=576460752557211763$. Two 316-column k11 bases, four matched channels, separately planted satisfiable formulas.], [Frozen bounded CryptoMiniSat recovery of both controls, then a new common-target pilot with exact full-point checks.],
  [2], [Prime], [$p=9223372021248595841$, prime $r=9223372018953067627$. Three equal 475-point bases; 21 common-target systems for $m=2 dots 8$.], [Validate a genuine 63-bit polynomial backend against independent arithmetic and positive-root controls, then attempt matched capped systems.],
  [3], [Koblitz], [Certified prime subgroups at field degrees 71/73; the reviewed GF($2^53$) row targets a 45-bit subgroup.], [Construct a target-blind cofactor-aware orbit base and same-column control, then a frozen pilot on one full-width fixture.],
)

== Exact count ceiling for the fixed prepared bases

For $B$ projected columns and $m$ signed terms, $binom(2 B+m-1,m)$ counts signed multisets with repetition. The chart divides that count by the checked prime order $r$. Below one it bounds the representable fraction for uniformly sampled subgroup targets. Above one it is only a count ratio. It does not measure relation yield, point-sum collisions, algebraic regularity, or solver cost.

#image("2026-10-17-icperf-next-experiments.svg", width: 83%)

The fixed bases have count ratios below 0.016 through $m=7$ and above one at $m=8$. A complete $m=2 dots 8$ cost ladder needs arity-specific base sizes and must charge base construction, relation attempts, useful rank, linear algebra, target work, verification and matched rho. Short lower-arity panels on these particular bases cannot support a performance claim.

== Evidence boundary and next check

The ordinary-binary positive witnesses satisfy every serialized CNF and XOR constraint, but no solver has recovered them. The prime common targets have public known-answer scalars; they are correctness fixtures, not planted decompositions. At prime $m=8$, the coset direct input has 118 monomial occurrences versus 3910 and 3902 for equal-size controls; its quadratic lift has 103 variables and 104 equations. Those are input counts, not solving-degree or time observations. The Koblitz group fixtures are checked, but no complete full-width IC runner exists.

The immediate binary gate records solver and certificate viability under fixed caps; any modest base advantage requires a separate, powered target panel. The prime gate requires arithmetic-correct wide-field solving before timing. The Koblitz gate keeps field degree and prime subgroup order separate. The canonical ECDLP frontier graph was checked and needs no update because no reviewed full-cost result changed.

#text(size: 7.5pt)[Evidence: docs/reports/2026-10-16-elite-factor-base-baseline.md; 2026-10-17-binary-k11-planted-xcnf.md; 2026-10-17-prime-475-target-systems.md; 2026-10-17-koblitz-size-screen.md; problems/full-width-ic-arity-grid-unmeasured.md. Chart source: 2026-10-17-icperf-next-experiments-chart.py. Numerical provenance: internal input records and derived exact binomial counts.]
