# ECDLP-IDEA-271 — Cyclotomic trace source digits

## Status and claim labels

- Class: `homotopy_arithmetic_transfer`
- Risk band: `high_risk`
- Top lane: `-`
- State: `merged_rejected_cyclotomic_trace_forgets_prime_to_p_source_orientation`
- Cohort: `20260718-j`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: none
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a trace class, Frobenius fixed point, valid relation, recovered digit, or toy scalar is not an ECDLP break.

## Falsifiable hypothesis

A target-uniform algebraic object attached to `E,P,Q` has a cyclotomic trace from algebraic K-theory to topological cyclic homology whose Frobenius-Tate equalizer components expose compressed digits of `x` in `Q=[x]P`.  Decoding those components would return exact factors or the scalar below rho and BSGS.

## Mechanism-new operation

The screened operation is **compile the marked endpoint into K-theory, apply the cyclotomic trace to THH/TC, and decode source digits from restriction/Frobenius equalizer data**.  This homotopy-arithmetic transform is not an ordinary character table or a solver change.  TC is an additive, often p-completed approximation to K-theory; a functorial construction from the unmarked finite subgroup is insensitive to prime-to-`p` generator orientation.  Conversely, an input ring, module, or endomorphism algebra whose trace distinguishes every source point has already materialized the source deck or a point-faithful representation.  It merges with trace/character and transfer negatives after construction and return costs are charged.

## Assumptions

1. There is a canonical target-uniform ring, category, or module built from public `E,P,Q,N` without a source enumeration.
2. Its cyclotomic trace preserves prime-to-characteristic scalar information rather than only additive or p-complete invariants.
3. Frobenius/Tate equalizer components admit a compressed, exact inverse to source factors or `x`.
4. Object construction, spectra or finite models, precision, trace maps, output, factor logs, descent, verification, time, and peak memory are charged.

## Semantic fingerprint

`prime_field_ECDLP | K_theory_to_TC_cyclotomic_trace | Frobenius_Tate_equalizer | source_digit_decode | exact_factor_return`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-NR-1051`, the trace-like invariant and source-separation negative.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1479`, the transformed-spectrum output boundary.
3. `inputs/ledger_inventory.json` — imported `ECFG-MX-1478`, the representation-state and materialization control.
4. `inputs/ledger_inventory.json` — imported `ECFG-RT-1476`, the return-map requirement for transformed data.
5. `inputs/ledger_inventory.json` — imported `ECFG-P1470`, the source-coordinate and point-separation gate.

## Closest primary literature

- Nikolaus and Scholze, [On topological cyclic homology](https://doi.org/10.4310/ACTA.2018.v221.n2.a1), gives the Frobenius and homotopy-fixed-point formulation of TC.
- Bhatt, Morrow, and Scholze, [Topological Hochschild homology and integral p-adic Hodge theory](https://arxiv.org/abs/1802.03261), links THH/TC to p-adic filtrations and exposes the completion regime.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies the finite-field factor-base baseline.

No checked source gives a cyclotomic-trace inverse for prime-order ECDLP or a sub-rho source return; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the instance, source-object functor, cyclotomic-trace model, prime/completion, observables, factor base, masks, and verifier.
2. Construct the ring/category/module and its K-theory-to-TC data for public marked points without enumerating source points.
3. On known-log endpoints, decode trace components and return exact signed factor points, recording every ambiguous lift and output class.
4. Verify relations, collect full-rank rows, solve and verify all factor logs.
5. Apply the identical frozen trace and decoder to fresh masked targets `Q+[t]P`.
6. Return a full factor decomposition or scalar residue, remove the mask, and verify the original endpoint equation.
7. Accept only exact `x` with `[x]P=Q`, including complete construction, spectral, precision, output, descent, and peak-memory receipts.

## Full rho/BSGS cost model

Pollard rho has expected time exponent `1/2`; BSGS has time and memory exponents `1/2`.  Let setup time and memory be `N^a,N^a_m`, factor-base size be `N^beta`, reciprocal relation and target success densities be `N^delta,N^delta_t`, one object/trace/equalizer/decode attempt cost `N^q,N^q_m`, independent-rank gain be `N^r`, trace-output multiplicity be `N^o`, inverse ambiguity be `N^u`, and factor-log completion be `N^ell,N^ell_m`.  Then

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every generator, cell or finite surrogate, cyclotomic structure map, completion digit, fixed-point calculation, trace component, failed inverse, source branch, factor log, verifier step, and live byte is charged.

## Likely fatal obstruction

Cyclotomic trace is designed as an additive and p-adic approximation to K-theory, not as a faithful coordinate system on a cyclic group of unrelated prime order `N`.  Any target-uniform unmarked construction is invariant under automorphisms of the cyclic source, so it cannot name the coefficient relative to `P`.  A ring or module enriched until its TC classes separate all `[x]P` must carry at least the point-faithful source action or equivalent deck.  The proposed digits therefore vanish/alias or are already paid for in the input state.

## Proof track

Give a canonical compact source object, prove its cyclotomic trace separates prime-to-`p` scalar classes, construct an exact return, and certify both complete exponents at most `0.45`.

## Disproof track

Prove p-completion/additivity erases the scalar, show generator invariance or trace collisions, prove the separating object has source-deck dimension/state, or derive either complete exponent at least `0.50`.

## Positive and negative controls

- Positive control: a supplied finite ring endomorphism with known p-primary K/TC class and known digit label.
- Negative controls: prime-to-`p` cyclic groups under generator relabeling, Morita-equivalent unmarked objects, random trace components, explicit character tables, point-faithful regular representations, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires a compact scalar-separating trace, exact all-strata factor return, full relation rank, blind masked-target descent, and complete `lambda,mu<=0.45`.  Trace collisions, p-primary-only retention, a source-deck input, output/state at least `N^0.50`, or either exponent at least `0.50` falsifies this version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-271/cyclotomic_trace_source_theorem.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-271/fixtures.json`
- Prospective independent verifier: `ideas/artifacts/ECDLP-IDEA-271/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-271/cost_analysis.md`

All four paths are prospective; no artifact root exists and no experiment ran.

## Interpretation boundary

This is a novelty-unverified merged/scoped-negative homotopy-transfer proposal.  Every finite surrogate would be toy and projections heuristic and model-bound.  A computed trace class or toy scalar does not establish a generic-prime ECDLP improvement or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-271/cyclotomic_trace_source_theorem.md` proving scalar separation and exact return or the completion/invariance/source-state obstruction.
