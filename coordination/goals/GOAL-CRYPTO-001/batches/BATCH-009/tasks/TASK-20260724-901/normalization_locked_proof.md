# Normalization-locked Newton-corner proof packet

Task: `TASK-20260724-901`  
Idea: `IDEA-20260723-006`  
Verdict: `PROOF_PACKET_COMPLETE`  
Claim boundary: negative Newton/BKK gate for the original target-sectioned
Semaev polynomial only.  
`breakthrough_claimed: false`

This is non-operational academic mathematics. No finite-field search,
polynomial expansion, curve execution, relation collection, key recovery, or
standardized-curve computation was performed.

## 1. Locked coefficient domain, resultant, and circuit

Put
\[
  \delta=4A^3+27B^2,\qquad
  R=\mathbb Z[1/6,A,B,\delta^{-1}].
\]
Every short-Weierstrass curve
\[
  E/k:\quad y^2=x^3+Ax+B
\]
over a field \(k\) of characteristic different from \(2,3\), with
\(\delta\ne0\), is an allowed specialization of \(R\).

The resultant convention is fixed once and for all by
\[
 \operatorname{Res}_Z(f,g)
   =a_d^{\,e}\prod_{f(\alpha)=0}g(\alpha)
\]
when \(f=a_d\prod_{i=1}^d(Z-\alpha_i)\) and \(\deg_Zg=e\), extended as the
corresponding Sylvester-determinant polynomial identity. In particular,
\[
 \operatorname{Res}_Z(f,a-Z)=f(a),\qquad
 \operatorname{Res}_Z(f,(a-Z)^2)=f(a)^2.                 \tag{1}
\]

The exact right-comb circuit is
\[
\begin{aligned}
S_2(X_1,X_2)&=X_1-X_2,\\
S_3(X_1,X_2,X_3)
 &= (X_1-X_2)^2X_3^2\\
 &\quad-2\bigl((X_1+X_2)(X_1X_2+A)+2B\bigr)X_3\\
 &\quad+(X_1X_2-A)^2-4B(X_1+X_2),                       \tag{2}\\
S_s(X_1,\ldots,X_s)
 &=\operatorname{Res}_Z\!\left(
     S_{s-1}(X_1,\ldots,X_{s-2},Z),
     S_3(X_{s-1},X_s,Z)\right),\quad s\ge4.              \tag{3}
\end{aligned}
\]
There is no primitive-part extraction, square-free reduction, division,
monicization, or coefficient-dependent rescaling after (3). Equations
(1)--(3), including the order of the resultant arguments, are the
normalization lock.

We use the following exact established Semaev theorem for this circuit:
\(S_s\) is symmetric, has degree \(D_s=2^{s-2}\) in every variable, and for
all \(x_i\in\bar k\),
\[
 S_s(x_1,\ldots,x_s)=0
 \iff
 \exists P_i\in E(\bar k)\setminus\{\mathcal O\}:
 x(P_i)=x_i,\quad \sum_iP_i=\mathcal O.                 \tag{4}
\]
The pointwise biconditional in (4), rather than only generic
set-theoretic agreement, is important below. Exact recurrence (3) and (4)
are Semaev, *Summation polynomials and the discrete logarithm problem on
elliptic curves*, IACR ePrint 2004/031, Theorem 1; the all-field formulation
for the same exact resultant circuit is Kosters--Yeo, *Notes on summation
polynomials*, arXiv:1503.08001, Definition in Section 2 and Proposition 2.1.
Applying the symmetry statement first over the generic field
\(\mathbb Q(A,B)\) gives equality of the permuted circuit polynomials there;
because both sides lie in \(R[X_1,\ldots,X_s]\), this is also an exact
polynomial identity over \(R\), not symmetry only up to a scalar.

## 2. Exact leading coefficient and unit induction

### Lemma 1 (normalization-locked leading coefficient)

For \(s\ge3\) and every \(i\),
\[
 [X_i^{D_s}]S_s(X_1,\ldots,X_s)
   =S_{s-1}(X_1,\ldots,\widehat{X_i},\ldots,X_s)^2.      \tag{5}
\]
The multiplicative factor is exactly \(1_R\), hence a unit under every
allowed specialization.

### Proof

