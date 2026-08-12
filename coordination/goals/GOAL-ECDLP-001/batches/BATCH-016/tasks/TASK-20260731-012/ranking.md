# TASK-20260731-012 — Ranking, sub-goal decomposition, selection

**Role:** coordinator (in-session; Claude/GPT subagent API limits → fallback `cursor-grok-4.5`)  
**Goal / batch:** GOAL-ECDLP-001 / BATCH-016  
**Question:** RQ-ECDLP-002  
**Depends on:** TASK-20260731-010 (ideation), TASK-20260731-011 snapshot `7ab1563a6c1f9a981abf0f44049cc2d45fb6eb20` (verified)

## Inputs bound

- IDEA-20260731-007 .. IDEA-20260731-011 (archived)
- EV-STR-004 / DEC-20260730-014 (BATCH-015: EXP-STR-004 inconclusive; H-STR-002 remains weakened)
- docs/target-result-profile.md, docs/inventor-protocol.md
- Prior ledger: H-STR-002 weakened, H-IC-001 weakened, H-ENDO-001 approved, H-YIELD-001 / H-GGM-001 specified, H-FCP-001 analyzed; IDEA-20260727-001..008

## Ranking (IDEA-20260731-007..011)

| Rank | ID | Class | Score drivers | Decision |
|---:|---|---|---|---|
| 1 | IDEA-20260731-007 | algorithm | Exponent-shaped bottleneck→claw conversion; named HEUR-DS-1; falsifiable R; pairs with null control | **SELECT** for /design-experiment |
| 2 | IDEA-20260731-011 | control | Inventor-protocol mandatory gate for any sub-birthday claim | **BIND** into selected contract (not a standalone attack) |
| 3 | IDEA-20260731-008 | mechanism | Strong overclaim gate; not itself a generic exponent move | Queue as SG-ECDLP-002 |
| 4 | IDEA-20260731-009 | measurement | Building-block for IC cost honesty / HEUR-FF-1 | Queue as SG-ECDLP-003 |
| 5 | IDEA-20260731-010 | composition | Multi-target amortization; dominated at T=1 by rho given current floors | Queue as SG-ECDLP-004 after single-target honesty |

### Rejected as primary this batch

- Any STR / `phi_alpha` / displacement-rank instrument ablation: blocked by DEC-20260730-014 inconclusive close and BATCH-016 opening constraint (no new mechanism named for STR).
- Selecting 008/009/010 first: lower exponent-search value than 007 under the target profile (gate / measurement / amortization vs bottleneck rewrite).

## Sub-goal decomposition (durable)

Canonical file:

`coordination/goals/GOAL-ECDLP-001/sub_goals/decomposition_BATCH-016.yaml`

| Sub-goal | Status | Primary IDEA / H | Claim ceiling |
|---|---|---|---|
| SG-ECDLP-001 | selected_next | IDEA-20260731-007 (+011 control); H-IC-001 context only | toy charged-cost ratio |
| SG-ECDLP-002 | queued | IDEA-20260731-008 | transfer gate / toy accounting |
| SG-ECDLP-003 | queued | IDEA-20260731-009 | measurement only |
| SG-ECDLP-004 | queued | IDEA-20260731-010; H-YIELD-001 | multi-target composition |
| SG-ECDLP-005 | mandatory_template | IDEA-20260731-011 | methodology only |
| SG-ECDLP-006 | parked | H-STR-002, H-ENDO-001, H-GGM-001, H-FCP-001, IDEA-20260727-* backlog | bookkeeping; no STR reopen |

Pointer also recorded on `ledger/goals/GOAL-ECDLP-001.yaml` under `sub_goals`.

## Selection

- **selected_sub_goal_id:** `SG-ECDLP-001`
- **selected_idea_id:** `IDEA-20260731-007`
- **Why:** Sole BATCH-016 algorithm proposal that targets a Semaev membership bottleneck with a Wesolowski-style MITM/smoothness rewrite, an explicit numbered heuristic, Pareto fields filled, and a clear falsifier (R≥0.9 or null-tracking). Aligns with RQ-ECDLP-002 and exponent-first bias; keeps H-STR-002 parked.

Ideas remain proposals. No hypothesis status changes. No runs. MAKE NO COMMIT in this task — TASK-20260731-013 archives.

## next_action (written to GOAL-ECDLP-001)

Open BATCH-017 to `/design-experiment` on IDEA-20260731-007 under SG-ECDLP-001, freezing IDEA-20260731-011 null-control into the contract; do not reopen STR instrument polish.

## Inference

```yaml
requested_policy: coordinator-orchestration-code
resolved_model_id: cursor-grok-4.5
fallback_used: true
fallback_reason: Claude/GPT coordinator subagent API limits; completed in-session
```
