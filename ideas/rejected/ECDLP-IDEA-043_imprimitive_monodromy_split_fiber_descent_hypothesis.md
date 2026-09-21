# ECDLP-IDEA-043 — Imprimitive-monodromy split-fiber descent

## Status and claim labels

- Class: `mechanism`
- Risk band: `high-risk`
- State: `proposed_unapproved`
- Evidence scale: `toy` preflight only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; an explicit cover, split fiber, or valid pushforward is not a break.

## Falsifiable hypothesis

There is a target-independent family of correspondences over a generic ordinary
`E/F_p`, of degree `d=N^alpha`, whose imprimitive geometric monodromy gives a complete
rational-fiber splitting probability exponentially larger than matched generic covers.
Factoring a successful fiber returns all point atoms directly, and its divisor
pushforward yields verified known-scalar relations and a separate target descent with
full time and bit-memory exponent below `1/2`. This is toy, heuristic, model-bound, and
novelty-unverified.

## Mechanism-new operation

The new operation is **monodromy-engineered full-fiber splitting with direct atom output**.
It uses a block system in the cover's permutation representation to amplify rational
splitting while retaining a fast factorization path. Unlike `010/019/023/026`, it does
not use a deck-orbit label, monodromy word, zeta fingerprint, or hidden branch selector:
every rational fiber point is output and verified. Unlike `002`, it does not assume
smoothness in a split Jacobian. Fixed-degree constant gains, a generic cover, or a
target-chosen branch are controls and must be merged with the occupied cover lane.

## Assumptions

- `E(F_p)` has a prime subgroup `<P>` of order `N=p^(1+o(1))`.
- The correspondence family, monodromy block system, and atom rule are public and independent of `Q`.
- Complete fiber factorization returns equations and multiplicities for every point; no oracle labels branches.
- Cover construction, degree, coefficient height, failed applicability, factorization,
  split density, output size, and verification are charged.
- The divisor pushforward coefficient on `E[N]` is public and invertible modulo `N`.
- Toy-to-asymptotic extrapolation is heuristic and model-bound.

## Semantic fingerprint

`elliptic_correspondence_family | imprimitive_geometric_monodromy | amplified_complete_rational_splitting | full_fiber_atom_witnesses | pushforward_relation_and_target_descent`

## Five closest ledger entries

1. `ledger/H-ISO-001.yaml` — closest correspondence/isogeny boundary, but it has no growing split fibers.
2. `ledger/EV-ISO-001.yaml` — provides the matched coefficient-variance control.
3. `ledger/FINDING-PF-IC-001.md` — supplies the relation-density and full-cost floor.
4. `ledger/H-FB-001.yaml` — prevents ordinary atom-set structure from counting as the mechanism.
5. `ledger/SYNTHESIS-20260716.md` — requires an end-to-end exponent change and scoped claims.

## Closest primary literature