It is enough by exact symmetry to take \(i=s\). Let
\[
 f(Z)=S_{s-1}(X_1,\ldots,X_{s-2},Z),\quad d=D_{s-1}.
\]
From (2),
\[
 [X_s^2]S_3(X_{s-1},X_s,Z)=(X_{s-1}-Z)^2.              \tag{6}
\]
The resultant is homogeneous of degree \(d\) in the coefficients of its
second argument. Equivalently, over the fraction field, its root formula
shows that the coefficient of \(X_s^{2d}\) in (3) is
\[
 a_d^2\prod_{j=1}^d(X_{s-1}-\alpha_j)^2
   =f(X_{s-1})^2.
\]
Both sides are polynomial identities, so the equality descends from the
fraction field to \(R[X_1,\ldots,X_s]\). Since \(2d=D_s\), this is (5).
There is no unspecified scalar: (1) makes the factor \(1_R\). ∎

Now section the final variable:
\[
 f_{m,t}(x_1,\ldots,x_{m-1})=S_m(x_1,\ldots,x_{m-1},t).
\]
For \(J\subseteq\{1,\ldots,m-1\}\), let
\[
 c_{m,J}(t)=
 \left[\prod_{j\in J}x_j^{D_m}\right]f_{m,t},
\]
where every free variable outside \(J\) has exponent zero. Symmetry makes
this depend only on \(k=|J|\); write it as \(c_{m,k}\). Directly from (2),
\[
 c_{3,0}=A^2-4Bt,\qquad c_{3,1}=t^2,\qquad c_{3,2}=1.   \tag{7}
\]

### Lemma 2 (exact corner-square recurrence)

For \(m\ge4\) and \(1\le k\le m-1\),
\[
 c_{m,k}(t)=c_{m-1,k-1}(t)^2.                           \tag{8}
\]

### Proof

Choose a maximal-exponent variable and apply (5). Each remaining variable
has degree at most \(D_{m-1}=D_m/2\) in each factor. In the square, exponent
\(D_m\) forces exponent \(D_{m-1}\) from both factors, while exponent zero
forces exponent zero from both. Thus exactly one exponent pair contributes
to the requested corner, and its coefficient is the square in (8). The
unit is still exactly \(1\). ∎

Writing
\[
 F_s(t)=S_s(\underbrace{0,\ldots,0}_{s-1},t),
\]
(7)--(8) give
\[
\begin{aligned}
c_{m,k}(t)&=F_{m-k}(t)^{2^k} &&(0\le k\le m-3),\\
c_{m,m-2}(t)&=t^{D_m},\\
c_{m,m-1}(t)&=1.                                      \tag{9}
\end{aligned}
\]

## 3. Exact all-zero-corner classifier

Choose \(\beta\in\bar k\) with \(\beta^2=B\), and put
\[
 P_0=(0,\beta)\in E(\bar k).
\]
Changing \(\beta\) replaces \(P_0\) by \(-P_0\) and does not change any
\(x([r]P_0)\). Define
\[
 \mathcal R_s=\{-(s-1),-(s-3),\ldots,s-3,s-1\}.         \tag{10}
\]

### Lemma 3 (all-zero roots, including degeneracies)

For every \(s\ge3\), \(F_s\) is a nonzero polynomial and its finite
set-theoretic root set over \(\bar k\) is exactly
\[
 V(F_s)=
 \{x([r]P_0):r\in\mathcal R_s,\ [r]P_0\ne\mathcal O\}. \tag{11}
\]

### Proof

First suppose \(B\ne0\). The two affine points above \(x=0\) are exactly
\(P_0\) and \(-P_0\). A choice of the first \(s-1\) lifts in (4) therefore
sums to \([r]P_0\) for some \(r\in\mathcal R_s\). If this sum is affine, the
last point is forced to be \(Q=-[r]P_0\), and its coordinate is
\(t=x(Q)=x([r]P_0)\). Conversely, that choice of lifts and that \(Q\) give
a sum of \(\mathcal O\), so (4) gives a root.

If \([r]P_0=\mathcal O\), cancellation would require the last point to be
\(\mathcal O\). It has no finite \(x\)-coordinate and is forbidden in (4),
so such an \(r\) contributes no finite root. This explicitly handles a
partial sum at infinity. If \(P_0\) is torsion, different \(r\)'s can give
the same affine point, opposite points, or \(\mathcal O\); these events only
merge listed roots or invoke the preceding omission. They create no new
root.

Now suppose \(B=0\). Nonsingularity forces \(A\ne0\). There is one point
above zero, \(P_0=(0,0)=-P_0\), and it has order two. The first \(s-1\)
points therefore sum to \((s-1)P_0\). If \(s\) is odd this is
\(\mathcal O\), so no affine last point can cancel it and \(V(F_s)\) is
empty. If \(s\) is even it is \(P_0\), the last point must be \(P_0\), and
\(V(F_s)=\{0\}\). Formula (11) gives exactly the same alternatives because
every integer in \(\mathcal R_s\) has parity \(s-1\). The base case also
shows the degree drop without ambiguity:
\[
 F_3(t)=A^2\ne0.
\]

