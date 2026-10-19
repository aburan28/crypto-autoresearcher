#set page(paper: "a4", margin: 17mm)
#set text(size: 9pt)
#set heading(numbering: none)

= Binary-field multiplicative-divisor eligibility

*Derived field screen, 2026-10-17 UTC.* Exact factorizations of $2^n - 1$ were
checked at $n=50,53,63$. The chart shows the nearest multiplicative divisor to
twice the nominal default factor-base size across $m=2 dots 8$. This constructs
no binary curve or base and measures no index-calculus cost.

#image("2026-10-17-icperf-binary-divisor-fit.svg", width: 100%)

#table(
  columns: (1fr, 2fr), inset: 5pt,
  [Field], [Cells with divisor within 15% of $2B$],
  [GF(2^50)], [m=2,3,4,6,8],
  [GF(2^53)], [None of m=2…8],
  [GF(2^63)], [m=3,4,6,8],
)

For $n=63, m=8$, the nominal $B$ is 406, the closest divisor is 889,
and the integer gap is $77/812 = 9.48%$. For $n=53$, the field has only
eight divisors and none fits. The default-size changes over the full Hasse
interval are at most one and leave all 21 classifications unchanged.

== Remaining measurement

A concrete certified ordinary-binary or Koblitz curve, actual target subgroup,
point lifts, realized base, matched controls and all collection, sparse-solve
and target costs are needed. The prime-field constructor cannot be used for
binary-field arithmetic. Koblitz signed-Frobenius bases are a distinct path.
The canonical ECDLP frontier graph remains unchanged because this screen adds
no reviewed cost comparison.

Machine-readable data: research/icperf_binary_divisor_20261017/field_fit.json
(SHA-256 a5d2387e5cebdf34c3a66e766ab14e7d43878c24998132eb32c2d19aa6b8c6b9).
