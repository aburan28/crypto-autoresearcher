---
name: research-status
description: >-
  Summarize the current state of the research program: open questions,
  hypothesis statuses, experiments in flight, recent decisions, and next
  actions. Use at session start or whenever an overview of the ledger is
  needed. Read-only.
---

# Research status

Produce a read-only snapshot of the program. Make no state changes.

## Steps

Read the generated census first; open individual records only for the
items it flags. A status wake that reads forty ledger files by hand is the
cost `docs/track-record-review-20261006.md` measured and asked to stop
paying.

1. Run the census and the cached portfolio view:
   - `python3 tools/ledger_summary.py` — questions, proposals, hypotheses by
     status, experiments by `execution_state`, recent decisions, open
     handoffs, the portfolio KPIs (approved-unrun per goal against the
     capacity cap, aged open handoffs, bus unread counts), and the session
     receipt summary;
   - `python3 tools/portfolio_health_cache.py --show` — the goal-head
     classification `main-health.yml` refreshed on the last merge, with its
     age; stale (`--max-age-hours`) means read `goal_portfolio_health.py`
     live only for the goals you are about to act on;
   - `python3 tools/agent_bus.py inbox --as <your address>` and
     `peers` for unread traffic.
2. For experiments the census lists as `ready` or `approved` without runs,
   confirm against `python3 tools/newest_experiments.py` (readiness-first,
   holds honoured, off-`main` runs discovered) rather than by scanning
   `experiments/*/` yourself.
3. Check integrity while scanning and flag (do not fix):
   - hypotheses referencing missing questions, evidence referencing missing
     runs, experiments approved with null fields;
   - run directories missing required artifacts;
   - decisions whose `next_actions` have no follow-up handoff;
   - theory, experiment, task-report, knowledge, or ledger paths that remain
     uncommitted or lack a verified Coordinator archive receipt;
   - the working branch behind `origin/main` (un-merged-upstream) or with no
     open PR against `main` — flag it so the next generation step can merge
     `main` and open/refresh the PR before producing new records.
4. Report: a short table per ledger area, experiments in flight with run
   tallies, the latest decision per active hypothesis, integrity flags, and
   the concrete next action the lifecycle implies (e.g. "EXP-ISO-002 is
   approved but has no runs → /run EXP-ISO-002").
5. **Receipt.** End with `python3 tools/session_receipt.py --skill
   research-status --role <role> --outcome no_change --files-read <n>`
   (`docs/session-receipts.md`). Read-only is still a cost; the receipt is
   how the program learns what a status wake costs.
