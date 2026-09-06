---
name: deep-research
description: >-
  Deeply analyze the whole research portfolio -- ledger, knowledge corpus, and
  literature -- and produce a ranked, justified shortlist of what experiments
  to run next. Dispatches idea-generator for fresh divergent candidates and
  the coordinator for portfolio-wide prioritization, with an optional
  red-team stress-test of the shortlist. Read-only: writes no ledger record
  and changes no status. Use when the user asks what to work on next, wants a
  research roadmap or priority ranking, a goal's next_action needs deeper
  justification than the mechanical fallback order, or before opening a new
  campaign against an open question.
---

# Deep research

Answer one question with rigor: **of everything this program could do next,
what is actually worth doing, and why?** This is not another status readout —
`/research-status` already gives the read-only ledger scan. This skill spends
real reasoning effort turning that scan, the knowledge corpus, and external
literature into a ranked, falsifiable, cost-aware shortlist, and defends it
against the two failure modes `AGENTS.md` and `docs/inventor-protocol.md` name
as symmetric: overclaiming a result, and prematurely closing a promising lead
(AGENTS.md rule 9; inventor-protocol §4).

**Read-only and side-effect-free.** This skill writes no ledger record,
changes no hypothesis or goal status, and commits nothing. It is safe to run
from any worktree, on any branch, at any time — no git hygiene, ID
pre-allocation, or snapshot/ledger archive is needed, because the output is a
report handed to the user (or fed into the Coordinator inside
`/coordinate-research-goal`), never a durable artifact by itself. Acting on a
shortlist entry still goes through `/propose-ideas`, `/design-experiment`,
`/run-experiment`, `/curate-knowledge`, or a Coordinator ledger archive,
exactly as it would without this skill.

## Scope

Take a scope from the user's request, in priority order:

1. An explicit `RQ-*`, `GOAL-*`, or `H-*` — analyze within that boundary.
2. "the active goal" / current branch context — resolve the same way
   `/launch-research-harness` step 3 resolves goal selection.
3. No scope given — analyze the whole portfolio. This is the expensive,
   comprehensive mode and is the default for a bare `/deep-research`.

State the resolved scope back to the user before dispatching any subagent.

## 1. Ground the scan in current committed state

