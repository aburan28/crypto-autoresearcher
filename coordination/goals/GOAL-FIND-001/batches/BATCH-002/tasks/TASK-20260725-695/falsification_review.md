# Red-team falsification review — GOAL-FIND-001 BATCH-002 repair

Task `TASK-20260725-695` · Snapshot `80238727042d450118062a0ec439aa8a65299594`  
Prior REVISE: `RT-20260725-683` · Decision context: `DEC-20260725-021`  
Verdict: **PASS**

Inference: requested_policy=`review-xhigh`; resolved_model_id=`cursor-grok-4.5-high-fast`; fallback_used=`true`; authorization_ref=`AMEND-PATH-001-001`; independent_session=`true`.

## Snapshot integrity

- Commit `80238727042d` is reachable from review `HEAD`; parent `020168fe52d3`.
- Path SHA-256 values match `TASK-20260725-694` receipt and `git show 80238727042d:<path>` for
  `promotion_map.yaml`, `draft_findings.md`, and `repair_note.md`.
- Receipt still has `pending_post_commit` / null SHAs (deferred N6 hygiene); not a mathematical defect.

## N1–N4 discharge

| ID | Target | Status | Check |
| --- | --- | --- | --- |
| N1 | KN-FIND-019 | **closed** | Hull/MV wording + 2/30 interior losses + char-0/generic-t + C1 open matches `ledger/DEC-20260722-003` / `EV-BKKMV-002`. |
| N2 | KN-FIND-020/005/011 | **closed** | `p≤2^12`, subgroup-base exclusion, and toy boolean-Semaev `n≤24` appear in scoped_claim sentences. |
| N3 | KN-FIND-027 | **closed** | Null invalidity narrowed to D=6 @ n=9 (C5 fail); cascade only for D≤5. |
| N4 | KN-FIND-017/002/003 | **closed** | `empirical_only` retained; `proof_refs` + theorem cross-note cite `THM_BKKMV1` / `DEC-20260722-003` for m≤5 proved barrier; C1 open. |

## What was tried and did not break the repair

1. **Reintroduce literal m=6 box saturation.** Draft now forbids it in Not claimed / Limits; scoped claim is hull-level.
2. **Broaden SIG null failure to all D≥6.** Wording and Not claimed block prevent that reading.
3. **Treat theorem cross-note as upgrading EV rows to proved claims.** `proof_status` stays `empirical_only`; Provenance separates EV claim from later upgrade.
4. **Coverage drop or extra promote row.** Still exactly the eleven §1.1 EVs; `promote=11`, `not_warranted=0`.
5. **Crypto-scale / impossibility language.** Absent from scoped claims.

## Fatal / blocking objections

None.

## Deferred (non-blocking)

- **N5** — thin Key claims: expand at `/curate-knowledge`, per DEC-20260725-021.
- **N6** — receipt metadata: Coordinator archive hygiene.
- **H1 (advisory)** — `DEC-20260722-003` ID collides with an ML-KEM decisions-path record; BKKMV content is at `ledger/DEC-20260722-003.yaml` and remapped as `DEC-20260724-009`. Repair citation matches N4’s required ID/content; dual-cite remap at knowledge write is optional hygiene.

## Narrowest supported statement

Repaired drafts are ready for Coordinator ledger archive and a subsequent promotion decision. This red-team does **not** authorize `knowledge/findings/` writes.

## Next concrete action

Archive this report (`TASK-20260725-696`), then Coordinator decides knowledge promotion of the eleven drafts, expanding N5 Key claims at write time.
