# ECDLP-IDEA-209 — Simultaneous Hermite–Padé orbit denominator

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- Top lane: `conservative`
- State: `merged_rejected_low_recurrence_duplicates_ideas_006_011_070_or_p1530_tester`
- Cohort: `20260718-e`
- Evidence scale: primary-literature and semantic audit only; no experiment ran
- Contract posture: retired zero-run `review_required` theorem preflight
- Scale labels: every prospective finite check is `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a fitted recurrence, correct zero, or valid relation is not an ECDLP break.

## Falsifiable hypothesis

For generic signed factor base `F`, the translation-orbit vector built from `H_F(X)=prod_{A in F}(X-x(A))` and fixed sign companions has a target-uniform simultaneous Hermite–Padé approximant of degree at most `N^0.45`. A full-cycle zero decoder would identify exact factor points without scanning `N`, yielding factor logs and blind target descent below rho and BSGS.

## Mechanism-new operation

The claimed operation is **divisor-induced joint approximation plus certified full-cycle zero routing**, not a solver swap. It merges with IDEA-006/011/070 unless a generic-`F` theorem escapes elliptic-net recurrence, scalar-orbit period, and finite-state reverse-automaton controls. For exponent-coset `F`, independently audited P1530 makes it Gallant type-1 membership; its surviving partial elliptic-period type-2 label is a distinct successor whose direct evaluator is above rho.

## Assumptions

1. Public `E/F_p`, prime-order `G=<P>` of size `N`, generic target-independent `F` of size `B=N^beta`, and target `Q` are frozen.
2. `F` is not an exponent coset or known-scalar orbit, and `H_F`, companions, and samples cost at most `N^0.45`.
3. One approximant theorem holds on the full cyclic orbit through poles, repeats, and signs, not merely on a fitted prefix.
4. The decoder returns every zero index and exact point identity; samples, masks, output, rank, and memory are charged.

## Semantic fingerprint

`generic_factor_base_vanishing_polynomial | additive_translation_orbit_samples | simultaneous_Hermite_Pade_annihilator | full_cycle_zero_index_decoder | factor_logs_and_blind_target`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-H679`, the compact cyclic-sequence hypothesis.
2. `inputs/ledger_inventory.json` — imported `P1474`, the orbit-sampling/recurrence boundary.
3. `inputs/ledger_inventory.json` — imported `P1477`, the dense serial-state control.
4. `inputs/ledger_inventory.json` — imported `ECFG-MX-1478`, the structured orbit-model collision.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1479`, the compact-feature/source-orientation barrier.

## Closest primary literature

- Beckermann and Labahn, [A uniform approach for the fast computation of matrix-type Padé approximants](https://doi.org/10.1007/BF02141914), gives algorithms for supplied approximation data, not a short elliptic-orbit recurrence.
- Ward, [Memoir on elliptic divisibility sequences](https://doi.org/10.2307/2371930), is the nearest genuine elliptic recurrence control.
- Gallant, [Finding discrete logarithms with a set orbit distinguisher](https://eprint.iacr.org/2010/370), supplies the type-1 set-orbit distinguisher prior art identified by the P1530 literature correction.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies endpoint relations without a full-cycle zero router.

No checked source proves the generic-`F` recurrence and decoder. The late P1530 independent audit passes the scoped producer/prior-art reconstruction, makes P1530 terminal inconclusive, and isolates a different partial elliptic-period type-2 successor. It is used only as a collision/control boundary, and novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `F`, `H_F`, companions, approximant order, masks, and verifier.
2. For known-log endpoints, build charged prefixes and prove one full-cycle joint approximant.
3. Enumerate all decoded zero indices, map them to signed factor points, and verify one-term rows.
4. Obtain `B` independent diagonal rows, solve and verify all factor logs.
5. Run the identical query on fresh `Q+[t]P`; from a zero compute each candidate `x=±log(A)-k-t`.
6. Preserve ambiguity and accept only candidates satisfying `[x]P=Q`, charging setup, samples, output, rank, time, and memory.

## Full rho/BSGS cost model

Rho costs `N^(1/2+o(1))` time; BSGS costs that time and memory. For setup `N^a,N^a_m`, reciprocal base/target densities `N^delta,N^delta_t`, query plus exact zero inverse `N^q,N^q_m`, rank gain `N^r`, output/ambiguity `N^o,N^u`, and factor-log work `N^ell,N^ell_m`,

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Here one base query may output `B`, so `r=beta` only when all output is charged. Promotion requires both exponents at most `0.45`.

## Likely fatal obstruction

Generic translation observables have near-full period and linear complexity; the divisor of `H_F` accumulates `N` translates. A short recurrence is likely an existing elliptic-net/orbit/finite-state control, Gallant/P1530 type-1 membership, the P1531 partial-period type-2 control, or fitted-prefix overreach. Evaluating `H_F` does not predict unseen zeros.

## Proof track

Prove a generic-`F`, full-cycle joint-degree bound and exact zero decoder independent of source logs, then audit every exponent through blind descent.

## Disproof track

Show linear complexity at least `N^0.5`, one missed zero, special-orbit dependence, reduction to IDEA-006/011/070 or P1530, or complete exponent at least `0.50`.

## Positive and negative controls

- Positive control: manufactured low-recurrence vector sequences with known full-cycle zeros.
- Negative controls: random periodic sequences, Ward/IDEA-006 nets, IDEA-011 orbit invariants, IDEA-070 reverse automata, P1477 dense state, P1530/Gallant type-1 membership, the P1531 partial elliptic-period type-2 label, dense tables, rho, and BSGS.

## Quantitative promotion and falsification gates

This version is merged/rejected. Reopening requires two preregistered generic-`F` families, 100% full-cycle zero recall, zero false indices, degree/sample/query/memory exponents at most `0.45`, no point/orbit table, and `lambda,mu<=0.45`. Any semantic reduction above or exponent at least `0.50` falsifies it.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-209/simultaneous_pade_recurrence_theorem.md`
- Prospective collision audit: `ideas/artifacts/ECDLP-IDEA-209/p1530_and_orbit_collision_audit.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-209/fixtures.json`
- Prospective verifier: `ideas/artifacts/ECDLP-IDEA-209/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-209/cost_analysis.md`

All paths are prospective; no artifact root exists.

## Interpretation boundary

This is novelty-unverified merged/rejected algorithm analysis. Finite checks would be toy and projections heuristic and model-bound. A recurrence, zero decoder, relation, or toy scalar is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-209/simultaneous_pade_recurrence_theorem.md` proving a generic-`F` full-cycle joint approximant outside IDEA-006/011/070, Gallant/P1530 type-1, and the P1531 type-2 period control, or recording the semantic merge without fitting toy recurrences.
