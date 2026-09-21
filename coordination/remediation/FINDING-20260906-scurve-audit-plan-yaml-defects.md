# FINDING-20260906-scurve-audit-plan-yaml-defects

Recorded by: coordinator-ecrank-5 (Coordinator session, GOAL-ECRANK-002 lineage)
Date: 2026-09-06
Branch: scurve-plan-defects-20260906 (from origin/main 14c80d032)
Status: coordination-remediation record. NOT a ledger record, NOT evidence,
NOT a research result. No goal record edited, no decision minted, no batch
opened, no hypothesis or criterion cell touched.

## What was done

Read-only parse attempt (`yaml.safe_load`) of every committed SCURVE audit
plan on main:

    coordination/goals/GOAL-SCURVE-*/batches/*/tasks/*/audit-plan.yaml

20 files found. 9 parse cleanly. 11 FAIL to parse:

| goal | first parser error (truncated) |
|---|---|
| GOAL-SCURVE-15e805 | while parsing a block collection (mapping key indented inside a block sequence, ~line 1754) |
| GOAL-SCURVE-28e491 | while scanning a simple key |
| GOAL-SCURVE-48e06c | while scanning a simple key |
| GOAL-SCURVE-4f0635 | while parsing a flow mapping |
| GOAL-SCURVE-51437e | while parsing a block collection |
| GOAL-SCURVE-7b280d | mapping values are not allowed here |
| GOAL-SCURVE-873d08 | while scanning a block scalar |
| GOAL-SCURVE-8ba49a | mapping values are not allowed here |
| GOAL-SCURVE-9eb661 | while parsing a block mapping |
| GOAL-SCURVE-be9707 | while parsing a block mapping |
| GOAL-SCURVE-e33f7d | while parsing a block mapping |

The inspected 15e805 defect is structural, not cosmetic: sibling mapping keys
(`no_lane_declared_impossible`, `open_directions_for_next_session`) are
indented inside the `closures_enumerated` block sequence. The content is
human-readable; the file is not machine-readable.

## Why this matters now

All 20 GOAL-SCURVE-* goals sit in the portfolio's "batch complete" bucket
awaiting one Coordinator successor decision each (capability gate ANSWERED by
FINDING-20260904-scurve-execution-capability.md, on main). Those successor
batches will hand the archived audit plan to executors as frozen input. For
11 of 20 goals that input does not parse, and:

- `tools/validate_ledger.py` does not cover coordination artifacts, so
  nothing in CI catches this;
- `tools/schema_supersession_registry.yaml` kinds are
  ledger/experiment/knowledge/goal_checkpoint — coordination paths cannot be
  routed through it, so the sanctioned repair is NOT a registry supersession.

## What this does NOT establish

- It does NOT say the plans are semantically wrong — only that 11 files are
  malformed YAML at the byte level. The remaining 9 parse; parse success is
  not a quality judgement either.
- It does NOT adjudicate any criterion cell, lane, or curve, and generalises
  to nothing beyond the listed files at main 14c80d032.
- The originals are immutable committed artifacts: they stay exactly as they
  are.

## Repair path for successor decisions (per goal, when its turn comes)

1. The successor decision discloses the defect for its goal (this file is the
   fleet-level pointer; re-verify at decision time — state may have moved).
2. The successor batch authors a CORRECTED COPY as a new artifact under its
   own task write_scope (e.g. `audit-plan.v2.yaml`), content-faithful to the
   committed original with only the YAML structure repaired, and carries a
   provenance header naming the original path, its commit, and the defect.
   The original is never edited.
3. Executors bind the corrected copy (parse-checked at dispatch), and the
   task receipt records the original→copy correspondence. A dispatch that
   hands a non-parsing plan to an executor and discovers it mid-run is the
   exact failure mode FINDING-20260904's per-session-capability caveat warns
   about, one level down.
4. Where the corrected copy's content is ambiguous at the damaged site, the
   ambiguity is disclosed in the copy's header and the lane scoped around it
   — never silently resolved.

## Provenance

Parse sweep run in worktree
/Volumes/SSD990/crypto-autoresearcher/.worktrees/aes003-batch015-20260831 at
origin/main 14c80d032, 2026-09-06, by the Coordinator session directly
(declared fallback; resolved model
fireworks-ai/accounts/fireworks/models/qwen3p8-max, model_verified false).
Announced on the agent bus to all addresses.
