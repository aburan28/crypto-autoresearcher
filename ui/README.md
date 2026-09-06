# `ui/` — a read-only dashboard over the research corpus

Published to **GitHub Pages** on every push to `main`, and servable
locally against the working tree:

```sh
make ui                       # live, http://127.0.0.1:8787
make ui-build                 # static, ./site (gitignored, ~125 MB)
python3 -m http.server -d site 8080
```

Standard library plus PyYAML, which the repository already depends on. No
`npm`, no bundler, no CDN, no new entry in `pyproject.toml`: this runs in
an offline container, which is where most of this program's sessions
actually run.

## One app, two hosts

GitHub Pages serves files; it cannot answer a query. So **nothing asks
one.** `ui/payloads.py` defines a file-shaped data contract,
`ui/build.py` writes it out and `ui/server.py` computes the same bytes on
request, and the browser does every filter, sort and search itself over
`data/index.json` (~0.8 MB gzipped). The published site and the local
server run the same `app.js` against the same paths.

Two products that disagree about their own data are one product and one
bug, so the contract lives in one module and the tests build a fixture
site and check it file by file.

Three differences remain, and they are the ones that cannot be otherwise:

| | live (`make ui`) | published snapshot |
| --- | --- | --- |
| `data/meta.json` `mode` | `live` | `static`, with commit and build time |
| record source text | inlined from disk | linked to GitHub at the built commit |
| refresh | `POST api/refresh` re-reads the corpus | rebuilt by CI on the next push |

**The published site is a snapshot and says so.** A banner on every view
names the commit and the build time and links to it. A reader comparing
the page against their working tree has to know which commit they are
looking at; a static page that implied freshness would mislead on exactly
the point that matters.

Source text is deliberately not bundled: 116 MB of YAML would triple the
site for bytes that are one click away on GitHub, permalinked to the
built commit and syntax-highlighted there. Full-text search over record
bodies is opt-in and loads per-kind excerpt shards on demand — the whole
set is ~3.8 MB gzipped and two thirds of it is the literature corpus,
which most searches do not need.

Knowledge entries are the one exception, and a deliberate one: a markdown
entry's body *is* the entry, and a finding's page that showed a title and a
link to GitHub was not a page. Each `data/records/KN-*.json` carries the
entry's body (~16 MB across ~8,000 entries, fetched one page at a time);
YAML records still carry only their parsed form.

The built `index.html` references `app.js?v=<commit>` and `app.css?v=<commit>`.
Pages lets a browser keep an asset for ten minutes, and a reloaded page
pointing at a bare `app.js` ran the previous deploy's client against the
new deploy's data. With the commit in the reference, a deploy always shows
its own client.

## Publishing

`.github/workflows/pages.yml` builds and deploys on every push to `main`
that touches `ledger/`, `experiments/`, `knowledge/`, `ui/` or the ECC
policy, plus a daily run and `workflow_dispatch`. It runs the UI tests,
builds, and refuses to deploy a site with fewer than 100 records, a
missing entry file, or one over the 1 GB Pages limit — an empty build
must not replace a working page.

**One-time setup:** *Settings → Pages → Build and deployment → Source:
**GitHub Actions***. Until that is set the workflow builds and then fails
at the deploy step.

The output (`site/`) is gitignored, like `knowledge/INDEX.md` and the
dispatch plans: it is derived byte-for-byte from committed files, and
committing it would add the whole corpus to the repository a second time
in a form that changes on every merge.

## What it is for

`/research-status` answers "what is the state of the program?" once, in
prose, by spending a model's turn on it. This answers the same question
continuously, for free, and it answers the questions that follow — *which
records cite this evidence? what does this goal's next action refer to?
which identifiers are cited but do not exist?* — which prose cannot,
because they are navigation, not summary.

It reads `ledger/`, `experiments/` and `knowledge/` directly. It is not a
second source of truth and holds nothing of its own.

## The views, in the order a reader asks

- **Overview** — what the program has established, what it is working on,
  and what is still open, with the program's own loop as a row of counts
  (questions → proposals → hypotheses → experiments → runs → evidence →
  decisions → findings). Each count carries the qualifier that keeps it
  honest: how many hypotheses reached a verdict, how many experiments ever
  ran, how much evidence points anywhere.
