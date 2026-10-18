#set page(paper: "a4", margin: 13mm)
#set text(font: "Libertinus Serif", size: 9pt)
#set heading(numbering: "1.")

= Koblitz $m=2 dots 8$ high-arity correctness inputs

_2026-10-18. Planted chains and point-specialized direct polynomials; no natural solver or ECDLP cost result._

== Fixed inputs

The certified curve is $y^2 + x y = x^3 + x^2 + 1$ over `GF(2^73)` with a 62.224-bit prime subgroup. The eight predetermined base-point indices are `0,73,146,219,292,365,1,74` in the independently replayed 438-coordinate six-orbit base. Each $m$-term target is the full-point sum of the first $m$ selected points.

The characteristic-two equation is $S_3(x,y,z) = (x y + x z + y z)^2 + x y z + 1$. Every planted chain has $m-1$ checked equations. For the direct control, fix all $m$ base coordinates, enumerate the $2^m$ sign assignments, fold global point negation, and form the monic polynomial in target $x$ from the resulting $2^(m-1)$ roots. An independent Sage replay checks the full points, target sums, roots, coefficients, nonroot controls and the factorized recursive resultant at every arity.

== Exact specialization sizes

#table(columns: (auto, auto, auto, auto),
  [Summands], [Direct label], [Degree / nonzero terms], [Chain S₃ equations],
  [2], [S₃], [2 / 3], [1],
  [3], [S₄], [4 / 5], [2],
  [4], [S₅], [8 / 9], [3],
  [5], [S₆], [16 / 17], [4],
  [6], [S₇], [32 / 33], [5],
  [7], [S₈], [64 / 65], [6],
  [8], [S₉], [128 / 129], [7],
)

#image("../../docs/reports/2026-10-18-koblitz-high-arity-inputs.svg", width: 86%)

All coefficients of these univariate specializations are nonzero on the fixed points. Direct $S_8$ addresses seven summands plus target; eight summands require $S_9$ or a chain. The producer's construction wall was 0.379315 seconds after separate factor-base preparation. The first Sage replay attempt failed only at JSON serialization of a Sage integer and its partial bytes are retained; the corrected complete replay passed.

== Interpretation and next gate

Fixing every base coordinate makes these target-variable polynomials tractable. It does not construct full multivariate $S_8$ or $S_9$, measure solver degree, certify natural relations, or compare complete costs. The next frozen comparison requires same-size base controls, symbolic direct/chained formulations, planted and negative solver checks, then natural yield, distinct rank, linear algebra, unseen-target work, charged setup and matched rho. Unexecuted cells remain unavailable, and resource stops remain censored.

_Provenance:_ Full sources, exact bytes and failure scope are in `docs/reports/2026-10-18-koblitz-high-arity-inputs.md` and `research/icperf_koblitz_high_arity_20261018/`. This input screen changes no canonical attack-cost graph edge.
