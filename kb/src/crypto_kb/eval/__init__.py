"""Retrieval evaluation: questions, metrics, gates, and single-mode baselines."""

from crypto_kb.eval.harness import (
    EvalQuestion,
    EvalReport,
    evaluate,
    evaluate_modes,
    load_questions,
)

__all__ = ["EvalQuestion", "EvalReport", "evaluate", "evaluate_modes", "load_questions"]
