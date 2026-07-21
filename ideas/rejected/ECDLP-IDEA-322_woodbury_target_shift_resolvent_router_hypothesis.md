# ECDLP-IDEA-322 — Woodbury target-shift resolvent router

## Status and claim labels

- Class: `algebraic_algorithm`
- Risk band: `conservative`
- Top lane: `-`
- State: `merged_rejected_woodbury_update_assumes_source_resolvent_and_exact_backsolve`
- Cohort: `20260718-n`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: abandoned duplicate/control contract preserved at `ideas/rejected/contracts/ECDLP-EXP-CONTRACT-322_woodbury_target_shift_preflight.yaml`; retired `review_required`, unapproved, and zero-run
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a low-rank update identity, correct kernel, valid relation, or toy scalar is not an ECDLP break.

## Falsifiable hypothesis

There is a compact source-faithful resolvent `A(R)` for five-term elliptic decomposition such that every public target shift `R -> R+[c]P` is a bounded-rank update, Sherman–Morrison–Woodbury maintenance costs at most `N^0.25` per target, and kernel back-substitution returns exact signed factor points with complete campaign time and memory at most `N^0.45`.

## Mechanism-new operation

The screened operation is **assert a bounded-rank target-shift identity for an implicit source resolvent, use Woodbury only for off-hit inverse maintenance, derive a separate singular-Schur kernel lemma at relation hits, and back-substitute kernel vectors to exact factor points**. Woodbury is only a backend for a supplied invertible base matrix, supplied update factors, and a small invertible Schur complement. Here both mechanism-bearing inputs—the compact source-faithful resolvent and its exact point back-substitution—are the already-missing source representation and inverse; at a desired singular hit the inverse formula itself ceases to apply. Naming the target shift does not remove that obstruction. Natural factor-base restrictions can make the update full rank, while a point-faithful resolvent may already have `B^3=N^0.6` state. It therefore merges with the transition, boundary-response, and source-unranking controls in IDEAs 056, 071, 077, 194, and 267 rather than opening a new theorem-deferred gate.

## Assumptions

1. A target-independent implicit resolvent `A(R)` is constructible from the five factor decks without enumerating pair/triple states or a dense eliminant.
2. For every permitted mask shift, `A(R+[c]P)-A(R)=U_cV_c^T` has target-independent rank `O(1)` or exponent compatible with `q<=0.25`.
3. Maintained kernel data have a canonical all-strata inverse to exact signed factor points, not only endpoint membership.
4. Setup, rank updates, inversions, singular cases, back-substitution, output, relation rank, factor logs, descent, verification, and peak memory are charged.
5. The same frozen resolvent and update law serve known-log relation targets and fresh `Q+[t]P` targets.
6. The P1553 incidence arm uses prelogged pairwise-disjoint actual-point decks; colliding known targets are replaced, and blind-mask resampling or deck rebuilds are charged unless a globally confluent overlap-safe construction is proved.

## Semantic fingerprint

`implicit_source_resolvent_A_of_R | bounded_rank_public_target_shift | Sherman_Morrison_Woodbury_kernel_update | exact_factor_backsubstitution | blind_masked_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1478`, the exact compact one-transition norm whose first source-complete composition becomes dense quadratic state.
2. `inputs/ledger_inventory.json` — imported `P1434`, the missing public source-fiber generator and transposed target join.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`, the source-generative batch boundary.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1423-FULL-PHASE-NONLINEAR-GAP`, the aggregate low-displacement versus exact-source gap.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`, the explicit ancestry/state boundary.

The decisive live-ledger controls are `ledger/FINDING-PF-IC-001.md` entries
`ECFG-P1552-R1` and `ECFG-P1553-R1`: they identify the endpoint-only source
unranking operation that this supplied resolvent/backsolve merely renames. The
remaining succinct common-norm branch is already owned by P1513/`ECDLP-IDEA-121`
and its P1551 review; this record creates no successor lane.

## Closest primary literature

- Sherman and Morrison, [Adjustment of an inverse matrix corresponding to a change in one element of a given matrix](https://doi.org/10.1214/aoms/1177729893), gives inverse maintenance for a supplied rank-one update of an invertible matrix when its scalar denominator is nonzero; it does not recover a kernel at the singular relation hit.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), provides endpoint equations but no compact source-faithful resolvent or bounded-rank target-shift identity.

No checked source proves the required elliptic resolvent update, all-strata source back-substitution, or complete `N^0.45` campaign; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N`, five signed coloured decks with `B=N^(1/5)`, resolvent representation, base target, shift factors, singular-update rule, masks, and independent verifier.
2. Build `A(R_0)` and its off-hit inverse data without materializing pair/triple source tables; charge all setup and state.
3. For at least `B` independent known-log rows, apply only the frozen low-rank updates, invoke a separately proved singular-Schur kernel lift at each hit, back-substitute exact signed factor points, verify each relation, solve all factor logs with charged linear algebra, and independently verify them.
4. Apply the identical update and singular-hit lift to fresh masked targets `Q+[t]P` without target-trained factors or source advice; replace colliding known targets and charge every blind-mask resample or deck rebuild under the frozen disjoint-deck policy.
5. Substitute verified factor logs, remove masks, retain every singular/kernel ambiguity, and return all scalar candidates.
6. Accept only exact `[x]P=Q`, charging setup, every update, failures, output, rank, factor logs, descent, verification, and memory.

