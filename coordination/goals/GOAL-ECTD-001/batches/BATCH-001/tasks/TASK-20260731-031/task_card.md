# TASK-20260731-031: Independent review of ECTD literature + ideation package

- **goal:** GOAL-ECTD-001
- **batch:** BATCH-001
- **role:** red-team
- **state:** queued
- **priority:** 60
- **depends_on:** TASK-20260731-027, TASK-20260731-028, TASK-20260731-029, TASK-20260731-030
- **review_required:** False
- **archived_by:** TASK-20260731-032

## Objective

Adversarially review the ECTD literature package and three IDEA proposals: challenge citation honesty, class-invariant smuggling, conflation with H-ISO-001 or IDEA-20260731-008, missing null-object controls, overclaim of fixed-factor GLV as a trapdoor, and premature closure language.

## Completion gate

- Each of IDEA-20260731-016..018 has an admit/revise/reject_for_batch verdict with rationale.
- Citation-honesty and class-invariant-smuggling checks are explicit.
- independent_session: true and model metadata recorded.
