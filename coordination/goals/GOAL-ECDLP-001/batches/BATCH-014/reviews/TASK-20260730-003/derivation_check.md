# TASK-20260730-003 — Derivation check for EXP-STR-004 v2

**Report:** `RT-20260730-001` (path + task id).
**Reviewed HEAD:** `26625837d422d3c0cf8a108e93b09cee149c9070` (TASK-20260730-002 amendment snapshot).
**Question:** Does `T(cell)` still hold, and is any derivation change required by the v2 amendment?

## Verdict

**`T(cell)` still holds. No derivation change is required.**

## Evidence

1. **Byte identity.** `experiments/EXP-STR-004/derivation_note.md` at HEAD `26625837` has sha256
   `fb7f33d94c953b1dd1b51f0e8452d7da03fc1485e32cd86df651a52ed67fe582` (26879 bytes), identical to the
   blob at the v1 freeze commit `f3e15614`.
2. **Amendment declaration.** `experiments/EXP-STR-004/amendments/v1_to_v2.yaml` lists
   `derivation_note.md` under `not_changed`. The v2 edits are confined to the verdict rule
   (`prediction_failed` / F-1–F-4 matrix labeling), the B-2 coincide retraction, and the M-1
   F-4 rephrase — none of which alter the square-branch identity, the MIS vanishing criterion,
   or the closed form of `T(cell)` in §8.1.
3. **Prior independent re-derivation.** `RT-20260729-034` / `TASK-20260729-042` re-derived the
   square-branch identity and `T(cell)` from `harness/endomorphism_la.py` and matched the note.
   Because the note and the harness sources bound by the contract are unchanged by PA-STR-004-v1-to-v2,
   that re-derivation is not reopened here.

## Scope of this check

This is a **derivation** check (class 2), never `proved`. No cell was measured. The REVISE
verdict of the companion `contract_review.yaml` is about verdict-label completeness (B-1), not
about `T(cell)`.
