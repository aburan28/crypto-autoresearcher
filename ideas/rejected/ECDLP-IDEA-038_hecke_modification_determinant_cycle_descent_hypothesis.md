# ECDLP-IDEA-038 — Hecke-modification determinant-cycle descent

## Status and claim labels

- Class: `representation`
- Risk band: `high-risk`
- State: `proposed_unapproved`
- Evidence scale: `toy` graph preflight only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; bundle construction, a Hecke path, or determinant correctness is not a break.

## Falsifiable hypothesis

For some fixed or slowly growing rank `r`, determinant-balanced Hecke modifications on
semistable vector bundles over a generic ordinary prime-field elliptic curve create a
public nonabelian state graph in which paths with prescribed determinant can be found
more cheaply than relations in the direct Cayley graph of `E(F_p)`. Projecting those paths
through `det:Bun_r(E)->Pic^0(E)=E` yields enough factor-base relations and a separate
target path that total time and bit-memory exponents are below `1/2`.

The claim is not that vector bundles or Hecke correspondences exist. It predicts that
internal bundle states supply an algorithmic path-density or canonical-collision gain
that survives exact determinant projection, state construction, relation collection,
linear algebra, and individual descent.

## Mechanism-new operation

Represent `R` by the canonical bundle `V_R=O_E^(r-1) direct_sum L_R`. A paired elementary
modification at a factor-base point and an inverse modification at the origin preserves
rank and degree while multiplying the determinant by `L_(F_i-O)`. Search the resulting
Hecke graph for a certified path from `V_O` to `V_R`; its signed modification labels give
a relation for `R`.

The new operation is **nonabelian Hecke-state path search with determinant projection**.
It is not a Fourier-Mukai restatement, a scalar-orbit dictionary, a matrix solver applied
to the original group, or a post-hoc choice of a path known to encode the toy logarithm.

## Assumptions

1. `E/F_p` is ordinary with a known prime subgroup `<P>` of order `N=p^(1+o(1))`, and
   `Q=[x]P`.
2. Rank `r`, stability convention, canonical endpoint construction, and paired upper/lower
   Hecke move are fixed before any target query.
3. Bundle isomorphism or S-equivalence, determinant, exceptional modifications, and move
   inverses are computed exactly; hashes are never accepted as equality proofs.
4. A target-independent factor base `{F_i}` of size `B=N^beta` labels the permitted Hecke
   moves; no move label contains `log_P(F_i)`.
5. Canonical reduction of intermediate bundles is public and charges all field operations,
   coefficient growth, branch enumeration, and failed isomorphism tests.
6. Any toy path-density model is heuristic and model-bound, and novelty remains unverified.

## Semantic fingerprint

`elliptic_vector_bundle_moduli | paired_Hecke_modification | internal_nonabelian_state_graph | determinant_path_certificate | projected_E_relation | frozen_target_path_descent`

If internal bundle state is erased, the graph becomes the ordinary factor-base Cayley
graph. If a Fourier-Mukai equivalence is invoked without a path-finding theorem, or the
correct endpoint is selected using the hidden scalar, the proposal merges with a rejected
representation or orbit-label control.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — supplies the generic prime-field relation-density floor
   that internal state must beat rather than rename.
2. `ledger/H-FB-001.yaml` — excludes interpreting a special set of Hecke labels as the new
   mechanism.
3. `ledger/EV-FB-001.yaml` — provides the direct random/structured relation-yield control.
4. `ledger/H-REP-001.yaml` — requires an exponent-changing operation beyond a different
   coordinate or equation model.
5. `ledger/SYNTHESIS-20260716.md` — fixes end-to-end rho/BSGS and independent-verification
   requirements.

## Closest primary literature

