# TASK-20260723-801 Newton-saturation screen

## Verdict

`ADMIT_ASYMPTOTIC_NEWTON_SATURATION_PROOF_ROUTE_FOR_REVIEW`.

`breakthrough_claimed: false`

`first_failed_obligation: null`

This is a zero-compute derivation candidate, not an established theorem or an
official state transition. It gives an all-\(m\) corner-coefficient route and
an explicit classification of the only target sections where the Newton box
can lose a vertex. Independent review must check the normalization and
degenerate cases before the result is treated as a theorem.

No finite-field search, polynomial expansion, relation collection,
standardized-curve execution, key recovery, or cryptographic-size computation
was performed.

## Exact theorem candidate

Let

\[
E:\ y^2=x^3+Ax+B
\]

be nonsingular over a field of characteristic different from \(2,3\). Let
\(S_m\) be the canonical recursively defined Semaev summation polynomial and
put

\[
f_{m,t}(x_1,\ldots,x_{m-1})
  =S_m(x_1,\ldots,x_{m-1},t),\qquad
D_m=2^{m-2}.
\]

Choose \(\beta\) in the algebraic closure with \(\beta^2=B\), and write
\(P_0=(0,\beta)\). Define the finite exceptional set

\[
\mathcal E_m(E)=
\left\{x([r]P_0):
  1\le r\le m-1,\ [r]P_0\ne\mathcal O\right\}.
\]

Repeated values are counted once. Thus
\(\lvert\mathcal E_m(E)\rvert\le m-1\); restriction to \(\mathbb F_p\), to
liftable target coordinates, or to a chosen prime-order subgroup can only
make it smaller.

The theorem candidate is

\[
t\notin\mathcal E_m(E)
\quad\Longrightarrow\quad
\operatorname{Newt}(f_{m,t})
  =[0,D_m]^{m-1}.
\]

Moreover, if \(t\in\mathcal E_m(E)\), at least one box-corner coefficient
vanishes, so the Newton polytope is a proper subpolytope of that box. This
classifies box saturation, not the exact interior support of an exceptional
section.

For a square system of \(n=m-1\) nonexceptional sections, every Newton
polytope is the same box and hence

\[
\operatorname{MV}
  =n!D_m^n
  =(m-1)!\,2^{(m-1)(m-2)}.
\]

This is exactly the multigraded box Bézout number measured at \(m=3,4,5\) in
EV-BKK-001 and EV-BKKMV-001.

## Corner reduction

For \(0\le k\le m-1\), let \(c_{m,k}(t)\) be the coefficient of any box
corner having exactly \(k\) free-variable exponents equal to \(D_m\), with
the remaining exponents zero. Symmetry of \(S_m\) makes this depend only on
\(k\), reducing \(2^{m-1}\) vertices to \(m\) coefficient classes.

The explicit \(S_3\) formula gives

\[
c_{3,0}=A^2-4Bt,\qquad
c_{3,1}=t^2,\qquad
c_{3,2}=1.
\]

Semaev's established leading-coefficient identity says that the coefficient
of \(x_i^{D_m}\) in \(S_m\), viewed as a polynomial in any one variable
\(x_i\), is \(S_{m-1}^2\), up to the fixed nonzero normalization. Choose one
of the \(k\) maximal-exponent free variables as \(x_i\). Each remaining
variable has degree at most \(D_m/2\) in \(S_{m-1}\). In the square:

- exponent \(D_m\) can only be obtained as \(D_m/2+D_m/2\);
- exponent \(0\) can only be obtained as \(0+0\).

There is therefore no convolution cancellation at a box corner, and

\[
c_{m,k}(t)=c_{m-1,k-1}(t)^2
\qquad(1\le k\le m-1).
\]

Consequently,

\[
\begin{aligned}
c_{m,k}&=c_{m-k,0}^{\,2^k}
  &&(0\le k\le m-3),\\
c_{m,m-2}&=t^{D_m},\\
c_{m,m-1}&=1.
\end{aligned}
\]

All corner losses are therefore inherited from an all-zero corner at a lower
order, together with \(t=0\).

## The all-zero corner

The remaining coefficient is simply

\[
c_{m,0}(t)=S_m(0,\ldots,0,t).
\]

Over the algebraic closure, the two points above \(x=0\) are \(P_0\) and
\(-P_0\). A choice of \(m-1\) such points sums to

\[
[r]P_0,\qquad
r\in\{-(m-1),-(m-3),\ldots,m-3,m-1\}.
\]

By the defining Semaev zero property,
\(S_m(0,\ldots,0,t)=0\) exactly when a point \(Q\) above \(t\) can cancel one
of those sums. Its finite roots are therefore the \(x\)-coordinates of the
corresponding affine multiples of \(P_0\). Multiplicity and torsion
collisions are irrelevant to Newton support.

