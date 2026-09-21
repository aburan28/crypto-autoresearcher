# ECDLP-IDEA-031 — Anderson t-motive extension coordinate

## Status and claim labels

- Class: `representation`
- Risk band: `high-risk`
- State: `proposed_unapproved`
- Evidence scale: `toy` derivation only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a matched Frobenius module or Ore normal form is not a point transfer.

## Falsifiable hypothesis

The marked one-motive `[Z -> E], 1 mapsto R` admits a functorial equal-characteristic
tau-module extension `epsilon_R in Ext^1_tau(1,M_E)` with exact Baer additivity and a
canonical bounded-degree Ore-polynomial normal form. Its explicitly based `N`-torsion
coordinate `c(R)` remains nonzero and injective on `<P>`, so `x=c(Q)/c(P)` is recovered
below rho/BSGS after construction, rank, Ore degree, gauge, field, and memory costs.

## Mechanism-new operation

Apply a **marked one-motive to tau-module extension functor and canonical Ore normal
form**. This is not a cover/orbit, semistable specialization, same-field isogeny, local
jet, or scalar-power map. The new operation is cross-category: it must send point addition
to Baer sum and turn an unbased extension into a public torsion coordinate.

## Assumptions

1. The functor from the elliptic marked point to the tau-module extension is explicit and target-independent.
2. Baer additivity, gauge equivalence, and torsion compatibility are exact.
3. The coefficient field and an order-`N` public basis are constructed without a DLP.
4. Tau-rank, Ore degree, coefficient height, orientation multiplicity, and memory are charged.
5. A merely matching Frobenius characteristic polynomial is not a point-level transfer.
6. All evidence is toy, heuristic, model-bound, and novelty-unverified.

## Semantic fingerprint

`marked_elliptic_one_motive | tau_module_Ext1_class | Baer_additive_Ore_normal_form | public_torsion_coordinate`

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — motivates a direct cross-category coordinate.
2. `ledger/H-REP-001.yaml` — distinguishes a tau-module functor from a curve model.
3. `ledger/H-ISO-001.yaml` — this is not a same-field E-to-E map.
4. `ledger/EV-REP-002.yaml` — requires gauge and orientation branches to be retained.
5. `ledger/SYNTHESIS-20260716.md` — supplies complete transport, cost, and verification gates.

## Closest primary literature

- Anderson, [t-motives](https://doi.org/10.1215/S0012-7094-86-05328-7), develops the equal-characteristic motive framework.
- Drinfeld, [Elliptic modules](https://doi.org/10.1070/SM1974v023n04ABEH001731), supplies the Drinfeld-module boundary.
- Deligne, [Théorie de Hodge III](https://www.numdam.org/item/PMIHES_1974__44__5_0/), supplies the marked one-motive framework and highlights the missing cross-category functor.
- Tate, [Endomorphisms of Abelian Varieties over Finite Fields](https://eudml.org/doc/141848), supplies the finite-field Frobenius-module comparison boundary.

These sources do not give the claimed functor from arbitrary marked elliptic points or a
public order-`N` Ore coordinate. Novelty remains unverified.

## Complete factor-base-to-target-descent path

The replacement factor base is the single extension coordinate `c(P)`.

1. Freeze the coefficient ring, tau-module, extension functor, gauge group, and Ore normal-form algorithm.
2. Construct `epsilon_P,epsilon_Q` directly and certify Baer additivity on held-out sums.
3. Reduce both extensions to canonical gauge-invariant normal forms in a public basis.
4. Solve `c(Q)=x c(P)` in the based torsion module, retaining orientation ambiguity.
5. Transport every candidate back and return only `[x]P=Q`.

## Full rho/BSGS cost model

Let functor availability/construction be `N^(zeta+c)`, tau-rank `N^beta`, Ore degree
`N^gamma`, coefficient-field degree `N^phi`, normal-form cost
`N^(omega*beta+gamma+phi)`, gauge/orientation ambiguity `N^a`, coordinate solve `N^u`,
verification `N^v`, and bit-memory `N^s`. Rho costs `N^1/2`; BSGS costs `N^1/2`
time/memory. The candidate has time exponent
`lambda=max(zeta+c,omega*beta+gamma+phi,a,u+v)` and
memory exponent `mu=max(s,2*beta+gamma+phi,a,u)`. An `N`-sized basis or unbased module DLP fails.

## Likely fatal obstruction

Anderson/Drinfeld theory is naturally attached to function-field objects; no known
functor sends an arbitrary `E/F_p` marked point to such a bounded extension. Any linear
functor may kill prime-order torsion, while selecting a basis orientation for a surviving
cyclic module may be exactly the original DLP.

## Proof track

Construct the functor and normal form, prove Baer additivity, gauge invariance,
nonvanishing, and injectivity, and bound every rank/degree/field/ambiguity cost below `1/2`.

## Disproof track

Show no compatible point-level functor exists, torsion dies, the normal form changes with
gauge, or any faithful public basis has square-root-or-larger rank/degree/ambiguity.

## Positive and negative controls

- Positive control: synthetic isomorphic tau-modules with a planted based extension coordinate.
- Positive instrumentation control: split extension for `O` and Baer sum for `P+P`.
- Negative control: random tau-extensions and unmatched Frobenius modules.
- Gauge control: exhaustive basis/gauge changes on tiny examples.
- Leakage control: freeze normal forms before exhaustive scalar labels.

## Quantitative promotion and falsification gates

Start with one ordinary prime-order curve over `F_101`, then all feasible 7–16-bit
instances. Promotion only to scaling requires an explicit functor, exact Baer additivity
and gauge invariance on 10,000 held-out triples, nonzero injective coordinates, zero wrong
scalars, and upper 95% `beta<=0.15`, `gamma+phi<=0.20`, `lambda<=0.45`, and
`mu<=0.45`. Falsify if torsion always dies, gauge changes labels, or rank/degree/orientation
has lower 95% exponent at least `0.50`.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-031/t_motive_extension_preflight.sage`
- `ideas/artifacts/ECDLP-IDEA-031/runs/<run_id>/manifest.yaml`
- `ideas/artifacts/ECDLP-IDEA-031/runs/<run_id>/extensions.jsonl`
- `ideas/artifacts/ECDLP-IDEA-031/runs/<run_id>/costs.tsv`
- `ideas/artifacts/ECDLP-IDEA-031/analysis.md`

## Interpretation boundary

All results remain toy, heuristic, model-bound, and novelty-unverified. Frobenius-module
matching, Baer additivity, or a toy normal form is not a breakthrough without a public
point transfer and verified sub-rho/BSGS scalar recovery.

## Exactly one next executable action

1. Construct or disprove a concrete functor from the frozen marked elliptic one-motive to a declared equal-characteristic `A`-motive extension, specifying the coefficient ring and characteristic morphism before any Ore implementation.
