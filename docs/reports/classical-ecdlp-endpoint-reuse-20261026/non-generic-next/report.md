# Non-generic continuation: an ordered-root constructor obligation

2026-10-26. The remaining task is a uniform constructor for an order-sensitive coordinate predicate. This note defines that object, gives its reduction to scalar recovery, and supplies a cheap wrong-root control. It also resolves the parameter-dependence caveat in a Miller differential screen. These are derived mathematical checks and bounded source inspection; no new scientific run or algorithmic speedup was measured.

![Analytical proof-search map. The missing constructor is explicit; existence, a correct field root, and a short symbolic expression are not a priced evaluator.](proof-map.pdf){width=95%}

## Exact object and the sparse difference equation

Let $E:y^2=f(x)=x^3+ax+b$ over $\mathbf F_p$, with $p>3$, and let $P$ have odd prime order $r\ne p$. Put $m=(r-1)/2$. The subgroup abscissas $x(jP)$, $1\le j\le m$, are distinct. Define
\[
K_P(X)=\prod_{j=1}^{m}(X-x(jP)),\qquad
A_P(x(jP))=y(jP),\quad \deg A_P<m.
\]
Interpolation gives a unique $A_P$, and $A_P^2=f\pmod {K_P}$. More importantly,
\[
y(kP)=A_P(x(kP))\quad\Longleftrightarrow\quad 1\le k\le m.
\]
Thus this *generator-ordered* square root would decide a scalar half, rather than an arbitrary point-sign convention.

Equivalently, let $H(kP)=0$ for $0\le k\le m$ and $H(kP)=1$ for $m+1\le k<r$. It is the unique solution on the subgroup of
\[
H(O)=0,\qquad H(R+P)-H(R)=\delta_{mP}(R)-\delta_{-P}(R).
\]
The two pulse locations are public. A finite-point equality indicator uses Fermat zero tests with $O(\log p)$ field multiplications; identity points are handled separately. The missing operation is a cheap, uniform **discrete antiderivative** of this sparse right-hand side in the finite coordinate algebra. Iterating around the orbit gives it in linear work and is not the desired construction.

The values $H(Q),H(2Q),\ldots$ give the binary digits of $k/r$. For $L=\lceil\log_2r\rceil+1$ digits representing the integer $v$, the interval
\[
v/2^L\le k/r<(v+1)/2^L
\]
contains one possible scalar, $k=\lceil rv/2^L\rceil$, which is publicly checked. This is a reduction conditional on the constructor, not an implemented solver.

## Four cheap audits

**Identifiability.** The congruence $A^2=f\pmod {K_P}$ has exactly $2^m$ roots: each abscissa permits an independent sign. The kernel polynomial is unchanged when $P$ is replaced by any other generator. Only the specified ordering selects the desired root. Correct roots, subgroup membership, or one anchored value do not identify it.

**Quantifier and price.** The required statement is one uniform procedure from public $(E,P,r)$, producing a circuit correct for all targets in the declared family. Construction, constants, kernel data, exceptional inputs, arithmetic bit cost, evaluation and final recovery all count. Existence by interpolation, a circuit built from known logs, or target-specific advice is not this procedure.

**Nearby known-false control.** For $p=3\bmod4$, $A_0=f^{(p+1)/4}$ is a short circuit and a valid square root on the subgroup abscissas. Normalize it at $P$:
\[
\sigma_P(X)=\frac{y(P)}{A_0(x(P))}A_0(X).
\]
It even has $\sigma_P(x(P))=y(P)$ and $\sigma_{-P}=-\sigma_P$, but need not have scalar ordering. On $E/\mathbf F_{11}:y^2=x^3+x+6$, there are 13 points. With $P=(2,7)$, $2P=(5,2)$ and $3P=(8,3)$, the normalized circuit is $-f^3$. It gives $\sigma_P(8)=8\ne3$, although $3\le m=6$. This hand-derived counterexample is a required control, not an experiment.

**Method ceiling.** For $r\ge11$, the nonzero polynomial $A_P^2-f$ has at least $m$ roots, hence $\deg A_P\ge\lceil m/2\rceil$. Dense coefficients therefore require linear-size output. This does not lower-bound straight-line circuit size: $A_0$ already demonstrates high degree with a short circuit. Likewise, a short functional DAG for a translated sum must not treat calls at different points as one evaluation. An expanded sum of $s$ translated two-pulse functions has support at most $2s$, so this elementary representation requires linear terms; nonlinear coordinate circuits remain outside that statement.

