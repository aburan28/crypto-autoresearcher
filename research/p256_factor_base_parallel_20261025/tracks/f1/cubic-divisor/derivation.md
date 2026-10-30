# Cubic-divisor membership: exact hypotheses and strata

2026-10-25 · TASK-20261025-13c38e. These are derived statements and executable
checks by this session, not independent review or a claim of novelty.

## 1. The factor scheme

Let K be a field, let F∈K[t] be monic of degree S≥3, and assume F is separable.
Over K[u,v,w], let h=t³−ut²+vt−w and write the unique monic division

```
F = h q + R₀ + R₁t + R₂t².
```

Then A=K[u,v,w]/(R₀,R₁,R₂) is finite and geometrically reduced, with exactly
C(S,3) geometric points and dimension C(S,3) over K. Geometric points correspond
to unordered sets of three distinct roots of F.

Proof: at a geometric zero of R, h divides F. Since F is separable, h has three
distinct roots, and choosing h is equivalent to choosing a three-element subset
of the S roots. This finite geometric zero set proves that A is finite. At a
zero, differentiate the division identity while holding F fixed:

```
δR = −q δh mod h.
```

Because gcd(h,q)=1, multiplication by q in Kbar[t]/h is invertible. The linear
map (δu,δv,δw)↦δh=−δu t²+δv t−δw is also invertible. Thus the 3×3 Jacobian of
(R₀,R₁,R₂) is invertible at every geometric zero. Every local Artinian factor
therefore has maximal ideal m satisfying m/m²=0, and Nakayama gives m=0. All
local factors are fields, so A is geometrically reduced. Each point has length
one, giving dimension C(S,3). Equivalently this is the scheme of monic degree-three
factors of a separable polynomial; no discriminant saturation is needed.

In the coefficient order (R₀,R₁,R₂) and variable order (u,v,w), the two minus
sign determinants cancel and

```
det Jacobian(R) = det(multiplication by q modulo h) = Res(h,q) ≠ 0.
```

The implementation checks this exact equality at all 4+56+560 divisors in its
S=4,8,16 fully split fixtures. The count is over the algebraic closure. Over K,
rational h can encode a Galois-stable set whose individual roots are not in K.
Our P-256 fixtures avoid that distinction by checking a complete linear
factorization of F over Fp; then all C(S,3) points and all their roots are rational.

For S<3 there are no monic cubic divisors and this stratum is empty. Nothing in
this proposition says that arbitrary input triples with repetitions are retained:
they are intentionally handled by the two additional strata below.

## 2. Dickson specialization and the short remainder circuit

Here K=Fp for the published P-256 prime. Let S=2ᵏ and F=D_S(t)−c, where
D₂(t)=t²−2 and D_(2n)=D_n²−2. Since p is odd, p∤S. The generic terminal condition
c≠±2 implies F is separable: from t=z+z⁻¹, D_S(t)=z^S+z^−S, and a critical value
away from z=±1 is ±2; at z=±1 the limiting derivative is ±S², which is nonzero.
The generic norm-one coset construction from original F1 makes F fully split in
Fp. The committed finite fixture roots are checked by exact factorization.

Retain A=A₀+A₁t+A₂t² as the remainder of the current Dickson iterate modulo h.
Set

```
B₀=A₀², B₁=2A₀A₁, B₂=A₁²+2A₀A₂, B₃=2A₁A₂, B₄=A₂².
```

Using t³=ut²−vt+w and t⁴=(u²−v)t²+(w−uv)t+uw, the next iterate has coefficients

```
A₀' = B₀ + wB₃ + uwB₄ − 2
A₁' = B₁ − vB₃ + (w−uv)B₄
A₂' = B₂ + uB₃ + (u²−v)B₄.
```

Start at (0,1,0), repeat k times, then impose A₀−c=A₁=A₂=0. This retains an O(k)
arithmetic circuit. Its literal coefficient formulas contain degree-four products
in the fixed h coefficients and current A's; introducing a variable for each
multiplication makes a quadratic gate circuit with O(k) variables and equations.
We do not claim the three-output update itself is quadratic in all unknowns.