For either value of \(B\), the possible sums of the first \(s-1\) lifts form
a finite set. Since \(\bar k\) is infinite, choose a finite \(t\) outside
the corresponding finite \(x\)-set. The biconditional (4) then gives
\(F_s(t)\ne0\); hence \(F_s\) is not the zero polynomial.

Finally, (4) is an exact statement for every specialized tuple of the exact
circuit (2)--(3). It rules out an additional finite root caused by a
degree drop or a common projective root of an intermediate resultant. The
argument above also rules out specialization to the zero polynomial.
Thus no recurrence-induced extraneous finite factor changes (11).
Root multiplicities are intentionally not asserted or needed. ∎

## 4. Exact exception union and Newton conclusion

Define
\[
 \mathcal E_m(E)=
 \{x([r]P_0):1\le r\le m-1,\ [r]P_0\ne\mathcal O\}.    \tag{12}
\]
It has at most \(m-1\) elements, with torsion and sign collisions only
reducing the count. For \(B=0\), it is exactly \(\{0\}\).

By (9) and Lemma 3, the union of the vanishing sets of all corner classes is
\[
 \{0\}\cup\bigcup_{s=3}^m V(F_s).                       \tag{13}
\]
The set in (13) equals (12). For one inclusion, every index appearing in
\(V(F_s)\) has absolute value at most \(s-1\le m-1\), and
\(0=x(P_0)\). Conversely, \(r=1\) is supplied by the \(t^{D_m}\) corner;
for every \(2\le r\le m-1\), choose \(s=r+1\). Then
\(r=s-1\in\mathcal R_s\), so every affine \([r]P_0\) occurs in \(V(F_s)\).
This proves both inclusions, including all torsion collisions and omitted
infinity values.

Therefore
\[
 t\notin\mathcal E_m(E)
 \Longleftrightarrow
 \text{every one of the \(2^{m-1}\) box-corner coefficients is nonzero}.
                                                                    \tag{14}
\]
The degree bound places the support of \(f_{m,t}\) inside
\([0,D_m]^{m-1}\). Under (14), all vertices of that box lie in the support,
so
\[
 \operatorname{Newt}(f_{m,t})=[0,D_m]^{m-1}.            \tag{15}
\]
If \(t\in\mathcal E_m(E)\), at least one corner vanishes, so its Newton
polytope is a proper subpolytope. This does not determine the exceptional
section's interior support or its mixed volume in a square system.

For \(n=m-1\) nonexceptional original sections, all \(n\) Newton polytopes
are the box in (15), hence the BKK-normalized mixed volume is
\[
 \operatorname{MV}=n!D_m^n
   =(m-1)!\,2^{(m-1)(m-2)},\qquad
 \frac{\operatorname{MV}}{\text{box Bézout}}=1.         \tag{16}
\]
Equation (16) is only a path-count/Newton-hull statement. It is not a
runtime lower bound for every sparse implementation, lifted formulation,
Gröbner system, arithmetic circuit, or non-Semaev method.

## 5. Uniform-mask exception bridge in one cost model

This paragraph concerns only the bridge explicitly named in the task.
Let \(H=\langle P\rangle\) have prime order \(N\), let \(Q\in H\), and draw
fresh independent \(U\) uniformly from \(\mathbb Z/N\mathbb Z\). Then
\(Q+[U]P\) is uniform in \(H\). At most two subgroup points lie above each
finite exceptional \(x\)-coordinate, so the eligible count \(K\) satisfies
\[
 K\le2|\mathcal E_m(E)|\le2(m-1),\qquad
 p_{\rm hit}=K/N\le2(m-1)/N.                            \tag{17}
\]
If \(K=0\), the expected hitting time is infinite. Otherwise independent
repetition has expected trial count
\[
 \mathbb E[T]=N/K\ge N/(2(m-1)).                        \tag{18}
\]

The common model \(\mathcal M_{\log N}\) is a word-RAM/traffic model with
\(\Theta(\log N)\)-bit words. Its additive work ledger counts word
operations and words read, written, transmitted, or replayed; peak words
are reported separately. A mask trial costs at least one ledger unit even
if all elliptic-curve arithmetic is optimistically free. An accepted replay
must materialize or retrieve the \(m\) canonical arity entries—the \(m-1\)
source-point entries and the masked-target entry—together with their
orientation/sign data. Each point entry occupies at least one word, so
replay output costs \(\Omega(m)\) in this same ledger.

