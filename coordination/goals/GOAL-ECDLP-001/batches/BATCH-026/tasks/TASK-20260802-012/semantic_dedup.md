# TASK-20260802-012 semantic deduplication

## Disposition

`ZERO_SURVIVORS` after five pre-ID object screens. This is not closure of
`GOAL-ECDLP-001`, `RQ-ECDLP-002`, generic ordinary prime-field ECDLP, or the
space of tracked objects. It means only that none of the five exact objects in
`idea_cohort.yaml` crosses the mechanism-new, lossy-compatible,
source-invertible, and fully charged exponent gate.

No canonical `ECDLP-IDEA-*` id was allocated. No experiment, solver, relation
campaign, factor-log solve, descent, or scalar recovery ran.

## Corpus receipt and count reconciliation

The current worktree contains 1,105 substantive files under `ideas/`, 922 under
`ledger/`, and 7,766 under `knowledge/`, excluding AppleDouble `._*` files. The
complete `ideas/` content-hash stream has SHA-256
`ffd3789d4fdaf675587350124fca460b3a42877cbe9dea39b0395fcf80cec041`.

The canonical idea corpus is gap-free `ECDLP-IDEA-001` through
`ECDLP-IDEA-410`: 17 active, 27 deferred, and 366 rejected. The active registry
has 17 rows. Strings `ECDLP-IDEA-411` through `ECDLP-IDEA-433` occur only in
rejected preallocation material; they are not canonical allocations. Treating
those strings as entries would repeat the precise pre-ID allocation error that
the corpus reviews prohibit.

The handoff names a root `research_ledger.md`, but that path is absent in this
committed worktree. I did not pretend otherwise. The scan covered the current
structured `ledger/` tree and all eight preserved input-ledger snapshots:
`autolab_research_ledger.md`, `ecdlp_ic_research_ledger.md`,
`main_research_ledger.md`, `research_ledger_main.md`,
`index_calculus_ledger.md`, `index_calculus_research_ledger.md`,
`research_ledger_ic.md`, and `research_ledger_ic_state.md`.

The operation-level frontier is consistent across the canonical ideas, the
P1552 mechanism review, later zero-survivor reviews, the current claim matrix,
and the structured ledger:

| Occupied family | Object actually tracked | Operation | Persistent obstruction |
|---|---|---|---|
| Generic collision/orbit | affine scalar labels attached to a random walk | group addition and collision | Shoup `Omega(sqrt(N))` inside the generic model |
| Relation decomposition | factor-base source tuples or their endpoint aggregate | summation, elimination, source unranking | density, source output, rank, factor logs, and descent must all be charged |
| Scalar/orientation return | character, period, cover sheet, torsion orientation | lift, separate, return | return requires an order-`N` dictionary/DLP or rho-scale orbit work |
| Source-preserving transform | source-labelled tensor, module, exterior row, path, or circuit | transform/contraction | removing labels leaves an aggregate; retaining them pays the source deck |
| Cover/correspondence transfer | point or relation image on another curve/variety | homomorphic transport and pullback | fixed degree is faithful/constant-factor; growing state and return restore cost |
| Public augmented invariant | jet, net, spectrum, incidence, or public predicate | deterministic public evaluation/update | simulator-visible unless a concrete non-generic structure and its density are proved |

This table is a partial mapping toward `KN-OPEN-019`, not the missing closed
taxonomy.

## Primary-literature boundary

Nearby primary sources were checked rather than relying on name matches:

