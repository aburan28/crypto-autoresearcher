# ECDLP-IDEA-323 — Cohn–Umans TPP Abel–Jacobi embedding

## Status and claim labels

- Class: `representation_changing_algorithm`
- Risk band: `representation-changing`
- Top lane: `representation_changing`
- State: `merged_rejected_tpp_embedding_and_decoder_encode_source_incidence`
- Cohort: `20260718-n`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: retired `review_required`, unapproved, zero-run contract at `ideas/rejected/contracts/ECDLP-EXP-CONTRACT-323_cohn_umans_tpp_preflight.yaml`
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a triple-product embedding, group-algebra multiplication, valid relation, or toy witness is not an ECDLP break.

## Falsifiable hypothesis

The three special `B^2` Abel–Jacobi pair-wedge families admit a target-independent Cohn–Umans triple-product-property embedding into a finite group algebra of represented size at most `B^(9/4)`, with an exact witness decoder costing at most `B^(5/4)` per fresh target and preserving all six signed source points.

## Mechanism-new operation

The screened operation is **seek normalized public maps from the three source-labelled pair-wedge surfaces to TPP subsets `A,B,C`, prove rather than assume the biconditional `x wedge y wedge z=0` iff `abc=1`, multiply supplied group-algebra indicators, and decode one identity coefficient to exact source pairs**. TPP does not convert an arbitrary wedge incidence into a group identity: Cohn–Umans embeds a supplied multiplication tensor and does not construct the missing elliptic incidence maps or witness inverse. Here the maps must already exclude every false triple and the decoder must retain exact source labels, so together they encode the source-incidence dictionary audited by P1552/P1553. Moreover, three `B^2` subsets satisfying ordinary TPP make the pair-product map injective, forcing `|G|>=B^4`; a dense group-algebra vector already exceeds the `B^(9/4)` state cap. Sparse or irreducible-representation compression and exact witness replay require separate proved bounds. The route therefore merges with IDEAs 035, 050, 117, 257, and 280 rather than opening a new representation theorem gate.

## Assumptions

1. Public evaluation rows and their pair wedges map injectively to three group subsets without materializing ternary incidences.
2. The subsets satisfy an exact TPP or simultaneous TPP biconditional for every distinct, repeated, signed, and coloured source stratum.
3. Group-algebra multiplication and representation transforms fit setup/state `B^(9/4)` and fresh-target `B^(5/4)` bounds including bit complexity.
4. Nonzero identity coefficients decode to exact six source indices rather than only counts or sums.
5. Relation density, independent rank, factor logs, blind descent, output, verification, and memory are fully charged.
6. The P1553 incidence arm uses prelogged pairwise-disjoint actual-point decks; colliding known targets are replaced, and blind-mask resampling or deck rebuilds are charged unless a globally confluent overlap-safe construction is proved.

## Semantic fingerprint

`three_Abel_Jacobi_pair_wedge_surfaces | explicit_triple_product_property_embedding | group_algebra_identity_coefficient | exact_six_source_witness_decoder | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the source-fiber generator and transposed multi-target join requirement.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`, the exact source-resolving predicate boundary.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`, the batch source-generator boundary.
4. `inputs/ledger_inventory.json` — imported `P1478`, the compact transition whose source-complete composition becomes dense.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1423-FULL-PHASE-NONLINEAR-GAP`, the aggregate-transform versus exact-source boundary.

The decisive live-ledger controls are `ledger/FINDING-PF-IC-001.md` entries
`ECFG-P1552-R1` and `ECFG-P1553-R1`, which own the exact `2+2+2` incidence and
source-unranking boundary. This TPP wrapper supplies neither the public incidence
embedding nor the witness decoder and therefore creates no successor lane.

## Closest primary literature

