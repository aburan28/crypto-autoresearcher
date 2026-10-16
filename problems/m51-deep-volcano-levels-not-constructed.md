# m=51 deep volcano inference and maps remain open

- **Status:** `open`
- **Kind:** control-gated inference, implementation, and proof gap
- **Affected work:** inferential comparison of all four conductor levels in
  the [deep rho study](../research/isogeny_volcano_m51_deep_rho_20261013/RESULTS.md)
  and any vertical-transfer comparison for this isogeny class
- **Next action owner:** unassigned executor for a fresh frozen replication
  and explicit map/dual construction
- **Last updated:** 2026-10-13

## Problem

Endpoint construction and a four-level execution are now complete. The frozen
[deep scan](../research/isogeny_volcano_m51_deep_scan_20261013/README.md)
exhausted 3.6 billion ranks, certified 42 bottom/parent orbit pairs, and fixed
the first 32 eligible pairs with zero admitted or blocking failures. The
separately frozen [deep rho run](../research/isogeny_volcano_m51_deep_rho_20261013/RESULTS.md)
completed 20,480 verified solves across all four levels.

The remaining empirical obstruction is inferential: the preregistered A/A
release gate failed narrowly on arms A and B, so all dependent nonzero, null,
equivalence, practical-significance, conductor-effect, and weakness labels are
withheld. The remaining transfer obstruction is operational: no explicit
point-evaluable adjacent map or dual has been serialized, and subgroup
preservation, scalar recovery, and complete transfer pricing remain open.

The fixed class is over
`F=GF(2)[z]/(z^51+z^6+z^3+z+1)` with trace `t=-38,684,515`, ambient order
`N=2,251,799,852,369,764`, prime subgroup order `r=17,192,986,687`, and

```text
Delta_pi = -7*(271*120,871)^2,
f_pi = 32,756,041 = 271*120,871.
```

The earlier accepted experiment constructed and measured only `f_E=1` and
`f_E=271`; that historical scope was superseded for endpoint construction and
descriptive measurement by the scan and run above. A fresh independent run is
still required for admissible inference. A vertical-transfer comparison
additionally requires executable maps, duals, subgroup preservation,
recovery, and complete cost accounting.

## Evidence and uncertainty

- **Observed, admitted endpoint sample:** the frozen
  [deep scan](../research/isogeny_volcano_m51_deep_scan_20261013/README.md)
  processed `[0,3,600,000,000)`, certified all 42 hits as distinct
  bottom/unique-ascent-parent pairs, and selected the first 32 at global rank
  `2,531,725,702`. Exact certificates identify parent `f_E=120,871`, bottom
  `f_E=32,756,041`, and a degree-271 ascending relation. This resolves the
  endpoint-sampling obstruction but supplies no evaluator or dual.
- **Observed, executed but inference withheld:** the frozen
  [four-level result](../research/isogeny_volcano_m51_deep_rho_20261013/RESULTS.md)
  has 20,480 verified solves and valid integrity seals. Its largest pairwise
  point difference is `0.026350` bit; `B-C=-0.000024` bit,
  `M120871=-0.006404` bit, and `2I=+0.039892` bit. These are diagnostics only.
  A's simultaneous 99% A/A interval missed the `-0.15` boundary by
  `0.003036` bit and B's missed `+0.15` by `0.009038` bit, so the frozen rule
  withholds every dependent inferential and equivalence label.
- **Observed:** the accepted [m=51 report](../research/isogeny_volcano_m51_rho_20261013/README.md)
  records 25,600 verified solves on the crater and 16 fixed representatives
  of the 272-model `f_E=271` slice. It explicitly states that the
  factor-120871 descent and bottom level were neither constructed nor
  measured. The sealed [archive](../research/isogeny_volcano_m51_rho_20261013/ARCHIVE.md)
  supports only that two-level scope.
- **Observed:** introducing revision
  `f0bdf9f739462766a9060532c59f9bfed69d00b1` contains the source
  `research/ecc2k130_conductor_isogenies_20261007/m51_m53/cm51_120871.gp`.
  It proposes constructing the degree-120,870 class polynomial, reducing and
  factoring it modulo 2, and writing `floor51_120871_cm.txt`. That revision
  contains the source but not the named output. Its `m5153.out` reports the
  structural values `h(-7*120871^2)=120870` and a kernel-field degree of
  `60,435` for the degree-120871 direction. These are planning facts, not a
  completed endpoint construction, map, or measured resource failure.
