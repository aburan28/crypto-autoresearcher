# FC0-R2 joint stochastic resource-reconciliation worksheet

Task `TASK-20260730-005` · one zero-compute worksheet · convention
`CSIDH-COLLIMATION-FC0-R2`

## Question and pass rule

Can the pinned final Peikert binary-c-sieve row be represented by one
source-compatible stopping process \(\tau\) such that every additive resource
is charged under expectation, every peak resource is bounded on the same
global schedule, and every error term maps to one final operational event?

The control passes only if all of the following hold jointly:

1. the source meaning of the aggregate query quantity is identified as
   \(\mathbb E Q\), or an exact conversion to \(\mathbb E Q\) is supplied;
2. one stopping law covers recursive discards, fresh-sieve retries,
   punctured-regularization attempts, recovery runs, and tail entry;
3. query, repeated-sieve, postprocessing, classical-tail, and other classical
   costs are finite expectations under that same law;
4. QRACM, coherent workspace, other classical backing, and tail memory have a
   finite hard or essential-supremum peak under one liveness schedule; and
5. source errors map to one final failure event before composition.

No single realized trace, typical value, or separately selected retry
multiplier may stand in for these joint requirements.

## Source facts admitted

All page numbers refer to the archived PDF with SHA-256
`d4785e2863eebe97eb3a2909e02d669d138b2080c6e96e42c70d8d4fd2e89675`.

- PDF page 12, Equation (3.3), models per-sieve oracle queries as
  \(Q=(r/(1-\delta))^d\log L_0\), supposing that a random \(\delta\) fraction
  of recursive calls are discarded. The source calls this a model and reports
  empirical conformity; it does not define a joint stopping distribution.
- PDF page 15, Section 3.4.1, says a failed regularization measurement causes
  the vector to be discarded and the sieve to run again. Its success
  probability depends on the realized least-frequent multiplier.
- PDF pages 15–16, Sections 3.4.2 and 3.4.4, allow repeated punctured
  regularization attempts on leftover vectors and report expected recovered
  information empirically; these passages do not supply a recovery stopping
  law.
- PDF page 18, Figure 1, calls \(\widetilde Q_{\rm total}\) the total queries
  to recover all but the terminal residual, assumes expected information per
  run, and assumes an actual per-run query count within a factor of the
  Equation (3.3) estimate. It does not state that
  \(\widetilde Q_{\rm total}=\mathbb E[\sum_{k\le\tau}Q_k]\).
- PDF page 18 enforces \(\widetilde L_{\max}=8L\) and uses Equation (3.5) for
  reusable QRACM. This bounds that QRACM row, not all live memory.
- PDF page 20, Equation (4.1), gives an essentially/typically parameterized
  sieve T-gate estimate and a per-collimation \(D\)-cell QRACM lookup
  derivation. It does not jointly charge retries, postprocessing, tail work,
  and all memory.

## One joint FC0-R2 candidate

On one probability space, let \(\tau\) count every top-level sieve invocation
through terminal recovery, tail entry, or failure. For invocation \(k\), use
the BATCH-009 definitions \(Q_k,S_k,P_k,C_k\), terminal tail work \(H\), and
global live-memory processes \(W(t),R(t),B(t),M_{\rm tail}(t)\). The only
admissible joint row is

\[
\begin{aligned}
\bar Q&=\mathbb E\!\left[\sum_{k\le\tau}Q_k\right],&
\bar S&=\mathbb E\!\left[\sum_{k\le\tau}S_k\right],\\
\bar P&=\mathbb E\!\left[\sum_{k\le\tau}P_k\right],&
\bar C&=\mathbb E\!\left[\sum_{k\le\tau}C_k+H\right],
\end{aligned}
\]

with \(W_{\rm peak},R_{\rm peak},B_{\rm peak}\) evaluated as hard bounds or
essential suprema on the same global timeline, and with a separately typed
final failure probability.

## Joint reconciliation

| Resource | Source anchor | Required FC0-R2 statistic | Joint result |
| --- | --- | --- | --- |
| Complete labeled-state queries | Eq. (3.3); Figure 1 \(\widetilde Q_{\rm total}\) | \(\bar Q\) | **Unreconciled.** The source gives a model estimate, an empirical per-run factor, and a total-query label, but no statement equating the aggregate to this expectation under a defined recovery law. |
| Repeated sieve work | Eq. (4.1); recursive and regularization discards | \(\bar S\) | **Unreconciled.** Equation (4.1) accounts approximately for tree discards but is not a random sum over all fresh top-level retries and recovery runs. |
| Postprocessing | Sections 3.4.1–3.4.4 | \(\bar P\) | **Unreconciled.** Operations and empirical success/information statements are described, but failed attempts and fresh-sieve transitions are not jointly costed. |
| Classical work and terminal tail | Figure 1 residual brute force | \(\bar C\) | **Unreconciled.** Tail entry, stopping certificate, verification, and terminal work distribution are not instantiated in the same law. |
| QRACM | Eq. (3.5); \(8L\) hard cap | hard \(R_{\rm peak}\) | **Partially reconciled.** The reusable QRACM formula and per-vector hard cap are source-verified, but they do not bound concurrent instances or non-QRACM memory. |
| Coherent workspace | Eq. (3.5) discussion gives collimation ancilla order only | \(\operatorname{ess\,sup}W_{\rm peak}\) | **Unreconciled.** There is no end-to-end register liveness and reuse schedule including oracle, sieve, postprocessing, and retries. |
| Classical backing and tail memory | QRACM implementation remarks only | \(\operatorname{ess\,sup}B_{\rm peak}\) | **Unreconciled.** Widths, birth/death events, overlap, cleanup, and tail memory are absent. |
| Error | empirical/model assumptions and measurement success statements | \(\Pr[F]\) in one operational metric | **Unreconciled.** No cited map puts oracle, sieve, postprocessing, recovery, and tail contributions into one final event. |

## Finiteness and mutation controls

- **Heavy-tail mutation: FAIL to reject from the source.** FC0-R2 definitions
  are nonnegative, so Tonelli permits extended expectations, but the source
  does not establish finite \(\bar Q,\bar S,\bar P,\bar C\) under one law. A
  stopping process can therefore be changed so one expected random sum
  diverges while another remains finite without contradicting the extracted
  statements.
- **Overlap mutation: FAIL to reject from the source.** The \(8L\) cap remains
  true per charged vector even if an unbounded number of retries overlap.
  Without a deterministic concurrency and cleanup rule, finite global peak
  memory does not follow.
- **Trace mutation: PASS at the schema level only.** Different realized retry
  counts need not equal an expectation, and peak memory is not multiplied by
  retry count. This repeats the valid FC0-R2 type repair but supplies no
  missing source law.

## Result

**Joint stochastic reconciliation: FAIL / UNRESOLVED.**

The archived PDF clears the narrow O5 quotation-integrity defect and supports
the conservative \(D=8L\) symbolic cap. It does not provide the common
stopping law, source identification of the aggregate query statistic,
jointly finite additive ledger, global liveness schedule, non-QRACM peak, or
common operational error metric required to pass this worksheet. Therefore
`QUERY_MEMORY` remains unreconciled. The complete uniform-oracle channel is
still a visible later boundary, but it is not the present disposition.

This is a literature/accounting result only: no curve, isogeny, simulator, or
quantum-circuit computation; no numeric security, parameter, breakthrough,
ECDLP, or goal-completion claim.
