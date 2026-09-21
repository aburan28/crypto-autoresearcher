# ECDLP-IDEA-153 — Deligne–Lusztig anisotropic-torus character tomography

## Status and claim labels

- Class: `mechanism`
- Risk band: `high-risk`
- State: `merged_rejected_class_function_scalar_orbit_tomography`
- Cohort: `20260718-a`
- Evidence scale: character-theory and semantic audit only; no experiment ran
- Contract posture: rejected archival record; no execution contract
- Scale labels: every prospective measurement is `toy`; complexity claims are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a correct Deligne–Lusztig character value, sparse toy spectrum, relation, or toy scalar is not an ECDLP break.

## Falsifiable hypothesis

There is a public scalar-blind embedding of elliptic source or scalar-orbit states into an anisotropic maximal torus of a finite reductive group such that a sub-rho family of Deligne–Lusztig virtual-character evaluations uniquely determines the exact signed factor-base sources, or the scalar of `Q=[x]P`, without sweeping all torus characters or solving a hidden DLP in the torus.

## Mechanism-new operation

The proposed operation is **anisotropic-torus Deligne–Lusztig character tomography**. Embed the public relation or scalar-orbit object into `T^F` inside `G^F`, evaluate selected virtual characters `R_T^G(theta)`, and invert their trace vector using the Weyl/Frobenius structure of the anisotropic torus.

Semantic review rejects the current form. Deligne–Lusztig characters are class functions and generally retain conjugacy or Weyl-orbit information, not a canonical source label. Sweeping all characters of `T^F` is ordinary full Fourier inversion. A single faithful cyclic character can separate torus elements in principle, but efficiently constructing, evaluating, typing, and inverting its value from a scalar-blind elliptic embedding relocates the order-`N` DLP. No selected bounded-complexity Deligne–Lusztig family has the required source-injectivity/readout theorem.

## Assumptions

1. Public `E/F_p`, prime-order `<P>` of order `N`, target `Q=[x]P`, and factor base `F` of size `B=N^beta` are frozen.
2. The reductive group, Frobenius, anisotropic torus, embedding, character family, normalizations, and evaluation algorithms are derived from public data without `x` or source tuples.
3. The character vector is injective on every admitted source fiber or scalar orbit after explicitly charged Weyl/Frobenius ambiguity.
4. Character construction and evaluation do not enumerate `T^F`, all torus characters, all scalar shifts, or all factor-base tuples.
5. Inverting the trace vector returns exact source identities and signs, not merely a conjugacy class or orbit statistic.
6. Group construction, character evaluation, coefficient fields, Fourier inversion, retries, output, linear algebra, masked descent, ambiguity, and memory are charged.

## Semantic fingerprint

`elliptic_source_or_scalar_orbit | finite_reductive_group_embedding | anisotropic_maximal_torus | Deligne_Lusztig_virtual_character_vector | exact_source_tomography`

The novelty gate is a scalar-blind embedding plus a provably sparse injective character family. Ordinary additive or multiplicative characters, full character tables, conjugacy-class statistics, supplied torus exponents, and post-hoc character selection are duplicates or controls.

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-H664`, where exact curve-derived additive-character phases remain controls without a source or scalar generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-P1422-EXACT-CHARACTER-FILTER-CONTROL`, the exact deterministic character-kernel positive control.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1422-ADDITIVE-CHARACTER-NO-PROMOTION`, where character kernels retain full pair-state rank and recall-preserving truncation fails.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1423-FULL-PHASE-NONLINEAR-GAP`, where scalar phase and entrywise character matrices remain full-state.
5. `inputs/ledger_inventory.json` — imported `P1475`, where canonical residual-character buckets provide no polynomial support concentration.

## Closest primary literature

