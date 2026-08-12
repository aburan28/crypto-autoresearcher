# FC0-R2 joint stopping-law and global-liveness control

Task `TASK-20260730-009` · convention `CSIDH-COLLIMATION-FC0-R2`  
Control count: one · curve/isogeny/circuit computation: none

## Pass rule

The control passes only if the pinned Peikert row supplies, or supports an
explicit construction of, all of the following on one probability space and
one global timeline:

1. a stopping time \(\tau\) covering recursive discards, failed
   regularization, repeated punctured-regularization attempts, fresh-sieve
   recovery runs, and terminal residual entry;
2. finite expectations
   \[
   \mathbb E\!\sum_{k\leq\tau}Q_k,\quad
   \mathbb E\!\sum_{k\leq\tau}S_k,\quad
   \mathbb E\!\sum_{k\leq\tau}P_k,\quad
   \mathbb E\!\left[\sum_{k\leq\tau}C_k+H\right];
   \]
3. a deterministic liveness/cleanup schedule giving finite hard or
   essential-supremum peaks for coherent workspace \(W\), QRACM \(R\), other
   classical backing \(B\), and terminal-tail memory \(M_{\rm tail}\); and
4. one final operational failure event \(F\), with every oracle, sieve,
   postprocessing, recovery, and tail error mapped to \(\Pr[F]\).

An estimated or typical per-run quantity cannot establish these joint
properties.

## Source extraction

Page numbers are one-indexed physical pages of the archived author-hosted PDF,
SHA-256
`d4785e2863eebe97eb3a2909e02d669d138b2080c6e96e42c70d8d4fd2e89675`.

- PDF page 12, Equation (3.3), models a sieve run's query count as
  \(Q=(r/(1-\delta))^d\log L_0\), under a random discard-fraction model. It
  does not define the joint law of top-level retries or recovery.
- PDF page 15, Section 3.4.1, says a failed regularization measurement
  discards the vector and runs the sieve again. The success probability is the
  realized least-frequency ratio \(mS/\widetilde L\); the reported ranges are
  empirical, not a uniform tail bound.
- PDF pages 15–16, Sections 3.4.2 and 3.4.4, permit repeated measurements on a
  leftover punctured vector and report expected recovered information. They
  do not define the number or dependence of fresh-sieve recovery runs.
- PDF page 18, Figure 1 and its bullets, call
  \(\widetilde Q_{\rm total}\) the total queries to recover all but the
  terminal residual, assume expected information per run, and assume an
  actual per-run query count within a factor of the Equation (3.3) estimate.
  No equation identifies this quantity with the required expected random sum.
- PDF page 14, Equation (3.5), bounds bits of reusable QRACM as a function of
  \(L_{\max}\). PDF page 18 imposes
  \(\widetilde L_{\max}=8L\) per generated vector by partial measurement.
  These statements do not give births, deaths, cleanup, retry concurrency,
  non-QRACM backing, or tail memory on a global schedule.
- PDF page 20, Equation (4.1), estimates non-oracle sieve T gates as
  \(36\widetilde L(2/(1-\delta))^d\), where \(\widetilde L\) is an upper bound
  on typical phase-vector length. Its derivation charges a tree traversal and
  QRACM lookups; it does not jointly charge all top-level retries,
  postprocessing, recovery, and the classical tail.

Thus the source supports FC0-R2's resource types and the narrow per-vector
QRACM cap, but not a finite source-compatible joint law or complete liveness
schedule.

## Candidate joint ledger attempt

The only source-compatible candidate found is the uninstantiated FC0-R2
schema:

\[
\tau=\inf\{k\geq1:\text{recovery enters terminal tail or failure after run }k\},
\]

with additive resources summed through \(\tau\), peaks taken on one global
timeline, and errors mapped to a final event \(F\). The paper does not provide
the transition kernel, independence conditions, tail bound, deterministic
retry-concurrency rule, complete register inventory, cleanup rule, or
component-to-\(F\) maps needed to turn that schema into a finite ledger.

In particular, choosing an iid geometric law from empirical success
percentages would add an uncited independence and uniform-success assumption.
Choosing sequential cleanup would add an uncited end-to-end liveness contract.
Neither is extracted from the pinned source.

## C2 heavy-tail mutation

Let the number of top-level invocations have
\[
\Pr[\tau=n]=\frac1{n(n+1)},\qquad n\geq1.
\]
Then \(\Pr[\tau\geq n]=1/n\), so \(\mathbb E[\tau]=\infty\). Give every
invocation positive finite per-run costs \(q,s,p,c\) consistent with the
paper's per-run model and let only the last invocation enter the terminal
state. The cited statements do not impose iid retries or a uniform conditional
success lower bound, so they do not exclude this dependence/tail mutation.
Consequently the required additive expectations can be infinite even though
every realized run is finite and respects the per-run estimates.

**C2 result: NOT REJECTED.**

## C3 overlap mutation

For a realization with \(\tau=n\), keep every failed retry/recovery object's
classical table and associated live state until terminal entry. Enforce the
source's \(\widetilde L_{\max}=8L\) cap separately on every vector. At the
terminal time, \(n\) individually capped objects overlap. Since the source
does not impose a deterministic top-level cleanup/concurrency rule and
\(\tau\) has unbounded support, the global coherent, QRACM, backing, or tail
peak need not have a finite essential supremum. Per-vector Equation (3.5)
remains true throughout.

**C3 result: NOT REJECTED.**

## Error control

No cited passage maps complete-oracle channel error, discard/model error,
regularization and measurement failure, recovery error, verification error,
and residual-tail failure to one operational event \(F\). A transcriptwise
union or hybrid bound is therefore only a type template, not an instantiated
source bound.

## Result

**FAIL — `FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED`.**

The joint ledger was not completed. Remaining blockers are
`QM-STOPPING` (O1: no source law or finite joint additive expectations),
`QM-MEMORY` (O4: no complete deterministic liveness/cleanup schedule), and
`QM-ERROR` (O3: no common operational error mapping). O5 remains cleared only
for the archived-host text and conservative symbolic-cap scope.

This is a zero-compute literature/accounting control. It makes no numeric
security, NIST-level, parameter, breakthrough, curve-compute, or goal-
completion claim and does not reopen `IDEA-20260725-001/002/003`.
