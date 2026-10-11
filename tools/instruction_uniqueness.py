#!/usr/bin/env python3
"""Measure how much of the always-loaded instruction text says something new.

`tools/check_instruction_budget.py` counts words; this tool measures meaning.
It splits AGENTS.md and CLAUDE.md into statements (sentences of paragraphs and
list items, rows of tables; code blocks and headings are skipped), embeds each
statement, and reports:

- **near-duplicate pairs**: statements whose embeddings are closer than the
  backend's threshold, i.e. two places saying the same thing;
- **novelty** of each statement: 1 - its cosine similarity to its nearest
  other statement (0 = said elsewhere, higher = unique);
- **effective distinct statements**: the effective rank exp(H(p)) of the
  statements' Gram matrix, where p is its normalized eigenvalue spectrum. N
  statements that all say different things approach N; N paraphrases of one
  rule approach 1. Divided by the word count it gives distinct statements per
  1,000 words, the density this file is trying to keep high. Dense
  embeddings are mean-centered first (see `CENTERED`).

Backends, best available first unless `--backend` picks one:

- `bge`: BAAI/bge-small-en-v1.5 through `fastembed` (a learned sentence model;
  needs `pip install fastembed` and a one-time model download);
- `model2vec`: minishlab/potion-base-8M through `model2vec` (static, small,
  CPU-only; `pip install model2vec`);
- `lexical`: TF-IDF over word unigrams and bigrams with numpy only. It finds
  repeated wording, not paraphrase; it is the fallback, and what tests use.

Statements a test pins in two sections on purpose are listed in
`INTENTIONAL_REPEATS` and reported apart from accidental duplicates.

Usage:
    python3 tools/instruction_uniqueness.py                 # report
    python3 tools/instruction_uniqueness.py --ref origin/main   # compare
    python3 tools/instruction_uniqueness.py --json
    python3 tools/instruction_uniqueness.py --max-duplicates 0  # gate
"""
from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
FILES = ("AGENTS.md", "CLAUDE.md")

# Cosine, after mean-centering dense embeddings, at or above which two
# statements count as saying the same thing. Calibrated on this repository's
# AGENTS.md and CLAUDE.md (2026-10-09): each flagged pair restated a rule or a
# fact stated elsewhere; distinct rules on one topic fell below. `lexical`
# sees only shared wording, so it flags near-verbatim copies only.
THRESHOLDS = {"bge": 0.55, "model2vec": 0.70, "lexical": 0.45}
# Sentence models give every text a large shared component, which makes all
# cosines high and the Gram spectrum one-dimensional; subtracting the mean
# embedding removes it (the usual anisotropy correction).
CENTERED = {"bge", "model2vec"}

# Repeated on purpose: tests require each phrase in more than one section
# (tools/test_ecc_priority.py, tools/test_no_goal_pausing.py).
INTENTIONAL_REPEATS = (
    "rank ahead of doing nothing",
)

MIN_WORDS = 4


@dataclass
class Statement:
    file: str
    section: str
    line: int
    text: str
    table: int | None = None  # rows of one table are distinct entries
    words: int = field(init=False)

    def __post_init__(self) -> None:
        self.words = len(self.text.split())


# --------------------------------------------------------------------------
# segmentation
# --------------------------------------------------------------------------
_SENTENCE_END = re.compile(r"(?<=[.!?:;])\s+(?=[A-Z*`\"(\[])")
_ITEM = re.compile(r"^\s*(?:[-*+]|\d+\.)\s+")


def _mask_code(text: str) -> tuple[str, list[str]]:
    """Hide inline code so sentence splitting never cuts inside it."""
    spans: list[str] = []

    def keep(m: re.Match) -> str:
        spans.append(m.group(0))
        return f"\x00{len(spans) - 1}\x00"

    return re.sub(r"`[^`]*`", keep, text), spans


def _unmask(text: str, spans: list[str]) -> str:
    return re.sub(r"\x00(\d+)\x00", lambda m: spans[int(m.group(1))], text)


def _sentences(block: str) -> list[str]:
    masked, spans = _mask_code(" ".join(block.split()))
    parts = _SENTENCE_END.split(masked)
    return [_unmask(p, spans).strip() for p in parts if p.strip()]


