# TASK-20260731-052 — EXP-ECTD-001 freeze validation

**Role:** validator · **Session:** independent (`independent_session: true`)  
**Snapshot:** `189678cb` (TASK-20260731-051) · **Verdict:** **approve_for_execution**

## Summary

EXP-ECTD-001 faithfully embeds all TASK-20260731-049 admit conditions for IDEA-20260731-016. The frozen contract is ready for Coordinator approval and execution planning; this validation does not approve trapdoor claims or asymptotic results.

## Checklist (all pass)

| Check | Result |
|-------|--------|
| claim_tier toy, approved_by null, status review_required, frozen true | pass |
| Within-class permutation null | pass (`CTRL-PERMUTATION`, `TAIL-ECTD-PERM-STABLE`) |
| Mandatory planted outlier | pass (`CTRL-PLANTED-OUTLIER`, `instrument_void` on failure) |
| Semaev-shaped degree-profile null | pass (`CTRL-DEGREE-PROFILE`, ALBIN note) |
| Decision table + scoped_homogeneity wording | pass (explicitly not family closure) |
| HEUR-ECTD-TAIL-1 not credited from JMV alone | pass (KS/permutation only) |
| No class-invariant secret endpoints | pass (detector + negative arms only) |
| Heavy-tail ≠ trapdoor | pass (claim_ceiling, branches, H statement) |
| 017/018 revised in proposals; EXP is 016-only | pass |
| Snapshot receipt + hash binding | pass |

## Non-blocking notes

1. **IDEA-20260731-016.yaml** was not snapshotted and still has stale barrier wording in `falsification_conditions`. Binding scope is **H-ECTD-001 + EXP-ECTD-001** at `189678cb`, which is correct.
2. Snapshot receipt `commit_sha` is null in-blob; validated via git commit and SHA-256 path hashes.
3. Policy fallback: runtime `composer-2.5-fast`, not probe-verified `review-adversarial`.

## Next step

Coordinator **TASK-20260731-053** may set `EXP-ECTD-001.status: approved` and assign `approved_by` if this verdict stands with TASK-20260731-049's IDEA-016 admit intact.
