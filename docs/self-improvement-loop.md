# The self-improvement loop

`tune-skill` treats a skill's instructions as a policy and the ledger as its
reward. On its own it is one step: a person picks a target, an agent
proposes a diff, a person approves it, and nobody checks whether the applied
diff helped. Both recorded rounds (`round-19a7fc`, `round-faba84`) stopped at
`deferred` for that reason. `tools/self_improve.py` closes the loop. The
loop itself is in `.claude/skills/tune-skill/SKILL.md`, "Loop mode". This
page gives the reasons and the limits.

Nothing here is evidence about ECDLP. Like `evals/`, it is evidence about the
harness (`docs/measuring-the-harness.md`) and never enters `ledger/`.

## The cycle

```text
plan ──► tune <skill> ──► guard ──► (discipline eval) ──► PR ──► human merge = applied
  ▲                                                                   │
  │                                                                   ▼
  └──── revert (if regressed) ◄── outcome record ◄── measure (once mature)
```

| action | when | writes |
| --- | --- | --- |
| `revert` | an outcome says `regressed` and nothing reverts it yet | a PR restoring the files, with a round that `reverts:` it |
| `measure` | an applied round's arms are mature, or it is past 90 days (censored) | `outcome-<tok>.yaml` |
| `tune` | no live round, and the window since the last round holds ≥ 5 scored items in > 1 area | `round-<tok>.yaml` + diff, on branch `skill-tuning/<skill>-<round>` |
| `wait_review`, `wait_outcomes`, `idle` | otherwise | nothing |

A round is **applied** when its record reaches `origin/main`. The applied
date is the first-parent commit that added it, so the tool needs neither the
GitHub API nor a mutable status field. An unmerged or closed PR leaves no
record on main. Its branch blocks the target for 30 days and then stops
blocking it.

## Recursion, and what it cannot touch

`tune-skill` is a target of itself. Its items are the outcome records of
object-level rounds (`improved` +2, `no_change_detectable` 0, `regressed`
−2), each dated by when the tuner *produced* the round, and each round
records `tuner_blob` (the git blob of the tune-skill file that wrote it). A
change to the tuner is therefore measured by whether the rounds written
after it improved the skills they touched more often than the rounds written
before it.

A loop that can edit its own reward will find that edit, which is the
standard reward-hacking failure. Its controls are mechanical, not
instructions to behave:

- **Allow-list write scope.** `guard` accepts only the target's files
  (`TARGETS`) plus *new* `round-`/`outcome-` records. The scorer
  (`tools/tune_skill_batch.py`), this loop, `orchestration/eval/`,
  `evals/`, `AGENTS.md`, the role and policy files are outside every scope.
  `agents/coordinator.md` is excluded even though `design-experiment`
  dispatches it: tuning a skill must not rewrite who approves what.
- **Frozen regions.** The reward table, the tuner's hard constraints and the
  loop gates sit between `<!-- frozen:NAME -->` markers in the tune-skill file.
  `guard` compares each region byte for byte against the merge base, and
  deleting the markers counts as a change.
- **Minimal diffs.** At most 60 changed lines across the target's files
  (generated mirrors excluded).
- **Discipline is not tradeable.** A diff touching a fingerprinted file
  (`orchestration/eval/fingerprint.py`, `TRACKED`) is `eval_required`, and a
  discipline regression ends the round (`docs/measuring-the-harness.md`, §3).
- **A person merges.** The loop opens PRs and never merges tuning.

## Measurement design

The question for each applied round is whether items produced under the new
instructions resolve more decisively than items produced under the old ones.
Three confounds would each produce a positive answer with no real effect.

1. **Age.** Post-change items are younger and have had less time to reach
   evidence. Fix: with `H` days since applying and horizon `h = H/2`,
   post items are those dated `[applied, today − h]` and pre items those
   dated `[applied − (H − h), applied)`. Each item is scored only on
   evidence dated within `h` days of itself
   (`tune_skill_batch.collect(evidence_horizon_days=h)`). Both windows have
   equal length and every item gets an equal horizon. Undated evidence is
   excluded from both arms.
