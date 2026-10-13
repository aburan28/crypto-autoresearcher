# m=51 deep volcano sampling and maps remain open

- **Status:** `open`
- **Kind:** admitted-sampling, implementation, and proof gap
- **Affected work:** the unmeasured `f_E=120,871` and
  `f_E=271*120,871` levels in the [m=51 volcano study](../research/isogeny_volcano_m51_rho_20261013/README.md), its [frozen protocol](../research/isogeny_volcano_m51_rho_20261013/PROTOCOL.md), and any complete-level or vertical-transfer comparison for that isogeny class
- **Next action owner:** unassigned executor after the indexed-scan protocol is frozen
- **Last updated:** 2026-10-13

## Problem

An unpredeclared feasibility pilot has now found one bottom/parent pair in the
two deeper levels of the ordinary `m=51` binary isogeny class. That removes the
earlier endpoint-existence bottleneck for this one observed pair, but it does
not admit the pair as a statistical sample: the search, selection rule, and
stopping boundary were not frozen before the pair was observed. No frozen
level-wide sampling frame has been executed, and no explicit adjacent
map/dual certificate reaches either level.

The fixed class is over
`F=GF(2)[z]/(z^51+z^6+z^3+z+1)` with trace `t=-38,684,515`, ambient order
`N=2,251,799,852,369,764`, prime subgroup order `r=17,192,986,687`, and

```text
Delta_pi = -7*(271*120,871)^2,
f_pi = 32,756,041 = 271*120,871.
```

The accepted experiment constructed and measured only `f_E=1` and
`f_E=271`. A same-action comparison at every conductor level still requires
valid models for `f_E=120,871` and `f_E=f_pi` selected by a frozen rule before
rho outcomes are observed. A vertical-transfer comparison additionally
requires executable maps, duals, subgroup preservation, recovery, and
complete cost accounting.

## Evidence and uncertainty

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
- **Updated implementation evidence:** the pilot shows that a direct indexed
  sieve plus fresh conductor checks can find at least one deeper-level pair
  cheaply enough to justify a frozen scan. It does not measure the full
  population, certify a sampling estimand, or show that the same throughput
  persists over the next range. The degree-120,870 CM inventory remains an
  independent census route rather than the fastest currently evidenced route
  to a precommitted endpoint sample.
- **Missing capability:** a frozen, replayable multi-orbit sample for both
  deeper levels; a fixed Frobenius-orbit sampling frame for level-wide
  inference; and serialized or deterministically reconstructible adjacent
  maps and duals with point evaluation, exceptional-input handling, subgroup
  checks, recovery, and measured costs. The pilot's unique ascent relation is
  not an explicit point-evaluable map or dual.
- **What this evidence does not establish:** it does not show that either
  deeper level is empty, unreachable, infeasible to construct, weak, or as
  hard as the measured levels. It does not establish a conductor effect or
  conductor independence. The completed `f_E=271` result cannot be
  extrapolated across the unmeasured factor-120871 gap or to the bottom.

## What would unblock it

- [ ] Preserve and independently replay the pilot pair, including the exact
  field encoding, both curve identities, order checks, bottom-conductor
  `[2,2,2]` witnesses at `271^2`, unique-ascent classification, commands,
  software versions, hashes, and failures. The observed pair is feasibility
  evidence only and remains excluded from the admitted sample.
- [ ] Execute a precommitted indexed scan over `[0, 3,600,000,000)` and select
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
- [ ] Freeze and execute a matched four-level negation-rho experiment using
  identical planted scalars and paired random-stream namespaces, separately
  charging construction, map-in, walk, recovery, verification, field
  primitives, memory, failures, and cold-start versus genuinely amortized
  work. Compare against the existing crater native-`tau` control as a
  separate action/transfer baseline; do not mix its symmetry discount into
  the same-action level contrast.

