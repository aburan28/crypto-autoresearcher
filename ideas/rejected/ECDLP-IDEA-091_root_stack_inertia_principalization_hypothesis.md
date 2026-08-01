# ECDLP-IDEA-091 — Root-stack inertia principalization descent

## Status and claim labels

- Class: `representation`
- Risk band: `representation-changing`
- State: `rejected_fixed_inertia_no_go`
- Evidence scale: `toy` stack-theoretic boundary only; no experiment or timing was run
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a valid root stack, Picard identity, or principal divisor is not an ECDLP break.

## Falsifiable hypothesis

Rooting `E` along the public factor-base divisor creates a stack `X` whose inertia characters give persistent atom labels. A relation divisor that is nonprincipal on the coarse curve becomes principal in a ray/stacky Picard group; sparse factorization of its principalizing function into inertia-labelled primes then recovers exact factor-base sources. Coarse norm of those sources, followed by the same construction on masked targets, yields a complete descent with total relation, rank, output, and memory costs below rho.

## Mechanism-new operation

The proposed operation is **root-stack inertia labelling followed by ray-Picard principalization, sparse inertia factorization, and coarse norm descent**. A fixed cover, torsor, ray-class coordinate, principal-divisor solver, or explicit point-label dictionary is a control. Survival requires inertia to label generic factor atoms before their discovery, not merely record already selected branch divisors, and it must do so without root order, Picard tables, or character dictionaries of `N`-scale.

## Assumptions

1. `E(F_q)` contains a prime-order subgroup `<P>` of order `N`, and `F={F_1,...,F_B}` is a public factor base with `B=N^(beta+o(1))`.
2. A frozen root construction `X=sqrt[r_1,...,r_B]{(E;F_1,...,F_B)}` or an explicitly compressed equivalent is defined over the base field with all inertia orders and fields charged.
3. Each accepted elliptic relation divisor maps to a ray/stacky Picard class that can be principalized without solving an equivalent DLP.
4. Factorization of the principalizing function returns a sparse list of exact inertia-labelled stacky primes biconditional with the signed factor-base tuple.
5. Coarse norm preserves point identity and sign and introduces only a bounded, explicitly enumerable kernel.
6. Stack construction, inertia dictionaries, principalization, factor output, `B+sigma` rows, rank, factor logs, blind descent, and peak memory are fully charged.

## Semantic fingerprint

`factor_base_root_stack | inertia_character_atom_labels | ray_Picard_principalization | sparse_inertia_factorization | coarse_norm_descent`

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `TRANSFER-H008`, the closest open representation-changing Prym/Jacobian smoothness lane.
2. `ledger/FINDING-PF-IC-001.md` — imported `TRANSFER-NR-054`, where a direct principalization/descent route is blocked by the absence of a rational maximal-isotropic subgroup.
3. `ledger/FINDING-PF-IC-001.md` — imported `PO96`, the geometry-only saturation and alternate-principal-form gate that forbids relation claims before representation verification.
4. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H642`, the structured-coordinate barrier for factor-base predicates and recursive addition circuits.
5. `ledger/FINDING-PF-IC-001.md` — imported `P1479`, where tested compact public feature spaces do not contain the factor logs.

## Closest primary literature

- Cadman, [Using stacks to impose tangency conditions on curves](https://arxiv.org/abs/math/0312349), defines the root construction along a divisor; the supplied arXiv record is withdrawn in favor of its journal version and contains no ECDLP source-factorization algorithm.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), gives the relation/decomposition boundary that stack principalization must improve.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://doi.org/10.1007/3-540-69053-0_18), gives the generic square-root boundary when inertia and Picard operations reveal no non-generic scalar information.

No checked source proves that fixed root-stack inertia identifies generic elliptic factor atoms or supports sub-rho blind descent. Novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,F`, `B=N^beta`, all root divisors and orders, the stacky/ray Picard representation, principalization algorithm, factorization rule, norm convention, masks, and independent coarse-source verifier.
2. For a known random scalar `u`, map `R=[u]P` and its elliptic relation divisor to `X`, principalize the class, factor the resulting function into sparse inertia-labelled primes, norm to signed points in `F`, and replay their sum to `R`.
3. Collect at least `B+sigma` independently accepted source rows with the same frozen stack; retain failed principalizations, generic unlabelled primes, kernel ambiguities, duplicate rows, full factor output, and character-table costs.
4. Form the relation matrix over `Z/NZ`, satisfy the preregistered full-rank threshold, solve all factor logs, and verify every `[log_P(F_i)]P=F_i` independently.
5. Commit a random mask `r` for a blind `Q=[x]P`, set `T=Q+[r]P`, and apply the identical stack, principalization, sparse factorization, and coarse-norm path without target-specific roots or characters.
6. Combine the verified factor logs of `T`, resolve only explicitly bounded norm-kernel ambiguity, unmask `x=(sum_i epsilon_i log_P(F_i))-r mod N`, and verify `[x]P=Q`.