As \(k\) varies, the inherited all-zero corners cover the alternating parity
classes from orders \(3,\ldots,m\), and \(c_{m,m-2}=t^{D_m}\) adds
\(x(P_0)=0\). Their union is exactly contained in, and subject to the
normalization check equals,

\[
\{x([r]P_0):1\le r\le m-1,\ [r]P_0\ne\mathcal O\}.
\]

Outside this set all box vertices occur. Since the per-variable degree bound
already puts the support inside \([0,D_m]^{m-1}\), its convex hull must be the
full box.

The \(B=0\) case makes \(P_0=(0,0)\) a two-torsion point. It can only merge or
remove members of the finite set, but the exact specialization should be
checked separately in review rather than hidden in the generic argument.

## Typed-oracle admission card

Oracle ID: `NEWTON-CORNER-ADMISSION-001`.

The oracle is deterministic and stateless. Equality means exact polynomial
identity or exact field equality; there is no numerical threshold, hidden
root selector, randomness, or state.

### Inputs

Theorem mode requires:

1. the field or universal coefficient ring and its characteristic;
2. exact nonsingular short-Weierstrass parameters \(A,B\);
3. \(m\ge3\) and a symbolic target \(t\);
4. the canonical recursive \(S_m\) circuit and its nonzero normalization.

A specialized cost claim additionally requires:

1. exact \((p,A,B,t)\) and the prime-order subgroup \(H=\langle P\rangle\) of
   order \(N\);
2. target provenance: fixed public, known-log relation target, or fresh
   scalar-blind masked target;
3. exact factor base, masking law, arity, success, and miss semantics; and
4. setup, relation collection, output, independent rank, factor-log linear
   algebra, fresh-target descent, verification, traffic, and peak-memory
   costs.

### Outputs

Theorem mode returns:

- \(D_m\) and the \(m\) corner-class identities;
- the exceptional set represented by affine multiples \([r]P_0\);
- `SATURATED_GENERIC`;
- the full-box mixed-volume formula; and
- exact references or hashes for the normalization and lemmas used.

Specialized mode returns either:

- `SATURATED_SECTION`, after every corner class evaluates nonzero; or
- `EXCEPTION_SECTION`, with the exact missing corner classes.

An exceptional result also returns `NO_COST_CREDIT` unless the actual support
or mixed volume and the complete relation-to-descent ledger are supplied.
A missing corner is not by itself a sub-rho algorithm.

### Replay and verification

A verifier must:

1. re-evaluate the three \(S_3\) corner classes;
2. verify symmetry, degree, and the leading-coefficient identity;
3. replay the corner-square induction without expanding \(S_m\);
4. verify the all-zero root set from the defining summation property;
5. establish the presence of every box vertex before using the box
   mixed-volume formula; and
6. for any algorithmic claim, replay target selection, misses, source tuple,
   signs, direct group sum, relation rank, factor logs, and fresh masked
   descent.

### Forbidden free oracles

The following cannot be supplied at zero cost:

- a dense support table, mixed volume, exceptional root, resultant
  factorization, or coefficient-dependent lifting;
- a target-fitted exceptional section or its scalar relation;
- source tuples, signs, \(y\)-branches, factor logs, target logs, rank, or
  descent witnesses;
- a map from an arbitrary target into \(\mathcal E_m(E)\) without exact scalar
  provenance and charged construction;
- successful labels for failed decompositions, points at infinity, repeated
  relations, or dependent rows; or
- an alternate curve model, unsectioned support, or lifted polynomial system
  treated as though it were certified by the original sectioned box.

Standardized-curve execution, key recovery, and cryptographic-size runs are
also outside this task.

## Fully charged cost versus Pollard rho

Pollard rho has expected work \(N^{1/2+o(1)}\) group operations and
\(N^{o(1)}\) serial memory. BSGS has the same work exponent with
\(N^{1/2+o(1)}\) stored group elements.

For a nonexceptional section, the original Newton driver equals the box
Bézout driver. Support awareness alone changes no exponent. The complete path
still has cost

\[
\begin{aligned}
W={}&W_{\rm setup}
 +R\,W_{\rm full\ box\ solve}
 +W_{\rm relation\ output}
 +W_{\rm rank}\\
 &+W_{\rm factor\ logs}
 +W_{\rm fresh\ descent}
 +W_{\rm verification}
 +W_{\rm traffic},
\end{aligned}
\]

with peak memory charged separately. None of these terms is assigned zero.

For an exception-only route using a uniform scalar mask
\(Q+[u]P\), the masked point is uniform in \(H\). At most \(2(m-1)\) subgroup
points lie above the exceptional \(x\)-set, so

