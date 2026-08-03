# Ordinary-input nonlinear acquisition: scoped generic barrier and escape theorem

## Outcome

This proof-only analysis obtains two scoped results.

1. In the exact ordinary generic-group model defined below, a constant-success,
   certificate-bearing acquisition of
   \(R=\alpha^dG\), for
   \(d=N^{\delta+o(1)}\) with \(0<\delta<1\), requires
   \(N^{1/2-o(1)}\) charged work. More generally, the same barrier applies to
   \(f(\alpha)G\) whenever \(f\) has \(o(N)\) agreement with every affine
   function. Composing this acquisition cost with Cheon's known auxiliary-input
   algorithm cannot reduce the ordinary-input expected-time exponent below
   \(1/2\).

2. A precisely typed graded bilinear tower would break affine closure and would
   construct a same-group triple
   \(T_d,\alpha T_d,\alpha^dT_d\) in \(O(\log d)\) interface calls. If the
   tower's construction, access, certification, data, and verification costs
   all have charged exponent below \(1/2\), then composition with Cheon is
   conditionally sub-rho. No such tower is asserted to exist for an ordinary
   prime-order elliptic-curve group. Its realization and cost are an explicit
   open escape interface, not an ordinary-ECDLP result.

This is not a closure, SOTA, support, or breakthrough claim. Cheon's
augmented-input method is treated solely as attributed prior art.

## 1. Scalar orientation and parameters

Let \(r\) be prime, let \(N:=r\), and let

\[
  \mathbb G=\langle G\rangle
\]

be an additive cyclic group of order \(r\). Scalars lie in
\(\mathbb F_r\). The ordinary ECDLP instance is

\[
  G,\qquad Q=\alpha G,
\]

where \(\alpha\) is sampled uniformly from \(\mathbb F_r^*\). This orientation
is used throughout.

For the Cheon composition, \(d\mid r-1\), \(1<d<r-1\), and

\[
  d=N^{\delta+o(1)},\qquad 0<\delta<1.
\]

The requested nonlinear target is

\[
  R_d=\alpha^dG.
\]

For an arbitrary scalar function \(f:\mathbb F_r^*\to\mathbb F_r\), define its
affine-agreement parameter

\[
  \rho_f=\max_{a,b\in\mathbb F_r}
    \#\{x\in\mathbb F_r^*:f(x)=a+bx\}.
\]

The barrier below covers an "equivalent nonlinear generator" only when its
specified \(f\) satisfies \(\rho_f=o(r)\). For \(f(x)=x^d\) with
\(d<r\),

\[
  \rho_f\le d
\]

by the root bound for \(X^d-bX-a\). Thus
\(\rho_f=N^{\delta+o(1)}=o(N)\).

## 2. Exact ordinary generic-group model

### 2.1 Encodings and equality

At group setup, the oracle samples a uniformly random injection

\[
  \sigma:\mathbb F_r\longrightarrow\{0,1\}^{\lambda}.
\]

The handle \(\sigma(x)\) denotes \(xG\). Equality of handles is exact equality
of their represented group elements. Apart from equality and passing handles
to the allowed oracles, their bit patterns have no specified algebraic
meaning. The algorithm may branch on bit strings, but the lazy-sampling
simulation makes fresh strings independent of their formal scalar labels.

The input handles are \(\sigma(1)\) and \(\sigma(\alpha)\).

### 2.2 Allowed ordinary operations

The ordinary interface supplies:

- group addition:
  \(\operatorname{Add}(\sigma(x),\sigma(y))=\sigma(x+y)\);
- inversion:
  \(\operatorname{Neg}(\sigma(x))=\sigma(-x)\);
- known-scalar multiplication:
  \(\operatorname{Mul}(c,\sigma(x))=\sigma(cx)\) for disclosed
  \(c\in\mathbb F_r\);
- equality tests on handles;
- scalar-field arithmetic on disclosed scalars;
- private randomness.

Each oracle call, handle comparison, and accessed stored handle is charged in
the declared cost accounting. Standard polylogarithmic scalar arithmetic is
absorbed in \(N^{o(1)}\).

The model has no coordinate access, pairing, multilinear map, extension-field
operation on hidden point coordinates, input-dependent endomorphism,
order-changing correspondence, nonlinear point map, leakage, or
\(\alpha\)-dependent advice unless one is separately declared as an escape
interface.

### 2.3 Preprocessing and advice

Three cases are distinguished.

- Instance-independent advice created before \(\sigma\) is sampled may contain
  algorithms and disclosed field constants, but no valid group handles.
- Encoding-dependent, \(\alpha\)-independent preprocessing may create \(P\)
  handles for known constant multiples \(c_iG\). Its construction time, stored
  data, and memory are charged.
