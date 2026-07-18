# ECDLP-IDEA-114 — Punctured-elliptic Magnus path signature

## Status and claim labels

- Class: `representation`
- Risk band: `high-risk`
- State: `merged_rejected_path_oracle`
- Top lane: `-`
- Evidence scale: semantic screen only; no run; any future quotient check would be `toy`
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a valid iterated integral, Magnus coefficient, path identity, relation, or toy scalar is not an ECDLP break.

## Falsifiable hypothesis

Puncture `E` at a target-independent divisor containing the factor base and lift elliptic addition paths to a finite nilpotent quotient of the punctured curve's fundamental group. A truncated Magnus/Chen signature is hypothesized to factor uniquely into source-loop signatures for signed factor-base points, while remaining computable from the public endpoint alone. If the quotient and inverse have sub-rho size, they could emit full-rank relation rows and descend a masked target below rho and BSGS.

## Mechanism-new operation

The operation is **replace the abelian endpoint by a canonical nonabelian path torsor, compute a truncated Magnus signature, and factor that signature into exact factor-base loops**. This is distinct as a proposed noncommutative lift, but it merges with the occupied unipotent-Albanese, augmentation-ideal, Massey, and factor-word lanes because the needed path is not determined by the endpoint. Supplying the path supplies the source word; discarding it returns the abelian group sum or aggregate iterated-integral data.

## Assumptions

1. `E(F_p)` has a public prime-order subgroup `<P>` of order `N=p^(1+o(1))`; `F={F_1,...,F_B}` is deterministic with `B=N^beta`, and relation arity `m` is frozen.
2. A target-independent puncture divisor and tangential basepoint define a finite nilpotent etale, crystalline, or de Rham path quotient over a controlled extension.
3. Every public endpoint `R` has a canonical endpoint-only path class independent of an unknown scalar expression or source decomposition.
4. Truncated Magnus/Chen coefficients retain ordered signed source indices and multiplicities and have an exact public factorization inverse.
5. Relation and masked-target arms use identical path, truncation, normalization, factorization, and ambiguity rules.
6. Quotient construction, periods, extensions, path selection, coefficient size, factorization, source output, rank, factor logs, descent, verification, and memory are charged.

## Semantic fingerprint

`punctured_elliptic_path_torsor | finite_nilpotent_quotient | Magnus_Chen_signature | exact_source_loop_factorization | blind_descent`

