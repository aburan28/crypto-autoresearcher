# ECDLP-IDEA-140 — de Rham–Witt torsion residue

## Status and claim labels

- Class: `mechanism`
- Risk band: `high-risk`
- Top lane: `-`
- State: `rejected_prime_to_p_de_rham_witt_no_go`
- Cohort: `20260717-h`
- Evidence scale: exact algebraic scope audit; no experiment ran
- Contract posture: no contract; execution is not authorized
- Scale labels: any future finite test would be `toy`; costs are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a nonzero function residue, correct Witt identity, or recovered toy scalar is not an ECDLP break.

## Falsifiable hypothesis

Apply de Rham–Witt `dlog`, Cartier, Frobenius, and ghost coordinates to public division/Miller functions so their residues define an addition-compatible coordinate that separates the prime-order subgroup and its factor-base sources. Combine several bounded Witt levels to recover relations and masked target scalars below rho.

## Mechanism-new operation

The proposed operation is **p-typical Witt-residue scalar/source extraction**. It differs syntactically from ordinary formal logarithms by acting on logarithmic differentials and function divisors.

The scope audit gives an exact rejection for additive p-typical coordinates. On every truncated target `W_n Omega^bullet`, and on its p-complete inverse limit, multiplication by `N` with `gcd(N,p)=1` is an automorphism; the inverse limit need not be p-primary torsion. Hence any additive homomorphism from `<P>` is zero. A nonzero residue of a chosen Miller/division function is a separate possible circularity only if an explicit reduction shows that constructing or normalizing the function already contains the source divisor. Nonadditive function-valued invariants and targets on which `N` is not invertible are outside this no-go.

## Assumptions

1. Public `E/F_p` has prime-order `<P>` of order `N` with `N!=p`, target `Q`, and factor base `F` of size `B=N^beta`.
2. The proposed Witt coordinate is canonical, public, addition compatible, and computable without known source divisors or factor logs.
3. A bounded number of Witt levels separates every subgroup point/source and has an exact inverse.
4. Function construction, precision/level, residues, inverse, output, rank, descent, and memory are charged.
5. Anomalous `N=p`, supplied divisor, leakage, and extension-field MOV cases are controls outside the generic prime-field claim.

## Semantic fingerprint

`division_Miller_function | de_Rham_Witt_dlog | Cartier_Frobenius_ghost_residue | prime_to_p_scalar_coordinate | exact_factor_source_inverse`

The exact no-go applies to the claimed addition-compatible `p`-typical target. A nonadditive operation or a target on which `N` is not invertible would require a new ID and operation.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H664`, whose exact character/phase controls do not create a factor source or scalar coordinate.
2. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1425-BOUNDED-PHASE-LIFT-NO-PROMOTION`, where bounded lifted phase predicates fail exact factor membership.
3. `ledger/FINDING-PF-IC-001.md` — imported `P1474`, where a large known-scalar CM orbit gives no invariant sparse source deck.
4. `ledger/FINDING-PF-IC-001.md` — imported `P1479`, where public low-dimensional feature spaces miss true factor logs.
5. `ledger/FINDING-PF-IC-001.md` — imported `TRANSFER-NR-005`, whose restricted homomorphism model records that fiber multiplicity/known maps do not create original-group rank or descent.

## Closest primary literature

