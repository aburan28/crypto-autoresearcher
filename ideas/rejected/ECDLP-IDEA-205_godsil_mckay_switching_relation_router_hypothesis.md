# ECDLP-IDEA-205 — Godsil–McKay switching relation router

## Status and claim labels

- Class: `mechanism`
- Risk band: `high-risk`
- Top lane: `-`
- State: `merged_rejected_switching_preserves_spectrum_not_endpoint_source_incidence`
- Cohort: `20260718-d`
- Evidence scale: literature and information-flow audit only; no experiment ran
- Contract posture: none
- Scale labels: prospective finite checks are `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; cospectrality, a switched edge, or a valid relation is not an ECDLP break.

## Falsifiable hypothesis

The factor-base partial-sum relation graph admits a public Godsil–McKay switching partition that converts rare target neighborhoods into dense regular neighborhoods while preserving a compact spectral certificate. An exact inverse switch then recovers every signed source relation and supports factor logs and blind target descent below rho and BSGS.

## Mechanism-new operation

The proposed operation is **incidence-changing cospectral switching followed by exact changed-edge source inversion**. It differs from a spectral filter because the claim is that switching changes relation support, not merely eigenvalues. The audit rejects the current version: the switching partition and neighborhood counts require the relation graph, cospectrality does not preserve elliptic endpoints or source labels, and exact inversion needs a dictionary of the changed source edges.

## Assumptions

1. Public `E/F_p`, prime-order group of size `N`, factor base `B=N^beta`, and target are frozen.
2. A valid switching partition is constructed target-independently without materializing relation edges.
3. Switching improves endpoint relation density by a fixed exponent while keeping setup at most `B^2.25`.
4. Every switched edge has a bounded exact inverse to all signed factor-base sources and exceptional strata.
5. Partition search, graph access, changed-edge storage, output, rank, factor logs, blind descent, verification, and memory are charged.

## Semantic fingerprint

`factor_base_relation_graph | public_Godsil_McKay_partition | support_changing_cospectral_switch | exact_changed_edge_source_inverse | blind_descent`

The fingerprint fails if the graph/partition is materialized, if only the spectrum changes, or if inverse source labels are stored explicitly.

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing public source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `P1477`, the serial relation-state control.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1474`, the nonfunctional stable-deck transition boundary.
4. `inputs/ledger_inventory.json` — imported `P1474`, the CM-stable sparse-deck compression preflight.
5. `inputs/ledger_inventory.json` — imported `ECFG-MX-1478`, the exact one-transition extractor/dense-composition boundary.

## Closest primary literature

- Godsil and McKay, [Constructing cospectral graphs](https://doi.org/10.1007/BF02189621), proves a spectrum-preserving switch for a supplied graph and admissible partition.
- Chaiken, [A combinatorial proof of the all minors matrix tree theorem](https://doi.org/10.1137/0603033), is a nearby spectral/determinantal graph control that likewise assumes explicit incidence.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies elliptic endpoint relations but no implicit switching partition.

No checked primary source supplies the proposed support router and exact inverse; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the relation graph grammar, switching partition rule, changed-edge inverse, masks, and verifier.
2. Construct the partition and switched representation without enumerating source edges.
3. Query known-log endpoints in the switched graph and invert every accepted edge to exact signed sources.
4. Verify relations and preserve unchanged/changed edge tags, collisions, repeats, infinity, multiplicity, and empty endpoints.
5. Collect full-rank rows, solve and verify factor-base logarithms.
6. Apply the identical frozen switch to fresh masks `Q+[r]P`.
7. Substitute logs, invert switch labels, subtract masks, retain ambiguity, and verify `[x]P=Q`.
8. Charge partition construction, graph queries, inverse storage, output, rank, linear algebra, descent, verification, time, and memory.

## Full rho/BSGS cost model

Rho costs `N^(1/2+o(1))` time; BSGS costs that time and memory. Let setup be `N^a,N^a_m`; reciprocal relation and target densities be `N^delta,N^delta_t`; one switched query and inverse cost `N^q,N^q_m`; ranked rows/query be `N^r`; output and inverse ambiguity be `o,u`; and factor-log linear algebra be `N^ell,N^ell_m`. The complete exponents are

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Both must be at most `0.45`; a spectral invariant without charged graph and inverse access has no promotion value.

## Likely fatal obstruction

Godsil–McKay switching preserves adjacency spectrum, not endpoint labels, elliptic addition, or factor-base incidence. Determining a valid partition needs neighborhood counts in the source graph. After switching, exact inversion needs the changed-edge dictionary; discarding it leaves cospectral nonisomorphic graphs and therefore an information-theoretic source ambiguity. Keeping it restores the source deck.

## Proof track

Construct an implicit switching partition and exact source inverse of total size at most `B^2.25`, prove a fixed density gain and independent row rank, and derive `lambda,mu<=0.45` through blind descent.

## Disproof track

Reduce partition tests to relation-edge enumeration, construct cospectral switched graphs with incompatible endpoint/source labels, lower-bound the changed-edge dictionary by `B^3`, or derive exponent at least `0.50`.

## Positive and negative controls

- Positive control: supplied toy graphs with a valid partition and independently recorded changed-edge dictionary.
- Negative control: cospectral graphs with permuted or incompatible endpoint labels.
- Negative control: explicit relation graphs, stored changed-edge maps, spectral-only selectors, rho, and BSGS.

## Quantitative promotion and falsification gates

This version is merged/rejected. Reopening requires partition plus inverse size at most `B^2.25`, query at most `B^1.25`, a preregistered fixed density gain, 100% source/multiplicity recall, zero false tuples, and `lambda,mu<=0.45`. Explicit edge access, `Omega(B^3)` inverse state, spectral ambiguity, one lost source, or exponent at least `0.50` falsifies it.

## Artifact plan

- Prospective partition theorem: `ideas/artifacts/ECDLP-IDEA-205/implicit_switching_partition_theorem.md`
- Prospective inverse specification: `ideas/artifacts/ECDLP-IDEA-205/changed_edge_source_inverse_spec.md`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-205/cost_analysis.md`

All paths are prospective; no artifact root exists.

## Interpretation boundary

This is merged/rejected, novelty-unverified mechanism analysis. Finite checks would be toy and scaling heuristic and model-bound. Cospectrality, a valid switched relation, or toy scalar is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-205/implicit_switching_partition_theorem.md` proving a source-free partition and exact changed-edge inverse of size at most `B^2.25` or proving that admissibility and inversion require `Omega(B^3)` explicit relation-edge state.
