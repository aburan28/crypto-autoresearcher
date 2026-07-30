# Evaluation records

Suites live in `suites/`. Results written by
`python3 -m orchestration.eval run --out evals/results/<name>` land here as
immutable records: `summary.json`, `trials.json`, `report.txt`.

**Scope.** These are evidence about the harness and its inference backends.
They are **not** mathematical evidence about ECDLP and must never be cited in
an evidence record, decision, or synthesis statement as if they were. That is
why they live here and not in `ledger/`.

See `docs/measuring-the-harness.md` for what the suites measure, what they
deliberately do not, and why grading is arithmetic rather than a judge model.