The first condition is sufficient to admit a model-level measurement on the
two missing levels. The second is additionally required for a level-wide
inference. The third is required for transfer or source-weakness claims. Even
all four conditions would establish only the frozen proxy measurements and
certified paths, not a NIST-scale result or a weak curve without a separately
predeclared and met end-to-end advantage criterion.

## Next discriminating step

- **Action or proof obligation:** freeze and run a deterministic indexed sieve
  over `[0, 3,600,000,000)`, selecting the first 32 distinct certified
  bottom/unique-ascent-parent Frobenius-orbit pairs under an encounter-order
  tie rule. Exclude the complete parent orbit represented by
  `b=7746411922983` and all 272 bottom-child orbits that ascend to it because
  the pilot exposed that fiber before freeze; this includes the observed
  bottom orbit containing `b=675235026289400`. Do not choose or reject
  endpoints from rho outcomes. This
  supersedes CM-first construction as the fastest currently evidenced next
  endpoint-sampling step.
- **Inputs and controls:** use the fixed field polynomial, `N`, `r`, and
  conductor factorization above. Freeze the index-to-candidate mapping,
  encounter order, orbit canonicalization, deduplication, pilot-exclusion,
  exact-order, and conductor-certificate rules before scanning. Pass the known
  crater `b=1`, `m51-floor-o01`, and the excluded pilot pair through the same
  point-count and conductor classifier as identity controls, and require the
  classifier to reject deliberately wrong level labels. Verify every
  candidate and its Frobenius conjugates without treating conjugates as
  independent curves.
- **Execution limits and stop condition:** scan the complete frozen interval
  once under recorded host safety limits and preserve all candidates,
  duplicates, exclusions, certifications, failures, and timing. The pass ends
  only after index `3,599,999,999` is processed, even if 32 pairs appear
  earlier; the selected sample is the first 32 eligible distinct-orbit pairs.
  If fewer than 32 pairs exist in the interval, retain the complete result as
  a bounded census and freeze a new range before extending it. An admitted or
  unresolved field, order, conductor, subgroup, ascent, or certificate failure
  at or before the provisional 32-pair cutoff invalidates the selected sample;
  it is never backfilled with a later success. Failures after that cutoff stay
  retained and reported but do not by themselves invalidate the already fixed
  selected 32. Map, dual, transfer, and performance inference remain outside
  this discovery study. A safety watchdog or resource exhaustion is
  infrastructure/resource evidence, not a mathematical result.
- **Outcomes and next actions:** 32 certified pairs admit a separately frozen
  matched same-negation rho experiment on the sampled parent and bottom
  orbits. Fewer than 32 pairs determine the complete count in this interval
  but do not prove scarcity outside it. Passing explicit maps and duals admits
  a separately frozen transfer-cost experiment; endpoint certificates alone
  do not. A process or resource failure identifies the stage to replace or
  checkpoint and leaves the deeper-level comparison unmeasured.
- **Independent census lane:** replay the exact `cm51_120871.gp` construction
  from revision `f0bdf9f739462766a9060532c59f9bfed69d00b1` in a pinned
  PARI/GP environment and retain every intermediate needed to validate its
  intended 120,870-entry `floor51_120871_cm.txt`. This remains valuable for a
  complete CM census and cross-check, but it no longer blocks the faster
  precommitted indexed sample.
- **Recheck trigger:** a committed, independently replayed 32-pair sample (or
  complete bounded scan with fewer hits), the completed independent CM census,
  or a committed explicit map/dual artifact for either missing direction.

A planned construction is not a completed experiment. It must use the
repository's execution, review, visual-record, and archival rules before its
outputs support an inference.

## Resolution and history

Unresolved. The unpredeclared pilot changes endpoint existence from unknown to
demonstrated for one parent/bottom pair, while leaving admitted sampling,
explicit maps/duals, transfer costs, and rho measurements open. It asserts no
general conductor effect, impossibility, or weakness result.
