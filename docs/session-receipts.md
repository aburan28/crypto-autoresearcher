# Session receipts

A session receipt is one write-once YAML file that an interactive skill
writes when it ends. It records what the session was and what it produced,
so that "tokens per validated outcome" (`docs/token-efficiency.md`) finally
has a denominator. Adopted by `docs/track-record-review-20261006.md`, item
P2.11, which found that the program measured its research outputs in detail
and its own cost not at all.

## What a receipt is, and is not

A receipt is a **process record**. It asserts that a session of skill `X`
ran, in role `Y`, on runtime `Z`, created these records, read about this many
files, and ended with this outcome. It is never evidence (core rule 10 cites
experiments, runs and evidence records, not receipts), it changes no status,
and it carries no scientific content. Its `asserts_nothing_about` field says
so in the file.

Three things it must never do:

- **Estimate usage.** `usage` is the runtime's own counters, passed in as
  `--usage-json` with `--usage-source` naming where they came from (a Cursor
  cloud `run-info` result, a Claude Code transcript total). Where the runtime
  exposes nothing, `usage` is `null`. An estimated token count is a
  fabrication under core rule 5.
- **Be edited.** Files are opened `O_EXCL`. A wrong receipt is corrected by a
  new receipt with `supersedes: <old id>`.
- **Stand in for a record.** A receipt that says "approved EXP-X" is a claim
  that a decision record exists; the decision record is the approval.

## Writing one

At the start of a session (optional, so the receipt carries a real start):

```sh
export SESSION_RECEIPT_STARTED="$(python3 tools/session_receipt.py start)"
```

At the end, always:

```sh
python3 tools/session_receipt.py --skill design-experiment --role coordinator \
    --outcome approved --created EXP-FROB-123456,H-FROB-000001,TASK-20261007-aaaaaa \
    --files-read 41 --goal GOAL-FROB-000001
```

`--bounced <n>` records how many records the session sent back to a
subagent for schema completeness before filing (`propose-ideas` step 4). It
is `null` when the session did not count, never an estimate, and
`tools/tune_skill_batch.py` sums it per window as a diagnostic.

Outcomes are a closed list (`approved`, `review_required`, `refused_capacity`,
`proposed`, `ran`, `nothing_executable`, `reviewed`, `archived`, `published`,
`impeded`, `no_change`, `other`) so they aggregate. Runtime and model are
detected from markers the runtime itself sets (`CURSOR_AGENT`, `CLAUDECODE`,
`AUTORESEARCH_RUNTIME`, `AUTORESEARCH_RESOLVED_MODEL`, …) and are `null` when
no marker is present; `--runtime` and `--model` override.

Receipts land under `coordination/sessions/receipts/<YYYYMMDD>/SR-<date>-<tok>.yaml`
and are committed with the session's other coordination files. They are
coordination traffic, like the bus: `validate_ledger.py` does not know about
them.

## Reading them

```sh
python3 tools/session_receipt.py summary
```

prints receipts per skill and outcome, records created per skill, and how
many receipts carry real usage. `/research-status` includes the same block.
`tune-skill` reads receipts to bound the batch it scores against: the review
found 1,995 unused proposals and could not say how many sessions wrote them.

## Which skills write one

Every public skill: `run`, `coordinate`, `design-experiment`,
`propose-ideas`, `review-evidence`, `research-status` (yes, even read-only —
a status wake that reads 40 files is a cost), `deep-research`,
`curate-knowledge`, `consolidate-lanes`, `tune-skill`. A skill that stops at
an impediment writes `--outcome impeded`; a `run` that found nothing to
execute writes `nothing_executable`, which is the number P0.3 of the review
wants driven to zero.
