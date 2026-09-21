# FC0-R2 stochastic invocation ledger

Task `TASK-20260730-037` · convention `CSIDH-COLLIMATION-FC0-R2`  
Scope: zero-compute accounting control for `IDEA-20260729-001`

## 1. Probability space and stopping process

Let \((\Omega,\mathcal F,\Pr)\) contain all sieve, regularization,
postprocessing, recovery, and classical-tail randomness. Let
\(\mathcal F_k\) be the information available after the \(k\)-th top-level
sieve invocation. The stopping time

\[
\tau(\omega):=\inf\{k\geq 1:\text{the declared recovery rule enters its
terminal classical-tail or failure state after invocation }k\}
\]

counts every fresh-sieve discard, retry, and recovery invocation. The realized
ordered invocation ledger is
\(\mathcal I(\omega)=(I_1,\ldots,I_{\tau(\omega)})\). No independent
success multiplier may be applied after these events have already been
included in \(\tau\).

For invocation \(k\), define nonnegative random variables:

- \(Q_k\): complete labeled-state oracle calls;
- \(S_k\): non-oracle logical work of the full sieve traversal, including
  every traversal repeated after a discard;
- \(P_k\): postprocessing work after that invocation;
- \(C_k\): associated classical sieve/postprocessing work;
- \(E_k^{\rm oracle},E_k^{\rm sieve},E_k^{\rm post}\): error contributions,
  but only after all three have been mapped to the final operational failure
  metric in Section 4.

Let \(H\) be terminal classical-tail work and \(M_{\rm tail}(t)\) its live
classical memory. Let \(W_k(t)\), \(R_k(t)\), and \(B_k(t)\) respectively be
coherent logical width, QRACM bits, and other classical backing memory on one
global schedule. The source-derived hard QRACM bound is a bound on \(R_k(t)\),
not an equality with \(W_k(t)\).

## 2. Declared comparison statistic

FC0-R2 uses **expectation for additive work**, **essential-supremum/worst-case
for peak memory**, and an **operational failure-probability bound for errors**.
A realized trace is retained only as an audit object. It is never required to
equal an expectation.

| Resource | Realized random variable | FC0-R2 comparison statistic | Rule |
| --- | --- | --- | --- |
| Queries | \(Q(\omega)=\sum_{k=1}^{\tau(\omega)}Q_k(\omega)\) | \(\mathbb E Q\) | Reconcile a source expected/estimated aggregate only with \(\mathbb E Q\), after the source meaning is verified. |
| Repeated sieve | \(S(\omega)=\sum_{k=1}^{\tau(\omega)}S_k(\omega)\) | \(\mathbb E S\) | Every fresh traversal is included; no one-traversal shortcut. |
| Postprocessing | \(P(\omega)=\sum_{k=1}^{\tau(\omega)}P_k(\omega)\) | \(\mathbb E P\) | Failed postprocessing that triggers a fresh sieve remains charged before the next invocation. |
| Classical tail | \(H(\omega)\) | \(\mathbb E H\) | Tail is terminal classical work under its declared enumeration/stopping rule; canonical quantum-tail query/T/depth/width are zero. |
| Other additive classical work | \(\sum_{k\leq\tau}C_k+H\) | expectation | Uses the same stopping law as queries and repeated work. |
| Coherent logical width | \(W_{\rm peak}(\omega)=\sup_t W(t,\omega)\) | \(\operatorname*{ess\,sup}_\omega W_{\rm peak}\) | Never summed across invocations; overlap must be represented on the global timeline. |
| QRACM | \(R_{\rm peak}(\omega)=\sup_t R(t,\omega)\) | enforced hard bound / essential supremum | For the pinned row, each charged vector is truncated by partial measurement at \(\widetilde L_{\max}=8L\); this does not bound all non-QRACM memory. |
| Classical backing/tail memory | \(B_{\rm peak}(\omega)=\sup_t(B(t,\omega)+M_{\rm tail}(t,\omega))\) | essential supremum, or a separately named percentile if no hard bound exists | Currently unresolved; an expectation is not substituted for peak memory. |
| Errors | final failure event \(F\) | \(\Pr[F]\) upper bound | Not an additive work expectation; use the composition contract in Section 4. |

