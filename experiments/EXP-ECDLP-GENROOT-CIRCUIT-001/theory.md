# Theory preflight: exact five-leaf addition circuit

## Claim boundary

This note proves only that a branch-labeled polynomial circuit can represent
five-term decomposition exactly with constant graph size. It does not provide a
fast generalized-root algorithm. The bounded-root and sparse-completion claims
remain `CONJECTURE`, `HEURISTIC`, and `REVIEW_REQUIRED`.

## Registered setting

Let `p > 3`, and let

```text
E/F_p : y^2 = x^3 + a*x + b
```

have odd prime order `q`. A factor-base registry contains public identifiers

```text
(branch b, accepted source t, orientation, affine point P).
```

For each branch, `M_b(T)` is the squarefree product of exactly the accepted,
non-pole source residues. The rational map is
`phi_b(T)=N_b(T)/D_b(T)`. The registry is authoritative for source fibers and
orientation labels; two identifiers may map to the same point, and repeated
identifier use is allowed.

Write

```text
Reg(b,t,x,y) subset PublicIDs
```

for the exact public decoration relation. An accepted decorated leaf is a
finite-field leaf solution together with one identifier in this relation.
Registry decoration is part of accepted-solution semantics even when the first
solver stage applies it as a checked external filter.

## Exact two-input addition cover

Represent a point as either the distinguished symbol `O` or an affine pair on
`E`. Define `Add_E(P,R,S)` as the following finite, branch-labeled union. An
implementation may enumerate the branch labels or encode them with one-hot
Boolean selectors. The equations below contain no division.

Enumeration is the frozen primary semantics. A future one-hot polynomial
encoding must add Boolean selector equations, an exactly-one equation, and
gated or saturated inactive branch equations; branch priority alone is not an
algebraic selector.

### Left identity

```text
P = O, S = R.
```

This branch also owns `P=R=O`.

### Right identity

```text
R = O, P is finite, S = P.
```

### Ordinary addition

Both inputs and the output are finite. Introduce `lambda,u` and impose

```text
(x_R-x_P)*u = 1
lambda*(x_R-x_P) = y_R-y_P
x_S = lambda^2-x_P-x_R
y_S = lambda*(x_P-x_S)-y_P.
```

### Doubling

Both inputs and the output are finite. Impose `P=R`, introduce `lambda,u`, and
impose

```text
(2*y_P)*u = 1
lambda*(2*y_P) = 3*x_P^2+a
x_S = lambda^2-2*x_P
y_S = lambda*(x_P-x_S)-y_P.
```

### Inverse pair

Both inputs are finite and the output is the identity. Impose

```text
x_R = x_P
y_R = -y_P
S = O.
```

Every finite coordinate tuple in a branch also satisfies the curve equation.
Because `E(F_p)` has odd prime order, it contains no finite point with `y=0`.
Consequently the five cases are disjoint under the stated priority and cover
every pair of subgroup points.

## Five-leaf circuit

For ordered leaves `P_1,...,P_5`, introduce typed intermediate points
`S_2,S_3,S_4` and impose

```text
Add_E(P_1,P_2,S_2)
Add_E(S_2,P_3,S_3)
Add_E(S_3,P_4,S_4)
Add_E(S_4,P_5,Q).
```

For leaf `i` on branch `b_i`, also impose

```text
M_b_i(t_i) = 0
D_b_i(t_i)*x_i-N_b_i(t_i) = 0
D_b_i(t_i)*v_i = 1
y_i^2-x_i^3-a*x_i-b = 0.
```

The inverse witness `v_i` excludes poles. After solving, exact registry lookup
of `(b_i,t_i,x_i,y_i)` returns the public factor identifier or rejects the
candidate. The integer representative bound on `t_i` belongs to the
bounded-root stage, while `M_b_i(t_i)=0` gives exact finite-field membership.
Each bounded-root instance registers a unique lift `0 <= t_i < T_b <= p` for
every accepted source residue. A modular alias invalidates that instance or is
represented as a separate charged candidate.

## Equivalence lemma

**Lemma.** Under the registered setting, the projection to public identifiers of
accepted decorated solutions of the four-gate circuit is exactly the set of
ordered registered five-leaf witnesses for `Q`:

```text
pi_ID(accepted decorated circuit solutions)
  = {ordered registered five-leaf witnesses for Q}.
```

This is equality of projections, not a bijection. Duplicate identifiers may
decorate one coordinate solution, and distinct branch solutions may project to
the same identifier witness.

**Forward direction.** Each leaf equation and pole inverse places `P_i` in the
rational-map fiber; the decoration relation enforces the exact public source,
orientation, and identifier policy. Each selected addition branch is a standard
chord, tangent, inverse, or identity formula, so its output is the elliptic-curve
sum of its inputs. Induction through the four gates gives
`P_1+...+P_5=Q`. Registry rejection prevents an algebraic leaf outside the
accepted public factor base from becoming a witness.

**Reverse direction.** Start from any ordered registered witness. Its accepted
source and point satisfy the leaf equations and have a denominator inverse.
At every partial sum, exactly one case in the addition cover applies. The
ordinary or doubling slope and inverse witnesses exist in their respective
branches. Assigning the true partial sums therefore yields a circuit solution.
Identity intermediates, inverse pairs, doubling, repeated identifiers, and an
identity target are all included.

No permutation quotient is used in this lemma. A later solver may impose a
canonical order only after proving that every multiset witness retains at least
one ordered representative.

## Constant graph size is not a complexity result

There are four addition gates and at most `5^4` branch patterns, a constant in
`B`. For a fixed pattern, the number of coordinate, slope, inverse, and type
variables is `O(1)`. However, each accepted-root equation has degree `B_b`, and
solver shift sets, Macaulay supports, integer coefficient growth, rejected
nonregistry roots, duplicate decorations, candidate-list size, and completion
degree may still be polynomial or exponential in `B`.

At the index-calculus balance `B approximately p^(1/5)`, five interval-like
source bounds have box volume

```text
T_1*T_2*T_3*T_4*T_5 approximately B^5 approximately p.
```

Thus the compact graph alone supplies no generic small-root margin. A positive
preflight requires a concrete shift family and a registered determinant or
root-recovery inequality with nonzero asymptotic slack after every full-field
variable is charged. Until then, the exact circuit is only a correctness
surface and the solver hypothesis remains open.

## Scoped lattice negative

`first-power-box-lattice-negative-v1.md` freezes one explicit tensor-box shift
family. Its `Theta(B^5)` materialized columns and raw generators
unconditionally violate the preprocessing gate. Dense expanded membership
polynomials conditionally give `Theta(B^6)` nonzeros. Its determinant-volume
heuristic has no positive recovery slack because average scaled source degree is
`Theta(B)`, but this does not exclude exceptional short combinations. That
family is `REJECTED_SCOPED` before implementation. Higher-power,
support-adapted, composition-tower, implicit, and non-lattice generalized-root
operators remain outside the result.

## Next concrete action

First replay the decorated projection identity over every feasible typed branch
pattern, including duplicate identifiers and exact selector semantics. Do not
tune the rejected tensor-box shift family. The next positive mechanisms are an
exact composition-tower frontier with width `o(B^1.5)` per attempt or the
separately registered subset-norm root operator.
