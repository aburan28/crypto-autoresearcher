# CTRL-B protocol design note — TASK-20260725-689

## Purpose
Freeze the Red Team–specified CTRL-B measurement so a later executor batch can
pin the genuine support-independent D6 deficit without repeating the BATCH-002
support-gap confound.

## Inference
- requested_policy: research-sol-max
- resolved_model_id: cursor-grok-4.5-high-fast
- fallback_used: true
- authorization_ref: AMEND-PATH-001-001

## Authorization
Review-only freeze. **No measurement** in BATCH-003. Execution only after
independent review PASS.

## Why CTRL-B
BATCH-002 showed null rank = sr_pred = 156520 (deficit 0) and sem rank = 138573.
Raw deficit 17947 vs sr_pred is confounded: null has 16016 extra degree-6 columns
(~89% of the headline). Column-deletion gives genuine deficit ≥ 1931. CTRL-B
ranks null on sem's exact support to pin the exact value in [1931, 17947].

## Confounders avoided
1. Treating sr_pred as support-matched when the implemented null is only
   degree-multiset-matched.
2. Using unchunked first-fall instruments that swap to root (infra, not evidence).
3. Promoting 17947 as a syzygy signal before support correction.

## Admission metrics
See `ctrl_b_protocol.yaml` `admission_metrics` and `quarantine.predicates` —
intended to be machine-checkable at review and at later execution receipt time.

## After PASS
`deficit_genuine` becomes the admissible D6 structural number. Raw 17947 stays
non-structural. Toy / single-cell limits remain; wrong-sign reading relative to
WIN (`d_reg(sem) ≥ d_reg(null)`) is unchanged unless new data contradict.
Pending measurement, the honest degree-axis observable remains the D5 series
(1322/1862/1823/1999).

## Supersedes
Failed_infrastructure card TASK-20260725-621 (non-mathematical).
