# Track record and skill-efficiency review, 2026-10-06

A holistic read of what the program has actually produced against what it has
spent, and the changes that would raise evidence per token. Everything in the
first half is **measured** at `main` commit `9c2bc35e93` with the commands
shown; everything in the second half is a **proposal** and changes no record,
status, or rule by itself. This document is not evidence about any
cryptographic claim.

## 1. Summary

The program is a design engine with a tiny execution tail. Ideation and design
convert at close to 1:1 — 86% of the 2,319 proposals reach a frozen experiment
contract and 1,473 contracts are `approved` — but only 7% of proposals ever
reach an evidence record, 1,469 approved contracts have no run on `main`, and
82 of the 84 contracts the `/run` selector offers today need an implementation
nobody is allowed to write (`/coordinate` may not implement, `/run` may not
implement). Two Coordinator decisions filed on 2026-10-05
(`DEC-20261005-138b51`, `DEC-20261005-98a823`) already name the mechanism: the
"open ECC ideas are designed, not shelved" rule plus unlimited ECC budget plus
standing authorization produces an approval stream whose contracts carry no
decision-changing information, including 173 template contracts whose outcome
was written into the record before any run.

Token spend is dominated by five sinks, none of them reasoning about
mathematics: (1) a 14k-word instruction wake-up per Coordinator session,
(2) oversized state records that every resume reads (a 139k-word goal head, a
55k-character `next_action`, 28 KB median dispatch queues), (3) ceremonial
fields and duplicated policy paragraphs copied into 849 records, (4) a 56 MB
proposal corpus that the dedup step is told to read, and (5) coordination
traffic nobody reads (89% of bus messages have no receipt, 278 handoffs have no
return). None of this is measured: the token-efficiency work that exists
(`docs/token-efficiency.md`, prompt caching) covers only the `api_direct`
runtime, while essentially every commit since September came from Cursor and
Claude Code sessions that record no usage. The eval harness
(`orchestration/eval`) has never written a result and `tune-skill` has never
run a round.

The highest-leverage changes are therefore not prompt polish. They are
(a) an execution-capacity gate on approval, (b) making "runnable" a condition
of approval, (c) a decision-aware `/run` selector, and (d) halving the bytes a
session must read before it can act. Those four would have prevented most of
the September–October spend without weakening any evidence rule.

## 2. What was measured

All counts from `main` at `9c2bc35e93` (2026-10-06). Reproduce with
`python3 tools/ledger_summary.py`, `python3 tools/goal_portfolio_health.py
--json`, `python3 tools/newest_experiments.py --limit 0 --json`, and the
one-off shell/Python shown inline. `rg` in the Cursor image mis-parses `-N`;
use `grep -rhoE` for identifier harvesting.

### 2.1 The funnel

| stage | records | notes |
| --- | ---: | --- |
| research questions (`RQ-*`) | 174 | 168 `active` |
| proposals (`IDEA-*`) | 2,319 | 1,995 still `proposed`; 2 `selected` |
| hypotheses (`H-*`) | 1,945 | 958 `specified`, 404 `proposed`, 354 `approved`, 144 `analyzed`; **29 `supported`, 22 `weakened`, 4 `rejected`** |
| experiment contracts (`EXP-*`) | 2,556 dirs | 1,473 `approved`, 579 `draft`, 326 `review_required`, **29 `completed`, 55 `analyzed`** |
| experiments with any run content | 478 (19%) | 1,014 have only `runs/.gitkeep`; 1,064 have no `runs/` |
| run manifests parsed by the census | 126 | 74 `completed_valid`, 15 `failed_implementation`, 5 `completed_invalid` |
| evidence (`EV-*`) | 709 | 242 `preliminary`, 101 `inconclusive`, 75 `replicated`, 36 `strong`, 33 `moderate`, 55 `n/a` |
| decisions (`DEC-*`) | 3,054 | |
| handoffs (`TASK-*`) | 5,453 | 278 with no recorded return |
| corrections (`CORR-*`) | 588 | |

Conversion, by literal-ID mention across the chain
(`grep -rhoE 'IDEA-2026[0-9]{4}-([0-9a-f]{6}|[0-9]{3})'`):

