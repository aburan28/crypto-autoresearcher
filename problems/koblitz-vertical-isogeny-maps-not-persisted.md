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
  freezes a deterministic K-163 forward-map gate and its producer.  A fresh
  seed preflight reaches endpoint orbit minimum
  `24362196697750487851526857852297647817644684697`, outside the six sampled
  historical orbits.  This exposed an invalid allow-list gate: the six are
  samples from 280 descending absolute-Frobenius orbits, not an exhaustive
  set.  The repaired producer instead tests the sampled line against both
  absolute-`tau` eigenlines and fails if it is horizontal.  The fresh endpoint
  independently passes the exact point-count/twist check and the archived
  degree-11 cycle predicate (`1` at the crater, `9128` at the endpoint).
  A second bounded relative-tower probe removes `ffembed`, constructs an
  exact-order witness, proves exact absolute x-degree 3,260 for its kernel
  line, enumerates all 22,820 half-kernel abscissae, and certifies a different
  descending endpoint before stopping at the kernel-polynomial boundary.
  Neither probe emitted a map artifact or measured a transfer.
- **Passing small-degree control:** the new local
  [`map73_dual_control.gp`](../research/isogeny_volcano_rho_20261005/map73_dual_control.gp)
  deterministically constructs a degree-73 forward map and algebraic dual on
  the `m=37` proxy.  Its retained receipt checks both compositions and
  inverse-degree recovery for 1,024 distinct frozen prime-subgroup targets,
  plus a separate planted target.  Earlier signed-map and cross-basis bridge
  evidence is retained in `aburan28/crypto` commits
  [`03ac279b2`](https://github.com/aburan28/crypto/commit/03ac279b2e0945ab8b42561df50db5b4d8475cd6)
  and
  [`2ada30059`](https://github.com/aburan28/crypto/commit/2ada300594e486850842d2fa54bcc57f72cd58f1).
  Those earlier artifacts use root finding for the reverse path and do not
  themselves provide an algebraic dual.  The new local control closes this
  proxy prerequisite; it does not certify the missing degree-45,641 map or
  dual.
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

- [ ] Admit the K-163/K-283 construction work with a frozen experiment
  contract and canonical launcher; the current selector has no runnable row.
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

The first three conditions are prerequisites for a valid transfer experiment.
The fourth is additionally required before any performance or weakness
inference.

## Next discriminating step

- **Action or proof obligation:** with the degree-73 map/dual prerequisite now
  passing, admit and execute the relative-tower K-163 conductor-45,641
  forward-map producer under a frozen contract.  Then construct its algebraic
  dual and replay both compositions and recovery on planted subgroup points
  before optimizing or comparing one-time versus transported actions.
  Separately, execute K-283's endpoint census before admitting it as a
  map-construction target; a census result alone does not satisfy this gate.
- **Inputs and controls:** the existing `m=37` crater/73-floor pair, standard
  sect163k1 identity, the frozen relative-tower endpoint with orbit minimum
  `664574991296028830578085892445595444511031875`, exhaustive
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
