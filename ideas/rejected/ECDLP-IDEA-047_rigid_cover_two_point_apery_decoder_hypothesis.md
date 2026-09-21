# ECDLP-IDEA-047 — Rigid-cover two-point Apéry decoder

## Status and claim labels

- Class: `algorithm`
- Risk band: `high_risk`
- State: `proposed_unapproved`
- Evidence scale: `toy` theorem-first preflight only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a separating profile, Riemann--Roch jump, or valid
  principal divisor is not a break.

## Falsifiable hypothesis

For a generic ordinary prime-field curve `E` with prime subgroup `<P>` of order
`N=p^(1+o(1))`, there is a deterministic target-independent rigid cover
`pi:C->E` of charged degree and genus such that the two-fiber Apéry/discrepancy profile
of `D_O=pi^*(O)` and `D_R=pi^*(R)` has both:

1. a public algebraic inverse decoder that recovers the scalar label of enough
   `R in <P>` without an orbit dictionary; and
2. certified jump functions whose divisors give complete factor-base relations after
   pushforward to `E`.

With relation collection, sparse linear algebra, individual descent, inverse decoding,
cover construction, coefficient output, and bit memory charged, the complete ECDLP time
and memory exponents are below `1/2`.

The hypothesis is stronger than computing a two-point Weierstrass semigroup or observing
profile collisions. It requires a witness-producing inverse theorem and an end-to-end
descent that beats rho/BSGS.

## Mechanism-new operation

Freeze `C` from `(E,P,N)` and represent each Frobenius-stable fiber divisor
`D_R`. For a fixed auxiliary divisor `A` and preregistered window, compute the exact
jump table

`J_R(u,v)=ell(A+u*D_O+v*D_R)-ell(A+(u-1)*D_O+v*D_R)`

together with a basis function for every positive jump. Apply a proved
Apéry/discrepancy inverse rule to select a supported jump function, factor its zero and
pole divisors over a fixed closed-point base, and push the principal-divisor equality
through `pi` to `E`.

The new operation is **two-fiber Riemann--Roch jump inversion with supported-function
witness recovery**. It is not a new factor-base shape, an error-locator polynomial,
ordinary support enumeration, a dense resultant, a different Riemann--Roch solver, or a
relation-only certificate. If the profile merely identifies one of `N` orbit entries,
needs a scalar lookup table, or finds a function only after generic support search, this
record merges into the occupied factor-base/support lanes.

## Assumptions

1. `E(F_p)` has a public prime subgroup `<P>` of order
   `N=p^(1+o(1))` and target `Q=[x]P`.
2. The cover equations, branch data, lift divisors, auxiliary divisor, profile window,
   bases, and decoder are fixed from `(E,P,N)` before target descent.
3. Fibers `D_R` and factor-base closed points are represented with Frobenius orbits,
   multiplicities, ramification, and exceptional support explicit.
4. Every jump is accompanied by an exact rational function and complete divisor
   factorization; a dimension count alone is insufficient.
5. Pushforward, Abel--Jacobi projection to `<P>`, signs, cofactors, and any degree
   inverse modulo `N` are verified on `E`.
6. Relation samples are target-independent, and failed profiles/functions/factorizations
   are included in density costs.
7. Cover genus, Riemann--Roch matrices, coefficient heights, output lists, decoder state,
   and bit memory are fully charged.
8. All finite evidence remains toy, heuristic, model-bound, and novelty-unverified.

## Semantic fingerprint

`rigid_cover_C_to_E | two_fiber_Apery_discrepancy_profile | algebraic_inverse_decoder | supported_Riemann_Roch_jump_function | pushforward_factor_base_descent`

The indispensable operation is the inverse theorem that emits a supported function
witness. Without it, the record is only another description of the known support-search
problem.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — records the dominant prime-field
   point-decomposition and full-cost obstruction this decoder must remove.
2. `ledger/H-FB-001.yaml` — rules out treating a different closed-point base as a
   mechanism by itself.
3. `ledger/EV-FB-001.yaml` — supplies the generic relation-yield baseline for
   matched base size and arity.
4. `ledger/RQ-FB-001.yaml` — requires a complete relation source and individual
   descent rather than applicability or relation validity alone.
5. `ledger/SYNTHESIS-20260716.md` — imposes rho/BSGS, construction, linear-algebra,
   memory, and target-descent accounting.

## Closest primary literature