| from → to | fraction |
| --- | ---: |
| proposal → mentioned in a hypothesis | 78% |
| proposal → mentioned in an experiment spec | 86% |
| proposal → mentioned in a decision | 61% |
| **proposal → mentioned in an evidence record** | **7%** |
| hypothesis → mentioned in an evidence record | 12% |

The design stage is not a filter. Almost everything proposed is specified and
approved; almost nothing approved is run.

### 2.2 Throughput by month

| month | proposals | hypotheses | approvals (`DEC`) | evidence | decisions |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2026-07 | 58 | 1 | 20 | 23 | 175 |
| 2026-08 | 1,474 | 35 | 75 | 162 | 644 |
| 2026-09 | 539 | 931 | 1,112 | 80 | 1,759 |
| 2026-10 (6 days) | 245 | 335 | 382 | 52 | 475 |

September produced 14 approvals per evidence record; October so far produces 7.
51 of October's 475 decisions approve a contract and in the same breath say
"do not launch until a later decision releases it". Commit volume over the same
period: 19,330 commits total, peaking at 4,449 in week 36 (913 merges); since
2026-09-01 the authors are `Cursor Agent` 3,281, `Dispatch Test` 3,158,
`Claude` 2,563, `cursor[bot]` 488 — i.e. the work is done in interactive agent
sessions, not in `api_direct`.

### 2.3 The execution gap, as the tools see it

- `goal_portfolio_health.py`: 65 active goals → 32 `batch_complete` (waiting
  on a Coordinator checkpoint), 23 `blocked`, 5 `needs_repair`, **5 `ready`**.
- `newest_experiments.py --limit 0`: 84 selectable contracts after the two
  2026-10-05 holds drop 151 ids → **82 `needs_implementation_or_plan`, 2
  `ready`**.
- `ledger_summary.py`: **1,469 approved/running experiments with no run
  recorded**.
