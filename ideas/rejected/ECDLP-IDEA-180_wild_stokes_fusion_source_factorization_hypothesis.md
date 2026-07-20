# ECDLP-IDEA-180 — Wild-Stokes fusion source factorization

## Status and claim labels

- Class: `representation`
- Risk band: `high_risk`
- Top lane: `high_risk`
- State: `merged_rejected_monoidal_fusion_source_inverse_backend`
- Cohort: `20260718-c`
- Evidence scale: primary-literature and semantic preflight only; no experiment ran
- Contract posture: retired `review_required` preflight under `ideas/rejected/contracts/`; zero runs permitted
- Scale labels: any future finite test is `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a Stokes factorization, valid fusion identity, relation, or toy scalar is not an ECDLP break.

## Falsifiable hypothesis

A scalar-blind map sends each elliptic point over a finite field to framed irregular-connection data so that elliptic addition corresponds to quasi-Hamiltonian fusion. A canonical ordered factorization of the fused Stokes data then returns every exact signed factor-base point atom, enabling complete relations, factor logs, and masked target descent below rho and BSGS.

## Mechanism-new operation

The operation is **point-to-wild-connection encoding, quasi-Hamiltonian fusion, and canonical Stokes-factor source inversion**. It is mechanism-new only if the encoding is finite-field, target-uniform, scalar-blind, and its ordered factorization recovers point atoms from endpoints without enumerating sources. Characteristic-zero lifting, a supplied connection factorization, or a generic solver is a control.

Independent operation-level review found that neither the finite-field functor nor the
canonical source inverse is supplied. Without them, this is the monoidal
point-object/fusion followed by factor inversion already rejected in IDEA-127/108, with
nearby IDEA-095/030. Stokes vocabulary does not remove the occupied source-factor gate,
so the current version is merged/rejected.

## Assumptions

1. Public `E,P,N,Q,F,B=N^beta`, connection type, framing, sector order, masks, and verifier are frozen.
2. A canonical point-to-irregular-connection map is defined over the finite field without scalar advice.
3. Fusion exactly represents elliptic addition on every source, multiplicity, sign, and exceptional stratum.
4. Gauge-invariant ordered Stokes factorization returns all exact point atoms without a source table.
5. Lifting, gauge reduction, fusion, factorization, output, rank, factor logs, descent, and memory are charged.

## Semantic fingerprint

`scalar_blind_point_to_wild_connection | quasi_Hamiltonian_fusion | canonical_ordered_Stokes_factors | exact_point_atoms | blind_masked_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing public algebraic source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1410-DIRECT-LABEL-NO-PROMOTION`, the scalar-orientation label control.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1423-FULL-PHASE-NONLINEAR-GAP`, the full-phase nonlinear-rank boundary.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1430-MATERIALIZED-RATIO-OUTPUT-NO-PROMOTION`, the materialized factor-output boundary.
5. `inputs/ledger_inventory.json` — imported `P1478`, the nearest composed transition/resultant mechanism.

## Closest primary literature

- Boalch, [Quasi-Hamiltonian Geometry of Meromorphic Connections](https://arxiv.org/abs/math/0203161), constructs fusion-based finite-dimensional moduli of monodromy/Stokes data over complex geometry.
- Boalch, [Geometry and braiding of Stokes data; Fission and wild character varieties](https://arxiv.org/abs/1111.6228), develops wild character varieties, Stokes data, and their Poisson geometry.

Neither checked primary source gives a finite-field elliptic encoding or a gauge-canonical endpoint-to-point-atom inverse; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the connection type, point encoding, framing, sectors, fusion order, factor base, masks, and verifier.
2. Encode known-log endpoints `R_j=[r_j]P` as irregular-connection/Stokes data without `r_j` or sources.
3. Canonically gauge-reduce and factor the endpoint data into every ordered signed factor-base point tuple.
4. Verify all tuples; preserve gauges, braid/order branches, collisions, repeats, infinity, misses, and output.
5. Collect rank `B`, solve factor-base logs, and independently verify every recovered log.
6. Apply the identical encoding and factorization to fresh masked targets `Q+[t]P`.
7. Substitute verified logs, remove masks, retain all ambiguity candidates, and verify `[x]P=Q`.
8. Charge field lifting, connection construction, fusion, gauges, factors, output, rank, descent, time, and memory.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` time; BSGS costs `N^(1/2+o(1))` time and memory. Let field lift/precision, connection dimension, gauge reduction, sector/braid branching, and other connection setup have separate time exponents `h,d,g,s` and memory exponents `h_m,d_m,g_m,s_m`; set `a=max(h,d,g,s)` and `a_m=max(h_m,d_m,g_m,s_m)`. Let reciprocal relation and target densities be `N^delta,N^delta_t`, canonical factorization cost `N^q,N^q_m`, output and target ambiguity be `N^o,N^u`, and factor-log algebra be `N^ell,N^ell_m`. Then

`lambda=max(a,beta+delta+q+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

These are the complete time and peak-memory exponents; every lift, gauge, sector order, Stokes factor, and source is charged.

## Likely fatal obstruction

The cited theory is characteristic-zero analytic/algebraic geometry and supplies no canonical compatible connection for a finite-field elliptic point. Stokes factors depend on irregular type, framing, gauge, sectors, and braid/order choices. Making the factorization canonical may require exactly the missing point ordering; searching all compatible factors is the original source-fiber search.

## Proof track

Construct the finite-field point/connection functor, prove fusion/addition compatibility and gauge-canonical all-source factorization on every stratum, then derive complete blind-descent exponents `lambda,mu<=0.45`.

## Disproof track

Prove no target-uniform finite-field encoding exists, exhibit gauge/order-equivalent data with different sources, reduce factorization to source enumeration, lose one stratum, or derive either exponent at least `0.5`.

## Positive and negative controls

- Published characteristic-zero framed meromorphic-connection fusion examples.
- Synthetic Stokes products with supplied ordered factors.
- Gauge, braid, sector-order, and characteristic-lift perturbation controls.
- Exhaustive toy elliptic fibers, rho, BSGS, known-log, and blind-target checks.

## Quantitative promotion and falsification gates

This version is merged/rejected at the finite-field-functor and source-inverse gates. Reopening under a new ID requires an operation distinct from IDEA-127/108, 100% source/multiplicity recall, zero false tuples, invariant output under frozen gauge equivalences, no source advice, and formal `lambda,mu<=0.45`; one failure falsifies the scoped successor.

## Artifact plan

- Point/connection theorem: `ideas/artifacts/ECDLP-IDEA-180/wild_stokes_encoding_theorem.md`
- Fusion and source-factor specification: `ideas/artifacts/ECDLP-IDEA-180/fusion_factorization_spec.md`
- Prospective fixtures, verifier, and cost receipt: `ideas/artifacts/ECDLP-IDEA-180/fixtures.json`, `ideas/artifacts/ECDLP-IDEA-180/independent_verifier.py`, and `ideas/artifacts/ECDLP-IDEA-180/cost_analysis.md`
- Retired review-required contract: `ideas/rejected/contracts/ECDLP-EXP-CONTRACT-180_wild_stokes_fusion_preflight.yaml`

All research-artifact paths are prospective; the retired contract remains review-required, unapproved, and zero-run. No artifact or run exists.

## Interpretation boundary

This is merged/rejected, novelty-unverified high-risk evidence. All prospective measurements are toy and cost projections heuristic and model-bound. Fusion correctness, factorization, or relation validity is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-180/wild_stokes_encoding_theorem.md` specifying one finite-field point-to-connection map and proving or refuting fusion compatibility plus gauge-canonical exact source inversion before implementation.
