---
name: review-run
description: >-
  Review another runner's experiment from its experiment.export/v1 bundle,
  without the producer's session, and file a write-once experiment.review/v1
  record of checks, observations, per-claim judgments, open questions and a
  recommendation. Verifies hashes, protocol adherence, controls, a nonce-sampled
  replay where the backend admits one, a recompute of the headline numbers from
  the raw rows, statistics and scope. Use when asked to review, check, replicate
  or second-opinion a run, a benchmark or a sweep from any of the owner's
  repositories, before an evidence review or validation gate cites it, or on a
  schedule. Changes no research status and repairs nothing.
---

# Review a run

The cross-runner half of `docs/experiment-protocol.md`. One runner produced an
export; this one reads it without trusting it and writes what it found. The
schema is `schemas/experiment-review.v1.json`; the tool is
`tools/experiment_protocol.py`; the example review is under
`examples/experiment-protocol/ecbench-l2-smoke-subset/reviews/`. A review is a
record about an export, never an edit to one, and it asserts nothing about
official research status: `review-evidence` (here), the validation gate and
the PR review (crypto) decide what follows and cite it.

## When

- Before `review-evidence`, `audit-runs` or the validation gate cites an
  export, or a benchmark row, leaderboard row or paper number rests on one.
- When asked for a second opinion, a replication, or "is this real".
- On a schedule over exports with no review yet (`find -name export.json`
  with no `reviews/*.json` beside it).
- Never in the session that produced the export: independence is the point.
  Fetch the branch that published it.

## Steps

1. **Scaffold.** `python3 tools/experiment_protocol.py review new
   <dir>/export.json --role validator --runtime <r> --model <m> --session
   <s>`. The tool recomputes every file and artifact hash, re-lints the
   export against its frozen protocol (arms, roles, seeds, row counts,
   isolation, blinding, analysis hash) and writes `reviews/REV-<stamp>-<tok>.json`
   with the `hashes` and `protocol_adherence` checks filled in. Fill in
   `reviewer.independence` honestly: `shares_code_with_producer` is true when
   your replay used the producer's binary.
2. **Controls.** Read the A/A rows: the spread is the floor every difference
   is read against. Read the positive-control rows: the expected detection
   must be present, or every "nothing found" in the export is
   `positive_control_failed`. Read the negative-control rows and the null
   population's `matched_on`. Cite row ids.
3. **Replay.** Where the backend admits it, replay a sample chosen by a nonce
   you draw now: `ecbench verify --dir <session> --replay K --exit-code` for
   an ecbench session; `python3 tools/runbook.py audit <session>` for a
   runbook session; a `taskq` re-submission at the pinned commit for a queue
   task; the frozen launcher at the pinned commit otherwise. Record
   `units_sampled`, `identical`, `mismatched` and the miss-probability table
   `(1-f)^k`. A replay writes only under the review directory.
4. **Recompute.** Derive the headline numbers from the raw rows yourself,
   with the protocol's frozen analysis if there is one and from the
   statement alone if not (a blind re-derivation, not a copy of the
   producer's summary). Apply the decision rule as written: statistic,
   interval, correction, effect size. A difference inside the A/A spread is
   not a difference. Price uncharged counters at 0, 0.1 and 1 per operation
   on every arm where the comparison is a cross-method ECDLP cost
   (crypto AGENTS.md section 5a) and rank only where the order holds.
5. **Measurement validity.** Rows with `wall_valid: false`, below the
   protocol's isolation level, contended, interrupted or resumed carry no
   clock; counted units stand. Refuted certificates are invalid measurements,
   never negative results. `not_completed` rows are never evidence about the
   thing measured. Check the `flow` block against the rows and against the
   protocol's planned count; a shortfall must be an infrastructure stop.
6. **Scope and provenance.** What the rows cover (curves, sizes, seeds,
   hosts) and what they do not; whether the protocol was frozen and
   committed before the first data point; whether amendments preceded the
   data they affect; whether arm labels were masked until the analysis was
   frozen.
7. **Write.** `observations` (what was seen, with row ids and values),
   `judgments` (one per protocol claim, in the fixed vocabulary:
   `supported_within_scope`, `within_control_distribution`,
   `more_extreme_than_controls`, `not_established`, `invalid_measurement`,
   `positive_control_failed`, `inconclusive`, `refuted_within_scope`, each
   with its basis and scope), `open_questions`, and one `recommendation`
   (`replicate`, `expand`, `respecify`, `rerun_after_infrastructure_fix`,
   `no_action`, `escalate`). Keep observation and judgment apart; never
   write "significant", "breakthrough" or "no effect" outside the
   vocabulary. `python3 tools/experiment_protocol.py review validate
   <review>` must pass.
8. **Publish.** Commit the review file on your own branch and open or
   refresh a PR; the review rides to the owning repository by that PR or by
   a pointer in the export's PR. Under Claude Code the deterministic half
   (steps 1, 3, 5) may run through the model tiers as a card; the reading
   (steps 2, 4, 6, 7) stays with this tier. End with a session receipt
   (`python3 tools/session_receipt.py --skill review-run --role validator
   --outcome reviewed --created <REV id>`).

## What a review never does

- Edit, re-pack or delete an export, a session, a certificate or a row.
- Rerun a trial until it looks favourable, or count a replay as a new run.
- Change a hypothesis, goal, leaderboard or benchmark row; it is one input
  the owning repository's gate cites.
- Report a number it did not recompute or observe.
