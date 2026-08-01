# ECDLP-IDEA-212 — Principal-pivot delta-matroid signed-source router

## Status and claim labels

- Class: `representation`
- Risk band: `representation-changing`
- Top lane: `representation-changing`
- State: `rejected_scoped_fixed_cardinality_fiber_violates_symmetric_exchange`
- Cohort: `20260718-e`
- Evidence scale: primary-literature and theorem audit only; no experiment ran
- Contract posture: retired zero-run `review_required` theorem preflight
- Scale labels: every prospective finite check is `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; matrix representability, a pivot identity, or a valid feasible set is not an ECDLP break.

## Falsifiable hypothesis

A universal bounded-degree antisymmetric kernel on signed factor atoms, plus an `O(1)` endpoint gadget, yields an `O(B^2)` representable even delta-matroid. Endpoint principal pivots make its size-five feasible sets biconditional with exact signed five-source elliptic decompositions, with a typed inverse supporting full relation collection and blind target descent below rho and BSGS.

## Mechanism-new operation

The proposed operation is **endpoint principal pivot followed by symmetric-exchange feasible-set inversion**. Independent review rejects the direct formulation: odd skew-symmetric principal determinants vanish, so five sources need a mandatory gadget; moreover, nonzero-principal-minor feasibility is Zariski open while exact five-sum equality is a proper closed condition. A more elaborate source-to-feasible-set code needs auxiliary layers/ancestry state and ceases to be the claimed direct bounded kernel.

## Assumptions

1. Public `E/F_p`, prime-order `G` of size `N`, signed factor ground set of size `B=N^beta`, and target are frozen.
2. A target-independent bounded-degree pair kernel and constant-size endpoint gadget build the skew matrix in `O(B^2)` time/state without pair-completion or source labels.
3. Principal-minor feasibility is biconditional with all exact size-five sources, including signs, repeats, infinity, multiplicity, and empty fibers.
4. Pivot, feasible-set output, typed untwist, rank, factor logs, blind descent, verification, and memory are charged.

## Semantic fingerprint

`signed_factor_ground_set | universal_elliptic_skew_pair_kernel | endpoint_principal_pivot | size_five_symmetric_exchange_source_support | exact_untwist_to_points | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing public source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-RT-1476`, the closest representation-transform router.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1477`, the serial source-state boundary.
4. `inputs/ledger_inventory.json` — imported `P1480`, the structured source-equivalence frontier.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`, the lossless source-edge floor.

## Closest primary literature

- Bouchet, Dress, and Havel, [Delta-matroids and metroids](https://doi.org/10.1016/0001-8708(92)90013-B), develops the delta-matroid structure surrounding feasible-set exchange.
- Brijder and Hoogeboom, [Nullity and loop complementation for delta-matroids](https://doi.org/10.1137/110854692), gives principal-pivot/nullity transformations but no elliptic source compiler.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies the endpoint relation baseline.

No checked source supplies the universal elliptic kernel, all-strata biconditional, and typed inverse. Novelty remains unverified; the stated direct representation is scoped-rejected by exchange.

## Complete factor-base-to-target-descent path

1. Freeze the atom encoding, universal skew kernel, endpoint gadget, pivot sequence, untwist, masks, and verifier.
2. Build the `O(B^2)` matrix without source/completion enumeration and prove the principal-minor/source biconditional.
3. For known-log endpoints, enumerate every feasible size-five set, decode exact signed points and multiplicities, and verify each row.
4. Collect at least `B+sigma` independent rows, solve and verify factor-base logarithms.
5. Apply the identical construction to fresh `Q+[t]P`, substitute factor logs, subtract `t`, preserve ambiguity, and verify `[x]P=Q`.
6. Charge matrix construction, pivots, output, rank, linear algebra, descent, time, and peak memory.

## Full rho/BSGS cost model

Rho costs `N^(1/2+o(1))` time; BSGS costs that time and memory. With setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, pivot plus exact source query `N^q,N^q_m`, independent rank gain `N^r`, output/ambiguity `N^o,N^u`, and factor-log costs `N^ell,N^ell_m`,

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Promotion requires both exponents at most `0.45`; matrix and feasible-set enumeration are not free.

## Likely fatal obstruction

In odd characteristic every odd-order skew-symmetric principal determinant is zero, and a nonsingular even pivot preserves skew-symmetry/parity. More fundamentally, determinant-nonzero feasibility for a universal bounded-degree kernel is Zariski open, whereas exact elliptic five-sum equality is a proper Zariski-closed condition, so they cannot be generically biconditional. Reversing zero/nonzero over `F_p` needs high-degree indicator interpolation. If all feasible sets (or the minimum layer) are forced to be the decoded size-five tuples, ordinary basis exchange also fails generically; auxiliary layers restore the missing coding state.

## Proof track

Reduce the universal Pfaffian/principal-minor biconditional modulo the generic signed five-sum ideal and saturated complement, then prove typed all-strata inversion and `lambda,mu<=0.45`.

## Disproof track

Prove odd-minor parity and the open-versus-closed mismatch, exhibit the conditional fixed-layer basis-exchange violation, show a source-marked coefficient/completion oracle is necessary, or derive matrix/state at least `B^3` or exponent at least `0.50`.

## Positive and negative controls

- Positive control: supplied representable even delta-matroids with planted feasible sets and independently checked pivots.
- Negative controls: nonrepresentable fixed-size set systems, source-marked matrices, explicit completion graphs, cluster/matchgate/forest routers, rho, and BSGS.

## Quantitative promotion and falsification gates

This scoped direct version is rejected. Reopening requires an explicit source-free coding operation that evades parity and the open-versus-closed mismatch, uses state at most `B^2.25` and query at most `B^1.25`, has 100% recall and zero false sets, and gives `lambda,mu<=0.45`. Indicator interpolation, source advice, or exponent at least `0.50` falsifies it.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-212/delta_matrix_spec.md`
- Prospective symbolic fixtures: `ideas/artifacts/ECDLP-IDEA-212/symbolic_exchange_fixtures.json`
- Prospective verifier: `ideas/artifacts/ECDLP-IDEA-212/independent_pivot_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-212/cost_analysis.md`

All paths are prospective; no artifact root exists.

## Interpretation boundary

This is a novelty-unverified scoped negative, not an accepted algorithm. Finite checks would be toy and projections heuristic and model-bound. A pivot, Pfaffian, feasible set, relation, or toy scalar is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-212/delta_matrix_spec.md` proving the odd-minor parity and Zariski open-versus-closed obstruction for the direct kernel, or exhibiting one bounded source-free coding operation that evades both without indicator interpolation.
