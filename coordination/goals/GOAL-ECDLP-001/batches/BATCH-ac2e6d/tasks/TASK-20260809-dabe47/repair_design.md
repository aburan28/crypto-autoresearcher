# Arm-A versioned repair design

This is a new successor to the rejected `EXP-ECDLP-51921d` contract. The
predecessor remains immutable and is not executed. The repair directly answers
the independent review findings `REV-f27fa2-01` through `REV-f27fa2-06`.

## Repair boundary

- New canonical records: `H-ECDLP-80fceb` and `EXP-ECDLP-a76937`.
- Superseded for execution: `H-ECDLP-1853dc` / `EXP-ECDLP-51921d`.
- No approval, freeze, implementation, run, evidence record, or official
  status promotion is created by this design task.
- The existing RQ remains active. The result ceiling is toy finite-size
  comparison only; no exponent or cryptographic-scale claim is licensed.

## Review finding closure map

| Finding | Repair artifact |
|---|---|
| Curve/automorphism admission not executable | `certificate_schema`, deterministic generation, and fail-closed rejection predicates in `EXP-ECDLP-a76937/specification.yaml` |
| Controls not mechanism-discriminating | Fixed six-variant paired matrix, same target/seed rule, auditable byte permutation, matched same-order random construction, and separate calibrations |
| Charged work and budget incomplete | `COST-ECDLP-a76937-v1`, integer weights, raw counter vector, memory/serialization/precompute charge, and 80-row matrix |
| Replication/held-out/stopping underspecified | Eight train and four held-out groups, exact seeds, paired sign-permutation test, slope/censoring rule, cycle windows, and invalidity branches |
| Prior review citation inaccurate | New decision `DEC-20260809-54f91c` states the prior BATCH-bd36fe review was unrelated and adopts the current NO-GO as the first canonical Arm-A review |
| Proof/Pareto fields dishonest | Frozen fixture pointers in `proof_audits.yaml` are required before approval; `dominated_by` is `null` with `no_result_claimed` status and no fabricated SOTA delta |

## Pre-compute proof audits

The repair package includes `protocol/proof_audits.yaml` as a required
producer artifact. It contains deterministic, machine-checkable fixtures for
the baseline transition/recovery equation and the observation-collision
quotient-vs-preimage distinction. Passing those fixtures is an admission gate,
not empirical support. The Coordinator must archive the fixture bytes before
any implementation or expensive run and must record a reason if an audit is
inapplicable.

## Execution handoff boundary

Even after a fresh independent review passes, a separate Coordinator decision
must freeze and authorize `EXP-ECDLP-a76937`, and a separate Executor task must
create `rho_census.py` and the complete run package. The current adapter
preflight has no usable API backend; that remains infrastructure-only. A native
Codex exception may be used only with exact-session provenance and no Bedrock.