- `DEC-20261005-98a823` F-2: 173 frozen contracts from one template across 19
  areas, designed 2026-10-01..04; 104 "carry an outcome written in the record
  and disclaim every measured object"; 259 specification commits by `Cursor
  Agent` and 81 by `cursor[bot]` in that window. The `/run` selector reads
  only `main` and ignored decisions until T-2 landed.
- `docs/focused-autoresearch-loop.md` rule 1 ("at most three critical
  experiments active") and its tool `tools/autoresearch_focus.py` were last
  exercised 2026-07-20 (`focus/`). Nothing enforces the rule today.

### 2.4 What a session must read before it can act

| what | size | read by |
| --- | ---: | --- |
| `AGENTS.md` | 8,084 words | every role, every session (auto-loaded) |
| `CLAUDE.md` | 3,659 words | every Claude Code session (auto-loaded); 21 lines verbatim-duplicated from `AGENTS.md`, plus a "summary of AGENTS.md" |
| `agents/coordinator.md` + `.claude/skills/coordinate/SKILL.md` + `WORKFLOW.md` + `references/lifecycle.md` | 5,985 words | Coordinator wake (skill step 1) |
| **Coordinator wake total** | **≈14,069 words ≈ 19k tokens** | before any data |
| docs the skills direct agents to read (`templates/research-records.md`, `inventor-protocol.md`, `target-result-profile.md`, `claims-and-verification.md`, `inference-backends.md`, `concurrent-goal-lanes.md`, `inter-agent-messaging.md`, `batch-inference.md`) | 22,255 words | on demand, often several per turn |
| `.claude/skills/*/SKILL.md` (12) | 11,718 words | `deep-research` 2,013, `tune-skill` 1,713, `design-experiment` 1,160 |
| "Budget policy" paragraph | 7 copies | pasted into 7 files instead of linked |

State records read on resume (`os.path.getsize` over the ledger):

| record kind | n | median | p90 | max |
| --- | ---: | ---: | ---: | ---: |
| goal heads | 116 | 11.3 KB | 78.9 KB | **1,178.9 KB** (`GOAL-ECDLP-001/goal.yaml`, 139k words) |
| `next_action` field | 116 | 1,028 chars | 3,568 | **54,834 chars** |
| dispatch queues (`*.json`) | 604 | 28.2 KB | 98.3 KB | 3,443 KB |
| proposals | 2,319 | 20.9 KB | 46.0 KB | 217 KB (56 MB total) |
| experiment specifications | 2,516 | 7.8 KB | 27.0 KB | 1,054 KB |
| decisions | 3,054 | 4.2 KB | 24.0 KB | 187 KB |
| handoffs | 5,453 | 2.1 KB | 11.4 KB | 1,293 KB |
| coordination task reports | 891 | 8.2 KB | 28.7 KB | 291 KB |

`goal_portfolio_health.py` renders every active goal's queue from scratch and
took ~2.5 minutes on this VM; `/coordinate` runs it at every wake.

### 2.5 Ceremony and dead traffic

- `amazon_bedrock: NOT SELECTED, NOT CONFIGURED, NOT PROBED, NOT CONTACTED,
  NOT USED.` appears in **849** ledger records (289 decisions). The rule it
  attests to is already enforced offline by
  `tools/check_inference_cost_policy.py` and at the adapter boundary.
- `budget.wall_clock_seconds: null` in 2,444 of 5,453 handoffs; the policy
  says estimates may be null, so the field carries no information.
- Agent bus: 332 messages, **37 receipts**. 89% of what sessions write to
  each other is never acknowledged.
- 21 occurrences of `<NNN>` / "next free number" across 11 skill and agent
  files contradict rule 14 (random suffix via `allocate_id.py`).
- `gh pr create` is hard-coded in 4 skills; Cursor cloud sessions cannot use
  it and must use their own PR tool, so the instruction is wrong for the
  runtime that writes most commits.

### 2.6 What is not measured at all

- No token, cache, or cost counter exists for Cursor or Claude Code sessions.
  The ~15 receipts under `coordination/` that carry `input_tokens` are all
  `api_direct` inference receipts (`fireworks`, `zai` backends) or
  `codex_cli` attempts from August–September; none comes from the runtimes
  that author the commits.
- `evals/` has `suites/` and `baselines/` and no `results/`; the
  capability/discipline harness in `docs/measuring-the-harness.md` has never
  produced a record.
- `coordination/skill-tuning/` does not exist: `tune-skill` has never run,
  so no skill has been scored against its downstream outcomes.
- `.git/autoresearch-autopilot/` is absent on this checkout: the opt-in
  continuous supervisor (`docs/research-throughput-autopilot.md`) has not
  been exercised here.

## 3. Diagnosis

### 3.1 The loop rewards records, not runs

Each skill ends by producing records and a PR, and the next stage is a separate
skill in a separate session. `/propose-ideas` → `IDEA`; `/design-experiment` →
`H` + `EXP` + `TASK` + `DEC` + snapshot archive + PR; `/run` → runs, but is
forbidden to implement, fetch, or publish; `/review-evidence` → `EV` + `DEC` +
archive + PR. Every stage before `/run` is cheap in machine terms and
unbounded in policy terms (standing authorization, unlimited ECC budget,
"open ECC ideas are designed, not shelved"), while `/run` is bounded by what
has a launcher. The predictable fixed point is the one measured: a backlog of
approved, unrunnable contracts that the ranking rule keeps refilling.

### 3.2 Context is spent on governance text and stale state

A Coordinator session reads ~19k tokens of rules before it opens a goal head
that may itself be larger than a context window. The rules are mostly history
("this bug shipped three times", "on 2026-09-15 a session…") — valuable in
`docs/`, expensive as an always-loaded preamble. Goal heads accrete
`next_action` prose in capitals because nothing caps them, and
`tools/shard_goal.py` exists but the largest heads are unsharded.

### 3.3 Dedup and orientation are told to read the corpus

`propose-ideas` step 2 says to gather "existing proposals in
`ledger/proposals/` so duplicates are avoided" — 56 MB. There is no compact
index of (id, claim, mechanism, status, area). The same applies to "existing
hypotheses" (22 MB). Sessions either skip the step or spend the context on it.

### 3.4 Nothing closes the loop on the skills themselves

The reward chain `tune-skill` describes is correct (decisiveness of downstream
`EV-*`), but it has never been run, and it would currently report "batch too
thin" for every skill because only 7% of ideas reach evidence. The eval
harness exists and has never been run. So the program has no measured answer
to "did this prompt change help".

## 4. Recommendations

Ordered by expected evidence-per-token gain. Each names the change, the
mechanism that enforces it, and the number that would show it worked. None
weakens the evidence rules, role authority, immutability, or review
independence in `AGENTS.md`; several make an existing rule enforceable.

### P0 — stop paying for approvals that cannot run

1. **Execution-capacity gate on approval.** `design-experiment` step 4 and
   `coordinate` step 5 refuse to record approval for a goal/area whose
   approved-unrun count already exceeds a small cap (the focused-loop rule 1
   number, 2–3), unless the new contract supersedes one of them. Enforce in
   `tools/validate_ledger.py` as a warning first, then an error for
   `DEC-*` records dated after the rule lands. Metric: approved-unrun count
   (1,469 today) falls monotonically; approvals per evidence record (14→7)
   approaches 1–2.
2. **Runnable is a condition of approval.** A contract is `approved` only
   when `newest_experiments.py --experiment <ID>` reports
   `execution_state: ready` — a committed launcher or trial plan exists.
   This moves implementation into the design lane, which is where the
   designer's context already is. `design-experiment` gains a step
   "implement or bind the launcher; if that cannot be done in this turn,
   leave the contract `review_required` and say why". Metric:
   `needs_implementation_or_plan` share of the selector (82/84 today) → 0 for
   new contracts.
3. **Decision-aware, readiness-first `/run` selection.** Extend
   `newest_experiments.py` so holds (`DEC-*` withholding ids) are read by
   default, `ready` sorts above `needs_implementation_or_plan`, and
   off-`main` executions are visible (F-2's `EXP-BINSTD-fdd2d9` exposure).
   Let `/run` commit and push its run records on its own branch; forbidding
   publication strands results and causes duplicate runs. Metric: zero
   duplicate runs of one `EXP-*` across branches; `/run` sessions that end
   with "nothing executable" → 0.
4. **Make "designed, not shelved" bounded.** Amend the rule-11.3 reading in
   `AGENTS.md`/`CLAUDE.md`: an open ECC idea is designed when it can be
   approved under P0.1–P0.2; otherwise it stays `proposed` with a recorded
   reason, which is not shelving. Record this as an additive amendment, as
   `DEC-20261005-138b51` F-1 already requests at the operator level.
5. **Reject pre-written outcomes at design time.** Add a validator check for
   new specifications: success and falsification criteria must reference a
   metric the run produces, and the contract must state what decision changes
   on each outcome (focused-loop rule 3). A contract whose `out_of_scope` text
   disclaims every measured object fails. Metric: template-class contracts
   (F-2's 173) cannot be approved again.

### P1 — halve what a session reads before acting

6. **Instruction diet.** Make `CLAUDE.md` a one-paragraph pointer to
   `AGENTS.md` (the sibling `cairn` repository already does this), keep
   `AGENTS.md` to the rules and the one-line "why", and
   move each incident narrative to `docs/` with a link. Replace the seven
   pasted "Budget policy" paragraphs with one sentence and a link. Target:
   always-loaded instruction ≤ 4k words; Coordinator wake ≤ 7k words. Check
   with `wc -w` in CI (`tools/check_runtime_bindings.py --list` already
   tracks per-role bindings; add a word budget per role).
7. **Cap and shard state records.** Validator warning when a goal head exceeds
   64 KB or `next_action` exceeds 1,000 characters (`next_action` points to a
   file instead); shard the five largest goal heads with
   `tools/shard_goal.py` as they are next opened; add a
   `research_dispatch.py --ready-only` render so a session reads the Ready
   Tasks (typically < 2 KB) instead of the 28 KB queue. Cache
   `goal_portfolio_health.py --json` as a committed artifact refreshed by
   `main-health.yml` so `/coordinate` reads it instead of recomputing it.
8. **Compact indexes for dedup and orientation.** A generated, gitignored
   `ledger/.index/proposals.jsonl` and `hypotheses.jsonl` (id, area, status,
   claim, mechanism, 200-char excerpt) built by `tools/build_ledger_index.py`,
   rebuilt in CI like `knowledge/INDEX.md`. `propose-ideas` step 2 and the
   `tune-skill` chain walk read the index, never the corpus. Expected read
   size: ~0.5 MB instead of 78 MB.
9. **Delete ceremony from templates.** Drop the `amazon_bedrock:` attestation
   from `templates/research-records.md` and the agent contracts (the offline
   guard is the enforcement); drop `budget.*: null` placeholders from handoff
   templates; forbid all-caps prose in `next_action`. Historical records stay
   as they are.
10. **Cap proposal size.** New `IDEA-*` records ≤ 8 KB; long derivations go to
    a sibling `notes.md` the index does not read. Validator warning above the
    cap. Median today is 21 KB with 1,995 unused.

### P2 — measure the thing being optimized

11. **Session receipts for interactive runtimes.** Every skill ends by
    appending one write-once line to `coordination/sessions/receipts/` via a
    small `tools/session_receipt.py`: skill, role, runtime, model (from the
    session environment where available), start/end, records created by kind,
    files read count, outcome. Where the runtime exposes usage (Cursor cloud
    run info, Claude Code transcript totals), record it; where it does not,
    record `null`, never an estimate. This gives the denominator for "tokens
    per validated outcome" that `docs/token-efficiency.md` asks for and the
    program has never had.
12. **Run the eval harness once, then weekly.** `python3 -m orchestration.eval
    run --suite evals/suites/discipline.yaml` and `capability.yaml` on the
    available backend, results into `evals/results/<date>/`; add a weekly
    workflow. This is the only place the harness's own token cost per task
    class is measurable today.
13. **Run `tune-skill` round 1 on `design-experiment` and `propose-ideas`.**
    Expect "batch too thin"; that verdict, with its coverage numbers, is the
    first measured statement about the skills and starts the composable
    window. Add the bounce-count logging the skill lists as a known gap.
14. **Portfolio KPIs in `/research-status`.** Add to `tools/ledger_summary.py`:
    approved-unrun count, proposal→evidence conversion, approvals per
    evidence record, median goal-head size, bus unread fraction. The
    Coordinator's ranking step reads these; a session that raises
    approved-unrun must say why.

### P3 — correctness of the skill text

15. Fix the 21 `<NNN>` / "next free number" instructions to `allocate_id.py`
    (rule 14); make PR creation runtime-neutral ("open or refresh a PR with
    the runtime's PR tool"); remove `gh pr create` from skill text or gate it
    on `gh auth status`.
16. **Bus hygiene.** `research-status` prints the unread count per role;
    messages carry a `ttl`; `agent_bus.py inbox` defaults to a one-line
    digest. If receipts stay below 20% after that, stop requiring pointer
    messages at archive time — a message nobody reads costs a write and a
    read budget for nothing.
17. **Handoff returns.** 278 handoffs have no return. Add a validator warning
    for a dispatched `TASK-*` older than N days with no receipt and no
    superseding correction, surfaced in the portfolio health sweep as its own
    bucket.

## 5. What this review does not claim

- No statement here is evidence for or against any cryptographic hypothesis;
  the 29 `supported` hypotheses are not evaluated on their merits.
- Conversion rates are by literal-ID mention and over-count genuine
  provenance (a `dominated_by` cross-reference counts as a mention), so the
  true proposal→evidence rate is at most 7%.
- Token costs are inferred from bytes and word counts; no provider usage
  counters exist for the sessions in question, which is item P2.11.
- The per-month tables date records by the date in their identifier or
  `recorded_at`; 643 hypotheses and 392 evidence records carry neither and are
  excluded from the monthly rows but included in the totals.

## 6. Checklist

- [ ] P0.1 approval capacity gate (validator warning → error)
- [ ] P0.2 runnable-at-approval in `design-experiment`
- [ ] P0.3 decision-aware readiness-first selector; `/run` may publish
- [ ] P0.4 additive amendment bounding "designed, not shelved"
- [ ] P0.5 pre-written-outcome validator check
- [ ] P1.6 instruction diet with word budgets in CI
- [ ] P1.7 goal-head/`next_action` caps, `--ready-only` render, cached health
- [ ] P1.8 generated ledger indexes
- [ ] P1.9 remove ceremony fields from templates
- [ ] P1.10 proposal size cap
- [ ] P2.11 session receipts
- [ ] P2.12 eval harness baseline + weekly run
- [ ] P2.13 `tune-skill` round 1
- [ ] P2.14 portfolio KPIs in `/research-status`
- [ ] P3.15 stale identifier/PR instructions
- [ ] P3.16 bus hygiene
- [ ] P3.17 handoff-return warning
