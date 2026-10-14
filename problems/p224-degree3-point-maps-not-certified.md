# P-224 degree-3 point maps are not certified

- **Status:** `open`
- **Kind:** implementation gap and proof gap
- **Affected work:** complete degree-3 volcano traversal, subgroup transfer, and any P-224 isogenous-representative weakness test
- **Next action owner:** unassigned implementation task
- **Last updated:** 2026-10-13

## Problem

The P-224 screen enumerates four rational linear degree-3 kernels and their
Vélu codomain coefficients, but it has no evaluable two-coordinate map,
normalization witness, dual, composition certificate, subgroup transfer, or
complete component traversal. Codomain adjacency alone cannot support an
ECDLP transfer or weakness conclusion.

## Evidence and uncertainty

- **Observed:** `tools/isogeny_class_screen.py` returns `(a',b')` for a
  degree-3 kernel and lists the four source neighbours. Its focused tests pin
  kernel roots, division-polynomial membership, target `j`-invariants and
  modular-polynomial adjacency, but do not evaluate a point map or dual.
- **Derived or proved:** the archived Frobenius discriminant has `f_pi=3`, so
  the representative conductor is either 1 or 3. That fact alone does not
  identify the level of each endpoint.
- **Suspected explanation:** the screen was intentionally structural and did
  not retain the `u^3` normalization needed for a full `y`-coordinate map.
- **Missing capability:** explicit `phi` and `dual(phi)`, both composition
  identities, exact endpoint conductors and directions, complete graph
  closure, and a subgroup recovery test.
- **What this evidence does not establish:** no endpoint attack, transfer
  advantage, weak representative, or complete eight-vertex component is
  certified by the current one-hop codomains.

## What would unblock it

- [ ] Implement and serialize the degree-3 map for every linear kernel,
  including kernel, exceptional inputs, field, raw codomain and both
  normalization factors.
- [ ] Construct the dual and verify `dual(phi(P))=[3]P` and
  `phi(dual(Q))=[3]Q` on exhaustive toy curves and deterministic P-224
  subgroup samples; verify recovery by `[3^(-1) mod r]`.
- [ ] Traverse to closure, pair reverse edges, and independently certify
  `f_E` and `horizontal|ascending|descending` for every endpoint.

These conditions establish a transfer substrate, not an ECDLP advantage.

## Next discriminating step

- **Action or proof obligation:** implement the specialized short-Weierstrass
  degree-3 rational functions for one kernel, its raw dual, and target
  normalization before expanding the graph.
- **Inputs and controls:** the four P-224 kernels; exhaustive small-prime toy
  curves; wrong-root, wrong-target, wrong-scale and wrong-dual-sign mutations;
  the standard P-224 generator and subgroup order.
- **Execution limits and stop condition:** stop transfer inference on any
  map-to-curve, homomorphism, composition, subgroup-order or recovery failure.
- **Outcomes and next actions:** one passing dual pair admits complete graph
  traversal; a formula failure identifies the invalid identity; complete maps
  with no cheaper endpoint attack remain structural evidence only.
- **Recheck trigger:** a committed P-224 map/dual certificate or an independent
  endpoint-conductor proof.

## Resolution and history

Unresolved. This record does not assert that P-224 is weak or safe.
