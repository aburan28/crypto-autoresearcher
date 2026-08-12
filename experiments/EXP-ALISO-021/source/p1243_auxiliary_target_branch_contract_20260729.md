# Experiment Contract: Auxiliary Principalization Target-Branch Enumeration

Date: 2026-07-29

## Claim status

`HYPOTHESIS / TOY-EVIDENCE / MODEL-BOUND / NO COMPLEXITY CLAIM`

## Hypothesis

On the fixed `GF(29)` degree-`2` ascending fixture with auxiliary
discriminant `-7`, all `delta+1=8` cyclic target lines in `E1[7]` can be
enumerated without the hidden isogeny.  Each line should yield:

1. a cyclic `7`-isogeny `phi1:E1 -> F1`;
2. a graph `(2,2)` gluing of `E1 x F1`;
3. a geometric principalization `q1:E1^2 -> X1`.

The hidden degree-`2` map is used only after construction to label which line
equals `eta(ker(phi0))`.  Exactly one of the eight branches should be
compatible with the fixed source line.  This replaces the earlier uncharged
target-line oracle by an explicit branch factor `delta+1`.

## Null hypothesis

The hypothesis is rejected or narrowed if full `7`-torsion is unavailable in
the preregistered field; the line census is not exactly eight; line kernels
collide; a branch cannot construct its cyclic isogeny or principalized theta
surface; more or fewer than one branch contains `eta(ker(phi0))`; or a
mutated/omitted line passes the completeness hash.

## Parameters

- Base field: `GF(29)`, trace `6`.
- Full computation field: `GF(29^24)`, the least common extension degree
  registered for full `7`- and `8`-torsion.
- Hidden audit map: fixed degree-`2` ascending `eta:E0 -> E1`.
- Fixed source line: kernel of the first canonical degree-`7` direction
  `phi0:E0 -> F0`.
- Target line enumeration: `P+tQ` for `t=0..6`, plus `Q`, for a
  deterministic symplectic basis `(P,Q)` of `E1[7]`.
- Principalization matrix:

  ```text
  H=[[2,1],[1,4]], R=[[2,1],[0,-phi1]].
  ```

- Deterministic seeds: `20260729`, `20260730`, `20260731`.
- Baseline: the previous geometric probe supplied the correct target
  direction; this successor must construct all target branches before using
  `eta`.

## Metrics

- target line count and subgroup hashes;
- cyclic-isogeny construction count and degrees;
- theta-constructor calls, smooth/product codomain classification, canonical
  codomain hashes, field degree, wall time, and peak RSS;
- `gR` product-`2`-torsion zero census for every branch;
- compatible-branch count and index;
- distinct line, codomain, and scientific payload hashes;
- complete charged branch factor.

## Positive controls

1. Reconstruct exactly eight distinct cyclic subgroups of `E1[7]`.
2. Construct a degree-`7` quotient for every subgroup and verify its kernel.
3. Construct a valid principalization for every branch and require `gR` to
   kill all `16` product `2`-torsion points.
4. Require exactly one target quotient to kill `eta(P0)`, where `P0`
   generates the fixed source line.
5. Require the compatible branch to equal the direction selected by exact
   square commutation in the earlier fixture.

## Negative controls

1. Omit one projective line and require the completeness hash/count to fail.
2. Duplicate one line and require the subgroup-distinctness gate to fail.
3. Pair a wrong target line with the source square and require kernel
   transport to fail.
4. Mutate one payload byte and require an independent verifier to reject.

## Success criterion

All three seeds enumerate the same eight subgroups, construct all eight
principalizations, and identify exactly one transported branch.  All
mutations reject, and an independent verifier replays the line census,
kernel checks, branch count, and scientific hash without importing the
producer.

Passing removes an uncharged target-line oracle for this toy
principalization.  It does not remove the factor `delta+1`, prove that
`delta=q^o(1)`, execute the dimension-four Kani isogeny, or establish an
end-to-end recovery improvement.

## Reproduction commands

```bash
cd /Volumes/Volume/autolab
sage experiments/ecdlp_isogeny/p1243_auxiliary_target_branch.sage.py
sage experiments/ecdlp_isogeny/p1243_auxiliary_target_branch_verify.sage.py
```
