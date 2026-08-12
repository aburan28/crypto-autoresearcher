# PO48 Theory and Red Team: Richelot Visibility Obstruction

## Claim Status

- `RESTRICTED THEOREM`: a homomorphism from a Jacobian to an elliptic curve
  always induces a curve-to-elliptic map after composing with the Abel-Jacobi
  embedding.
- `RESTRICTED THEOREM`: composing a degree-two elliptic quotient with one
  Richelot `(2,2)` edge induces a degree-four map from the Richelot neighbor to
  the elliptic curve.
- `RESTRICTED THEOREM`: dual target transport maps `T` to a genus-two
  Jacobian class whose forward image is `[4]T`.
- `NEGATIVE RESULT / MODEL-BOUND`: PO48's registered requirement that the
  elliptic factor be hidden from every degree-at-most-four curve map is
  incompatible with its proposed transfer.
- `OPEN`: non-homomorphic incidence objects with independently verified norm
  or factorization semantics are not covered by this obstruction.

## Assumptions

Let `k` have characteristic different from two. Let `C0` and `C1` be smooth
genus-two curves with rational base points and principally polarized Jacobians
`J0` and `J1`. Let

```text
rho:J1 -> J0
```

be a separable Richelot isogeny. Let `f0:C0->E` be a separable degree-two
elliptic quotient and write

```text
q=(f0)_*:J0->E.
```

All adjoints are Rosati adjoints under the principal polarizations.

## Theorem 1: Every Jacobian Quotient Is Curve-Visible

Fix a base point `P0` and the Abel-Jacobi embedding

```text
i0:C->Jac(C),  P |-> [P-P0].
```

For any nonzero homomorphism `psi:Jac(C)->E`, the composition

```text
f=psi o i0:C->E
```

is a nonconstant morphism. By the universal property of the Jacobian, the
induced pushforward `f_*` is `psi`. Conversely, every based morphism to `E`
extends uniquely to such a homomorphism.

Therefore a homomorphic elliptic transfer from a curve Jacobian cannot be
map-invisible. A correspondence may obscure the formula or raise its degree,
but it does not evade this equivalence.

## Theorem 2: One Richelot Edge Produces Degree Four

The degree-two map satisfies

```text
q q^dagger = [2]_E.
```

For a Richelot `(2,2)` isogeny,

```text
rho rho^dagger = [2]_{J0}.
```

Define the PO48 transfer

```text
psi = q rho:J1->E.
```

Then

```text
psi psi^dagger
  = q rho rho^dagger q^dagger
  = q [2] q^dagger
  = [4]_E.
```

Let `f1=psi o i1:C1->E`. Albanese/Picard duality gives
`(f1)_*=psi` and `(f1)^*=psi^dagger`. For a finite separable curve map,

```text
(f1)_* (f1)^* = [deg(f1)]_E.
```

Hence

```text
deg(f1)=4.
```

More generally, composing a degree-`d` elliptic quotient with an
`(ell,ell)` polarized isogeny satisfying `rho rho^dagger=[ell]` produces a
curve map of degree `ell*d`.

## Theorem 3: The Bounded Target Class Is Standard Transport

The dual map sends a public target to

```text
D_T=psi^dagger(T) in J1(k).
```

Applying the forward transfer gives

```text
psi(D_T)=[4]T.
```

Every class in a genus-two Jacobian has a reduced Mumford representative of
degree at most two. Thus PO48's target-degree bound is true, but it is true for
every transported Jacobian class and does not establish factor-base
smoothness, cheap decomposition, or a hidden channel. It is a representation
bound, not a target-fiber advantage.

## Contract Conflict

PO48 simultaneously requires:

1. the explicit nonzero homomorphism `psi=q rho`; and
2. no degree-at-most-four map `C1->E` in the registered exact model.

Theorem 2 constructs exactly such a degree-four map. No parameter search can
make both gates pass under the stated assumptions. The construction stage is
therefore closed before run; implementing it would only reproduce a known
visible quotient in a less direct presentation.

## Narrowest Negative Result

One non-decomposed Richelot edge after a degree-two split quotient cannot hide
the elliptic factor from low-degree curve maps. This does not say that all
Richelot representations have identical constants, and it does not rule out
higher-degree maps, non-Jacobian source objects, or non-homomorphic incidence
labels. It rules out PO48's claimed attribution mechanism.

## Next Positive Question

What non-homomorphic object supplies a factorization or batch-incidence
predicate while exact pushed relations remain verifiable on `E`?

The surviving registered candidate is PO8's balanced cubic Hesse norm. It
uses a cyclic-cover label and a determinant norm rather than a Jacobian
homomorphism. The first gate is an actual batch query over balanced block
evaluation rows, compared with the direct expanded-norm implementation after
image deduplication and full preprocessing charge.

## Handoff: Richelot obstruction to balanced Hesse norm

### Claim or task

Test whether a non-homomorphic balanced norm label supports a batch query that
cannot be reproduced at comparable cost by the direct elliptic baseline.

### Status

OPEN

### Assumptions

- The Richelot negative is restricted to homomorphic Jacobian transfers.
- PO7 closed only the linear Kummer function `z-v`.
- PO8's multi-coefficient Hesse norm and batch-query hypothesis are untested.

### Evidence so far

- PO45-PO47 show functionality without hidden attribution or cost advantage.
- PO6 proves fixed split-cover cofibers do not supply reusable rank.
- The theorem above makes PO48's low-degree-map exclusion impossible.

### Failure modes

- Hesse evaluation rows may be projectively generic.
- Direct elliptic preprocessing may reproduce the same query.
- Preprocessing memory or query cost may exceed rho.

### Next concrete action

Implement PO8's symbolic norm, exact `L(kO)` bases, planted quartic residual,
and projective incidence statistics at `m=4` before opening relation rank.

### Artifact paths

- `research/PO_transfer_048_bounded_richelot_contract.md`
- `research/PO_transfer_048_theory_red_team.md`
- `research/PO_transfer_008_contract.md`

