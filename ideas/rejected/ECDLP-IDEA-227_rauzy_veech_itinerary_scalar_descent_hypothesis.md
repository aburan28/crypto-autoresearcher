# ECDLP-IDEA-227 — Rauzy–Veech itinerary scalar descent

## Status and claim labels

- Class: `mechanism`
- Risk band: `high-risk`
- Top lane: `-`
- State: `rejected_scoped_no_canonical_interval_order_for_prime_cyclic_orbit`
- Cohort: `20260718-f`
- Evidence scale: primary-literature and theorem audit only; no experiment ran
- Contract posture: none
- Scale labels: every prospective finite check is `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; an interval-exchange itinerary, induction matrix, or orbit label is not an ECDLP break.

## Falsifiable hypothesis

A public coordinate order converts the prime-order elliptic scalar orbit into a bounded interval-exchange transformation. Rauzy–Veech induction would then expose a short itinerary and integer matrices whose digits recover the scalar and exact source branches below rho and BSGS.

## Mechanism-new operation

The claimed operation is **coordinate-derived interval exchange followed by Rauzy–Veech digit recovery**. The direct formulation is scoped-rejected: a generic finite-field orbit has no canonical compatible real interval order or invariant length vector. A faithful itinerary or chosen origin/order labels all `N` scalar positions and reimports the DLP; a coarse itinerary loses scalar/source identity.

## Assumptions

1. Public `E/F_p`, prime-order `G=<P>` of size `N`, coordinate partition, interval order, and induction rule are scalar-blind and target-independent.
2. The induced map is closed under the elliptic orbit with bounded discontinuities and state, without a scalar table.
3. Itinerary digits recover exact scalar orientation and every factor-source branch, not only orbit membership.
4. Partition construction, induction matrices, output, factor logs, descent, verification, and memory are charged.

## Semantic fingerprint

`finite_elliptic_scalar_orbit | public_interval_exchange_order | Rauzy_Veech_induction | itinerary_digit_scalar_and_source_return | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-NR-1474`, the known-scalar orbit invariance negative.
2. `inputs/ledger_inventory.json` — imported `ECFG-H679`, the compact cyclic-sequence hypothesis.
3. `inputs/ledger_inventory.json` — imported `P1477`, the dense orbit-state recurrence control.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1477`, the serial membership negative.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1479`, the source-orientation feature boundary.

## Closest primary literature

- Rauzy, [Échanges d'intervalles et transformations induites](https://doi.org/10.4064/aa-34-4-315-328), defines the induction for supplied ordered interval exchanges.
- Veech, [Gauss measures for transformations on the space of interval exchange maps](https://doi.org/10.2307/1971391), studies invariant measures for the supplied dynamical systems.
- Gallant, [Finding discrete logarithms with a set orbit distinguisher](https://eprint.iacr.org/2010/370), is the nearest scalar-orbit label prior-art boundary.

No checked source constructs a canonical interval exchange from a generic elliptic orbit. Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the coordinate order, partition, interval lengths, induction rule, source return, masks, and verifier.
2. Build the exchange for known-log endpoints without using their scalar order; compute charged itineraries and matrices.
3. Recover exact factor-base scalars or signed relation sources and independently verify every result.
4. Obtain full factor logs and relation rank with all ambiguity retained.
5. Apply the identical exchange to fresh `Q+[t]P`, recover candidates, subtract `t`, and preserve all branches.
6. Accept only `[x]P=Q`, charging partition size, itinerary length, output, verification, and memory.

## Full rho/BSGS cost model

Rho costs `N^(1/2+o(1))` time; BSGS costs that time and memory. Let setup cost `N^a,N^a_m`, reciprocal success densities `N^delta,N^delta_t`, induction plus exact return `N^q,N^q_m`, rank gain `N^r`, output/ambiguity `N^o,N^u`, and factor-log completion `N^ell,N^ell_m`. The complete exponents are

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Partition labels, interval precision, itinerary length, and scalar outputs are charged. Promotion requires `lambda,mu<=0.45`.

## Likely fatal obstruction

Rauzy–Veech induction presupposes an ordered measured interval exchange. Finite-field elliptic coordinates do not make scalar translation piecewise isometric in a bounded ordered partition. Choosing an order compatible with `[k]P -> [k+1]P` is a scalar enumeration; any faithful itinerary has period/state `N`, while a bounded coordinate partition has many scalar collisions.

## Proof track

Construct a scalar-blind bounded interval exchange and prove injective scalar/source itineraries plus complete `lambda,mu<=0.45`.

## Disproof track

Show every bounded public partition has scalar collisions, prove any compatible order encodes the full orbit table, or derive itinerary/state exponent at least `0.50`.

## Positive and negative controls

- Positive control: a supplied low-interval IET with known ordering and independently recovered Rauzy itinerary.
- Negative controls: coordinate-randomized orbit orders, doubling/orbit automata, IDEA-011/032/070/154, Gallant/P1530/P1531 labels, scalar tables, rho, and BSGS.

## Quantitative promotion and falsification gates

This direct version is scoped-rejected. Reopening requires a public partition of sub-square-root size, exact scalar/source recall, zero collisions, no scalar-labelled ordering, and `lambda,mu<=0.45`. One partition collision, orbit table, or either exponent at least `0.50` falsifies it.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-227/finite_orbit_iet_no_go.md`
- Prospective collisions: `ideas/artifacts/ECDLP-IDEA-227/itinerary_collision_fixtures.json`
- Prospective verifier: `ideas/artifacts/ECDLP-IDEA-227/independent_itinerary_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-227/cost_analysis.md`

All paths are prospective; no artifact root exists.

## Interpretation boundary

This is a novelty-unverified scoped mechanism negative. Finite checks would be toy and projections heuristic and model-bound. An itinerary, orbit label, correct digit on a supplied IET, or toy scalar is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-227/finite_orbit_iet_no_go.md` proving that every bounded public coordinate partition collides on the generic prime-cyclic orbit or exhibiting a scalar-blind compatible interval exchange.
