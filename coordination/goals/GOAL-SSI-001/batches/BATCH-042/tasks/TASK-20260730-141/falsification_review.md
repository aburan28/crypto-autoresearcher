# Falsification review — BATCH-042 QM-ERROR F-union tightening (RT-20260730-141)

Independent red-team review of producer TASK-20260730-139, snapshot archive
TASK-20260730-140 (commit `f968b9baa1f08e17de4f79d3d3714e942cf8cff7`, bind
`c7474711fd7becb127bbd82ba831f52d945c9857`). Independent session; no producer or
official artifact was edited. Requested `review-xhigh`; resolved model
`Cursor Agent (Claude Opus 4.8)` under authorized fallback
(`model_verified:false`), per CLAUDE.md model policy note.

## Verdict: CONFIRM_SCOPED

The batch is an honest, bounded, zero-compute QM-ERROR advancement with outcome
`f_union_tightened`. Exactly one obligation (OBL-2a) is advanced from committed
structure, and it is genuinely new checkable content — not a relabel — with all
residual obligations honestly blocked and revisit-tied. No clearance, invented
numeric, τ, host-level exhaustiveness, or QM-STOPPING reopen survives review.

## What I tried to falsify, and what happened

1. **"The tightening is a relabel of BATCH-025."** Checked the source: BATCH-025
   `f_union_ledger.yaml` records only the forward inclusion `U ⊆ F`
   (`inclusion_into_common_F: U ⊆ F`); the reverse inclusion is absent. The
   recovery_spec exit-typing sentence OBL-2a relies on exists verbatim
   (`recovery_spec.md` line 19–20). So OBL-2a adds content that was not present
   before. The harness `check_not_relabel_only` and injection
   `test_relabel_only_rejected` independently guard this. **Not a relabel.**

2. **"Spec-internal exhaustiveness is being smuggled as host-level."** OBL-2b
   (host-level exhaustiveness) is `not_supported` (BATCH-020 no_admissible_pin);
   OBL-2a's scope is `recovery_spec_internal_typed_exit_set_only` and explicitly
   excludes the host. `check_no_host_level_exhaustiveness_claim` and
   `test_host_level_exhaustiveness_smuggled_rejected` reject the smuggle.
   **No host-level claim.**

3. **"A probability / error bound / security bit / τ was invented."** OBL-3/OBL-4
   are `not_instantiated`; no `Pr[F_*]`, epsilon, security bit, or τ appears.
   `check_no_invented_numerics`, `check_no_illicit_clearance`, and injections
   (`test_invented_probability_rejected`, `test_probability_assigned_rejected`,
   `test_fake_tau_rejected`) all hold. **Nothing invented.**

4. **"QM-STOPPING was reopened, or QM-ERROR/QUERY_MEMORY cleared."** QM-STOPPING
   remains `FAIL`, lane `paused_pending_revisit`, `reopened_this_batch:false`;
   disposition `FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED` retained; all `cleared`
   flags false. Injections `test_qm_stopping_reopen_rejected`,
   `test_qm_error_cleared_rejected`, `test_disposition_drift_rejected` reject the
   mutations. **No clearance, no reopen.**

5. **"The snapshot is not faithfully archived."** Snapshot commit parent is
   `e2015759f` (matches producer `git_revision_at_execution`); exactly 12 files
   changed; all 12 `path_sha256` recomputed from `git show` equal the
   dispatch-queue archive block; snapshot is an ancestor of HEAD; harness
   re-runs 25/25 with a byte-identical receipt
   (`72308c657745b6fd584c0476a4cce49f315146efd5792abfa52fa344e693656c`); producer
   tree clean afterwards. **Faithful.**

## Non-blocking objections

- **OBJ-1** — the tightening is spec-internal/definitional; `sota_delta=0`,
  fully dominated on the attack frontier. Real but modest; producer states it.
- **OBJ-2** — REV-E1/E2/E3 are all currently unavailable, and REV-E1 shares the
  QM-STOPPING REV-1 host gap; the remaining QM-ERROR obligations are
  host/source/probability-gated, so the Coordinator should not expect a further
  zero-compute QM-ERROR tightening to move an obligation. Feeds next action.
- **OBJ-3** — the harness positively locks the outcome; it is a claim-guard for
  this batch, not a general three-outcome verifier.
- **OBJ-4** — `model_verified:false` under authorized fallback.

## Recommended next concrete action

Ledger-archive as `f_union_tightened` with all controls retained. Because the
remaining QM-ERROR obligations are pin/source/probability-gated (OBJ-2), the
honest next lever is a **pin-seeking / host-admissibility probe that does not
invent CollimationSieve APIs** (the shared REV-E1/REV-1 pin gate), or an explicit
scoped pause of the QM-ERROR lane with REV-E1/E2/E3 as re-entry gates. Do not
reopen QM-STOPPING (REV-1/REV-2 unmet), iterate the toy width lane, invent τ /
gate B, advance MEMORY-MAP, clear QUERY_MEMORY, or launch EXP-SSI-001.