Many worktrees write to this ledger concurrently (CLAUDE.md "Concurrency:
many agents, many worktrees"). A recommendation built on a stale local branch
can duplicate work another session already landed, or already has an open PR
for.

- `git fetch origin`, then read ledger and knowledge state as of
  `origin/main` (or `git merge-base HEAD origin/main`) rather than trusting
  an out-of-date local branch tip.
- `gh pr list --state open` and skim titles/bodies for record IDs that
  overlap the scope — an open PR may already be doing the work a naive scan
  would recommend.
- If the local branch carries uncommitted or unpushed records relevant to
  the scope (this branch's own in-flight work), fold them in and say so
  explicitly; they are real even though `origin/main` cannot see them yet.

## 2. Comprehensive context gathering (this session, read-only)

Do this directly — no subagent needed, exactly as `/research-status` does its
scan. Read broadly before ranking anything:

- **Governing docs**: `AGENTS.md` (rule 9 — good-faith pursuit, no
  suppressing a plausible lead without recorded evidence/budget/boundary/
  successor; rule 4 — scoping; rule 6 — citation discipline; rule 5 — no
  fabrication), `docs/target-result-profile.md` (Parts A-C, the C1-C18
  checklist), `docs/inventor-protocol.md` (all 8 sections),
  `docs/claims-and-verification.md`, `docs/task-lifecycle.md`.
- **Ledger, the whole tree**: `ledger/questions/`, `ledger/proposals/` (not
  yet converted to hypotheses), `ledger/hypotheses/` grouped by status,
  `ledger/evidence/`, `ledger/decisions/` (recent `next_actions`),
  `ledger/goals/` — including sharded goals under
  `ledger/goals/GOAL-*/{goal.yaml,checkpoints/*.yaml}` — and
  `ledger/handoffs/`. Grep the whole tree recursively
  (`grep -rl <term> ledger/ knowledge/`), never just the top-level
  `ledger/*.yaml` files: those are frozen legacy records covering a fraction
  of the area codes, and a top-level-only scan reports a clean "free" for an
  area that is in fact heavily worked.
- **Knowledge corpus, every subtype**: `knowledge/open-problems/` (read the
  "why it matters" / forward-guidance text on every `KN-OPEN-*` record in
  scope — this is the program's own list of promising, unresolved leads),
  `knowledge/findings/` (proven boundaries — what NOT to re-propose),
  `knowledge/techniques/`, `knowledge/literature/`.
- **Reconciliation flags** — grep goal records for `verdict: UNRESOLVED`,
  `unresolved_carried_forward`, and `what_would_settle_it`. These are
  pre-scoped, uncontended, already-justified units of work with acceptance
  criteria already written down by whoever raised them; treat each as a
  free-standing candidate before generating anything new, and verify its
  stated premise rather than inheriting it — a session that raised the flag
  by analogy can be wrong about the state it assumed.
- **Promotion-gate and validation debt**: hypotheses carrying an
  `asymptotic_claim` stuck below `supported` — check which of the four
  promotion gates (`agents/coordinator.md`; `docs/target-result-profile.md`
  Part D) are still open: archived proof decomposition, every heuristic
  validated or scheduled, a concrete-cost table, independent xhigh review.
  Also check hypotheses whose `heuristic_assumptions[]` carry an empty
  `validation_experiment_ids`, and proof-oriented hypotheses whose
  `proof_search_map` is null or has an unaudited field
  (`docs/inventor-protocol.md` §8). Discharging a named gate on existing,
  already-approved work is frequently higher-value and lower-risk than
  generating a new idea from nothing.
- **Knowledge retrieval (crypto-kb MCP)**: call `search_knowledge` and
  `find_related` for every candidate direction under consideration, per
  `AGENTS.md` "Knowledge retrieval policy" — this skill's entire purpose
  triggers that policy's "proposing an experiment likely to duplicate earlier
  work" and "asserting an avenue already tested" clauses. If the server has
  no index built (`:memory:` / empty), say so plainly rather than silently
  skipping novelty checks.

Build, in your own working notes (not committed anywhere), a frontier map per
live target problem in scope: current best internal/external result,
`dominated_by` and `sota_delta` as last honestly recorded (never assume
`null` without checking — `docs/inventor-protocol.md` §5), and which open
problems or findings bound it.

## 3. Divergent pass — fresh candidates (optional, dispatch idea-generator)

Skip this only when the scope already has more ready, ranked work than the
user's stated budget can cover (several approved-but-unrun hypotheses,
several open reconciliation flags) and the user wants ranking, not new ideas.
Otherwise dispatch the **idea-generator** subagent, giving it:

- the resolved scope, the frontier map from step 2, and which established
  families/objects are already exhausted per the corpus, so it applies
  `docs/inventor-protocol.md` §1's off-limits naming rather than regressing
  to a variant in new notation;
  for an ECDLP scope, the off-limits list and the object frame are already
  written down — paste the constraint block from
  `docs/object-frame-ideation.md` rather than restating them;
- an explicit instruction to run the lossy-projection test (§2) on every
  candidate before returning it — free, no compute, the cheapest available
  filter for "is this actually new";
- an explicit instruction that "this target looks saturated" is not by
  itself a reason to generate nothing (§4's premature-closure standard) — if
  it reaches that conclusion for part of the scope, it must meet the
  named-obstruction-plus-argument-plus-forward-guidance bar, not report a
  screened-and-rejected count as a closure.

Take its full output, including the mandatory §5 honest-accounting block
(`dominated_by`, `sota_delta`, enumerated closures, open directions) even
when it proposes nothing usable — a session that finds nothing still owes
that block.

## 4. Convergent pass — portfolio ranking (dispatch coordinator)

Dispatch the **coordinator** subagent — prioritization is its authority
(`AGENTS.md` "Roles"), and this step is where that authority earns its keep,
even though nothing here is written as an official decision. Give it:

- everything gathered in steps 1-3: the frontier map, reconciliation flags,
  promotion-gate debts, and the idea-generator's fresh candidates (if run);
- explicit instruction that this is **advisory synthesis, not a
  `coordinator_decision`**: no ledger write, no status change, no experiment
  approval — the deliverable is a ranked report only;
- the ranking rubric below, to apply explicitly per candidate rather than
  asserting a holistic order.

**Ranking rubric** — state each axis per candidate, do not just assert a
final order:

1. **Cost tier.** Free/cheap pre-compute audits first — the lossy-projection
   test, `proof_search_map`'s four audits, a reconciliation flag's named
   check, a controls-before-belief null-object run — before anything that
   needs a real experiment budget.
2. **Expected information gain vs. cost** — the idea-generator's own
   convention, applied portfolio-wide: what does a positive vs. negative
   outcome each teach, and does the minimal test actually discriminate
   between explanations.
3. **Gate/dependency unlock** — does this discharge a named promotion gate,
   validate a heuristic something else depends on, or unblock a hypothesis
   stuck at `specified`/`approved` for lack of exactly this?
4. **Target-profile ambition (C1-C2)** — exponent-moving mechanisms over
   logarithmic-cofactor or constant-factor polishing; a cofactor-level
   candidate is not excluded, but must justify its priority as a building
   block rather than being scored as if it were exponent-first.
5. **Pareto/SOTA honesty** — `dominated_by` checked against every frontier
   row, not defaulted to null; `sota_delta` stated quantitatively.
6. **Premature-closure check** — for any candidate the scan wants to drop, or
   any open problem the corpus already calls saturated, hold it to the §4
   closure standard before excluding it; a fatigue report is not a reason to
   deprioritize.
7. **Contention** — flag candidates already covered by an open PR found in
   step 1; prefer surfacing the uncontended alternative over recommending
   duplicate work.

## 5. Adversarial stress-test (optional, dispatch red-team)

For a portfolio-wide run, or whenever the top-ranked candidate would be
expensive, run one **red-team** pass against the top 3-5 shortlist entries
only. This is a deliberate extension of Red Team's normal trigger: it usually
reviews a Coordinator-committed snapshot of a *completed* result; here there
is no snapshot because nothing has run yet, so it is reviewing the
*prioritization reasoning itself*. Say this explicitly in its handoff, and
keep its authority unchanged — it may not approve, rank, or write any ledger
record; its output is a challenge memo the shortlist is weighed against, not
a gate that blocks anything.

Ask it specifically: which top candidate has a hidden assumption or omitted
cost; which "obviously next" pick is actually regression to an off-limits
established family under new notation; whether any `dominated_by: null` in
the shortlist was actually checked against every frontier row; whether any
proposed closure meets the §4 standard rather than being a fatigue report.

Fold surviving objections back into the shortlist — reorder or annotate; do
not silently drop a challenged entry without recording why it survived.

## 6. Report

Present, in this order:

1. **Resolved scope**, and the commit/PR state it was checked against.
2. **Ranked shortlist**, tiered (free/cheap pre-compute first, then highest
   information-gain, then fresh speculative candidates last). Each entry
   carries: target ID (existing `RQ-*`/`H-*`/`GOAL-*`/`KN-OPEN-*`, or `NEW`),
   a one-line description, the rubric axes from step 4 that drove its rank,
   its `dominated_by`/`sota_delta` line, and the exact next skill/command to
   run it (`/propose-ideas RQ-...`, `/design-experiment IDEA-...`,
   `/run-experiment EXP-...`, `/curate-knowledge KN-...`, or "feed to
   `/coordinate-research-goal` as `next_action` for `GOAL-...`").
3. **Red-team objections**, if run, and how each was resolved.
4. **One explicit top pick** — "if only one thing happens next, it is X,
   because Y" — mirroring the idea-generator's own single-pick convention.
5. **What this report is not**: no ledger record was written and no status
   changed; every recommendation still needs its normal lifecycle skill and,
   where applicable, Coordinator approval and a ledger archive commit before
   it is official.

## Rules

- Never fabricate a citation, a prior result, a cost estimate, or a
  `dominated_by`/`sota_delta` value; an unchecked `null` is a fabrication
  under `AGENTS.md` rule 5, in this report exactly as in a filed idea.
- Never treat "this looks saturated" as a valid reason to drop a candidate
  without meeting the `docs/inventor-protocol.md` §4 closure standard —
  rule 9 makes that the same failure as overclaiming.
- Never let this skill's own output be cited as evidence, an approval, or a
  status change. It is a pointer to work, not the work.
- Every candidate cites the exact record IDs or corpus paths it rests on; a
  shortlist entry with no citable basis is a guess, and must be labeled one.
- If the portfolio scan or the knowledge-retrieval step finds nothing usable
  in scope, say so plainly and name what would need to happen first (e.g. no
  open `RQ-*` in scope, or `crypto-kb` has no index built) rather than
  inventing a plausible-sounding shortlist.
