# ECDLP lead atlas

**What this program has already tried against the elliptic-curve discrete log,
one mechanism family per file, across all four repositories. It is written so
that a fresh clone answers "has this been done?" by computation, not by
re-reading 280,000 files.**

The known-results map (`knowledge/frontiers/ecdlp/`) records what the
*literature* established. This atlas records what *we* did: each lead's
disposition, the obstruction that closed it or the next step that would decide
it, and the evidence in `crypto-autoresearcher`, `crypto`, `cryptanalysis` and
`ecc-challenges`.

```sh
python3 tools/lead_atlas.py --brief          # what the session-start hook prints
python3 tools/lead_atlas.py --match "idea"   # leads and KR rows an idea collides with
python3 tools/lead_atlas.py --delta          # watched paths changed since the last review
python3 tools/lead_atlas.py --coverage       # ECDLP ledger records with no lead
python3 tools/lead_atlas.py --check          # CI (make check-ledger)
python3 tools/lead_atlas.py --render --out knowledge/leads/ecdlp/ATLAS.md
python3 tools/lead_atlas.py --stamp <session> # close a review: pin every repo's HEAD
```

## Why it exists

At the first 2026-10-24 review the ledger held 2,049 ECDLP-area hypotheses and ideas. 971 of its
1,031 hypotheses (94%) had no terminal status. Every new session re-surveyed the same ground, and idea generation
re-proposed mechanisms that an earlier lane had already measured or closed. The
known-results map stops re-derivation of *published* results. Nothing stopped
re-derivation of *our own*.

The later 2026-10-24 coverage reconciliation maps 2,078 current records. Its
29 new mappings and two open transfer leads are recorded in
`docs/reports/ecdlp-lead-atlas-20261024/coverage-20261024-mapping-review.json`.
`REVIEW_STATE.json` still identifies the earlier four-repository review; coverage
alone does not certify a fresh review of every changed sibling path.

## What "already done" means

`REVIEW_STATE.json` pins the commit of each repository at the last completed
review. `--delta` lists the watched paths (ledger records, ideas, findings,
problem records, research notes, leaderboards) added or modified since those
commits. The session-start brief combines that with the tallies:

- **nothing new since review**: every lead and every idea in the four
  repositories has been examined. The work is the open leads' `next_action`s,
  or a genuinely new lead that `--match` does not find.
- **changed since review**: fold the listed paths into leads (skill
  `lead-atlas`), then `--stamp`.

The atlas is **saturated** when three gates hold together: no lead is
`open_unexamined`, every ECDLP ledger record maps to a lead in `coverage.tsv`,
and nothing has changed since the review. Saturation is a reporting state. It
pauses no goal (AGENTS.md "Goals are never paused"), and open next steps remain
work.

## Layout

```text
knowledge/leads/ecdlp/
  README.md               this file
  REVIEW_STATE.json       commits examined, date, reviewer, tallies (--stamp writes it)
  coverage.tsv            <ledger record id> TAB <lead id | NONE>, every ECDLP H-* and IDEA-*
  ATLAS.md                GENERATED (gitignored): --render
  <family>/LEAD-<FAM>-<slug>.yaml
```

Families: `generic` (RHO), `ic-binary` (ICB), `ic-engine` (ICE), `ic-prime`
(ICP), `transfer` (TRF), `structure` (STR), `exotic` (EXO).

## Row schema

```yaml
id: LEAD-ICB-frobenius-invariant-factor-base
family: ic-binary
title: one line
mechanism: what it does and why it could help
disposition: open_next_step   # see below
obstruction:                  # required for closed_* and exhausted_at_scale
  kind: measured              # theorem | proof | measured | literature | cost_model
  statement: the precise reason, with scope
  revisit_when: the condition that reopens it
next_action:                  # required for open_*
  step: the concrete next experiment or proof obligation
  discriminates: what each outcome decides
  blocked_by: problems/x.md   # open_blocked only
best_measured: "S_IC/S_rho = 5.23x at log2 r = 36.6 (Table A)"   # or null
evidence:                     # >= 1; paths are checked
  - {repo: crypto, path: docs/ic/LEADERBOARD.md, note: one line}
ledger_refs: [H-FROB-..., DEC-..., EV-...]   # must exist under ledger/
known_results: [KR-IC-...]                   # must exist in the known-results map
related: [LEAD-...]                          # optional
dominated_by: LEAD-...                       # closed_dominated only
forecloses: [>= 3 phrases an idea would use when re-proposing this]
areas: [FROB, QSP]
last_reviewed: 2026-10-24
```

Dispositions:

| disposition | meaning |
|:--|:--|
| `closed_obstructed` | a named theorem, proof or controlled measured scaling shows it cannot beat the matched baseline in scope |
| `closed_known` | a literature result (KR or KN-LIT) the program reproduced; nothing new in scope |
| `closed_dominated` | works, but another lead (`dominated_by`) strictly dominates it |
| `exhausted_at_scale` | measured across the reachable range with controls, no improvement, no named mechanism left; `revisit_when` names the scale that reopens it |
| `open_next_step` | a concrete, runnable, discriminating next step exists |
| `open_blocked` | the next step is known but blocked (`blocked_by`) |
| `open_unexamined` | ideas exist; no experiment or evidence has touched it |

## Rules

1. **A closure names its obstruction** (AGENTS.md "Research direction":
   premature closure fails like overclaiming). A null or timed-out search is
   not an obstruction; use `exhausted_at_scale` with the scale reached, or an
   open disposition.
2. **The atlas changes no research state.** A disposition cites the decision,
   evidence or known-result row that decided it; hypothesis, experiment and goal
   statuses move only by Coordinator decision records.
3. **Rows are curated and editable.** A review updates `disposition`,
   `next_action`, `evidence` and `last_reviewed` in place; git keeps the history.
   Never delete a lead: a lead absorbed into another becomes `closed_dominated`
   or names the successor in `related`.
4. **Every ECDLP idea names its lead.** From IDEA-20261025-* on, an idea whose
   `prior_art.frontier_map` is an ECDLP map carries `prior_art.lead`: a LEAD id
   it advances, or `new` with `new_lead_reason` saying why `--match` found
   nothing (`tools/validate_ledger.py`). A new lead is added to the atlas in the
   same PR as the idea.
5. **Gaps to rho are distance remaining**, never pass or fail (AGENTS.md "Every
   improvement is a success"). Superseded leaderboard wins are not results.
