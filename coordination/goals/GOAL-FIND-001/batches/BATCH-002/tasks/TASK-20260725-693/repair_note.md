# Repair note — TASK-20260725-693

Discharges RT-20260725-683 N1–N4 against TASK-20260725-681 drafts.
Decision context: DEC-20260725-021 / EV-FIND-002.
Prior producer and red-team artifacts were not edited.
No `knowledge/findings/` writes.

Inference: requested_policy=`research-sol-max`; resolved_model_id=`cursor-grok-4.5-high-fast`; fallback_used=`true`; authorization_ref=`AMEND-PATH-001-001`.

Coverage preserved: promote=11, not_warranted=0 (all assessment §1.1 EVs).

---

## N1 — KN-FIND-019 overstates finite-p box saturation

**Objection:** “persistent box saturation” omitted DEC-20260722-003 / EV-BKKMV-002 hull-vs-literal caveat (2/30 sections lost 30–60 hull-interior monomials; corners intact; MV unchanged).

**Citation bounds used:**
- `ledger/DEC-20260722-003.yaml` limitations: saturation is a hull statement at finite p; literal support saturation is char-0/generic-t; C1 open.
- `ledger/EV-BKKMV-002.yaml` observations/boundaries: 2/30 hull-interior losses; MV about hulls.

**Changed text**

| Field | Before (TASK-20260725-681) | After (TASK-20260725-693) |
| --- | --- | --- |
| `scoped_claim` | Toy m=6 extension: MV_6=125829120=5!·2^20 on 6/6 with persistent box saturation; beyond m=6 unmeasured. | Toy m=6 extension: MV_6=125829120=5!·2^20 on 6/6 with MV/Bézout_box=1; hulls box-saturated at finite p (2/30 sections lost 30–60 hull-interior monomials; corners intact; MV unchanged); literal support saturation is char-0/generic-t; beyond m=6 unmeasured; all-m law remains C1 open. |

Also mirrored in `draft_findings.md` KN-FIND-019 Scoped claim / Limits / Not claimed.

**Status:** closed.

---

## N2 — Load-bearing DEC/EV bounds omitted from scoped_claims

### KN-FIND-020 (EQJ)

**Citation:** `ledger/DEC-20260718-006.yaml` limitations: “Toy p <= 2^12, m=4, 3 seeds…”.

| Field | Before | After |
| --- | --- | --- |
| `scoped_claim` | Toy m=4 fibers: isotypic blocking yields no LA cost gain (full-rank survivors; 4× all-blocks cost); only orbit storage matching FHJRV symmetrization. | Toy p≤2^12, m=4 fibers: isotypic blocking yields no LA cost gain (full-rank survivors; 4× all-blocks cost); only orbit storage matching FHJRV symmetrization. |

### KN-FIND-021 (FB)

**Citation:** `ledger/EV-FB-001.yaml` boundaries: “Toy p~2^14, m=3, d<=12; subgroup base excluded…”; `ledger/DEC-20260716-004.yaml` limitations also name subgroup-base exclusion.

| Field | Before | After |
| --- | --- | --- |
| `scoped_claim` | Toy p~2^14, m=3, d≤12: tested FB structures leave d_reg, yield, and solve-cost scaling invariant vs random FB. | Toy p~2^14, m=3, d≤12 (subgroup base excluded): tested FB structures leave d_reg, yield, and solve-cost scaling invariant vs random FB. |

### KN-FIND-027 (SIG-005)

**Citation:** `ledger/DEC-20260720-001.yaml` limitations: toy scale n≤24, D≤5 valid; sibling SIG drafts already used “Toy boolean Semaev…” prefix.

| Field | Before | After |
| --- | --- | --- |
| `scoped_claim` prefix | *(none; started at “D4 law…”)* | Toy boolean Semaev t=3, n≤24: … |

(Combined with N3 rewrite of the null/cascade clause below.)

**Status:** closed.

---

## N3 — KN-FIND-027 overgeneralizes D≥6 null invalidity

**Objection:** Demonstrated fact is D=6 null C5 failure at n=9; blanket “D≥6 null baseline invalid” overreaches.

**Citation:** `ledger/DEC-20260720-001.yaml` rationale: support-matched null fails C5 at D6 (RUN-k, n=9); cascade characterization valid ONLY for D≤5; D6 birth-law measurement retracted as invalid.

| Field | Before | After |
| --- | --- | --- |
| null/cascade clause | D≥6 null baseline invalid — cascade admissible only through D≤5. | D=6 null baseline invalid at tested n=9 (C5 fail) — cascade claims admissible only for D≤5. |

**Full revised scoped_claim (N2+N3):**
> Toy boolean Semaev t=3, n≤24: D4 law (2n/3+1) holds through n=24; D5-born residual non-monotone through n=18; D=6 null baseline invalid at tested n=9 (C5 fail) — cascade claims admissible only for D≤5.

**Status:** closed.

---

## N4 — empirical_only drafts omit THM_BKKMV1 upgrade

**Objection:** DEC-20260722-003 / `research/THM_BKKMV1.md` prove m≤5 sectioned barrier; KN-FIND-017/002/003 had empty `proof_refs` and no cross-note (underclaim).

**Citation:** `ledger/DEC-20260722-003.yaml` rationale + limitations; `research/THM_BKKMV1.md`.

**Changed text (KN-FIND-017, KN-FIND-018, KN-FIND-019):**
- Keep `proof_status: empirical_only` (EV-scoped empirical claims unchanged).
- Set `proof_refs: [research/THM_BKKMV1.md, DEC-20260722-003]`.
- Add package-level and per-draft theorem cross-note: m≤5 proved; m=6 certified; do not invent all-m theorem (C1 open).
- Add `DEC-20260722-003` to KN-FIND-017/002 `internal_refs` as the later upgrade pointer.

**Status:** closed.

---

## Not in this repair (explicitly deferred)

| ID | Why deferred |
| --- | --- |
| N5 | Thin Key claims bodies — DEC-20260725-021 accepts until `/curate-knowledge`; not a ledger-PASS blocker for scoped-claim repair. |
| N6 | Snapshot receipt metadata — Coordinator archive hygiene (TASK-20260725-682 / successor), not producer wording. |

---

## Diff checklist vs cited bounds

| Finding | Phrase retained/added | Source | Crypto-scale language? |
| --- | --- | --- | --- |
| KN-FIND-019 | hulls box-saturated; 2/30; 30–60 hull-interior; corners intact; MV unchanged; literal = char-0/generic-t; C1 open | DEC-20260722-003, EV-BKKMV-002 | no |
| KN-FIND-020 | p≤2^12 | DEC-20260718-006 | no |
| KN-FIND-021 | subgroup base excluded | EV-FB-001, DEC-20260716-004 | no |
| KN-FIND-027 | toy boolean Semaev; n≤24; D=6@n=9 C5 fail; D≤5 only | DEC-20260720-001 | no |
| KN-FIND-017/002/003 | THM_BKKMV1 + DEC-20260722-003 proof_refs; m≤5 proved / C1 open | DEC-20260722-003 | no |

## Files written

1. `coordination/goals/GOAL-FIND-001/batches/BATCH-002/tasks/TASK-20260725-693/promotion_map.yaml`
2. `coordination/goals/GOAL-FIND-001/batches/BATCH-002/tasks/TASK-20260725-693/draft_findings.md`
3. `coordination/goals/GOAL-FIND-001/batches/BATCH-002/tasks/TASK-20260725-693/repair_note.md`
