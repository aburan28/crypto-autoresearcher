# P1531 Cauchy elliptic-period type-2 specification

## Record status

- Candidate root: `ECDLP-IDEA-003`
- Focus experiment: `P1531`
- Expansion of: `P1530`
- Artifact class: theorem-only producer specification and operation screen
- Decision: `SCOPED_NO_PASS__OPEN_CAUCHY_PERIOD_TRANSFER_OPERATOR`
- Evidence scale: exact separation theorem and asymptotic route screen; no experiment
- Claim labels: `model-bound`, `novelty-unverified`
- Breakthrough claim: none
- Contract authorization: none
- Solver or elliptic fixture: none

This specification replaces the heuristic requirement that one elliptic period happens
to distinguish every scalar coset with a public randomized label whose collision
probability is proved. It does not compress the label evaluator. The sole surviving
operation is an explicit sub-square-root transfer operator for three Cauchy periods.

## Bound predecessor

- `ideas/artifacts/ECDLP-IDEA-003/p1530_r1_r2_independent_audit.md`
  - SHA-256: `e7dfae990f357da7d1f3f8503c06d6334323d925244d3803f2a002888081c402`
  - Decision:
    `INDEPENDENT_SCOPED_AUDIT_PASS__INCONCLUSIVE__RERANK_TYPE2_PERIOD`

## Parameter interface

Let

```text
E/F_p ordinary,
G=<P> <= E(F_p),                |G|=ell prime,
#E(F_p)=h*ell,                   h=ell^(o(1)),
ell-1=A*D,                      gcd(A,D)=1,
D=ell^(alpha+o(1)),             0<alpha<1,
H <= F_ell^*,                   |H|=D.
```

The main specification takes `D` even, so `-1 in H` and an `x`-coordinate orbit is
sign-complete. The factorization family is part of the claim. Replacing a fixed target
curve or hiding the cost of finding a suitable divisor does not establish an arbitrary
generic-order result.

For `u in F_ell^*`, write

```text
O_u = {[u*h]P:h in H},
X_u = {x([u*h]P):h in H/{+1,-1}}.
```

The `A` sets `X_u`, indexed by `F_ell^*/H`, are pairwise disjoint and each has
`n=D/2` elements. Indeed, equality of two abscissas gives
`u*h=+v*k` or `u*h=-v*k`; since `-1 in H`, either equality implies `u/v in H`.

Define the monic orbit polynomial

```text
F_u(Z) = product_(z in X_u) (Z-z) in F_p[Z].
```

Materializing `F_u` is a control, not the proposed evaluator.

## Exact Cauchy-period label

For a public `c in F_p`, define

```text
L_c([u]P) = POLE                        if F_u(c)=0,
L_c([u]P) = F_u'(c)/F_u(c)              otherwise
           = sum_(h in H/{+1,-1}) 1/(c-x([u*h]P)).
```

This is exactly invariant under replacing `u` by `u*h0`, `h0 in H`. A pole value is
tagged rather than divided by zero. Because the `X_u` are disjoint, a fixed `c` is a
pole for at most one orbit.

Choose public independent uniform `c_1,...,c_t in F_p` and set

```text
L([u]P) = (L_(c_1)([u]P),...,L_(c_t)([u]P)).
```

The same public tuple is used for every label in the DLP algorithm.

## Separation theorem

For distinct scalar cosets `uH` and `vH`, set

```text
N_(u,v)(Z) = F_u'(Z)F_v(Z)-F_v'(Z)F_u(Z).
```

This polynomial is nonzero and has degree at most `2n-2`. If it were zero, then
`(F_u/F_v)'=0`. In characteristic `p`, this would make `F_u/F_v` a rational function
of `Z^p`; its zero and pole multiplicities would be divisible by `p`. But `F_u` and
`F_v` are coprime squarefree polynomials with simple, disjoint roots. This is impossible.

Away from tagged poles, equality `L_c([u]P)=L_c([v]P)` requires
`N_(u,v)(c)=0`. Therefore

```text
Pr_c[label collision for one fixed pair] <= (D-2)/p.
```

Across all fewer than `A^2/2` orbit pairs and `t` independent coordinates,

```text
Pr[any collision] <= A^2/2 * ((D-2)/p)^t.
```

