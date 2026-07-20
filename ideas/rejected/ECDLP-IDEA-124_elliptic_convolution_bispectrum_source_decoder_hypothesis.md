# ECDLP-IDEA-124 — Elliptic-convolution bispectrum source decoder

## Status and claim labels

- Class: `higher-order-spectral`
- Risk band: `high-risk`
- State: `rejected_bispectrum_recovers_aggregate_signal_not_relation_sources`
- Evidence scale: information-flow and literature preflight only; no experiment ran
- Scale labels: any future computation would be `toy`; all cost claims are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; phase recovery, an exact convolution value, a valid relation, or a toy scalar is not an ECDLP break.

## Falsifiable hypothesis

A third-order elliptic convolution invariant of the public factor-base indicator and target translate determines a source-labelled five-fold convolution fiber, so bispectrum phase synchronization can decode every signed factor-base tuple below rho without enumerating pair or triple states. The claim is falsified if the invariant determines only the already-public indicator up to group symmetries or if different source fibers have the same bispectrum.

## Mechanism-new operation

The proposed operation is **source-labelled elliptic bispectrum inversion**: compute selected third-order Fourier products on the prime-order subgroup, synchronize their phases, and use cross-target constraints to lift the recovered phase to exact five-source tuples. It would be new only if a theorem maps a sub-rho set of bispectral coefficients biconditionally to ordered source decompositions and charges every ambiguity and output.

The preflight rejects the declared operation. Standard bispectrum inversion recovers a signal up to translation under support/nonvanishing assumptions. Here the factor-base signal is already public, while the unknown is a decomposition inside a five-fold convolution coefficient. Triple correlation aggregates all contributing triples and does not retain their ancestry. Adding source backpointers or enough cross-moments to split them restores the explicit relation fiber.

## Assumptions

1. `E(F_p)` has a public prime-order subgroup `<P>` of order `N=p^(1+o(1))`, target `Q=[x]P`, and a public signed factor-base indicator `f` of support `B=N^beta`.
2. Characters of the subgroup can be evaluated or represented without knowing discrete logarithms of arbitrary points.
3. A sub-rho set of third-order invariants determines not merely `f` up to translation but every source-labelled atom contributing to `f^{*5}(R)`.
4. Zero Fourier coefficients, translation/reflection symmetries, repeated points, signs, infinity, and multiplicities have a canonical scalar-blind resolution.
5. Phase synchronization and tuple recovery do not use an explicit large-prime table, pair/triple state, or post-hoc selector.
6. Fourier evaluation, coefficient selection, synchronization, ambiguity, source output, factor logs, blind descent, verification, and memory are charged.

## Semantic fingerprint

`elliptic_group_convolution | third_order_bispectrum | phase_synchronization | fivefold_source_ancestry | exact_tuple_decoder`

The removal test is a theorem that selected third-order invariants expose exact five-source ancestry below rho. Additive-character scoring, ordinary Fourier inversion of the public indicator, full phase matrices, aggregate convolution counts, or source tables are duplicates or controls.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1422-ADDITIVE-CHARACTER-NO-PROMOTION`, where tested additive-character kernels have full pair-state rank and recall-preserving truncations remain too large.
2. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1423-FULL-PHASE-NONLINEAR-GAP`, where scalar rational-phase and character matrices remain full rank; bispectrum helps only if its nonlinear invariant preserves sources.
3. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H664`, which derives exact phases from the rational addition circuit but leaves the complete nonlinear source inverse open.
4. `ledger/FINDING-PF-IC-001.md` — imported `P1479`, where tested public linear features do not contain factor logs; phase recovery cannot smuggle in unknown logarithmic coordinates.
5. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1479`, which records the exact failure of canonical sparse subgroup-`x` factor logs to lie in the tested feature spaces and blocks a feature-only descent.

## Closest primary literature