The removal test requires an endpoint-canonical path quotient and source inverse that do not encode the witness. A chosen source path, Fox/Magnus linearization of a supplied word, unipotent Albanese coordinate, Massey invariant, or factor-word rewriting backend is a duplicate/control.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H642`, the structured-coordinate barrier for any compact public coordinate that claims to retain source ancestry.
2. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H664`, the closest attempt to derive exact phase data from a public elliptic subtraction circuit.
3. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`, where exact public transition/value matrices remain full rank and do not expose a compact source block.
4. `ledger/FINDING-PF-IC-001.md` — imported `P1477`, the dense forward/backward path-state boundary when endpoint ancestry is retained.
5. `ledger/FINDING-PF-IC-001.md` — imported `P1478`, the exact local identity whose source-faithful composition becomes dense.

## Closest primary literature

- Kim, [The unipotent Albanese map and Selmer varieties for curves](https://arxiv.org/abs/math/0510441), gives nonabelian path torsors and iterated-integral coordinates in Diophantine geometry, not an endpoint-only finite-field source factorization.
- Chen, [Iterated path integrals](https://doi.org/10.1090/S0002-9904-1977-14320-6), establishes the signature framework and its path dependence; it does not canonically recover a path word from an elliptic endpoint.
- Luo, [The elliptic KZB connection and algebraic de Rham theory for unipotent fundamental groups of elliptic curves](https://arxiv.org/abs/1710.07691), gives explicit characteristic-zero de Rham structure for once-punctured elliptic curves, not an endpoint-only finite-field source inverse.
- Cao and Terasoma, [The motivic fundamental group of a punctured elliptic curve and algebraic cycles](https://arxiv.org/abs/2407.00692), resolve motivic structures via Schur complexes but do not construct the proposed ECDLP path selector.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic comparison boundary.

No checked primary source gives a canonical endpoint-only punctured-elliptic path whose finite signature factors into arbitrary factor-base sources. Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,F,B,m`, punctures, tangential basepoint, path category, nilpotent depth, coefficient field, signature basis, factorization order, and exceptional-path policy.
2. Construct the finite path quotient without factor logs or source enumeration and prove endpoint canonicity under all accepted charts.
3. For a public output `R`, compute its signature, factor it into every exact signed source tuple in `F`, and independently verify membership and elliptic sum.
4. Apply the frozen procedure to known `R_j=[r_j]P`; retain verified rows until exactly `B+sigma` have rank `B`.
5. Solve factor-base logarithms and verify every `[log_P(F_i)]P=F_i`.
6. Mask `Q` with fresh `t`, compute `R_t=Q+[t]P`, and apply the identical canonical-path, signature, factorization, and source checks.
7. Substitute factor logs, subtract `t`, retain all factorization ambiguities, and accept only `[x]P=Q`.
8. Preserve noncanonical choices, monodromy, period failures, signature collisions, coefficient growth, duplicate rows, and rejected candidates.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` time with constant-state memory; BSGS costs `N^(1/2+o(1))` time and memory. Let quotient/period plus factor-base construction time and memory be `N^a,N^a_m`; serialized signature basis and working state be `N^s,N^s_m`; `B=N^beta`; reciprocal relation and target densities be `N^delta,N^delta_t`; complete per-endpoint path/signature/source-factorization plus exact elliptic verification work be `N^k`; source and target ambiguity exponents be `o,u`; and linear-algebra time and memory be `N^ell,N^ell_m`. Then

`lambda=max(a,s,beta+delta+k+o,ell,delta_t+k+o+u,beta)`

and

`mu=max(a_m,s_m,beta+o,ell_m,u)`.

Every path representative, iterated-integral coefficient, period, factor word, failed conditional, output tuple, row, and candidate is charged. A short signature with an `N`-scale path dictionary receives no credit.

## Likely fatal obstruction

An elliptic endpoint determines only an abelian homology class. Nonabelian signatures distinguish paths, not endpoints. There is no canonical reason the source word used in one addition expression should be the path chosen from the endpoint; different decompositions give different paths with the same endpoint. Making the choice canonical requires solving a word/section problem equivalent to selecting the hidden scalar or source tuple, while quotienting away path dependence destroys the desired provenance.

## Proof track

Define an endpoint-canonical finite path section, prove a biconditional signature/source factorization on complete fibers, and bound all construction, output, rank, factor-log, blind-descent, and memory exponents by `0.45`.

## Disproof track

Exhibit two source paths with the same endpoint but incompatible signatures, prove no endpoint-natural section respects elliptic addition, or show that any source-faithful quotient/path table has exponent at least `1/2`. A supplied source word or target-scalar-selected path also disproves the mechanism.

## Positive and negative controls

- Free and nilpotent groups with known words and independently computed Magnus expansions.
- Punctured toy curves with planted canonical paths.
- The same endpoints under two distinct source words, which must expose path dependence.
- Unipotent-Albanese, augmentation-ideal, Massey, and factor-word controls matched for output.
- Exhaustive ordinary toy-curve relations and blind masked targets.
- Matched rho and BSGS baselines.

## Quantitative promotion and falsification gates

No active promotion gate remains. A versioned successor must prove endpoint canonicity, exact source factorization, and `a,a_m,s,s_m,k,o,u,lambda,mu<=0.45` without a path/source table. Any toy preflight would require zero independent signature/source/sum/factor-log/descent errors across 20 curves at four sizes, 1,000 rows and 100 blind descents at each of the two largest sizes. Falsify after one canonicality contradiction, one source collision, or a lower 95% exponent bound `>=0.50`.

## Artifact plan

- Endpoint-path obstruction proof: `ideas/artifacts/ECDLP-IDEA-114/endpoint_path_no_go.md`
- Frozen path quotient specification: `ideas/artifacts/ECDLP-IDEA-114/path_signature_spec.yaml`
- Prospective toy signature code: `ideas/artifacts/ECDLP-IDEA-114/magnus_signature.sage`
- Independent source verifier: `ideas/artifacts/ECDLP-IDEA-114/verify_path_sources.py`
- Complete cost analysis: `ideas/artifacts/ECDLP-IDEA-114/analysis.md`

## Interpretation boundary

This merged/rejected record is toy, heuristic, model-bound, and novelty-unverified. Its path-dependence argument is scoped to the proposed signature factorization, not a universal ECDLP lower bound. A correct iterated integral, path identity, relation, or toy scalar is not a below-rho algorithm or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-114/endpoint_path_no_go.md` proving whether any endpoint-natural section into the chosen finite path quotient can be compatible with elliptic addition and still distinguish exact factor-base source words.
