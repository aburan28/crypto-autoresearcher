# TASK-20260730-007 — Derivation check for EXP-STR-004 v3

**Report:** `RT-20260730-002` (path + task id).
**Reviewed HEAD:** `135149d098f8213b2da043135817b2c6499339d1` (TASK-20260730-006 amendment snapshot).
**Question:** Does `T(cell)` still hold, and is any derivation change required by the v3 amendment?

## Verdict

**`T(cell)` still holds. No derivation change is required.**

## Evidence

1. **Byte identity.** `experiments/EXP-STR-004/derivation_note.md` at HEAD `135149d0` has sha256
   `fb7f33d94c953b1dd1b51f0e8452d7da03fc1485e32cd86df651a52ed67fe582` (26879 bytes), identical to the
   blob at the v1 freeze commit `f3e15614` and at the v2 amendment commit `26625837`
   (git object `1ee38722a8fd005ae998634e689fa82c33558bdb` at all three).
2. **Amendment scope.** `experiments/EXP-STR-004/amendments/v2_to_v3.yaml` changes only the
   instrument verdict label `prediction_failed` (generalized F-1 on either arm with F-4 silent)
   and inherits B-2 / M-1 from v2. It does not alter the square-branch identity, the MIS
   vanishing criterion, or the closed form of `T(cell)` in §8.1.
3. **v2→v3 specification diff.** Confined to version/provenance metadata and the
   `prediction_failed` clause inside `verdict_rule`. No prediction P-1..P-4 text, no cell
   table, and no `R_base` arithmetic changed.
4. **Prior independent re-derivation.** `RT-20260729-034` / `TASK-20260729-042` re-derived the
   square-branch identity and `T(cell)` from `harness/endomorphism_la.py` and matched the note.
   Because the note and the harness sources bound by the contract are unchanged by
   PA-STR-004-v2-to-v3, that re-derivation is not reopened here.

## Scope of this check

This is a **derivation** check (class 2), never `proved`. No cell was measured. The PASS
verdict of the companion `contract_review.yaml` is about verdict-label completeness (B-1
remainder closed), not about a new derivation.
