# ECDLP-IDEA-037 — Generalized-Jacobian kernel-dither descent

## Status and claim labels

- Class: `representation`
- Risk band: `representation-changing`
- State: `proposed_unapproved`
- Evidence scale: `toy` theorem/preflight only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a valid lift, smooth representative, or projected relation is not an ECDLP break.

## Falsifiable hypothesis

Let `D` be a reduced rational modulus on a generic ordinary `E/F_p`. The generalized
Jacobian fits into an explicit extension

`1 -> L_D -> J_D -> E -> 0`,

where `L_D` is a linear algebraic group. There is a target-independent algorithm that
uses public `L_D(F_p)` kernel elements to sample many representatives above a point
`R in <P>`, and finds atom-supported representatives often enough that projected
relation collection, sparse linear algebra, and individual descent have time and bit-
memory exponents below `1/2` in `N=|<P>|=p^(1+o(1))`.

The prediction is stronger than existence of the extension or correctness of projection.
It requires a measurable projected-smoothness advantage after kernel sampling, modulus
degree, failed reductions, atom construction, and target descent are all charged.

## Mechanism-new operation

Choose a deterministic lift of each `R` to `J_D`, multiply it by independently sampled
public elements of the linear kernel, and reduce the resulting generalized divisor class
against a fixed atom base. All accepted identities are then pushed through
`pi:J_D->E`. The proposed operation is **kernel-fiber representative randomization before
supported reduction**.

This is not an injection of the prime-order subgroup into a torus, a pairing/MOV transfer,
a different factor-base shape, a cover-branch selector, or a single S-unit search on `E`.
The kernel coordinate is discarded after projection; it is useful only if its many-to-one
fiber genuinely changes witness density rather than adding independent bookkeeping.

## Assumptions

1. `E/F_p` is ordinary and contains a known prime subgroup `<P>` of order
   `N=p^(1+o(1))`, with `Q=[x]P`.
2. `D=S_1+...+S_d` is reduced, rational, target-independent, disjoint from all accepted
   divisor supports, and has an explicit generalized-Jacobian group law and projection.
3. A deterministic section as a set map, not a group homomorphism, supplies one auditable
   starting representative above every queried point; all section failures are retained.
4. The atom base has `B=N^beta` generalized divisor classes with explicit projected
   images `F_i in <P>`; atom construction never uses `Q` or a known toy logarithm.
5. The reducer returns complete coefficients and kernel residuals, not a smoothness count.
6. Relation and target success probabilities are measured over all preregistered kernel
   samples; toy slopes remain heuristic, model-bound, and novelty-unverified.

## Semantic fingerprint

`generalized_Jacobian_extension | public_linear_kernel_dither | many_representatives_per_E_class | supported_generalized_divisor_reduction | quotient_projection_to_E | separate_target_descent`

Removing the kernel-dither step collapses the idea to ordinary genus-one supported
reduction. Injecting `E[N]` into `L_D`, selecting successful representatives after seeing
the target, or returning only a projected relation certificate changes it into a rejected
torus, selector, or relation-only control.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — fixes the prime-field membership and relation-density
   floor that the projected-smoothness gain must actually remove.
2. `ledger/H-FB-001.yaml` — prevents kernel sampling from being counted as a mere new
   factor-base shape.
3. `ledger/EV-FB-001.yaml` — supplies the matched random-base yield control and requires a
   scaling, not constant-factor, improvement.
4. `ledger/H-ISO-001.yaml` — rules out presenting another same-field isogeny or quotient
   identity as the mechanism.
5. `ledger/SYNTHESIS-20260716.md` — requires full relation, projection, linear-algebra,
   target-descent, and memory accounting against rho.

## Closest primary literature

