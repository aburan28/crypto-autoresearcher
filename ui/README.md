# `ui/` — a read-only dashboard over the research corpus

```sh
make ui                       # http://127.0.0.1:8787
python3 -m ui --port 9000 --open
```

Standard library plus PyYAML, which the repository already depends on. No
build step, no `npm`, no CDN, no new entry in `pyproject.toml`: this runs
in an offline container, which is where most of this program's sessions
actually run.

## What it is for

`/research-status` answers "what is the state of the program?" once, in
prose, by spending a model's turn on it. This answers the same question
continuously, for free, and it answers the questions that follow — *which
records cite this evidence? what does this goal's next action refer to?
which identifiers are cited but do not exist?* — which prose cannot,
because they are navigation, not summary.

It reads `ledger/`, `experiments/` and `knowledge/` directly. It is not a
second source of truth and holds nothing of its own.

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
encode that; they must stay in step.

## HTTP API

Everything the page renders is available as JSON.

| endpoint | returns |
| --- | --- |
| `GET /api/status` | build state, counts, resolved ECC area set |
| `GET /api/overview` | portfolio summary, ECC-first goals, recent records |
| `GET /api/goals`, `/api/goals/<id>` | the board; one goal with checkpoints and bound records |
| `GET /api/records?q=&kind=&area=&status=&limit=&offset=` | filtered search |
| `GET /api/records/<id>` | parsed body, raw source, links in and out |
| `GET /api/ids` | every identifier the index holds |
| `GET /api/experiments` | contracts with run tallies by terminal status |
| `GET /api/integrity` | unparseable records, duplicate ids, dangling refs, goal flags |
| `GET /api/facets` | kind / area / status counts |
| `POST /api/refresh` | re-read the corpus from disk |

Loopback by default. There is no authentication because there is nothing
to authenticate: every handler reads.

## Layout

```
ui/
  scan.py      shallow header scanner; the identifier grammar
  index.py     the in-memory index: records, links, goals, experiments, integrity
  server.py    stdlib HTTP server, JSON API, static files
  static/      index.html, app.css, app.js — vanilla, no dependencies
tests/test_ui_index.py
```