- Homma and Kim, [Goppa Codes with Weierstrass
  Pairs](https://doi.org/10.1016/S0022-4049(00)00134-1), develops two-point gap
  and pure-gap structure; it does not provide a scalar-label inverse on elliptic fibers.
- Duursma and Park, [Coset Bounds for Algebraic Geometric
  Codes](https://arxiv.org/abs/0810.2789), formulates divisor semigroup ideals,
  discrepancy sets, and decoding bounds close to the proposed profile.
- Hess, [Computing Riemann--Roch Spaces in Algebraic Function Fields and Related
  Topics](https://doi.org/10.1006/jsco.2001.0513), supplies an algorithmic baseline
  whose genus, field, and matrix costs cannot be omitted.

The checked literature gives semigroup and Riemann--Roch machinery, not the proposed
target-independent scalar inverse. Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Construct `pi:C->E`, certify smoothness/ramification, compute `g(C)`, and freeze
   `A`, the profile window, closed-point enumeration, and exceptional-fiber rules.
2. Form a target-independent factor base `Z={Z_1,...,Z_B}` of closed points on `C`.
   For each `Z_i`, push `Z_i-deg(Z_i)D_O/deg(D_O)` through `pi`, clear
   denominators, project to `<P>`, and obtain a source point `F_i` with initially
   unknown logarithm.
3. For frozen known scalars `a`, set `R=[a]P`, compute `D_R` and its exact
   two-fiber profile, and invoke the inverse decoder. Accept only a jump function whose
   complete divisor is supported on `D_R`, `D_O`, and the fixed `Z_i`, with all
   residual support explicit.
4. Push the principal-divisor equality to `E` to obtain and verify a relation
   `c_R R + sum_i e_i F_i=O` with public nonzero `c_R mod N`. Collect
   `B+margin` independent rows, counting every miss and dependent row.
5. Solve the sparse system modulo `N` for every `log_P(F_i)` and verify the base
   logarithms on `E`.
6. Apply the identical profile and supported-function decoder to frozen randomized target
   representatives `Q+[t]P`. Push forward a verified target relation, substitute the
   base logs and public `t`, and solve for `x mod N`.
7. Accept only after `[x]P=Q` verifies on the original curve; retain all target
   failures, ambiguity, factorization output, and retries in the cost.

## Full rho/BSGS cost model

Let cover degree be `N^(k+o(1))`, genus `g=N^(gamma+o(1))`, factor-base
size `B=N^(beta+o(1))`, and cover/profile setup cost `N^(c+o(1))`.
Let one complete profile, Riemann--Roch basis, inverse-decoder, supported-function, and
divisor-factorization query cost `N^(r+o(1))`. Let reciprocal relation and target
success densities be `N^(delta+o(1))` and `N^(delta_t+o(1))`. Sparse
linear algebra costs `N^(omega_s*beta+o(1))`. Let stored curve, matrices,
functions, and decoder data use `N^(s+o(1))` bits.

- Pollard rho: `N^(1/2+o(1))` expected group operations and constant state.
- BSGS: `N^(1/2+o(1))` time and `N^(1/2+o(1))` stored points.
- Cover/base setup: `T_setup=N^(max(c,beta+r_0)+o(1))`, where `r_0`
  charges per-base closed-point and pushforward processing.
- Relation collection:
  `T_rel=N^(beta+delta+r+o(1))` for the complete batch needed to obtain
  `Theta(B)` verified independent rows.
- Sparse linear algebra: `T_LA=N^(omega_s*beta+o(1))`.
- Target descent: `T_desc=N^(delta_t+r+o(1))`.

The full time exponent is
`lambda=max(c,beta+r_0,beta+delta+r,omega_s*beta,delta_t+r)` and the
bit-memory exponent is `mu=max(s,beta,2*gamma)`, with dense
Riemann--Roch storage explicitly represented by `2*gamma` when applicable. Cover
degree/genus output, all profile entries, function coefficients, factors, and residual
lists are charged. Promotion requires `lambda<1/2` and `mu<1/2`.

## Likely fatal obstruction

For a fixed low-genus cover, the two-fiber profile may depend only on coarse divisor-class
data such as the order of `R-O`; this order is `N` for every nonzero subgroup point and
does not reveal `x`. A profile that separates all `N` fibers may need total window,
cover degree, genus, coefficient output, or a hidden dictionary of size `Omega(N)`.
Even when a jump is informative, finding one whose divisor is supported on a small fixed
base is exactly the occupied decomposition problem. Standard Riemann--Roch computation
can certify a function after its divisor constraints are supplied without discovering
the useful support or scalar label.

## Proof track

Give an explicit rigid-cover family and prove a two-fiber discrepancy theorem that
constructs a supported jump function and a public inverse decoder without scalar tables.
Bound genus, profile window, Riemann--Roch complexity, factorization output, relation and
target densities, and sparse algebra. Prove pushforward correctness and all seven descent
steps, then derive `lambda<1/2` and `mu<1/2`.

## Disproof track

Show any one of: profile constancy on nonzero `N`-torsion fibers; separation requiring
degree/genus/window/output `N^(1-o(1))`; supported-function recovery equivalent to
generic factor-base search; relation or target density forcing
`beta+delta+r>=1/2` or `delta_t+r>=1/2`; an uncharged residual divisor;
or an inverse rule that is an orbit lookup table.

## Positive and negative controls

- Positive Riemann--Roch control: curves with published two-point semigroups and exact
  discrepancy sets.
- Positive witness control: planted principal divisors supported on the declared base,
  with every recovered function checked by independent divisor arithmetic.
- Negative arithmetic control: random covers matched for degree, genus, ramification,
  base size, and closed-point counts.
- Negative mechanism control: ordinary support enumeration and a generic
  Riemann--Roch solve after the support is supplied.
- Negative profile control: randomize scalar labels on the same fiber profiles; any
  decoder advantage must vanish.
- Leakage control: a profile-to-scalar dictionary and a target-chosen cover are invalid
  oracle arms.

## Quantitative promotion and falsification gates

The theorem-first toy screen uses the lexicographically first supported ordinary
prime-order curve over each prime `p<=211`, every cover in a frozen degree-at-most-four,
genus-at-most-twelve branch grammar, exhaustive fibers, and blinded scalar labels.
Escalation requires:

- exact agreement of independent Riemann--Roch dimensions, jump functions, divisors,
  pushforwards, relations, and scalar verifications;
- a predeclared algebraic inverse rule separating at least 95% of nonzero fibers with no
  scalar dictionary;
- at least 1000 verified target-independent relations and 100 target descents at each of
  the two largest completed strata, with zero false accepted witnesses;
- upper 95% bounds `lambda<=0.45` and `mu<=0.45` including all misses,
  residual support, output, and factorization;
- a significant advantage over support enumeration, random-cover, and label-permutation
  controls.

Falsify the scoped claim if all fixed covers have identical nonzero-torsion profiles, the
inverse rule fails blind labels, any accepted divisor is wrong after repair, supported
functions require ordinary support search, or every full-cost lower 95% bound reaches
`lambda>=0.50` or `mu>=0.50`. Timeouts and unsupported covers are
infrastructure/coverage outcomes only.

## Artifact plan

- Planned cover grammar: `ideas/artifacts/ECDLP-IDEA-047/cover_grammar.yaml`
- Planned derivation: `ideas/artifacts/ECDLP-IDEA-047/apery_inverse_derivation.md`
- Planned implementation: `ideas/artifacts/ECDLP-IDEA-047/apery_decoder.sage`
- Planned manifests: `ideas/artifacts/ECDLP-IDEA-047/runs/<run-id>/manifest.yaml`
- Planned profiles: `ideas/artifacts/ECDLP-IDEA-047/runs/<run-id>/profiles.jsonl`
- Planned functions/relations: `ideas/artifacts/ECDLP-IDEA-047/runs/<run-id>/relations.jsonl`
- Planned analysis: `ideas/artifacts/ECDLP-IDEA-047/analysis.md`
- Required retained data: cover equations, ramification, fibers, complete profiles,
  function bases, divisors, factors, misses, relations, targets, timings, memory, seeds,
  commands, environment, commit, dirty-tree state, stdout, stderr, and checksums.

## Interpretation boundary

A novel-looking profile, correct Riemann--Roch computation, supported principal divisor,
or toy scalar recovery is not a breakthrough. Relation validity is separate from support
discovery, and correctness is separate from cost. Only a public inverse theorem and
independently verified complete descent below rho/BSGS justify escalation; until then all
claims are toy, heuristic, model-bound, and novelty-unverified.

## Exactly one next executable action

1. Enumerate the frozen degree-at-most-four, genus-at-most-twelve rigid-cover grammar for the lexicographically first supported prime-order curves over `p<=211`, compute blinded two-fiber profiles and exact jump functions, and accept a lane only if the predeclared algebraic inverse separates scalars without a lookup table.
