# ECDLP-IDEA-089 — Grothendieck-residue idempotent splitter

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- State: `merged_rejected`
- Evidence scale: `toy` symbolic boundary only; no experiment or timing was run
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; exact quotient-algebra splitting, a valid relation, or a verified source lift is not an ECDLP break.

## Falsifiable hypothesis

For each known-scalar relation target `R=[u]P`, let `A_R` be the finite relation algebra cut out by the factor-base constraints and elliptic summation equations. An implicitly computed Grothendieck-residue functional gives a nondegenerate dualizing pairing on `A_R`; primitive idempotents recovered from that pairing split `A_R` into source atoms without constructing a dense quotient basis. If atom evaluations lift to exact factor-base points with total setup, relation collection, rank, descent, output, and memory exponents below `1/2`, this would yield a complete index-calculus path.

## Mechanism-new operation

The proposed operation is **implicit dualizing-residue pairing followed by primitive-idempotent splitting and atom-evaluation lift**. Its intended novelty is source extraction from algebra duality rather than a new polynomial-system solver. The operation begins only after the zero-dimensional relation algebra exists. Replacing a Groebner, resultant, rational-univariate, SAT, or Krylov backend by a residue/idempotent routine while leaving that algebra, its length, and its source output unchanged is a solver substitution and therefore a duplicate/control, not a new obstruction-removing mechanism.

## Assumptions

1. `E(F_q)` contains a prime-order subgroup `<P>` of order `N`, and the public factor base `F={F_1,...,F_B}` has `B=N^(beta+o(1))` exactly indexed points.
2. A frozen arity-`m` relation ideal for `R` is zero-dimensional, radical or separably decomposable, and its geometric atoms are in bicondition with exact signed factor-base tuples summing to `R`.
3. A residue functional and its pairing can be applied without first materializing a basis, multiplication matrices, a dense resultant, or all solutions of `A_R`.
4. Primitive idempotents can be isolated output-sensitively, and each idempotent evaluates to an auditable tuple of factor-base indices and signs.
5. Relation-algebra construction, multiplicities, rejected atoms, source lifting, `B+sigma` accepted rows, rank, factor-log solving, target descent, output, and peak memory are charged.
6. The relation and descent procedures are scalar-blind apart from public known masks; no target-trained selector, hidden discrete-log label, or uncharged fixed-curve table is allowed.

## Semantic fingerprint

`zero_dimensional_relation_algebra | implicit_dualizing_residue_pairing | primitive_idempotent_split | atom_evaluation_lift | blind_descent`

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `P1477`, where materialized serial-S3 backward state polynomials are dense and miss the required query exponent.
2. `ledger/FINDING-PF-IC-001.md` — imported `P1478`, whose exact one-transition norm composes into a dense quadratic state object.
3. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1428-SHARED-ROW-NORM-NO-PROMOTION`, where shared union-root recovery loses source labels and remains above the gate.
4. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-P1428-EXACT-SHARED-UNION-CONTROL`, the exact source-resolved shared-union control whose symbolic reduction still does not meet the cost gate.
5. `ledger/FINDING-PF-IC-001.md` — imported `P1480`, the staged solver/completeness negative for a frozen five-term membership encoding.

## Closest primary literature

