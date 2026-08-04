# Snapshot input audit — TASK-20260804-1bdcf5

## Scope and binding

This is a design audit of the committed approval-facing draft only. It neither
approves nor freezes `EXP-SMTH-92d322`, authorizes execution, creates data, or
makes an ECDLP or mathematical claim.

The exact committed draft examined is:

| Item | Value |
|---|---|
| Path | `experiments/EXP-SMTH-92d322/specification.yaml` |
| Content SHA-256 | `bdb6e96f9b7b8f1548912dfc163bf9b76a16c1c707a068d15019d02293c4d634` |
| Commit containing that path version | `cbb93954f6c049e9a1906267c9a242b8da0a8232` |

The audit also reads the companion draft report at
`coordination/goals/GOAL-ECDLP-001/batches/BATCH-fe8b5c/tasks/TASK-20260804-eecf1c/draft_report.md`,
`H-SMTH-001`, `DEC-20260801-011`, and the non-execution refusal report
`TASK-20260803-e50765`. The refusal established an authorization and binding
defect only; it produced no run, data, or evidence about `H-SMTH-001`.

## Approval-requirement audit

| Requirement in `EXP-SMTH-92d322` | Audit status | Required independent-review disposition |
|---|---|---|
| Deterministic curve and factor-base procedure | Unspecified. The draft says “one deterministic ordinary prime-field curve” and a deterministic 512-coordinate base but does not specify a seed-to-prime, curve, point, ordering, eligibility, or rejection procedure that reproduces the exact objects. | Resolve with a complete deterministic algorithm or reject the draft as amendment-required; do not infer missing rules. |
| Exact `INT-1` / `ENC-B` / root exceptional cases | Unspecified. The draft does not fix field-to-integer representatives, root-multiset computation/ordering, multiplicity treatment, non-split/repeated-root behavior, or arithmetic/encoding exceptional cases. | Resolve exact arithmetic and every exceptional case or reject as amendment-required. |
| Complete-factorization solver and output verification | Unspecified. “Complete factorization” is required, but solver/version/configuration, timeout/resume behavior, proof or product-verification format, and treatment/null raw schema are absent. | Resolve the solver and independently checkable raw/verification schema, or reject as amendment-required. |
| Numerical RSS probe tolerance and margins | Unspecified. The predecessor required preflight probes near 5%, 10%, and 20% completion; this draft repeats the memory ceiling but supplies no numerical tolerances, margins, measurement method, or failure rule. | Set numerical probe tolerances and margins or reject as amendment-required. |
| Domain-separation comparability | Unresolved. The successor deliberately uses `EXP-SMTH-92d322/v1`, while retaining the predecessor’s numerical master seed. The draft does not define what reproducibility comparison, if any, remains valid across the distinct domains. | Reconcile the comparison scope or explicitly reject predecessor-comparability claims; do not assume stream equivalence. |

## Audit conclusion

All five listed requirements remain open design gaps. The only admissible next
step in this package is an independent design review of the hash-bound draft.
That review may recommend a successor revision; it may not approve, freeze,
authorize execution, create data, or make an ECDLP claim.
