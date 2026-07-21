# ECDLP-IDEA-150 — Moore-syndrome rank-metric source decoder

## Status and claim labels

- Class: `algebraic-representation`
- Risk band: `representation-changing`
- Top lane: `representation-changing`
- State: `deferred_needs_public_moore_embedding_and_source_biconditional`
- Cohort: `20260718-a`
- Evidence scale: literature and semantic audit only; no experiment ran
- Contract posture: retired `review_required` preflight under `ideas/rejected/contracts/`; zero runs permitted
- Scale labels: every prospective measurement is `toy`; complexity claims are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a valid Moore syndrome, decoded planted error, recovered relation, or toy scalar is not an ECDLP break.

## Falsifiable hypothesis

For a fixed five-source prime-field elliptic relation fiber, there is a public scalar-blind extension-field encoding under which every accepted signed factor-base tuple becomes a bounded-rank error and the public target determines its Moore syndrome. A Gabidulin-style unique or bounded-list rank-metric decoder then returns the exact factor-base identities and signs without enumerating the relation fiber, materializing a dense resultant, or consulting a post-hoc source dictionary above the sub-rho budget.

## Mechanism-new operation

The proposed operation is **elliptic relation-to-Moore-syndrome compilation followed by rank-metric source decoding**. Freeze an extension `K/F_p`, a public encoding `phi` of signed factor-base points, and a Moore parity-check operator `H`. The required identity is

`H e(S_1,...,S_5)=s(R) iff sum_i epsilon_i S_i=R`,

where `e` has bounded rank over a specified subfield and decoding `s(R)` recovers the exact source positions, values, and signs.

This differs from replacing Gröbner, resultant, or bit-vector solvers: the claimed new operation is a proved scalar-blind reduction of the elliptic source fiber itself to a correctable rank-metric syndrome. A Moore matrix constructed only after enumerating sources, a decoder that returns an unlabeled error-support subspace, or dictionary matching over all factor-base combinations is a duplicate or control.

## Assumptions

1. Public `E/F_p`, prime-order `<P>` of order `N=p^(1+o(1))`, target `Q=[x]P`, and factor base `F` of size `B=N^beta` are frozen.
2. The extension field, basis, Moore operator, point encoding, syndrome map, signs, infinity convention, and repeated-point policy are derived from public data without knowing source tuples or `x`.
3. Every admitted relation maps to rank at most `t`, while the code distance supports unique decoding or a fully charged bounded list.
4. Decoder output inverts biconditionally to exact factor-base identities; a recovered base-field support subspace without source positions is insufficient.
5. Syndrome construction does not expand the five-source Semaev fiber, a degree-`Theta(B^3)` intermediate, or a table of all rank supports.
6. Extension arithmetic, code construction, syndrome formation, decoding, list size, source output, relation retries, factor-log linear algebra, blind descent, verification, and peak memory are charged.

## Semantic fingerprint

`five_source_elliptic_fiber | public_extension_field_embedding | target_determined_Moore_syndrome | bounded_rank_error | exact_position_and_sign_decoder`

The removal test is a public target-to-syndrome identity and exact source biconditional. A rank-metric decoder fed an already materialized source word, an unlabeled rank support, a solver substitution, or a source dictionary exceeding the cost gate is not mechanism-new.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `P1434`, the missing public source-fiber generator and target join that the Moore syndrome must construct rather than assume.
2. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H642`, the structured-coordinate barrier requiring a compact coordinate to retain exact source ancestry.
3. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`, where exact transposed value matrices retain full rank and expose no useful fixed tensor compression.
4. `ledger/FINDING-PF-IC-001.md` — imported `P1478`, where an exact sparse one-transition norm becomes dense under source-complete composition.
5. `ledger/FINDING-PF-IC-001.md` — imported `P1479`, where tested public feature spaces do not contain factor-log orientation.

## Closest primary literature

