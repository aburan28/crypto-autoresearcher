# ECDLP-IDEA-302 — Homological-perturbation source router

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- Top lane: `-`
- State: `merged_rejected_contraction_and_homotopy_require_source_cells`
- Cohort: `20260718-m`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: `none`
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a correct transferred differential, surviving homology class, valid relation, or toy source tuple is not an ECDLP break.

## Falsifiable hypothesis

A target-independent contraction of a universal elliptic source complex can absorb endpoint and mask data as a perturbation, and the Basic Perturbation Lemma can transfer the perturbed differential and homotopy to a sub-rho effective complex whose canonical surviving generators are exact signed factor tuples for relation collection and blind descent.

## Mechanism-new operation

The screened operation is **freeze a contraction `(C,d) <-> (H,0)`, insert an endpoint-dependent perturbation `Delta`, sum the homological-perturbation series, and lift surviving effective generators through the transferred homotopy to exact points**. This is narrower than a generic `A_infinity` decomposition and distinct in name from IDEA-073: the claimed gain must come specifically from reusing one contraction across endpoints. It still merges with IDEAs 069, 073, 088, 152, and 176 because constructing the contraction and homotopy requires source cells, the transfer series expands source paths, and homology generators are noncanonical modulo boundaries.

## Assumptions

1. A target-independent sparse complex and contraction are constructible from `E`, the factor base, and public masks without enumerating source tuples.
2. Every endpoint perturbation satisfies the nilpotence/convergence conditions with effective state below `N^0.50`.
3. Effective generators lift biconditionally to every signed, repeated, singular, and infinity source stratum.
4. Contraction construction, transfer series, output, relation rank, factor logs, target descent, verification, time, and peak memory are charged.

## Semantic fingerprint

`universal_source_complex | frozen_contraction | endpoint_differential_perturbation | transferred_homotopy | exact_factor_lift | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `TRANSFER-H003`, the supplied extension/source-complex control.
2. `inputs/ledger_inventory.json` — imported `TRANSFER-H004`, the exact source-return obligation after a homological transfer.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`, the public source-fiber generator and batch boundary.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`, the lossless source-edge state boundary.
5. `inputs/ledger_inventory.json` — imported `P1478`, the exact compact-transition identity and dense-composition control.

## Closest primary literature

- Gugenheim, Lambe, and Stasheff, [Perturbation theory in differential homological algebra II](https://doi.org/10.1215/ijm/1255987784), transfers supplied contraction data under a perturbation; it does not construct an elliptic source contraction.
- Chuang and Lazarev, [On the perturbation algebra](https://doi.org/10.1016/j.jalgebra.2018.10.032), gives a conceptual multiplicative perturbation framework and explicit transferred structures.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), supplies endpoint equations without source-labelled chain data.

No checked source supplies the endpoint-uniform contraction, canonical exact source lift, or complete sub-rho ECDLP path; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N`, factor base, universal complex, contraction, masks, conventions, and an independent verifier.
2. For random known-log endpoints, compile only the endpoint perturbation and transfer it through the frozen contraction.
3. Lift every accepted effective generator to exact signed factor points and independently verify the elliptic relation.
4. Collect independent rows, solve the complete factor-log system, and verify every recovered log.
5. Apply the identical transfer and lift to fresh masked targets `Q+[t]P` without target-trained choices.
6. Substitute verified factor logs, remove the mask, preserve all ambiguity, and return scalar candidates.
7. Accept only exact `[x]P=Q`, charging contraction, series terms, generators, branches, failures, rows, logs, descent, verification, and live bytes.

## Full rho/BSGS cost model

Let setup time and memory be `N^a,N^a_m`, factor-base size `N^beta`, reciprocal relation and target densities `N^delta,N^delta_t`, one transfer/lift attempt `N^q,N^q_m`, independent-rank gain `N^r`, output `N^o`, target ambiguity `N^u`, and factor-log completion `N^ell,N^ell_m`. Then

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Here `q` includes perturbation transfer, exact lift, and independent verification; `o` includes every enumerated branch; `u` is residual target ambiguity only. Pollard rho has expected time exponent `1/2` and negligible memory; BSGS has time and memory exponents `1/2`.

## Likely fatal obstruction

The perturbation lemma transfers an already supplied contraction; it does not find one. A source-faithful contraction names source cells or an equivalent basis, while forgetting that basis leaves homology classes only up to boundaries and change of generators. Expanding `(1-Delta h)^-1` can enumerate all source paths, so the operation either imports the source deck or restores its work/state.

## Proof track

Prove a target-independent contraction of sub-rho description, a uniformly truncated transfer series, and a canonical all-strata generator-to-point biconditional, then prove full relation rank, factor-log completion, blind target descent, and `lambda,mu<=0.45`.

## Disproof track

Prove that any source-complete contraction or transferred lift contains one independent generator/path per source component, or exhibit one valid source stratum whose class is merged or basis-dependent; account for resulting `N^0.50`-or-worse state, output, or work.

## Positive and negative controls

- Positive: supplied toy complexes with labelled cells and a known finite perturbation must transfer and lift exactly.
- Negative: random basis changes preserving homology must destroy any uncharged point labels; source-labelled contractions and explicit path expansions are charged controls.
- Baselines: dense chain reduction, IDEAs 069/073/088/152/176, rho, and BSGS under matched accounting.

## Quantitative promotion and falsification gates

- Promote only after independent proofs and future frozen tests return every source stratum, at least 1,000 independently verified rows and 100 blind descents at each large size, with both complete exponents at most `0.45`.
- Falsify this version if contraction state, transfer expansion, output, or ambiguity reaches `N^0.50`; if one stratum is absent; or if the source lift depends on labelled cells or target advice.
- Values strictly above `0.45` and below `0.50` are inconclusive and non-promoting.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-302/perturbation_source_biconditional.md`
- `ideas/artifacts/ECDLP-IDEA-302/fixtures.json`
- `ideas/artifacts/ECDLP-IDEA-302/independent_verifier.py`
- `ideas/artifacts/ECDLP-IDEA-302/cost_analysis.md`

## Interpretation boundary

This record is a preserved semantic merge, not a lower bound for every implicit homological representation. A correct transfer or relation does not supply source construction, rank, factor logs, blind descent, or a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-302/perturbation_source_biconditional.md` proving either a compact endpoint-uniform contraction/lift theorem or the scoped source-cell materialization obstruction before any code or run.
