# ECDLP-IDEA-408 — Raynaud–Gruson flattening source family

## Status and claim labels

- Class: `flattening_by_blowup`
- Risk band: `representation-changing`
- Top lane: `-`
- State: `merged_rejected_flattening_centers_require_source_morphism_and_flatness_supplies_no_point_section`
- Cohort: `20260718-u`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: none; rejected before dispatch
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a correct flattening blowup or flat-family certificate is not an ECDLP break.

## Falsifiable hypothesis

The universal signed relation family can be flattened by an endpoint-constructible Raynaud–Gruson blowup of subgate complexity, after which flat base change and a canonical section lift every restricted endpoint to occurrence-labelled factor points for relations and blind descent.

## Mechanism-new operation

The screened operation is **flatten a source morphism by a controlled blowup of the base, pull back to a flat family with uniform Hilbert data, and use that uniformity to lift a base point to an exact source section**. The proposed primitive is flattening by modification, not a generic blowup, jet lift, or elimination backend.

## Assumptions

1. The relation-family morphism and flattening centers are endpoint-constructible without source enumeration.
2. One target-independent bounded blowup atlas handles every signed and exceptional stratum.
3. Flatness yields an exact canonical occurrence section, not only constant Hilbert polynomial or fiber length.
4. Arbitrary restrictions commute with base change without rebuilding source-sized Rees data.
5. Morphism construction, centers, blowups, charts, base change, section, output, rank, logs, descent, verification, bit time, and memory are charged.

## Semantic fingerprint

`universal_relation_family_morphism | Raynaud_Gruson_flattening_blowup | uniform_flat_base_change | flat_fiber_to_factor_occurrence_section | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`; family regularity must still return exact sources.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`; aggregate fiber invariants require a point section.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`; occurrence labels and negative restrictions remain charged.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`; lossless chart transitions can retain source incidence.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`; source-labelled Rees or chart data cross the explicit-source boundary.

## Closest primary literature

- Raynaud and Gruson, [Critères de platitude et de projectivité](https://eudml.org/doc/142084), develops flattening techniques by modification for supplied morphisms/modules.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), gives a relation family without compact flattening centers or a source section.

No checked source supplies the proposed endpoint-only flattening and occurrence section; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, signed decks, family morphism, flattening centers, blowup charts, transition maps, section rule, restrictions, and verifier.
2. Build the target-independent flattening modification within `B^(9/4+o(1))` without source-indexed Rees generators or charts.
3. For known-log targets, pull back through the appropriate chart, decide exact restricted existence, apply the section to one occurrence-labelled tuple, and verify its sum.
4. Collect at least `B` independent verified rows, charging empty charts, exceptional fibers, ambiguity, output, and dependent rows; solve factor logs.
5. Reuse the unchanged modification on fresh scalar-blind `Q+[t]P` targets under arbitrary restrictions.
6. Substitute factor logs, remove `t`, retain every chart/section branch, and verify `[x]P=Q`.
7. Charge morphism/center construction, blowups, transitions, base change, section, output, rank, logs, descent, verification, bit time, and peak memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, query work excluding output `N^q,N^q_m`, verified rank credit `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

With `0<=r<=o`, setup/state must be at most `B^(9/4+o(1))`, a complete fresh restricted query at most `B^(5/4+o(1))`, and promotion needs `lambda<=0.45` and `mu<=0.45`. Pollard rho has expected time exponent `0.50`; BSGS has time and memory exponents `0.50`.

## Likely fatal obstruction

Flattening begins with the full source morphism and constructs centers from its nonflat locus and module data. Flatness controls dimensions, Hilbert polynomials, or base-change behavior; it does not select a point in a finite symmetric fiber. A section or chart refinement separating every occurrence restores the source deck. This meets IDEAs 085, 097, 159, 216, and 275 at the modification-versus-section boundary.

## Proof track

Construct endpoint-only bounded flattening centers, prove restriction-stable flatness and an exact canonical occurrence section, and certify `lambda,mu<=0.45`.

## Disproof track

Show a center/Rees generator depends on source incidence, exhibit flat equal fibers with different labelled points, or prove blowup/chart/section growth above the caps.

## Positive and negative controls

- Positive: supplied nonflat families with known flattening blowups and labelled sections must reproduce charts and base change.
- Negative: flat finite covers without sections, equal Hilbert polynomials with relabelled points, nonflat restrictions, signed strata, and blind targets.
- Baselines: IDEAs 085/097/159/216/275, generic blowup/flattening software, Query2P1, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only bounded modification, exact restriction-stable occurrence section, `1,000` independent rows, `100` blind descents, caps, and `lambda,mu<=0.45`.
- Falsify on one source-bearing center, flat-fiber label collision, missing chart, cap violation, or either exponent at least `0.50`.
- A correct toy flattening is only a control.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-408/flattening_source_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-408/flat_fiber_section_collisions.json`
- `ideas/artifacts/ECDLP-IDEA-408/restricted_base_change_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-408/cost_analysis.md`

## Interpretation boundary

This rejects the screened elliptic flattening route, not Raynaud–Gruson theory. Every finite check would be toy, heuristic, model-bound, and novelty-unverified; a flatness certificate is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-408/flattening_source_obligations.md` and classify every family equation, center, Rees generator, chart, base-change map, and section by endpoint versus source dependence.
