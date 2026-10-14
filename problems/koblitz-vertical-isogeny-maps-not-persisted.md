# Koblitz vertical isogeny maps are not persisted

- **Status:** `open`
- **Kind:** implementation gap and proof gap
- **Affected work:** [Koblitz isogeny rho-transfer protocol](../docs/experiments/koblitz-isogeny-rho-transfer.md), [2026-10-14 conductor-gap panel](../research/conductor_gap_panel_20261014/REPORT.md), K-163 conductor-45641 endpoints, and K-283 conductor-1697 endpoints
- **Next action owner:** unassigned executor after an experiment contract admits the map-construction work
- **Last updated:** 2026-10-14

## Problem

We cannot test whether a NIST Koblitz ECDLP becomes cheaper on the known
conductor floors, or whether the source Frobenius action remains usable after
transfer, because no durable explicit source-to-endpoint map and dual with a
subgroup-action certificate are available for the K-163 conductor-45641 or
K-283 conductor-1697 candidates.

The scoped sources are sect163k1 over its standard `F_(2^163)` polynomial and
sect283k1 over its standard `F_(2^283)` polynomial, each with its standard
prime subgroup. The candidate endpoints must retain the same trace and group
order. The required threat model distinguishes a publicly discoverable path
from supplied private advice and charges discovery accordingly.

## Evidence and uncertainty

- **Observed:**
  `research/ecc2k130_conductor_isogenies_20261007/analogues/run163_45641.gp`
  and its output generated six K-163 conductor-45641 endpoint representatives,
  while `iso163_45641.txt` retains endpoints. The generator computes kernel
  material transiently but does not persist a replayable point evaluator,
  exceptional-input behavior, normalization, or dual. The K-283
  [`README`](../research/ecc2k130_conductor_isogenies_20261007/k283/README.md)
  explicitly states that its conductor-1697 census constructs neither the
  degree-1697 map nor its dual or subgroup certificate.
- **Observed implementation progress:**
  [`MAP163_45641_PROTOCOL.md`](../research/ecc2k130_conductor_isogenies_20261007/analogues/MAP163_45641_PROTOCOL.md)
  now freezes a deterministic K-163 forward-map gate and its producer.  A
  bounded compatibility diagnostic reaches the expensive `ffembed` stage
  after fixing the driver's prior silent included-file exit.  The bounded run
  did not finish, emitted no map artifact, and says nothing about the dual or
  full transfer cost.
- **Derived or proved:** the archived source signed-Frobenius certificates for
  all five NIST K curves pass the Stage-0 consistency audit. That audit trusts
  their point-check booleans and does not emit a primality certificate. For
  any valid degree-`d` map coprime to the subgroup order, the candidate
  transported subgroup action is
  `[d^(-1)] o phi o tau o dual(phi)`. This identity does not construct the
  missing maps or price them.
- **Suspected explanation:** retaining only endpoint coefficients was enough
  for the earlier conductor census, whose objective was structural. It was
  not designed as a transfer benchmark. This explains the artifact shape but
  does not show map construction is infeasible.
- **Missing capability:** a serialized or deterministically reconstructible
  `phi` and `dual(phi)`, independent composition checks, full-size subgroup
  tests, and measured evaluation/canonicalization costs.
- **What this evidence does not establish:** it does not show the endpoints
  lack useful endomorphisms, that their best quotient is negation-only, that a
  conductor gap changes ECDLP hardness, or that no weak representative exists.
  An endpoint coefficient outside `F_2` makes absolute Frobenius move to a
  conjugate curve; the conjugate orbit is not by itself a native endpoint
  rho quotient.

## What would unblock it

- [ ] Persist or deterministically rebuild one K-163 degree-45641 or K-283
  degree-1697 `phi` and its dual, including complete endpoint identities,
  kernel representation, normalization, field of definition, exceptional
  inputs, and artifact hashes.
- [ ] Verify both dual compositions, map a standard generator to a nonzero
  point of exact prime order, recover planted logarithms back on the source,
  and certify or reject the transported signed-Frobenius action on the target
  subgroup.
- [ ] Measure construction and evaluation under the matched five-arm protocol
  with all representation conversions and failures retained.

The first two conditions make a transfer experiment valid. The third is still
required before any performance or weakness inference.

## Next discriminating step

- **Action or proof obligation:** first persist and certify the smaller
  degree-73 map/dual on the existing `m=37` proxy edge, and compare one-time
  endpoint-to-crater transfer with the transported action. Then execute the
  frozen K-163 conductor-45641 forward-map producer under an admitted run,
  add a dual, and replay both on planted subgroup points before optimizing
  them.  Separately, execute K-283's endpoint census before admitting it as a
  map-construction target; a census result alone does not satisfy this gate.
- **Inputs and controls:** the existing `m=37` crater/73-floor pair, standard
  sect163k1 identity, the first frozen conductor-45641 endpoint, exhaustive
  toy point-map checks, wrong-kernel and wrong-normalization mutations,
  identity path, one-time transfer, and the source signed-Frobenius incumbent.
- **Execution limits and stop condition:** first produce one exact replayable
  map certificate. Stop performance inference on any map, dual, subgroup,
  exception, or planted-log failure; preserve the failure as implementation
  evidence.
- **Outcomes and next actions:** a passing certificate admits the five-arm
  cost experiment; a construction failure keeps the route indeterminate and
  identifies the failed representation; a valid but expensive map supplies a
  measured gate cost; discovery of a cheap target action adds an arm rather
  than being folded into negation-only.
- **Recheck trigger:** a committed explicit map/dual artifact or a new
  construction method for either named conductor direction.

## Resolution and history

Unresolved. This record names a missing transfer certificate; it is not a
negative result about the isogeny class or ECDLP.
