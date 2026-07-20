# ECDLP-IDEA-211 — Coleman norm-coherent elliptic-unit return

## Status and claim labels

- Class: `arithmetic-transfer`
- Risk band: `high-risk`
- Top lane: `high-risk`
- State: `merged_rejected_coleman_norm_is_p_primary_or_miller_s_unit_duplicate`
- Cohort: `20260718-e`
- Evidence scale: primary-literature and theorem audit only; no experiment ran
- Contract posture: retired zero-run `review_required` theorem preflight
- Scale labels: every prospective finite check is `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; norm coherence, a unit factorization, or valid relation is not an ECDLP break.

## Falsifiable hypothesis

A canonical lift and Lubin–Tate/Coleman tower attach a norm-coherent elliptic-unit series `Col_A(T)` to each point. A bounded norm-fixed endpoint coefficient factors canonically into exact signed factor sources iff they sum to that endpoint, enabling factor logs and blind return/descent below rho and BSGS.

## Mechanism-new operation

The claimed operation is **norm-fixed Coleman-series factorization with typed return**, not a formal logarithm or Miller-function backend. It merges/rejects absent a theorem because Coleman norms control a local `p`-primary tower, while the generic subgroup of order `N` is prime to `p`; a nonlinear unit factorization duplicates Miller/S-unit descent and a digit return duplicates ramification lanes.

## Assumptions

1. Public `E/F_p`, prime-order `N`, factor base `B=N^beta`, and target are frozen with a canonical target-independent lift and tower.
2. Prime-to-`p` subgroup sensitivity survives the norm, with truncation, extension degree, and state at most `N^0.45`.
3. Coefficient factorization returns every exact signed source and multiplicity on every stratum.
4. Lift, tower, unit atoms, factorization, return, output, rank, factor logs, masked descent, and memory are charged.

## Semantic fingerprint

`canonical_local_lift | norm_coherent_elliptic_units | Coleman_power_series_fixed_point | nonlinear_coefficient_factor_to_exact_sources | blind_return_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `OFQ-autolab-05`, the torsion-orientation division boundary.
2. `inputs/ledger_inventory.json` — imported `ISO-SP-001`, the transfer/isogeny special-case control.
3. `inputs/ledger_inventory.json` — imported `TRANSFER-H003`, the orientation-preserving transfer hypothesis.
4. `inputs/ledger_inventory.json` — imported `TRANSFER-H004`, the nonhomomorphic cover-label route.
5. `inputs/ledger_inventory.json` — imported `TRANSFER-NR-045`, the failed native-factor transfer boundary.

## Closest primary literature

- Coleman, [Division values in local fields](https://doi.org/10.1007/BF01390028), develops norm-coherent power series in local towers.
- Lubin and Tate, [Formal complex multiplication in local fields](https://doi.org/10.2307/1970622), supplies the formal `p`-primary tower.
- Miller, [The Weil pairing, and its efficient calculation](https://crypto.stanford.edu/miller/), is the closest elliptic-function/unit control.

No checked source proves a bounded prime-to-`p` source-biconditional coefficient and exact return; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the lift, tower, unit construction, coefficient, factor inverse, masks, return, and verifier.
2. Precompute charged factor-unit atoms without source tuples.
3. For known endpoints, compute and factor the coefficient to all exact signed factor atoms; verify every elliptic row.
4. Collect full rank, solve and verify factor-base logs.
5. Repeat unchanged on fresh `Q+[t]P`, return all local candidates, substitute logs, and subtract `t`.
6. Preserve ambiguity and accept only `[x]P=Q`, charging tower setup, extension, output, and memory.

## Full rho/BSGS cost model

Rho costs `N^(1/2+o(1))` time; BSGS costs that time and memory. With setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, norm/factor/return query `N^q,N^q_m`, rank gain `N^r`, output/ambiguity `N^o,N^u`, and factor-log costs `N^ell,N^ell_m`,

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

All extension and precision terms enter `a,q,a_m,q_m`; promotion requires both exponents at most `0.45`.

## Likely fatal obstruction

Norm coherence linearizes the formal `p`-primary direction. Prime-to-`p` torsion is étale/semisimple and lacks a canonical scalar orientation in these coefficients. A source-sensitive factorization needs a full torsion field, grows with conductor, aggregates sources, or recreates the Miller S-unit/DLP problem.

## Proof track

Construct a coefficient with prime-to-`p` sensitivity, a nonlinear all-strata source biconditional, bounded truncation/extension, exact return, and complete `lambda,mu<=0.45`.

## Disproof track

Show the coefficient factors through formal log/character data, collides on distinct `N`-torsion points, needs a Miller straight-line program/torsion table, or has extension or total exponent at least `0.50`.

## Positive and negative controls

- Positive control: supplied Lubin–Tate norm-coherent sequences on `p`-primary torsion.
- Negative controls: shuffled prime-to-`p` torsion, Miller S-units/IDEA-007, ramification IDEA-160, uncharged torsion fields, rho, and BSGS.

## Quantitative promotion and falsification gates

This version is merged/rejected. Reopening requires nonzero separation on generic prime-to-`p` `N`-torsion, 100% source/multiplicity recall, zero false sources, all extension/truncation costs charged, and `lambda,mu<=0.45`. Formal/Miller reduction, one collision, or exponent at least `0.50` falsifies it.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-211/coleman_prime_to_p_source_return_theorem.md`
- Prospective inverse: `ideas/artifacts/ECDLP-IDEA-211/norm_coefficient_inverse_spec.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-211/fixtures.json`
- Prospective verifier: `ideas/artifacts/ECDLP-IDEA-211/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-211/cost_analysis.md`

All paths are prospective; no artifact root exists.

## Interpretation boundary

This is novelty-unverified merged/rejected arithmetic-transfer analysis. Finite checks would be toy and projections heuristic and model-bound. Norm coherence, unit factorization, relation validity, or toy scalar recovery is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-211/coleman_prime_to_p_source_return_theorem.md` proving a canonical norm-fixed coefficient with a prime-to-`p` source biconditional and bounded return, or proving it factors through the formal/Miller controls.
