# Stage-zero constructor admission: IDEA-20260723-001

## Verdict and boundary

`NO_ADMISSIBLE_CONSTRUCTION`.

This is a zero-compute, non-operational mathematics review. It defines the
exact support object, but it does not construct that object from compact input
inside the required resource rectangle. It gives no ECDLP algorithm or
advantage, performs no standardized-curve work, and concerns no real key or
deployed system. Failure here is not a lower bound against all representations.

The first failed requirement is requirement 2: no explicit compact
fresh-target update identity or recurrence survives without treating a
whole-divisor translation, represented coefficient family, resultant, or
common factor as supplied.

## 1. Exact object and support proof — PASS

Let \(p>3\), let

\[
E/\mathbb F_p:\quad Y^2Z=X^3+a_EXZ^2+b_EZ^3
\]

be smooth, and use its everywhere-defined projective group law with identity
\(O=[0:1:0]\). The intrinsic group law fixes the identity, infinity, tangent,
vertical, repeated-point, and order-two cases; no affine denominator-clearing
equation is used to define support.

For one admitted restriction, let the first four signed, coloured occurrence
sets produce the ordered pair-occurrence multisets

\[
D_{12}=\{(\alpha_1,\alpha_2,u=P_{\alpha_1}+P_{\alpha_2})\},\qquad
D_{34}=\{(\alpha_3,\alpha_4,v=P_{\alpha_3}+P_{\alpha_4})\}.
\]

Equal endpoint points remain repeated roots, while their ordered occurrence
labels remain distinct sidecar data. Let \(I_5\) be the selected fifth
occurrences. Each \(a\in I_5\) has a signed point \(A_a\) and a distinct public
label \(t_a\in\mathbb F_p\).

Choose an irreducible cubic \(h\), put
\(K=\mathbb F_p[\theta]/(h)\), and define the signed point key

\[
\kappa([x:y:1])=x+\theta y,\qquad \kappa(O)=\theta^2.
\]

The basis \(1,\theta,\theta^2\) makes \(\kappa\) injective on
\(E(\mathbb F_p)\): equality of two finite keys gives equality of both signed
coordinates, and no finite key equals \(\theta^2\).

Write \(m=|I_5|\), \(n_{12}=|D_{12}|\), and \(n_{34}=|D_{34}|\). Define

\[
\begin{aligned}
g_I(T)&=\prod_{a\in I_5}(T-t_a),\\
H_{12}(U)&=\prod_{d\in D_{12}}(U-\kappa(u_d)),\\
H_{34}^{R,a}(U)&=\prod_{e\in D_{34}}
  (U-\kappa(R-A_a-v_e)),\\
\rho_{R,a}&=\operatorname{Res}_U(H_{12},H_{34}^{R,a})\in K.
\end{aligned}
\]

Because the labels are distinct, there is a unique polynomial
\(r_R(T)\in K[T]\) of degree less than \(m\) satisfying

\[
r_R(t_a)=\rho_{R,a}\quad\text{for every }a\in I_5.
\]

Equivalently, \(r_R\) is the corresponding element of the split algebra

\[
A_I=K[T]/g_I(T)\simeq\prod_{a\in I_5}K.
\]

Finally define

\[
z_R(T)=\operatorname{monic}\gcd_{K[T]}(g_I(T),r_R(T)).
\]

This use of a resultant defines the mathematical object; it does not grant a
resultant value or its coefficients as constructor input.

For monic split polynomials, the resultant product formula gives

\[
r_R(t_a)=
\prod_{d\in D_{12}}\prod_{e\in D_{34}}
\bigl(\kappa(u_d)-\kappa(R-A_a-v_e)\bigr).
\]

Since \(K\) is a field, this product is zero exactly when one factor is zero.
Injectivity of \(\kappa\) then gives

\[
r_R(t_a)=0
\iff \exists d,e:\ u_d=R-A_a-v_e
\iff \exists d,e:\ u_d+v_e+A_a=R.
\]

The projective group law makes this equivalence valid on every exceptional
addition stratum. Repeated pair endpoints only repeat factors and do not
change whether the product vanishes. Since \(g_I\) is squarefree,

\[
z_R(T)=
\prod_{\substack{a\in I_5\\
\exists d,e:\ u_d+v_e+A_a=R}}(T-t_a).
\]

Thus \(z_R\) is exactly the extendible fifth-occurrence-label support;
\(z_R=1\) is the no-hit case. It does not encode row multiplicity or the other
four source labels.

## 2. Fresh-target update attempt — FAIL

