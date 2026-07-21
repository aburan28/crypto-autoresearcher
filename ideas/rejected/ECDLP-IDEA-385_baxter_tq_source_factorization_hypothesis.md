# ECDLP-IDEA-385 — Baxter T–Q source factorization

## Status and claim labels

- Class: `spectral`
- Risk band: `high-risk`
- Top lane: `-`
- State: `merged_rejected_source_faithful_transfer_matrix_is_hidden_dictionary_and_bethe_roots_lack_point_provenance`
- Cohort: `20260718-s`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: none; rejected before dispatch
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a solved toy T–Q relation or matching spectrum is not an ECDLP break.

## Falsifiable hypothesis

An endpoint-constructible integrable transfer matrix admits a compact Baxter `T–Q` relation whose Bethe roots factor into the five signed deck occurrences of an exact relation, with restriction-stable source recovery and blind descent below the P1553 gates.

## Mechanism-new operation

The screened operation is **construct a commuting transfer matrix and Q-operator from endpoint data, solve their functional T–Q relation, factor the Q-polynomial into Bethe roots, and map those roots canonically to exact factor points**. It is distinct from generic spectral/tensor transforms only if the source-faithful Hamiltonian/dictionary is not supplied as hidden incidence.

## Assumptions

1. The five-deck relation has an endpoint-only integrable-model embedding with compact local Lax/transfer operators.
2. The T–Q functional relation is exact over the relevant finite field/extension and includes every signed P1553 stratum.
3. Bethe roots are complete, nonspurious, restriction-stable, and canonically lift to occurrence-labelled factor points.
4. Transfer/Q construction, diagonalization or functional solving, root factoring, and inverse source map satisfy the frozen gates.
5. Degeneracy, completeness, extension degree, output, rank, factor logs, blind descent, verification, bit time, and memory are charged.

## Semantic fingerprint

`endpoint_integrable_transfer_matrix | Baxter_TQ_functional_relation | Bethe_root_factorization | canonical_roots_to_factor_occurrences | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`; complete source/descent accounting remains mandatory.
2. `inputs/ledger_inventory.json` — imported `ECFG-H642`; spectral representations must preserve exact provenance and full cost.
3. `inputs/ledger_inventory.json` — imported `ECFG-H675`; a compact source-resolving operator is missing.
4. `inputs/ledger_inventory.json` — imported `ECFG-H676`; target-uniform point generation remains unconstructed.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1423-FULL-PHASE-NONLINEAR-GAP`; full spectral/nonlinear information did not supply exact sources.

## Closest primary literature

- Baxter, [Partition function of the eight-vertex lattice model](https://doi.org/10.1016/0003-4916(72)90335-1), develops the transfer-matrix/Q-operator functional method for a supplied integrable model.
- Baxter, [Eight-vertex model in lattice statistics and one-dimensional anisotropic Heisenberg chain](https://doi.org/10.1016/0003-4916(72)90334-X), relates commuting transfer matrices and Bethe-type spectral data but not elliptic factor-deck provenance.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies endpoint relations without an integrable source dictionary.

No checked source constructs the proposed source-faithful transfer matrix or canonical root lift; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, signed decks, integrable embedding, local operators, transfer/Q construction, Bethe/root conventions, restrictions, masks, and verifier.
2. Build target-independent operator state within `B^(9/4)` without one basis state or coupling per source tuple.
3. For known-log targets, update the transfer matrix, solve the exact T–Q relation, factor Q, apply restrictions, lift roots to one occurrence-labelled tuple, and verify its group sum.
4. Collect at least `B` independent verified rows, charge degeneracy/spurious/incomplete roots and dependent rows, solve factor logs, and verify them.
5. Apply the unchanged operators and root lift to fresh scalar-blind `Q+[t]P`, charging extension arithmetic, ambiguity, restrictions, and rebuilds.
6. Recover a tuple, substitute factor logs, remove `t`, retain ambiguity, and verify `[x]P=Q`.
7. Charge operator construction/state, functional solving, root factoring, source lift, output, rank, logs, descent, verification, bit time, and memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, query work excluding output `N^q,N^q_m`, verified rank credit `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

With `0<=r<=o`, setup/state must be at most `B^(9/4+o(1))`, a complete fresh restricted query at most `B^(5/4+o(1))`, and promotion needs time exponent `lambda<=0.45` and memory exponent `mu<=0.45`. Pollard rho has expected time exponent `0.50`; BSGS has time and memory exponents `0.50`.

## Likely fatal obstruction

Baxter's method begins with a precisely structured integrable transfer matrix. A matrix whose eigenstates or Bethe roots distinguish elliptic relation tuples must encode the source Hamiltonian/dictionary; constructing those local couplings is the missing incidence object. Spectra and Q-polynomials also have permutation, degeneracy, completeness, and gauge ambiguities, so roots do not canonically identify factor occurrences. Restriction-specific operators restore source-sized rebuilding. This merges with IDEAs 102, 186, 213, 273, and 305 unless a new endpoint-only integrability and inverse-provenance theorem is proved.

## Proof track

Construct compact endpoint-only commuting operators, prove Bethe completeness and a restriction-stable root-to-occurrence biconditional on every stratum, and derive complete exponents at most `0.45`.

## Disproof track

Show that local operator entries require source couplings, or construct isospectral/equal-Q systems with different factor labels, incomplete/spurious roots, or supergate restriction rebuilds.

## Positive and negative controls

- Positive: supplied finite integrable chains with independently known Bethe roots and labelled states must satisfy the T–Q relation and inverse map.
- Negative: isospectral label permutations, degenerate/incomplete Bethe solutions, gauge changes, generic nonintegrable decks, arbitrary restrictions, all strata, and blind targets.
- Baselines: IDEAs 102/186/213/273/305, explicit source Hamiltonians, Query2P1, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only integrability, exact complete root/source lift, `1,000` independent rows, `100` blind descents, frozen state/query caps, and `lambda,mu<=0.45`.
- Falsify on one source-labelled coupling, one isospectral source collision, incomplete/spurious root, supergate restriction rebuild, or either exponent at least `0.50`.
- A correct toy T–Q identity or spectrum is only a control.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-385/tq_source_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-385/isospectral_root_cases.json`
- `ideas/artifacts/ECDLP-IDEA-385/root_to_source_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-385/cost_analysis.md`

## Interpretation boundary

This rejects the screened elliptic T–Q construction, not Baxter's method. Every finite check would be toy, heuristic, model-bound, and novelty-unverified; spectral correctness is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-385/tq_source_obligations.md` and enumerate every source-dependent coefficient required by the smallest proposed transfer matrix.