\[
\Pr[x(Q+[u]P)\in\mathcal E_m(E)]
 \le \frac{2(m-1)}{N}.
\]

Even granting success after the first exceptional hit, expected mask work is
\(\Omega(N/m)\). A replayable decomposition has \(m\) factor entries and
signs, so output alone is \(\Omega(m)\). Hence

\[
W_{\rm exception\ bridge}
  =\Omega(N/m+m)
  =\Omega(\sqrt N).
\]

This is equality with the rho exponent, not an advantage, and it misses the
campaign work cap \(0.45\). Decomposition failures, relation collection,
independence, rank, factor logs, fresh descent, verification, and memory can
only add cost.

Choosing \([r]P_0\) directly does not evade the charge: it does not freely
provide \(\log_P(P_0)\), independent known right-hand sides, enough
decompositions, or a bridge for a fresh \(Q\). Any different target-uniform
bridge is a new mechanism that must receive its own typed card. This report
does not declare such a mechanism impossible.

## Prior art and novelty boundary

The internal search covered `knowledge/`, `ledger/hypotheses/`,
`ledger/proposals/`, the BKK evidence, and EXP-BKK-001/BKKMV-001/002.
EV-BKK-001 and EV-BKKMV-001 establish full boxes only for \(m=3,4,5\);
EXP-BKKMV-002 is an unexecuted \(m=6\) specification. No internal record gives
the all-\(m\) corner-exception classifier.

An external search found:

- Semaev, *Summation polynomials and the discrete logarithm problem on
  elliptic curves*, IACR ePrint 2004/031, for the symmetry, degree,
  summation-zero property, and leading coefficient \(S_{m-1}^2\);
- Yokoyama, Yasuda, Takahashi, and Kogure, *Complexity bounds on Semaev's
  naive index calculus method for ECDLP*, Journal of Mathematical
  Cryptology 14(1), 2020, DOI `10.1515/jmc-2019-0029`, which reports
  experimental density for almost every section but not this Newton-box
  exception theorem; and
- KN-LIT-014/015 for the BKK and polyhedral-solver background.

The proposal is therefore classified as `adaptation`, not as a novel theorem:
it composes a known leading-coefficient result, the defining Semaev semantics,
and the internal scoped BKK evidence into a new admission gate.

## Outcome map, controls, and falsification

The paper replay discriminates two explanations.

1. If the corner recurrence and all-zero root classification verify, generic
   sectioning is box-saturated for every \(m\). Any support win must use the
   explicit exceptional set and pass the target bridge and complete-cost
   card.
2. If either lemma fails, the first failing \(m\), Hamming weight, and extra
   coefficient factor identify a genuine support-exception theorem target.
   That result still receives no algorithmic credit until its frequency,
   mixed volume, relation supply, and fresh descent are charged.

Required controls are:

- the explicit \(S_3\) coefficients;
- symmetry by Hamming weight;
- \(t=0\) as a negative exception control;
- a symbolic nonexceptional target as a full-corner control;
- a nonzero-normalization check; and
- rejection of direct exceptional-target advice without scalar provenance.

The theorem route is falsified by any verified characteristic-at-least-5
section outside the stated set with a missing corner, by an extra vanishing
factor in the exact leading-coefficient extraction, or by an all-zero-corner
root not arising from the signed \(P_0\) sums. The cost conclusion is
falsified, only for its stated scope, by a fully typed target-uniform bridge
with complete \(o(\sqrt N)\) work after every stage is charged.

## Limits

This route covers the original target-sectioned Newton hull. It does not cover
the unsectioned polytope, alternate curve models, coefficient-dependent
liftings that change the polynomial system, all Gröbner or arithmetic
circuits, or non-Semaev algorithms. A full box also does not by itself prove a
lower bound for every solver. The cost statement is specifically for an
exception-only route whose bridge is uniform scalar masking with replayable
\(m\)-entry output.

The existing \(m=3,4,5\) records remain toy-scoped observations; they are
consistency checks, not the proof. No cryptographic advantage, ECDLP hardness
theorem, scalar recovery, or breakthrough is claimed.

## Ranking rationale

`IDEA-20260723-006` is the single idea I would test first. Its information
gain is high because one known leading-coefficient identity and one geometric
all-zero-corner lemma classify every \(m\) and expose the complete
corner-exception target set. Its paper-only replay is the cheapest valid
discriminator: it needs no support expansion, mixed-volume computation, toy
curve, or standardized-curve execution. A support-exception algorithm ranks
lower because no typed fresh-target bridge survives the
\(\Omega(N/m+m)\) uniform-mask and output charge.

The idea ID is task-local and not an official ledger proposal. The
Coordinator alone may file it or change research state after snapshot and
independent review.