## Relationship to previous work

The pilot's L2 measured linear EDS complexity and one 15-monomial quadratic grammar; L6 enumerated residual states and orientation data; L7/L8 used truth-derived coefficients. None supplied a uniform high-degree circuit constructor for this exact ordered root. Their bounded results do not establish a circuit-size lower bound.

The atlas's low-degree coordinate census, torsor/deck rational-section obstruction, and recognizable/invertible-subset lead are relevant constraints. Here the root identity holds only modulo a finite subgroup polynomial, not as a rational section of the whole elliptic double cover. The half predicate is not a homomorphism or a translation-respecting small quotient. The precise degree-versus-circuit obligation is therefore not discharged by those arguments. Nevertheless, earlier scalar-orbit period and root-to-source orientation proposals already expose related constructor gaps: different wording is not evidence of novelty.

**Current scope:** no qualified new constructor was found in this search. This is a sharpened proof obligation, not an admitted experimental algorithm. The next mathematical submission must provide its explicit circuit and cost recurrence before another cohort is collected for it.

## Miller differential: preserve the variable-parameter constant

Fix $S\ne O$ in the rational $r$-torsion subgroup and normalize the Miller function with divisor $r[S]-r[O]$. For $t=-x/y$ write
\[
f_{r,S}=t^{-r}(1+C_r(S)t+\cdots),\qquad \omega=dx/(2y).
\]
Riemann-Roch gives the identity in the **evaluation point**
\[
\frac{df_{r,S}/f_{r,S}}{\omega}
=r\frac{y+y_S}{x-x_S}+C_r(S).
\]
For fixed base $S$, the evaluation-point dependence is a chord slope. But if the Miller parameter is the variable target $S=Q$, the nonlinear public quantity $C_r(Q)$ remains and must not be discarded.

Normalize line/vertical factors $g_{R,S}$ to leading coefficient one. Their first Laurent coefficient is the chord/tangent slope $\lambda(R,S)$; for vertical or identity addition take $\lambda=0$. Divisors and leading terms give
\[
C_r(R+S)=C_r(R)+C_r(S)-r\lambda(R,S).
\]
Set $C_r(O)=0$. Therefore $Z=-C_r/r$ is the unique primitive satisfying
\[
Z(R+S)=Z(R)+Z(S)+\lambda(R,S).
\]
Uniqueness follows because the difference of two primitives is a homomorphism from an $r$-group to the additive $p$-group. A normalized Miller-chain coefficient recurrence computes $C_r(S)$ in $O(\log r)$ group/field steps. These identities were checked in a separate read-only algebra pass; this was not an independent scientific review.

This identifies the map with **IDEA-20261016-09fd08**, the existing zeta-defect proposal. Its proposed chance/white-spectrum predictions are not established by that proposal's existence. The earlier IDEA-20260905-24b41a also groups Miller and additive torsor coordinates together. No new scalar-information claim or family closure follows here.

A model boundary also remains explicit: KN-TECH-005 applies to opaque group encodings. KN-FIND-002 labels its coordinate-based jet discussion a structured GGM and acknowledges that the opaque simulator lacks coordinate access. A lower-bound transfer between those models needs its own argument; it is not supplied by calling a coordinate function deterministic.

## Provenance and next discriminating step

Read sources: the completed pilot report; the exotic EDS, coordinate-statistic, p-adic, torsor, Miller and invertible-subset atlas rows; the exact Miller/zeta proposals; KN-FIND-002 and KN-TECH-005. The current source hashes and revisions are in source-manifest.json. Targeted searches across the three repositories and public literature did not locate a matching ordered-root constructor. This bounded search is not a novelty or impossibility result; the knowledge-index tools were unavailable.

Require the next proposed constructor to pass the anchored $\mathbf F_{11}$ control, the exact two-pulse identity and its point exceptions, generator/coordinate covariance, and a charged construction/evaluation recurrence. A failed candidate only resolves its stated grammar. A proved small circuit advances implementation readiness; it does not by itself establish a runtime exponent or move a scientific ledger status. The linked problem draft retains this missing ingredient and its exit conditions.

