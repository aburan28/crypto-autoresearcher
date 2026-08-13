# GitHub Automation

Three automations run against this repository: agentic review of every pull
request, an interactive `@claude` agent, and a periodic branch sync that keeps
open branches current with `main`. This document covers what is wired up, what
an operator must still do to activate it, and — most importantly — the standing
of machine output inside a research program whose whole point is that claims
carry authority only when they are earned.

The review is tuned to this program's integrity rules rather than to generic
code style; the sync is deliberately incapable of resolving anything.

## Standing: advisory, never authoritative

The PR reviewer is **not** the Reviewer, Validator, or Red Team role. Those are
defined in `orchestration/roles.yaml` and `agents/*.md`, run under a Coordinator
handoff with an `independent_of_producer` requirement, and act on artifacts that
have already been snapshot-committed. Their output is a research artifact.

The PR reviewer reads an uncommitted diff, has no handoff, and produces
comments. Nothing it says is evidence, and a merged PR settles no research
question. It cannot approve, block, or change state; the Coordinator remains the
only role that changes official research state (`AGENTS.md`, "Roles"). Treat a
clean review as "no integrity defect was spotted in the diff", never as
validation of a result.

The reason to run it anyway is coverage: CI checks record *shape*, the research
roles check committed *artifacts*, and nothing else looks at a diff at the
moment it is proposed. That gap is where a mutated ledger record or an
uncited number slips through.

## What is wired up

