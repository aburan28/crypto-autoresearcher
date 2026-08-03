"""A fixed, reproducible corpus slice for evaluation.

The full repository stages ~8,400 documents. Running the question set against
all of them takes minutes and, worse, makes the labelled answers unstable:
whether ``KN-LIT-006`` is retrievable should not change because 300 unrelated
literature notes were added last week.

So evaluation runs against an explicit slice -- named globs, not "the first N
files", which reorders whenever a file is added. Growing the slice is a
deliberate edit here, and the labelled answers are re-checked when it changes.
"""

from __future__ import annotations

from pathlib import Path

from crypto_kb.ingest.repo_corpus import RULES, StagingRule, stage_repository

#: Globs that define the evaluation slice, by staging-rule name.
EVAL_GLOBS: dict[str, str] = {
    # The founding ECDLP literature: Semaev, Gaudry, Diem, index calculus.
    "literature": "knowledge/literature/KN-LIT-0[0-9][0-9].md",
    "techniques": "knowledge/techniques/KN-TECH-0[0-9][0-9].md",
    "findings": "knowledge/findings/KN-FIND-*.md",
    "open-problems": "knowledge/open-problems/KN-OPEN-*.md",
    "evidence": "ledger/evidence/EV-*.yaml",
    "hypotheses": "ledger/H-*.yaml",
    "questions": "ledger/RQ-*.yaml",
    "docs": "docs/*.md",
}


def eval_rules() -> tuple[StagingRule, ...]:
    """The staging rules restricted to the evaluation slice."""
    by_name = {rule.name: rule for rule in RULES}
    narrowed: list[StagingRule] = []
    for name, glob in EVAL_GLOBS.items():
        rule = by_name.get(name)
        if rule is None:  # pragma: no cover - guards a rename in repo_corpus
            raise KeyError(f"no staging rule named {name!r}")
        narrowed.append(
            StagingRule(
                name=rule.name,
                glob=glob,
                destination=rule.destination,
                source_type=rule.source_type,
                id_prefix=rule.id_prefix,
                build=rule.build,
            )
        )
    return tuple(narrowed)


def build_eval_corpus(repo_root: Path, store) -> list:
    """Stage the evaluation slice into ``store``."""
    return stage_repository(repo_root, store, rules=eval_rules())