- Rosenlicht, [Generalized Jacobian varieties](https://doi.org/10.2307/1969707), constructs
  generalized Jacobians and the linear-kernel extension used here.
- Khuri-Makdisi, [Linear algebra algorithms for divisors on an algebraic curve](https://doi.org/10.1090/S0025-5718-04-01630-1), gives explicit divisor-class arithmetic against which reduction work must be charged.
- Gaudry, [Index calculus for abelian varieties of small dimension](https://doi.org/10.1016/j.jsc.2008.08.005), supplies the nearby smooth-divisor cost baseline.

These sources do not provide the asserted projected-smoothness improvement from kernel
fibers. This proximity check is not a novelty proof.

## Complete factor-base-to-target-descent path

1. Freeze `(E,P,N)`, the rational modulus `D`, exact generalized-divisor conventions, the
   projection `pi`, the set-theoretic starting lift, and an exhaustive kernel-sampling rule.
2. Construct `B=N^beta` target-independent atoms `A_i in J_D(F_p)`, compute
   `F_i=pi(A_i)`, discard zero or duplicate images, and retain every construction cost.
3. For a frozen stream of known scalars `a`, lift `R=[a]P`, dither the lift by the next
   kernel sample, and run the same supported reducer; record misses and ambiguities.
4. Accept only an exact identity `R_tilde+K=sum_i e_i A_i` with a fully represented kernel
   residual `K`. Project and independently verify `R=sum_i e_i F_i` on `E`.
5. Collect at least `B+margin` independent projected rows and solve for every required
   `log_P(F_i)`, charging dependencies and sparse-matrix work.
6. Freeze the base-log state, then apply the identical lift, dither, and reduction sequence
   to `Q+[t]P` for preregistered public randomizers `t`; no target-trained kernel policy is allowed.
7. Substitute solved atom logs, remove `t`, enumerate every certified ambiguity, recover
   `x mod N`, and accept only after `[x]P=Q` on the original curve.

## Full rho/BSGS cost model

Let `B=N^beta`, generalized-Jacobian construction and atom setup cost `N^(s+o(1))`,
modulus/representation degree and coefficient-height cost `N^(mu+h+o(1))`, one complete
kernel-dither reduction cost `N^(kappa+o(1))`, reciprocal relation success
`N^(delta+o(1))`, reciprocal target success `N^(delta_t+o(1))`, target trial cost
`N^(kappa_t+o(1))`, and independent verification cost `N^(v+o(1))`.

- Pollard rho: `T_rho=N^(1/2+o(1))` group operations and `N^o(1)` bits of state.
- BSGS: `T_BSGS=N^(1/2+o(1))` and `M_BSGS=N^(1/2+o(1))` stored-point bits up to logarithmic factors.
- Setup and representation: `T_setup=N^(max(s,mu+h)+o(1))`.
- Relation collection: `T_rel=N^(beta+delta+kappa+o(1))` for `Theta(B)` accepted rows.
- Sparse linear algebra: conservatively `T_LA=N^(2*beta+o(1))` and
  `M_LA=N^(beta+o(1))` bits for bounded-weight rows.
- Individual descent: `T_desc=N^(delta_t+kappa_t+o(1))`.
- Verification: `T_verify=N^(v+o(1))`.
- Total bit memory, including atom encodings, modulus coefficients, kernel states, and
  caches, is `M=N^(max(beta,mu,h,m_rep)+o(1))` bits.

Thus the full time exponent is
`lambda=max(s,mu+h,beta+delta+kappa,2*beta,delta_t+kappa_t,v)` and the memory exponent is
`m=max(beta,mu,h,m_rep)`. Promotion requires upper confidence bounds `lambda<1/2` and
`m<1/2`; online-only improvement does not beat rho or BSGS.

## Likely fatal obstruction

The generalized-Jacobian fiber may factor statistically and algorithmically into the
original `E` supported-reduction problem and an independent linear-kernel coordinate.
Then every apparent increase in the number of upstairs representatives is matched by an
equal increase in state space, while the projected smoothness probability is unchanged.
Growing `deg(D)` can also make representation size or reduction cost dominate. A direct
quotient-collapse theorem would reject the mechanism without an experiment.

## Proof track

Construct an explicit modulus family and reducer, prove that kernel dithering gives
distinct cheaply sampled representatives, and establish a projected-smoothness law whose
gain survives atom construction, quotient projection, sparse solving, and target descent.
The proof must bound all representation sizes and cannot assume a section homomorphism.

## Disproof track

Prove that supported-reduction success is constant on `L_D` fibers after projection, or
that its average equals the pushed-forward atom-base success law. Alternatively prove
`mu+h>=1/2`, `beta+delta+kappa>=1/2`, or that target-compatible representatives require a
hidden logarithm or post-hoc selector.

## Positive and negative controls

- Positive algebra control: the split product `E(F_p) x F_p^*` with planted supported
  representatives validates kernel sampling, projection, and coefficient bookkeeping.
- Positive truth control: exhaustive enumeration of `J_D(F_p)` for `D=S_1+S_2` on the
  smallest curves must match every reducer success and miss.
- Negative quotient control: direct supported reduction on `E` using the exact projected
  multiset `{F_i}` and the same operation budget.
- Negative-label control: randomly permute kernel encodings while preserving fiber sizes;
  a claimed gain that survives only chosen labels is invalid.
- Torus/MOV control: any arm that evaluates a nontrivial order-`N` character of the kernel
  is reported separately and cannot promote this mechanism.
- Oracle control: an oracle may reveal a smooth lift only to test downstream plumbing; it
  contributes no evidence for the non-oracle reducer.

## Quantitative promotion and falsification gates

The first toy matrix uses ordinary prime-order subgroups over all eligible primes
`p<=257`, moduli of two and three rational points, atom-base sizes `B in {4,6,8,12}`, and
complete fiber enumeration where feasible. Promotion only to a larger scaling study
requires zero incorrect identities, exact exhaustive agreement, at least 1,000 accepted
non-oracle projected relations, at least 100 target descents, a projected-success exponent
advantage of at least `0.15` over the direct quotient control with a 95 percent interval
excluding zero, and upper bounds `lambda<=0.45`, `m<=0.45`.

Falsify the scoped mechanism if exact enumeration proves fiber-invariant projected
success, if every gain disappears against the pushed-forward multiset control, if any
accepted kernel residual or projected relation fails verification, or if the lower 95
percent full-cost bound is `lambda>=0.50`. Infrastructure failures are not mathematical
negative evidence.

## Artifact plan

- Planned contract: `ideas/artifacts/ECDLP-IDEA-037/contract.yaml`
- Planned implementation: `ideas/artifacts/ECDLP-IDEA-037/generalized_jacobian_dither.sage`
- Planned exhaustive truth: `ideas/artifacts/ECDLP-IDEA-037/exhaustive_fibers.jsonl`
- Planned runs: `ideas/artifacts/ECDLP-IDEA-037/runs/<run-id>/`
- Planned relation records: `ideas/artifacts/ECDLP-IDEA-037/runs/<run-id>/relations.jsonl`
- Planned analysis: `ideas/artifacts/ECDLP-IDEA-037/analysis.md`
- Retain exact curve/modulus data, atoms, kernel samples, misses, identities, operation
  counts, peak bit memory, commands, seeds, environment, stdout, stderr, and checksums.

## Interpretation boundary

Every claim is toy, heuristic, model-bound, and novelty-unverified. A constructed
generalized Jacobian, correct group law, abundant fiber, smooth oracle lift, or verified
projected relation is not a breakthrough. Only a complete scalar recovery whose charged
time and bit-memory exponents beat both rho and BSGS may advance beyond preflight, and it
would still require independent replication.

## Exactly one next executable action

1. Implement the bounded `D=S_1+S_2` exhaustive-fiber quotient-collapse preflight for all eligible prime-order toy curves over `p<=257`, comparing kernel-dither success with the exact pushed-forward multiset control.
