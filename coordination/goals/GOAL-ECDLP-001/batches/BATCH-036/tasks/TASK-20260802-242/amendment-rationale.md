# Amendment Rationale

Record: `PA-IT-001-v3-rc36-repair-2`  
Task: `TASK-20260802-242`  
Scope: frozen experiment design only; no implementation and no run.

## Decision

The amendment keeps the exact v3 MOV charge
`ceil(0.886*sqrt(p^k))`. It forbids the BATCH-030 replacement
`ceil(k*log2(p))`, which counted pairing evaluation while omitting the field
DLP. Every future MOV row must additionally expose the end-to-end BSGS sanity
term `2*ceil(sqrt(N*))`, including at `k=1`, without creating a second charged
formula from which an Executor could choose.

The anomalous calibration uses a deterministically selected curve with exact
`#E(F_p)=p`, hence trace 1. An embedding-degree-1 label cannot satisfy this
control. The anomalous solver and wrapper must recover a planted scalar on that
actual curve.

## Why Two Positive Controls Are Required

An `F_p`-rational isogeny preserves Frobenius trace. Consequently, a trace-1
anomalous curve cannot be walked by rational isogenies to a curve on which the
trace-1 detector is false. The prior request cannot honestly be implemented as
one anomalous-to-non-special walk.

The amendment therefore freezes two non-substitutable controls:

1. `CTRL-ANOMALOUS-TRACE1-POS` validates the actual anomalous detector, solver,
   and anomalous cost calibration.
2. `CTRL-ISOGENY-PULLBACK-NONSPECIAL-POS` validates scalar transport on a
   detector-negative instance. It evaluates explicit degree-2 `phi` and
   `dual_phi` maps and checks the pullback identities, instead of accepting a
   same-curve direct solve as a transfer certificate.

The second control is deliberately labeled a transfer-mechanics control, not a
special-family shortcut. Its BSGS work cannot support a sub-rho claim.

## Six Repairs

1. **Cost and anomalous control:** one binding MOV formula is retained; the
   field-DLP term is audited; the anomalous control requires exact trace 1.
2. **Genuine transfer:** the fixed-field fixture is selected deterministically,
   starts and ends detector-negative, changes `j`, evaluates `phi` and
   `dual_phi`, and verifies scalar identities before passing.
3. **Live null and ledger:** a certificate-bearing synthetic `R_xfer<0.7` claim
   must be rejected because the same speedup appears on the structure-destroyed
   null. The 4x plant uses nonempty search and chosen-path edge ledgers that
   independently reconstruct `C_path`.
4. **Pareto honesty:** every design and future result carries non-null
   `dominated_by` plus numerical time, memory, and data/query deltas. Design
   artifacts use `not_applicable` only because they are explicitly non-solver
   records with zero achieved deltas.
5. **Density:** the exact 20-22 bit window selects three primes per bit length
   that each possess a persisted actual trace-1 witness. It samples exactly
   2,048 retained classes per selected prime, reports exact Clopper-Pearson 95%
   intervals, and applies Bonferroni simultaneous 95% coverage over the nine
   primary estimands.
6. **Reproducibility:** four future source files are the complete repository
   implementation surface. A pre-run snapshot must archive them, the amended
   contract, controls, a hash manifest, and exact command before execution.

## Interpretation

Control failure, timeout, density shortfall, fixture miss, or snapshot mismatch
invalidates the measurement package; none is evidence against `H-IT-001`.
Successful controls make a future toy run admissible for review but do not
support the hypothesis, establish generic safety, improve an exponent, or close
the goal.

## Pareto

`dominated_by: not_applicable`

Non-solver scope: this document explains a pre-run contract and reports no
algorithmic frontier point.

`sota_delta.time = {exponent_delta: 0.0, achieved_group_ops_delta: 0}`  
`sota_delta.memory = {exponent_delta: 0.0, achieved_bytes_delta: 0}`  
`sota_delta.data_or_query = {exponent_delta: 0.0, achieved_query_delta: 0}`