- Any advice depending on \(\alpha\), \(Q\), \(\alpha^dG\), or a correlated
  leakage is a non-generic input and must be declared on the
  data/query-assumption axis.

If a group-specific table is amortized over \(K\) independent instances, both
its total cost \(P\) and its amortized contribution \(P/K\) must be reported.
It is not free in the single-instance comparison.

### 2.4 Certificate semantics

A generic acquisition certificate consists of disclosed scalars, generic
handles, and a finite derivation transcript. A public verifier receives only

\[
  (G,Q,R,d,\text{certificate})
\]

and the same declared interfaces as the acquisition algorithm.

Perfect soundness means that, for every \(\alpha\), every valid encoding
injection, and every certificate, acceptance implies
\(Q=\alpha G\) and \(R=\alpha^dG\). Statistical soundness permits invalid
acceptance probability at most \(\varepsilon_s\), which is charged explicitly.

A scalar witness \(z\) is valid: the verifier checks

\[
  zG=Q,\qquad R=z^dG.
\]

Producing such a witness is ordinary DLP acquisition and does not evade the
lower bound.

## 3. Single-purpose generic-group lemmas

### Lemma 1: formal-label span

Before an informative collision, every handle constructed by the ordinary
interface has a unique formal scalar label

\[
  \ell(X)=a+bX,\qquad a,b\in\mathbb F_r.
\]

**Proof.** The initial labels are \(1\) and \(X\). Addition, inversion, and
known-scalar multiplication preserve the two-dimensional
\(\mathbb F_r\)-span of \(1,X\). Random choices alter only the disclosed
coefficients. Equality does not create a new handle. Induction over oracle
calls proves the claim. \(\square\)

Consequently, no ordinary operation syntactically constructs \(X^d\) for
\(1<d<r-1\).

### Lemma 2: unseen-encoding distribution

Conditioned on the absence of equality between two distinct formal affine
labels, the lazy-sampled handles assigned to newly encountered labels are
uniform unused strings. For fixed algorithm randomness and fixed lazy-sampling
randomness, the same collision-free formal transcript can therefore be coupled
across every \(\alpha\) that avoids the transcript's affine collision
equations.

**Justification.** The oracle table is a random injection. Until two distinct
formal labels evaluate to the same field element, the simulator allocates a
fresh unused handle for each new formal label. Allocation and all branches on
fresh handle strings are independent of the numerical value of \(\alpha\).

### Lemma 3: informative-collision probability

Equality of two distinct affine labels gives

\[
  a+b\alpha=a'+b'\alpha.
\]

If \(b=b'\), distinct labels never collide. If \(b\ne b'\), there is at most
one possible instance scalar,

\[
  \alpha=(a'-a)(b-b')^{-1}.
\]

Let \(P\) be the number of preprocessed constant handles and let \(L\) be the
number of input-dependent affine labels encountered online, including \(Q\).
For adaptive generic computation,

\[
  \Pr[\text{informative collision}]
  \le
  \frac{B(P,L)}{r-1},
\]

where the conservative root count

\[
  B(P,L)=(P+1)L+\binom{L}{2}
\]

counts constant-versus-online and online-versus-online pairs. Pairs of two
constant labels contribute no root. The adaptive bound follows by deferred
decisions: conditioned on the prior collision-free transcript, each new
distinct affine equality excludes at most one still-unconditioned value of
\(\alpha\).

With \(q\) online group-oracle results, \(L\le q+1\), so

\[
  B(P,L)=O(Pq+q^2+P+q).
\]

### Lemma 4: information per collision

Every informative ordinary generic collision determines the entire scalar
\(\alpha\) through

\[
  \alpha=(a'-a)(b-b')^{-1}.
\]

There is no generic collision that reveals only \(\alpha\) modulo a
multiplicative subgroup or only a many-to-one value \(\alpha^d\): equality of
affine labels is a linear equation with either zero or one solution.

### Lemma 5: uncertified nonlinear-output bound

Suppose a collision-free algorithm outputs a previously constructed handle
with formal label \(a+bX\). Conditioned on its transcript, correctness for
target \(f(\alpha)G\) is possible for at most \(\rho_f\) values of \(\alpha\).
Therefore

\[
  \Pr[R=f(\alpha)G]
  \le
  \frac{B(P,L)+\rho_f}{r-1}.
\]

For \(f(X)=X^d\),

\[
  \Pr[R=\alpha^dG]
  \le
  \frac{B(P,L)+d}{r-1}.
\]

The \(d/(r-1)\) term is an accidental-output probability, not an acquisition
algorithm with a recognizable success event.

### Lemma 6: certificate-bearing lower bound

