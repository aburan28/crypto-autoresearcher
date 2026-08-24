---
name: tune-skill
description: >-
  Propose a reward-guided textual revision to another skill's instructions
  (and its dispatched agent contract, if any), using that skill's own
  downstream ledger records as the reward signal. Standalone prototype: reads
  ledger/experiments state but writes no ledger record and holds no
  Coordinator authority — every diff is a normal code change a human approves
  before it is applied. Use when asked to tune, improve, or "RL" a skill's
  prompt against its track record, e.g. `/tune-skill propose-ideas`.
---

# Tune skill

Treats a target skill's instruction file as a policy: gathers the batch of
ledger records it has produced since the last tuning round, scores that batch
on decisiveness (not on whether it was "right"), and asks an agent to propose
a minimal, citation-backed diff to the instructions. A human approves before
anything is applied. Nothing here writes to `ledger/`, changes a hypothesis
or goal status, or claims Coordinator authority — it edits files under
`.claude/skills/` and `agents/` exactly like any other code change, so normal
git/PR review is the only gate. See the conversation this came out of for the
alternative, ledger-integrated design (an `RQ-META-*` campaign) if this
prototype proves useful enough to graduate into the program's own governance
model instead of living beside it.

**Scope of applicability.** This reward chain only exists for skills whose
output is a record with a gradable downstream outcome:

| skill | output record | downstream chain |
| --- | --- | --- |
| `propose-ideas` | `IDEA-*` (`ledger/proposals/`) | → `H-*` → `EXP-*` → `EV-*` → `DEC-*` |
| `design-experiment` | `H-*` status change + `EXP-*` contract | → `EXP-*` → `EV-*` → `DEC-*` |
| `run-experiment` | run records under `experiments/EXP-*/` | → `EV-*` → `DEC-*` |
| `review-evidence` | `EV-*` + `DEC-*` | (terminal — score its own `strength`/`knowledge_promotion` choices against later corrections, if any) |

For anything else in `.claude/skills/` (`deep-research`, `research-status`,
`curate-knowledge`, `coordinate-research-goal`, `agent-bus`,
`launch-research-harness`) there is no single graded output record to chain
from — refuse, and tell the user this prototype only covers the four skills
above.

## Steps

1. **Resolve target and files in scope.** Take the skill name from the
   command args (`/tune-skill <skill-name> [--since <date-or-commit>]`).
   Confirm it's one of the four skills above; if not, stop and say so. Read
   `.claude/skills/<skill-name>/SKILL.md`. If its text dispatches a
   subagent ("Dispatch the **X** subagent"), also read `agents/X.md` — both
   files are in scope for the diff, since instructions live in either place.

2. **Ground against `origin/main` and find the batch window.** `git fetch
   origin`. List `coordination/skill-tuning/<skill-name>/round-*.yaml`
   (create the directory if this is the first round for this skill); if any
   exist, sort by `round.decided_at` and read the latest's
   `round.batch_window.until` as the cutoff. Otherwise use `--since` if
   given, else no lower bound (full history). Record the resolved window
   (`since`, and `until` = `origin/main` HEAD sha) — this is what makes
   rounds composable instead of re-scoring the same records twice.

3. **Collect the batch.** Per the table above, find every output record of
   the target skill dated inside the window, then walk the chain forward.
   **Structured fields alone under-count badly** — a dry run against
   `propose-ideas`'s full history (799 ideas) found only 2 terminal outcomes
   via fields alone, versus at least 5 once free-text matching was added
   below, and every free-text match checked was hand-verified as genuine
   provenance, not an incidental mention. Do both passes, in this order:
   - **Structured pass.** `IDEA-*` → `H-*`: grep `ledger/hypotheses/*.yaml`
     for `proposal_id: <id>`, `source_idea_id: <id>`, **and** `idea_id:
     <id>` — the corpus uses all three field names inconsistently, and
     checking fewer silently drops records. `IDEA-*` → `EXP-*` directly:
     grep `experiments/EXP-*/specification.yaml` for `derived_from_idea:
     <id>` — many experiments carry this even when `hypothesis_id: null`,
     i.e. they skip the hypothesis link entirely; missing this path alone
     was the largest single source of undercount in the dry run. `H-*` →
     `EXP-*`: grep for `hypothesis_id: <id>`. `H-*`/`EXP-*` → `EV-*`: grep
     `ledger/evidence/*.yaml` for matching `hypothesis_id` and
     `experiment_ids`. `EV-*` → `DEC-*`: grep `ledger/decisions/*.yaml` for
     the `EV-*` id in `evidence_refs` (more reliable than `target_ids`,
     which mixes record types).
   - **Free-text fallback pass.** For every idea not yet resolved to a
     terminal `EV-*` by the structured pass, grep its literal ID
     (`IDEA-YYYYMMDD-<tok>`) across `ledger/hypotheses/`, `experiments/`,
     `ledger/evidence/`, and `ledger/decisions/`. A hit in an `EV-*` or
     `DEC-*` file is a candidate terminal outcome — read the surrounding
     text before trusting it, since a mention can be a comparison or
     cross-reference (e.g. "dominated_by IDEA-X") rather than provenance.
     Tag which pass found each match (`structured` vs `free_text`) in the
     batch table; free-text matches carry more review burden and should
     stay visibly distinguishable, never silently merged with structured
     ones.
   Every batch item ends in one of: a terminal `EV-*` (has `strength`), still
   in-flight (reached `H-*`/`EXP-*` but no `EV-*` yet — exclude from scoring,
   count separately as coverage), or never picked up at all (no downstream
   record by either pass — same treatment). Do this gathering directly; it's
   grep and read, no agent needed.