def segment(name: str, text: str) -> list[Statement]:
    out: list[Statement] = []
    section = "(preamble)"
    lines = text.splitlines()
    in_code = False
    block: list[str] = []
    block_line = 0
    table = None  # id of the table the current row belongs to
    tables = 0

    def flush() -> None:
        nonlocal block
        if block:
            for sentence in _sentences(" ".join(block)):
                if len(sentence.split()) >= MIN_WORDS:
                    out.append(Statement(name, section, block_line, sentence))
        block = []

    for number, raw in enumerate(lines, 1):
        line = raw.rstrip()
        if line.lstrip().startswith("```"):
            flush()
            in_code = not in_code
            continue
        if in_code:
            continue
        if line.startswith("#"):
            flush()
            section = line.lstrip("#").strip()
            continue
        if not line.strip():
            flush()
            continue
        if line.lstrip().startswith("|"):
            flush()
            nxt = lines[number] if number < len(lines) else ""
            if table is None:
                tables += 1
                table = tables
            if re.fullmatch(r"\s*\|[\s:|-]+\|\s*", nxt) or \
                    re.fullmatch(r"\s*\|[\s:|-]+\|\s*", line):
                continue  # header row or separator, not a statement
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            row = " | ".join(c for c in cells if c)
            if len(row.split()) >= MIN_WORDS:
                out.append(Statement(name, section, number, row, table))
            continue
        table = None
        if _ITEM.match(line):
            flush()
            block_line = number
            block = [_ITEM.sub("", line)]
            continue
        if not block:
            block_line = number
        block.append(line.strip())
    flush()
    return out