- **Observed feasibility pilot, not an admitted sample:** an old adapted
  point-count sieve scanned 10,000,000 sequential candidates in 38 seconds on one
  core and returned `b=675235026289400` in the fixed `a2=0` model family. A
  fresh PARI check gave the exact class order `N`; its Frobenius orbit is
  disjoint from the previously measured `f_E=271` orbit; and fresh PARI
  `[2,2,2]` witnesses at `271^2` prove that this candidate is on the bottom
  `f_E=271*120,871` level. Its unique 271-ascent parent is
  `b=7746411922983`, `a2=0`; that parent has Frobenius-orbit size 51 and exact
  order `N`. These observations establish construction feasibility for one
  pair. Because the pilot was not predeclared, its bottom orbit, its observed
  parent orbit, and every other bottom child resolving to that parent are
  excluded from the next statistical sample and support no rho comparison.
- **Derived or proved:** the arithmetic assessment in
  [`TRACE_ZERO_LANE.md`](../research/isogeny_volcano_m51_rho_20261013/TRACE_ZERO_LANE.md)
  derives that `tau^17` belongs to the orders of conductor 1 and 271 but not
  to the orders of conductor 120,871 or `271*120,871`. Thus negation is the
  currently specified native action common to all four levels. This does not
  predict a conductor-only collision-work effect.
- **Historical pre-freeze implementation evidence:** the pilot showed that a
  direct indexed sieve plus fresh conductor checks could find a deeper-level
  pair and motivated the now-completed frozen scan. It did not enter the
  admitted sample. The degree-120,870 CM inventory remains an independent
  census cross-check, not a prerequisite for the completed endpoint sample.
- **Missing capability:** a fresh, replayable, outcome-independent endpoint
  sample plus a separately frozen rho run whose preregistered control gate
  passes; a justified population model for inference beyond the finite
  selected set; and serialized or
  deterministically reconstructible adjacent maps and duals with point
  evaluation, exceptional-input handling, subgroup checks, recovery, and
  measured costs. A certified unique-ascent relation is not an explicit
  point-evaluable map or dual.
- **What this evidence does not establish:** it establishes neither a
  conductor effect nor conductor independence. The failed control gate is an
  instrument alert, not evidence for or against weakness. The completed run
  also does not establish an executable transfer, an end-to-end advantage,
  NIST-scale behavior, a security-bit discount, or a weak curve.

## What would unblock it

- [x] Preserve and independently replay the pilot pair, including the exact
  field encoding, both curve identities, order checks, bottom-conductor
  `[2,2,2]` witnesses at `271^2`, unique-ascent classification, commands,
  software versions, hashes, and failures. The observed pair is feasibility
  evidence only and remains excluded from the admitted sample.
- [x] Execute a precommitted indexed scan over `[0, 3,600,000,000)` and select
  the first 32 distinct bottom/parent Frobenius-orbit pairs under the frozen
  encounter-order and deduplication rules. Require exact order `N` and fresh
  conductor certificates for both members of every selected pair; exclude
  the pilot parent orbit and its complete 272-child bottom fiber before
  selection.
- [ ] Before a level-wide statistical claim, define the finite population of
  Frobenius orbits at each new level or freeze a deterministic orbit-sampling
  rule and its estimand. Select models before any rho outcome is observed;
  conjugate models are strata, not independent replicas.
- [ ] Before a vertical-transfer claim, provide an executable degree-120871
  map `phi:E_1 -> E_120871` and degree-271 map
  `psi:E_120871 -> E_bottom`, with their duals. A kernel-polynomial or other
  compressed representation is acceptable only if it deterministically
  evaluates the exact maps over `F`. Verify the fields and directions,
  exceptional loci, both identities
  `dual(phi) o phi=[120871]` and `dual(psi) o psi=[271]`, and the reverse
  compositions on the codomains. On the order-`r` subgroups, verify nonzero
  images of exact order `r`, preservation of planted scalars, recovery using
  the inverse degree modulo `r`, and verification back on the source.
- [x] Freeze and execute a matched four-level native negation-rho experiment
  using identical planted scalars and paired random-stream namespaces, with
  native setup and online `walk_ops` retained separately. The completed run
  executed no isogeny transfer and priced neither transfer nor scalar-
  recovery/verification work as an end-to-end attack.
