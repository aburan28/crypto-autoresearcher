# ECDLP-IDEA-040 — Arithmetic-surface double-tame-symbol descent

## Status and claim labels

- Class: `mechanism`
- Risk band: `high-risk`
- State: `proposed_unapproved`
- Evidence scale: `toy` theorem/preflight only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a valid Gersten boundary, reciprocity identity, or elliptic relation is not a break.

## Falsifiable hypothesis

Embed `E/F_p` as a distinguished fiber of an explicit regular surface `X`. There is a
target-independent search for bounded-complexity `K_2(k(X))` symbols whose first tame
symbols are supported on a fixed curve base and whose second residues on the distinguished
fiber give a useful principal zero-cycle containing `R` and factor-base points. Cross-
fiber residues are public and cancelable. Bilinear construction of two surface functions
finds such relations and a separate target descent with total time and bit-memory
exponents below `1/2`.

The prediction is not the reciprocity law itself. It is a complete algorithm in which the
two-stage Gersten boundary creates supported elliptic relations more cheaply than direct
S-unit or point-decomposition search after all surface, function-height, residue, failed-
symbol, sparse-solve, and target costs are charged.

## Mechanism-new operation

For a symbol `{f,g}`, compute its codimension-one tame symbols on curves of `X`, then the
divisors of those residue functions at codimension-two points. Arrange the public residues
on auxiliary fibers so that the remaining distinguished-fiber divisor is

`(R)-(O)+sum_i e_i((F_i)-(O))`,

or a specified nonzero multiple. The proposed operation is **double tame-boundary
factorization with cross-fiber cancellation**: two independently structured surface
functions generate the final one-fiber relation.

This is not a direct additive map from `E[N]`, a single Miller/S-unit function on `E`, a
Cartier-support syndrome, a Chow-square regulator, a dense resultant, or a relation-only
certificate. It survives only if the bilinear surface factorization removes rather than
relocates the supported-function search.

## Assumptions

1. `E/F_p` is ordinary with a known prime subgroup `<P>` of order `N=p^(1+o(1))`, and
   `Q=[x]P`.
2. `X` is a regular projective surface with a frozen distinguished fiber isomorphic to
   `E`, exact local parameters, and computable Gersten boundary maps.
3. Horizontal lifts of the origin and factor-base points, auxiliary fibers, curve bases,
   and admissible bidegree/height panels are fixed independently of `Q`.
4. Every codimension-one tame symbol and every codimension-two residue is enumerated;
   discarded auxiliary-fiber terms or poles invalidate a certificate.
5. The distinguished-fiber divisor is returned with actual factor-base support and a
   nonzero known coefficient of `R`, not only as a reciprocity sum or smoothness count.
6. Smooth-symbol probabilities and slopes are heuristic and model-bound; novelty is
   unverified.

## Semantic fingerprint

`regular_arithmetic_surface | K2_symbol_pair | first_tame_boundary_on_curves | second_residue_zero_cycles | public_cross_fiber_cancellation | distinguished_E_relation | frozen_target_symbol_descent`

If the second boundary is computed only after a direct supported function on `E` is
already known, the idea collapses to the S-unit lane. If global reciprocity gives only a
zero total with no isolated fiber witness, it is a relation-validity control. Post-hoc
selection of auxiliary fibers or symbols using `x` is forbidden.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — states the prime-field supported-relation cost that the
   double-boundary factorization must lower.
2. `ledger/H-FB-001.yaml` — excludes a different horizontal-point set as the mechanism.
3. `ledger/EV-FB-001.yaml` — provides the direct structured/random factor-base yield and
   scaling controls.
4. `ledger/H-REP-001.yaml` — prevents a surface coordinate or equation rewrite from being
   mistaken for a complexity change.
5. `ledger/SYNTHESIS-20260716.md` — requires exact negative boundaries and full rho/BSGS
   relation-to-target accounting.

## Closest primary literature

