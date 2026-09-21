# ECDLP-IDEA-011 — Scalar-orbit elliptic-period descent

## Status and claim labels

- Class: `algorithm`
- Risk band: `high-risk`
- State: `proposed_unapproved`
- Evidence scale: `toy` preflight only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a separating toy invariant or correct coset classification is not a break.

## Falsifiable hypothesis

For a family of generic ordinary prime-field curves with prime subgroup order
`N=ell=p^(1+o(1))` and a public subgroup chain in `(Z/ell Z)^*`, there is a uniformly
constructible scalar-orbit invariant

`I_H(R) = sum_(h in H) x([h]R)`

or an explicitly specified orbit-polynomial coefficient with the same invariance, whose
compressed construction and evaluation separate `H`-cosets without enumerating `H`.
Refining through the subgroup chain recovers `x` from `Q=[x]P` with total charged time and
memory exponents strictly below `1/2`.

The prediction includes invariant construction, collisions, failed refinements, subgroup
factorization, and final verification. It is restricted to orders admitting the frozen
chain; extrapolation beyond that family is heuristic and model-bound.

## Mechanism-new operation

Quotient the nonzero scalar torsor `<P> minus {O}` by a multiplicative scalar subgroup
`H <= (Z/ell Z)^*`, and evaluate a coordinate function invariant under the orbit
`R -> [h]R`. Use a chain of such quotients to refine the unknown coset containing `x`.
The claimed new operation is **sublinear evaluation of a separating scalar-orbit elliptic
period**, not an isogeny, endomorphism, factor-base parameter change, explicit table of all
scalar multiples, post-hoc selector, or relation-only certificate.

## Assumptions

1. `E(F_p)` contains a known prime subgroup `<P>` of order `N=ell=p^(1+o(1))`, and
   `Q=[x]P` with `x != 0 mod ell`.
2. The public factorization of `ell-1` contains a preregistered chain
   `{1}=H_0 < H_1 < ... < H_t=(Z/ell Z)^*`; chain length is `ell^o(1)` and every index is
   charged. The density of eligible input orders is measured as `N^(-zeta+o(1))`; a
   search for a favorable curve/order pays `N^(zeta+o(1))`, while an arbitrary input
   lacking the chain is explicitly outside applicability rather than silently replaced.
3. The chosen period or orbit-polynomial coefficient is invariant under `H_i` and separates
   the child cosets used at refinement, except for a measured and charged ambiguity rate.
4. Construction and evaluation do not enumerate `Theta(|H_i|)` scalar multiples or use a
   hidden discrete-log, Diffie-Hellman, or target-specific advice table.
5. Coordinate exceptions, the sign symmetry of `x(R)=x(-R)`, and all period collisions are
   retained rather than silently resolved with known toy logarithms.
6. All scaling inferred from toy orders is heuristic, model-bound, and novelty-unverified.

## Semantic fingerprint

`scalar_multiplicative_orbit_quotient | elliptic_period_invariant | subgroup_chain_coset_refinement | sublinear_orbit_evaluation | direct_target_to_scalar_descent`

The new mathematical operation is quotient-and-refine on the scalar torsor. It does not
reuse the ledger's point-decomposition ideal, curve-model substitution, same-field
isogeny neighborhood, or elementary factor-base structure.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — establishes why leaving the membership-constrained
   prime-field index-calculus route is necessary.
2. `ledger/H-REP-001.yaml` — rules out treating a coordinate rewrite of the same PDP as a
   new exponent mechanism.
3. `ledger/EV-REP-001.yaml` — records the explicit sign-branch artifact that the
   `x`-coordinate period must charge.
4. `ledger/H-ISO-001.yaml` — distinguishes scalar-orbit quotienting from a linear
   same-field isogeny action.
5. `ledger/SYNTHESIS-20260716.md` — supplies the full-cost, scaling, and independent-review boundary.

## Closest primary literature