Let the verifier have perfect soundness and use only the ordinary generic
interface. In the sub-rho regime
\(B(P,L)+\rho_f<r-1\), a collision-free transcript cannot contain an accepted
certificate for \(R=f(\alpha)G\).

**Proof.** Couple the same formal transcript, algorithm coins, verifier coins,
and lazy-sampled handles across all \(\alpha\) avoiding the transcript's
affine collision equations. The verifier has the same view and decision on
each coupled instance. Because at most \(\rho_f\) such scalars make the
selected affine output equal \(f(\alpha)G\), at least one coupled scalar makes
it invalid. Acceptance would violate instance-wise soundness. Hence acceptance
requires an informative collision. \(\square\)

For a verifier with soundness error \(\varepsilon_s\),

\[
  \Pr[\text{accepted correct acquisition}]
  \le
  \frac{B(P,L)}{r-1}+\varepsilon_s
\]

within the same nonvacuous regime.

Thus constant certified success and negligible \(\varepsilon_s\) require

\[
  Pq+q^2=\Omega(r).
\]

For no preprocessing, \(q=\Omega(\sqrt r)\). If preprocessing is charged for a
single instance, \(P+q=\Omega(\sqrt r)\). In exponent notation, with
\(P=N^{\pi+o(1)}\) and \(q=N^{\beta+o(1)}\),

\[
  \max(\pi+\beta,2\beta)\ge 1,
  \qquad
  \max(\pi,\beta)\ge \tfrac12.
\]

The theorem is time/query based and does not assert a positive memory lower
bound: Pollard-style collision search can retain memory exponent zero.

### Lemma 7: expected-work and inverse-success accounting

A Las Vegas certified acquisition with expected charged work \(T\) can be
truncated at \(2T\), preserving success probability at least \(1/2\).
Lemma 6 then gives

\[
  T=\Omega(\sqrt r)
\]

for the no-preprocessing, single-instance ordinary model.

For an uncertified \(q=N^{\beta+o(1)}\) attempt without preprocessing,

\[
  p_{\rm lucky}
  \le N^{\max(2\beta,\delta)-1+o(1)}.
\]

Repeating such an attempt does not create a valid expected-time algorithm
unless success is recognizable. An ordinary generic recognizer is precisely a
certificate verifier and restores the certified bound. Reporting only
per-attempt cost while omitting \(1/p\), or assuming an omniscient scorer, is
invalid.

## 4. Composition with the known Cheon baseline

Given the additional same-group point \(\alpha^dG\), Cheon's known
auxiliary-input algorithm costs

\[
  C_{\rm Cheon}
  =
  N^{(1-\delta)/2+o(1)}
  +
  N^{\delta/2+o(1)}.
\]

Its exponent is

\[
  \chi(\delta)
  =
  \max\left\{\frac{1-\delta}{2},\frac{\delta}{2}\right\},
\]

minimized at \(\delta=1/2\), where
\(\chi(1/2)=1/4\). The cited rho/distinguished-point realization permits
memory exponent zero up to subpolynomial factors.

For ordinary input, the complete cost is

\[
  C_{\rm ordinary}
  =
  C_{\rm acquire}
  +
  C_{\rm Cheon}
  +
  C_{\rm certificate}
  +
  C_{\rm verification}.
\]

Lemma 6 gives

\[
  \operatorname{exp}(C_{\rm acquire})\ge \tfrac12
\]

for a constant-success certified generic acquisition. Therefore

\[
  \operatorname{exp}(C_{\rm ordinary})\ge \tfrac12.
\]

At balanced \(d=N^{1/2+o(1)}\), Cheon's downstream \(1/4\) term is dominated by
the restored \(1/2\) acquisition term. Recovering \(\alpha\) by Pollard rho,
computing \(\alpha^dG\), and then invoking Cheon is valid but redundant and
does not beat rho.

Verification from a disclosed scalar witness uses \(zG=Q\), modular
exponentiation \(z^d\bmod r\), and a known-scalar multiplication, all
\(N^{o(1)}\) beyond acquisition.

## 5. Typed non-generic escape theorem

A graded bilinear tower of depth at least \(d\) consists of cyclic additive
groups

\[
  \mathbb H_1,\ldots,\mathbb H_d
\]

of common prime order \(r\), distinguished generators \(T_i\), and maps

\[
  e_{i,j}:\mathbb H_i\times\mathbb H_j\longrightarrow\mathbb H_{i+j}
  \quad (i+j\le d)
\]

satisfying

\[
  e_{i,j}(xT_i,yT_j)=xyT_{i+j}.
\]

The ordinary input is placed at level one:

\[
  T_1=G,\qquad Q=\alpha T_1.
\]

Using addition chains:

- construct \(T_d\) from \(T_1\);
- construct \(A_d=\alpha T_d\), for example by combining \(Q\) with
  \(T_{d-1}\);