- Illusie, [Complexe de de Rham–Witt et cohomologie cristalline](https://doi.org/10.24033/asens.1374), constructs the p-typical de Rham–Witt complex.
- Bloch and Kato, [p-adic etale cohomology](https://doi.org/10.1007/BF02831624), identify the p-adic logarithmic setting rather than a prime-to-p scalar channel.
- Semaev, [Evaluation of discrete logarithms in a group of p-torsion points](https://doi.org/10.1090/S0025-5718-98-00887-4), is the relevant positive p-torsion boundary, explicitly outside `N!=p`.
- Smart, [The discrete logarithm problem on elliptic curves of trace one](https://doi.org/10.1007/s001459900052), gives the neighboring anomalous-curve boundary, not a generic prime-order lift.

The literature supports the scoped p-primary distinction; it does not support the proposed generic channel. Novelty remains unverified outside the rejected fingerprint.

## Complete factor-base-to-target-descent path

1. Freeze curve, subgroup, factor base, target, Witt level, functions, residue conventions, and independent verifier.
2. Construct the public coordinate for every factor point and known-log target without supplied relation divisors.
3. Use coordinate addition to derive exact source rows, verify tuples, reach rank `B`, and solve/verify factor logs.
4. Evaluate fresh masked targets, invert residues to sources/scalars, subtract masks, and accept only `[x]P=Q`.
5. Charge function construction, Witt arithmetic/precision, residues, inverse, rank, linear algebra, descent, and memory.

## Full rho/BSGS cost model

Rho costs `N^(1/2+o(1))` time and constant state; BSGS costs `N^(1/2+o(1))` time/memory. Let coordinate setup/memory be `N^a,N^a_m`, level/precision payload `N^c`, query/inversion time and working memory `N^q,N^q_m`, inverse densities `N^delta,N^delta_t`, output `o`, ambiguity `u`, and linear algebra `N^ell,N^ell_m`. Then

`lambda=max(a,c,beta+delta+q+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,c,q_m,beta+o,ell_m,u)`.

Thus `lambda` is the complete time exponent and `mu` is the complete peak-memory exponent.
The algebraic no-go makes favorable costs irrelevant for the stated generic fingerprint. Toy p-torsion results cannot be extrapolated.

## Likely fatal obstruction

It is exact in the declared category: if `phi:<P>->W` is additive and multiplication by `N` is invertible on the truncated or p-complete p-typical target, then `0=phi([N]P)=N phi(P)` implies `phi(P)=0`. This does not close nonadditive invariants or targets with `N`-torsion. Function residues that depend on a preselected divisor/source relation fail instead by circular input.

## Proof track

The stated proof track is closed by the prime-to-p vanishing argument. A successor must define a genuinely nonadditive public operation or a target on which `N` is not invertible, plus a complete source inverse, under a new ID.

## Disproof track

Identify the additive target `M`, prove that multiplication by `N` acts invertibly, and apply the homomorphism argument. A separate supplied-divisor rejection requires an explicit reduction showing that function construction or normalization already contains the source divisor.

## Positive and negative controls

- **Positive control:** anomalous/p-torsion curves where the cited p-primary attacks apply, labelled outside scope.
- **Positive control:** supplied Miller divisors whose residues are independently known.
- **Negative control:** ordinary prime-order curves with `N!=p`, random subgroup points, and multiple Witt levels.
- **Negative control:** source-shuffled functions with the same divisor degree and residue budget.
- **End-to-end control:** rho/BSGS on the ordinary curve family.

## Quantitative promotion and falsification gates

The declared mechanism is rejected exactly for addition-compatible p-typical targets with `gcd(N,p)=1`. No experiment can promote it. A successor requires a nonadditive operation or a target on which `N` is not invertible and a fresh semantic audit; correctness on anomalous curves or supplied divisors remains a control.

## Artifact plan

- Exact no-go derivation: `ideas/artifacts/ECDLP-IDEA-140/prime_to_p_witt_no_go.md`
- Boundary fixtures: `ideas/artifacts/ECDLP-IDEA-140/fixtures.json`
- Prospective independent checker: `ideas/artifacts/ECDLP-IDEA-140/check_witt_boundary.sage`
- Cost-boundary note: `ideas/artifacts/ECDLP-IDEA-140/cost_analysis.md`

No artifact exists.

## Interpretation boundary

This is an exact scoped rejection, not a universal statement about every nonlinear invariant. All finite demonstrations would be toy; costs are heuristic/model-bound; novelty outside the fingerprint is unverified. No correctness result is a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-140/prime_to_p_witt_no_go.md` identifying the additive p-typical targets on which `N` is invertible and separating that theorem from the conditional supplied-divisor circularity reduction.