- Deligne and Lusztig, [Representations of reductive groups over finite fields](https://annals.math.princeton.edu/1976/103-1/p03), construct representations and virtual characters from Frobenius-stable maximal tori; they do not provide source-labelled elliptic tomography or a sparse scalar inverse.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), supplies the neighboring elliptic relation equations but no anisotropic-torus character decoder.

No checked primary source supplies the public elliptic embedding, sparse injective character family, or complete sub-rho descent. Novelty remains unverified outside the rejected semantic family.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,Q,F,B,beta`, relation arity, signs, reductive group, Frobenius, torus, embedding, character set, masks, and independent verifier.
2. Construct the embedding and prove it is scalar blind, efficiently computable, and compatible with exact elliptic source addition.
3. For known-log targets `R_j=[r_j]P`, evaluate the frozen Deligne–Lusztig character vector, invert it to every exact signed factor-base tuple, and verify each tuple directly.
4. Preserve conjugacy collisions, Weyl/Frobenius ambiguity, false sources, missing sources, exceptional elements, and failed character evaluations.
5. Collect `B+sigma` verified relation rows of rank `B`, solve factor-base logarithms, and verify them independently.
6. For fresh masks `R_t=Q+[t]P`, apply the identical embedding and tomography, substitute factor logs, and subtract `t`.
7. Retain all ambiguity candidates and accept only `x` satisfying `[x]P=Q`.
8. Charge group and torus construction, character count, representation dimensions, trace evaluation, inversion, retries, output, linear algebra, descent, and peak memory.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` time with constant-state memory; BSGS costs `N^(1/2+o(1))` time and memory. Let `B=N^beta`; group, torus, embedding, and character-family derivation cost time/memory be `N^a,N^a_m`; reciprocal relation and target densities be `N^delta,N^delta_t`; trace evaluation, tomography, source inversion, and verification per query be `N^q,N^q_m`; relation output and Weyl/target ambiguity exponents be `o,u`; and factor-log linear algebra be `N^ell,N^ell_m`. Then

`lambda=max(a,beta+delta+q+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

The number and degree of characters, cohomological or representation construction, coefficient fields, conjugacy resolution, Fourier inversion, all outputs, and masks are charged. A sparse-looking formula whose evaluation sweeps `T^F` fails. Toy spectra are heuristic and model-bound.

## Likely fatal obstruction

Deligne–Lusztig characters are class functions, so they identify conjugacy data rather than canonical torus elements or elliptic sources. Weyl and Frobenius actions add ambiguity. Although a faithful one-dimensional cyclic character may separate elements, reading its exponent is the torus DLP; no public scalar-blind embedding transports elliptic addition into a typed torus coordinate and inverts it below rho without collapsing to known homomorphic information or relocating that DLP.

## Proof track

Construct the public embedding; prove a sub-rho character family is injective on all admitted source and target states modulo explicitly bounded ambiguity; give a source-position inverse; bound representation construction and evaluation; and derive `lambda,mu<=0.45` through factor-log calibration and masked descent.

## Disproof track

Exhibit source-distinct states with identical vectors for the selected bounded-complexity character family; prove class-function or Weyl/Frobenius ambiguity exceeds the gate; reduce the scalar-blind embedding, typed readout, or inversion to a torus DLP, full hidden-shift Fourier transform, or existing additive-character control; or derive either complete exponent at least `0.5`.

## Positive and negative controls

- Small finite reductive groups with supplied torus elements and exhaustive full character tables.
- Full Fourier inversion on `T^F`, explicitly charged as a non-promoting correctness control.
- Weyl- and Frobenius-conjugate torus elements that must collide under class functions.
- The exact P1422 additive-character kernels and their no-promotion companions.
- Random character subsets matched in cardinality to the proposed sparse family.
- Exhaustive toy elliptic fibers, rho, BSGS, and independent source/scalar verification.

## Quantitative promotion and falsification gates

The current formulation is rejected. Reopening requires a scalar-blind embedding, a proved injective family of at most `N^0.45` characters with total construction and evaluation below `N^0.45`, exact source inversion, and formal `lambda,mu<=0.45`. Any future toy preflight must recover `100%` of exhaustive sources with `0` false outputs across all frozen exceptional strata. Falsify on one class-function collision outside the declared ambiguity, full character-table enumeration, supplied torus exponent, post-hoc character choice, a torus-DLP reduction, or either complete exponent at least `0.5`.

## Artifact plan

- Archival class-function no-go: `ideas/artifacts/ECDLP-IDEA-153/deligne_lusztig_tomography_no_go.md`
- Frozen reductive-group and torus fixtures: `ideas/artifacts/ECDLP-IDEA-153/fixtures.json`
- Prospective character evaluator: `ideas/artifacts/ECDLP-IDEA-153/character_tomography.sage`
- Independent collision/source verifier: `ideas/artifacts/ECDLP-IDEA-153/verify_sources.py`
- Complete character and cost receipt: `ideas/artifacts/ECDLP-IDEA-153/cost_analysis.md`

All paths are prospective. No contract or experiment is authorized.

## Interpretation boundary

This is preserved rejected, novelty-unverified evidence. Every prospective finite computation is toy, and all complexity claims are heuristic and model-bound. A correct character value, sparse toy spectrum, recovered relation, or toy scalar establishes only scoped correctness, not a generic ECDLP improvement or breakthrough.

## Exactly one next executable action

1. Archive the class-function, Weyl/Frobenius ambiguity, and full-character-count boundary in `ideas/artifacts/ECDLP-IDEA-153/deligne_lusztig_tomography_no_go.md` without opening an experiment contract.