## Full rho/BSGS cost model

Pollard rho has time exponent `1/2` and negligible-table memory; BSGS has time and memory exponents `1/2`. Let `beta` be factor-base exponent, `gamma` aggregate root-order/character-dictionary exponent, `s` stack and Picard setup, `k` principalization plus sparse factorization, `delta,delta_t` reciprocal relation/descent density exponents, `o` exact atom output, and `ell` rank/factor-log solving. The complete time exponent is `lambda=max(gamma,s,beta+delta+k+o,ell,delta_t+k+o,beta)`. Peak memory is `mu=max(beta,gamma,mu_Picard,mu_factorization,mu_linear_algebra,o)`. Product root orders, ray-class tables, per-factor characters, and branch dictionaries are counted at full size; a table reused only inside this instance is not free preprocessing.

## Likely fatal obstruction

Root-stack inertia is supported on the chosen branch divisor. With fixed inertia orders it labels only those already named branch points and contributes a bounded local character at each; generic relation atoms away from the branch support remain unlabelled, while the identity of a factor-base branch point was already present in the public dictionary. Principalization does not factor the resulting function or select its source atoms. Increasing root orders or adjoining enough roots to encode global source combinations moves the missing information into a ray/Picard character dictionary whose order or product is `N`-scale. The proposal therefore merges with cover, torsor, principal-divisor, and explicit-label lanes rather than removing their source-discovery obstruction.

## Proof track

Construct a base-field root stack of provably sub-rho description, prove that its inertia characters distinguish every accepted source atom before factor discovery, give a DLP-free ray-Picard principalization and sparse factorization algorithm, and bound `B+sigma` relation collection, rank, logs, blind descent, output, and memory by `lambda,mu<1/2`.

## Disproof track

Prove inertia support is confined to preselected branch divisors; exhibit distinct generic source tuples with identical inertia/Picard data; reduce principalization plus sparse factorization to the original elliptic decomposition problem; or lower-bound the necessary root-order/character dictionary by exponent at least `1/2`.

## Positive and negative controls

- Positive: root stacks on tiny curves with explicitly known branch divisors, inertia characters, and Picard groups.
- Positive: planted principal divisors supported entirely on the rooted factor-base points.
- Negative: equal-degree divisors with generic support away from all root loci.
- Negative: fixed-inertia stacks under permutations of factor-base point identities that preserve the inertia multiset.
- Negative: direct principal-divisor and ray-class factorization on the coarse curve with identical output charging.
- Negative: masked blind targets for which only a Picard equality, not exact source factors, is recovered.

## Quantitative promotion and falsification gates

The theorem gate requires a biconditional inertia-character-to-source theorem, DLP-free principalization, exact sparse factorization, and symbolic `gamma,lambda,mu<0.50`. Any future empirical promotion requires at least `B+sigma` accepted rows per size, full rank, every factor log verified, at least 100 independent masked descents, and upper 95% bounds `gamma<=0.45`, `lambda<=0.45`, and `mu<=0.45`. Falsify this mechanism if any generic accepted atom lacks a unique inertia label, if growing roots or dictionaries have lower-bound exponent at least `0.50`, or if principalization returns only a relation certificate without source factors.

## Artifact plan

- Fixed-inertia no-go: `ideas/artifacts/ECDLP-IDEA-091/root_stack_inertia_no_go.md`
- Stack schema: `ideas/artifacts/ECDLP-IDEA-091/root_stack_schema.yaml`
- Source verifier design: `ideas/artifacts/ECDLP-IDEA-091/verify_inertia_sources.py`
- Cost worksheet: `ideas/artifacts/ECDLP-IDEA-091/cost_model.json`
- Future runs, if separately approved: `ideas/artifacts/ECDLP-IDEA-091/runs/<run-id>/`

## Interpretation boundary

This rejected representation is toy, heuristic, model-bound, and novelty-unverified. The rejection covers fixed inertia as an atom decoder and growing roots whose dictionaries are fully charged; it does not reject all stack, cover, or transfer mathematics. A correct Picard principalization, inertia character, coarse norm, or relation certificate is not a source-complete factorization, full-rank log solution, blind descent, better-than-rho result, or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-091/root_stack_inertia_no_go.md` proving that fixed root inertia is supported only at the chosen branch divisor and charging the character/root-order growth needed to distinguish generic source combinations.
