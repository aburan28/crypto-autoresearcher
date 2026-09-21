# Root operator preflight v1: companion displacement

## Handoff: subset-norm root specialization

### Claim or task

Derive the exact identity-complete translated-D3 polynomial `c_Q`, then test the
companion-commutator displacement and direct-approximant representations for
compact target specialization at the D2 root.

### Status

`RESTRICTED THEOREM` for the algebraic formulas.

`NEGATIVE RESULT`, `MODEL-BOUND`, independently reviewed `GO` for the companion-
displacement/direct-approximant family. Its displacement rank is zero, but the
commutator kernel has dimension `N2`; the standard representation still needs
the `N2`-coefficient target remainder, while the explicit factor representation
touches `N3` translated factors. This is not a lower bound against every implicit
scalar-norm or source-structured algorithm.

No implementation, experiment, or child-node construction is authorized.

### Assumptions

- `E/F_p: y^2=x^3+a*x+b`, `p>3`, has odd prime order.
- `K=F_p[omega]/(omega^2-delta)`, where `delta` is a nonsquare and conjugation
  sends `omega` to `-omega`.
- `enc(x,y)=x+omega*y`.
- `D2^fin,D3^fin` contain distinct oriented affine points; identity support is
  represented by sentinels `o_2,o_3`.
- `N2=|D2^fin|` and `N3=|D3^fin|`; `Theta(B^2),Theta(B^3)` are used only in the
  measured collision-light specialization.
- `M(Z)=product_(R in D2^fin)(Z-enc(R))` is monic and squarefree.
- The companion statement assumes `N2>=1`. If `N2=0`, bypass it and evaluate
  only the registered identity routes.

### Evidence so far

#### Exact translation factors

For finite `Q=(u,v)` and `S=(x,y)` with `d=u-x != 0`, define

```text
A = (v+y)^2-(u+x)*d^2
B = (v+y)*(u*d^2-A)-v*d^3.
```

The ordinary addition formula gives

```text
Q-S = (A/d^2,B/d^3)
tau_Q(S)=enc(Q-S)=(d*A+omega*B)/d^3,
```

so the exact monic factor is

```text
Z-tau_Q(S)=d^-3*(d^3*Z-d*A-omega*B).
```

If `d=0`, the two oriented possibilities are `S=Q` and `S=-Q`. The first gives
the identity and emits no finite root. The second gives `Q-S=2Q`; its factor is
`Z-enc(2Q)`, using

```text
lambda_2=(3*u^2+a)/(2*v)
x_2Q=lambda_2^2-2*u
y_2Q=lambda_2*(u-x_2Q)-v.
```

The denominator `2*v` is nonzero because a finite `v=0` point would have order
two in the odd prime-order group.

#### Exact translated polynomial

For finite `Q`, let

```text
epsilon_+(Q) = 1 when Q is in D3^fin, else 0
epsilon_-(Q) = 1 when -Q is in D3^fin, else 0
O_Q = {S=(x,y) in D3^fin : x != u}
kappa_Q = product_(S in O_Q) (u-x_S)^3.
```

Then the exact monic translated-D3 polynomial is

```text
c_Q(Z) = kappa_Q^-1
         *(Z-enc(2Q))^epsilon_-(Q)
         *product_(S in O_Q)
           ((u-x_S)^3*Z-(u-x_S)*A_S-omega*B_S).
```

Its degree is `N3-epsilon_+(Q)`. If the translated finite support is empty,
`c_Q=1`. For `Q=O`,

```text
c_O(Z)=product_(S=(x,y) in D3^fin) (Z-(x-omega*y))
      = conjugate(P_3(Z)),
```

where `P_3(Z)=product_S(Z-enc(S))`.

The D3 identity sentinel is handled outside `c_Q`: for finite `Q`, it contributes
the route `o_3 and Q in D2`; for `Q=O`, it translates to the identity and emits
no finite root. The `R=O,S=Q` route is `o_2 and Q in D3`. Therefore

```text
Hit(Q) = [gcd(M,c_Q) != 1]
         or (o_2 and Q in D3)
         or (o_3 and Q in D2).
```

Translation by `Q` is injective, so after omitting `S=Q`, the roots of `c_Q`
remain distinct.

The oriented encoding itself is injective because

```text
z^p=x-omega*y,
x=(z+z^p)/2,
y=(z-z^p)/(2*omega).
```

Here `omega^p=-omega` since `delta` is a nonsquare. In `c_O`, conjugation is
coefficientwise and fixes the indeterminate `Z`.

#### Quotient multiplication and norm

Set

```text
A_root = K[Z]/(M)
zeta   = Z mod M
r_Q    = c_Q mod M.
```

Let `J` be multiplication by `zeta` in the power basis. Multiplication by `r_Q`
is

```text
T_Q = r_Q(J)
    = product_(S in D3^fin, Q-S != O)
        (J-enc(Q-S)*I).
```