For a cryptographic-size prime subgroup on a prime-field curve,
`p=ell^(1+o(1))`. Hence

```text
Pr[any collision] <= ell^((2-t)(1-alpha)+o(1)).
```

Taking `t=3` gives failure probability

```text
ell^(-(1-alpha)+o(1)).
```

Thus three public Cauchy periods give a high-probability type-2 label without assuming
that a single unweighted elliptic period separates all rational scalar cosets. Final
`[x]P=Q` verification detects the negligible bad-setup event; resampling the three
public constants has expected constant repetitions.

This theorem proves separation only. It does not provide a fast evaluator.

## Gallant type-2 cost rectangle

Let target-independent setup, one label query, and label-specific state have exponents
`c`, `q`, and `m`. Gallant's type-2 reduction uses `sqrt(A)` labels in its outer
collision stage and `sqrt(D)` group elements in its inner orbit recovery. The complete
time and memory exponents are at least

```text
lambda_2 = max(c, (1-alpha)/2, alpha/2, (1-alpha)/2+q,
               final verification),
mu_2     = max(m, (1-alpha)/2, alpha/2).
```

For strict sub-rho time at fixed `alpha`, the label evaluator must satisfy

```text
q < alpha/2,        c < 1/2.
```

At the balanced point `alpha=1/2`,

```text
lambda_2=max(c,1/4+q),       mu_2=max(m,1/4).
```

The focus promotion cap `lambda<=0.45,mu<=0.30` therefore requires, at this point,

```text
c<=0.45,             q<=0.20,             m<=0.30.
```

The three label coordinates and pole tags have constant field-word size and do not
change the exponents.

## Direct evaluator control

Evaluating one label coordinate from its defining sum requires `D/2` scalar multiples,
abscissas, inversions, and additions. Iterating an order-`D` scalar generator reduces
each new point to one scalar-map application but still visits every term. Batched
inversion saves inversions, not orbit visits. The direct exponent is

```text
q_direct=alpha,
lambda_direct >= (1-alpha)/2+alpha=(1+alpha)/2>1/2.
```

Materializing `F_u`, its roots, or its coefficient vector has the same `D` traffic.
Brieulle et al.'s elliptic-period evaluator likewise charges one scalar multiplication
per period summand in its auxiliary finite-field setting.

## Transfer-operator normal form

For a rational function `f` on `E`, define

```text
T_H(f)(R) = sum_(h in H/{+1,-1}) f([h]R).
```

Each label coordinate is

```text
T_H(f_c)(R),          f_c(R)=1/(c-x(R)).
```

If `H=H_1*H_2` is an internal direct product, the full signed-count transfer operators
factor formally as `T_H=T_(H_1) o T_(H_2)`, after the constant sign multiplicity is
normalized. Expanding this composition as an ordinary arithmetic circuit still has one
leaf for every `h in H`: each inner function is evaluated at a distinct scalar multiple
of the query. A subgroup tree or smooth factorization names the same `D` leaves and does
not itself reduce query work.

A passing operation must give an identity that aggregates these leaves before they are
visited. Treating a reusable function call, modular composition, or transfer operator as
unit cost is not an arithmetic-cost proof.

## Orbit-polynomial recursion control

For a cyclic ordering `H=<beta0>` and a length-`r` segment, define

```text
F_(r,R)(Z)=product_(j=0)^(r-1)(Z-x([beta0^j]R)).
```

The natural divide-and-conquer identity is

```text
F_(2r,R)(Z)=F_(r,R)(Z)*F_(r,[beta0^r]R)(Z).
```

It is exact, but its two calls have different point inputs. Recursing to scalars doubles
the number of leaves at every level and returns `D` point evaluations. Computing only
`F'/F` gives the analogous additive recursion and the same leaf count. No common
subexpression or bounded-state recurrence is supplied.

This closes the natural subgroup-tree implementation only. It is not an arithmetic
circuit lower bound against a different identity.

## Summation-polynomial gate

Semaev polynomials can encode addition chains proving `R_j=[beta0^j]R` and eliminate
ordinate signs. They do not aggregate the Cauchy weights by themselves. A passing
summation-polynomial construction must publish:

1. A target-independent circuit producing all three tagged traces directly, rather than
   a relation variety containing their `D` summands.
2. A biconditional excluding false branches, repeated roots, vertical pairs, poles, and
   points outside `G`.
