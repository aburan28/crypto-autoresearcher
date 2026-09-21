# ECDLP-IDEA-245 — Isospectral-Hilbert sheet source lift

## Status and claim labels

- Class: `geometric_representation`
- Risk band: `representation_changing`
- Top lane: `-`
- State: `merged_rejected_isospectral_sheet_is_source_labelled_hilbert_deck`
- Cohort: `20260718-h`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: none
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; correctness, a local identity, a source tuple, relation validity, or a toy scalar is not an ECDLP break.

## Falsifiable hypothesis

The endpoint Abel-Jacobi fiber lifts to an isospectral Hilbert scheme whose finite cover retains an ordered sheet for each factor point while its Hilbert-Chow quotient stays compact.  A canonical Procesi-bundle projector would select the exact source sheet and enable full descent below rho and BSGS.

## Mechanism-new operation

The screened operation is **lift the symmetric source divisor to the isospectral Hilbert cover and recover ordered point sheets through a canonical Procesi-bundle projector**.  The isospectral cover retains more sheet data than IDEA-169's nested Hilbert flag and is not merely a post-hoc ordering.  Deduplication fails it because constructing the relevant Hilbert point, cover fiber, or projector requires the source-labelled zero-dimensional subscheme itself; the quotient endpoint supplies only its Abel-Jacobi class.  A solver swap,
parameter change, same-field isogeny variant, explicit large-prime/source table, post-hoc selector,
dense resultant, or relation-only certificate receives no mechanism credit.

## Assumptions

1. A compact endpoint-derived Hilbert point and isospectral lift exist over the prime field without enumerating factor tuples.
2. The cover degree, Procesi bundle, projector evaluation, and rational sheet return have sub-rho represented size and work.
3. The selected sheet yields all exact signed points and multiplicities on diagonal and nonreduced strata.
4. Construction, cover branches, output, relation density, rank, factor logs, blind descent, verification, and memory are charged.

## Semantic fingerprint

`abel_jacobi_endpoint | hilbert_chow_fiber | isospectral_hilbert_cover | procesi_sheet_projector | exact_ordered_points | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-H642`, the structured-coordinate source-deck barrier.
2. `inputs/ledger_inventory.json` — imported `ECFG-H686`, the algebraic support/source-return frontier.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1447`, the aggregate coordinate-energy negative.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1449`, the coordinate-expansion matrix boundary.
5. `inputs/ledger_inventory.json` — imported `P1476`, the complete five-source exponent gate.

## Closest primary literature

- Haiman, Hilbert schemes, polygraphs and the Macdonald positivity conjecture, [https://arxiv.org/abs/math/0010246](https://arxiv.org/abs/math/0010246), constructs the isospectral Hilbert scheme and Procesi bundle from supplied point-scheme data.
- Haiman, Vanishing theorems and character formulas for the Hilbert scheme of points in the plane, [https://arxiv.org/abs/math/0201148](https://arxiv.org/abs/math/0201148), studies the same supplied isospectral geometry but gives no Abel-Jacobi source section.
- Semaev, Summation polynomials and the discrete logarithm problem, [https://eprint.iacr.org/2004/031](https://eprint.iacr.org/2004/031), supplies a relation fiber, not a compact isospectral sheet section.

These sources were checked as primary records for the named supplied-input operation.  None gives
the endpoint-only compiler, exact point-source inverse, factor-log calibration, and fresh masked
descent required here.  No ECDLP novelty is claimed; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze public `E/F_p`, prime-order `G=<P>` of size `N`, factor base `F` of size `B=N^beta`, signs, arity, public colours/auxiliary choices, masks, tie rules, and the independent verifier before targets.
2. For each known-log endpoint `R=[r]P`, derive the Hilbert point, isospectral cover data, and sheet projector from each public endpoint without a factor-point ideal or source-labelled subscheme.
3. Evaluate the projector, enumerate every rational ordered sheet and signed lift, preserve diagonal multiplicities, and verify exact sums. Preserve every failure, duplicate, ambiguity branch, repeated point, infinity chart, nonreduced case, and rejected candidate.
4. Collect independently verified rows until rank `B`, charge rank loss and output, solve all factor logs, and independently verify every `[log_P(S)]P=S`.
5. Apply the identical frozen constructor and source inverse to fresh masks `Q+[t]P`, with no known-log-only branch, target-selected parameter, or post-hoc source advice.
6. Substitute verified factor logs, subtract `t`, retain every candidate caused by source ambiguity, and accept only `x` satisfying `[x]P=Q`; serialize complete time and peak-memory accounting.

## Full rho/BSGS cost model

Pollard rho has expected time exponent `1/2`; BSGS has time and memory exponents `1/2`.
Let setup time and memory be `N^a,N^a_m`, reciprocal relation and target success densities
be `N^delta,N^delta_t`, one mechanism evaluation plus exact source inverse cost
`N^q,N^q_m`, independent-rank gain be `N^r`, source output and target ambiguity be
`N^o,N^u`, and factor-log completion be `N^ell,N^ell_m`.  The complete exponents are

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every constructor coefficient, represented state, preprocessing query, failed target, branch,
source output, relation row, rank defect, factor log, masked descent, verifier call, bit operation,
and live byte is charged.  Promotion requires both complete exponents at most `0.45`; correctness
or relation validity alone has no performance meaning.

## Likely fatal obstruction

The isospectral Hilbert scheme resolves and labels a supplied symmetric-product point; it does not choose a divisor in the positive-degree Abel-Jacobi fiber.  A source-faithful Hilbert ideal or Procesi projector contains the roots/labels being sought, while the cover has factorial sheet ambiguity and the full source-fiber degree.

## Proof track

Construct an endpoint-only compact Hilbert point and canonical rational sheet section on all strata, then prove complete source recovery and exponents at most 0.45.

## Disproof track

Show the endpoint determines only a Picard class, exhibit distinct source divisors with the same endpoint and isomorphic quotient data, or prove cover/projector/output or either complete exponent at least 0.50.

## Positive and negative controls

- Positive control: supplied zero-dimensional subschemes with independently known isospectral sheets and Procesi projectors.
- Negative controls: source-label permutations, equal Abel-Jacobi divisors, IDEA-085, IDEA-094, IDEA-169, explicit Hilbert ideals, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires a source-free Hilbert compiler, canonical exact sheet recall with zero false points, bounded cover/projector state, full rank and factor logs, blind descent, and complete lambda and mu at most 0.45.  Any supplied ideal, point-coloured tautological bundle, unresolved sheet permutation, or exponent at least 0.50 falsifies this version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-245/isospectral_sheet_section_theorem.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-245/fixtures.json`
- Prospective independent verifier: `ideas/artifacts/ECDLP-IDEA-245/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-245/cost_analysis.md`

All paths are prospective; no artifact root exists and no contract or experiment ran.

## Interpretation boundary

This is a novelty-unverified merged/scoped-negative hypothesis.  Every finite check would be toy and every complexity projection remains
heuristic and model-bound.  A correct identity, canonical form, decomposition, valid relation,
recovered source tuple, or toy scalar is not a complete generic ECDLP algorithm, crypto-scale
validation, or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-245/isospectral_sheet_section_theorem.md` proving an endpoint-only Hilbert-point and Procesi-sheet section or a Picard-fiber/source-deck no-go.
