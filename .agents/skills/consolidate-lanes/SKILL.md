---
name: consolidate-lanes
description: "Run a cross-lane consolidation pass over the agent bus: read traffic ACROSS lanes that cannot see each other and carry pointers between them, so two sessions circling one experiment find out before the second spends its budget. Use on a schedule (hourly to daily) while several sessions work one goal, when opening a second lane on a goal another session is already working, before approving a batch that overlaps another lane, or when asked to cross-pollinate or reconcile what parallel sessions are doing. Dispatches the consolidator subagent. Carries pointers, never findings; writes no ledger record and changes no status."
---

# consolidate-lanes

Read `.claude/skills/consolidate-lanes/SKILL.md` from this checkout and follow it. Resolve references and assets relative to that canonical directory. Preserve its authority and execution boundaries; this adapter adds no runtime role.
