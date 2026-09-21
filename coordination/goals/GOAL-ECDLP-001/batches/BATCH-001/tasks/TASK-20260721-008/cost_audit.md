# TASK-20260721-008 — verification and cost-model frontier audit

```yaml
terminal_verdict: FRONTIER_ONLY
requested_policy: research-sol-max
resolved_model_id: gpt-5.6-sol-high
reasoning_effort: high
fallback_used: true
adapter_version: "unavailable: the Cursor runtime did not expose an adapter version to this agent session"
adapter_availability: "runtime available; version value unavailable"
authorization: DEC-20260721-002
```

This is a proposal/frontier analysis. It is not evidence, a validated
improvement, a lower bound, an ECDLP solve, or a breakthrough. No tool was
implemented and no experiment was executed.

## Decision impact

Two non-duplicate artifact types survive as frontier proposals:

1. A **target-swap state non-interference receipt** can falsify an amortization
   claim when target material leaks into supposedly target-independent
   preprocessing.
2. A **rank-and-failure conservation cost certificate** can falsify a speedup
   claim when failed/censored work, duplicate relations, dependent rows, or
   parallel worker effort is omitted.

Both change a concrete decision: whether a candidate may retain preprocessing
credit or proceed from a pilot to a scaling study. Neither reduces attack cost
by itself. The attack-cost route remains conditional on a later, approved,
independently reviewed experiment.

## Inspected boundary

The audit is bound to Git `7885e51da107b25d91ed79dcc7374f7548f72dd3`.
Git emitted a non-monotonic-index warning for the AppleDouble sidecar
`.git/objects/pack/._pack-bf28963975edac0a131e4a23003990d5911047dc.idx`;
the sidecar was neither repaired nor treated as research evidence.

Path inventory at screening covered all declared handoff inputs: `AGENTS.md`;
5 `docs/` files; 7 `harness/` files; 11 `tools/` files; 2 `templates/` files;
125 `ledger/` files; 942 `experiments/` paths; 44 `knowledge/` files; 919
`ideas/` files; and 116 `focus/` paths. Required contracts, the active harness,
nearest experiments and knowledge entries, P1553 R4, and the newest
deduplication/red-team reports were read directly. Repository-wide textual
screens covered every named tree and the terms relevant to techniques,
instruments, certificate rules, open problems, preprocessing, target reuse,
source replay, cost, memory, parallelism, invalid runs, censoring, and claim
tiers. Inventoried binary runtime-cache payloads were not interpreted as
research text.

The final pre-write dirty boundary was:

- modified: `ideas/README.md` and
  `ideas/rejected/preallocation/README.md`;
- untracked preallocation cohorts `20260721-a` (`I01`–`I12`, retired contract
  texts `I01/I04/I08`), `20260721-b` (`J01`–`J12`, contracts
  `J01/J02/J11`), `20260721-c` (`K01`–`K12`, contracts `K01/K02/K08`), and
  `20260721-d` (`L01`–`L12`, contracts `L01/L07/L11`);
- untracked reviews `DEDUP-20260721T111703-0700.md`,
  `DEDUP-20260721T140704-0700.md`,
  `DEDUP-20260721T171454-0700.md`,
  `REDTEAM-20260721T112622-0700.md`,
  `REDTEAM-20260721T142922-0700.md`, and
  `REDTEAM-20260721T172536-0700.md`.

Those `ideas/` paths were screened but preserved exactly. This task wrote only
the two declared artifacts in its assigned directory.

## Deduplication audit

The nearest existing capabilities are substantial:

- `harness/runner.py` independently verifies final discrete-log and
  decomposition witnesses.
- `tools/validate_ledger.py` checks manifest completeness, verified
  certificates, references, and claim-tier ceilings.
- `docs/evidence-and-reproducibility.md` requires matched baselines, invalid
  and censored-run reporting, and complete run artifacts.
- `KN-TECH-005` and `KN-LIT-013` give the generic and preprocessing bars,
  including the reported \(S T^2=\widetilde{\Omega}(N)\) tradeoff.
- `KN-TECH-006` requires the practical parallel rho control, including failed
  attempts and memory traffic.
- `EXP-ICI-001/analysis.md` manually preserves censoring, resource use,
  per-target costs, and a matched rho control.
- P1553 R4 and the recent idea cohorts already require unchanged
  target-independent state, fresh masked targets, source replay, verified rank,
  factor logs, blind descent, and full setup/query/output/ambiguity/memory
  charging.

Therefore the following were rejected as duplicates: another final-witness
certificate; another generic run manifest; another prose checklist for complete
cost; target replacement without a bound receipt; and a censoring table without
resource/rank conservation.

The exact added capabilities are narrower:

- frontier-A binds setup inputs, outputs, randomness, observed dependencies,
  and target-swap state hashes, producing a divergence witness on failure;
- frontier-B binds every attempt and resource counter to certificate validity
  and incremental relation rank, with explicit conservation identities.

Neither proposal duplicates an ECDLP mechanism in the idea corpus because
neither claims to construct a relation source or solve ECDLP. Their novelty is
only the proposed audit artifact and decision gate.

## Complete-cost model

For any candidate, keep setup, relation collection, factor-log linear algebra,
target descent, and verification separate:

\[
C(K)=W_{\mathrm{setup}}+W_{\mathrm{relations}}+
W_{\mathrm{LA}}+\sum_{j=1}^{K}
(W_{\mathrm{descent},j}+W_{\mathrm{verify},j}).
\]

The relation term includes every scheduled attempt:

\[
W_{\mathrm{relations}}=\sum_{i\in\mathrm{attempts}} W_i,\qquad
R_{\mathrm{gain}}=\operatorname{rank}(M_{\mathrm{final}})
-\operatorname{rank}(M_{\mathrm{initial}}).
\]

