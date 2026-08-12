# Experiment Contract: Auxiliary Type-(1,7) Geometric Principalization

Date: 2026-07-29

## Claim status

`HYPOTHESIS / TOY-EVIDENCE / MODEL-BOUND / NOVELTY-UNVERIFIED`

## Hypothesis

Let `E` be an elliptic curve in characteristic different from `2` and `7`,
let `phi:E -> F` be a cyclic isogeny of degree `7`, and put

```text
H = [[2,1],[1,4]],       v = (1,-2),
R = [[2,1],[0,-phi]].
```

Let `g:E x F -> X` be the `(2,2)` gluing isogeny whose kernel is the graph
of `phi` on `E[2]`.  Then `g*R` kills `E^2[2]`, so it factors uniquely as

```text
g*R = q*[2] = [2]*q
```

for a degree-`7` isogeny `q:E^2 -> X`.  The adjoint identity

```text
R^dagger*R = 2H
```

should imply `q^dagger*q=H`.  Thus `q` geometrically realizes a
principalization of the type-`(1,7)` polarization defined by `H`, using one
ordinary elliptic `7`-isogeny and one standard `(2,2)` theta gluing.

On the fixed `GF(29)` ascending fixture, the source and target degree-`7`
directions should give principalized surfaces `X0,X1`.  The exact
degree-`2` commuting square should transport the gluing kernel and hence
descend to `X0 -> X1`.  The auxiliary norm-`23` matrix

```text
A = [[3,-4],[2,5]]
```

should preserve the principalization kernel because

```text
A^T H A = 23H,       A*v = 4v (mod 7).
```

This closes one geometric realization of the auxiliary-lattice Kani
interface for `(n,d,S)=(5,2,23)`, where `25=2+23>8` and `23` is not a sum
of two integer squares.  It does not by itself implement the final
dimension-four `5`-isogeny or prove the advertised asymptotic complexity.

## Null hypothesis

The hypothesis is rejected or narrowed if the registered curve square
changes; the graph is not maximal isotropic; the theta gluing is singular;
`g*R` does not kill all product `2`-torsion; the induced degree-`7` map has
the wrong kernel; the exact adjoint or polarization identities fail; the
degree-`2` square does not transport the gluing graph; `A` does not transport
the type-`(1,7)` kernel; or any semantic mutation passes.

## Parameters

- Base field: `GF(29)`, trace `6`.
- Fixed ascending map: `eta:E0 -> E1` of degree `d=2`, with
  `j(E0)=5`, `j(E1)=12`.
- Fixed commuting degree-`7` direction:
  `phi0:E0 -> F0`, `phi1:E1 -> F1`, and
  `eta_prime:F0 -> F1`, selected by exact square commutation.
- Auxiliary discriminant: `-7`; polarization determinant `delta=7`.
- Kani arithmetic: `S=23`, `n=5`, recovery margin `n^2-4d=17`.
- Polarization and auxiliary matrices:

  ```text
  H=[[2,1],[1,4]]
  A=[[3,-4],[2,5]]
  A^dagger=H^(-1) A^T H
  ```

- Principalization line: the cyclic kernel of each registered degree-`7`
  isogeny, embedded through the multiplicity vector `v=(1,-2)`.
- Gluing kernel: the graph of `phi_i` on full `2`-torsion.
- Deterministic seeds: `20260729`, `20260730`, `20260731`; seeds may vary
  compatible torsion lifts but not curves, maps, graph subgroups, or
  canonical theta invariants.
- Baseline: the source two-squares gate rejects `S=23`, so the integer Kani
  construction uses four squares and abelian dimension `8`.

## Metrics

- exact curve/map degrees, kernels, dual identities, and square commutation;
- full `2`-torsion graph size, rank, and pairing isotropy;
- theta-constructor calls, field degree, wall time, and peak RSS;
- smoothness and canonical invariants of each genus-`2` theta codomain;
- all `16` product `2`-torsion evaluations of `g*R`;
- exact kernel census for `q` on product `7`-torsion when the required
  extension is computationally feasible;
- exact matrix determinant, adjoint, similitude, and transported-line gates;
- degree-`2` transport of the two gluing graphs;
- semantic mutation rejection counts and artifact hashes.

## Positive controls

1. Reconstruct the fixed `GF(29)` degree-`2` ascending square and both
   degree-`7` directions from public curve data.
2. Verify each graph has order `4`, rank `2`, and trivial product Weil
   pairing.
3. Construct each `(2,2)` theta gluing from explicit `8`-torsion lifts and
   obtain a smooth genus-`2` codomain.
4. Verify `g_i*R_i` kills all of `E_i^2[2]`.
5. Verify `det(H)=7`, `det(A)=23`,
   `A^T H A=23H`, `A^dagger*A=A*A^dagger=23I`, and
   `A*v=4v mod 7`.
6. Verify the exact square maps the source graph to the target graph and
   therefore descends between the two principalized theta surfaces.

## Negative controls

1. Replace the graph by a different `2`-torsion isomorphism; require at least
   one nonzero value of `g*R` on `E^2[2]`.
2. Mutate one entry of `R`; require the adjoint identity or divisibility gate
   to fail.
3. Mutate one entry of `A`; require the similitude or transported-line gate
   to fail.
4. Pair mismatched degree-`7` directions; require exact square transport to
   fail.
5. Mutate one byte of the result payload; require the independent verifier
   to reject before accepting arithmetic replay.

## Success criterion

The producer passes only if all three seeds give the same public fixture and
canonical codomain classes; every positive gate passes; each negative control
rejects; and a separate verifier source and process reconstruct the exact
maps, matrices, graph kernels, divisibility checks, and scientific payload
hash without importing the producer.

Passing establishes a geometric type-`(1,7)` principalization primitive for
this auxiliary-lattice fixture.  It does not establish an end-to-end
Galbraith improvement until a charged dimension-four `n`-isogeny backend,
candidate enumeration, and asymptotic auxiliary-search theorem are supplied.

## Falsification criterion

Any mandatory failure is preserved as a scoped `NEGATIVE RESULT` naming the
failed layer.  A successful principalization with no dimension-four Kani
execution remains a component result, not an isogeny-complexity theorem.

## Reproduction commands

```bash
cd /Volumes/Volume/autolab
sage experiments/ecdlp_isogeny/p1243_auxiliary_geometric_principalization.sage.py
sage experiments/ecdlp_isogeny/p1243_auxiliary_geometric_principalization_verify.sage.py
```
