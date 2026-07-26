# Agentic Pull-Request Review

Automated review of every pull request, tuned to this program's integrity
rules rather than to generic code style. This document covers what is wired up,
what an operator must still do to activate it, and — most importantly — the
standing of a machine review inside a research program whose whole point is
that claims carry authority only when they are earned.

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

`REVIEW.md` is deliberately not duplicated into the workflow prompt. The
workflow is a bootstrap that tells the agent to read the contract, so the two
review paths below cannot drift apart — the same discipline
`tools/check_runtime_bindings.py` applies to role definitions.

### Division of labor with CI

`.github/workflows/validate.yml` enforces everything mechanical: ledger schema,
cross-references, the numeric `claim_tier` ceiling, run companion artifacts,
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

### Amazon Bedrock or Google Cloud instead

Both workflows use the direct Claude API. To route through Bedrock or Google
Cloud's Agent Platform, drop `anthropic_api_key`, add `use_bedrock: "true"` or
`use_vertex: "true"`, and add the corresponding cloud auth step. The pattern is
in <https://code.claude.com/docs/en/github-actions>. This is the same
substitution `orchestration/providers.yaml` makes for the research runtimes,
but the GitHub Action resolves its model independently of
`orchestration/model-bindings.yaml` — a reviewer model is not a research
inference policy and is not recorded in any run manifest.

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