- Atiyah, [Vector bundles over an elliptic curve](https://doi.org/10.1112/plms/s3-7.1.414), classifies the nearby bundle states and is a likely source of a quotient-collapse theorem.
- Burban and Schiffmann, [On the Hall algebra of an elliptic curve, I](https://arxiv.org/abs/math/0505148), describes Hall/Hecke structure for coherent sheaves on elliptic curves.
- Laszlo, [About G-bundles over elliptic curves](https://doi.org/10.5802/aif.1623), gives nearby moduli structure that constrains internal-state multiplicity.

None supplies a sub-square-root determinant-path algorithm. The literature comparison
establishes proximity only, not novelty.

## Complete factor-base-to-target-descent path

1. Freeze `(E,P,N)`, rank `r`, the exact bundle representation, canonical endpoints
   `V_R`, determinant normalization, and the paired Hecke move for every permitted point.
2. Construct `B=N^beta` factor-base labels `F_i` and their forward and inverse modification
   operators without using `Q` or any toy logarithm.
3. For a frozen stream of known `a`, construct `V_[a]P` and run the preregistered path
   algorithm from `V_O`; retain all explored states, failures, duplicate certificates, and
   canonicalization costs.
4. Accept a path only after exact composition and endpoint isomorphism checks. Project its
   determinant labels and independently verify `[a]P=sum_i e_i F_i` on `E`.
5. Collect `B+margin` independent projected rows and solve all factor-base logarithms,
   charging path dependencies and sparse linear algebra.
6. Freeze the graph, caches, and base logs, then apply the same path algorithm to canonical
   bundles for `Q+[t]P` under preregistered public randomizers `t`.
7. Project the target path, substitute base logs, remove `t`, retain all ambiguities,
   recover `x mod N`, and accept only after `[x]P=Q`.

## Full rho/BSGS cost model

Let `r=N^(mu+o(1))`, factor-base size `B=N^beta`, bundle/Hecke setup
`N^(s+o(1))`, one fully canonicalized state expansion `N^(kappa+o(1))`, reciprocal
relation-path success `N^(delta+o(1))`, stored explored-state count `N^sigma`, and target
path parameters `kappa_t,delta_t`.

- Pollard rho baseline: `T_rho=N^(1/2+o(1))`, with `N^o(1)` state bits.
- BSGS baseline: `T_BSGS=N^(1/2+o(1))` and `M_BSGS=N^(1/2+o(1))` bits up to logarithmic factors.
- Setup: `T_setup=N^(max(s,mu)+o(1))`.
- Relation collection: `T_rel=N^(beta+delta+kappa+o(1))`.
- Sparse linear algebra: `T_LA=N^(2*beta+o(1))` and `M_LA=N^(beta+o(1))` bits.
- Individual descent: `T_desc=N^(delta_t+kappa_t+o(1))`.
- Exact bundle encodings and visited states require
  `M=N^(max(beta,mu,sigma,m_coeff)+o(1))` bits; every field element contributes
  `Theta(log p)` bits and is included.

The complete time exponent is
`lambda=max(s,mu,beta+delta+kappa,2*beta,delta_t+kappa_t)` and the bit-memory exponent is
`m=max(beta,mu,sigma,m_coeff)`. Both upper bounds must be below `1/2`; a shorter online
target path after an `N^(1/2)` graph build is not a win.

## Likely fatal obstruction

The determinant is a graph quotient: every internal Hecke path projects to the same
sequence of Cayley moves. Atiyah-style classification may show that internal state
multiplicity expands the number of vertices and paths by the same factor, leaving the
probability of a useful projected relation unchanged or worse. Canonical bundle
isomorphism can also cost as much as exploring the direct determinant graph. The most
likely result is an exact quotient-collapse theorem rather than an algorithmic gain.

## Proof track

Define a rank family and canonicalization with a provable many-path advantage conditioned
on determinant, then give a path-reporting algorithm whose work is output-sensitive in
useful projected paths. Prove the determinant certificate, relation rank, target descent,
and full time/bit-memory inequalities without an endpoint oracle.

## Disproof track

Use the classification of semistable bundles to construct an explicit graph quotient or
lumping showing that the conditional distribution of determinant paths equals the direct
Cayley distribution. A lower bound `beta+delta+kappa>=1/2`, state memory
`sigma>=1/2`, or target endpoint recognition equivalent to ECDLP also rejects the scope.

## Positive and negative controls

- Positive mechanics control: planted short Hecke paths with hidden labels validate move
  composition, canonicalization, endpoint isomorphism, and determinant projection.
- Exhaustive truth control: enumerate every rank-2 S-equivalence class and permitted move
  on the smallest curves.
- Direct quotient control: the Cayley graph on `E(F_p)` with precisely the same determinant
  moves and operation budget.
- State-shuffle control: randomly permute internal bundle states inside each determinant
  fiber while preserving fiber sizes and degrees.
- Oracle-path control: reveal a path only to test projection and downstream solving; it
  cannot support the non-oracle claim.
- Target-leakage control: changing the graph or canonicalization after seeing `Q` invalidates
  the run.

## Quantitative promotion and falsification gates

The bounded preflight uses all eligible ordinary prime-order curves over `p<=251`, ranks
`r in {2,3}`, bases `B in {4,6,8,12}`, and exact graph enumeration whenever the full state
set has at most one million vertices. Promotion only to a scaling study requires zero
incorrect paths, exact determinant and exhaustive-graph agreement, at least 1,000
non-oracle relation paths and 100 target paths, a useful projected-path work advantage of
at least `2x` over the direct Cayley control at matched memory on each of the two largest
sizes, and upper 95 percent bounds `lambda<=0.45`, `m<=0.45`.

Falsify if the exact quotient graph has identical projected first-hit distribution, the
advantage vanishes after equal-state/equal-memory controls, any endpoint certificate is
wrong, or every valid configuration has lower 95 percent `lambda>=0.50`. A timeout or
missing bundle routine is infrastructure, not a mathematical negative.

## Artifact plan

- Planned contract: `ideas/artifacts/ECDLP-IDEA-038/contract.yaml`
- Planned implementation: `ideas/artifacts/ECDLP-IDEA-038/hecke_graph.sage`
- Planned exhaustive states: `ideas/artifacts/ECDLP-IDEA-038/exhaustive_states.jsonl`
- Planned paths: `ideas/artifacts/ECDLP-IDEA-038/runs/<run-id>/paths.jsonl`
- Planned quotient controls: `ideas/artifacts/ECDLP-IDEA-038/runs/<run-id>/quotient.json`
- Planned analysis: `ideas/artifacts/ECDLP-IDEA-038/analysis.md`
- Retain exact bundle encodings, move traces, isomorphism certificates, determinants,
  misses, relation rows, costs, peak bit memory, commands, seeds, environment, and checksums.

## Interpretation boundary

All claims are toy, heuristic, model-bound, and novelty-unverified. A correct bundle,
Hecke move, endpoint isomorphism, determinant identity, or planted path is not a
breakthrough. Only non-oracle scalar recovery with complete setup, relation, sparse solve,
target, verification, and bit-memory exponents below rho/BSGS could justify escalation.

## Exactly one next executable action

1. Enumerate the complete paired-Hecke and determinant-quotient graphs for ranks `2` and `3` on all eligible prime-order toy curves over `p<=251`, and test exact lumpability against the matched Cayley graph.
