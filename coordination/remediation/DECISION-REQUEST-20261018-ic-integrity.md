# Decision request: index-calculus integrity findings, 2026-10-18

Written by a non-Coordinator session at the owner's request (branch `claude/ic-integrity-fixes-20261018`). It changes no hypothesis, goal, experiment or knowledge status. Each item names the record, the exact action, and the authority it needs. Evidence: [`docs/reports/2026-10-18-semaev-s4-factor-base-audit.md`](../../docs/reports/2026-10-18-semaev-s4-factor-base-audit.md) and the `problems/` records linked below.

## R-1. KN-OPEN-5b3a08 (shared `s4_expr`, factor-base scope)

1. **Close Q1 as repaired and exact-tested.** `harness/semaev.py` now vanishes exactly on `±P1±P2±P3±P4 = O` (0 mismatches, two toy curves; `tests/test_semaev_s4_exact.py`). Knowledge entries are corrected by superseding, so the request is: file a successor open problem for the remaining questions (matched reruns of the affected runs; Q2 cofactor confound) and set `superseded_by` on KN-OPEN-5b3a08.
2. **Extend CORR-20260813-d9f0fa** (or file a new CORR) to add **RUN-ICINV-e0cd8f-m3class** to the affected archived families. Its m4 invariants (`s4_support` 227/225 archived, 439 recomputed on two sample curves) came from the defective `s4_expr`; the CORR record lists only EXP-MTIC-001 (11 runs) and EXP-FIB-001 (10 runs). The m3 columns are unaffected.
3. **Authorize matched reruns** (CORR-20260813-d9f0fa already requires a Coordinator-approved contract) of the 21 MTIC/FIB runs and the ICINV m4 stage under the repaired code, with the archived runs kept. Until then no MTIC/FIB/ICINV-m4 number should be compared with a post-repair output.

## R-2. Negatives whose ground was infrastructure or process

Annotated by `problems/` records (the schema has no note field on hypotheses and goals, and those files are Coordinator-owned). Requested: link each record from the affected goal or hypothesis notes so it stops being cited as a result.

| Item | Ground | Record | Rerun needed |
| --- | --- | --- | --- |
| GOAL-DREG-001 item C1 | 0/6 runs `failed_infrastructure`; prepare RSS 11.73-12.22 GiB vs 8 GiB cap (DEC-20260828-653923) | [dreg-c1-memory-cap-exhausted](../../problems/dreg-c1-memory-cap-exhausted.md) | Execute TASK-20261005-821d86 (16 GiB floor, DEC-20261005-8d23bb); no output on `main` yet |
| EXP-ECTD-0cf008 | 17 of 20 arms: 11 `psutil` missing, 2 RSS sampling, 4 blocked on them | [ectd-arity3-panel-infrastructure-loss](../../problems/ectd-arity3-panel-infrastructure-loss.md) | Approve the 17-arm additive recovery amendment (draft in the experiment's `amendments/`) |
| H-STR-002 | `weakened` for absent run records and non-reproducing numbers (DEC-20260727-009); EXP-STR-004 tested the instrument only | [str002-support-verdict-missing-artifacts](../../problems/str002-support-verdict-missing-artifacts.md) | Mechanism-level successor with frozen criteria |
| H-DTREE-001 | `inconclusive`, `design_infeasible` stop rule (DEC-20260809-91d4c7) | [dtree-slope-grid-design-infeasible](../../problems/dtree-slope-grid-design-infeasible.md) | Seed-policy amendment or successor, with a `target_subgroup` versus `full_curve` factor-base arm |

## R-3. Stale registers KN-OPEN-004 to KN-OPEN-010

**The premise did not hold, so nothing was closed.** DEC-20260722-003, -004, -005 concern other goals and DEC-20260722-006 does not exist. The relevant records are the scoped toy-scale negatives (EV-BKK-001, EV-BKKMV-001/002, EV-JET-001, EV-JETB-001, EV-NET-001, EV-NCP-001, EV-TTN-001/002, EV-TRA-001), DEC-20260804-4f37d5 (KN-OPEN-009 `CLOSED`, KN-OPEN-005 `PARTIALLY_ADDRESSED`) and the survey DEC-20260804-139a86, whose `knowledge_promotion.promoted` lists no KN-OPEN closure. Each entry's own text says its asymptotic or general question remains open, and the monodromy statement is contested (KN-FIND-a8990a "NOT closed by it"; KN-OPEN-8a7432 reopens m >= 4). Each of the seven entries got an appended reconciliation note with these cross-references and kept `status: open`.

Requested: a Coordinator decision per entry choosing one of (a) keep `open` with the scope the note states, (b) supersede with a successor entry naming the unresolved asymptotic question (as done for KN-OPEN-009), or (c) close, only where a proof rather than a toy-scale negative is cited. Missing from this checkout: hypothesis files H-BKK-001, H-BKKMV-001, H-JET-001, H-JETB-001, H-NET-001 (cited by evidence records but not found under `ledger/hypotheses/`), and decision records for the "rejected_scoped" lines in DEC-20260804-139a86 (H-TTN-001, H-NCP-001, H-TRA-001).

## R-4. H-BINSTD-5fdceb

`ledger/hypotheses/H-BINSTD-5fdceb.yaml` has two `status:` keys in one mapping (lines 23-24): `rejected` then `weakened`. A YAML loader keeps the last, so tools read `weakened`, and `ledger/.index/hypotheses.jsonl` is built from that. `status_history` ends `weakened -> rejected` by DEC-20261003-adddf4 (EV-BINSTD-f9c882, replication, `reject_scoped`, clause (C)/H1 at n=17, m=3, l in {5,6} only; clause (A) stands). The decision therefore supports `rejected`. Requested: delete the stray `status: weakened` line (a one-line edit that matches the file to the recorded decision), rebuild the ledger index, and confirm the scope text stays attached to `rejected`. Not edited here because the effective parsed status would change from `weakened` to `rejected`.

## Not requested

No status change to any hypothesis, goal or experiment other than the R-4 duplicate key. No claim here is an improvement over the index-calculus baseline; these are integrity repairs (engineering) and records of unmeasured effects.
