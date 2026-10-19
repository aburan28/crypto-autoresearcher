# Prospective 2,304-edge prime-field isogeny scan

**Status:** design draft, not a frozen `EXP-*` contract or execution authorization.
**Owner of formal approval:** Coordinator. **Study unit:** a certified curve
isomorphism class, not a Weierstrass equation chosen after inspecting yield.
The existing 20-arm conductor-gap experiment remains a separate frozen study.

## Question and scope

Within fixed prime-order isogeny classes, how much do three-summand useful
relation yield, useful rank growth, and complete same-point ECDLP cost vary
with the curve and a fixed factor-base rule? Can a base that performs well on
one curve perform poorly on another? The search is finite and deliberately
selected. It estimates variation on the specified walks, not a law for all
elliptic curves or all isogeny classes.

Use the already certified floor sources from `EXP-ECTD-0cf008`:

| stratum | field `p` | prime group order `r` | source `(a,b,Gx,Gy)` | `(D_K,f_pi,f_E)` | directed degree-7 edges |
| --- | ---: | ---: | --- | --- | ---: |
| P29 | 320092037 | 320091991 | `(101186781,57596093,0,112219098)` | `(-19,8209,8209)` | 2048 |
| P37 | 81640512137 | 81640511861 | `(6064550680,68678790390,2,25752399999)` | `(-19,131101,131101)` | 256 |

PARI `quadclassunit` gives cyclic floor class groups of orders 8,208 and
131,100. The ideal class of a prime above 7 has respective orders 2,736 and
131,100 (`class_group.gp`). Thus each proposed nonbacktracking prefix can
contain distinct vertices. This arithmetic predicts a possible walk; it does
not certify the individual edges. The degree-7 prime is coprime to both
conductors and both subgroup orders. Preserve the P29/P37 split throughout.

## Graph and curve identities

At each source obtain the two rational degree-7 neighbors. Choose the
neighbor with the smaller integer `j` as step 1; subsequently choose the
neighbor that does not return to the previous `j`. Abort on an unexpected
neighbor count, repeated `j`, field/order mismatch, or missing map/dual.
Include the initial vertex, giving 2,049 P29 and 257 P37 vertices. Save every
kernel polynomial, codomain, map, dual, `j`, `(D_K,f_pi,f_E)`, source/codomain
group order, and path index. Verify each edge's modular-polynomial equation
independently and verify `dual(phi)(phi(P))=[7]P` on the transported generator
and target. Spot checks alone do not certify the full walk.

For comparable native bases, use a deterministic model for every `j`, including
the source. For `j` neither 0 nor 1728, let `A=3j/(1728-j)` and
`B0=2j/(1728-j)` in `F_p`; select this model if its order is `r`, otherwise
select its quadratic twist `(d^2 A,d^3 B0)`, where `d` is the least integer
at least 2 that is a nonsquare modulo `p`. Verify the order exactly and save
the isomorphism from the walk's codomain. Abort and amend if `j=0` or `1728`
occurs; no exceptional-model rule is silently inserted. Evaluate the map
followed by that isomorphism, and carry the same source `P,Q` through the
entire walk. Curve IDs use `tools/curve_identity.py`; path, base, and run IDs
are separate. The original floor equations remain the DLP input source.

## Factor bases and target streams

At every canonical vertex use exactly `B=256` x-orbits on P29 and `B=1600`
on P37, with both signs of each point. Four prespecified rules:

1. `low_x`: first `B` liftable x-values in ascending order.
2. `mid_x`: first `B` liftable x-values in cyclic order starting at
   `floor(p/2)`.
3. `random_x`: `B` distinct liftable x-values drawn uniformly by rejection
   sampling with a vertex-domain-separated seed.
4. `power_x`: inspect `g^0,g^1,...` for the least primitive root `g` of
   `F_p^*`, taking the first `B` liftable x-values. Run on every eighth P29
   vertex and every fourth P37 vertex, selected by path index before yield.

All bases store their ordered point lists and digests. The first three rules
run on every vertex. On prespecified check vertices, also transport the
source's `low_x` base along the exact map chain; the targetwise decomposition
counts must agree exactly with source counts. Independently rebuild `low_x`
on an isomorphic `u=2` model for coordinate sensitivity. A difference between
native bases can be a coordinate effect, so report it as such.

After code and graph manifests are frozen, commit hashes of independent
256-bit graph, base, discovery-target, confirmation-target, solve-target, and
verifier roots. The collector receives public points and `(a_i,b_i,R_i)` but
not planted logarithms. Use the same accepted coefficient sequence at all
vertices: `R_i=[a_i]P+[b_i]Q`, with `a_i` uniform in `F_r`, `b_i` uniform in
`1..r-1`, and `R_i` distinct and nonidentity. The map chain makes these
same-point target vectors across curves. Domains and rejection rules are
versioned and recorded. Do not reuse discovery targets in confirmation or
ECDLP timing. Reveal planted scalars only after outputs are sealed.

## Fixed stages

| stage | P29 | P37 | purpose |
| --- | ---: | ---: | --- |
| Graph | 2,048 edges | 256 edges | certify paths, maps, duals, identities |
| Discovery | 8,192 targets per vertex/base | 2,048 targets per vertex/base | rank candidates; first three bases everywhere |
| Structured-base check | every 8th vertex | every 4th vertex | `power_x` and transported controls |
| Confirmation | 32,768 fresh targets per selected vertex/base | 32,768 fresh targets per selected vertex/base | independent estimates |
| Same-point solve | 5 cold starts and 16 warm targets per finalist | same, subject to exact solver gate | full cost and rho comparison |