- Mourrain, [Bézoutian and quotient ring structure](https://doi.org/10.1016/j.jsc.2004.11.010),
  relates Bézoutian constructions to quotient-algebra structure; it does not make the
  relation algebra or its primitive-atom output sub-rho.
- Rouillier, [Solving Zero-Dimensional Systems Through the Rational Univariate Representation](https://doi.org/10.1007/s002000050114), gives an exact representation of zero-dimensional solutions; it does not make construction of the quotient algebra or enumeration of its atoms free.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), supplies the relation system whose complete source recovery and cost must still be paid.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://doi.org/10.1007/3-540-69053-0_18), supplies the generic square-root boundary when the algebraic interface leaks no exploitable representation-specific structure.

No checked source establishes an implicit sub-rho residue-to-source splitter for prime-field elliptic relation algebras. Novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N`, the factor base `F` of size `B=N^beta`, relation arity, masks, ideal construction, residue oracle, split policy, and independent source verifier.
2. For known random scalars `u`, form `R=[u]P`, construct `A_R`, apply the residue pairing, split primitive idempotents, lift atom evaluations to signed tuples in `F`, and verify that each tuple sums to `R`.
3. Retain exactly source-labelled rows until at least `B+sigma` independently accepted relations exist; record all attempts, algebra lengths, split failures, multiplicities, and duplicate rows.
4. Build the sparse relation matrix over `Z/NZ`, prove the preregistered rank threshold (full factor-base rank, modulo any explicitly fixed normalization), solve every factor log `log_P(F_i)`, and independently verify `[log_P(F_i)]P=F_i`.
5. For a blind target `Q=[x]P`, choose and commit a random mask `r`, set `T=Q+[r]P`, and run the identical frozen algebra/residue/source path without target-chosen parameters.
6. Combine the verified factor logs from a decomposition of `T`, unmask `x=(sum_i epsilon_i log_P(F_i))-r mod N`, enumerate any explicitly bounded sign ambiguity, and verify `[x]P=Q`.

## Full rho/BSGS cost model

Pollard rho has time exponent `1/2` and negligible-table memory, while BSGS has time and memory exponents `1/2`. Let `beta` be the factor-base exponent, `s` relation-algebra setup exponent, `d` the quotient-length/materialization exponent, `r` the residue/idempotent-split exponent, `delta` and `delta_t` the reciprocal accepted-relation and blind-descent probability exponents, `o` the source-output exponent, and `ell` sparse-rank/factor-log exponent. The complete time exponent is `lambda=max(s,d,beta+delta+s+r+o,ell,delta_t+s+r+o,beta)`. Peak memory is `mu=max(beta,mu_algebra,mu_pairing,mu_split,mu_linear_algebra,o)`. Any quotient basis, multiplication matrix, primitive-idempotent list, or atom list of size `N^d` is charged at exponent at least `d`; preprocessing used by only this ECDLP instance is not amortized away.

## Likely fatal obstruction

Grothendieck residues and primitive idempotents reorganize a finite algebra that has already been presented; they do not construct the relation algebra or reduce its length. Computing the residue pairing normally requires a quotient basis, multiplication data, a univariate representation, or equivalent elimination output, and splitting into primitive idempotents emits at least one object per atom. If the dense algebra or its atom set is the recorded obstruction, the proposed step begins after that cost and returns the same source output. It therefore merges with the existing dense-elimination and solver-substitution lanes rather than removing their obstruction.

## Proof track

Give a scalar-blind black-box representation of `A_R`, prove that residue pairing and primitive-idempotent isolation use sub-rho queries and memory without a dense basis, prove a biconditional idempotent-to-factor-tuple lift, and bound relation probability, `B+sigma` collection, rank, factor logs, blind descent, output, and verification under `lambda,mu<1/2`.

## Disproof track

Reduce residue evaluation to construction of a quotient basis or rational-univariate representation of the same asymptotic size; prove idempotent output is linear in the full atom count; exhibit two source tuples with the same available residue data; or show that the purported speedup changes only the solver after the dense relation algebra has been constructed.

## Positive and negative controls

- Positive: square-free planted zero-dimensional algebras supplied directly in Chinese-remainder form, where primitive idempotents and source labels are known.
- Positive: complete tiny elliptic relation ideals with exhaustive tuples and independent point-addition replay.
- Negative: nonradical algebras with colliding residue signatures and nilpotent components.
- Negative: matched random zero-dimensional systems with the same length and degree profile but no elliptic source map.
- Negative: rational-univariate, dense resultant, and explicit multiplication-matrix baselines charged from raw equations.
- Negative: masked blind targets with permuted source labels and no target-specific selector.

## Quantitative promotion and falsification gates

The theorem gate requires a complete input-to-idempotent complexity proof, zero missing or spurious source atoms on exhaustive toy fixtures, and a source-biconditional verifier. Any future empirical promotion would require at least `B+sigma` accepted rows at each preregistered size, full required rank, all factor logs verified, at least 100 independent masked descents, and upper 95% bounds `lambda<=0.45` and `mu<=0.45`. Falsify this mechanism if algebra construction is unchanged from a dense baseline, if any source atom is unresolved, or if a proved lower bound or lower 95% scaling bound gives `max(d,r,o,lambda,mu)>=0.50`.

## Artifact plan

- Boundary theorem: `ideas/artifacts/ECDLP-IDEA-089/residue_splitter_boundary.md`
- Algebra interface: `ideas/artifacts/ECDLP-IDEA-089/relation_algebra_schema.yaml`
- Source verifier design: `ideas/artifacts/ECDLP-IDEA-089/verify_idempotent_sources.py`
- Cost worksheet: `ideas/artifacts/ECDLP-IDEA-089/cost_model.json`
- Future runs, if separately approved: `ideas/artifacts/ECDLP-IDEA-089/runs/<run-id>/`

## Interpretation boundary

This merged rejection is toy, heuristic, model-bound, and novelty-unverified. It records a semantic and cost boundary, not an executed negative experiment. A correct residue, a complete idempotent split, or a valid relation certifies only the represented algebra and source equality; it is not full-rank factor-log recovery, blind target descent, a better-than-rho result, or a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-089/residue_splitter_boundary.md` proving that the residue/idempotent phase consumes an already constructed relation algebra and lower-bounding its explicit atom output by the number of source components.
