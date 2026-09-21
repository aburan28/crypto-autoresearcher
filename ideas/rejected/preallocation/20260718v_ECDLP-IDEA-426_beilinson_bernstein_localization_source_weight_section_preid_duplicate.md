# Pre-ID duplicate draft — Beilinson–Bernstein localization source-weight section

## Status and claim labels

- Class: `beilinson_bernstein_localization_source_weight_section`
- Risk band: `representation-changing`
- Top lane: `-`
- State: `merged_rejected_central_character_aggregates_weights_and_point_faithful_module_is_source_sized`
- Cohort: `20260719-a`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: none; rejected before dispatch
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; localizing a supplied Lie-algebra module is not an ECDLP break.

## Falsifiable hypothesis

Endpoint relation state compiles to a bounded module with central character whose Beilinson–Bernstein localization on a flag variety has weight/costalk support equal to the restricted five-source fibre; a canonical point section returns occurrences below rho and BSGS.

## Mechanism-new operation

The screened operation is **compile endpoint state to a central-character module, localize it as a twisted D-module on a flag variety, isolate weight or costalk support, and pull a support point back to labelled elliptic sources**. This exact localization/point-section operation is distinct from a solver or basis change.

## Assumptions

1. The module and central character are endpoint-derived and source-blind.
2. Localization preserves exact restriction nonemptiness and occurrence identity.
3. A bounded rank/flag dimension represents arbitrary source fibres.
4. Weyl, singular-character, and localization ambiguities are fully charged.
5. Compilation, localization, costalks, output, rank, logs, descent, bit time, and memory are charged.

## Semantic fingerprint

`endpoint_central_character_module | beilinson_bernstein_localization | weight_costalk_support | canonical_source_point_section | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`; localized support must return an exact public source, not a representation certificate.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`; basis transforms retain full source rank.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1422-ADDITIVE-CHARACTER-NO-PROMOTION`; character decompositions have not compressed exact source state.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1423-FULL-PHASE-NONLINEAR-GAP`; nonlinear weight separation remains unconstructed.
5. `inputs/ledger_inventory.json` — imported `P1449`; any joint feature must preserve ancestry under permutations.

## Closest primary literature

- Beilinson and Bernstein, [Localisation de g-modules](https://gallica.bnf.fr/ark:/12148/bpt6k98224180/f47.item), relates supplied modules with central character to twisted D-modules; it does not compile or label this elliptic source fibre.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies endpoint relations without a bounded localization source module.

No checked source provides the proposed compiler or point section; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, decks, restrictions, Lie type, central character, localization twist, support rule, and verifier.
2. Build target-independent module/D-module state within `B^(9/4+o(1))` without source labels.
3. For known-log restricted targets, decide exact nonemptiness from weight/costalk support and recover five occurrences by charged bisection plus singleton verification.
4. Collect at least `B` independent verified rows, charge localization failures and Weyl ambiguity, and solve factor logs.
5. Reuse unchanged localized machinery for fresh scalar-blind `Q+[t]P`.
6. Pull back support points, substitute logs, remove `t`, and verify `[x]P=Q`.
7. Charge compilation, localization, support output, rank, logs, descent, verification, bit time, and memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Here `0<=r<=o`; setup/state is at most `B^(9/4+o(1))`, fresh restricted query at most `B^(5/4+o(1))`, and promotion requires `lambda,mu<=0.45`. Pollard rho expected time and BSGS time/memory retain exponent `0.50`.

## Likely fatal obstruction

Localization begins with a supplied module. A central character aggregates weights, while a module whose costalks distinguish arbitrary elliptic occurrences must encode them at source scale. Singular and Weyl-equivalent support adds ambiguity rather than a canonical point inverse. This meets IDEAs 123, 127, 187, 273, and 306.

## Proof track

Construct a bounded endpoint-only module, prove exact restriction-stable labelled costalks and canonical pullback, then certify complete descent and exponents.

## Disproof track

Exhibit equal central character/localized support with different source labels, identify source-bearing module generators, or prove rank/support output violates a gate.

## Positive and negative controls

- Positive: supplied regular integral central-character modules with known localized support.
- Negative: singular characters, Weyl-conjugate weights, permuted source labels, equal support/different generators, empty restrictions, and blind targets.
- Baselines: IDEAs 123/127/187/273/306, explicit modules, Query2P1, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only compilation, exact all-strata support, `1,000` verified rows, `100` blind descents, caps, and `lambda,mu<=0.45`.
- Falsify on one source-bearing generator, equal-support/different-source collision, localization failure, cap violation, or exponent at least `0.50`.
- Correct localization of a supplied toy module is only a control.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-426/localization_source_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-426/equal_support_source_collisions.json`
- `ideas/artifacts/ECDLP-IDEA-426/restriction_costalk_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-426/cost_analysis.md`

## Interpretation boundary

This rejects the screened localization source section, not Beilinson–Bernstein localization. Prospective checks are toy, heuristic, model-bound, and novelty-unverified; a localization theorem receipt is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-426/localization_source_obligations.md` and classify each module generator, central-character coefficient, localization chart, weight, costalk, pullback map, restriction bit, and occurrence label.