- Couveignes and Lercier, [Elliptic periods for finite fields](https://arxiv.org/abs/0802.0165), constructs fast arithmetic from elliptic orbits, but does not provide the proposed hidden-scalar coset descent.
- Derickx and van Hoeij, [Gonality of the modular curve X1(N)](https://arxiv.org/abs/1307.5719), studies low-degree functions on the moduli space of marked torsion points and is directly relevant to the likely degree obstruction.
- Poonen, [Gonality of modular curves in characteristic p](https://arxiv.org/abs/math/0601141), gives characteristic-`p` growth results relevant to quotient invariants.
- Shoup, [Lower Bounds for Discrete Logarithms](https://www.shoup.net/papers/dlbounds1.pdf), is the generic `Omega(sqrt(N))` boundary that a coordinate-specific invariant must genuinely escape.

These sources make elliptic periods and scalar actions known. They do not establish a
sublinear, separating evaluator for the proposed `H`-orbit invariant. That absence is not
proof of novelty; novelty remains unverified.

## Complete factor-base-to-target-descent path

Here the “factor base” is the frozen set of child-coset representatives at each scalar
subgroup level, not an index-calculus point base.

1. Factor `ell-1`, freeze `{H_i}`, explicit child representatives, the period coordinate,
   sign convention, and collision-handling rule before inspecting any target result.
2. Construct a compressed evaluator for each `I_(H_i)` and validate invariance under every
   enumerated toy `h in H_i` without retaining an explicit large-prime orbit table.
3. Begin with the known statement `x in (Z/ell Z)^*`; at level `i`, evaluate
   `I_(H_(i-1))(Q)` and the fingerprints of the children `[c*d]P` consistent with the
   already selected parent coset `c*H_i`.
4. Retain every matching child. Resolve only by the preregistered next invariant or branch
   search, and charge all surviving ambiguity; never select with the known toy `x`.
5. Continue until the candidate set is a singleton modulo the unavoidable sign symmetry;
   test both signed candidates when necessary.
6. Return the surviving scalar `x mod ell` and independently verify `[x]P=Q` on the
   original curve.

## Full rho/BSGS cost model

Let `|H_i|=N^(eta_i+o(1))`; child index `[H_i:H_(i-1)]=N^(gamma_i+o(1))`;
compressed-invariant construction cost `N^(a_i+o(1))`; evaluation cost
`N^(kappa_i+o(1))`; reciprocal unambiguous-refinement probability
`N^(delta_i+o(1))`; and evaluator storage `N^(s_i+o(1))`. Let `u` be the exponent of any
residual candidate list after the final refinement, and let `zeta` be the reciprocal
density exponent of orders admitting the frozen chain.

- Pollard rho baseline: expected `sqrt(pi*N/2)=N^(1/2+o(1))` group operations and `O(1)`
  state, apart from constant-factor automorphism gains.
- BSGS baseline: `N^(1/2+o(1))` group operations and `N^(1/2+o(1))` stored points.
- Subgroup factorization and chain setup: `N^(f+zeta+o(1))` when favorable-input search is
  part of the claim, including every rejected curve/order. For an already-fixed input,
  applicability is binary and a missing chain terminates the lane.
- Invariant construction: `T_build=N^(max_i(a_i)+o(1))`.
- Coset refinement: `T_refine=N^(max_i(gamma_i+kappa_i+delta_i)+o(1))`; the
  `N^gamma_i` children and all ambiguous retries are charged.
- Residual search and verification: `T_finish=N^(u+o(1))`; ordinary scalar
  multiplication is exponent zero.
- Bit memory: `M=N^(max_i(s_i,gamma_i,u)+o(1))`, including invariant coefficients,
  orbit representatives, and candidate encodings.

The complete time exponent is
`lambda=max(f+zeta, max_i(a_i), max_i(gamma_i+kappa_i+delta_i), u)` and the memory exponent is
`mu=max_i(s_i,gamma_i,u)`. Naive period summation has `kappa_i=eta_i` and does not beat
rho. A chain available only after an `N^(1/2)` order search also does not beat rho.

## Likely fatal obstruction

The pair `(E,R)` is a point of the level structure parameterized by `X_1(ell)`, and scalar
multiplication acts through diamond operators. A function separating large scalar orbits
is therefore expected to have degree, representation size, or evaluation cost comparable
to the orbit being collapsed. The coordinate sum may also collide on many distinct
cosets. Either effect makes some `a_i`, `kappa_i+delta_i`, or `u` at least `1/2`.

## Proof track

Give an explicit recurrence or product formula for every frozen invariant, prove
`H_i`-invariance and child-coset separation, and prove its construction/evaluation
complexity without orbit enumeration. Combine these bounds along the complete refinement
chain to derive `lambda<1/2` and verify the recovered scalar.

## Disproof track

Prove a degree or straight-line-complexity lower bound of `N^(1/2-o(1))`; exhibit
superpolynomially many indistinguishable cosets; reduce compressed evaluation to ECDLP;
or show that chain availability, construction, refinement, residual search, or memory
forces `lambda>=1/2`.

## Positive and negative controls

- Positive control: a multiplicative finite-field torsor with classical Gaussian periods,
  where the same subgroup-chain refinement is known to separate cosets.
- Positive instrumentation control: exhaustive toy scalar orbits, naive period sums, and
  all coset fingerprints must agree with the compressed evaluator.
- Negative control: random functions on the same scalar orbits with matched output range;
  collision accounting must reject spurious apparent separation.
- Negative mechanism control: standard endomorphisms and Frobenius, which output known
  linear scalar actions and must not be reported as nonlinear orbit compression.
- Circularity control: log every scalar multiplication and lookup; reject any evaluator
  whose trace enumerates `H_i`, queries known toy `x`, or indexes an explicit target table.

## Quantitative promotion and falsification gates

The toy preflight uses prime subgroup orders from 18 through 44 bits, at least 30 ordinary
curves per size, and only preregistered orders whose `ell-1` admits chains with child
indices at most `N^0.10`. Exhaustive orbit truth is required through 24 bits. Promotion
requires all of:

- zero incorrect coset refinements and zero incorrect final scalars;
- at least `99.9%` agreement between compressed and naive period values where exhaustive
  evaluation is feasible;
- upper 95% fitted bounds `max_i(a_i)<=0.45`,
  `max_i(gamma_i+kappa_i+delta_i)<=0.45`, and `u<=0.10`;
- a reported eligible-order density with upper 95% `f+zeta<=0.45`; any claim restricted
  to supplied eligible inputs must say so and may not generalize to arbitrary curves;
- upper 95% full-cost bound `lambda<=0.45` and memory bound `mu<=0.45`;
- end-to-end recovery faster than matched rho and BSGS operation models at the two largest
  feasible sizes, with construction and failed refinements included.

Falsify the scoped prediction if any accepted singleton is wrong, a period collision
cannot be resolved without known `x`, naive orbit enumeration is required, the needed
chain is absent in the frozen family, or every fitted full-cost configuration has lower
95% bound `lambda>=0.50`. A timeout or unsupported order factorization is infrastructure
or coverage evidence, not evidence against other invariants.

## Artifact plan

- Contract: `ideas/artifacts/ECDLP-IDEA-011/experiment_contract.yaml`
- Planned implementation: `ideas/artifacts/ECDLP-IDEA-011/scalar_orbit_period.sage`
- Planned chain catalog: `ideas/artifacts/ECDLP-IDEA-011/subgroup_chains.jsonl`
- Planned runs: `ideas/artifacts/ECDLP-IDEA-011/runs/<run-id>/`
- Planned raw fingerprints: `ideas/artifacts/ECDLP-IDEA-011/runs/<run-id>/fingerprints.jsonl`
- Planned analysis: `ideas/artifacts/ECDLP-IDEA-011/analysis.md`
- Required retained data: invariant formula, operation trace, collisions, surviving
  branches, timings, peak memory, exact seeds, commit, dirty-tree state, stdout, and stderr.

## Interpretation boundary

Every proposed or measured claim is toy, heuristic, model-bound, and novelty-unverified.
An invariant identity, compressed toy evaluation, or correct coset classification is not
an ECDLP break. Only complete scalar recovery with construction, ambiguity, chain, memory,
and verification costs below rho/BSGS can justify escalation, and crypto-scale claims
would still require independent replication and review.

## Exactly one next executable action

1. Draft and structurally validate the bounded naive-versus-compressed orbit-invariant contract at `ideas/artifacts/ECDLP-IDEA-011/experiment_contract.yaml`, with operation traces that forbid hidden orbit enumeration; do not execute it yet.
