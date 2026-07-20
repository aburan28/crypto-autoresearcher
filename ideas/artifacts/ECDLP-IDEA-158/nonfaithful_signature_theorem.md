# IDEA-158 x-only Kummer WNU interpretation gate

Status:
`SCOPED_NEGATIVE_FULL_S3_KUMMER_SIGNATURE_PP_INTERPRETS_ADDITION__HIGH_ARITY_SIGNATURE_OPEN`

This is a theorem-only producer receipt. No contract, CSP solver, finite
instance, relation campaign, toy curve, or timing run was executed. It screens
the natural x-only operation proposed by ECDLP-IDEA-158: use a non-affine weak
near-unanimity (WNU) polymorphism on the x-coordinate Semaev relation and a
sparse x-factor base, then lift quotient solutions to signed sources.

The result is all-arity but scoped to a signature containing the full ternary
Kummer/Semaev relation `S3=0`, public adjacent constants, and the sparse
factor-base unary relation. A deliberately weaker high-arity-only signature
that does not primitive-positive interpret this structure remains outside the
theorem and must separately provide complete source lifting.

## Frozen Kummer structure

Let

```text
G = <P> ~= Z/NZ
```

with prime `N>=5`. Let

```text
K = G/{+1,-1}
```

and write `[t]` for the sign orbit `{t,-t}`. The ternary x-only relation is

```text
T([a],[b],[c])
  iff [c] is [a+b] or [a-b]
  iff there exist signs ea,eb,ec with ea*a+eb*b+ec*c=0.
```

On a short-Weierstrass elliptic curve this is the rational-point Kummer
restriction of `S3(x_a,x_b,x_c)=0`, with the usual point-membership and
exceptional-chart conditions handled separately.

Fix any nonzero `g in G`. Since `N` is prime, `g` generates `G`. The public
points `P,[2]P,[3]P` provide the constants `[g],[2g],[3g]`; no scalar secret is
used.

Let `F_x subset K` be the target-independent x-factor base. Its oriented lift
is

```text
F_tilde = {t in G: [t] in F_x}.
```

For a cryptanalytic factor base, `1<|F_tilde|<N`.

## Lemma 1: four Kummer states encode one oriented group element

Define

```text
Enc(t) = ([t],[t+g],[t+2g],[t+3g]) in K^4.
```

Define `D(a0,a1,a2,a3)` by the six ternary atoms

```text
T(ai,[(j-i)g],aj)  for every 0<=i<j<=3.
```

Then

```text
D = {Enc(t): t in G},
```

and `Enc:G-->D` is a bijection.

Proof. Choose a lift `t` of `a0`. The three atoms based at `a0` imply

```text
ai = [t+ei*i*g],  ei in {+1,-1}.
```

Changing `t` to `-t` if necessary makes `e1=+1`. The atom between positions
1 and 2 says

```text
[t+e2*2g] is in {[t],[t+2g]}.
```

The `e2=+1` branch is desired. If `e2=-1`, equality with `[t+2g]`
either gives the same sign orbit or requires `4g=0`; equality with `[t]`
either requires `2g=0` or leaves the one distinct possibility `t=g` and
`a2=[g]`. On that possibility the three constraints for `a3` require

```text
a3 in {[4g],[2g]} intersection {[0],[4g]} intersection {[0],[2g]},
```

which is empty for prime `N>=5`.

Thus `a2=[t+2g]`. The position-0 constraint leaves
`a3=[t+3g]` or `[t-3g]`. If the latter orbit is distinct, the position-1
constraint forces `t=2g`, while the position-2 constraint forces `t=g`;
the alternatives instead require `2g=0` or `4g=0`. Hence no distinct minus
branch survives and `a3=[t+3g]`. Thus every tuple is `Enc(t)`.

If `Enc(t)=Enc(u)`, the first coordinate gives `u=t` or `u=-t`. In the second
case the second coordinate would require `[t+g]=[-t+g]=[t-g]`, which for odd
prime `N` forces the coincident `t=0` case and still gives `u=t`. Hence the
encoding is injective.

All six constraints are primitive-positive atoms of the x-only relation with
public constants.

## Lemma 2: seven x-only atoms define oriented addition

Let

```text
A=Enc(alpha), B=Enc(beta), C=Enc(gamma).
```

Define `Add_D(A,B,C)` by the seven atoms

```text
T(Ai,B0,Ci)  for i=0,1,2,
T(A0,Bj,Cj)  for j=0,1,2,
T(A1,B1,C2),
T(A1,B2,C3).
```

The atom with `i=j=0` is shared by the first two rows, so the displayed list
contains seven distinct constraints. Then

```text
Add_D(Enc(alpha),Enc(beta),Enc(gamma))
  iff gamma=alpha+beta in G.
```

Proof. The forward direction follows by choosing the plus branch in every
Kummer sum.

For the reverse direction, scale by `g^(-1)` and write it as `g=1`. For
fixed `beta`, the three first-row atoms say that for `i=0,1,2`,

```text
[gamma+i] is in [alpha+i] plus/minus [beta].
```

Equivalently the quadratic polynomial in `i`

```text
((gamma+i)^2-(alpha+i+beta)^2)
*((gamma+i)^2-(alpha+i-beta)^2)
```

vanishes at three distinct field elements. Its two variable factors are
linear in `i`; therefore one constant factor vanishes and

```text
gamma=alpha+beta  or  gamma=alpha-beta.
```

The three second-row atoms similarly give

```text
gamma=alpha+beta  or  gamma=beta-alpha.
```

If the desired first alternative does not hold, then odd characteristic
forces

```text
alpha=beta, gamma=0.
```

The mixed atom `T(A1,B1,C2)` then requires