\[
W_{\mathrm{per\ rank}}=
\begin{cases}
(W_{\mathrm{setup}}+\sum_i W_i)/R_{\mathrm{gain}},
&R_{\mathrm{gain}}>0,\\
\infty,&R_{\mathrm{gain}}=0.
\end{cases}
\]

Invalid certificates, timeouts, resource exhaustion, duplicates, and dependent
rows receive zero rank credit but retain their consumed work. They are
operational cost, not negative mathematical evidence. Aggregate worker work and
elapsed wall time are separate metrics; parallel wall time cannot replace CPU,
group-operation, communication, or memory-traffic totals.

For a prespecified attempt model, let \(p_L\) be a conservative lower
confidence bound on verified incremental-rank yield. Acquiring \(r\) further
rank units requires at least

\[
\left\lceil r/p_L\right\rceil
\]

projected attempts, interpreted as infinity when \(p_L=0\). Adaptive or
correlated attempts require a model that justifies a different bound; silently
using an IID interval is a failure.

The multi-target break-even point against a comparator with cost
\(C_{\mathrm{base}}(K)\) is the smallest declared \(K\) for which the
candidate's conservative total-cost envelope is below the comparator. A
candidate must beat both:

- fully charged, parallel Pollard rho, not only an idealized serial loop; and
- BSGS with its time-memory cost, including table construction and storage.

Where the corpus uses \(B=N^{1/5}\), the existing screen remains controlling:

\[
\lambda=\max(a,\beta+\delta+q-r+o,\ell,
\delta_t+q+o+u,\beta),
\]

\[
\mu=\max(a_m,q_m,\beta+o,\ell_m,u),\quad 0\le r\le o,
\quad \beta=1/5.
\]

The proposed receipts do not improve these exponents. They test whether the
inputs assigned to \(a,a_m,q,q_m,r,o,u\) are honestly represented.

## Frontier-A: target-swap state non-interference

### Decision-changing test

Freeze setup on a public toy fixture, then replace the target at least twice.
Hash all declared setup inputs and outputs and bind the observed read/write
dependencies and randomness derivation. A target-derived dependency or changed
frozen-state hash is a falsifying witness.

On failure, move the affected construction and storage from setup \(S\) into
per-target cost \(T\), then recompute \(C(K)\). This can erase a claimed
multi-target advantage immediately. On a pass, the result establishes only
non-interference within the declared trace and deterministic fixture boundary.

### Cheapest validation and cost

Use three toy replays: one clean implementation, one planted target-cache leak,
and one planted target-seed leak. The receipt should pass the clean fixture and
identify the first divergent dependency for both leaks. Proposed overhead is
\(O(A)\) hashing for \(A\) artifact bytes and \(O(E)\) storage for \(E\)
observed dependency events. No runtime was measured.

### Failure modes

- Incomplete tracing can omit subprocess, mmap, environment, accelerator, or
  external-service dependencies.
- Equal hashes do not prove semantic non-interference.
- Unfrozen scheduling or randomness can create false divergence.
- A full trace may be source-sized, invalidating a memory claim.
- Clean setup does not excuse target-dependent work recomputed online.

### Quantitative gain

Within the bounded deterministic trace, every observed setup byte is compared
across two target swaps instead of the current zero machine-checkable
comparisons. If a pilot finds leakage, the remaining scaling runs premised on
reuse can be cancelled; symbolic saved runs are the unspent frozen budget.
There is no measured saving.

## Frontier-B: rank-and-failure conservation

### Decision-changing test

Require exactly one terminal receipt row for every scheduled attempt. Join each
accepted relation to an independent certificate, canonical row hash, and exact
rank-before/rank-after result. Duplicates, dependent rows, invalid certificates,
and censored attempts remain in the work sum and receive zero rank credit.

Proceed beyond a pilot only if the conservative projected cost to full rank,
factor logs, and fresh-target descent fits the frozen budget and remains below
both matched controls.

### Cheapest validation and cost

Use one toy stream containing one independent row, one duplicate, one dependent
row, one invalid certificate, one timeout, and overlapping two-worker
execution. The independently reconstructed final rank and resource totals must
match the receipt exactly. Receipt work is \(O(m)\) over \(m\) attempts plus
the selected exact incremental-rank algorithm; that audit overhead must itself
be reported. No run was performed.

### Failure modes

- OS counters may omit accelerator, scheduler, kernel, or shared-service work.
- Rank semantics can be wrong if the field or column schema is inconsistent.
- Censored completion time is unobserved and cannot be turned into a
  mathematical failure.
- IID confidence bounds are invalid for unmodelled adaptive dependence.
- Shared setup can be under- or double-counted without ownership rules.

### Quantitative gain

The receipt binds 100% of scheduled attempt IDs and assigns zero credit to all
non-rank-increasing rows. If, after \(m\) pilot attempts,
\(\lceil r/p_L\rceil\) exceeds `maximum_runs`, the methodology stops before
spending `maximum_runs - m` further attempts. This is a symbolic stopping
benefit, not an observed saving.

## Terminal assessment

`FRONTIER_ONLY` is required because both entries remain unimplemented,
unexecuted proposals. Their credible value is rigorous methodology: exposing
hidden target-dependent preprocessing and complete-cost denominator failures.
No attack-cost reduction, certificate improvement, empirical effect, or
cryptographic claim has been validated.

Exactly one next action: run the already-declared independent
`TASK-20260721-011` review against the verified snapshot. Do not authorize
implementation or experimentation unless that review selects and freezes one
bounded validation protocol.