# --------------------------------------------------------------------------
# embedding backends
# --------------------------------------------------------------------------
def _normalize(m: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(m, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return m / norms


def embed_lexical(texts: list[str]) -> np.ndarray:
    def terms(t: str) -> list[str]:
        words = re.findall(r"[a-z0-9_]+", t.lower())
        return words + [a + " " + b for a, b in zip(words, words[1:])]

    docs = [terms(t) for t in texts]
    vocab: dict[str, int] = {}
    for d in docs:
        for w in d:
            vocab.setdefault(w, len(vocab))
    tf = np.zeros((len(docs), len(vocab)))
    for i, d in enumerate(docs):
        for w in d:
            tf[i, vocab[w]] += 1
    df = (tf > 0).sum(axis=0)
    idf = np.log((1 + len(docs)) / (1 + df)) + 1
    return _normalize(tf * idf)


def embed_model2vec(texts: list[str]) -> np.ndarray:
    from model2vec import StaticModel  # type: ignore

    model = StaticModel.from_pretrained("minishlab/potion-base-8M")
    return _normalize(np.asarray(model.encode(texts), dtype=float))


def embed_bge(texts: list[str]) -> np.ndarray:
    from fastembed import TextEmbedding  # type: ignore

    model = TextEmbedding("BAAI/bge-small-en-v1.5")
    return _normalize(np.asarray(list(model.embed(texts)), dtype=float))


BACKENDS = {"bge": embed_bge, "model2vec": embed_model2vec, "lexical": embed_lexical}


def pick_backend(requested: str | None) -> str:
    if requested:
        return requested
    import importlib.util

    if importlib.util.find_spec("fastembed"):
        return "bge"
    if importlib.util.find_spec("model2vec"):
        return "model2vec"
    return "lexical"


# --------------------------------------------------------------------------
# metrics
# --------------------------------------------------------------------------
def effective_rank(vectors: np.ndarray) -> float:
    """exp(entropy) of the normalized Gram spectrum (Roy & Vetterli, 2007)."""
    if len(vectors) == 0:
        return 0.0
    eig = np.clip(np.linalg.eigvalsh(vectors @ vectors.T), 0, None)
    p = eig / eig.sum()
    p = p[p > 0]
    return float(math.exp(-(p * np.log(p)).sum()))


def _intentional(a: str, b: str) -> bool:
    return any(k in a and k in b for k in INTENTIONAL_REPEATS)


def measure(texts: dict[str, str], backend: str) -> dict:
    statements = [s for name, t in texts.items() for s in segment(name, t)]
    vectors = BACKENDS[backend]([s.text for s in statements])
    if backend in CENTERED and len(vectors) > 1:
        vectors = _normalize(vectors - vectors.mean(axis=0))
    sim = vectors @ vectors.T
    np.fill_diagonal(sim, -1.0)
    threshold = THRESHOLDS[backend]
    nearest = sim.argmax(axis=1)
    novelty = 1.0 - sim.max(axis=1)
    pairs, intentional = [], []
    n = len(statements)
    for i in range(n):
        for j in range(i + 1, n):
            same_table = statements[i].table is not None and \
                statements[i].table == statements[j].table
            if sim[i, j] >= threshold and not same_table:
                row = {"similarity": round(float(sim[i, j]), 3),
                       "a": _where(statements[i]), "b": _where(statements[j]),
                       "a_text": statements[i].text, "b_text": statements[j].text}
                (intentional if _intentional(statements[i].text, statements[j].text)
                 else pairs).append(row)
    pairs.sort(key=lambda r: -r["similarity"])
    words = sum(len(t.split()) for t in texts.values())
    erank = effective_rank(vectors)
    ranked = sorted(range(n), key=lambda i: novelty[i])
    return {
        "backend": backend,
        "threshold": threshold,
        "words": words,
        "statements": n,
        "effective_distinct_statements": round(erank, 1),
        "distinct_per_1000_words": round(1000 * erank / words, 2) if words else 0.0,
        "mean_novelty": round(float(novelty.mean()), 3) if n else 0.0,
        "near_duplicates": pairs,
        "intentional_repeats": intentional,
        "least_novel": [
            {"novelty": round(float(novelty[i]), 3), "at": _where(statements[i]),
             "text": statements[i].text,
             "nearest": _where(statements[int(nearest[i])]),
             "nearest_text": statements[int(nearest[i])].text}
            for i in ranked[:15]
        ],
    }


def _where(s: Statement) -> str:
    return f"{s.file}:{s.line} ({s.section})"


# --------------------------------------------------------------------------
# input and output
# --------------------------------------------------------------------------
def read_worktree(repo: Path = REPO) -> dict[str, str]:
    return {f: (repo / f).read_text(encoding="utf-8") for f in FILES if (repo / f).is_file()}


def read_ref(ref: str, repo: Path = REPO) -> dict[str, str]:
    out = {}
    for f in FILES:
        r = subprocess.run(["git", "-C", str(repo), "show", f"{ref}:{f}"],
                           capture_output=True, text=True)
        if r.returncode == 0:
            out[f] = r.stdout
    return out


def render(report: dict, label: str) -> str:
    lines = [
        f"{label}: {report['words']} words, {report['statements']} statements, "
        f"{report['effective_distinct_statements']} effective distinct "
        f"({report['distinct_per_1000_words']} per 1,000 words), mean novelty "
        f"{report['mean_novelty']} [{report['backend']}, duplicate at cosine >= "
        f"{report['threshold']}]",
    ]
    dups = report["near_duplicates"]
    lines.append(f"near-duplicate pairs: {len(dups)}"
                 + (f" (+{len(report['intentional_repeats'])} intentional)"
                    if report["intentional_repeats"] else ""))
    for d in dups:
        lines.append(f"  {d['similarity']:.3f}  {d['a']}\n         {d['a_text']}\n"
                     f"         {d['b']}\n         {d['b_text']}")
    lines.append("least novel statements:")
    for s in report["least_novel"][:10]:
        lines.append(f"  {s['novelty']:.3f}  {s['at']}: {s['text'][:110]}\n"
                     f"         nearest {s['nearest']}: {s['nearest_text'][:110]}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--backend", choices=sorted(BACKENDS))
    ap.add_argument("--ref", help="also measure AGENTS.md/CLAUDE.md at this git ref")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--max-duplicates", type=int,
                    help="exit 1 when more accidental near-duplicate pairs than this")
    args = ap.parse_args(argv)
    backend = pick_backend(args.backend)
    reports = {"worktree": measure(read_worktree(), backend)}
    if args.ref:
        reports[args.ref] = measure(read_ref(args.ref), backend)
    if args.json:
        print(json.dumps(reports, indent=2))
    else:
        print("\n\n".join(render(r, label) for label, r in reports.items()))
    if args.max_duplicates is not None and \
            len(reports["worktree"]["near_duplicates"]) > args.max_duplicates:
        print(f"FAIL: {len(reports['worktree']['near_duplicates'])} near-duplicate "
              f"pairs (allowed {args.max_duplicates})", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
