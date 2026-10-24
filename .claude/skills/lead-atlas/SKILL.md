---
name: lead-atlas
description: Review and maintain the ECDLP lead atlas (knowledge/leads/ecdlp/) - what this program has already tried against ECDLP across crypto-autoresearcher, crypto, cryptanalysis and ecc-challenges. Use at session start when the brief says something changed since the last review, before ideation, when asked whether an idea or lead has been done, or to bring the atlas to saturation (every record mapped, every lead dispositioned, nothing new since review).
---

# lead-atlas

The atlas makes "has this already been done?" a computed answer
(`knowledge/leads/ecdlp/README.md`). This skill is the review loop that keeps
the answer true. It changes no hypothesis, experiment or goal status. A
disposition cites the record that decided it (AGENTS.md "Research states").

## When the session-start brief says "nothing new since review"

Do not re-survey the repositories. The brief already establishes that every
lead and every idea was examined at the pinned commits. Pick the work from the
atlas:

1. `python3 tools/lead_atlas.py --render --out knowledge/leads/ecdlp/ATLAS.md`
   and read "Open next steps".
2. Take an `open_next_step` lead's `next_action` to `/design-experiment` or
   `/run`, an `open_blocked` lead's blocker to its problem record, or propose
   a NEW lead with `/propose-ideas`. A new lead must not appear in
   `--match`, or it must answer a closed lead's obstruction.

## When it says "changed since review"

1. `python3 tools/lead_atlas.py --delta` lists the watched paths added or
   modified in each repository since the pinned commits.
2. Read each new record by its summary (decision, evidence, CONCLUSION,
   README), not its raw logs. For each, decide:
   - it **advances an existing lead**: update that lead's `evidence`,
     `ledger_refs`, `best_measured`, and its `disposition` / `next_action` /
     `obstruction` if the record decided something. Set `last_reviewed`.
   - it **is a new mechanism**: add a lead row (README "Row schema"). Run
     `--match` first, because a near-duplicate belongs in the existing lead.
   - it **is not about ECDLP**: nothing to do. A ledger record still gets a
     `coverage.tsv` row with lead `NONE`.
3. `python3 tools/lead_atlas.py --coverage` shows ECDLP hypotheses and ideas
   without a lead. Append `<id>\t<LEAD-id>` rows to `coverage.tsv`, keeping
   the file sorted.
4. `python3 tools/lead_atlas.py --check` must pass.
5. `python3 tools/lead_atlas.py --stamp <session-or-agent>` pins every
   repository's HEAD as reviewed. Stamp only after steps 1-4 covered the whole
   delta. A partial review leaves the stamp alone and says what is left.
6. Commit the rows, `coverage.tsv` and `REVIEW_STATE.json` together. When
   dispositions changed, also refresh the atlas report and graph
   (`research-visuals`, "Deliverables for each search round";
   `docs/reports/ecdlp-lead-atlas-*/`).

## Closing a lead

A closure names its obstruction: a theorem, a proof, a controlled measured
scaling, a literature result, or a cost model with its units. A null or timed-out search is
`exhausted_at_scale` with the scale reached and the scale that reopens it, and
never `closed_obstructed`. Keep a lead open when in doubt. Premature closure
fails like overclaiming (AGENTS.md "Research direction").

## Saturation

The brief reports saturation when no lead is `open_unexamined`, every ECDLP
record is mapped, and nothing changed since review. Report it as such. It is
not a reason to stop a goal. The open next steps are still the work, and a
new lead is the most valuable thing a session can add.
