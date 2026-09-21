# FC0-R2 revision note — GOAL-SSI-001 BATCH-009

Task `TASK-20260730-037` · access date 2026-07-30  
Version: **CSIDH-COLLIMATION-FC0-R2**  
Supersedes for this control gate: `CSIDH-COLLIMATION-FC0-R1`

## Revision boundary

FC0-R2 is a source-reconciliation and resource-typing control for the pinned
final Peikert binary collimation-sieve row. It remains on the
`KN-TECH-051` posture `peikert_unconstrained_collimation_explicit_qracm`: the
row reports QRACM and imposes no exogenous resource-constrained/SQALE memory
budget. This posture name is a local accounting convention, not an attribution
that every concrete Peikert resource has been independently instantiated.

FC0-R2 adds two durable controls:

1. `stochastic_invocation_ledger.md` defines one stopping process and declares
   expectation semantics for all additive work, worst-case semantics for peak
   memory, and operational semantics for errors.
2. `primary_source_excerpts.md` archives direct primary-source text for
   Equation (4.1), Equation (3.5), and the enforced
   \(\widetilde L_{\max}=8L\) maximum.

No source constant is inferred from a numerical security label, and no
resource-constrained row is mixed into the pinned convention.

## Stochastic repair

Let \(\tau\) count every top-level sieve invocation, including fresh-sieve
discards and retries. FC0-R2 replaces the R1 trace equality with

\[
\bar Q=\mathbb E\!\left[\sum_{k\leq\tau}Q_k\right],\quad
\bar S=\mathbb E\!\left[\sum_{k\leq\tau}S_k\right],\quad
\bar P=\mathbb E\!\left[\sum_{k\leq\tau}P_k\right],\quad
\bar C=\mathbb E\!\left[\sum_{k\leq\tau}C_k+H\right].
\tag{R2-ADD}
\]

The geometric-retry mutation passes at the type level: traces with different
retry counts retain different realized totals, while every additive expected
cost scales under the same law. Peak coherent width, QRACM, and classical
memory are maxima on a global timeline, not expected additive sums.

The complete stochastic control does **not** pass source reconciliation. The
primary text describes expected information per run and a total query
estimate, but it does not explicitly identify
\(\widetilde Q_{\rm total}=\bar Q\), provide the stopping law of \(\tau\), or
instantiate the joint repeated-sieve, postprocessing, tail, and memory ledger.
FC0-R2 therefore does not manufacture those values from a single trace.

## Primary-source repair

The direct PDF excerpts verify:

- Equation (4.1):
  \(36\widetilde L(2/(1-\delta))^d\), where \(\widetilde L\) is an upper
  bound on typical phase-vector length, \(\delta\) is discard probability, and
  \(d\) is sieve-tree depth;
- the per-collimation derivation for input/output vectors bounded by \(D\);
- Equation (3.5)'s reusable-QRACM dependence on \(L_{\max}\); and
- Figure 1's imposed hard maximum
  \(\widetilde L_{\max}=8L\), enforced by partial measurement whenever a
  generated vector is longer.

Thus the same-row assignment \(D=\widetilde L_{\max}=8L\) is a verified
conservative symbolic cap for the charged collimations. It is an FC0
derivation, not a claim that the source equates its typical value with \(8L\).
The factor-eight sensitivity remains visible.

## O1–O5 status

- **O1 — partial, not source-complete.** The expectation-versus-trace category
  error is repaired and the geometric mutation passes. The paper does not pin
  the full stopping distribution or joint invocation ledger, so aggregate
  source reconciliation remains unresolved.
- **O2 — adequate type repair (standing).** The canonical residual search is
  classical; quantum-tail query, T-count, depth, and coherent width are zero.
  Classical tail work, memory, stopping, verification, and failure values
  remain unresolved.
- **O3 — partial, not adequate.** Random-stopping error composition is now
  transcriptwise and operationally typed. Sieve, postprocessing, and tail
  errors still lack cited mappings into the same final metric as complete
  channel diamond distance, and the uniform complete oracle is absent.
- **O4 — partial, not adequate.** FC0-R2 specifies a global timeline and
  worst-case peak semantics, including retry overlap. It still lacks
  instantiated register widths, birth/death times, and a non-overlap or reuse
  proof.
- **O5 — adequate primary anchor for the symbolic cap rule.** Primary excerpts
  now verify Equation (4.1), its symbols, the common vector-length bound, and
  the enforced \(8L\) maximum. No per-invocation numerical value is inferred.

## Classification

The type-level O1 mutation is necessary but not sufficient to clear the first
gate. The source-compatible expectation, stopping law, repeated-work ledger,
non-QRACM memory peak, and common error metric are not instantiated.

**Disposition: `FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED`.**

The separately unresolved complete uniform-oracle channel remains visible as a
second-stage boundary; it is not promoted to the disposition while the first
gate remains incomplete.

## Scope controls

- Zero curve, isogeny, simulator, and quantum-circuit computation.
- `IDEA-20260725-001`, `IDEA-20260725-002`, and `IDEA-20260725-003` are not
  reopened.
- No numerical security, NIST-level, parameter, breakthrough, ECDLP, or
  goal-completion claim is made.
- No attack resource point exists, so Pareto dominance and SOTA delta remain
  not evaluable rather than being set to an unchecked null.
