# Red-team falsification review — GOAL-FIND-001 BATCH-001

Task `TASK-20260725-683` · Snapshot `0168f5d15b43f6fcc93524ba665430611c331601`  
Verdict: **REVISE**

Inference: requested_policy=`review-xhigh`; resolved_model_id=`cursor-grok-4.5-high-fast`; fallback_used=`true`; authorization_ref=`AMEND-PATH-001-001`.

## What survives

- Coverage of assessment §1.1 is exact: all eleven replicated EVs
  (`EV-BKK-001` … `EV-SIG-005`) appear once with `disposition: promote`.
  `not_warranted: 0` is correct under `knowledge/README.md` (replicated ⇒
  `KN-FIND` or explicit `not_warranted`).
- No promote row should flip to `not_warranted`. Scoped negatives
  (`reject_scoped`) are valid findings.
- Toy / no-crypto-upgrade claim boundary is stated and not breached.
- `EV-SIG-002` + `EV-SIG-004` dual promote with lower-bound / canonical-count
  cross-link correctly avoids contradictory exact D4 series.
- Path hashes match the archive receipt; commit is reachable from `HEAD`.

## What fails as stated

1. **KN-FIND-019 overclaim (N1).** “Persistent box saturation” at m=6 drops
   the DEC-20260722-003 finite-p hull caveat (interior monomial loss on 2/30
   sections; MV unchanged). Narrow to hull/MV language.

2. **Missing load-bearing bounds (N2).** EQJ draft omits `p≤2^12`; FB draft
   omits subgroup-base exclusion; SIG-005 draft omits an explicit toy /
   boolean-Semaev prefix in the scoped claim sentence.

3. **KN-FIND-027 overgeneralization (N3).** Demonstrated fact is D=6 null C5
   failure at n=9. “D≥6 null baseline invalid” overreaches; keep
   “cascade admissible only through D≤5” with that narrower cause.

4. **Theorem underclaim (N4, non-blocking for promote).** DEC-20260722-003 /
   `THM_BKKMV1` already prove the m≤5 sectioned barrier; drafts stay
   `empirical_only` with no cross-ref. Fix before knowledge write so ground
   truth is not weaker than the ledger decision.

5. **Thin Key claims (N5).** Template “DEC closed the EV” bodies are fine for
   a draft package only after scoped claims are tightened; not final
   `knowledge/findings/` prose.

## Fatal objections

None. No missing §1.1 EV. No draft asserts crypto-scale advantage or
impossibility. Snapshot content is reviewable via queue-bound commit hashes
despite receipt `pending_post_commit` metadata (N6).

## Required revision before archive

- Rewrite KN-FIND-019 / KN-FIND-027 scoped claims (N1, N3).
- Fold EQJ/FB/SIG-005 bounds into scoped claims (N2).
- Add THM_BKKMV1 / DEC-20260722-003 note on BKK–BKKMV rows without claiming
  the open all-m lemma (N4).
- Re-snapshot revised producer hashes, then run ledger archive
  `TASK-20260725-684` (or a scoped repair task).

## Narrowest supported statement

Promote all eleven §1.1 replicated EVs as toy-scoped KN-FIND entries after the
wording fixes above; do not treat the current draft text as final internal
ground truth.