4. **Score the batch — decisiveness, not correctness.** For each item with a
   terminal `EV-*`, map `strength` to a reward:

   | `strength` | reward | why |
   | --- | --- | --- |
   | `strong`, `replicated` | +2 | minimal test actually discriminated |
   | `preliminary`, `anecdotal` | +1 | discriminated, weakly |
   | `inconclusive`, `contradictory` | 0 | test failed to resolve, or wasn't reproducible |

   **Any `strength` value outside this table is `unscored`, not `0`.** The
   dry run against `propose-ideas` found live evidence records using `n/a`
   (the majority of the free-text-matched sample) and `moderate` (a whole
   MLKEM chain), neither of which appears in `templates/research-records.md`'s
   documented six-value enum. Do not silently drop these and do not fold
   them into the histogram at any score — list each in its own `unscored`
   bucket with the literal value seen, so schema drift in the corpus stays
   visible instead of quietly shrinking the batch. An item with only
   `unscored` evidence counts toward coverage but never toward the
   thin-data threshold in step 5.

   **Explicitly ignore `direction`** (`supports`/`weakens`/`contradicts`/
   `neutral`) in the score. Rewarding `supports` outcomes would train the
   generator toward safe, easily-confirmed proposals and away from genuinely
   uncertain high-value ones — the premature-closure failure mode
   `AGENTS.md` rule 9 already names. A decisive falsification scores the same
   as a decisive confirmation. Also tabulate, as diagnostics only and never
   as reward inputs: coverage (fraction of the batch that ever reached
   `EXP-*`), and any `DEC-*` `rationale`/`limitations` text in the chain that
   flags an overclaim, undisclosed `dominated_by`, or missing
   `heuristic_assumptions` — these are evidence for the diff, not points
   against the score.

   **Known gap:** whether an idea was bounced back for schema incompleteness
   (`propose-ideas` step 4) leaves no ledger trace, so this signal cannot be
   reconstructed for historical batches — only noted here as future work
   (e.g. the skill could log bounce counts itself going forward).

5. **Build the tuner prompt.** Assemble: the full current text of the
   skill file (and agent contract, if applicable); the scored batch as a
   table of record IDs with short excerpts (`claim`/`mechanism` snippet,
   terminal `strength`+`direction`, any flagged `DEC-*` rationale); the
   window and coverage stats; and these hard constraints for the agent:
   - Propose a **minimal, targeted diff** — specific sentences or bullets
     added/changed/removed, not a rewrite.
   - **Cite the specific record IDs** from this batch that motivate each
     change. A proposed change with no citation is not eligible to include.
   - **Do not optimize toward `support` decisions** or toward any specific
     target/area being proposed more or less often — if a change would shift
     *which* questions get proposed against rather than *how clearly* a
     proposal is specified, it must independently justify itself against the
     `docs/inventor-protocol.md` §4 premature-closure standard, not against
     the decisiveness score alone.
   - **State if the batch is too thin to act on** (rule of thumb: fewer than
     5 *scored* terminal items — `unscored` items from step 4 don't count
     toward this — or concentrated in a single `RQ-*`/area) and recommend no
     change rather than a confident-sounding diff on noise.

6. **Dispatch a general-purpose agent** with that prompt, read-only against
   the repo (instruct it explicitly not to edit or write any file — it
   returns a diff as text plus a short rationale, it does not apply one).
   `run_in_background: false` — the next step needs its output immediately.

7. **Present to the user.** Show the proposed diff, its rationale with
   citations, the batch table, and the reward summary. This is the approval
   gate — do not apply anything automatically, and do not treat a prior
   approval of a different round as standing approval for this one.

8. **On approval, apply and record.** Edit the skill/agent file(s) with the
   approved diff. Mint a round id with
   `python3 -c "import secrets; print('round-' + secrets.token_hex(3))"` —
   a minted token, not a scanned "next free number" (`CLAUDE.md`
   "Concurrency"): two worktrees tuning the same skill must not collide.
   Write `coordination/skill-tuning/<skill-name>/<round-id>.yaml`:

   ```yaml
   round:
     id: <round-id>
     skill: <skill-name>
     files_changed: []
     batch_window: {since: null, until: null, origin_main_sha: null}
     batch_items: []          # record IDs considered, with terminal status
                              # and match_method: structured | free_text
     reward_summary: {terminal_n: 0, in_flight_n: 0, uncovered_n: 0,
                       unscored_n: 0, unscored_values: [],
                       histogram: {plus2: 0, plus1: 0, zero: 0}}
     diff_summary: null       # prose summary; the diff itself lives in the commit
     decision: applied | rejected | deferred
     rationale: []
     caveats: []              # e.g. "batch below thin-data threshold"
     decided_by: user
     decided_at: null
   ```

   If the user rejects or defers, still write the round record with
   `decision: rejected` / `deferred` and no `files_changed` — a null result
   is still a result, and the next round's window should start after it
   either way.

9. **Commit and push as a normal code change.** One commit covering the
   skill/agent file edit(s) and the round record, message referencing the
   round id. No ledger snapshot/archive step applies — this isn't a ledger
   record — but open a PR as usual so the diff gets the same review any other
   instruction change would.

## If this proves out

A round record's reward trend across several rounds is the "learning curve."
If it's actually moving decisiveness and the team wants this to carry real
authority (gate on Coordinator approval, cite as evidence, survive audit),
graduate it into the ledger as an `RQ-META-*` campaign over the skill file
instead of extending this prototype — that gets citation discipline,
immutability, and Coordinator sign-off for free instead of reimplementing
them here.