3. Query exponent `q<alpha/2`, with every resultant, factor, branch, and source inverse
   charged.
4. The exact family and full Gallant recovery cost.

A degree-`D` eliminant, a resultant whose roots include `X_u`, or a faster evaluation of
an already materialized orbit polynomial remains the direct control.

## FFE Frobenius gate

An FFE proposal may try to turn `[beta0]` into a cyclic Frobenius shift and evaluate the
trace as a field trace. For any homomorphism `Phi:E->A` defined over `F_(p^k)`, nonzero
on `G`, satisfying

```text
pi_A(Phi(R))=Phi([beta0]R)       for R in G,
```

iteration and the field of definition imply

```text
Phi(R)=pi_A^k(Phi(R))=Phi([beta0^k]R).
```

The prime-order restriction of `Phi` is injective, so `beta0^k=1 mod ell` and

```text
D divides k.
```

The extension coordinate payload is therefore at least `D` base-field words. Ordinary
elliptic normal bases can make Frobenius shifts and extension arithmetic quasi-linear in
`k`; they do not remove this degree floor. A nonlinear nonhomomorphic encoder remains
open only if it supplies the exact orbit-label biconditional and complete inverse-image
costs.

## Endomorphism and ECFFT gates

A low-degree endomorphism `psi` may act as a high-order scalar on `G`, making orbit
iteration cheap per step. It does not give a nonconstant global rational invariant:
`f o psi=f` with `deg(psi)>1` contradicts
`deg(f o psi)=deg(f)deg(psi)`. Pointwise invariants modulo the finite subgroup ideal
remain open but must state their circuit representation.

ECFFT and isogeny trees accelerate polynomial arithmetic on domains organized by
additive kernels and isogeny fibers. The scalar orbit is multiplicative in the hidden
coefficient. A passing ECFFT route must provide an explicit map that sends
`{[h]R:h in H}` to one supported evaluation fiber while preserving the three Cauchy
traces and allowing exact public inversion. Without that intertwiner, ECFFT only
accelerates arithmetic after a degree-`D` object has been supplied.

## Primary-source checks

- Gallant, *Finding discrete logarithms with a set orbit distinguisher*:
  <https://eprint.iacr.org/2010/370.pdf>
  defines type-2 labels and the
  `sqrt(A)+sqrt(D)+sqrt(A)*c(ell)` DLP reduction.
- Brieulle, De Feo, Doliskani, Flori, and Schost,
  *Computing Isomorphisms and Embeddings of Finite Fields*:
  <https://cs.uwaterloo.ca/~eschost/publications/ffisom.pdf>
  defines elliptic periods over scalar subgroups and gives the direct evaluation cost.
- Couveignes and Lercier, *Elliptic periods for finite fields*:
  <https://perso.univ-rennes1.fr/reynald.lercier/file/CL09.pdf>
  gives fast extension arithmetic and Frobenius shifts in elliptic bases; its extension
  representations remain linear or quasi-linear in their degree.

## Decision

The Cauchy-period construction proves a high-probability, sign-complete type-2 orbit
label from three public traces. This removes the unproved single-period collision
assumption. No screened implementation evaluates the traces with `q<alpha/2`.

- Direct summation and orbit-polynomial construction cost `D`.
- Natural subgroup and product-tree recurrences retain `D` distinct leaves.
- Standard summation-polynomial elimination supplies equations but no compressed trace.
- Homomorphic Frobenius encoding requires extension degree divisible by `D`.
- Low-degree endomorphisms supply cheap iteration but no global rational invariant.
- ECFFT lacks the required multiplicative-scalar-to-additive-fiber intertwiner.

The scoped disposition is
`SCOPED_NO_PASS__OPEN_CAUCHY_PERIOD_TRANSFER_OPERATOR`. It is not a sub-rho ECDLP
algorithm, a generic-order result, an experiment, or a breakthrough.

## Exactly one next action

Independently audit this P1531 specification, including the three-trace separation bound,
Gallant type-2 exponents, even-sign condition, direct and subgroup-tree leaf counts, and
the degree-`D` Frobenius-intertwiner proof; only a passing audit may freeze one explicit
summation-polynomial or ECFFT transfer recurrence with `q<alpha/2`, and no contract or
toy fixture is authorized.