2. **Program drift.** Areas, goals and reviewers change over the weeks. Fix:
   a difference in differences against the other object-level skill, used
   only when that skill had no applied round inside the windows. The two
   share a pipeline, so spillover biases the estimate toward zero. The
   outcome says so.
3. **Clustering.** Eleven `EXP-ALBIN-*` experiments score from one
   `EV-ALBIN-001`. Fix: a cluster bootstrap by area (10,000 draws,
   seeded), at least 5 scored items **and 4 clusters** per arm, otherwise
   `insufficient_data`.

A structured-match-only estimate is reported beside the main one as a
sensitivity check, because free-text matches are unreviewed candidates.

## Calibration: the placebo test

`self_improve.py placebo` measures fake rounds at dates where no instructions
changed. Every conclusive verdict there is a false positive of the
instrument. The checks above were found by running it, not designed up
front:

| instrument version | conclusive placebo verdicts | false positives |
| --- | --- | --- |
| item bootstrap (development, uncommitted) | 10 raw + 4 DiD, weekly 07-15..09-25 | raw 4/10, DiD 4/4 |
| + cluster bootstrap (development, uncommitted) | same dates | raw 1/10, DiD 2/4 (both from arms with 2 clusters) |
| + 4 clusters per arm (**this commit**) | every 3 days 07-01..09-30: propose-ideas 17 raw, 0 DiD; design-experiment 0 | **2/17 raw** (Wilson 95% [0.03, 0.34]) |

The development rows were measured on intermediate code versions that were
not committed and cannot be reproduced from this commit. The committed row
can: `docs/self-improvement/placebo-20261020/` holds the raw output, the base
commit and the commands
(`python3 tools/self_improve.py --today 2026-10-20 placebo --target <t>
--from 2026-07-01 --to 2026-09-30 --step-days 3`). Placebo dates three days
apart share most of their items, so 17 dates are far fewer than 17
independent trials. Both false positives are adjacent late-September dates
with horizons of 10–12 days: one episode. The thresholds were **not** tuned
further against this same data, since that would make the calibration
measure its own fit.

## What the calibration says about the loop

- **`design-experiment` is not measurable at today's throughput.** No
  placebo date in three months had 4 scored areas in both arms. Its rounds
  will mostly close as censored `insufficient_data` after 90 days. The loop
  still runs, but it cannot tell such a change from noise, and the curve
  says so instead of showing a trend.
- **`propose-ideas` is measurable,** with a false `regressed` rate that may
  exceed the nominal 5%. A false `regressed` costs a revert PR that a person
  reviews, not a lost change.
- **The meta level is far off.** Scoring `tune-skill` needs ≥ 5 outcome
  records on each side of a tuner change, which at roughly one measurable
  round per target per quarter means about two years. The recursion is
  wired and guarded but will be data-starved for a long time. The useful
  near-term output is the object-level learning curve
  (`self_improve.py curve`).
- **Throughput is the binding constraint, not the tuner.** Within a 20–30
  day horizon only about 5–24% of a window's items reach scored evidence.
  Raising that rate (more evidence reviews, dated evidence records) would
  speed every turn of the loop more than any instruction change.

## Running it

```sh
python3 tools/self_improve.py plan                       # what to do next, per target
python3 tools/self_improve.py measure <round> --write    # once mature; refuses to rewrite
python3 tools/self_improve.py guard --target <skill>     # before opening a tuning PR
python3 tools/self_improve.py curve                      # the learning curve
python3 tools/self_improve.py placebo --target <skill> --from <d> --to <d>
```

On a schedule, run `/tune-skill next` in a fresh session. Weekly is enough,
since outcomes mature over months. It is safe to repeat: one live round per
target, and every action short of `tune` either writes an immutable record
or does nothing.
