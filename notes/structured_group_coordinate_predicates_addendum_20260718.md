# Structured-coordinate barrier addendum, 2026-07-18

## Handoff: complete EC circuit to exact additive-intersection ranks

### Claim or task

Instantiate the structured-coordinate frontier with an actual complete
elliptic addition circuit and identify the exact theorem still needed to prove
compression or expansion.

### Status

- `RESTRICTED THEOREM`: a bound Renes--Costello--Batina circuit gives a
  constant-pre-indicator-rank five-source equality scalar, and the final
  Boolean tensor's TT cut ranks equal concrete partial-sum intersection sizes.
- `NEGATIVE RESULT`, `MODEL-BOUND`: constant input TT rank does not imply a
  compact finite-field zero indicator, even for five modes.
- `OPEN`: prove low-rank construction or additive rank expansion for the
  actual EC intermediate tensors. This does not instantiate the structured
  generic-group model's partial operation or close its coordinate gap.

### Assumptions

- Ordinary generated short-Weierstrass curves over `F_p`, `char(F_p)!=2,3`,
  with a registered odd prime-order subgroup.
- Five modes index `B` signed public identifiers and `q=Theta(B^5)`.
- The complete projective addition tree and equality residual are those frozen
  in `EXP-ECDLP-TT-ZERO-LOCATOR-001/preflight-v2.md`.
- TT ranks are exact unfolding ranks over `F_(p^2)` in the registered mode
  order.

### Evidence so far

Four complete projective additions produce

```text
S=P_(i1)+...+P_(i5)=(X:Y:Z).
```

For `Q=(X_Q:Y_Q:Z_Q)` and a quadratic basis element `omega`, the scalar

```text
g_Q=(X*Z_Q-X_Q*Z)+omega*(Y*Z_Q-Y_Q*Z)
```

vanishes exactly when `S=Q`, including `Q=O`. Because the bound addition tree
is a fixed polynomial circuit, `g_Q` has a formal CP and TT rank upper bound
independent of `B`. This is a concrete coordinate predicate, not an abstract
generic-group oracle.

The exact Boolean relation tensor is

```text
Zcal_Q=1-g_Q^(p^2-1).
```

At cut `k|(5-k)`, let `D_k` and `D_(5-k)` be the distinct registered partial
sums. Its unfolding is a disjoint union of all-one blocks, one for every
matching group element. Therefore

```text
rank(Zcal_Q^<k>)=|D_k intersect (Q-D_(5-k))|.
```

This is the missing concrete additive interpretation: final TT width is not an
opaque tensor statistic. It is exactly the number of compatible partial-sum
values. In a random-sum heuristic with `|D2| approximately B^2`,
`|D3| approximately B^3`, and `q approximately B^5`, the expected central
rank is constant. That explains why the final witness tensor can be tiny; it
does not explain how to find the intersection.

The algebraic indicator route contains `Theta(log p)` exact Hadamard products.
An intermediate central rank `Omega(B)` already forces `Omega(B^2)` standard
dense TT core words. Thus either of the following would settle the specified
route on paper:

1. **Positive track:** exhibit exact witness-preserving row-space bases for
   every intermediate with cumulative work, traffic, and peak state
   `o(B^2)`.
2. **Negative track:** construct one explicit `B by B` nonsingular minor in an
   intermediate central unfolding, or otherwise prove central rank
   `Omega(B)`.

A universal positive theorem is impossible. Over `F_p`, `p>B^2`, the
five-mode rank-two scalar

```text
g=i1+B*i2-i3-B*i4
```

has Fermat indicator

```text
1-g^(p-1)=delta_(i1,i3)*delta_(i2,i4),
```

whose registered central unfolding has rank exactly `B^2`. Special elliptic
structure must therefore do all the work.

This result does not turn a unary coordinate predicate or recursive circuit
into the structured generic-group model's compatible partial binary operation.
The earlier `delta`-density theorem remains a model-aware comparison, not a
lower bound for this concrete representation.

### Failure modes

- Calling low final intersection rank a cheap construction theorem.
- Treating constant circuit size or pre-indicator rank as stable under the
  finite-field zero map.
- Using random-sum expected intersection size as a worst-case or high-
  probability rank theorem without measuring collisions and target classes.
- Applying the generic five-mode counterexample as a rank lower bound for EC.
- Claiming that this coordinate construction instantiates structured-generic
  `delta` without a valid partial-operation embedding.
- Reporting one target decomposition as an ECDLP improvement without relation
  count, canonical rank yield, linear algebra, and descent.

### Next concrete action

Derive the exact `(12)|(345)` unfolding after every gate of the bound RCB plus
norm-indicator circuit and search symbolically for either a sub-`B` row-space
basis or a `B by B` nonsingular minor; keep both proof and disproof tracks.

### Artifact paths

- `notes/structured_group_coordinate_predicates_literature_20260717.md`
- `experiments/EXP-ECDLP-TT-ZERO-LOCATOR-001/preflight-v2.md`
- `experiments/EXP-ECDLP-TT-ZERO-LOCATOR-001/literature-review-v1.md`
