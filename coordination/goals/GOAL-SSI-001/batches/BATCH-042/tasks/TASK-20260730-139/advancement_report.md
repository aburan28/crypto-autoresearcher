# BATCH-042 advancement report — QM-ERROR F-union obligation ledger

- **Task**: TASK-20260730-139 (executor)
- **Goal / batch**: GOAL-SSI-001 / BATCH-042
- **Idea**: IDEA-20260729-001 (CSIDH-COLLIMATION-FC0-R2)
- **Basis**: DEC-20260730-039 / EV-SSI-041
- **Git revision at execution**: e2015759fbcdad09e94950b4ad89930e6ede3708
- **Compute**: zero curve/isogeny/quantum-circuit; maximum_runs=1, runs_attempted=1

## Objective

Advance the remaining QUERY_MEMORY blocker QM-ERROR (status
`f_union_ledger_partial`) with a concrete zero-compute ledger/obligation step
that either tightens the F-union account from committed BATCH-025+ structure or
records an honest scoped pause/revisit — no invented host APIs, probabilities,
τ, or security bits, and no reopening of the paused QM-STOPPING lane.

## What was done

1. Audited the F-union lineage (BATCH-023 → BATCH-024 → BATCH-025 +
   recovery_spec) against committed citations.
2. Decomposed the gap from `f_union_ledger_partial` to a QM-ERROR error account
   into eight single-responsibility obligations (`f_union_obligation_ledger.yaml`).
3. Advanced exactly one obligation from committed structure — **OBL-2a**, the
   reverse inclusion `F_spec ⊆ U` at spec-internal scope, a definitional
   consequence of the recovery_spec exit typing that BATCH-025 never stated.
4. Classified the remaining obligations honestly (`not_supported`,
   `not_instantiated`, `checklist_only`, `wired_symbolic`) with concrete revisit
   conditions REV-E1/REV-E2/REV-E3.
5. Pre-registered falsifiable criteria (`falsifiable_criteria.yaml`) before the
   claim, including the anti-relabel criterion (OUTCOME-T requirement E).
6. Wrote an adversarial harness (`error_harness/`) that fails on illicit
   clearance, invented probabilities/numeric-bounds/security-bits/τ,
   relabel-only overclaim, host-level exhaustiveness smuggling, disposition
   drift, gate-B, API invention, MEMORY-MAP advance, and QM-STOPPING reopen.

## Outcome

`f_union_tightened` — a scoped, checkable tightening (OBL-2a) with all residual
obligations honestly blocked and revisit-tied. **Not** QM-ERROR / QM-STOPPING /
QUERY_MEMORY / QM-MEMORY-MAP clearance; **not** a probability, numeric bound,
security bit, τ, breakthrough, or completion.

## Harness

Entry point: `python3 -m error_harness.run_harness` (run from the task
directory). Receipt: `error_harness/harness_receipt.json`. All positive checks
pass and all injection/mutation tests reject the illicit mutations.

## Boundaries (scoped)

Analysis-only control/derivation result. No cryptanalytic improvement, no
asymptotic claim, no cryptographic-scale evidence. `dominated_by`: fully
dominated on the GOAL-SSI-001 attack frontier; `sota_delta`: 0.
FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED retained; QM-STOPPING FAIL lane paused
and untouched; BATCH-020 no_admissible_pin retained;
CollimationSieve@6f9188e4 untouched.

## Inference provenance

requested_policy `executor-implementation`; resolved model `Cursor Agent
(Claude Opus 4.8)` under authorized fallback (fallback_used=true,
model_verified=false), per CLAUDE.md model policy note and
inference-amendment-TASK-20260730-139.yaml.