With uw, uv, u² precomputed, a uniform nontrivial step has 3 squarings, 9 general
multiplications, 3 written small-constant scalings and 8 additions/subtractions.
The fixed setup uses 1 squaring, 2 multiplications and 2 subtractions. Initial
zero products can be omitted; these are circuit operation counts, not measured
Python polynomial costs. Coefficients expanded in u,v,w have total degree S−2 for
S≥4. The fixed-field k=2,3,4,5 counts are (2,2,3), (10,13,14), (67,85,81),
(496,575,546); compact input does not bound elimination work.

## 3. Exactly two equal coordinates

Write the triple as (x,x,y), with x≠y. The repeated coordinate is distinguished,
so there are S(S−1) such states. Let

```
Δ_F(x,y) = (F(x)−F(y))/(x−y).
```

Use the polynomial ideal (F(x), Δ_F(x,y)). It automatically enforces F(y)=0.
On the diagonal, Δ_F(x,x)=F'(x), which cannot vanish at a root of separable F,
so the diagonal contributes no points. At an off-diagonal root pair the Jacobian
determinant is −F'(x)F'(y)/(x−y), which is nonzero. Thus this two-variable ideal
is finite reduced with S(S−1) geometric points.

For the Dickson iteration no rational division is performed. Start U=x,V=y,Δ=1
and update

```
Δ' = Δ(U+V), U'=U²−2, V'=V²−2.
```

After k steps impose U−c=0 and Δ=0. Join S4 after substituting
(u,v,w)=(2x+y,x²+2xy,x²y). This circuit has O(k) gates. Its uniform step uses
2 squarings, 1 multiplication and 3 additions/subtractions.

## 4. All equal coordinates and joining S4

The all-equal stratum is F(x)=0, with S simple geometric points. Substitute
(u,v,w)=(3x,3x²,x³) in S4. Univariate gcd/root extraction is sufficient, though
the shared adapter also accepts this as a one-variable Groebner input.

The three strata are disjoint by coordinate multiplicity, and exhaust all
unordered coordinate triples:

```
C(S,3) + S(S−1) + S = C(S+2,3).
```

These are coordinate multiplicities. Equal x-coordinates can lift to opposite
signed curve points, so an all-equal coordinate triple can still contain an
inverse-point pair. Those sign choices are retained and checked by point sums.

Each stratum's membership algebra is a product of geometric fields. Quotienting
by the S4 element keeps exactly its zero factors, so the joint ideal remains
geometrically reduced, including when the zero set is empty. With fully split F,
the reference point sets enumerate every geometric zero. The delivered basis
certificates check original reductions, all critical pairs, finite standard
monomial count and basis vanishing on every reference zero. A separate sparse
modular arithmetic implementation replays those checks. No independent review
or formal proof-assistant verification is claimed.

S4 alone is a coordinate condition. Every accepted coordinate state is factored,
all curve lifts and signs are generated, and the target point sum is checked.
The complete strata union is compared with independent exhaustive signed triples.
P-256's prime order/cofactor-one setting is inherited; the original base bundles
also checked every retained point's order.

## 5. Why separability is an actual hypothesis

The actual-field control F=D₈−2 and h=t³−4t has three distinct roots (−2,0,2),
and h divides F. But F has a repeated root at zero; h and F/h share t and the
remainder Jacobian determinant is zero. The implementation checks this exact
counterexample to extending the reduced argument without the hypothesis. It
asserts neither that every nonseparable fibre is nonreduced nor a global obstacle
for the generic formulation.

## 6. Scope of the resulting progress

The generic cubic-divisor construction removes the original terminal scheme's
multiplicities on distinct coordinates; the separate repeated-coordinate ideals
are also reduced. At S=8 the main membership quotient length is 56, versus 512
for the earlier symmetric-terminal input, while the full geometric state count
across all strata remains 120. These are exact algebraic lengths and counts,
not a runtime comparison, a lower bound, or an asymptotic algorithmic advantage.

The fixed k=3 joint target is now solved and certified. The k=4 distinct joint
solver remains unknown after fresh bounded attempts; its repeated strata complete.
Circuit/divisor/Jacobian witnesses through k=96 verify representation identities
only, not high-depth relation solving or complete ECDLP recovery.