- Guralnick, Müller, and Saxl, [The rational function analogue of a question of Schur and exceptionality of permutation representations](https://arxiv.org/abs/math/0201069), gives the closest exceptional/imprimitive monodromy framework.
- Petit, Kosters, and Messeng, [Algebraic approaches for the ECDLP over prime fields](https://christophe.petit.web.ulb.be/files/16PKC_primeECDLP.pdf), is the closest rational-map factor-base boundary.
- Gaudry, [Index calculus for abelian varieties](https://doi.org/10.1016/j.jsc.2008.08.005), supplies the divisor relation baseline.

None proves a growing-degree elliptic family with both amplified full splitting and cheap
witness output; novelty remains unverified.

## Complete factor-base-to-target-descent path

- Freeze a correspondence degree, block system, construction rule, and deterministic atom base `F`.
- Certify geometric/arithmetic monodromy and the public pushforward multiplier on `Pic^0(E)`.
- For independent known scalars `r`, specialize the correspondence at `R=[r]P` and
  completely factor the fiber, retaining all irreducible and repeated factors.
- Accept only fibers whose required points are rational atoms in `F`; verify the full
  divisor and push it to an exact relation on `E`.
- Collect full-rank rows and solve atom logarithms.
- Factor fibers over masked targets `Q+[t]P`, use the identical rule, substitute atom
  logs, invert the public pushforward multiplier, remove `t`, and verify the scalar.

## Full rho/BSGS cost model

Let degree `d=N^alpha`, atom-base size `B=N^beta`, family construction `N^c`, reciprocal
applicability `N^zeta`, complete fiber factorization and output `N^f`, reciprocal accepted
split-fiber densities `N^delta` and `N^delta_t`, and full stored cover/factor state `N^s`
bits. If one accepted fiber supplies `Theta(d)` useful atoms, `N^(max(0,beta-alpha))`
independent accepted fibers are optimistically required.

- Pollard rho: `N^(1/2+o(1))` time and constant-state exponent.
- BSGS: `N^(1/2+o(1))` time and memory.
- Construction: `N^(c+zeta+o(1))`.
- Relation collection: `N^(max(0,beta-alpha)+f+delta+o(1))`.
- Sparse linear algebra: `N^(2*beta+o(1))` time and `N^beta` memory.
- Target descent: `N^(f+delta_t+o(1))`.

The time exponent is
`lambda=max(c+zeta,max(0,beta-alpha)+f+delta,2*beta,f+delta_t)` and bit-memory exponent
is `mu=max(s,beta,alpha)`. Fiber output alone enforces `f>=alpha` when all `d` atoms are
materialized.

## Likely fatal obstruction

Chebotarev density may make complete splitting roughly the reciprocal of a monodromy
group whose growth cancels every `d`-atom gain. An imprimitive tower can merely defer the
same branch enumeration to successive blocks, while construction, coefficient height,
or output size reaches the rho boundary.

## Proof track

Construct a family with certified monodromy, prove a split-density advantage over generic
covers, and give a complete factor algorithm plus pushforward identity. Combine its
usable-atom rank and target density to establish `lambda,mu<1/2`.

## Disproof track

Show the full-split density is no better than the matched cycle-index prediction, block
enumeration cancels the gain, pushforwards are trivial on `E[N]`, or construction/output
forces every full-cost exponent to at least `1/2`.

## Positive and negative controls

- Positive control: a planted imprimitive cover with known block system and completely split fibers.
- Negative control: random covers with identical degree and ramification profile.
- Fixed-degree control: hold degree constant to expose mere constant-factor gains.
- Branch-label control: oracle-labeled factors are instrumentation only and cannot promote.
- Pushforward control: every accepted fiber is independently verified in divisors and on `E`.

## Quantitative promotion and falsification gates

Use every ordinary curve with `p<=257`, correspondence degrees 3 through 12, and all
families in a grammar frozen before split counts. Promotion requires exact monodromy and
fiber truth, zero invalid pushforwards, at least a `0.15` fitted split-density exponent
advantage over matched generic covers, and upper 95% `lambda,mu<=0.45`. Falsify the
scoped claim if the advantage disappears under matched monodromy controls, the
pushforward is zero/noninvertible on the prime subgroup, or every full-cost lower 95%
bound has `lambda>=0.50`.

## Artifact plan

- Specification: `ideas/artifacts/ECDLP-IDEA-043/preflight_spec.yaml`
- Family catalog: `ideas/artifacts/ECDLP-IDEA-043/correspondences.jsonl`
- Planned implementation: `ideas/artifacts/ECDLP-IDEA-043/split_fiber_descent.sage`
- Planned runs: `ideas/artifacts/ECDLP-IDEA-043/runs/<run-id>/`
- Planned analysis: `ideas/artifacts/ECDLP-IDEA-043/analysis.md`

## Interpretation boundary

This is a toy, heuristic, model-bound, novelty-unverified high-risk hypothesis. Cover
construction, rational splitting, or relation validity is not a breakthrough. Promotion
requires complete non-oracle target descent with all density and output costs below rho/BSGS.

## Exactly one next executable action

1. Enumerate every frozen degree-3-through-12 correspondence over ordinary curves with `p<=257`, compute exact monodromy and all fibers, and compare blinded full-split witness yield with matched generic covers.