## Full rho/BSGS cost model

With setup `N^a,N^a_m`, factor base `N^beta` where `beta=1/5`, reciprocal relation and target densities `N^delta,N^delta_t`, one update and singular-hit computation excluding source emission `N^q,N^q_m`, independently verified rank amortization `N^r`, separately charged exact-source output `N^o`, ambiguity `N^u`, and factor-log linear algebra `N^ell,N^ell_m`,

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Here `0<=r<=o`: rank credit cannot exceed independently verified emitted-row output. The fixed `beta=0.20` gate requires `beta+delta+q-r+o<=0.45`, online `delta_t+q+o+u<=0.25`, all setup/state/factor-log terms at most `0.45`, and at least `B` independent rows. Pollard rho has expected time exponent `0.50` and memory exponent `0`; BSGS has time and memory exponents `0.50`.

## Likely fatal obstruction

Changing an elliptic endpoint changes every factor-base membership condition. In natural resultants, multiplication matrices, or pair-wedge incidence operators, this is not a bounded-rank coefficient update after restriction to the source decks. Even if an off-hit update is low rank, a desired relation makes the relevant matrix or Schur complement singular, outside the inverse formula; a separate exact kernel-to-point lemma is required. A point-faithful resolvent or backsolve can require `B^3` state, so fast inverse maintenance accelerates only an aggregate matrix while source recovery remains above rho.

## Proof track

Prove an explicit implicit `A(R)`, constant-rank update factors derived without source enumeration, off-hit inverse maintenance, a separate singular-Schur kernel theorem at relation hits, exact all-strata kernel-to-point back-substitution, sufficient independent rank, reusable factor logs, blind descent, per-target exponent at most `0.25`, and `lambda,mu<=0.45`.

## Disproof track

Prove target shifts have rank growing beyond the rectangle, that any source-faithful resolvent/back-substitution has `B^3` state or work, that kernel vectors lose point labels, or that either complete exponent is at least `0.50`.

## Positive and negative controls

- Positive: supplied low-rank-updated matrices with planted labelled singular hits must match a direct linear solve and independently verified source back-substitution; off-hit inverse checks are separate.
- Negative: equal-determinant/low-rank aggregate operators with different point sources must not yield preferred factors.
- Baselines: IDEAs 056/071/077/194/267, P1478, direct half-GCD/resultant work, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with a symbolic all-strata bounded-rank identity, source-free constructor, 1,000 independently verified rows and 100 blind descents per large future toy size, query exponent at most `0.25`, and complete `lambda,mu<=0.45`.
- Falsify this version if update rank/state/back-substitution reaches `B^3`, source labels are input, any admitted stratum fails, or either complete exponent reaches `0.50`.
- Values in `(0.45,0.50)` or unproved bit complexity are inconclusive and non-promoting.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-322/woodbury_source_resolvent_merge_receipt.md`
- `ideas/artifacts/ECDLP-IDEA-322/rank_update_collision_fixtures.json`
- `ideas/artifacts/ECDLP-IDEA-322/independent_woodbury_verifier.py`
- `ideas/artifacts/ECDLP-IDEA-322/cost_analysis.md`

## Interpretation boundary

This is preserved rejected merge evidence, not an algorithm or promotion. A correct low-rank identity, fast inverse update, relation, or toy scalar does not establish source-faithful ECDLP recovery or a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-322/woodbury_source_resolvent_merge_receipt.md` mapping every assumed resolvent, singular-Schur lift, and source backsolve to the P1513/P1551/P1552/P1553 and `ECDLP-IDEA-121` owners.