- construct \(D_d=\alpha^dT_d\) recursively from
  \(D_1=Q\) using
  \(D_{i+j}=e_{i,j}(D_i,D_j)\).

Binary addition chains require \(O(\log d)\) map evaluations when prior
intermediate values can be reused. All three outputs are in the same group
\(\mathbb H_d\), so the Cheon input is correctly typed:

\[
  T_d,\quad \alpha T_d,\quad \alpha^dT_d.
\]

A derivation DAG is a certificate: the verifier recomputes every declared map
evaluation. Soundness additionally depends on a certified tower setup whose
verification cost and error must be charged.

Let:

- \(C_{\rm build}=N^{\kappa_b+o(1)}\) be tower construction;
- \(K\) be the number of instances over which construction is amortized;
- the total \(O(\log d)\) map-evaluation cost be
  \(N^{\kappa_e+o(1)}\);
- tower and derivation verification cost be
  \(N^{\kappa_v+o(1)}\);
- accessed parameter/data cost be \(N^{\xi+o(1)}\);
- peak memory be \(N^{\mu+o(1)}\).

The charged acquisition exponent is

\[
  \kappa_{\rm tower}
  =
  \operatorname{exp}\left(
    C_{\rm build}/K+
    N^{\kappa_e+o(1)}+
    N^{\kappa_v+o(1)}+
    N^{\xi+o(1)}
  \right).
\]

For a single instance, \(K=1\). The composed expected-time exponent is

\[
  \max\{\kappa_{\rm tower},\chi(\delta)\}.
\]

Hence a strict conditional sub-rho result requires

\[
  \max\{\kappa_{\rm tower},\chi(\delta)\}<\tfrac12.
\]

At \(\delta=1/2\), this becomes
\(\kappa_{\rm tower}<1/2\), with conditional total exponent
\(\max\{\kappa_{\rm tower},1/4\}\).

This construction does not assume \(\alpha\) or \(\alpha^dT_d\); its bilinear
maps create multiplicative scalar interaction. It does, however, assume a
succinct, certified graded tower reaching level
\(d=N^{1/2+o(1)}\). A parameter description or setup of size \(\Theta(d)\)
already has exponent \(1/2\) and fails the strict inequality. Ordinary elliptic
curves supply no such tower in the declared generic model. Existence with the
required costs is unresolved here.

## 6. Scope and excluded interfaces

The barrier proves only an average-case statement over uniform
\(\alpha\in\mathbb F_r^*\) in the random-encoding generic model. It covers
adaptive algorithms, randomness, known-scalar operations, and charged
\(\alpha\)-independent preprocessing.

It does not cover:

- coordinate algorithms exploiting a specified curve representation;
- symmetric, asymmetric, graded, or multilinear maps;
- efficiently certified nonlinear maps between groups;
- order-changing or field-changing correspondences;
- input-dependent endomorphisms;
- side channels or certified leakage correlated with \(\alpha\);
- quantum algorithms;
- nonuniform \(\alpha\)-dependent advice;
- targets \(f\) with \(\rho_f=\Theta(r)\);
- uncharged preprocessing or unreported multi-instance amortization.

Ordinary subgroup endomorphisms and group homomorphisms whose scalar action is
a disclosed constant remain affine and are not escapes.

## 7. Pre-registered proof controls

No control was executed.

1. **Symbolic affine-label simulator:** propagate pairs \((a,b)\) for every
   ordinary operation and flag equality of distinct pairs.
2. **Identical-shape random-label null:** replace formal affine labels by
   independent identifiers while retaining the same query and branch graph;
   any claimed nonlinear signal present in both traces is an encoding artifact.
3. **Oracle-removal control:** replace each non-generic map by an opaque random
   type-correct map. The graded-tower construction must then lose its scalar
   multiplication law.
4. **Fiber/inverse-success control:** report \(\rho_f\), accidental success,
   recognizability, and the full \(1/p\) factor.
5. **Type/orientation audit:** verify every relation uses
   \(Q=\alpha G\) and that the three Cheon points inhabit one order-\(r\)
   group.
6. **Composition control:** restore acquisition, setup, data, certificate, and
   verification costs before comparing against exponent \(1/2\).

## 8. Cheapest bounded proof repair

Independent review should first check the adaptive coupling and certificate
lemma under the exact perfect/statistical soundness definition. If accepted,
the ordinary generic barrier is complete within its stated scope. The next
bounded theory task is to test whether any concrete, succinct graded
correspondence for prime-order elliptic-curve subgroups satisfies the typed
tower interface with total setup/data/evaluation exponent below \(1/2\).
Failure to instantiate that interface is not evidence that every non-generic
escape is impossible.
