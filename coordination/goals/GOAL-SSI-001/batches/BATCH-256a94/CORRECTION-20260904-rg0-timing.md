# Correction: the "admitted upstream on 2026-08-09" timing was wrong

**Scope: a timing claim only. The RG-0 verdict `fix_already_applied` is
unaffected and stands.**

## What was claimed

The orchestrating session's dispatch prior, `BATCH-256a94/batch.yaml`'s
opening observation, and the commit message of `c1a39ee5a`
("runs(GOAL-SSI-001): RG-0 source-state census") all state or imply that the
EXP-WESOVOW-001 charging-law repair was **applied, reviewed and admitted
upstream on 2026-08-09**, and therefore that GOAL-SSI-001's recorded next
action of 2026-08-24 rested on a premise already overtaken.

## What git actually shows

`TASK-20260904-1f4e2f` reported this as anomaly **AN-1**, and the orchestrating
session then verified it independently:

| check | result |
| --- | --- |
| `git merge-base --is-ancestor 7d188a7c3 e45861af` | **non-zero** — the fix was NOT on the `origin/main` the BATCH-eb0a7e snapshot receipt recorded |
| `git merge-base --is-ancestor 7d188a7c3 bd47a3f5c` | **non-zero** — the fix was NOT an ancestor of that batch's snapshot base |
| `2675886ea` "Merge pull request #471 from aburan28/codex/ssi-cost-source-20260809" | **2026-08-24 20:50:28 UTC** — when the source reached `origin/main`'s first-parent line |
| `bd47a3f5c` (BATCH-eb0a7e snapshot base) | **2026-08-24 18:32 UTC** |

The intermediate merge `efd27d78` (2026-08-09) carried the fix but was itself
unreachable from `origin/main` until 2026-08-24 20:50 UTC.

## The corrected account

The **decision** `DEC-20260809-c1066f` is dated 2026-08-09. The **source** did
not reach `origin/main` until roughly two hours *after* BATCH-eb0a7e's snapshot
base. So:

- BATCH-eb0a7e was **not** reading a stale checkout of an already-upstream fix.
  Its localization of the defect at `cost_model.py:236` and `:270` was correct
  against the state it could actually see, and no fault attaches to it.
- The 2026-08-24 next action was **not** obviously stale when written.
- What remains true, and is what RG-0 was asked to settle: the corrected law
  **is** on `origin/main` today, so no source fix is outstanding now.

Recorded as a superseding note rather than by rewriting `c1a39ee5a`, whose
commit is already pushed. The authoritative account is AN-1 in
`tasks/TASK-20260904-1f4e2f/`; this note exists so a reader who arrives via the
commit message finds the correction.

The P=512 crossover and the w=2^80 sign remain NOT citation-eligible. Nothing
here lifts that.