- [ ] After explicit maps exist, separately charge path construction, map-in,
  destination attack, scalar recovery, verification, field primitives,
  memory, failures, and cold-start versus genuinely amortized work. Compare
  against the existing crater native-`tau` control as a separate
  action/transfer baseline; do not mix its symmetry discount into the
  same-action level contrast.
- [ ] Freeze and execute a genuinely independent replication using a new PRP
  endpoint domain, fresh setup/target/walk roots, fixed sample size, and the
  same predeclared all-arm A/A release rule. Exclude all 42 parent orbits
  found in the completed scan, their bottom-child fibers, and the earlier
  feasibility-pilot fiber before selecting the fresh sample. Pilot-based
  planning makes 128
  parent clusters (81,920 solves) a provisional fixed-N target under the
  assumptions in [the sizing note](../research/isogeny_volcano_m51_deep_rho_20261013/REPLICATION_SIZING.md).
  Do not reuse this run's outcomes to select endpoints or repeat until the
  gate passes.

The completed conditions admit the frozen finite-selected-set descriptions,
not their withheld inferential labels. The fresh replication is required for
a new inferential attempt. The population condition is additionally required
for inference beyond its selected endpoints, and the map condition is required
for transfer or source-weakness claims. Even all conditions would establish
only their scoped proxy measurements and certified paths, not a NIST-scale
result or a weak curve without a separately predeclared and met end-to-end
advantage criterion.

## Next discriminating step

- **Action or proof obligation:** freeze a new endpoint scan in a disjoint PRP
  domain and a fixed 128-cluster four-level same-negation experiment before
  observing any new rho outcome. Treat the completed run only as a sizing
  pilot; it can never gain labels retroactively.
- **Inputs and controls:** retain the exact field, `N`, `r`, conductor lattice,
  endpoint classifier, and one-child-per-parent cluster definition. Freeze
  new endpoint-selection and exclusion rules, setup/target/walk roots, the
  calibrated estimators, nine-contrast multiplicity family, disjoint A/A
  samples, simultaneous 99% `+/-0.15`-bit all-arm gate, and no-backfill/no-
  optional-stopping rule. Use one common native signed-negation action at all
  four levels for this association lane. Exclude all 42 previously discovered
  parent orbits and their bottom-child fibers, plus the feasibility-pilot
  fiber. Keep each level's best certified native action as a separate attack-
  ledger comparison.
- **Execution limits and stop condition:** process the complete new scan range
  even if 128 pairs appear early, then execute exactly the frozen 81,920-solve
  design. A material certification failure at or before the selected cutoff
  invalidates selection and is not backfilled. A failed A/A gate retains the
  run but again withholds every dependent inferential and equivalence label;
  it never triggers repeat-until-pass execution. If the complete frozen scan
  range yields fewer than 128 eligible clusters, preserve it as a bounded
  census, do not backfill or launch the 128-cluster rho design, and freeze a
  separate extension before continuing.
- **Outcomes and next actions:** a passing control gate releases only the new
  run's predeclared inference. A failed or non-estimable gate leaves that lane
  indeterminate. In parallel, a certified explicit map/dual permits a separate
  transfer-cost study; endpoint relations alone do not.
- **Independent census lane:** replay the exact `cm51_120871.gp` construction
  from revision `f0bdf9f739462766a9060532c59f9bfed69d00b1` in a pinned
  PARI/GP environment and retain every intermediate needed to validate its
  intended 120,870-entry `floor51_120871_cm.txt`. This remains valuable for a
  complete CM census and cross-check, but it does not block the already
  completed indexed endpoint sample.
- **Recheck trigger:** a committed fresh replication, the completed independent
  CM census, or a committed explicit map/dual artifact for either missing
  direction.

A planned construction is not a completed experiment. It must use the
repository's execution, review, visual-record, and archival rules before its
outputs support an inference.

## Resolution and history

Unresolved. On 2026-10-13 the frozen deep scan resolved admitted endpoint
sampling for 32 pairs and the frozen rho run completed the documented
four-level measurement in this repository. Its A/A gate failed narrowly, so
inferential labels remain withheld. Explicit maps/duals and transfer costs
also remain open. The record asserts no general conductor effect, conductor
independence, impossibility, or weakness result.
