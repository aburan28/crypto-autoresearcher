# Graph-wide factor-base and target-input preparer

This is implementation preparation for the prospective 2,306-vertex study in
`../PROTOCOL-original-draft.md`. It produces one prepared input in the exact
format consumed by the existing `research/conductor_relation_yield_20261014`
triple collector. It does **not** launch that collector or estimate a DLP cost.

## Fixed semantics implemented

- Read only the archived full P29 or P37 walk. Reject incomplete paths,
  discontinuous indices, repeated `j`, or a mismatch with the archived graph
  and independent-verification digests.
- Recover the canonical source generator from the recorded short-Weierstrass
  isomorphism; use each edge's saved transported generator thereafter.
- Build `low_x`, `mid_x`, and `random_x` on every vertex; build `power_x`
  only when the path index is divisible by eight (P29) or four (P37),
  including index zero. Build native and transported bases on the `u=2`
  coordinate model as controls.
- Use one domain-separated 256-bit target root per stratum and stage.
  Derive a nonzero hidden Q scalar and draw `(alpha,beta)` with exact
  modulo rejection. Reject identity and repeated targets by their scalar
  in the prime-order group. Every arm and vertex within a stratum/stage
  receives the same accepted coefficient sequence. Roots for discovery and
  confirmation must differ.
- Require a post-freeze commitment to the base root, target root, archived
  graph manifest, and preparer/dependency source hashes. CLI quotas are fixed
  to the draft discovery/confirmation counts. Output directories are
  exclusive; an interrupted write remains visible and is never overwritten.

`prepare_graph_input.py` exposes a small-count `prepare` function for
implementation controls. Its CLI is for later admitted preparation only;
no commitment or scientific root has been issued in this directory.

## Fixed implementation controls

`test_prepare_graph_input.py` ran 22 eight-target arm/vertex cases on both
strata. It checked repeatability, base sizes and distinct x-orbits, identical
target coefficients across arms, target group equations, the coordinate
transport identity, and the fixed `power_x` index rule. Three saved prepared
fixtures were replayed by `verify_prepared_graph.py` using independent point
arithmetic in `harness.toycurve`; the verifier also checked deterministic
base rules where applicable, signed pairs, uniqueness, group equations,
digests, and post-seal root replay. The raw control outputs and insight report
are in `controls/attempt-1/`.

These controls are not the prescribed discovery or confirmation streams.
They do not validate relation completeness, useful rank, a solver, or speed.
The verifier's optional root replay invokes the preparer and is a
reproducibility check; the point-equation replay uses separate arithmetic.

## Remaining executable obligations

1. Extend the source `low_x` base transport from the first two checked
   degree-7 edges to the complete paths and prespecified check vertices,
   with independent map/dual replay and targetwise equality on the fixed
   discovery targets. The two-edge implementation control and its censored
   predecessor are recorded in `controls/attempt-2/` and `controls/attempt-3/`.
   They use four planted three-point sums per stratum and therefore establish
   map/base arithmetic only, not the fixed discovery-stream equality.
2. Bind the collector, independent ordered-count oracle, rank verifier,
   fixed target roots and all output paths in a runnable versioned contract.
   Coordinator approval under the standing user authorization follows only
   when the execution-state checker reports ready.
3. Build and validate the complete same-point IC solve path: relation
   collection, rank/linear algebra, individual log, independent scalar
   replay, all costs, and matched source/destination rho. Compare any
   completed improvement with the best frozen end-to-end IC baseline for
   that curve and size, reporting the remaining rho and Bernstein–Lange gaps.

The separate 20-arm conductor-step experiment remains governed by its own
frozen plan and recovery record. No data from these fixed implementation
controls enter either study's inference.
The remaining graph-wide implementation and admission obligations are tracked
in [the problem record](../../../problems/isogeny-graph-wide-relation-solver.md).