For a fresh mutation \(R'=R+\Delta\), the exact leaf identity is

\[
q_{a,e}(R)=R-A_a-v_e,\qquad
q_{a,e}(R+\Delta)=q_{a,e}(R)+\Delta.
\]

Consequently,

\[
H_{34}^{R+\Delta,a}(U)=
\prod_{e\in D_{34}}
\left(U-\kappa(q_{a,e}(R)+\Delta)\right).
\]

This is explicit but not a compact aggregate recurrence. Across all fifth
labels it updates \(m n_{34}=\Theta(B^3)\) point/key components. The map
\(\kappa\) is injective but not a group homomorphism, so point translation is
not a scalar shift \(U\mapsto U-c_\Delta\) of the key polynomial.

Writing the same identity as

\[
\mathcal D_{34}^{R+\Delta,a}
=\tau_\Delta(\mathcal D_{34}^{R,a})
\]

does not improve it: treating \(\tau_\Delta\) on an entire degree-\(n_{34}\)
divisor as one gate is precisely the forbidden whole-divisor macro. A
recurrence for \(r_R\) would likewise have to construct the translated
coefficient family or the component resultants. Supplying either is the
forbidden coefficient/resultant payload. No smaller state transition was
found in the reviewed corpus.

## 3. Dimensions and target dependence — PASS AS AN AUDIT

Set \(m=\Theta(B)\) and \(n_{12},n_{34}=\Theta(B^2)\).

| Object | Dimension / count | Target dependence |
|---|---:|---|
| Curve constants, cubic key | \(O(1)\) field elements | independent |
| Five source decks and labels | \(\Theta(B)\) points/labels per deck | independent |
| \(D_{12},D_{34}\) occurrence sidecars | \(\Theta(B^2)\) each, up to polylogarithmic dyadic data | independent |
| \(H_{12}\) for one restriction | \(n_{12}+1=\Theta(B^2)\) \(K\)-coefficients | independent |
| \(g_I\), fifth labels and points | \(m+1=\Theta(B)\) coefficients plus \(m\) points | independent |
| Fresh input \(R\) | one point | dependent |
| \(q_{a,e}(R)\) | \(m n_{34}=\Theta(B^3)\) points if materialized | dependent |
| Split \(H_{34}^R\) | \(m(n_{34}+1)=\Theta(B^3)\) \(K\)-coordinates | dependent |
| \(r_R\bmod g_I\) | \(m=\Theta(B)\) \(K\)-coordinates | dependent |
| \(z_R\) | at most \(m+1=\Theta(B)\) coefficients | dependent output |

Streaming one fifth component avoids storing all \(B^3\) coordinates, but a
single degree-\(\Theta(B^2)\) translated polynomial remains live. No compact
constructor state exists to dimension beyond these explicit objects. Exact
source replay is not silently included: it would require additional positive
and negative restricted constructor calls, and requirement 2 already fails.

## 4. Generic-encoding erasure — FAIL FOR ADMISSION

Erase \(x,y\), field arithmetic, and the key \(\kappa\); replace every point by
a random encoding retaining only group operation and equality. The leaf update

\[
q_{a,e}(R+\Delta)=q_{a,e}(R)+\Delta
\]

still typechecks, so it is generic. It supplies no compact zero-label
aggregator.

The standard semantic route does contain named non-generic operations:

1. reading signed affine/projective coordinates;
2. finite-field zero masks and masked inversions for complete addition
   branches; and
3. forming and comparing the coordinate key
   \(\kappa(P)=x(P)+\theta y(P)\).

All three disappear under generic erasure. However, in the only explicit
route they are applied to \(\Theta(B^3)\) target-dependent components. No
coordinate-sensitive operation was connected to a compact aggregate
recurrence.

This distinction matters because the desired generic preprocessing rectangle
has

\[
S T^2=B^{9/4}\left(B^{5/4}\right)^2=B^{19/4}<B^5=N.
\]

As recorded by RT-20260722-103, a complete generic extraction path with
constant success at that rectangle conflicts with the cited generic
preprocessing benchmark up to polylogarithmic factors. That conditional
benchmark is not a lower bound for this support predicate or for
coordinate-sensitive methods. It does require a candidate to identify and
charge a concrete non-generic compact operation; none is present here.

## 5. Initial time and live-memory recurrences — FAIL THE CAPS

Let \(M(n)=n^{1+o(1)}\) denote fast polynomial arithmetic. Building a monic
product from \(n\) explicitly constructed roots obeys

\[
C(n)=2C(n/2)+M(n)=n^{1+o(1)}.
\]

A fast resultant of two represented degree-\(n\) polynomials costs
\(R(n)=n^{1+o(1)}\). Constructing and testing all \(m\) fifth components
without a supplied coefficient, resultant, or factor therefore obeys

\[
\begin{aligned}
Q(0,n)&=0,\\
Q(j+1,n)&=Q(j,n)+C(n)+R(n),\\
Q(m,n)&=m\,n^{1+o(1)}=B^{3+o(1)}.
\end{aligned}
\]

With component streaming, the live-memory recurrence has peak

\[
W(m,n)=\Theta(n^{1+o(1)}+m)=B^{2+o(1)};
\]

materializing the split family instead gives
\(\Theta(mn)=B^{3+o(1)}\) live coordinates. Target-independent pair and
product-tree setup remains \(B^{2+o(1)}\) time and retained state.

These recurrences charge construction rather than supplying a forbidden
payload, but they miss the required fresh-target time and workspace caps
\(B^{5/4+o(1)}\) by polynomial factors. The quasi-linear final gcd after
\(r_R\bmod g_I\) is supplied is only a positive extraction control and cannot
be counted as the constructor.

## Discriminating interpretation

- A claimed update that treats translated whole divisors, \(r_R\bmod g_I\),
  \(z_R\), a successful source, fitted coefficients, or a scalar orientation
  as input is an oracle restatement.
- The explicit component route is mathematically exact but fails the online
  time and live-memory rectangle.
- A future candidate would need a new coordinate-sensitive aggregate identity,
  fully typed state below the caps, and the same exact support proof. This
  report neither supplies nor rules out such an identity.

The internal deduplication remains unchanged: this is the known
P1553/P1513 compact common-factor construction obligation already preserved by
IDEA-20260723-001. No novelty claim or new mechanism owner is asserted.
