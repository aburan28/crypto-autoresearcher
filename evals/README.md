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

## Schedule

`.github/workflows/weekly-evals.yml` validates both suites every Monday and,
when the configured backend (`vars.EVAL_BACKEND`, default `anthropic`) has a
credential in the repository secrets, runs them with `vars.EVAL_TRIALS`
(default 3) repeats and uploads `evals/results/<date>/` as a 90-day workflow
artifact. Without a credential it validates, warns, and runs nothing: a
suite run against a backend with no key produces `trial_error` rows with
zero tokens, which is an infrastructure stop and not a measurement.

## Run log

Attempts are listed here because `evals/results/` is not committed. An entry
says what was run and what came back; it never summarises a result that
should be read from its record.

| date | commit | command | outcome |
| --- | --- | --- | --- |
| 2026-10-07 | `0804d91230` | `python3 -m orchestration.eval validate --suite evals/suites/{discipline,capability}.yaml` | both valid: 8 and 4 tasks, fixtures build, policies resolve (`capability` needs `sympy`, a core dependency) |
| 2026-10-07 | `0804d91230` | `python3 -m orchestration.eval run --suite evals/suites/discipline.yaml --backend anthropic --trials 1 --out /tmp/evalrun-discipline` | **not a measurement**: 5/5 trials `stop_reason: trial_error`, 0 steps, 0 tokens, `TransportError: backend anthropic needs credentials in $ANTHROPIC_API_KEY, which is unset`. No API-backed backend had credentials in the Cloud Agent environment; `local` requires a served model. Record discarded, no baseline pinned. First real run awaits a credential in the weekly workflow or an operator session. |
