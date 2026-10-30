# Director calibration suites

Calibration suites for Delphi's capability registry (aburan28/conductor,
`docs/DELPHI_OBJECTIVES.md` §3 and `docs/DELPHI.md`, "Capability registry"). They measure how
well a model does the `experiment-director` job (`docs/model-tiers.md`) as single-turn batch
answers, graded by this repository's own tools, so a pass means the answer would have been
accepted in production.

Same scope as the rest of `evals/`: evidence about models and the harness, **never** evidence
about ECDLP, and never cited in a ledger record.

| Suite | Family | Items | A pass means |
|---|---|---|---|
| `card-compile.json` | `card-compile` | 8 positive, 4 negative | positive: the card lints (`task_card.py ingest`) and carries exactly the design's argv, timeouts, exit codes, stdout, env, retry, outputs, receipt, scope, binds and commit pin; negative: the design leaves a value out and the reply names it as a specification error instead of choosing a default |
| `assess.json` | `assess` | 10 | `task_card.py ingest --expect assessment` accepts the reply against the real receipt: outcome copied, an allowed recommendation, reasons, `interpretation: not_assessed` |

Every prompt is exactly what `tools/task_card.py request compile|assess` prints. The
`assess` items come from real cards really run by `task_card.py run` (completed, stopped by
an exit code, a second command or a timeout, an output changed after the run, a write outside
the scope, never run), so the facts in each prompt are the facts `ingest` recomputes.

## Running a calibration

With Delphi from conductor (`delphi calibrate`, `delphi registry`):

```sh
delphi calibrate -suite evals/calibration/card-compile.json -provider anthropic -model claude-sonnet-5-5 -effort high
delphi calibrate -suite evals/calibration/card-compile.json -provider anthropic -model claude-haiku-5-5
delphi calibrate -suite evals/calibration/assess.json       -provider vllm -model glm-5.3
delphi registry table -family card-compile
```

Run it from a checkout of this repository: the grader (`grade.py`) reads the fixtures and
`tools/task_card.py` here. A calibration is a measurement that spends tokens, so it follows
the repository's rules for runs (AGENTS.md: resume checkpoint first).

**Size.** Twelve and ten items rank models that differ clearly, but even a perfect model's
Wilson 95% low bound is 0.76 (12/12) and 0.72 (10/10). They cannot certify a level above
that, or call two strong models equivalent within five points; that needs more items.

## Controls

`gold/<family>/<item>.md` is a reference answer per item. `tests/test_calibration_suites.py`
requires every gold answer to pass and a corrupted copy of it to fail (a changed timeout, an
emptied error list, a wrong outcome), plus three targeted failures: inventing a missing value,
naming the wrong missing value, and a recommendation the outcome does not allow. A grader that
cannot tell those apart would make every calibration meaningless.

## Rebuilding

```sh
python3 evals/calibration/build.py --force
```

regenerates the suites, fixtures and gold answers. The prompts embed the checkout (HEAD, the
director contract, the card template), so a rebuild changes each suite's sha256 and Delphi
treats it as a new measurement, never pooled with the old one. `fixtures/emit.py` is bound by
sha256 in every item; editing it requires a rebuild. The grader exits without a verdict when a
fixture no longer gives the outcome it was built with, so a broken item stops a calibration
instead of scoring a model on it.
