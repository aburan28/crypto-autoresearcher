# ECDLP-IDEA-221 — Gross–Koblitz Gauss-digit return

## Status and claim labels

- Class: `arithmetic-transfer`
- Risk band: `high-risk`
- Top lane: `-`
- State: `merged_rejected_character_orientation_reimports_dlp_and_p1532_controls`
- Cohort: `20260718-f`
- Evidence scale: primary-literature and live P1531/P1532 semantic audit only; no experiment ran
- Contract posture: none
- Scale labels: every prospective finite check is `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a Gauss-sum formula, character value, or digit identity is not an ECDLP break.

## Falsifiable hypothesis

A public elliptic Gauss sum attached to `[x]P` has Gross–Koblitz gamma factors whose valuations or residues expose typed digits of `x` without a chosen character orientation. Bounded digit return would recover exact factor logs and fresh masked targets below rho and BSGS.

## Mechanism-new operation

The claimed operation is **universal elliptic Gauss aggregation followed by p-adic gamma digit return**. It merges/rejects because Gross–Koblitz starts with a multiplicative character indexed by a known exponent. On an elliptic prime-order subgroup, obtaining a nonzero normalized Fourier mode requires the hidden character orientation and becomes a Gallant type-1 distinguisher; orientation-free powers erase it. The live P1531/P1532 audits record the admitted row-producing and recurrence controls. P1532 R1 correctly leaves a distinct collision-recovering multiset-resultant interface open for P1533, but supplies neither that operation nor the scalar-blind Gauss/gamma digit map claimed here.

## Assumptions

1. Public `E/F_p`, prime-order `G=<P>` of size `N`, factor base `F` of size `B=N^beta`, and canonical scalar-blind character data are frozen.
2. The Gauss sum is computable without a pairing, torsion basis, orbit scan, scalar table, or one field operation per hidden character.
3. Gamma valuations/residues return exact scalar digits with all conductor, extension, precision, and ambiguity costs charged.
4. Factor logs, fresh masked descent, output, verification, and memory are included end to end.

## Semantic fingerprint

`elliptic_orbit_character_sum | universal_Gauss_aggregate | Gross_Koblitz_p_adic_gamma | typed_scalar_digit_return | factor_logs | blind_target`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-NR-1474`, the known-scalar orbit compression boundary.
2. `inputs/ledger_inventory.json` — imported `P1479`, the public-feature factor-log compression test.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1479`, the exact feature/source-orientation negative.
4. `inputs/ledger_inventory.json` — imported `OFQ-autolab-05`, the torsion-orientation division gap.
5. `inputs/ledger_inventory.json` — imported `ISO-SP-001`, the special self-pairing orientation control.

## Closest primary literature

- Gross and Koblitz, [Gauss sums and the p-adic Gamma-function](https://annals.math.princeton.edu/1979/109-3/p06), relates finite-field multiplicative-character Gauss sums to gamma values for a supplied character index.
- Berghoff, [Efficient computation of universal elliptic Gauss sums](https://arxiv.org/abs/1707.08610), computes elliptic Gauss-sum data but does not provide orientation-free scalar recovery.
- Gallant, [Finding discrete logarithms with a set orbit distinguisher](https://eprint.iacr.org/2010/370), is the type-1 character-orientation prior-art boundary used by P1531/P1532.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), gives the endpoint-relation baseline.

No checked source supplies the claimed canonical elliptic character and digit return. Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the elliptic character family, Gauss sum, gamma normalization, digit map, masks, and verifier.
2. For known-log endpoints, compute charged orientation-free sums and return all candidate scalar digits.
3. Reconstruct and verify exact factor-base logarithms; reject any result that used known scalar indices to choose a character.
4. Obtain and verify full factor-base coverage and any relation rows used to interpolate missing logs.
5. Apply the identical sum and digit map to fresh `Q+[t]P`, subtract `t`, and preserve every candidate.
6. Accept only `[x]P=Q`, charging conductor, extension, precision, character batching, output, verification, and memory.

## Full rho/BSGS cost model

Rho costs `N^(1/2+o(1))` time; BSGS costs that time and memory. Let setup cost `N^a,N^a_m`, reciprocal base/target success densities `N^delta,N^delta_t`, Gauss/gamma query and digit inverse `N^q,N^q_m`, independent rank gain `N^r`, output/ambiguity `N^o,N^u`, and factor-log completion `N^ell,N^ell_m`. Then

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Character count, torsion payload, p-adic precision, and batch row preservation enter these exponents. Promotion requires `lambda,mu<=0.45`.

## Likely fatal obstruction

Gross–Koblitz returns digit information about the index of an already chosen multiplicative character. There is no canonical nontrivial character of a generic elliptic prime-order subgroup that reveals the unknown scalar. Fourier normalization introduces `chi(x)` and is Gallant type-1; universal/orientation-free powers cancel it. Directly retaining every character or explicit P1532 row has linear payload or reaches rho. The separately open P1533-style recoverable multiset intersection would be a different uninstantiated collision operation, not typed gamma-digit return.

## Proof track

Construct a scalar-blind nonzero elliptic character aggregate and prove typed digit recovery plus complete `lambda,mu<=0.45` outside the P1531/P1532/Gallant controls.

## Disproof track

Reduce every nonzero mode to a hidden character distinguisher, show orientation-free powers are scalar invariant, or prove character/batch payload or precision reaches exponent at least `0.50`.

## Positive and negative controls

- Positive control: finite-field Gauss sums with a supplied multiplicative-character index and independently checked Gross–Koblitz digits.
- Negative controls: shuffled character orientation, universal powers, P1531 independent Fourier modes, admitted P1532 row/recurrence routes, the separately open P1533 collision-resultant interface, pairings/torsion tables, rho, and BSGS.

## Quantitative promotion and falsification gates

This version is merged/rejected. Reopening requires exact scalar-blind digit recall on two generic families, zero orientation advice, no linear character payload, and `lambda,mu<=0.45`. Reduction to Gallant/P1531 or an admitted P1532 route, one orientation collision, or either exponent at least `0.50` falsifies it. A future P1533 collision-resultant success would require a new operation-level comparison and would not by itself validate gamma-digit return.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-221/gauss_digit_orientation_theorem.md`
- Prospective collision audit: `ideas/artifacts/ECDLP-IDEA-221/p1531_p1532_collision_audit.md`
- Prospective verifier: `ideas/artifacts/ECDLP-IDEA-221/independent_gauss_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-221/cost_analysis.md`

All paths are prospective; no artifact root exists.

## Interpretation boundary

This is novelty-unverified merged/rejected arithmetic-transfer analysis. Finite checks would be toy and projections heuristic and model-bound. A Gauss-sum identity, correct digit on a supplied character, relation, or toy scalar is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-221/gauss_digit_orientation_theorem.md` proving a scalar-blind nonzero mode outside Gallant/P1531/P1532 or proving that every admitted mode either erases or imports the hidden character.