The exact finite-finite root predicate is

```text
gcd(M,r_Q) != 1 iff det(T_Q)=0.
```

If `m_Q=deg(c_Q)`, the resultant identity is

```text
Res(M,c_Q)
  = det(T_Q)
  = (-1)^(N2*m_Q)
    *product_(S in D3^fin, Q-S != O) M(enc(Q-S)).
```

#### Companion displacement

The exact companion commutator is

```text
Delta_J(T_Q)=J*T_Q-T_Q*J=0,
```

so its generator rank is zero. This rank does not by itself compress the target.
The companion matrix is cyclic with minimal polynomial `M`; hence

```text
Cent(J)=K[J]
```

has dimension `N2`. The empty commutator generator identifies only membership in
this `N2`-dimensional space. Under the standard companion representation, the
boundary data distinguishing `T_Q` is its first column

```text
T_Q*e_0 = (r_(Q,0),...,r_(Q,N2-1))^T,
```

which is the dense remainder `r_Q`. This proves a representation failure for the
empty-generator companion-displacement interface; it does not prove that this
particular `r_Q` lacks every other short circuit or source-structured encoding.
Squarefreeness is needed for the distinct-root interpretation, but not for this
centralizer lemma.

#### Direct approximant interface

The exact division and gcd relations are

```text
c_Q = q_Q*M+r_Q,       deg(r_Q)<N2
a_Q*M+b_Q*r_Q=g_Q,     g_Q=gcd(M,r_Q).
```

A standard approximant or gcd solver changes the solver, not its explicit input
boundary: it receives either the `N3` factors or coefficients of `c_Q`, or the
`N2` coefficients of `r_Q`. A different implicit approximant input is outside
this negative and must state its construction and certificate cost.

#### Dimension and traffic census

| Route | Rank | Explicit target payload | Explicit target work or traffic |
|---|---:|---:|---:|
| Companion remainder `r_Q(J)` | `0` | `Theta(N2)` K-words | at least `Theta(N2)` reads/writes after construction; direct factors touch `Theta(N3)` translations |
| Dense `T_Q` | `0` | `Theta(N2^2)` K-words | strictly worse and unnecessary |
| Sequential scalar norm product | n/a | `O(1)` live accumulator | naive `Theta(N2*N3)` evaluation; explicit fast multipoint routes still process `N3` translated points |
| Tier A D2 scan | n/a | `O(1)` target-live words | `Theta(N2)` probes with charged explicit D3 advice |

The scalar row records costs of these explicit interfaces only. It is not a
lower bound against a nonlinear transposed norm circuit, nested source-level
resultant, or batched target specialization.

Fixed root advice is `Theta(N2)` for `M`, the D2 dictionary, and pair witnesses.
An explicit D3 factor stream is `Theta(N3)` advice in Tier A; regenerating the
same explicit stream in Tier B moves that cost into online work. Constant-many
membership tests for `Q` and `-Q` can use the registered `Theta(B)` factor scan
against D2 rather than a hidden D3 oracle.

#### Terminal lift

After a hypothetical descent returns `R`, set `S=Q-R`. Scan the `B` signed
factors `P`, compute `S-P`, and probe the charged D2 dictionary. A hit returns
`P` plus its deterministic pair witness. Charge `Theta(B)` group subtractions,
probes, record reads, and independent replay, with `O(1)` target-live state and
no D3 advice.

### Narrow scoped conclusion

The root failure is not high displacement rank. Every quotient-algebra
multiplication operator has rank-zero commutator displacement, but the
commutator kernel is `N2`-dimensional. For the frozen companion-displacement and
direct explicit-approximant interfaces, target specialization therefore falls
back to either:

```text
Theta(N2)=Theta(B^2) explicit remainder boundary data, or
Theta(N3)=Theta(B^3) explicit translated-factor processing
```

in the collision-light regime. This family fails the root zero-run gate. It does
not rule out a different nonlinear transposed norm circuit, source-level nested
resultant, batch specialization, or representation exploiting additional
factor-base structure.

### Failure modes

- Reporting rank zero as compression while omitting the `N2`-dimensional
  centralizer boundary.
- Treating streaming as removal of `N3` factor traffic.
- Hiding `c_Q` or `r_Q` inside an approximant or Sylvester input generator.
- Omitting the `S=Q` degree drop, `S=-Q` doubling route, `Q=O` conjugation, or
  the identity sentinels.
- Returning a root bit without the charged `Theta(B)` terminal lift.
- Generalizing this interface negative into a lower bound on all implicit
  scalar-norm algorithms.

### Next concrete action

Independently verify the translation formulas, centralizer lemma, and boundary
scope. If confirmed, mark only this companion-displacement/direct-approximant
family `REJECTED_SCOPED` and do not construct its child operators.

### Artifact paths

- `theory.md`
- `contract.md`
- `object-dimension-ledger.md`
- `pre-implementation-literature-review-v1.md`