For constants \(a,b>0\), the bridge therefore obeys
\[
\begin{aligned}
\mathbb E[W_{\rm bridge}]
 &\ge a\,\frac{N}{2(m-1)}+b\,m\\
 &\ge a\,\frac{N}{2m}+b\,m
  =\Omega(\sqrt N).                                     \tag{19}
\end{aligned}
\]
The final step is AM--GM and remains valid when \(m\) varies with \(N\).
Pollard rho has expected \(N^{1/2+o(1)}\) work in this model up to
subpolynomial arithmetic factors. Thus (19) earns no sub-rho exponent
credit and makes no constant-factor comparison. It is not a lower bound
for an unspecified nonuniform bridge. Relation supply, failed
decompositions, source recovery, rank, factor logs, blind descent,
verification, traffic, and memory can only be discussed after a separate
complete transcript; none receives positive credit here.

## 6. Versioned theorem-mode replay obligation

Any use of this packet as a theorem certificate must instantiate schema
`newton-corner-theorem-mode/1.0.0`. An instance is valid only if it contains:

1. schema name, exact semantic version, and a tagged mode equal to either
   `UNIVERSAL_THEOREM` or `SPECIALIZED_SECTION`;
2. the snapshot commit and SHA-256 digests of `proof_packet.yaml` and this
   file, supplied by `TASK-20260724-902`;
3. for `UNIVERSAL_THEOREM`, the byte-for-byte coefficient domain
   \(R=\mathbb Z[1/6,A,B,(4A^3+27B^2)^{-1}]\), with no concrete-field
   fields; or, for `SPECIALIZED_SECTION`, an exact field encoding,
   characteristic, \(A,B\), and a check that \(4A^3+27B^2\ne0\);
4. the exact AST or byte-for-byte equations (1)--(3), including resultant
   argument order and an assertion that no post-resultant normalization
   occurred;
5. \(m\) and \(D_m\); in `SPECIALIZED_SECTION` also the target encoding and
   an exact extension-field descriptor for \(P_0=(0,\beta)\), with
   invariance under \(P_0\mapsto-P_0\);
6. replay records for (7), the unit \(u_s=1\) in (5), recurrence (8), root
   classifier (11), exception union (12)--(14), and hull implication (15);
7. the exact list of omitted indices with \([r]P_0=\mathcal O\), duplicate
   \(x\)-values, and the explicit \(B=0\) branch;
8. the claimed output, limited to `SATURATED_SECTION`,
   `EXCEPTION_SECTION`, or `SATURATED_GENERIC`, plus (16) only when every
   required corner is certified; and
9. the claim boundary and `breakthrough_claimed: false`.

`UNIVERSAL_THEOREM` may return only `SATURATED_GENERIC`.
`SPECIALIZED_SECTION` may return only `SATURATED_SECTION` or
`EXCEPTION_SECTION`. The tagged union prevents a universal coefficient ring
from being treated as a field of a fixed characteristic.

The verifier must reject on a version mismatch, missing digest, alternate
normalization, unproved unit, absent \(B=0\)/infinity branch, or any use of
an exceptional section as positive algorithmic evidence. A backward-
incompatible field or semantic change requires a new major schema version;
an old verifier must fail closed.

The theorem schema has no randomness. Any later uniform-mask cost claim
must additionally instantiate a distinct
`uniform-mask-exception-bridge/1.0.0` transcript containing \(H,P,Q\) and
membership/order witnesses, the sampler description and complete random
tape, every mask and hit/miss receipt, all \(m\) canonical entries and
orientations, rejection reasons, and the additive
\(\mathcal M_{\log N}\) work/traffic/peak-memory ledger. Any end-to-end
algorithmic credit additionally requires relation, rank, factor-log,
descent, and verification certificates. No such specialized certificate
is instantiated by this zero-compute packet.

## 7. Lemma status and limits

- `NL-1 exact recursive normalization`: proved; resultant factor is
  \(1_R\).
- `NL-2 exact corner induction`: proved.
- `NL-3 all-zero root classifier`: proved set-theoretically, including
  \(B=0\), infinity, torsion, collisions, nonzero specialization, and no
  extra finite roots.
- `NL-4 exact exception union and full-box implication`: proved.
- `NL-5 common-model uniform-mask bridge charge`: proved only for fresh
  independent uniform masks with mandatory \(m\)-entry materialization or
  replay.
- `NL-6 versioned theorem replay obligation`: specified as
  `newton-corner-theorem-mode/1.0.0`.

There is no open lemma inside the stated boundary. The packet does not prove
ECDLP hardness, a general solver lower bound, equal sparse/dense runtime, or
anything about unsectioned polytopes, coefficient-dependent liftings,
alternate curve models, nonuniform target bridges, standardized curves, or
key recovery. A successful negative Newton/BKK gate is not a breakthrough.