- **Findings** — the promoted findings (`knowledge/findings/`), grouped
  under the research area they are filed in with that area's goals beside
  the heading, each with its proof status, claim tier, the statement
  excerpted from its own body and what it says it does *not* claim; a
  **By area** table of every research area (goals, findings, hypothesis
  verdicts, evidence polarity, open problems, latest finding); the
  hypotheses that reached a verdict; every evidence record with a
  direction; the obstructions recorded as measurements; and the open
  problems. This is the board for "what did it find?".
- **Goals** and a goal page with its record trail: every finding, evidence
  record, decision, hypothesis and experiment that cites the goal, grouped.
- **Experiments**, with run tallies by terminal status.
- **Records** — a faceted browser over everything, by kind, area, knowledge
  family and status, with opt-in full-text search.
- **Integrity** — what is broken, flagged and never fixed.

A record page leads with an *at a glance* block — the fields that say what
the record is (an evidence record's direction, strength, tier and proof
status; a decision's verdict, targets and knowledge promotion; a hypothesis'
statement and status) — above the full parsed tree. A knowledge entry page
renders the entry itself.

### Findings, exactly

`knowledge/findings/` and `knowledge/open-problems/` are parsed exactly, like
goals: ~130 small markdown files whose front matter a reader will act on.
The statement shown on a card is excerpted from the entry's own body — the
section its author labelled as the finding, and within it a blockquote if
there is one, which is the corpus convention for "the finding, in one
sentence" — clipped, never paraphrased. A finding names its goal in about
half the corpus; the rest are attributed through the evidence or decision
that promoted them, and the board says "goals named", not "owner". Each
finding and open problem is *filed* under one area — its goal's, or the
first record it cites — so the By-area table counts nothing twice, while
`areas` keeps every area its citations reach for filtering.

