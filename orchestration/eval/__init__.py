"""Evaluation harness: does this research loop actually work, and can we tell?

Two questions, deliberately never merged into one number:

  * capability -- does it solve problems whose answers this repository can
    verify arithmetically;
  * discipline -- does it refuse to claim more than the evidence supports.

For a cryptanalysis harness the second dominates. A loop that occasionally
reports a break that is not there costs more human time than one that finds
nothing, so `evals/suites/discipline.yaml` is the anti-benchmark: every task
there has a correct answer of the form "this does not show what it appears to".

Results are evidence about the harness and its backends. They are NOT
mathematical evidence about ECDLP, which is why they live in `evals/` and never
in `ledger/`.
"""
from .fingerprint import changed_between, harness_fingerprint
from .report import (Interval, RunSummary, TaskSummary, compare, regression,
                     render, render_regression, wilson)
from .runner import TrialResult, run_suite, run_trial, write_results
from .tasks import EvalTask, Suite, build_sandbox, load_suite

__all__ = ["EvalTask", "Interval", "RunSummary", "Suite", "TaskSummary",
           "TrialResult", "build_sandbox", "changed_between", "compare",
           "harness_fingerprint", "load_suite", "regression", "render",
           "render_regression", "run_suite", "run_trial", "wilson",
           "write_results"]