- Cohn and Umans, [A group-theoretic approach to fast matrix multiplication](https://arxiv.org/abs/math/0307321), embeds supplied matrix-multiplication tensors into group algebras through the triple product property.
- Cohn, Kleinberg, Szegedy, and Umans, [Group-theoretic algorithms for matrix multiplication](https://arxiv.org/abs/math/0511460), develops simultaneous embeddings and their represented multiplication costs.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), does not provide a TPP embedding or source-decoding identity coefficient.

No checked source constructs the required Abel–Jacobi TPP subsets, all-strata witness decoder, or P1552-compliant complete path; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N`, six coloured signed decks with `B=N^(1/5)`, evaluation basis, pair wedges, finite group, TPP maps, transforms, masks, and independent verifier.
2. Build the three group subsets and representation data without enumerating pair-pair incidences or a `B^3` separator.
3. For at least `B` independent known-log rows, multiply group-algebra indicators, decode exact six-source tuples, verify rows, collect independent rank, solve all factor logs with charged linear algebra, and independently verify them.
4. Reuse the identical embedding and decoder on fresh `Q+[t]P` targets without target-specific subsets or source tables; replace colliding known targets and charge every blind-mask resample or deck rebuild under the frozen disjoint-deck policy.
5. Substitute verified factor logs, remove masks, retain coefficient/witness ambiguity, and return scalar candidates.
6. Accept only `[x]P=Q`, charging group construction, representations, multiplication, decoding, output, rank, factor logs, descent, verification, and memory.

## Full rho/BSGS cost model

With setup `N^a,N^a_m`, factor base `N^beta` where `beta=1/5`, reciprocal relation and target densities `N^delta,N^delta_t`, one group product and coefficient computation excluding witness emission `N^q,N^q_m`, independently verified rank amortization `N^r`, separately charged exact-source output `N^o`, ambiguity `N^u`, and factor-log linear algebra `N^ell,N^ell_m`,

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

All group elements, representation degrees, transforms, coefficients, witness tags, and decoding are charged; ordinary `B^2` TPP subsets force `|G|>=B^4` before any dense transform. Here `0<=r<=o`: rank credit cannot exceed independently verified emitted-row output. The fixed `beta=0.20` gate requires `beta+delta+q-r+o<=0.45`, online `delta_t+q+o+u<=0.25`, all setup/state/factor-log terms at most `0.45`, and at least `B` independent rows. Pollard rho has expected time exponent `0.50` and memory exponent `0`; BSGS has time and memory exponents `0.50`.

## Likely fatal obstruction

TPP is an injectivity property for supplied subset triples. Mapping a wedge incidence to `abc=1` without false triples can encode the entire rare incidence relation, which is the missing source locator. Natural realizations with `B^2` elements per subset can require group-algebra or represented multiplication state at least `B^3`, and the identity coefficient aggregates all witnesses unless source-sized provenance tags are retained.

## Proof track

Exhibit normalized public TPP maps, prove rather than assume the all-strata wedge-incidence iff group-identity biconditional, account for the ordinary `|G|>=B^4` injection or prove a sparse/irrep alternative inside the rectangle, prove exact witness replay and independent relation rank, then complete factor-log and blind target descent with `lambda,mu<=0.45`.

## Disproof track

Show any faithful TPP map determines the incidence/source dictionary, prove group/representation/witness state exceeds `B^(9/4)`, produce coefficient collisions with distinct source tuples, or show either complete exponent at least `0.50`.

## Positive and negative controls

- Positive: standard published TPP matrix-multiplication subsets must reproduce all planted product coefficients and externally tagged witnesses.
- Negative: random group embeddings matched for subset sizes and aggregate coefficient counts must not decode elliptic sources.
- Baselines: IDEAs 035/050/117/257/280, P1434, P1478, direct `3+3` separator, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with explicit source-free maps, exact all-strata biconditional, 1,000 verified rows and 100 blind descents at each large future toy size, campaign/state at most `B^(9/4)`, query at most `B^(5/4)`, and `lambda,mu<=0.45`.
- Falsify if embedding construction uses incidences/source tags of super-cap size, any false/missed source occurs, or either complete exponent reaches `0.50`.
- Intermediate exponents or aggregate-only coefficients are inconclusive and non-promoting.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-323/tpp_incidence_embedding_merge_receipt.md`
- `ideas/artifacts/ECDLP-IDEA-323/tpp_collision_fixtures.json`
- `ideas/artifacts/ECDLP-IDEA-323/independent_tpp_verifier.py`
- `ideas/artifacts/ECDLP-IDEA-323/cost_analysis.md`

## Interpretation boundary

This is preserved rejected representation evidence, not a matrix-multiplication claim or executable ECDLP algorithm. A valid TPP, fast aggregate product, relation, or toy witness is not generic-prime scalar recovery or a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-323/tpp_incidence_embedding_merge_receipt.md` recording the `|G|>=B^4` dense-state gate and mapping the missing incidence maps and witness decoder to P1552/P1553.