- Victor Shoup, *Lower Bounds for Discrete Logarithms and Related Problems*
  (EUROCRYPT 1997), from the [author's publication page](https://www.shoup.net/papers/):
  generic discrete log retains the square-root barrier.
- Henry Corrigan-Gibbs, Alexandra Henzinger, and David J. Wu,
  [*The Structured Generic-Group Model*](https://people.eecs.berkeley.edu/~henrycg/pubs/structured-generic-groups/)
  (EUROCRYPT 2026 / ePrint 2026/384): structure occupying a `delta` fraction is
  controlled by `Omega(min(sqrt(N),1/delta))` in their model, with applications
  stated for elliptic-curve-point structure. This is a model boundary, not a
  universal impossibility theorem.
- Amadori, Pintore, and Sala,
  [*On the discrete logarithm problem for prime-field elliptic curves*](https://eprint.iacr.org/2017/609):
  the prime-field summation-polynomial/Groebner route is established prior art;
  a solver reduction is not a complete sub-rho attack by itself.
- Claus Diem,
  [*On the discrete logarithm problem in elliptic curves*](https://doi.org/10.1112/S0010437X10005075),
  and Pierrick Gaudry,
  [*Index calculus for abelian varieties of small dimension and the elliptic curve discrete logarithm problem*](https://doi.org/10.1016/j.jsc.2008.08.005):
  the subexponential results concern extension-field/small-dimension regimes and
  do not supply a generic ordinary prime-field exponent improvement.

No source found establishes one of the five screened mechanisms as a generic
ordinary prime-field sub-rho attack. That absence does not prove novelty; each
candidate already fails an internal semantic or cost gate.

## Candidate-by-candidate semantic test

| Handle | Proposed object and operation | Nearest occupied mechanisms | Dedup/falsification verdict |
|---|---|---|---|
| `B21-P01` | Binary low-degree-divisor membership word along `X -> X+P`; update by shift plus one evaluation | IDEA-011 orbit/period, IDEA-329 delay observer, IDEA-374 inversion index, KN-LIT-7606 | A short word has average fibre at least `N/2^(sw)`; an isolating scalar-labelled dictionary constructs the missing inverse at rho-or-worse cost. |
| `B21-P02` | Unordered Kummer neighbourhood deck; x-only differential update | IDEA-010 deck descent, IDEA-057 Kummer router, IDEA-158 nonfaithful x-only lift | Discarding order makes deletion/insertion ambiguous; restoring it returns an orbit window. Sign quotient is constant-factor only. |
| `B21-P03` | Truncated Hasse-jet principal part; pullback under translation | IDEA-004 jets, IDEA-068 marked Hasse forms, IDEA-160 ramification digits, EV-JET-001 | Endpoint jets are public deterministic functions; source jets require occurrence leaves/labels. Random degree-matched function is the mandatory same-shape null. |
| `B21-P04` | Factor-base membership signatures across bounded-degree isogenies; componentwise homomorphic transport | IDEA-002 split projection, IDEA-057 isogeny routing, ISO-CW-NR-001, KN-FIND-007 | Isogenies are injective faithful re-encodings on the prime subgroup; no union-density or independent-rank gain survives equal-total-base accounting. |
| `B21-P05` | Rank/sketch of the exact six-list `2+2+2` Abel-Jacobi exterior tensor; contraction | IDEA-050/052/056, prior tensor candidate C2, P1539/P1506/P1552 | This is the occupied exterior/tensor frontier. Exactness restores full separator/source state; truncation is lossy without the missing rank and recall theorem. |

Renaming the representation does not change these information flows. In every
row, the cheapest adversarial mutation freezes the public object/transcript and
changes the hidden source fibre or scalar position. If output does not change,
the object has no source inverse. If source labels/backpointers are added until
output does change, their construction is charged and the object merges with an
occupied family.

## Same-shape controls and quantitative boundary

Every future successor must compare against both matched rho/BSGS and a null of
the same shape:

| Real object | Required null |
|---|---|
| Divisor membership word | random prime cyclic encoding with identically distributed public predicate bits |
| Kummer deck | random encoding paired by a public involution with same-size random neighbourhood multisets |
| Hasse jets | random rational function with matched degree, poles, multiplicities, charts, and identical jet code |
| Isogeny ensemble | random-permutation transports preserving marginal hit counts, map count, and total factor-base size |
| Exterior tensor sketch | random six-list tensor preserving dimensions, deck sizes, marginal degrees, and pair-collision counts |

The candidate claim must be evaluated end to end:

`public setup + object construction + failed attempts + success amplification + exact source output + duplicate-normalized independent relation rank + factor-base logs + blind masked-target descent + output verification + peak memory/data/communication`.

Pollard rho remains time exponent `0.50` with negligible memory; BSGS remains
time and memory exponent `0.50`. The stricter occupied P1552 campaign rectangle
requires complete `lambda,mu <= 0.45`, including setup/state
`B^(9/4+o(1))`, fresh target work `B^(5/4+o(1))`, and `B=N^(1/5)` verified
independent relations. None of the five candidates instantiates those costs.
The supported SOTA delta is therefore exactly zero on time, memory, and
data/query axes.

## Named closures and forward guidance

These are scoped closures, each with an argument and a redirection:

1. **Orbit-word/deck closure.** A short secret-independent orbit projection has
   large fibres; a source-invertible one needs the scalar-index dictionary or
   search it was meant to replace. This closes these two window/deck objects,
   not all nonhomomorphic public predicates. Redirect to predicates with a
   proved encoding-specific propagation theorem and a charged source-free
   inverse.
2. **Bounded endpoint-jet closure.** Public endpoint jets are simulator-visible;
   source-marked jets import occurrence leaves. This closes bounded public
   principal-part filters, not every arithmetic differential construction.
   Redirect to a concrete point statistic with exploitable fraction
   `delta>N^-1/2` and a proved non-simulable use.
3. **Bounded isogeny-ensemble closure.** Faithful homomorphic transports and
   equal-total factor bases do not create new rank. This closes chart
   multiplication at bounded degree, not all correspondences. Redirect to a
   non-permutation correspondence with a source-valid rank theorem after full
   map and descent costs.
4. **Current exterior-sketch closure.** Exact contraction retains the full
   separator/source state; approximate truncation loses completeness. This
   closes format/sketch swaps of the current six-list tensor, not a future rank
   theorem. Redirect only if an exact real-vs-null separator-rank exponent gap
   and biconditional source contraction are proved.

The highest-value next action is mathematical ingredient scouting: a new
correspondence, exact rank bound, or source-free inverse theorem. Further
BATCH-020 threshold/instrument repair, longer orbit windows, higher jet order,
more bounded-degree charts, or a different tensor format does not dominate
that search on expected information gain.

## Pareto accounting

`dominated_by: n/a (no result claimed)`. Each screened object is dominated on
demonstrated performance by Pollard rho or by its direct matched subtask
baseline. Quantitative `sota_delta`: supported generic-ECDLP time-exponent
improvement `0.00`; memory-exponent improvement `0.00`; data/query improvement
`0`; cryptographic security bits reduced `0`.

