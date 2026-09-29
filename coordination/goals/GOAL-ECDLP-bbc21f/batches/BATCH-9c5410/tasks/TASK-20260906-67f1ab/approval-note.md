# Approval authorship note -- TASK-20260906-67f1ab (BATCH-9c5410, GOAL-ECDLP-bbc21f)

## Branch taken

BRANCH A (APPROVE) for BOTH contracts: `EXP-ECDLP-612fb1` (H-ECDLP-37dc01)
and `EXP-ECDLP-869870` (H-ECDLP-3550b8). No contract was declined.

## Authorship and model

Authored inline by the Coordinator role under the declared fallback of this
task's handoff (`inference.fallback_allowed: true`, `degraded_allowed:
false`), disclosed here for the ledger receipt of TASK-20260906-2d30dd.

- requested policy: `coordinator-orchestration-code`
- runtime: Claude Code subagent `coordinator` (effort `high`, per
  `orchestration/model-policies.yaml` via `orchestration/roles.yaml`)
- resolved model that actually answered: `claude-fable-5-1` (Claude Fable
  5.1), as self-reported by the runtime; `model_verified: false` (not probed
  by `orchestration/adapter`). The `anthropic` binding for this policy in
  `orchestration/model-bindings.yaml` names `claude-opus-5`, so this is a
  recorded FALLBACK (a different model serving the same capability contract:
  tool use and reasoning effort `high` were available), not a degradation.
  Nothing was downgraded and no requirement was relaxed.
- session: https://claude.ai/code/session_018SX2HAYZWdBm75LE8QVtGz
- no shell was available to this task: no `sha256`, `git diff` or
  `tools/validate_ledger.py` run was performed here. The orchestrating
  session validates the YAML and diffs both specifications against their
  committed bytes to confirm the five-field scope; TASK-20260906-2d30dd
  re-verifies before committing and records the sha256 bindings in
  DEC-20260906-2b1387.

## The recorded user answer (source of this approval)

Obtained by the orchestrating session on 2026-09-06 through the interactive
question tool, after the campaign-opening commit `28a63c4d5` was pushed.

Question presented, verbatim:

> Approve the two frozen contracts under RQ-ECDLP-78dbc5 (GOAL-ECDLP-bbc21f)?
> (1) EXP-ECDLP-612fb1, the batch-reselected fixed-size table
> (H-ECDLP-37dc01): toy scale, a generic keyed-random-function instrument at
> N in {2^20, 2^24, 2^30} plus a certified toy prime-order curve arm at
> N ~ 2^24 (every solve re-verified by an independent scalar multiplication
> and against the seeded logarithm). Decidable success criterion at a = 1/4,
> r = 2, k = 4, at both generic N: the T/2 re-selected table's steady-state
> per-target success at U = 8T is within CI of the static T-entry table (CI
> upper bound of the difference >= 0, point estimate >= -0.03); NULL-A
> (relabelled batch evidence) at zero and NULL-B / phi = 0 bit-identical to
> static; phi decay monotone with gain(0) = 0; no re-selected table's hit
> rate exceeds the exact oracle top-T share. Falsification: the T/2 table
> still CI-separated below static T at U = 16T. Budget 12 CPU-h, 48 runs,
> 3600 s/run, 8 GB, one worker. (2) EXP-ECDLP-869870, the basin-partition
> coverage instrument (H-ECDLP-3550b8), Stages 1-3: exact basins at N in
> {2^20, 2^22, 2^24}, sampled coverage at 2^30, plus a certified toy-curve
> transfer arm; gated on reproducing Bernstein-Lange's 1.79 case study and
> Table 4.1 within 0.10; measures the Borel basin law, the unselected law,
> the exact oracle top-T share against C_max(a), the published weight
> against the oracle as a function of N/T, a relabelling null, a sigma-noise
> decay and N-independence. Budget 16 CPU-h, 40 runs, 3600 s/run, 8 GB, one
> worker. Both are constant-factor, generic-model measurements under the
> KN-LIT-013 S T^2 = Omega~(eps N) ceiling; neither can move an exponent and
> both say so. Approval authorizes execution: a committed Coordinator
> decision marks it approved and writes the executor handoffs.

Options offered:

1. "Approve both as frozen (Recommended)"
2. "Approve EXP-ECDLP-612fb1 only"
3. "Approve EXP-ECDLP-869870 only"
4. "Do not approve; revise"

ANSWER, VERBATIM: **"Approve both as frozen (Recommended)"**

Meaning applied: branch A for EXP-ECDLP-612fb1 AND branch A for
EXP-ECDLP-869870.

## Diff scope of this task (and ONLY this scope)

1. `experiments/EXP-ECDLP-612fb1/specification.yaml` -- FIVE designated gate
   fields, nothing else:
   - `status: review_required` -> `status: approved`
   - `approved_by: null` -> `approved_by: coordinator`
   - `frozen: false` -> `frozen: true`
   - `execution_authorized: false` -> `execution_authorized: true`
   - `approval_note` -> approval record (date 2026-09-06, the option set and
     the verbatim answer, DEC-20260906-2b1387 as the decision that
     TASK-20260906-2d30dd commits, the five-field scope, the executor
     handoff TASK-20260906-3623b9, the reserved review chain, the
     amendment-only rule) with the pre-approval text "DESIGNED, NOT
     APPROVED. ..." preserved VERBATIM inside it.
   `version` stays 1. Every protocol field byte-identical.
2. `experiments/EXP-ECDLP-869870/specification.yaml` -- the same five fields
   under the same rules (executor handoff named: TASK-20260906-d17254;
   hypothesis named: H-ECDLP-3550b8). `version` stays 1. Every protocol
   field byte-identical.
3. `ledger/handoffs/TASK-20260906-3623b9.yaml` -- executor handoff for
   EXP-ECDLP-612fb1: policy `executor-implementation`, `review_required:
   true`, budget copied verbatim from the contract (per-run 3600 s, 12
   CPU-h, 8 GB, 48 runs, 1 worker), implementation path declared as
   `experiments/EXP-ECDLP-612fb1/source/`, `archived_by:
   TASK-20260906-7a2446` (reserved snapshot archive), Validator
   TASK-20260906-7ec3ea and Red Team TASK-20260906-90e7cf reserved,
   first-batch scope Stage G + Stages 1-2 with Stage 3 only if budget
   allows (else "not yet run"), `batch_id: null` with a note (execution
   batch not yet opened).
4. `ledger/handoffs/TASK-20260906-d17254.yaml` -- executor handoff for
   EXP-ECDLP-869870: same shape; budget verbatim (per-run 3600 s, 16 CPU-h,
   8 GB, 40 runs, 1 worker); implementation path
   `experiments/EXP-ECDLP-869870/source/`; first-batch scope Stages 1-2
   with the blocking fixture gate at 2^24, Stages 3-4 only if budget allows
   (else "not yet run").
5. This note.

Why FIVE fields and not the precedent's three: `frozen` and
`execution_authorized` are gate fields of THESE contracts' own schema, and
invalidation rule 1 of each contract reads `execution_authorized` ("Execution
while status is not approved or execution_authorized is false: no run under
this contract is evidence"). Leaving either false would make every run
non-evidence by the contract's own rule. The precedent EXP-ECRANK-76a70d did
not carry those two fields, which is why BATCH-832f3d named three.

## Decision-record placement

`ledger/decisions/DEC-20260906-2b1387.yaml` is NOT an output of this task. It
is authored by the ledger archive TASK-20260906-2d30dd (decision
`approve_experiment` with the verbatim `user_confirmation_record` above, the
`approved_contract_binding` of each contract to version 1 at the sha256 of
its committed bytes, the `executor_handoff_note` for both handoffs,
`knowledge_promotion: not_warranted`, and no hypothesis status change),
exactly as TASK-20260905-59fb55 wrote DEC-20260905-2d466e in BATCH-832f3d, so
that no artifact path has two owners.

## What this task did not do

- No hypothesis status changed: H-ECDLP-37dc01 and H-ECDLP-3550b8 stay
  `specified`. Nothing promoted to `knowledge/`.
- No other file written; no identifier minted or searched for (every id used
  was pre-minted and relayed by the orchestrating session); no commit; zero
  compute spent on either experiment (`maximum_runs: 0`).
- No run, no execution: approval authorizes execution by the batch opened
  AFTER DEC-20260906-2b1387 merges to `main`; a message or in-session word is
  never an approval.