If a later row reports a percentile, it must name one common level
\(1-\alpha\) and compute
\[
b_X(1-\alpha):=\inf\{x:\Pr[X\leq x]\geq1-\alpha\}
\]
for each additive resource \(X\in\{Q,S,P,H,\sum C_k+H\}\) under the same
stopping process. Such percentiles are supplementary in FC0-R2 and may not be
mixed with \(\mathbb E Q\) in one equality. Memory remains a hard/worst-case
quantity unless a separately named resource posture explicitly permits a
percentile memory budget.

## 3. Expectation identities and source-reconciliation gate

Provided the nonnegative sums are measurable, Tonelli's theorem gives

\[
\begin{aligned}
\bar Q&:=\mathbb E\!\left[\sum_{k\geq1}\mathbf1_{\{k\leq\tau\}}Q_k\right],\\
\bar S&:=\mathbb E\!\left[\sum_{k\geq1}\mathbf1_{\{k\leq\tau\}}S_k\right],\\
\bar P&:=\mathbb E\!\left[\sum_{k\geq1}\mathbf1_{\{k\leq\tau\}}P_k\right],\\
\bar C&:=\mathbb E\!\left[\sum_{k\geq1}\mathbf1_{\{k\leq\tau\}}C_k+H\right].
\end{aligned}
\tag{R2-EXPECT}
\]

These are definitions, not instantiated Peikert constants. Reconciliation
with \(\widetilde Q_{\rm total}\) requires a primary-source or source-code
statement fixing whether that quantity is an expectation, percentile, or
deterministic model estimate, plus the stopping law needed to evaluate all
four expectations. The archived paper excerpt calls it a total query estimate
and uses expected recovered information per run, but does not explicitly
identify \(\widetilde Q_{\rm total}=\mathbb E Q\) or provide the full law of
\(\tau\). Therefore the equality remains **unverified**.

## 4. Error semantics

For each realized transcript \(h\) through stopping, every oracle contribution
must be a complete-channel diamond-distance bound, and every sieve,
postprocessing, and tail contribution must first be mapped by a cited theorem
to the same final operational event \(F\). Only then may a transcriptwise
hybrid/union bound be written:

\[
\Pr[F\mid h]\leq
\sum_{k\leq\tau(h)}
\left(E_k^{\rm oracle}(h)+E_k^{\rm sieve}(h)+E_k^{\rm post}(h)\right)
+E^{\rm tail}(h).
\tag{R2-ERR-PATH}
\]

Averaging this pathwise inequality over transcripts yields an operational
average failure bound. It does not turn error into an expected work unit.
Absent the required mappings for sieve, postprocessing, and tail errors,
`R2-ERR-PATH` is a type requirement only and O3 remains partial.

## 5. Required O1 stochastic mutation

Control object: let \(R\sim\mathrm{Geom}(p)\) on \(\{1,2,\ldots\}\), let every
invocation cost \(q\) oracle calls, \(s\) sieve work, and \(z\)
postprocessing work, and let terminal tail work be \(h\). Then

\[
\mathbb E Q=q/p,\quad
\mathbb E S=s/p,\quad
\mathbb E P=z/p,\quad
\mathbb E H=h.
\]

Two realized traces with \(R=1\) and \(R=3\) respectively report
\((q,s,z,h)\) and \((3q,3s,3z,h)\). Neither trace is required to equal the
expectation vector. Peak memory is the maximum live allocation on each trace,
not \(R\) times per-invocation memory. Error terms are admitted only under
Section 4's common operational metric.

**Control result: PASS as a semantic/type mutation.** The ledger treats every
additive resource under one expectation semantics and does not force a trace
to equal an expectation. **Source instantiation result: UNRESOLVED.** The
paper excerpts do not supply \(p\), an equivalent stopping distribution, or
the joint per-invocation ledger. Hence this control repairs the O1 category
error but does not instantiate a source-compatible query/memory vector.

## 6. Scope and unresolved fields

- No stochastic simulation, curve, isogeny, or quantum-circuit computation was
  performed.
- The stopping law, per-invocation repeated work, postprocessing work,
  terminal-tail distribution, non-QRACM peak memory, and common error mapping
  remain uninstantiated.
- The uniform complete action-oracle channel remains a later boundary.
- This ledger supports no numerical comparison, parameter recommendation,
  security label, breakthrough claim, or goal-completion claim.