- Bendory, Boumal, Ma, Zhao, and Singer, [Bispectrum Inversion with Application to Multireference Alignment](https://arxiv.org/abs/1705.00641), recover cyclic signals from bispectral information under signal assumptions; they do not split a convolution coefficient into labelled elliptic sources.
- Pinilla, Mishra, and Sadler, [Unique Bispectrum Inversion for Signals with Finite Spectral/Temporal Support](https://arxiv.org/abs/2111.06479), prove recovery results from finitely supported measurements; the recovered object is a signal, not its five-fold convolution ancestry.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), supplies the neighboring elliptic decomposition relation but no bispectral source decoder.

No checked primary source proves the required labelled-convolution inverse or complete sub-rho ECDLP path. Novelty remains unverified; the aggregate version is rejected.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,Q,F,B,beta`, signed factor-base indicator, character convention, selected bispectral coefficients, zero-frequency policy, and target masks.
2. Compute the selected third-order invariants from public curve operations without first obtaining subgroup scalar coordinates or enumerating pair/triple states.
3. Synchronize phases and apply the claimed nonlinear lift to enumerate every signed five-source atom of the target convolution coefficient with multiplicity.
4. Independently verify curve membership, factor-base membership, and elliptic sum for every emitted tuple; preserve collisions, missing atoms, and symmetries.
5. Repeat for known multiples until `B+sigma` verified relation rows have rank `B`, charging every coefficient and failed target.
6. Solve and independently verify all factor-base logarithms.
7. Apply the identical blind invariant and decoder to `Q+[t]P`, substitute factor logs, subtract `t`, and retain every candidate.
8. Accept only `[x]P=Q` and serialize Fourier, phase, source, rank, time, output, and peak-memory receipts.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` time with constant-state memory; BSGS costs `N^(1/2+o(1))` time and memory. Let `B=N^beta`; invariant setup time/memory be `N^a,N^a_m`; selected bispectrum payload and synchronization state be `N^c,N^c_m`; reciprocal relation and target densities be `N^delta,N^delta_t`; phase recovery, source splitting, and exact verification per query be `N^k`; source and target ambiguity exponents be `o,u`; and factor-log linear-algebra time/memory be `N^ell,N^ell_m`. Then

`lambda=max(a,c,beta+delta+k+o,ell,delta_t+k+o+u,beta)`

`mu=max(a_m,c_m,beta+o,ell_m,u)`.

All Fourier coefficients, character evaluation, phase synchronization, zeros, cross-target measurements, source atoms, failed targets, relation rows, factor logs, and blind candidates are charged. An FFT over the full order-`N` subgroup costs exponent one, and an explicit `B^2` pair table costs exponent `2beta`.

## Likely fatal obstruction

The bispectrum is an invariant of a signal under translation; it is not an ancestry-preserving factorization of its convolution powers. For public `f`, recovering `f` again provides no new relation source. A value of `f^{*5}(R)` is the sum of all accepted tuples, and phase products aggregate those tuples. Homometric or symmetry-related signals and zero spectral components add ambiguity, but even unique signal recovery does not identify which terms contribute to one target coefficient. Exact splitting needs higher-order labelled moments or backpointers whose payload approaches the relation state.

## Proof track

Historic survival would require a source-biconditional theorem from a sub-rho selected bispectrum, characters computable without hidden discrete logs, complete treatment of zero spectra and symmetries, and `lambda,mu<=0.45` through blind descent. Standard signal-recovery theorems stop at the already-public factor-base indicator, so this proof track fails for the declared operation.

## Disproof track

Construct two labelled relation fibers with identical selected bispectra but different source tuples; show the decoder output is invariant under a source permutation that changes ancestry; prove character evaluation requires the unknown scalar coordinate; or show complete invariant/source payload has exponent at least `0.5`. Any one is sufficient.

## Positive and negative controls

- Cyclic signals satisfying published nonvanishing/support assumptions, where inversion up to translation is a positive signal-recovery control.
- Homometric, zero-spectrum, translated, and reflected signal pairs with known ambiguity.
- The public factor-base indicator before and after inversion, demonstrating that signal recovery alone adds no source information.
- Exhaustive toy five-fold elliptic convolution fibers with independently enumerated tuples.
- Frozen additive-character and full-phase matrices from the ledger as matched negatives.
- Blind known-log targets and matched rho/BSGS baselines with an independent source/scalar verifier.

## Quantitative promotion and falsification gates

This record is rejected. Historic promotion required a proved selected-bispectrum/source biconditional; zero false and `100%` recalled exhaustive toy tuples including all symmetries; no hidden scalar coordinates or pair table; and `lambda,mu<=0.45`. Falsify on any identical-invariant/different-source pair, recovery of only the public signal or an aggregate count, missed multiplicity, post-hoc backpointer, or time/memory exponent at least `0.5`.

## Artifact plan

- Information-flow rejection gate: `ideas/artifacts/ECDLP-IDEA-124/bispectrum_source_gate.md`
- Prospective ambiguity fixtures: `ideas/artifacts/ECDLP-IDEA-124/ambiguity_fixtures.json`
- Prospective selected-bispectrum evaluator: `ideas/artifacts/ECDLP-IDEA-124/bispectrum.py`
- Independent source verifier: `ideas/artifacts/ECDLP-IDEA-124/verify_sources.py`
- Complete cost worksheet: `ideas/artifacts/ECDLP-IDEA-124/cost_analysis.md`

These are prospective paths only; no artifact or experiment was created.

## Interpretation boundary

This is a rejected, novelty-unverified aggregate-invariant proposal. The complexity model is heuristic and model-bound, and any future check would be toy. The rejection does not preclude every nonlinear Fourier method; it closes ordinary bispectrum/phase recovery without a new exact source-ancestry operation. No generic ECDLP improvement or breakthrough is claimed.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-124/bispectrum_source_gate.md` formalizing the map from labelled five-source fibers to selected bispectra and exhibit an identical-invariant/different-source counterexample before any implementation is considered.