- Gabidulin, [Theory of codes with maximum rank distance](https://www.mathnet.ru/eng/ppi967), constructs Moore-matrix maximum-rank-distance codes and their decoding structure; it does not compile elliptic relation fibers into source-labelled syndromes.
- Gaborit, Ruatta, and Schrek, [On the complexity of the Rank Syndrome Decoding problem](https://arxiv.org/abs/1301.1026), analyze generic and algebraic rank-syndrome decoding; they assume the rank-syndrome instance and do not supply the proposed elliptic source biconditional.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), supplies neighboring elliptic relation equations but no Moore-syndrome source decoder.

No checked primary source supplies the target-determined syndrome, exact factor-base-position inverse, or complete sub-rho descent. Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,Q,F,B,beta`, five-source signs and ordering, extension field, subfield, basis, Moore operator, decoder radius, masks, and independent verifier.
2. Construct the target-independent point encoder and prove the target-to-syndrome identity without enumerating `F^5`, valid source tuples, or rank-support tables.
3. For each known-log target `R_j=[r_j]P`, compute `s(R_j)`, decode every bounded-list error, invert each error to exact signed factor-base points, and verify curve membership and elliptic addition.
4. Preserve all misses, list collisions, support-subspace ambiguities, repeated points, infinity cases, false positions, and failed targets.
5. Repeat until `B+sigma` independently verified relation rows have rank `B`; solve the factor-base logarithms and verify every recovered log by scalar multiplication.
6. For fresh public masks `t`, form `R_t=Q+[t]P`, run the identical syndrome and decoder, and substitute verified factor logs into every emitted decomposition.
7. Remove the mask by subtracting `t`, retain every ambiguity candidate, and accept only `x` satisfying `[x]P=Q`.
8. Report setup, extension arithmetic, syndrome and decode costs, retries, list/output size, linear algebra, masked descent, time, and peak memory against rho and BSGS.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` time with constant-state memory; BSGS costs `N^(1/2+o(1))` time and memory. Let `B=N^beta`; one-time extension/code/representation derivation cost time/memory be `N^a,N^a_m`; reciprocal relation and target densities be `N^delta,N^delta_t`; syndrome formation, rank decoding, source inversion, and exact verification per query be `N^q,N^q_m`; relation-source output and target ambiguity exponents be `o,u`; and factor-log linear algebra be `N^ell,N^ell_m`. Then

`lambda=max(a,beta+delta+q+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Thus `lambda` is the complete time exponent and `mu` the complete peak-memory exponent. Serialized representation size and resident state are folded into `a,a_m`; query-time syndrome construction and decoding are folded into `q,q_m`. Extension degree, base-field bit operations, Moore matrix construction, decoding lists, position recovery, retries, source output, and verification are charged. A polynomial-time decoder in a representation of size `N^(1/2)` or larger does not beat rho. Toy decoding slopes are heuristic and model-bound.

## Likely fatal obstruction

Gabidulin decoding recovers an error value and its low-dimensional rank support, not automatically the positions of elliptic factor-base points that produced it. A public map making elliptic addition linear enough to determine the syndrome is likely either a homomorphism, which exposes no new information on a prime cyclic subgroup, or a representation whose coordinates and position dictionary materialize the original source fiber. Generic elliptic source tuples need not have bounded rank in any scalar-blind extension basis, and forcing bounded rank after seeing the tuple is post-hoc encoding.

## Proof track

Construct the public encoder and Moore operator; prove the syndrome equivalence in both directions for every admitted signed, repeated, and infinity stratum; prove a uniform correctable rank bound; prove exact recovery of positions and signs from decoder output without a super-gate dictionary; and derive fixed `epsilon>0` with `lambda,mu<=1/2-epsilon` through relation calibration and masked target descent.

## Disproof track

Prove that the syndrome identity implies a homomorphic or scalar-linear map on `<P>`; exhibit two distinct source fibers with identical syndromes; show generic relation errors exceed the decoding radius; show rank support fails to determine source positions; reduce position recovery to enumerating `Omega(B^3)` states or the original relation fiber; or derive `lambda>=0.5` or `mu>=0.5`.

## Positive and negative controls

- Planted Gabidulin errors with known positions, values, rank, and syndromes.
- Planted elliptic toy relations whose source encoder is deliberately supplied, separated from the construction claim.
- Random full-rank matrices matched in dimensions to detect benefits coming only from standard rank decoding.
- Shuffled factor-base labels and basis changes to detect post-hoc position dictionaries.
- Exhaustive toy elliptic fibers, including signs, repeats, infinity, and syndrome collisions.
- Direct enumeration, P1478-style composed states, rho, BSGS, and independent source/scalar verification.

## Quantitative promotion and falsification gates

Remain deferred. Promotion requires a checked public syndrome theorem, exact position-and-sign biconditional, and formal `lambda,mu<=0.45`. A later approved toy preflight must obtain `100%` source recall, `0` false tuples, and complete multiplicity recovery on at least three frozen curves and all exceptional strata; the decoded list must remain at most `N^0.05`, with every list element charged. Falsify on one missed valid source, one unreported false source, post-hoc basis or label selection, rank above the decoder radius, source-position lookup above `N^0.45`, or either complete exponent at least `0.5`.

## Artifact plan

- Homomorphism gate: `ideas/artifacts/ECDLP-IDEA-150/moore_syndrome_homomorphism_gate.md`
- Frozen embedding specification: `ideas/artifacts/ECDLP-IDEA-150/embedding_spec.md`
- Frozen extension/code fixtures: `ideas/artifacts/ECDLP-IDEA-150/fixtures.json`
- Independent source/scalar verifier: `ideas/artifacts/ECDLP-IDEA-150/independent_verifier.py`
- Complete cost receipt: `ideas/artifacts/ECDLP-IDEA-150/cost_analysis.md`
- Retired zero-run contract: `ideas/rejected/contracts/ECDLP-EXP-CONTRACT-150_moore_syndrome_rank_metric_source_decoder_preflight.yaml`

All paths are prospective except the retired contract record. The contract remains `review_required`; zero runs are permitted.

## Interpretation boundary

This is a deferred, representation-changing, novelty-unverified proposal. Every eventual finite test is toy, and all asymptotic expectations are heuristic and model-bound until the encoder theorem and complete cost proof exist. Correct rank decoding, a valid relation, or a recovered toy scalar establishes only scoped correctness, not a generic ECDLP improvement or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-150/moore_syndrome_homomorphism_gate.md` proving or refuting whether any public target-to-syndrome identity factors through a homomorphism or scalar-linear map before authorizing a decoder run.