| Path | Purpose |
|---|---|
| `REVIEW.md` | The review contract. Single source of truth for what gets flagged, at what severity, and what to leave alone. |
| `.github/workflows/claude-pr-review.yml` | Reviews every non-draft PR on open, push, ready-for-review, and reopen. Read-only; posts inline findings and a summary. |
| `.github/workflows/claude.yml` | Answers `@claude` in issues, PR comments, and reviews. May fix harness and tooling code; refuses to touch the research record. |
| `.github/workflows/sync-main.yml` | Every six hours, merges `main` into open PR branches that are behind it. See [Periodic branch sync](#periodic-branch-sync). |
| `tools/sync_open_branches.py` | The sync's decision logic, with the reasoning behind each rule. |

`REVIEW.md` is deliberately not duplicated into the workflow prompt. The
workflow is a bootstrap that tells the agent to read the contract, so the two
review paths below cannot drift apart — the same discipline
`tools/check_runtime_bindings.py` applies to role definitions.

### Division of labor with CI

`.github/workflows/validate.yml` enforces everything mechanical: ledger schema,
cross-references, the declared `claim_tier` metadata, run companion artifacts,
`experiments/**/runs/**` immutability, knowledge-index freshness, runtime
bindings, dispatch-queue validity, and the test suite. `REVIEW.md` tells the
reviewer not to repeat any of it.

What the reviewer covers instead is what a checker cannot reach:

- immutability of `ledger/**` and `knowledge/**`, which the mechanical check
  does not cover — it guards only run artifacts;
- prose that asserts beyond its declared `claim_tier`, which passes the
  numeric field check;
- numbers, timings, and citations with no traceable artifact;
- infrastructure failure narrated as mathematical evidence;
- certificate verification that is not actually independent of the solver;
- status transitions with no decision record or no supporting evidence.

## Activation

Two steps, both requiring repository-admin access. Until both are done the
workflows are inert — they run and fail on the missing secret.

1. **Install the Claude GitHub App** on `aburan28/crypto-autoresearcher`:
   <https://github.com/apps/claude>. It requests Contents, Issues, and Pull
   requests read/write. From a local Claude Code session, `/install-github-app`
   does this interactively.
2. **Add the `ANTHROPIC_API_KEY` repository secret** under Settings → Secrets
   and variables → Actions, using a key from
   <https://console.anthropic.com>.

To verify, open a throwaway PR that edits a markdown file. A `claude-pr-review`
job should appear in Checks within a minute or two and post a summary comment.

### Cloud-provider substitution

Amazon Bedrock is prohibited by the repository cost policy. Do not add
`use_bedrock`, AWS authentication for inference, a Bedrock endpoint, or a
Bedrock model to either workflow. Google Cloud's Agent Platform may be
configured with `use_vertex: "true"` and the corresponding authentication step,
provided the selected model still satisfies the review policy. GitHub Actions
resolve their models independently of `orchestration/model-bindings.yaml`, so
the workflow must enforce the no-Bedrock rule directly rather than relying on
the research adapter.

## The managed alternative

Anthropic also offers a hosted Code Review service (Team and Enterprise plans)
that needs no workflow file: a Claude organization Owner enables it at
<https://claude.ai/admin-settings/claude-code>, selects repositories, and picks
a trigger mode per repository (once on PR creation, on every push, or manual).
It runs a fleet of agents with a verification pass to filter false positives,
posts inline findings with severity markers, and reads the same `REVIEW.md`
committed here.

Choose one path, not both, or every PR gets reviewed twice:

- **Managed service** — stronger multi-agent review, no CI minutes, billed
  through usage credits at roughly \$15–25 per review. Requires Team or
  Enterprise, and is unavailable under Zero Data Retention.
- **GitHub Actions** (what is committed here) — works on any plan with an API
  key, consumes Actions minutes, costs ordinary API tokens, and is fully
  auditable in-repo.

If the managed service is enabled, delete `claude-pr-review.yml` and keep
`claude.yml`; `REVIEW.md` serves whichever path is active.

## Triggering a review by hand

Under the managed service, comment on an open PR:

| Command | Effect |
|---|---|
| `@claude review` | One review now, no subscription to later pushes |
| `@claude review always` | Review now, then on every subsequent push |
| `@claude review once` | Same as the bare command |

Post it as a top-level PR comment with the command first. Manual triggers work
on draft PRs.

With the committed Actions workflow, a review is triggered by pushing to the PR
branch or marking a draft ready; `@claude` in a comment reaches the interactive
agent in `claude.yml` instead.

## Tuning

Edit `REVIEW.md`. It is injected as the highest-priority instruction block, so
rules land there far more reliably than the same rules buried in `CLAUDE.md`.
Length has a cost — a long contract dilutes the rules that matter — so when
adding a rule, consider whether an existing one should go. If the reviewer is
noisy, the usual levers are the nit cap, the "Do not report" list, and the
verification bar.

Review-only guidance belongs in `REVIEW.md`; guidance that should shape every
Claude Code session in this repository belongs in `CLAUDE.md`, whose newly
introduced violations the reviewer already flags as nits.

## Periodic branch sync

`sync-main.yml` runs every six hours, and on demand via **Actions → sync-main →
Run workflow** (which offers a dry run). For each open pull request whose branch
is behind `main`, it merges `main` in and pushes the result.

It needs no secret and no app — it runs on the default `GITHUB_TOKEN` — so
unlike the review workflows it is live as soon as this branch merges.

### What it will not do

- **It never rebases.** A rebase rewrites every commit on the branch, including
  the ones run records were archived in, and a run receipt whose commit no
  longer exists is not reproducible (`AGENTS.md`, "Durable research commits").
- **It never resolves a conflict.** Records are immutable and corrections
  supersede rather than overwrite, so no machine may pick a side in a conflicted
  ledger record, run artifact, or knowledge entry. It aborts the merge and
  comments on the pull request with the conflicting paths. The resolution is a
  new superseding record under a new id.
- **It never pushes a tree it has not validated.** Two branches can each add a
  record that git merges cleanly but that `validate_ledger.py` rejects together
  — a duplicate id, a cross-reference to a record that moved. The merge is
  discarded and reported instead of pushed.
- **It never touches a fork** (`GITHUB_TOKEN` cannot push to one) or a pull
  request labelled `no-auto-sync`.
- **It never runs against a dirty working tree.** It switches branches and
  resets between them, so running it locally on uncommitted work would destroy
  that work. It refuses to start instead, and returns to the ref it began on.

A conflict or a failed validation exits the job **green**. Both are normal
outcomes that the pull request already carries; a schedule that goes red every
six hours teaches everyone to ignore it. Only an infrastructure failure — `gh`
unauthenticated, a branch that cannot be fetched — fails the job. Repeat reports
are suppressed per pull request per tip of `main`, so a branch that stays
conflicted is mentioned once each time `main` moves, not four times a day.

### Why it validates locally instead of letting CI do it

Pushes made with `GITHUB_TOKEN` do not trigger further workflow runs — GitHub's
recursion guard. So a sync push does **not** re-run `validate.yml` or
`claude-pr-review.yml` on the merged result. That keeps the review bill down (a
sync pass across a dozen stale branches would otherwise trigger a dozen reviews
of diffs nobody wrote), but it means nothing downstream would catch a sync that
broke the ledger. Hence the pre-push validation in `sync_open_branches.py`: it
is the only thing that ever sees the merged tree.

The consequence to know about: after a sync, the checks displayed on the pull
request are from the last human push, not from the merged state. Push a commit,
or re-run the checks, if you need CI's verdict on the merged result before
merging.