```text
[2] in {[0],[2alpha+2]},
```

leaving only `alpha=0` or `alpha=-2`. The first is already the desired sum.
For the second, `T(A1,B2,C3)` becomes

```text
T([-1],[0],[3]),
```

which would require `[3]=[1]`, impossible for prime `N>=5`. Thus only
`gamma=alpha+beta` survives.

This is a four-dimensional primitive-positive interpretation of the faithful
addition graph inside the full ternary x-only Kummer structure. It is stronger
than merely reconstructing signs after a solution is known.

## Lemma 3: every x-only WNU transfers to faithful addition

Let

```text
w:K^k-->K,  k>=3,
```

be idempotent, satisfy the WNU identities, preserve `T`, and preserve `F_x`.
Apply `w` coordinatewise to `k` encoded tuples in `D`. Because `D` and
`Add_D` are primitive-positive definitions using `T` and constants, and
idempotence fixes each repeated constant, coordinatewise `w` preserves both
relations.

Transport the result through `Enc` to obtain

```text
W:G^k-->G.
```

Then `W` is idempotent, satisfies the same WNU identities, and preserves the
faithful graph

```text
Add={(x,y,z):x+y=z}.
```

Moreover the relation

```text
D(A) and F_x(A0)
```

is primitive-positive and represents `F_tilde`. Therefore `W` preserves the
proper nontrivial oriented factor base `F_tilde`.

## Theorem: the natural x-only signature has no sparse-base WNU

Preservation of faithful `Add` makes `W:G^k-->G` a group homomorphism:

```text
W(u+v)=W(u)+W(v).
```

Hence

```text
W(x1,...,xk)=sum_i ai*xi.
```

Idempotence gives `sum_i ai=1`. The WNU identities make every `ai` equal. If
`N` divides `k`, these equations are inconsistent. Otherwise

```text
W(x1,...,xk)=k^(-1)*(x1+...+xk).
```

For the proper nontrivial set `F_tilde`, iterated Cauchy-Davenport gives

```text
|k*F_tilde| >= min(N,k*|F_tilde|-k+1) > |F_tilde|.
```

Multiplication by `k^(-1)` is a bijection, so

```text
W(F_tilde^k) is not a subset of F_tilde.
```

This contradicts the preservation transferred from `F_x`. Therefore no
idempotent WNU of any arity `k>=3` preserves the full ternary Kummer relation,
the public adjacent constants, and a proper nontrivial x-factor base.

The exact signed source lift is never reached: the required quotient WNU does
not exist on this signature.

## Relation to ECDLP-IDEA-146

IDEA-146 proved the affine/WNU/Cauchy-Davenport obstruction when faithful
signed addition is already basic or primitive-positive definable. The two
encoding lemmas above remove IDEA-158's natural recursive-`S3` exception:
four adjacent x-only windows primitive-positive interpret that faithful
addition graph without choosing a y-sign or using a source table.

The result is representation-level, not a claim that one x-coordinate alone
is faithful. Orientation is carried by a constant-size tuple of adjacent
Kummer states.

## Surviving high-arity exception

This theorem does not cover a language that deliberately omits the full
ternary Kummer relation and exposes only a high-arity relation that cannot
primitive-positive define the seven-atom addition gadget. Such a successor
must prove all of the following before implementation:

1. exact noninterpretability of the ternary Kummer gadget even with public
   constants and pinned intermediate variables;
2. a non-affine WNU or the full bounded-width algebra on that exact language;
3. preservation of the sparse x-factor base;
4. a source-biconditional all-sign lift without adding relations that restore
   the gadget; and
5. complete relation, rank, factor-log, masked-descent, output, time, and
   memory exponents at most `0.45`.

A solver substitution, an `S_m` relation recursively implemented with `S3`,
or a lift exposing adjacent Kummer transitions falls back inside the theorem.

## Cost disposition

For the full recursive-`S3` language, the required WNU constructor does not
exist, so no finite query exponent follows from bounded width. Dropping the
factor-base relation loses source recovery. Dropping `S3` creates the
high-arity theorem obligation above; recursively evaluating it with `S3`
restores this no-go, while explicit source completion restores the P1511/P1515
state costs.

No relation campaign, factor-log recovery, blind descent, generic-prime
below-rho algorithm, Shoup-bound improvement, or breakthrough is established.

## Independent review checklist

An independent reviewer should verify:

1. the six distance atoms define exactly the four-state encoding `Enc(G)`;
2. the seven cross atoms define `gamma=alpha+beta`, including the exceptional
   `alpha=beta=-2, gamma=0` branch;
3. the encoding is a primitive-positive interpretation, not an assumed sign
   oracle;
4. coordinatewise WNU application preserves the interpreted domain and
   addition graph;
5. `D(A) and F_x(A0)` represents the oriented lift of the x-factor base;
6. faithful-addition preservation forces the coefficient form;
7. the all-arity WNU and Cauchy-Davenport cases are complete; and
8. the high-arity-only noninterpretability exception remains open.

## Primary references

- Chalcraft and Fryers, *Kummer structures*:
  <https://arxiv.org/abs/0806.0409>.
- Barto and Kozik, *Constraint Satisfaction Problems of Bounded Width*:
  <https://doi.org/10.1109/FOCS.2009.32>.
- Davenport, *On the Addition of Residue Classes*:
  <https://doi.org/10.1112/jlms/s1-10.37.30>.
- Semaev, *Summation polynomials and the discrete logarithm problem on
  elliptic curves*: <https://eprint.iacr.org/2004/031>.

The references supply Kummer reconstruction, WNU/bounded-width, sumset, and
elliptic-relation controls. None states the four-window interpretation gate or
a below-rho ECDLP algorithm.