The **not claimed** line on a card is the entry's own boundary section
("Not claimed", "Non-claims", "Limits", "What this says, and what it does
NOT say"), because a claim shown without its boundary is the overclaim the
program's rules exist to prevent.

Evidence `direction` has four values in the schema and about forty spellings
in the records (`supports_with_caveat`, `weakening_scoped`,
`refutes_own_prior_reading`). The board folds them into four for grouping
and colour — *supports*, *weakens*, *mixed*, *neutral* — and always shows the
author's exact word beside the colour. Most evidence is neutral and most
hypotheses never reach a verdict; the counts say so.

An **obstruction** is a negative result recorded as a measurement
(`evidence.obstruction` in `templates/research-records.md`): what blocks an
approach, as a quantity over a stated scope. It lives nested inside an
evidence record, below what the shallow scan can see, so the few dozen
records that carry one are parsed exactly and listed with whether the
reversal — the block read as a resource — was examined.

## What it will not do

**It writes nothing.** Not a ledger record, not coordination state, not a
derived index on disk, not a `__pycache__` entry. `tests/test_ui_index.py`
asserts this by stat'ing every file in a fixture repository before and
after a full build, deep scan, record read and search.

That is a design constraint, not a missing feature. Only the Coordinator
changes hypothesis status or approves experiments (AGENTS.md rule 1);
records are immutable and corrections supersede rather than overwrite
(rule 2). A dashboard that could edit them would be a second, unauditable
path into state that the whole program is built to keep auditable. So the
integrity page **flags and never fixes**, and there is no POST endpoint
except `/api/refresh`, which re-reads the corpus.

## Two tiers, and why

The ledger is ~5,600 YAML records and ~82 MB. PyYAML's pure-Python loader
parses all of it in **about 55 seconds**; reading the same bytes takes
**about 0.6**. A dashboard that paid 55 s before showing anything, and
re-paid it on refresh, would not get used. So:

| tier | what | cost | what it drives |
| --- | --- | --- | --- |
| 1 | `ui/scan.py` shallow header scan of every file | ~10 s | lists, boards, search, the link graph |
| 2 | `yaml.safe_load` of one record, cached | instant | every detail view |

Tier 1 is line-oriented and therefore approximate. It is not assumed to be
correct — `tests/test_ui_index.py::test_shallow_reading_agrees_with_the_exact_parse`
parses a sample of the real ledger both ways and asserts the agreement rate,
so a record shape the scanner cannot read shows up as a failing test rather
than as blank rows in the browser. A value the shallow parser cannot
represent is reported as *structured*, never guessed at.

A record detail view carries a **`parsed`** badge when its body came from
tier 2. A record that does not parse says so, in red, and links to its
source.

Two things are deliberately exempt from tier 1:

- **Goals** are fully parsed at startup. There are ~100, they carry the
  numbers a reader acts on (budget, completion criteria, impediments), and
  the portfolio board is the view most likely to be trusted without opening
  the record.
- **The unparseable sweep** is an exact parse of the whole ledger and runs
  in a background thread after the server is already answering. Until it
  finishes the integrity page says *not yet measured* rather than showing
  zero — reporting a clean sweep that has not happened is the failure
  AGENTS.md rule 5 names.

## What it knows about the program's rules

The dashboard reads three rules out of `CLAUDE.md` and shows them, rather
than leaving a reader to check by hand:

- **Rule 11, ECC comes first.** ECC goals sort ahead of everything else on
  every board, and are tagged. The area set is read from
  `orchestration/research-priority.yaml` through `tools/ecc_priority.py` —
  it is **never** inferred from an identifier prefix. If that module cannot
  be loaded, ECC ordering is switched off and the integrity page says so,
  rather than the UI guessing a set.
- **Rule 11, ECC budgets are unlimited.** An active ECC goal with a bounded
  `maximum_batches` or `total_wall_clock_seconds` is flagged.
- **Rule 10, goals are never paused.** A goal whose status is `paused` or
  `blocked` is flagged by name. Impediments are shown as impediments — a
  campaign carrying one is still active.

## Identifier linking

Every program identifier in free text becomes a link **if a record with
that identifier exists**. One that resolves to nothing stays plain text,
which is how a dangling reference makes itself visible while you are
reading rather than only in a report.

Both identifier forms link: the random-token form (`GOAL-AUXIN-a93442`)
and the legacy three-digit form (`GOAL-ECDLP-001`). Legacy records are
immutable, must never be renamed, and are most of this program's history.

The second segment of an identifier is an area token for most kinds but a
**date** for `DEC-`, `IDEA-`, `TASK-` and `CORR-`, and a bare token for
`BATCH-`. Both `ui/scan.py:RECORD_ID_RE` and `ui/static/app.js:ID_RE`
encode that; they must stay in step. For `KN-` it is the entry's **family**
(`FIND`, `OPEN`, `TECH`, `LIT`): families are not research areas and get
their own facet, so 7,900 literature entries no longer sit in the area
filter under an area called `LIT`.

## The data contract

Everything the page renders is a plain JSON file, at the same path in
both hosts. Programmatic consumers can read them the same way the
browser does.

| path | contains |
| --- | --- |
| `data/meta.json` | mode, commit, build time, counts, ECC area set, facets |
| `data/index.json` | every record as a positional row — see `meta.columns` |
| `data/overview.json` | portfolio summary, ECC-first goals, recent records |
| `data/goals.json` | the goal board |
| `data/goals/<id>.json` | one goal: checkpoints, criteria, impediments, bound records |
| `data/records/<id>.json` | parsed body, link ids in and out, source path; a knowledge entry also carries `markdown` |
| `data/experiments.json` | contracts with run tallies by terminal status |
| `data/findings.json` | findings with excerpts and attribution, hypothesis verdicts, evidence rows with direction and polarity, obstructions, open problems |
| `data/integrity.json` | unparseable records, duplicate ids, dangling refs, goal flags |
| `data/search/<KIND>.json` | body excerpts for full-text search, per kind |
| `POST api/refresh` | live server only: re-read the corpus from disk |

Rows in `data/index.json` are positional rather than objects because at
14.6k records the repeated key names cost more than the values: 2.6 MB as
objects, 1.4 MB as rows. `meta.columns` names them.

The local server binds to loopback by default. There is no
authentication because there is nothing to authenticate: every handler
reads.

## Layout

```
ui/
  scan.py      shallow header scanner; the identifier grammar
  index.py     the in-memory index: records, links, goals, experiments, integrity
  payloads.py  the data contract, shared by the server and the builder
  server.py    stdlib HTTP server; computes the contract live
  build.py     writes the same contract out as a static site
  static/      index.html, app.css, app.js — vanilla, no dependencies
tests/test_ui_index.py
.github/workflows/pages.yml
```