At discovery, select the top and bottom eight P29 vertices and top and bottom
four P37 vertices **for each of the three main bases** by useful nonempty
target fraction; tie by smaller `j`. Take their union, the source, and 16 P29
or eight P37 control vertices selected by a precommitted uniform-index draw
that is independent of yield. Thus at most 65 P29 and 33 P37 vertices enter
confirmation. Do not substitute a failed candidate or increase the quota
after seeing effects. Report discovery min/max over the sampled vertices as
descriptive; the confirmed extrema are only extrema of the selected set.

At each target, retain raw ordered/unordered triple counts, useful triples
(three distinct IDs, no opposite pair, nonzero row), exact nonempty indicator,
duplicate rows, rank increment over `F_r`, and timings for base construction,
pair table, target probe, verification, deduplication, and rank. Eliminate a
known-generator base logarithm; merge the Q column if Q is itself a base
point. Recompute point sums and modular rank independently. Rank prefixes are
512, 2,048, 8,192, and 32,768 where present. The raw all-target ordered mean
`|F|^3/r` is an identity, not a relation-success probability.

For final ECDLP trials, choose deterministically from confirmed data: source,
best and worst `low_x` yield, best and worst confirmed `low_x/random_x`
ratio, and the median `low_x` vertex, deduplicating by `j` (at most six per
stratum). Use the exact same source point `P` and unseen source target `Q`
mapped to each finalist. The executable pair-table decomposition, relation
collection, modular linear algebra, target-log extraction, and independent
`[k]P=Q` replay all run to completion. Continue in fixed target batches until
the first verified scalar or 262,144 attempted targets on P29 and 524,288 on
P37. A censored solve remains censored. A planted fixture checks correctness
but never enters an ECDLP time estimate.

Measure separately: (i) native time from already-present `P_j,Q_j`, (ii) cold
source-to-destination time including graph construction, selection, route,
map preparation, two point transports, base/table setup, relations, rank,
recovery and verification, and (iii) amortized per-target time for 16 targets
sharing only genuinely reusable setup. Report CPU time, wall, group/field
operation counts, peak RSS, failed attempts and route degree sequence. Pair
each unseen target with source and destination rho, on the same device, in
shuffled order with A/A controls. Charge rho setup and verification too. The
minimum and maximum reported ECDLP times are over the **completed finalist
set**, with uncertainty and censoring visible; no untested curve is assigned
a solve time. Any speed/advantage claim needs `claims/*.json` passing
`tools.progress_fidelity validate`.

## Inference, resource protection, and decisions

The curve is the unit for class variation; targets are paired within and
across vertices through exact maps. Discovery only nominates candidates.
Confirmation uses fresh targets and simultaneous 99% bounds for all selected
curve/base fractions, with selection counts fixed above. Use exact
hypergeometric inversion per fraction and a Bonferroni family correction;
form conservative ratio bounds. Report the paired targetwise difference as a
secondary analysis and the curve-by-base interaction, including the random
base null and coordinate control. A confirmed lead requires a ratio interval
excluding one and at least a 20% point-ratio shift; an interval containing
one does not establish equivalence. Do not infer conductor causality from
within-floor variation. Repeat the report separately for P29 and P37.

Before any performance claim, distinguish mathematical occupancy, rank yield,
solver execution, native DLP cost, and full transfer cost. A relation lead
without verified scalar recovery is not a completed DLP cost result. A cold
source-to-destination advantage needs a paired interval below one against
source rho after all search and transport costs. An amortized advantage must
state the exact number of targets sharing setup. Do not fit an exponent from
these two selected field sizes.

Use one active relation worker, a 4 GiB RSS guard for P29, an 8 GiB guard for
P37, and a process watchdog of 1,800 seconds per discovery arm and 7,200
seconds per confirmation/solve batch. These protect the machine, not the
scientific sample count. Failure, timeout, and invalid map/row checks are
retained with raw logs, never scored as zero yield. Graph and runtime preflight
are required before freezing an `EXP-*` runner. Archive source/binary hashes,
maps and duals, seed commitments/reveals, raw per-target rows, all failed
attempts, resource receipts, certificates, report, graph, and inspected PDF.

The Coordinator must turn this draft into a runnable versioned contract,
approve it under the standing authorization, and publish a handoff before
`run` launches scientific targets. The existing Coordinator backend is
currently unavailable (`problems/prime-field-arity3-relation-oracle.md`).
If graph generation, exact map evaluation, or the full target solver cannot
meet its stated checks, record that specific obstruction before any inference.

## Sources

- `EXP-ECTD-0cf008/specification.yaml` and its sealed run receipts (`internal`):
  fixed curve inputs, base/target semantics, first measured runtime scale.
- `class_group.gp` and `probe_degree7.py` (`internal`): planning arithmetic
  and bounded map feasibility only.
- [Sutherland, *Isogeny volcanoes*](https://arxiv.org/abs/1208.5370)
  (`retrieved`): ordinary isogeny graph structure.
- [Sage isogeny reference](https://doc.sagemath.org/html/en/reference/arithmetic_curves/sage/schemes/elliptic_curves/ell_curve_isogeny.html)
  (`retrieved`): map, dual and kernel interfaces.
- [PARI/GP documentation](https://pari.math.u-bordeaux.fr/doc.html)
  (`retrieved`): class group and binary quadratic form functions.