- Quillen, [Higher algebraic K-theory I](https://doi.org/10.1007/BFb0067053), supplies the localization framework underlying the proposed boundary calculation.
- Kato and Saito, [Unramified class field theory of arithmetical surfaces](https://doi.org/10.2307/2007029), develops higher-dimensional local/global reciprocity for arithmetic surfaces.
- Bloch, [Algebraic K-theory and crystalline cohomology](https://www.numdam.org/item/PMIHES_1977__47__187_0/), gives nearby K-theoretic and cycle-theoretic structure in positive characteristic.

None supplies the asserted bounded double-symbol search or an ECDLP descent. The primary-
literature check marks proximity and likely obstructions; it does not verify novelty.

## Complete factor-base-to-target-descent path

1. Freeze `(E,P,N)`, the regular surface `X`, distinguished and auxiliary fibers, local
   parameters, the complete Gersten sign convention, and bounded function/symbol panels.
2. Choose `B=N^beta` target-independent points `F_i`, lift them to fixed horizontal curves,
   and construct the curve/point support base used by both boundary stages.
3. For known `R=[a]P`, impose the preregistered incidence with its horizontal lift and
   enumerate pairs `(f,g)` in deterministic height order; retain every failed or nonsmooth
   boundary.
4. Compute the complete first tame boundary and every second residue. Accept only when
   auxiliary-fiber cycles have public cancellations and the distinguished-fiber divisor
   yields `c_R R+sum_i e_iF_i+c_P P=O` with known `c_R != 0 mod N`.
5. Independently verify the Gersten identity, the full surface cycle, and the elliptic
   relation; collect `B+margin` independent rows and solve factor-base logarithms.
6. Freeze functions, support panels, caches, and base logs; run the identical symbol search
   for `Q+[t]P` using preregistered public randomizers and charge every unsuccessful pair.
7. Substitute factor logs, divide by `c_R`, remove `t`, enumerate ambiguity, recover `x`,
   and accept only if `[x]P=Q` on the original curve.

## Full rho/BSGS cost model

Let `B=N^beta`; surface/model construction `N^(s+o(1))`; curve/function degree,
coefficient-height, and local-expansion charge `N^(g+h+o(1))`; one complete two-stage
boundary attempt `N^(kappa+o(1))`; reciprocal relation success `N^(delta+o(1))`; target
parameters `kappa_t,delta_t`; and full verification `N^(v+o(1))`.

- Pollard rho: `T_rho=N^(1/2+o(1))` with `N^o(1)` state bits.
- BSGS: `T_BSGS=N^(1/2+o(1))` and `M_BSGS=N^(1/2+o(1))` bits.
- Surface, support, and local-table setup: `T_setup=N^(max(s,g+h)+o(1))`.
- Relation collection: `T_rel=N^(beta+delta+kappa+o(1))`, including all candidate symbol
  pairs and all cross-fiber residues.
- Sparse linear algebra: `T_LA=N^(2*beta+o(1))` and `M_LA=N^(beta+o(1))` bits.
- Individual descent: `T_desc=N^(delta_t+kappa_t+o(1))`.
- Complete independent verification: `T_verify=N^(v+o(1))`.
- Total bit memory is `M=N^(max(beta,g,h,m_surface,m_symbol)+o(1))` bits, including
  polynomial coefficients, local expansions, residue tables, failures, and caches.

The full time exponent is
`lambda=max(s,g+h,beta+delta+kappa,2*beta,delta_t+kappa_t,v)` and bit-memory exponent is
`m=max(beta,g,h,m_surface,m_symbol)`. Promotion requires upper bounds below `1/2` for both;
an online target win after a square-root symbol table does not beat rho or BSGS.

## Likely fatal obstruction

The Gersten differential satisfies `d^2=0`. Isolating a useful nonzero divisor on one
fiber may therefore force equally complicated horizontal or auxiliary-fiber terms, so
the apparent bilinear factorization simply distributes a direct S-unit search across the
surface. Symbol degree and coefficient height may grow with the target support, and a
bounded symbol may yield only tautological or known principal divisors. This can produce
an exact theorem-level collapse before any scaling test.

## Proof track

Give an explicit surface and factorable symbol family, prove complete cross-fiber
cancellation and a nontrivial distinguished-fiber relation, and bound symbol enumeration,
height, success density, relation rank, target descent, and bit memory below `1/2`. The
construction must start from `(E,P,R)`, not from a pre-existing supported function.

## Disproof track

Prove that every bounded symbol's distinguished-fiber boundary lies in the directly
generated S-unit relation module with no lower construction cost, or that cross-fiber
balancing has height/output exponent at least `1/2`. An exhaustive bounded-degree result
can close only that exact surface and symbol panel.

## Positive and negative controls

- Positive Gersten control: planted symbols with known tame symbols on `X=E x P^1` must
  reproduce every codimension-one and codimension-two residue exactly.
- Positive relation control: plant a known principal divisor on the distinguished fiber
  and verify that the surface encoding returns it without sign or exceptional-term loss.
- Direct S-unit control: search the same final distinguished-fiber support using one
  rational function on `E`, with matched degree and operation accounting.
- Random-surface control: replace horizontal factor-base lifts with matched random
  sections and preserve all bidegrees.
- Incomplete-boundary control: omit one auxiliary fiber deliberately; the independent
  verifier must reject the certificate.
- Oracle-symbol control: a supplied symbol tests only residues and downstream solving and
  supplies no construction evidence.

## Quantitative promotion and falsification gates

The first theorem/preflight fixes `X=E x P^1` on all eligible ordinary prime-order curves
over `p<=211`, function bidegrees at most `(2,2)`, factor bases `B in {4,6,8}`, and an
exhaustive symbol panel modulo constants and Steinberg-trivial pairs. Promotion only to a
larger study requires zero boundary or relation errors, exact agreement with exhaustive
Gersten truth, at least 1,000 non-oracle distinguished-fiber relations and 100 target
descents, a relation-work advantage of at least `2x` over the direct S-unit control at
matched output and memory, and upper 95 percent bounds `lambda<=0.45`, `m<=0.45`.

Falsify the bounded scope if every accepted target-fiber relation is already generated at
equal or lower cost by the direct S-unit control, if complete reciprocity cancels every
candidate before a useful fiber relation, if any residue is omitted or wrong, or if the
lower full-cost bound is `lambda>=0.50`. Unsupported surface arithmetic and timeouts are
infrastructure results.

## Artifact plan

- Planned contract: `ideas/artifacts/ECDLP-IDEA-040/contract.yaml`
- Planned implementation: `ideas/artifacts/ECDLP-IDEA-040/double_tame_boundary.sage`
- Planned exhaustive panel: `ideas/artifacts/ECDLP-IDEA-040/symbol_panel.json`
- Planned runs: `ideas/artifacts/ECDLP-IDEA-040/runs/<run-id>/`
- Planned boundary traces: `ideas/artifacts/ECDLP-IDEA-040/runs/<run-id>/boundaries.jsonl`
- Planned relation records: `ideas/artifacts/ECDLP-IDEA-040/runs/<run-id>/relations.jsonl`
- Planned analysis: `ideas/artifacts/ECDLP-IDEA-040/analysis.md`
- Retain surface equations, local parameters, every symbol and residue, misses, support
  cycles, costs, peak bit memory, commands, seeds, environment, stdout, stderr, and checksums.

## Interpretation boundary

All assertions are toy, heuristic, model-bound, and novelty-unverified. A correct tame
symbol, complete reciprocity check, valid principal divisor, or recovered planted scalar
is not a breakthrough. Only a non-oracle end-to-end recovery with complete construction,
relation, sparse solve, target, verification, and bit-memory exponents below rho/BSGS
could motivate escalation, and independent replication would still be required.

## Exactly one next executable action

1. Exhaust the bidegree-at-most-`(2,2)` symbol panel on `X=E x P^1` for all eligible prime-order toy curves over `p<=211`, compute complete Gersten boundaries, and compare every useful distinguished-fiber relation with the matched direct S-unit construction cost.
