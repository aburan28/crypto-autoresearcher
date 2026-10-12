# Repo radar: cryptography repositories on GitHub

The [`repo-radar` workflow](../.github/workflows/repo-radar.yml) runs
[`tools/repo_radar.py`](../tools/repo_radar.py) at 06:41 UTC each day, with a
manual `workflow_dispatch` option. GitHub may delay a scheduled job. Each run
combines three sources into one digest:

| Source | What it finds | How |
| --- | --- | --- |
| **Search** | Repos created or pushed since the last run | GitHub repository search, one query per configured topic or keyword |
| **Followed repos** | New commits on the default branch, releases and tags | REST API, against a cursor saved from the previous run |
| **GH Archive** | Stars, forks, releases and repos made public yesterday | [GH Archive](https://www.gharchive.org), GitHub's public event stream saved hourly |

Search hits and archive leads are scored for relevance (below). The radar
remembers relevant repos, so a digest lists only what is new to it, star
jumps, and activity on followed repos. The first run records a baseline and
says so.

Each digest is committed to the orphan branch `automation/repo-radar` and,
if it contains anything, opened as an issue labelled `repo-radar`. Opening an
issue is what sends watchers an email. The previous digest issue is closed, so
the open one is always the latest and the closed ones form the archive. A
quiet day opens no issue. The radar is intake signal, never evidence: it
writes no ledger or knowledge record. A repo worth keeping goes through
`curate-knowledge` like any other source.

## Configuration

Everything is in [`orchestration/repo-radar.toml`](../orchestration/repo-radar.toml),
read on each run from `main`:

- `[search] topics` and `keywords` each run two queries a day (created since,
  pushed since). Broad ones go in `created_only`. `extra_queries` are used
  verbatim with `{since}` substituted. `ignore_owners` drops your own repos.
- `[scoring]` adds a weight per GitHub topic and per case-insensitive regular
  expression over the repo name and description. `[scoring.negative]`
  subtracts for cryptocurrency and promotion noise, so a Bitcoin-puzzle
  kangaroo solver still passes but a trading bot does not. Repos at or above
  `min_score` are reported. To see why a repo scores what it does:

  ```sh
  GITHUB_TOKEN=... python3 tools/repo_radar.py score JeanLucPons/Kangaroo
  ```

- `[archive] name_pattern` is matched against the repo name split into
  lowercase words (`ECDLPSolver_gpu` becomes `ecdlp solver gpu`), never the
  owner. Archive events carry only a name. Up to `enrich_limit` new matches a
  day are therefore looked up through the API and scored like search hits.
  A lookup that falls below `min_score` is not retried for 30 days.
- `[watch] repos` lists the followed repos. The seed list holds the
  third-party repositories most often cited across `aburan28/crypto`,
  `cryptanalysis` and this repo. A renamed repo is reported as such and keeps
  working through GitHub's redirect. Update the name when you see it.
- `[digest]` sets table length, the star gain that counts as rising (10), and
  how long an unseen repo is remembered (a year).

## State branch

`automation/repo-radar` shares no history with `main` and is never merged.
`tools/sync_open_branches.py` skips it. It holds:

- `state.json`: relevant repos with score, reasons and star count when last
  seen; watch cursors; run dates.
- `digests/DATE.md` and `.json`: each digest and its item count.
- `archive/DATE.json`: each day's GH Archive aggregates for matching and
  tracked repos, with per-type event counts and missing hours. This is the
  history for longer analyses.
- `feeds.opml`: Atom feeds (releases, commits, tags) for every followed repo.
  Import it into an RSS reader to follow them between digests.

Deleting the branch resets the radar; the next run is a baseline again.

## One-time setup

1. Merge the workflow into `main`. Scheduled workflows only run from the
   default branch.
2. Run **Actions → repo-radar → Run workflow** once. It creates the branch
   and opens the baseline issue.
3. Make sure you watch this repository with issues included (**Watch →
   Custom → Issues**, or **All activity**). The digest arrives as an issue
   notification.

The job uses only the workflow's `GITHUB_TOKEN` with `contents: write` (to
push the state branch) and `issues: write`. If the push or the issue fails
with 403, check **Settings → Actions → General → Workflow permissions**. No
other secret is needed.

## Limits

- **Search.** GitHub returns at most 1,000 results per query. The radar
  fetches `max_pages` × 100 and marks truncated or incomplete queries in the
  digest's Coverage table; narrow those queries or move them to
  `created_only`. Topics are applied by repo owners, and many serious repos
  have none, which is why keyword queries over READMEs exist. Search allows
  30 requests a minute; the client spaces its calls and waits out rate
  limits. A day's run makes about 50 search requests.
- **Followed repos.** Commits are counted down to the previous head of the
  default branch. If that head is missing from the latest 30, the digest
  shows "30+" (a busy day or rewritten history). New tags are judged against
  the 20 most recent and exclude tags that belong to a release. A rename or
  deletion is reported instead of failing the run.
- **GH Archive** records the events GitHub publishes, which is not all
  activity, and stars and forks counted from it are a sample of the true
  totals. Coverage changes over time. Repository-creation events stopped
  appearing in 2026. From October 6–7, 2026, push and branch/tag creation
  events disappeared from the feed altogether, along with roughly 90% of its
  volume. Each digest states which of the expected event types the day held
  and how many of the 24 hourly files were readable. Up to `catch_up_days`
  missed days are scanned on the next run.
- **Untrusted text.** Descriptions, commit messages and tags are written by
  strangers. The digest escapes markdown and breaks `@` mentions and `#`
  references, so a digest issue cannot ping a user, cross-reference another
  repo's issue, or trigger the `@claude` workflow.

A problem (a failing source, more than four unreadable archive hours, a
token error) is listed in a warning box at the top of the digest. The state is still saved and
the issue still opened, and the job then fails so it shows in Actions.

## Running it locally

Python 3.11 or later; no dependencies.

```sh
export GITHUB_TOKEN=...                         # search needs a token for 30 requests/minute
python3 tools/repo_radar.py run --state-dir /tmp/radar        # writes /tmp/radar/digests/DATE.md
python3 tools/repo_radar.py run --state-dir /tmp/radar --only watch
python3 tools/repo_radar.py opml > feeds.opml

# Ad-hoc GH Archive analysis over several days; changes no state.
# A full day takes under a minute.
python3 tools/repo_radar.py archive --day 2026-09-01 --days 7 --sort stars --json /tmp/sept.json
```

`python3 -m pytest tools/test_repo_radar.py` runs the offline tests.

For history beyond what the state branch holds, GH Archive is also a public
BigQuery dataset (`githubarchive.day.YYYYMMDD`, `githubarchive.month.YYYYMM`).
Select only the columns you need, because the `payload` column dominates the
bytes billed:

```sql
SELECT repo.name AS repo,
       COUNTIF(type = 'WatchEvent') AS stars,
       COUNTIF(type = 'ForkEvent') AS forks,
       COUNTIF(type = 'ReleaseEvent') AS releases
FROM `githubarchive.month.202609`
WHERE REGEXP_CONTAINS(LOWER(SPLIT(repo.name, '/')[SAFE_OFFSET(1)]),
                      r'ecdlp|pollard|kangaroo|isogen|cryptanaly|lattice-(attack|estimator)')
GROUP BY repo
ORDER BY stars DESC
LIMIT 100
```
